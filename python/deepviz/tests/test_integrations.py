"""Exercise the public agent, command-line, and stdio boundaries without credentials."""
from __future__ import annotations

import asyncio
import base64
import importlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROWS = [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}]
SPEC = {"kind": "bar", "x": "month", "y": "revenue", "title": "Revenue"}
RENDER_NAMES = {"render_matplotlib", "render_plotly", "render_vega", "render_echarts", "render_antv"}
TOOL_NAMES = RENDER_NAMES | {"normalize_data", "recommend_chart"}


def integrations():
    return importlib.import_module("deepviz.tools")


def tools_at(path, **kwargs):
    pytest.importorskip("langchain_core")
    return {tool.name: tool for tool in integrations().create_tools(path, **kwargs)}


def test_public_integration_entrypoints_exist():
    for module in ("tools", "recommend", "mcp_server", "cli"):
        assert importlib.util.find_spec(f"deepviz.{module}") is not None


def test_normalization_returns_bounded_profile_and_reusable_handle(tmp_path):
    tools = tools_at(tmp_path)
    result = tools["normalize_data"].invoke({"data": ROWS, "spec": SPEC})
    assert result["input_count"] == 2
    assert result["output_count"] == 2
    assert result["profile"]["numeric_fields"] == ["revenue"]
    assert "records" not in result
    advice = tools["recommend_chart"].invoke({"data": {"dataset_id": result["dataset_id"]}})
    assert advice["spec"]["kind"] == "bar"
    assert advice["spec"]["x"] == "month"
    assert advice["spec"]["y"] == "revenue"


@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_every_structured_tool_creates_real_artifacts(engine, tmp_path):
    pytest.importorskip("langchain_core")
    from langchain_core.tools import StructuredTool

    tools = tools_at(tmp_path)
    assert set(tools) == TOOL_NAMES
    assert all(isinstance(tool, StructuredTool) for tool in tools.values())
    result = tools[f"render_{engine}"].invoke({"data": ROWS, "spec": SPEC})
    assert result["engine"] == engine
    assert result["input_count"] == 2
    assert result["output_count"] == 2
    assert result["paths"]
    for value in result["paths"]:
        path = Path(value)
        assert path.resolve().is_relative_to(tmp_path.resolve())
        assert path.stat().st_size > 100


def test_flow_preserves_original_input_count_after_bounded_profile(tmp_path):
    tools = tools_at(tmp_path)
    rows = [{"x": index, "y": index * 2} for index in range(150)]
    spec = {"kind": "scatter", "x": "x", "y": "y", "max_points": 10, "aggregation": "sample"}
    normalized = tools["normalize_data"].invoke({"data": rows, "spec": spec})
    assert normalized["input_count"] == 150
    assert normalized["output_count"] == 10
    artifact = tools["render_matplotlib"].invoke(
        {"data": {"dataset_id": normalized["dataset_id"]}, "spec": spec}
    )
    assert artifact["input_count"] == 150
    assert artifact["output_count"] == 10


@pytest.mark.parametrize("source", [{"file": "../secret.csv"}, {"file": "https://example.com/data"}])
def test_file_inputs_cannot_escape_the_explicit_data_root(tmp_path, source):
    data_dir = tmp_path / "input"
    data_dir.mkdir()
    tools = tools_at(tmp_path / "out", data_dir=data_dir)
    with pytest.raises(ValueError, match="data directory|relative|URL"):
        tools["normalize_data"].invoke({"data": source, "spec": SPEC})


def test_file_inputs_disabled_without_data_root(tmp_path):
    tools = tools_at(tmp_path)
    with pytest.raises(ValueError, match="data_dir"):
        tools["normalize_data"].invoke({"data": {"file": "data.csv"}, "spec": SPEC})


def test_file_input_and_recommendation_do_not_return_raw_rows(tmp_path):
    (tmp_path / "sales.csv").write_text("month,revenue\nJan,12\nFeb,18\n", encoding="utf-8")
    tools = tools_at(tmp_path / "out", data_dir=tmp_path)
    result = tools["normalize_data"].invoke({"data": {"file": "sales.csv"}, "spec": SPEC})
    assert result["input_count"] == 2
    assert "Jan" not in json.dumps(result)
    recommendation = tools["recommend_chart"].invoke({"data": {"dataset_id": result["dataset_id"]}})
    assert recommendation["spec"]["kind"] == "bar"


@pytest.mark.parametrize("data", ["../../secret.csv", "__import__('os').system('echo unsafe')", {"dataset_id": "absent"}])
def test_invalid_references_are_not_evaluated_or_treated_as_paths(tmp_path, data):
    tools = tools_at(tmp_path)
    with pytest.raises(ValueError):
        tools["normalize_data"].invoke({"data": data, "spec": SPEC})


def test_inline_payload_limit_points_to_file_workflow(tmp_path):
    tools = tools_at(tmp_path)
    with pytest.raises(ValueError, match="file"):
        tools["normalize_data"].invoke({"data": [{"x": "x" * 1_100_000}], "spec": SPEC})


def test_profile_bounds_field_names_and_does_not_leak_values():
    from deepviz.models import NormalizedData
    from deepviz.recommend import profile

    result = profile(NormalizedData(records=[{"x" * 10_000: 42, "valid": 7}], input_count=1))
    assert result["fields"] == ["valid"]
    assert result["numeric_fields"] == ["valid"]
    assert result["fields_truncated"] is True
    assert len(json.dumps(result)) < 1000


@pytest.mark.parametrize("name", ["../system", "/system", "v2/system"])
def test_prompt_loader_rejects_nonversioned_or_traversal_names(name):
    import deepviz

    assert callable(getattr(deepviz, "read_prompt", None))
    with pytest.raises(ValueError):
        deepviz.read_prompt(name)


def test_mcp_can_be_created_without_langchain(tmp_path):
    pytest.importorskip("mcp")
    code = """
import asyncio, importlib.abc, sys
class BlockLangchain(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'langchain_core', 'deepagents'}:
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, BlockLangchain())
from deepviz.mcp_server import create_server
server = create_server(sys.argv[1])
tools = asyncio.run(server.list_tools())
assert len(tools) == 7
"""
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_extra_executable_spec_fields_are_rejected(tmp_path):
    tools = tools_at(tmp_path)
    with pytest.raises(ValueError):
        tools["render_matplotlib"].invoke({"data": ROWS, "spec": {**SPEC, "eval": "process.exit()"}})


def test_model_cannot_choose_output_directory(tmp_path):
    tools = tools_at(tmp_path)
    with pytest.raises(ValueError):
        tools["render_matplotlib"].invoke({"data": ROWS, "spec": SPEC, "output_dir": "../outside"})


@pytest.mark.parametrize(
    ("goal", "rows", "kind"),
    [
        ("trend", [{"date": "2026-01-01", "value": 1}, {"date": "2026-01-02", "value": 2}], "line"),
        ("relationship", [{"a": 1, "b": 2}, {"a": 2, "b": 4}], "scatter"),
        ("distribution", [{"value": 1}, {"value": 2}], "histogram"),
        ("composition", [{"part": "A", "value": 1}, {"part": "B", "value": 2}], "pie"),
        ("composition", [{"part": "A", "value": -1}, {"part": "B", "value": 2}], "bar"),
        ("composition", [{"part": "A", "value": 0}, {"part": "B", "value": 0}], "bar"),
    ],
)
def test_recommendation_uses_observed_types_and_goal(goal, rows, kind, tmp_path):
    tools = tools_at(tmp_path)
    result = tools["recommend_chart"].invoke({"data": rows, "goal": goal})
    assert result["spec"]["kind"] == kind
    assert result["rationale"]


def test_import_does_not_require_optional_agent_or_mcp_packages():
    code = """
import importlib.abc, sys
class BlockOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'langchain_core', 'deepagents', 'mcp'}:
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, BlockOptional())
import deepviz
from deepviz import ChartSpec, render, normalize, create_tools
assert ChartSpec(kind='bar').kind == 'bar'
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_public_normalize_export_remains_callable_after_first_use():
    import deepviz

    result = deepviz.normalize(ROWS, SPEC)
    assert result.input_count == 2
    assert callable(deepviz.normalize)
    assert deepviz.normalize(ROWS, SPEC).input_count == 2


def test_cli_render_outputs_machine_readable_metadata(tmp_path):
    (tmp_path / "data.json").write_text(json.dumps(ROWS), encoding="utf-8")
    (tmp_path / "spec.json").write_text(json.dumps(SPEC), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "deepviz.cli", "render", str(tmp_path / "data.json"),
         "--spec", str(tmp_path / "spec.json"), "--output-dir", str(tmp_path / "out")],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    metadata = json.loads(result.stdout)
    assert metadata["engine"] == "matplotlib"
    assert Path(metadata["paths"][0]).is_file()


def test_cli_bad_spec_has_nonzero_exit_and_no_artifact(tmp_path):
    (tmp_path / "data.json").write_text(json.dumps(ROWS), encoding="utf-8")
    (tmp_path / "spec.json").write_text('{"kind":"run-python"}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "deepviz.cli", "render", str(tmp_path / "data.json"),
         "--spec", str(tmp_path / "spec.json"), "--output-dir", str(tmp_path / "out")],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 2
    assert not result.stdout
    assert "error" in result.stderr.lower()
    assert not list((tmp_path / "out").glob("**/*.png"))


@pytest.mark.integration
def test_real_deep_agent_attach_and_tool_execution(tmp_path):
    pytest.importorskip("deepagents")
    from deepagents import create_deep_agent
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, ToolMessage
    from langchain_core.outputs import ChatGeneration, ChatResult

    class LocalToolModel(BaseChatModel):
        @property
        def _llm_type(self):
            return "local-tool-fixture"

        def bind_tools(self, tools, **kwargs):
            return self

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            prior = [message for message in messages if isinstance(message, ToolMessage)]
            if prior and prior[-1].name == "render_matplotlib":
                message = AIMessage(content="Chart ready.")
            else:
                if not prior:
                    name, args = "normalize_data", {"data": ROWS, "spec": SPEC}
                else:
                    previous = json.loads(prior[-1].content)
                    reference = {"dataset_id": previous["dataset_id"]}
                    if prior[-1].name == "normalize_data":
                        name, args = "recommend_chart", {"data": reference, "goal": "comparison"}
                    else:
                        name, args = "render_matplotlib", {"data": reference, "spec": previous["spec"]}
                message = AIMessage(content="", tool_calls=[{
                    "name": name, "args": args, "id": f"chart-{len(prior)}",
                }])
            return ChatResult(generations=[ChatGeneration(message=message)])

    agent = create_deep_agent(model=LocalToolModel(), tools=list(tools_at(tmp_path).values()))
    result = agent.invoke({"messages": [{"role": "user", "content": "Make a revenue chart."}]})
    messages = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    assert [message.name for message in messages] == ["normalize_data", "recommend_chart", "render_matplotlib"]
    assert all(message.status == "success" for message in messages)
    assert list(tmp_path.glob("**/*.png"))


@pytest.mark.integration
def test_real_stdio_mcp_discovery_render_and_resource_access(tmp_path):
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def exercise():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "deepviz.mcp_server", "--output-dir", str(tmp_path / "out"),
                  "--data-dir", str(tmp_path)],
            env=dict(os.environ),
        )
        async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            discovered = await session.list_tools()
            assert {tool.name for tool in discovered.tools} == TOOL_NAMES
            result = await session.call_tool("render_matplotlib", {"data": ROWS, "spec": SPEC})
            assert not result.isError, result
            images = [block for block in result.content if block.type == "image"]
            assert images and base64.b64decode(images[0].data).startswith(b"\x89PNG\r\n\x1a\n")
            metadata = json.loads(next(block.text for block in result.content if block.type == "text"))
            uri = next(item["uri"] for item in metadata["resources"] if item["mime_type"] == "image/png")
            resource = await session.read_resource(uri)
            assert base64.b64decode(resource.contents[0].blob).startswith(b"\x89PNG")
            interactive = await session.call_tool("render_echarts", {"data": ROWS, "spec": SPEC})
            assert not interactive.isError, interactive
            metadata = json.loads(next(block.text for block in interactive.content if block.type == "text"))
            uri = next(item["uri"] for item in metadata["resources"] if item["mime_type"] == "text/html")
            html = await session.read_resource(uri)
            assert "<html" in html.contents[0].text.lower() or "<!doctype" in html.contents[0].text.lower()
            denied = await session.call_tool("normalize_data", {"data": {"file": "../secret.csv"}, "spec": SPEC})
            assert denied.isError

    asyncio.run(asyncio.wait_for(exercise(), timeout=90))
