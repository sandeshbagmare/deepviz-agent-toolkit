"""Registered file handles stay live across callback-admitted recommendations."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from langchain_core.callbacks import BaseCallbackHandler

from deepviz.tools import create_tools

METHODS = ("run", "arun", "invoke", "ainvoke")
ROWS = [{"label": "before 東京", "value": 3}]
UPDATED = [
    {"date": "2026-01-01", "amount": 2},
    {"date": "2026-01-02", "amount": 4},
]
RUN_ID = UUID("05000000-0000-4000-8000-000000000016")


class Trace(BaseCallbackHandler):
    run_inline = True

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
        self.events.append(("start", {**kwargs, "input_str": input_str}))

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        self.events.append(("end", {**kwargs, "output": output}))

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        self.events.append(("error", {**kwargs, "error_type": type(error).__name__}))


def call(tool: Any, method: str, value: Any, trace: Trace) -> Any:
    config = {
        "callbacks": [trace],
        "tags": ["r50-live-handle"],
        "metadata": {"r50": "compatibility"},
        "run_name": "r50-live-handle",
        "run_id": RUN_ID,
    }
    if method in {"invoke", "ainvoke"}:
        result = getattr(tool, method)(value, config=config)
    else:
        result = getattr(tool, method)(value, **config)
    return asyncio.run(result) if method in {"arun", "ainvoke"} else result


@pytest.mark.parametrize("method", METHODS)
def test_bare_registered_file_handle_rereads_mutated_file_per_call(
    method: str, tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    source = data_dir / "safe.json"
    source.write_text(json.dumps(ROWS), encoding="utf-8")
    tools = {tool.name: tool for tool in create_tools(tmp_path / "out", data_dir=data_dir)}
    normalize, recommend = tools["normalize_data"], tools["recommend_chart"]
    handle = normalize.run({"data": {"file": "safe.json"}})["dataset_id"]
    source.write_text(json.dumps(UPDATED), encoding="utf-8")

    bare_trace = Trace()
    live = call(recommend, method, json.dumps({"dataset_id": handle}), bare_trace)
    assert live["input_count"] == 2
    assert live["dataset_id"] != handle
    assert live["spec"]["kind"] == "histogram"
    assert live["spec"]["x"] == "amount"
    assert [kind for kind, _ in bare_trace.events] == ["start", "end"]
    start, end = bare_trace.events[0][1], bare_trace.events[1][1]
    assert start["run_id"] == end["run_id"] == RUN_ID
    assert start["tags"] == end["tags"] == ["r50-live-handle"]
    assert start["metadata"] == {"r50": "compatibility"}
    # e47 reports no structured callback inputs for a bare string; f48's
    # accepted canonical envelope is covered by the existing R41 suite.

    # Explicit data objects retain the existing cached-summary recommendation semantics.
    explicit_input = {"data": {"dataset_id": handle}}
    explicit_trace = Trace()
    cached = call(recommend, method, explicit_input, explicit_trace)
    assert explicit_input == {"data": {"dataset_id": handle}}
    assert cached["input_count"] == 1 and cached["dataset_id"] == handle
    assert cached["spec"]["kind"] == "bar"
    assert (cached["spec"]["x"], cached["spec"]["y"]) == ("label", "value")
    assert [kind for kind, _ in explicit_trace.events] == ["start", "end"]
    assert not (tmp_path / "out").exists()


def invalid_json(case: str) -> str:
    if case == "duplicate":
        return r'[{"value":1,"\u0076alue":2}]'
    if case == "depth":
        return "[" * 5000 + "]" * 5000
    small = json.dumps(ROWS, ensure_ascii=False)
    raw = " " * (1_000_001 - len(small.encode("utf-8"))) + small
    assert len(raw) < 1_000_000 < len(raw.encode("utf-8"))
    return raw


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("case", ("duplicate", "depth", "utf8-bytes"))
def test_invalid_original_json_rejects_before_callbacks_and_same_tool_recovers(
    method: str, case: str, tmp_path: Path,
) -> None:
    output = tmp_path / "out"
    tool = next(tool for tool in create_tools(output) if tool.name == "recommend_chart")
    rejected = Trace()
    with pytest.raises(ValueError):
        call(tool, method, {"data": invalid_json(case)}, rejected)
    assert rejected.events == []
    assert not output.exists()

    recovered = Trace()
    result = call(tool, method, {"data": json.dumps(ROWS)}, recovered)
    assert result["input_count"] == 1
    assert [kind for kind, _ in recovered.events] == ["start", "end"]
