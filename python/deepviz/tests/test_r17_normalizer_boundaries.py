"""Public source-lifetime regressions for the R17 normalizer boundary repair."""
from __future__ import annotations

import io
import json
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize


@pytest.mark.parametrize("phase", ["plan", "late-flatten", "selected-path-plan"])
def test_owned_jsonl_unwinds_before_downstream_exception_returns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str,
) -> None:
    path = tmp_path / "owned.jsonl"
    records: list[dict[str, Any]] = [{"label": "a", "note": "b"} for _ in range(40)]
    if phase == "late-flatten":
        records[35] = {"a.b": 1, "a": {"b": 2}}
    if phase == "selected-path-plan":
        records = [{"page": record} for record in records]
    path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
    handles: list[Any] = []
    original = Path.open

    def opened(self: Path, *args: Any, **kwargs: Any) -> Any:
        file = original(self, *args, **kwargs)
        if self == path:
            handles.append(file)
        return file

    monkeypatch.setattr(Path, "open", opened)
    spec: dict[str, Any] = {"kind": "bar", "format": "jsonl", "aggregation": "sum"}
    if phase == "late-flatten":
        spec["aggregation"] = "none"
    elif phase == "selected-path-plan":
        spec["data_path"] = "page"
    message = "collision" if phase == "late-flatten" else "numeric y"
    try:
        with pytest.raises(ValueError, match=message) as caught:
            normalize(path, spec)
        assert caught.traceback is not None
        assert handles and all(file.closed for file in handles), "Owned adapter must unwind even with retained traceback"
        moved = path.with_suffix(".unlocked")
        path.rename(moved)
        assert moved.exists()
    finally:
        for file in handles:
            file.close()


def test_borrowed_generator_is_not_closed_when_planning_raises() -> None:
    closed: list[bool] = []

    def records() -> Generator[dict[str, str], None, None]:
        try:
            for _ in range(40):
                yield {"label": "a", "note": "b"}
        finally:
            closed.append(True)

    source = records()
    try:
        with pytest.raises(ValueError, match="numeric y") as caught:
            normalize(source, {"kind": "bar", "aggregation": "sum"})
        assert caught.traceback is not None
        assert closed == [], "Do not transfer caller generator ownership on downstream failure"
        assert next(source) == {"label": "a", "note": "b"}
    finally:
        source.close()
    assert closed == [True]


def test_borrowed_second_line_jsonl_parse_failure_keeps_stream_usable() -> None:
    source = io.StringIO('{"v":1}\nnot-json\n')
    try:
        with pytest.raises(ValueError, match="line 2") as caught:
            normalize(source, {"kind": "table", "format": "jsonl", "aggregation": "none"})
        assert caught.traceback is not None
        assert not source.closed
        source.seek(0)
        assert source.readline() == '{"v":1}\n'
    finally:
        source.close()
