"""Portable real MCP/Deep Agents acceptance; no provider, installer, or source patch.

Run with pytest, or directly with an installed consumer's Python. Package resolution
is the caller's choice, checked by --mode/--expected-module-root, never a sys.path edit.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import importlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

CHECKPOINT = "3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab"
ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")
NAMES = {f"render_{engine}" for engine in ENGINES} | {"normalize_data", "recommend_chart"}
ROWS = [
    {"category": "Alpha", "amount": 2}, {"category": "Alpha", "amount": 5},
    {"category": "Beta", "amount": 11}, {"category": "Gamma", "amount": -3},
]
EXPECTED = [
    {"category": "Alpha", "amount": 7}, {"category": "Beta", "amount": 11},
    {"category": "Gamma", "amount": -3},
]
SPEC = {"kind": "bar", "x": "category", "y": "amount", "aggregation": "sum"}


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fingerprint(path: Path) -> dict:
    data = path.read_bytes()
    return {"name": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def runtime_identity(mode: str, expected_module_root: Path | None = None) -> dict:
    repository = Path(__file__).resolve().parents[3]
    source = repository / "python/deepviz/src"
    expected = (expected_module_root or source).resolve()
    distribution = importlib.metadata.distribution("deepviz-agent-toolkit")
    direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
    editable = direct_url.get("dir_info", {}).get("editable", False)
    installed_root = Path(distribution.locate_file("deepviz")).resolve()
    if mode == "installed":
        assert not editable, "Installed mode rejects editable source distributions"
        assert not os.environ.get("PYTHONPATH"), "Installed mode requires PYTHONPATH to be unset"
    modules = {}
    for name in ("deepviz", "deepviz.tools", "deepviz.mcp_server", "deepviz.models", "deepviz.engines"):
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        if mode == "source":
            assert path.is_relative_to(expected), f"Source identity mismatch: {name}"
        else:
            assert not path.is_relative_to(source.resolve()), f"Installed run leaked source: {name}"
            assert path.is_relative_to(installed_root), f"Installed mode module outside wheel: {name}"
            if expected_module_root is not None:
                assert path.is_relative_to(expected), f"Installed identity mismatch: {name}"
        modules[name] = {"path": str(path), **fingerprint(path)}
    versions = {}
    for name in ("mcp", "deepagents", "langchain-core", "langgraph", "deepviz-agent-toolkit"):
        versions[name] = importlib.metadata.version(name)
    identity = {"mode": mode, "python": sys.version, "executable": sys.executable,
                "declared_checkpoint": CHECKPOINT, "modules": modules, "versions": versions,
                "probe": fingerprint(Path(__file__)), "provider_calls": 0,
                "distribution_editable": editable}
    if mode == "source":
        identity["git_head"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repository, text=True,
        ).strip()
        dirty_source = subprocess.check_output(
            ["git", "diff", CHECKPOINT, "--", "python/deepviz/src"], cwd=repository, text=True,
        )
        assert not dirty_source, "Production source differs from the declared checkpoint"
    return identity


def metadata(result) -> dict:
    from mcp import types

    assert not result.isError, "Expected successful MCP tool call"
    text = next(block.text for block in result.content if isinstance(block, types.TextContent))
    value = json.loads(text)
    assert "records" not in value and "paths" not in value
    assert len(text.encode("utf-8")) < 16_000
    return value


def assert_manifest(value: dict, engine: str) -> None:
    assert value["engine"] == engine and value["strategy"] == "sum"
    chart = value["charts"][0]
    assert chart["records"] == EXPECTED
    assert (chart["input_count"], chart["output_count"]) == (4, 3)
    assert chart["requested_kind"] == chart["rendered_kind"] == "bar"


@asynccontextmanager
async def connected(root: Path, mode: str, journal: list, *, data_dir: Path | None = None):
    import anyio
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client import stdio

    root.mkdir(parents=True, exist_ok=True)
    output = root / "server-output"
    arguments = ["-m", "deepviz.mcp_server", "--output-dir", str(output)]
    if data_dir is not None:
        arguments += ["--data-dir", str(data_dir)]
    env = {"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg",
           "PYTHONDONTWRITEBYTECODE": "1"}
    if mode == "source":
        import deepviz

        env["PYTHONPATH"] = str(Path(deepviz.__file__).resolve().parent.parent)
    parameters = StdioServerParameters(command=sys.executable, args=arguments, cwd=str(root), env=env)
    # Observation only: the official SDK still creates/owns the real process and transport.
    factory = stdio._create_platform_compatible_process
    receiver = stdio.TextReceiveStream
    processes, chunks = [], []

    async def observe_process(*args, **kwargs):
        process = await factory(*args, **kwargs)
        processes.append(process)
        return process

    async def observe_stdout(*args, **kwargs):
        async for chunk in receiver(*args, **kwargs):
            chunks.append(chunk)
            yield chunk

    with patch.object(stdio, "_create_platform_compatible_process", observe_process), patch.object(
        stdio, "TextReceiveStream", observe_stdout,
    ), (root / "server.stderr").open("w", encoding="utf-8") as stderr, anyio.fail_after(120):
        async with stdio.stdio_client(parameters, errlog=stderr) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
                initialized = await session.initialize()
                assert initialized.serverInfo.name == "DeepViz"
                yield session, output
    assert len(processes) == 1 and processes[0].returncode == 0, "Server did not exit gracefully"
    lines = "".join(chunks).splitlines()
    assert lines
    for line in lines:
        types.JSONRPCMessage.model_validate_json(line)
    journal.append({"server": root.name, "processes": len(processes), "exit_code": processes[0].returncode,
                    "jsonrpc_stdout_lines": len(lines), "shutdown": "SDK closed stdin; server exited 0"})


async def mcp_lifecycle(root: Path, mode: str) -> dict:
    from mcp import types
    from mcp.shared.exceptions import McpError

    servers, resources, denials = [], [], []
    secret = root / "outside.json"
    secret.parent.mkdir(parents=True, exist_ok=True)
    secret.write_text('[{"secret":"ROLE10-NOT-AUTHORIZED"}]', encoding="utf-8")

    def denied(result, name: str) -> None:
        assert result.isError, name
        assert "ROLE10-NOT-AUTHORIZED" not in result.model_dump_json()
        denials.append(name)

    async with connected(root / "first", mode, servers) as (session, output):
        tools = (await session.list_tools()).tools
        assert {tool.name for tool in tools} == NAMES
        assert all(tool.inputSchema.get("additionalProperties") is False for tool in tools)
        assert not (await session.list_resources()).resources
        denied(await session.call_tool("recommend_chart", {"data": {"dataset_id": "missing"}}),
               "missing-handle")
        profile = metadata(await session.call_tool("normalize_data", {"data": ROWS}))
        handle = {"dataset_id": profile["dataset_id"]}
        assert profile["input_count"] == profile["output_count"] == 4
        assert "Alpha" not in json.dumps(profile)
        advice = metadata(await session.call_tool("recommend_chart", {"data": handle}))
        all_uris, delete_target, old_uri = set(), None, None
        for engine in ENGINES:
            result = await session.call_tool(f"render_{engine}", {"data": handle, "spec": advice["spec"]})
            info = metadata(result)
            assert (info["input_count"], info["output_count"]) == (4, 3)
            links = [block for block in result.content if isinstance(block, types.ResourceLink)]
            assert {str(link.uri) for link in links} == {item["uri"] for item in info["resources"]}
            for link in links:
                assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", link.name)
                response = await session.read_resource(link.uri)
                assert len(response.contents) == 1
                block = response.contents[0]
                content = base64.b64decode(block.blob, validate=True) if isinstance(
                    block, types.BlobResourceContents,
                ) else block.text.encode("utf-8")
                destination = root / "retrieved" / engine / link.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
                matches = [path for path in output.rglob(link.name) if path.read_bytes() == content]
                assert matches, "Resource bytes differ from server artifact"
                if link.mimeType == "application/json":
                    assert_manifest(json.loads(content), engine)
                elif link.mimeType == "image/png":
                    assert content.startswith(b"\x89PNG\r\n\x1a\n")
                    image = next(b for b in result.content if isinstance(b, types.ImageContent))
                    assert base64.b64decode(image.data, validate=True) == content
                elif link.mimeType == "image/svg+xml":
                    assert ElementTree.fromstring(content).tag.endswith("}svg")
                else:
                    assert b"<html" in content.lower() or b"<!doctype" in content.lower()
                resources.append({"engine": engine, **fingerprint(destination)})
                all_uris.add(str(link.uri))
                if engine == "echarts" and link.mimeType == "text/html":
                    delete_target, old_uri = matches[0], str(link.uri)
        assert {str(resource.uri) for resource in (await session.list_resources()).resources} == all_uris
        for value in ({"file": "rows.json"}, {"file": str(secret)}, str(secret), json.dumps(str(secret)),
                      {"file": "../outside.json"}, {"file": "https://example.invalid/data"}):
            denied(await session.call_tool("normalize_data", {"data": value}), "no-default-file-authority")
        denied(await session.call_tool("render_echarts", {
            "data": handle, "spec": SPEC, "output_dir": "caller-chosen",
        }), "caller-cannot-choose-output")
        for uri in (secret.as_uri(), "deepviz://artifacts/../../outside.json"):
            try:
                await session.read_resource(uri)
            except McpError as error:
                assert "ROLE10-NOT-AUTHORIZED" not in str(error)
            else:
                raise AssertionError("Arbitrary resource URI accepted")
        copied = metadata(await session.call_tool("normalize_data", {"data": json.dumps(handle)}))
        for index in range(31):
            metadata(await session.call_tool("normalize_data", {"data": [{"n": index}]}))
        for tool in ("normalize_data", "recommend_chart", "render_echarts"):
            arguments = {"data": handle}
            if tool == "render_echarts":
                arguments["spec"] = SPEC
            denied(await session.call_tool(tool, arguments), "evicted-handle-" + tool)
        copied_handle = {"dataset_id": copied["dataset_id"]}
        copied_info = metadata(await session.call_tool("render_echarts", {"data": copied_handle, "spec": SPEC}))
        manifest_uri = next(r["uri"] for r in copied_info["resources"] if r["mime_type"] == "application/json")
        assert_manifest(json.loads((await session.read_resource(manifest_uri)).contents[0].text), "echarts")
        assert delete_target is not None and old_uri is not None
        delete_target.unlink()
        try:
            await session.read_resource(old_uri)
        except McpError:
            denials.append("deleted-registered-artifact")
        else:
            raise AssertionError("Deleted artifact remained readable")
        assert {tool.name for tool in (await session.list_tools()).tools} == NAMES

    async with connected(root / "restart", mode, servers) as (session, _):
        denied(await session.call_tool("recommend_chart", {"data": copied_handle}), "cross-session-stale-handle")
        assert not (await session.list_resources()).resources
        try:
            await session.read_resource(old_uri)
        except McpError:
            denials.append("cross-session-stale-resource")
        else:
            raise AssertionError("Another server's resource was accessible")

    allowed = root / "allowed"
    allowed.mkdir()
    file = allowed / "rows.json"
    write_json(file, ROWS)
    async with connected(root / "configured", mode, servers, data_dir=allowed) as (session, output):
        file_profile = metadata(await session.call_tool("normalize_data", {"data": {"file": "rows.json"}}))
        for value in ({"file": "../outside.json"}, {"file": str(secret)}, {"file": "C:outside.json"},
                      {"file": "https://example.invalid/data"}, str(file), json.dumps(str(file))):
            denied(await session.call_tool("normalize_data", {"data": value}), "configured-root-escape-or-string")
        file.unlink()
        file_handle = {"dataset_id": file_profile["dataset_id"]}
        assert metadata(await session.call_tool("recommend_chart", {"data": file_handle}))["input_count"] == 4
        denied(await session.call_tool("render_echarts", {"data": file_handle, "spec": SPEC}), "stale-file-render")
        assert not list(output.rglob("*"))
    assert secret.read_text(encoding="utf-8") == '[{"secret":"ROLE10-NOT-AUTHORIZED"}]'
    return {"servers": servers, "resources": resources, "initial_resource_count": len(resources),
            "denied_operations": denials, "copied_handle_survived_eviction": True,
            "stale_file_policy": "recommend uses cached profile; rendering rechecks the original file",
            "symlink_controls": "Not in this portable probe; prior Windows WinError1314 skips retained"}


def deep_agent_chain(root: Path) -> dict:
    from deepagents import create_deep_agent
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, ToolMessage
    from langchain_core.outputs import ChatGeneration, ChatResult

    from deepviz.tools import create_tools

    class LocalDecisions(BaseChatModel):
        @property
        def _llm_type(self):
            return "role10-deterministic-local-decisions-no-provider"

        def bind_tools(self, tools, **kwargs):
            return self

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            prior = [message for message in messages if isinstance(message, ToolMessage)]
            assert all(message.status == "success" for message in prior)
            if len(prior) == 7:
                message = AIMessage(content="Five artifacts ready; this was a local deterministic model.")
            else:
                if not prior:
                    name, arguments = "normalize_data", {"data": ROWS}
                elif len(prior) == 1:
                    name = "recommend_chart"
                    arguments = {"data": {"dataset_id": json.loads(prior[0].content)["dataset_id"]}}
                else:
                    advice = json.loads(prior[1].content)
                    name = f"render_{ENGINES[len(prior) - 2]}"
                    arguments = {"data": {"dataset_id": advice["dataset_id"]}, "spec": advice["spec"]}
                message = AIMessage(content="", tool_calls=[{
                    "name": name, "args": arguments, "id": f"role10-{len(prior)}",
                }])
            return ChatResult(generations=[ChatGeneration(message=message)])

    tools = create_tools(root / "output")
    assert {tool.name for tool in tools} == NAMES
    agent = create_deep_agent(model=LocalDecisions(), tools=tools)
    result = agent.invoke({"messages": [{"role": "user", "content": "Compare the known category amounts."}]},
                          config={"recursion_limit": 40})
    messages = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    assert [m.name for m in messages] == ["normalize_data", "recommend_chart", *[
        f"render_{engine}" for engine in ENGINES
    ]]
    summaries = []
    for message in messages:
        payload = json.loads(message.content)
        assert message.status == "success" and "records" not in payload
        size = len(message.content.encode("utf-8"))
        assert size < 16_000
        summaries.append({"name": message.name, "status": message.status, "actual_content_bytes": size})
        if message.name.startswith("render_"):
            engine = message.name.removeprefix("render_")
            paths = [Path(value).resolve() for value in payload["paths"]]
            assert all(path.is_relative_to(root.resolve()) and path.is_file() for path in paths)
            manifest = next(path for path in paths if path.name == "manifest.json")
            assert_manifest(json.loads(manifest.read_text(encoding="utf-8")), engine)
    return {"tool_messages": summaries, "model": "deterministic-local; actual framework and tools",
            "provider_calls": 0, "host_widget": False}


def run_probe(output: Path, mode: str, expected_module_root: Path | None = None) -> dict:
    identity = runtime_identity(mode, expected_module_root)
    output.mkdir(parents=True, exist_ok=True)
    result = {"identity": identity, "mcp": asyncio.run(mcp_lifecycle(output / "mcp", mode)),
              "deep_agent": deep_agent_chain(output / "agent")}
    write_json(output / "summary.json", result)
    return result


def test_portable_real_stdio_and_local_agent(tmp_path: Path) -> None:
    mode = os.environ.get("R10_RUNTIME_MODE", "source")
    expected = os.environ.get("R10_EXPECTED_MODULE_ROOT")
    output = Path(os.environ.get("R10_ARTIFACT_ROOT", str(tmp_path)))
    run = Path(tempfile.mkdtemp(prefix="pytest-run-", dir=output)) if output.exists() else output
    result = run_probe(run, mode, Path(expected) if expected else None)
    assert result["mcp"]["initial_resource_count"] == 13
    assert len(result["deep_agent"]["tool_messages"]) == 7


def test_installed_label_rejects_editable_distribution() -> None:
    import pytest

    distribution = importlib.metadata.distribution("deepviz-agent-toolkit")
    direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
    if not direct_url.get("dir_info", {}).get("editable", False):
        pytest.skip("This negative control requires an actual editable runtime")
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    code = (
        "import importlib.util,sys;"
        "spec=importlib.util.spec_from_file_location('role10_guard',sys.argv[1]);"
        "module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);"
        "module.runtime_identity('installed')"
    )
    result = subprocess.run([sys.executable, "-c", code, str(Path(__file__).resolve())],
                            env=environment, capture_output=True, text=True, timeout=60)
    assert result.returncode != 0, "An editable source checkout was accepted as a clean installed wheel"
    assert "Installed mode" in result.stderr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--mode", choices=("source", "installed"), required=True)
    parser.add_argument("--expected-module-root", type=Path)
    options = parser.parse_args()
    options.output_dir.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="run-", dir=options.output_dir))
    run_probe(directory, options.mode, options.expected_module_root)
    print(json.dumps({"summary": str(directory / "summary.json"), "mode": options.mode,
                      "stdio_servers": 3, "retrieved_resources": 13, "agent_tool_calls": 7,
                      "provider_calls": 0}, indent=2))
