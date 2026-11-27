"""Real-SDK admission before tracing, with canonical successful data envelopes."""
from __future__ import annotations

import asyncio
import importlib
import json
import sys
import threading
from copy import deepcopy
from pathlib import Path
from types import FrameType
from typing import Any
from uuid import UUID

import pytest
from langchain_core.callbacks import BaseCallbackHandler

from deepviz.tools import create_tools

METHODS = ("run", "arun", "invoke", "ainvoke")
ROWS = [{"label": "東京 📊", "value": 3}, {"label": "B", "value": 7}]
RUN_ID = UUID("04100000-0000-4000-8000-000000000016")


class Trace(BaseCallbackHandler):
    """Observe real SDK callbacks without replacing dispatch or keeping raw payloads."""

    run_inline = True

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []
        self.timeline: list[str] = []

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
        self.timeline.append("start")
        self.events.append(("start", {**kwargs, "input_bytes": len(input_str.encode("utf-8")),
                                      "tool": serialized["name"]}))

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        self.timeline.append("end")
        self.events.append(("end", {**kwargs, "output": output}))

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        self.timeline.append("error")
        self.events.append(("error", {**kwargs, "error_type": type(error).__name__}))


def execute(tool: Any, method: str, value: Any, trace: Trace) -> Any:
    options = {"callbacks": [trace], "tags": ["r41-admission"], "metadata": {"r41": "local"},
               "run_name": "r41-canonical", "run_id": RUN_ID}
    if method in {"invoke", "ainvoke"}:
        result = getattr(tool, method)(value, config=options, audit_marker="forwarded")
    else:
        result = getattr(tool, method)(value, **options, audit_marker="forwarded")
    return asyncio.run(result) if method in {"arun", "ainvoke"} else result


def tool_at(output: Path, name: str = "normalize_data", **kwargs: Any) -> Any:
    return next(tool for tool in create_tools(output, **kwargs) if tool.name == name)


def envelope(raw: Any, shape: str) -> Any:
    return raw if shape == "bare" else {"data": raw}


def without_handle(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "dataset_id"}


def invalid_raw(case: str) -> str:
    if case == "duplicate":
        return r'[{"value":1,"\u0076alue":2}]'
    if case == "depth":
        return "[" * 5000 + "]" * 5000
    small = json.dumps(ROWS, ensure_ascii=False)
    result = " " * (1_000_001 - len(small.encode("utf-8"))) + small
    assert len(result) < 1_000_000 < len(result.encode("utf-8"))
    return result


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("shape", ["bare", "dict"])
@pytest.mark.parametrize("case", ["duplicate", "bytes", "depth"])
def test_invalid_raw_never_reaches_any_callback_and_same_tool_recovers(
    method: str, shape: str, case: str, tmp_path: Path,
) -> None:
    output = tmp_path / "out"
    tool = tool_at(output)
    rejected, recovered = Trace(), Trace()
    with pytest.raises(ValueError) as error:
        execute(tool, method, envelope(invalid_raw(case), shape), rejected)
    assert len(str(error.value)) < 500
    result = execute(tool, method, envelope(json.dumps(ROWS), shape), recovered)
    assert result["input_count"] == result["output_count"] == 2
    assert [event for event, _ in recovered.events] == ["start", "end"]
    assert not output.exists()
    assert rejected.events == [], "Invalid original JSON reached SDK callback telemetry"


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("name", ["normalize_data", "recommend_chart"])
def test_valid_bare_and_dict_results_and_canonical_callback_config_are_equivalent(
    method: str, name: str, tmp_path: Path,
) -> None:
    tool = tool_at(tmp_path / "out", name)
    raw = " \n" + json.dumps(ROWS, ensure_ascii=True) + "\t "
    original = {"data": deepcopy(ROWS)}
    bare_trace, dict_trace = Trace(), Trace()
    bare = execute(tool, method, raw, bare_trace)
    explicit = execute(tool, method, original, dict_trace)
    assert without_handle(bare) == without_handle(explicit)
    assert bare["input_count"] == 2
    assert original == {"data": ROWS}
    if name == "normalize_data":
        assert bare["strategy"] == "sample" and bare["warnings"] == []
        assert bare["profile"]["numeric_fields"] == ["value"]
        assert bare["profile"]["categorical_fields"] == ["label"]
    else:
        assert bare["spec"]["kind"] == "bar"
        assert (bare["spec"]["x"], bare["spec"]["y"]) == ("label", "value")
    for trace in (bare_trace, dict_trace):
        assert [event for event, _ in trace.events] == ["start", "end"]
        start, end = trace.events[0][1], trace.events[1][1]
        assert start["inputs"] == {"data": ROWS}
        assert start["input_bytes"] == len(str({"data": ROWS}).encode("utf-8"))
        assert start["run_id"] == end["run_id"] == RUN_ID
        assert start["name"] == "r41-canonical" and end["name"] == name
        assert start["tags"] == end["tags"] == ["r41-admission"]
        assert start["metadata"] == {"r41": "local"}
        assert start["audit_marker"] == end["audit_marker"] == "forwarded"
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("shape", ["bare", "dict"])
def test_exact_original_utf8_limit_accepts_then_traces_only_canonical_data(
    method: str, shape: str, tmp_path: Path,
) -> None:
    small = json.dumps(ROWS, ensure_ascii=False)
    raw = " " * (1_000_000 - len(small.encode("utf-8"))) + small
    assert len(raw.encode("utf-8")) == 1_000_000
    trace = Trace()
    result = execute(tool_at(tmp_path / "out"), method, envelope(raw, shape), trace)
    assert result["input_count"] == 2
    assert [event for event, _ in trace.events] == ["start", "end"]
    assert trace.events[0][1]["inputs"] == {"data": ROWS}
    assert trace.events[0][1]["input_bytes"] < 500
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("method", METHODS)
def test_bare_normalize_keeps_default_table_sample_capacity(method: str, tmp_path: Path) -> None:
    rows = [{"label": f"r{index}", "value": index} for index in range(201)]
    trace = Trace()
    result = execute(tool_at(tmp_path / "out"), method, json.dumps(rows), trace)
    assert result["input_count"] == 201 and result["output_count"] == 200
    assert result["strategy"] == "sample" and result["warnings"]
    assert result["profile"]["profiled_rows"] == 200
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("shape", ["bare", "dict"])
def test_original_raw_has_one_strict_decode_before_start_without_sdk_patch(
    method: str, shape: str, tmp_path: Path,
) -> None:
    module = importlib.import_module("deepviz.normalize")
    strict_code, json_code = module._json.__code__, json.loads.__code__
    tool, trace = tool_at(tmp_path / "out"), Trace()

    def observe(frame: FrameType, event: str, arg: Any) -> None:
        if event == "call":
            if frame.f_code is strict_code:
                trace.timeline.append("strict-decode")
            elif frame.f_code is json_code:
                trace.timeline.append("json.loads")

    previous, threads = sys.getprofile(), threading.getprofile()
    sys.setprofile(observe)
    threading.setprofile(observe)
    try:
        result = execute(tool, method, envelope(json.dumps(ROWS), shape), trace)
    finally:
        sys.setprofile(previous)
        threading.setprofile(threads)
    assert result["input_count"] == 2
    assert trace.timeline == ["strict-decode", "json.loads", "start", "end"]


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("shape", ["bare", "dict", "encoded-kwargs"])
def test_bare_data_never_supplies_required_render_spec_or_unpacks_render_kwargs(
    method: str, shape: str, tmp_path: Path,
) -> None:
    value = json.dumps(ROWS)
    if shape == "encoded-kwargs":
        value = json.dumps({"data": ROWS, "spec": {"kind": "bar", "x": "label", "y": "value"}})
    trace = Trace()
    with pytest.raises(ValueError, match="spec"):
        execute(tool_at(tmp_path / "out", "render_matplotlib"), method,
                {"data": value} if shape == "dict" else value, trace)
    assert [event for event, _ in trace.events] == ["start", "error"]
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("method", METHODS)
def test_encoded_goal_is_data_but_explicit_goal_is_delegated(method: str, tmp_path: Path) -> None:
    tool = tool_at(tmp_path / "out", "recommend_chart")
    encoded = execute(tool, method, json.dumps({"data": ROWS, "goal": "distribution"}), Trace())
    explicit = execute(tool, method, {"data": ROWS, "goal": "distribution"}, Trace())
    assert encoded["spec"]["kind"] == "bar"
    assert explicit["spec"]["kind"] == "histogram"
    # A mixed data/goal object is one data record, not render/recommend kwargs.
    assert encoded["input_count"] == 1 and explicit["input_count"] == 2
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("method", METHODS)
def test_encoded_paths_and_copied_handles_keep_host_authority_and_reread_source(
    method: str, tmp_path: Path,
) -> None:
    root = tmp_path / "data"
    root.mkdir()
    safe = root / "safe.json"
    safe.write_text(json.dumps(ROWS), encoding="utf-8")
    outside = tmp_path / "outside.json"
    outside.write_text('[{"label":"outside","value":999}]', encoding="utf-8")
    sentinel = outside.read_bytes()
    reference = r'{"\u0066ile":"safe\u002ejson"}'
    with pytest.raises(ValueError, match="data_dir"):
        execute(tool_at(tmp_path / "disabled"), method, reference, Trace())
    tool = tool_at(tmp_path / "out", data_dir=root)
    first = execute(tool, method, reference, Trace())
    copied = execute(tool, method, json.dumps({"dataset_id": first["dataset_id"]}), Trace())
    assert first["input_count"] == copied["input_count"] == 2
    for name in ("../outside.json", str(outside), "C:\\outside.json", "https://invalid.test/x"):
        with pytest.raises(ValueError, match="relative|URLs|escapes"):
            execute(tool, method, json.dumps({"file": name}), Trace())
    with pytest.raises(ValueError, match="Unknown|expired"):
        execute(tool, method, json.dumps({"dataset_id": "absent"}), Trace())
    safe.write_text('[{"label":"new","value":1},{"label":"next","value":2},{"label":"last","value":3}]',
                    encoding="utf-8")
    reread = execute(tool, method, json.dumps({"dataset_id": copied["dataset_id"]}), Trace())
    assert reread["input_count"] == 3 and outside.read_bytes() == sentinel
    assert not (tmp_path / "out").exists() and not (tmp_path / "disabled").exists()


@pytest.mark.parametrize("method", ["run", "arun"])
@pytest.mark.parametrize("shape", ["bare", "dict"])
def test_positional_callback_and_color_arguments_are_forwarded(method: str, shape: str, tmp_path: Path) -> None:
    trace = Trace()
    result = getattr(tool_at(tmp_path / "out"), method)(
        envelope(json.dumps(ROWS), shape), False, "blue", "cyan", [trace], audit_marker="positional",
    )
    if method == "arun":
        result = asyncio.run(result)
    assert result["input_count"] == 2
    assert [event for event, _ in trace.events] == ["start", "end"]
    assert trace.events[0][1]["color"] == "blue" and trace.events[1][1]["color"] == "cyan"
    assert all(event[1]["audit_marker"] == "positional" for event in trace.events)


@pytest.mark.parametrize("method", ["run", "arun"])
def test_real_sync_and_async_dict_render_keeps_callbacks_and_native_artifacts(method: str, tmp_path: Path) -> None:
    rows = [{"label": "A", "value": 3}, {"label": "B", "value": 7}]
    spec = {"kind": "bar", "x": "label", "y": "value", "aggregation": "none", "title": "R41 callback admission"}
    trace = Trace()
    result = execute(tool_at(tmp_path / "out", "render_matplotlib"), method,
                     {"data": json.dumps(rows), "spec": spec}, trace)
    assert result["engine"] == "matplotlib" and result["input_count"] == result["output_count"] == 2
    assert [event for event, _ in trace.events] == ["start", "end"]
    paths = [Path(path) for path in result["paths"]]
    assert all(path.is_file() and path.resolve().is_relative_to((tmp_path / "out").resolve()) for path in paths)
    manifest = json.loads(next(path for path in paths if path.name == "manifest.json").read_text(encoding="utf-8"))
    assert manifest["charts"][0]["records"] == rows
    assert next(path for path in paths if path.suffix == ".png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert "R41 callback admission" in next(path for path in paths if path.suffix == ".svg").read_text(encoding="utf-8")
