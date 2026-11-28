"""Exercise the local tools without a model provider or remote service."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from deepviz.models import ChartSpec, NormalizedData

ROWS = [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}]
SPEC = {"kind": "bar", "x": "month", "y": "revenue", "title": "Revenue"}
RENDER_NAMES = {f"render_{engine}" for engine in ["matplotlib", "plotly", "vega", "echarts", "antv"]}


def test_profile_classifies_observed_fields_without_raw_values():
    assert importlib.util.find_spec("deepviz.recommend") is not None
    from deepviz.recommend import profile

    observed = profile(NormalizedData([
        {"date": "2026-01-01", "value": 12, "part": "secret-alpha", "flag": True},
        {"date": "2026-01-02", "value": 18, "part": "secret-beta", "flag": False},
    ], 2))

    assert observed["numeric_fields"] == ["value"]
    assert observed["temporal_fields"] == ["date"]
    assert observed["categorical_fields"] == ["part", "flag"]
    assert observed["nonnegative_fields"] == ["value"]
    assert observed["positive_total_fields"] == ["value"]
    assert observed["profiled_rows"] == 2
    assert "secret-" not in json.dumps(observed)


@pytest.mark.parametrize(("goal", "rows", "expected"), [
    ("trend", [{"date": "2026-01-01", "value": 1}], ("line", "date", "value")),
    ("relationship", [{"a": 1, "b": 2}], ("scatter", "a", "b")),
    ("distribution", [{"value": 1}], ("histogram", "value", None)),
    ("composition", [{"part": "A", "value": 1}], ("pie", "part", "value")),
    ("composition", [{"part": "A", "value": -1}], ("bar", "part", "value")),
    ("composition", [{"part": "A", "value": 0}], ("bar", "part", "value")),
    ("comparison", [{"text": "A"}], ("table", None, None)),
])
def test_recommendation_returns_an_editable_validated_spec(goal, rows, expected):
    from deepviz.recommend import profile, recommend

    result = recommend(profile(NormalizedData(rows, len(rows))), goal)
    chart = ChartSpec.model_validate(result["spec"])

    assert (chart.kind, chart.x, chart.y) == expected
    assert result["engine"] == "matplotlib"
    assert result["rationale"]
    assert result["warnings"]


def test_profile_bounds_field_names_and_count():
    from deepviz.recommend import profile

    row = {f"field_{index}": index for index in range(110)}
    row["x" * 10000] = 12
    observed = profile(NormalizedData([row], 1))

    assert len(observed["fields"]) == 100
    assert observed["fields_truncated"] is True
    assert all(len(name) <= 256 for name in observed["fields"])


def test_tools_import_and_local_session_do_not_require_optional_dependencies(tmp_path):
    code = """
import importlib.abc, sys
class BlockOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'langchain_core', 'deepagents', 'mcp'}:
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, BlockOptional())
from deepviz.tools import ToolSession, create_tools
session = ToolSession(sys.argv[1])
assert session._source([{'x': 1}]) == [{'x': 1}]
try:
    create_tools(sys.argv[1])
except ImportError as exc:
    assert 'agents' in str(exc)
else:
    raise AssertionError('Missing optional agents package must be actionable')
"""
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True,
                            text=True, timeout=30)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("data", [float("nan"), {"x": float("inf")}, object(), 1, True, None])
def test_tool_session_rejects_non_json_container_inputs(tmp_path, data):
    from deepviz.tools import ToolSession

    with pytest.raises(ValueError, match="finite JSON|JSON array or object"):
        ToolSession(tmp_path)._source(data)


@pytest.mark.parametrize("data", ["../../secret.csv", '"../../secret.csv"', {"dataset_id": "absent"}])
def test_invalid_references_are_not_treated_as_executable_code_or_paths(tmp_path, data):
    from deepviz.tools import ToolSession

    with pytest.raises(ValueError):
        ToolSession(tmp_path)._source(data)


def test_file_references_require_host_data_directory_and_stay_inside_it(tmp_path):
    from deepviz.tools import ToolSession

    with pytest.raises(ValueError, match="data_dir"):
        ToolSession(tmp_path)._source({"file": "data.csv"})

    root = tmp_path / "input"
    root.mkdir()
    sentinel = tmp_path / "secret.csv"
    sentinel.write_text("secret", encoding="utf-8")
    session = ToolSession(tmp_path / "out", data_dir=root)
    for name in ["../secret.csv", str(sentinel.resolve()), "https://example.test/data.csv"]:
        with pytest.raises(ValueError):
            session._source({"file": name})
    assert sentinel.read_text(encoding="utf-8") == "secret"


def test_inline_size_limit_is_checked_in_utf8_bytes(tmp_path):
    from deepviz.tools import ToolSession

    with pytest.raises(ValueError, match="file reference"):
        ToolSession(tmp_path)._source('[{"x":"' + "\u00e9" * 510000 + '"}]')


@pytest.mark.parametrize("method", ["run", "arun", "invoke", "ainvoke"])
@pytest.mark.parametrize("enveloped", [False, True])
def test_oversized_original_input_is_rejected_before_langchain_callbacks(tmp_path, method, enveloped):
    from deepviz.tools import create_tools
    from langchain_core.callbacks import BaseCallbackHandler

    class Observe(BaseCallbackHandler):
        def __init__(self):
            self.events = []

        def on_tool_start(self, *args, **kwargs):
            self.events.append("start")

        def on_tool_error(self, *args, **kwargs):
            self.events.append("error")

    trace = Observe()
    tool = next(tool for tool in create_tools(tmp_path) if tool.name == "normalize_data")
    raw = " " * 1_000_001 + "[]"
    data = {"data": raw} if enveloped else raw
    kwargs = {"config": {"callbacks": [trace]}} if "invoke" in method else {"callbacks": [trace]}
    with pytest.raises(ValueError, match="file reference"):
        result = getattr(tool, method)(data, **kwargs)
        if method in {"arun", "ainvoke"}:
            asyncio.run(result)
    assert trace.events == []


def test_tools_provide_real_local_normalize_recommend_render_flow(tmp_path):
    from deepviz.tools import create_tools

    tools = {tool.name: tool for tool in create_tools(tmp_path)}
    assert set(tools) == RENDER_NAMES | {"normalize_data", "recommend_chart"}
    normalized = tools["normalize_data"].invoke({"data": ROWS})
    recommended = tools["recommend_chart"].invoke({"data": {"dataset_id": normalized["dataset_id"]}})
    rendered = tools["render_matplotlib"].invoke({
        "data": {"dataset_id": normalized["dataset_id"]}, "spec": recommended["spec"],
    })

    assert normalized["input_count"] == 2
    assert normalized["output_count"] == 2
    assert "records" not in normalized
    assert "Jan" not in json.dumps(normalized)
    assert recommended["spec"]["kind"] == "bar"
    assert (recommended["spec"]["x"], recommended["spec"]["y"]) == ("month", "revenue")
    assert rendered["input_count"] == 2
    assert rendered["output_count"] == 2
    png = next(Path(name) for name in rendered["paths"] if name.endswith(".png"))
    assert png.is_relative_to(tmp_path)
    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_tool_session_copies_inline_data_before_caching(tmp_path):
    from deepviz.tools import ToolSession

    rows = [{"month": "Jan", "revenue": 12}]
    session = ToolSession(tmp_path)
    result = session.normalize_data(rows)
    rows[0]["revenue"] = 999

    assert session._source({"dataset_id": result["dataset_id"]}) == [{"month": "Jan", "revenue": 12}]


def test_encoded_alias_remains_usable_after_original_handle_expires(tmp_path):
    from deepviz.tools import ToolSession

    session = ToolSession(tmp_path)
    first = session.normalize_data(ROWS)
    alias = session.normalize_data(json.dumps({"dataset_id": first["dataset_id"]}))
    for index in range(31):
        session.normalize_data([{"x": index}])

    with pytest.raises(ValueError, match="expired"):
        session._source({"dataset_id": first["dataset_id"]})
    assert session._source({"dataset_id": alias["dataset_id"]}) == ROWS


def test_tools_preserve_original_input_count_after_bounded_profile(tmp_path):
    from deepviz.tools import ToolSession

    session = ToolSession(tmp_path)
    rows = [{"x": index, "y": index * 2} for index in range(150)]
    spec = {"kind": "scatter", "x": "x", "y": "y", "max_points": 10, "aggregation": "sample"}
    normalized = session.normalize_data(rows, spec)
    rendered = session.render_chart("matplotlib", {"dataset_id": normalized["dataset_id"]}, spec)

    assert normalized["input_count"] == 150
    assert normalized["output_count"] == 10
    assert rendered["input_count"] == 150
    assert rendered["output_count"] == 10


def test_failed_render_cleans_only_its_request_directory(tmp_path):
    from deepviz.tools import ToolSession

    data_dir, output_dir = tmp_path / "input", tmp_path / "out"
    data_dir.mkdir()
    output_dir.mkdir()
    source = data_dir / "invalid.json"
    source.write_text("this is not JSON", encoding="utf-8")
    sentinel = output_dir / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    session = ToolSession(output_dir, data_dir=data_dir)

    with pytest.raises(ValueError, match="JSON"):
        session.render_chart("matplotlib", {"file": "invalid.json"}, {**SPEC, "format": "json"})

    assert source.read_text(encoding="utf-8") == "this is not JSON"
    assert list(output_dir.iterdir()) == [sentinel]
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_model_cannot_select_output_directory_or_executable_spec_fields(tmp_path):
    from deepviz.tools import create_tools

    tool = next(tool for tool in create_tools(tmp_path) if tool.name == "render_matplotlib")
    for extra in [{"output_dir": "../outside"}, {"spec": {**SPEC, "eval": "forbidden"}}]:
        with pytest.raises(ValueError):
            tool.invoke({"data": ROWS, "spec": SPEC, **extra})
    assert not list(tmp_path.iterdir())
