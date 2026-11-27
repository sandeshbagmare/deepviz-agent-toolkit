"""NEW R13 reducer-budget/read-error ownership tests, not R10 field validation.

Only public normalize inputs and actual 16MiB guard are used. Finite fixtures
have <=270 rows and <=18MiB payload per carrier. Acquisition spies preserve real
context managers; deterministic EIO injection is limited to text-stream reads.
"""
from __future__ import annotations

import errno
import io
import json
import os
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz.normalize import normalize

ROWS = 270
GROUP_BYTES = 65_520
CARRIERS = ("csv", "jsonl", "arrow", "parquet")
BUDGET_SPEC = {"kind": "bar", "x": "g", "y": "v", "aggregation": "count", "max_points": 512}


def _row(index: int, unique: bool) -> dict[str, Any]:
    suffix = f"{index if unique else 0:04d}"
    return {"g": "a" * (GROUP_BYTES - len(suffix)) + suffix, "v": 1}


@pytest.fixture(scope="module")
def source_path(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str, bool], Path]:
    """Stream-write each requested finite fixture once; no raw datasets committed."""
    directory = tmp_path_factory.mktemp("r13-bounded-sources")
    cache: dict[tuple[str, bool], Path] = {}

    def make(carrier: str, unique: bool) -> Path:
        key = carrier, unique
        if key in cache:
            return cache[key]
        path = directory / f"{'unique' if unique else 'onegroup'}.{carrier}"
        if carrier in {"csv", "jsonl"}:
            with path.open("w", encoding="utf-8", newline="") as sink:
                if carrier == "csv":
                    sink.write("g,v\n")
                for index in range(ROWS):
                    row = _row(index, unique)
                    sink.write(f"{row['g']},1\n" if carrier == "csv" else json.dumps(row, separators=(",", ":")) + "\n")
        else:
            arrow = pytest.importorskip("pyarrow", reason="Optional Arrow/Parquet ownership cases require pyarrow")
            schema = arrow.schema([("g", arrow.string()), ("v", arrow.int64())])
            if carrier == "parquet":
                import pyarrow.parquet as parquet

                with parquet.ParquetWriter(path, schema) as writer:
                    for start in range(0, ROWS, 32):
                        writer.write_table(arrow.Table.from_pylist([_row(i, unique) for i in range(start, min(start + 32, ROWS))], schema=schema))
            else:
                with path.open("wb") as binary_sink, arrow.ipc.new_stream(binary_sink, schema) as writer:
                    for start in range(0, ROWS, 32):
                        writer.write_batch(arrow.RecordBatch.from_pylist([_row(i, unique) for i in range(start, min(start + 32, ROWS))], schema=schema))
        assert path.stat().st_size <= 18 * 1024 * 1024
        cache[key] = path
        return path

    return make


def _rename(path: Path) -> dict[str, Any] | None:
    """Observe actual filesystem behavior and preserve reusable synthetic fixture."""
    moved = path.with_suffix(path.suffix + ".rename-probe")
    try:
        path.rename(moved)
    except OSError as error:
        return {"type": type(error).__name__, "errno": error.errno, "winerror": getattr(error, "winerror", None)}
    moved.rename(path)
    return None


def _error_stage(error: BaseException) -> dict[str, Any]:
    stage: dict[str, Any] = {"frames": []}
    tb = error.__traceback__
    while tb is not None:
        frame = tb.tb_frame
        if frame.f_globals.get("__name__") == "deepviz.normalize":
            stage["frames"].append(frame.f_code.co_name)
            if frame.f_code.co_name == "normalize":
                stage["input_count"] = frame.f_locals.get("input_count")
                stage["prefix_rows"] = len(frame.f_locals.get("prefix", []))
        tb = tb.tb_next
    return stage


def _observe_acquisition(path: Path, carrier: str, monkeypatch: pytest.MonkeyPatch) -> list[Any]:
    resources: list[Any] = []
    if carrier == "arrow":
        arrow = pytest.importorskip("pyarrow")
        original = arrow.input_stream

        def opened(*args: Any, **kwargs: Any) -> Any:
            result = original(*args, **kwargs)
            resources.append(result)
            return result

        monkeypatch.setattr(arrow, "input_stream", opened)
    elif carrier == "parquet":
        pytest.importorskip("pyarrow")
        import pyarrow.parquet as parquet

        original = parquet.ParquetFile

        def opened_parquet(*args: Any, **kwargs: Any) -> Any:
            result = original(*args, **kwargs)
            resources.append(result)
            return result

        monkeypatch.setattr(parquet, "ParquetFile", opened_parquet)
    else:
        original_open = Path.open

        def opened_text(self: Path, *args: Any, **kwargs: Any) -> Any:
            result = original_open(self, *args, **kwargs)
            if self == path:
                resources.append(result)
            return result

        monkeypatch.setattr(Path, "open", opened_text)
    return resources


@pytest.mark.parametrize("carrier", CARRIERS)
def test_reducer_state_guard_releases_owned_source_after_valid_prefix(
    source_path: Callable[[str, bool], Path], carrier: str,
    monkeypatch: pytest.MonkeyPatch, record_property,
) -> None:
    path = source_path(carrier, True)
    resources = _observe_acquisition(path, carrier, monkeypatch)
    try:
        with pytest.raises(ValueError, match="Normalized retained data exceeds 16777216 bytes") as caught:
            normalize(path, dict(BUDGET_SPEC, format=carrier))
        stage = _error_stage(caught.value)
        assert stage["prefix_rows"] == 32 and 32 < stage["input_count"] < ROWS
        assert "add" in stage["frames"], "Failure must originate in actual reducer state guard"
        assert resources, "Resource oracle must observe actual owned acquisition"
        closed = [resource.closed for resource in resources]
        before = _rename(path)
        record_property("error_stage", json.dumps(stage))
        record_property("handles_closed_before_test_cleanup", json.dumps(closed))
        record_property("rename_before_test_cleanup", json.dumps(before))
    finally:
        for resource in resources:
            resource.close()
        after = _rename(path)
        record_property("rename_after_test_cleanup", json.dumps(after))
        assert after is None, "Test must leave its own synthetic source unlocked"
    assert all(closed), f"Owned {carrier} source leaked after public reducer guard; rename={before}"
    if os.name == "nt":
        assert before is None


@pytest.mark.parametrize("carrier", CARRIERS)
def test_full_reducer_consumption_closes_owned_source(
    source_path: Callable[[str, bool], Path], carrier: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = source_path(carrier, False)
    resources = _observe_acquisition(path, carrier, monkeypatch)
    try:
        output = normalize(path, dict(BUDGET_SPEC, format=carrier))
        assert output.input_count == ROWS
        assert output.records == [{"g": _row(0, False)["g"], "v": ROWS}]
        assert output.strategy == "count" and not output.warnings
        assert resources and all(resource.closed for resource in resources)
        assert _rename(path) is None
    finally:
        for resource in resources:
            resource.close()


@pytest.mark.parametrize("carrier", ("csv", "jsonl"))
@pytest.mark.parametrize("unique", (True, False), ids=("guard", "full-consumption"))
def test_borrowed_text_source_ownership_survives_guard_or_full_consumption(
    source_path: Callable[[str, bool], Path], carrier: str, unique: bool, record_property,
) -> None:
    path = source_path(carrier, unique)
    with path.open("r", encoding="utf-8", newline="") as borrowed:
        if unique:
            with pytest.raises(ValueError, match="Normalized retained data exceeds 16777216 bytes") as caught:
                normalize(borrowed, dict(BUDGET_SPEC, format=carrier))
            stage = _error_stage(caught.value)
            assert stage["prefix_rows"] == 32 and 32 < stage["input_count"] < ROWS
            assert "add" in stage["frames"]
            record_property("error_stage", json.dumps(stage))
        else:
            result = normalize(borrowed, dict(BUDGET_SPEC, format=carrier))
            assert result.input_count == ROWS and result.records[0]["v"] == ROWS
            assert borrowed.read() == "", "Full consumption must reach actual source EOF"
        assert not borrowed.closed
        borrowed.seek(0)
        assert borrowed.read(1)
    assert borrowed.closed and _rename(path) is None


def test_borrowed_arrow_reader_remains_usable_after_reducer_guard(
    source_path: Callable[[str, bool], Path], record_property,
) -> None:
    arrow = pytest.importorskip("pyarrow", reason="Borrowed Arrow reader requires optional pyarrow")
    path = source_path("arrow", True)
    with arrow.input_stream(str(path)) as borrowed_stream, arrow.ipc.open_stream(borrowed_stream) as borrowed_reader:
        with pytest.raises(ValueError, match="Normalized retained data exceeds 16777216 bytes") as caught:
            normalize(borrowed_reader, BUDGET_SPEC)
        stage = _error_stage(caught.value)
        assert stage["prefix_rows"] == 32 and 32 < stage["input_count"] < ROWS
        assert "add" in stage["frames"]
        record_property("error_stage", json.dumps(stage))
        assert not borrowed_stream.closed
        remaining = borrowed_reader.read_next_batch()
        assert 0 < remaining.num_rows <= 32
        assert remaining.column(0)[0].as_py().endswith("0256")
    assert borrowed_stream.closed and _rename(path) is None


class ReadFault(io.StringIO):
    """Explicit deterministic EIO injection while preserving actual underlying file."""

    def __init__(self, file: io.TextIOBase, delivered_before_error: int | None):
        super().__init__("")
        self.file = file
        self.limit = delivered_before_error
        self.delivered = 0

    # Match _TextIOBase's own narrow ignore for its bytes-typed _IOBase ancestor.
    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        return self

    def __next__(self) -> str:  # type: ignore[override]
        if self.limit is not None and self.delivered == self.limit:
            raise OSError(errno.EIO, "R13 deterministic injected carrier read failure")
        line = next(self.file)
        self.delivered += 1
        return line

    def close(self) -> None:
        self.file.close()
        super().close()


def _small_path(tmp_path: Path, carrier: str) -> Path:
    path = tmp_path / f"small.{carrier}"
    with path.open("w", encoding="utf-8", newline="") as sink:
        if carrier == "csv":
            sink.write("g,v\n")
        for index in range(64):
            sink.write(f"group,{index}\n" if carrier == "csv" else json.dumps({"g": "group", "v": index}) + "\n")
    return path


@pytest.mark.parametrize("carrier", ("csv", "jsonl"))
@pytest.mark.parametrize("owned", (True, False), ids=("owned-path", "borrowed-stream"))
def test_after_prefix_carrier_eio_respects_source_ownership(
    tmp_path: Path, carrier: str, owned: bool, monkeypatch: pytest.MonkeyPatch, record_property,
) -> None:
    path = _small_path(tmp_path, carrier)
    faults: list[ReadFault] = []
    original_open = Path.open
    delivered = 48 + (carrier == "csv")

    def opened(self: Path, *args: Any, **kwargs: Any) -> Any:
        file = original_open(self, *args, **kwargs)
        if self != path:
            return file
        fault = ReadFault(file, delivered)
        faults.append(fault)
        return fault

    if owned:
        monkeypatch.setattr(Path, "open", opened)
        data: Any = path
    else:
        data = ReadFault(path.open("r", encoding="utf-8", newline=""), delivered)
        faults.append(data)
    try:
        with pytest.raises(OSError, match="R13 deterministic injected") as caught:
            normalize(data, dict(BUDGET_SPEC, format=carrier))
        stage = _error_stage(caught.value)
        assert caught.value.errno == errno.EIO
        assert stage["prefix_rows"] == 32 and stage["input_count"] == 48
        assert faults[0].delivered == delivered
        closed = faults[0].closed
        before = _rename(path)
        record_property("error_stage", json.dumps(stage))
        record_property("closed_before_caller_cleanup", str(closed))
        record_property("rename_before_caller_cleanup", json.dumps(before))
        assert closed is owned, "Library closes only the source it owns, even on I/O failure"
        assert faults[0].file.closed is owned
        if owned:
            assert before is None
        else:
            assert faults[0].file.seek(0) == 0
    finally:
        for fault in faults:
            fault.close()
        assert _rename(path) is None


@pytest.mark.parametrize("carrier", ("csv", "jsonl"))
@pytest.mark.parametrize("owned", (True, False), ids=("owned-path", "borrowed-stream"))
def test_sampling_limit_is_not_an_early_source_stop(
    tmp_path: Path, carrier: str, owned: bool, monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _small_path(tmp_path, carrier)
    resources = _observe_acquisition(path, carrier, monkeypatch) if owned else []
    borrowed = None if owned else path.open("r", encoding="utf-8", newline="")
    try:
        result = normalize(path if owned else borrowed, {
            "kind": "table", "format": carrier, "aggregation": "sample", "max_points": 10,
        })
        assert result.input_count == 64 and len(result.records) == 10
        assert result.strategy == "sample" and result.warnings
        if owned:
            assert resources and all(resource.closed for resource in resources)
        else:
            assert borrowed is not None and not borrowed.closed
            assert borrowed.read() == ""
    finally:
        if borrowed is not None:
            borrowed.close()
        for resource in resources:
            resource.close()
        assert _rename(path) is None
