"""R10-15 strict input-ownership regressions; intentionally RED until owner fixes F1.

Run with any installed DeepViz source via PYTHONPATH. Tests inspect real owned
handles and retain error tracebacks; they neither patch cleanup nor edit source.
Only each test's own handles are closed in finally blocks after observations.
"""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
from typing import Any

import pytest

from deepviz.normalize import normalize

RAW = {"kind": "table", "aggregation": "none", "max_points": 100}
COLUMNAR = {"arrow-file", "arrow-stream", "parquet"}


def _text_source(carrier: str, phase: str) -> str:
    rows: list[dict[str, Any]]
    if phase in {"parse", "parse-first"}:
        if carrier == "json":
            return "not-json"
        if carrier == "jsonl":
            return "not-json\n" if phase == "parse-first" else '{"id":1}\nnot-json\n'
        return "id,label\n1,a,extra\n".replace(",", "\t" if carrier == "tsv" else ",")
    if phase.startswith("flatten"):
        rows = ([{"safe": 1}] * 35 if phase == "flatten-late" else []) + [
            {"a.b": 1, "a": {"b": 2}}, {"safe": 3},
        ]
    elif phase == "plan":
        rows = [{"label": "a", "note": "b"} for _ in range(40)]
    else:
        rows = [{"id": 1, "label": "α"}, {"id": 2, "label": "β"}]
    if carrier == "json":
        return json.dumps(rows, ensure_ascii=False)
    if carrier == "jsonl":
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter="\t" if carrier == "tsv" else ",")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _write_source(tmp_path: Path, carrier: str, phase: str) -> Path:
    path = tmp_path / ("input." + ("arrow" if carrier.startswith("arrow") else carrier))
    if carrier not in COLUMNAR:
        path.write_text(_text_source(carrier, phase), encoding="utf-8")
        return path
    arrow = pytest.importorskip("pyarrow", reason="Optional columnar adapters require pyarrow")
    if phase == "schema-duplicate":
        table = arrow.Table.from_arrays([arrow.array([1, 2]), arrow.array([3, 4])], names=["v", "v"])
    elif phase == "flatten":
        table = arrow.table({"a.b": [1, 2], "a": [{"b": 3}, {"b": 4}]})
    elif phase == "plan":
        table = arrow.table({"label": ["a"] * 40, "note": ["b"] * 40})
    else:
        table = arrow.table({"id": [1, 2], "label": ["α", "β"]})
    if carrier == "parquet":
        import pyarrow.parquet as parquet

        parquet.write_table(table, path)
    else:
        factory = arrow.ipc.new_stream if carrier == "arrow-stream" else arrow.ipc.new_file
        with path.open("wb") as sink, factory(sink, table.schema) as writer:
            writer.write_table(table)
    return path


def _spec(carrier: str, phase: str) -> dict[str, Any]:
    return dict(
        RAW, format="arrow" if carrier.startswith("arrow") else carrier,
        aggregation="sum" if phase == "plan" else "none",
    )


def _owned_handles(path: Path, carrier: str, monkeypatch: pytest.MonkeyPatch) -> list[Any]:
    """Record real library-owned resources, leaving their context behavior intact."""
    handles: list[Any] = []
    if carrier.startswith("arrow"):
        arrow = pytest.importorskip("pyarrow")
        original = arrow.input_stream

        def track_arrow(*args: Any, **kwargs: Any):
            handle = original(*args, **kwargs)
            handles.append(handle)
            return handle

        monkeypatch.setattr(arrow, "input_stream", track_arrow)
    elif carrier == "parquet":
        pytest.importorskip("pyarrow")
        import pyarrow.parquet as parquet

        original = parquet.ParquetFile

        def track_parquet(*args: Any, **kwargs: Any):
            handle = original(*args, **kwargs)
            handles.append(handle)
            return handle

        monkeypatch.setattr(parquet, "ParquetFile", track_parquet)
    else:
        original_open = Path.open

        def track_text(self: Path, *args: Any, **kwargs: Any):
            handle = original_open(self, *args, **kwargs)
            if self == path and args and str(args[0]).startswith("r"):
                handles.append(handle)
            return handle

        monkeypatch.setattr(Path, "open", track_text)
    return handles


ERROR_CASES = [
    ("jsonl", "flatten"), ("jsonl", "flatten-late"), ("jsonl", "plan"),
    ("csv", "plan"), ("tsv", "plan"),
    ("arrow-file", "flatten"), ("arrow-stream", "flatten"), ("parquet", "flatten"),
    ("arrow-file", "plan"), ("arrow-stream", "plan"), ("parquet", "plan"),
]


@pytest.mark.parametrize("carrier,phase", ERROR_CASES)
def test_owned_input_closed_before_downstream_error_returns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, record_property, carrier: str, phase: str,
) -> None:
    path = _write_source(tmp_path, carrier, phase)
    handles = _owned_handles(path, carrier, monkeypatch)
    match = "numeric y" if phase == "plan" else "Flattened field collision"
    with pytest.raises(ValueError, match=match) as caught:
        normalize(path, _spec(carrier, phase))
    assert caught.traceback is not None  # Deliberately keep the caller's error alive.
    rename_error = None
    try:
        assert handles, "Oracle must observe at least one actual owned input resource"
        closed = [handle.closed for handle in handles]
        try:
            path.rename(path.with_suffix(path.suffix + ".renamed"))
        except OSError as error:
            rename_error = {"type": type(error).__name__, "errno": error.errno, "winerror": getattr(error, "winerror", None)}
        record_property("owned_handles_closed", json.dumps(closed))
        record_property("rename_error", json.dumps(rename_error))
        record_property("traceback_retained", "true")
        assert all(closed), f"Owned {carrier} input still open after {phase} failure; rename={rename_error}"
        if os.name == "nt":
            assert rename_error is None, "Owned input must be unlockable on Windows before error returns"
    finally:
        for handle in handles:
            handle.close()


CONTROL_CASES = [
    *[(carrier, phase) for carrier in ("json", "jsonl", "csv", "tsv") for phase in ("success", "parse")],
    ("json", "flatten"), ("json", "plan"),
    *[(carrier, phase) for carrier in ("arrow-file", "arrow-stream", "parquet") for phase in ("success", "schema-duplicate")],
]


@pytest.mark.parametrize("carrier,phase", CONTROL_CASES)
def test_owned_success_or_parser_originated_error_closes_its_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, carrier: str, phase: str,
) -> None:
    path = _write_source(tmp_path, carrier, phase)
    handles = _owned_handles(path, carrier, monkeypatch)
    try:
        if phase == "success":
            output = normalize(path, _spec(carrier, phase))
            assert output.records == [{"id": 1, "label": "α"}, {"id": 2, "label": "β"}]
            assert output.input_count == 2
        else:
            match = {"parse": "JSON|column count", "flatten": "Flattened field collision", "plan": "numeric y", "schema-duplicate": "Duplicate"}[phase]
            with pytest.raises(ValueError, match=match) as caught:
                normalize(path, _spec(carrier, phase))
            assert caught.traceback is not None
        assert handles, "Oracle must observe an actual owned resource"
        assert all(handle.closed for handle in handles)
        path.rename(path.with_suffix(path.suffix + ".renamed"))
    finally:
        for handle in handles:
            handle.close()


CALLER_CASES = [
    *[(carrier, phase) for carrier in ("json", "jsonl") for phase in ("success", "parse", "flatten", "plan")],
    *[(carrier, phase) for carrier in ("csv", "tsv") for phase in ("success", "parse", "plan")],
    ("jsonl", "parse-first"),
]


@pytest.mark.parametrize("carrier,phase", CALLER_CASES)
def test_caller_owned_text_stream_is_never_closed_by_normalize(carrier: str, phase: str) -> None:
    """A source cleanup fix must not transfer caller-owned text stream ownership."""
    stream = io.StringIO(_text_source(carrier, phase))
    try:
        if phase == "success":
            output = normalize(stream, _spec(carrier, phase))
            assert output.input_count == 2
            assert len(output.records) == 2
        else:
            match = {"parse": "JSON|column count", "parse-first": "JSON", "flatten": "Flattened field collision", "plan": "numeric y"}[phase]
            with pytest.raises(ValueError, match=match) as caught:
                normalize(stream, _spec(carrier, phase))
            assert caught.traceback is not None
        assert not stream.closed
        stream.seek(0)
        assert stream.read(1), "Caller must retain usable access to its stream"
    finally:
        stream.close()


def test_caller_owned_real_text_file_remains_open_after_second_line_parse_error(tmp_path: Path) -> None:
    path = tmp_path / "caller-owned.jsonl"
    path.write_text('{"id":1}\nnot-json\n', encoding="utf-8")
    with path.open("r", encoding="utf-8") as stream:
        with pytest.raises(ValueError, match="line 2") as caught:
            normalize(stream, _spec("jsonl", "parse"))
        assert caught.traceback is not None
        assert not stream.closed, "Only the caller may close this borrowed real file"
        stream.seek(0)
        assert stream.readline() == '{"id":1}\n'
