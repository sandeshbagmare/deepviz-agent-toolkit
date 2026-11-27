"""Nine small independent source-lifetime/Win32 oracles; no production patch."""
from __future__ import annotations

import csv
import errno
import hashlib
import io
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize


class TrackedText(io.TextIOBase):
    """Observe actual file ownership; optional EIO is explicit fault injection."""

    def __init__(self, file: Any, fault: OSError | None = None):
        super().__init__()
        self.file = file
        self.fault = fault
        self.delivered = 0
        self.close_calls = 0

    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        return self

    def __next__(self) -> str:  # type: ignore[override]
        if self.fault is not None and self.delivered == 40:
            raise self.fault
        line = next(self.file)
        self.delivered += 1
        return line

    def close(self) -> None:
        self.close_calls += 1
        self.file.close()
        super().close()


def source_file(directory: Path, carrier: str, rows: int, *, bad: bool = False) -> tuple[Path, list[dict[str, Any]], str]:
    data = [{"id": index, "text": "ok"} for index in range(rows)]
    path = directory / f"source.{carrier}"
    text = "id,text\n" if carrier == "csv" else ""
    text += "".join(f"{row['id']},ok\n" if carrier == "csv" else json.dumps(row) + "\n" for row in data)
    if bad:
        text += '"unterminated\n' if carrier == "csv" else '{"id":\n'
    path.write_text(text, encoding="utf-8", newline="")
    return path, data, hashlib.sha256(path.read_bytes()).hexdigest()


def track_open(path: Path, monkeypatch: pytest.MonkeyPatch, fault: OSError | None = None) -> list[TrackedText]:
    original = Path.open
    tracked = []

    def opened(self: Path, *args: Any, **kwargs: Any) -> Any:
        handle = original(self, *args, **kwargs)
        if self == path and args and args[0] == "r":
            observed = TrackedText(handle, fault)
            tracked.append(observed)
            return observed
        return handle

    monkeypatch.setattr(Path, "open", opened)
    return tracked


def assert_same_then_rename_unlink(path: Path, digest: str) -> None:
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    renamed = path.with_suffix(path.suffix + ".r22-unlocked")
    assert not renamed.exists()
    path.rename(renamed)  # Actual Windows operation, before any test-owned fallback cleanup.
    renamed.unlink()
    assert not path.exists() and not renamed.exists()


@pytest.mark.parametrize("carrier", ["csv", "jsonl"])
def test_owned_success_closes_once_preserves_rows_then_allows_windows_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, carrier: str,
) -> None:
    path, rows, digest = source_file(tmp_path, carrier, 3)
    marker = tmp_path / "caller-owned.txt"
    marker.write_text("keep", encoding="utf-8")
    handles = track_open(path, monkeypatch)
    result = normalize(path, {"kind": "table", "format": carrier, "aggregation": "none"})
    assert result.records == rows and result.input_count == 3 and result.warnings == []
    handle, = handles
    assert handle.close_calls == 1 and handle.closed and handle.file.closed
    assert_same_then_rename_unlink(path, digest)
    assert marker.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize("carrier", ["csv", "jsonl"])
@pytest.mark.parametrize("owned", [True, False], ids=["owned", "borrowed"])
def test_late_actual_parser_failure_unwinds_only_owned_file_and_keeps_original_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, carrier: str, owned: bool, record_property: Any,
) -> None:
    path, _, digest = source_file(tmp_path, carrier, 40, bad=True)
    handles = track_open(path, monkeypatch) if owned else []
    borrowed = None if owned else TrackedText(path.open("r", encoding="utf-8", newline=""))
    caught: Any = None
    try:
        with pytest.raises(ValueError, match="line 42" if carrier == "csv" else "line 41") as caught:
            normalize(path if owned else borrowed, {"kind": "table", "format": carrier, "aggregation": "none"})
        assert caught.traceback is not None
        assert isinstance(caught.value.__cause__, csv.Error if carrier == "csv" else json.JSONDecodeError)
        handle = handles[0] if owned else borrowed
        assert handle is not None and handle.delivered >= 40
        assert handle.close_calls == int(owned) and handle.closed is owned and handle.file.closed is owned
        record_property("close_before_caller_cleanup", handle.close_calls)
        record_property("retained_traceback", True)
        record_property("parser_cause_type", type(caught.value.__cause__).__name__)
        if owned:
            assert_same_then_rename_unlink(path, digest)
        else:
            assert handle.file.seek(0) == 0 and handle.file.readline()
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    finally:
        if borrowed is not None:
            borrowed.close()
        for handle in handles:
            if not handle.closed:
                handle.close()
    if borrowed is not None:
        assert borrowed.close_calls == 1
        assert_same_then_rename_unlink(path, digest)


@pytest.mark.parametrize("owned", [True, False], ids=["owned", "borrowed"])
def test_same_read_exception_object_propagates_after_prefix_without_caller_close(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, owned: bool, record_property: Any,
) -> None:
    path, _, digest = source_file(tmp_path, "jsonl", 48)
    fault = OSError(errno.EIO, "R22 explicit deterministic read fault")
    handles = track_open(path, monkeypatch, fault) if owned else []
    borrowed = None if owned else TrackedText(path.open("r", encoding="utf-8", newline=""), fault)
    try:
        with pytest.raises(OSError) as caught:
            normalize(path if owned else borrowed, {"kind": "table", "format": "jsonl", "aggregation": "none"})
        assert caught.value is fault and caught.value.errno == errno.EIO and caught.traceback is not None
        handle = handles[0] if owned else borrowed
        assert handle is not None and handle.delivered == 40
        assert handle.close_calls == int(owned) and handle.file.closed is owned
        record_property("same_exception_object", True)
        record_property("delivered_before_fault", handle.delivered)
        record_property("close_before_caller_cleanup", handle.close_calls)
        if owned:
            assert_same_then_rename_unlink(path, digest)
        else:
            assert handle.file.seek(0) == 0 and handle.file.readline()
    finally:
        if borrowed is not None:
            borrowed.close()
        for handle in handles:
            if not handle.closed:
                handle.close()
    if borrowed is not None:
        assert borrowed.close_calls == 1
        assert_same_then_rename_unlink(path, digest)


def test_plain_borrowed_iterator_exception_is_not_replaced_or_explicitly_closed() -> None:
    fault = RuntimeError("R22 borrowed iterator failure after prefix")

    class CallerIterator:
        delivered = 0
        close_calls = 0

        def __iter__(self) -> CallerIterator:
            return self

        def __next__(self) -> dict[str, int]:
            if self.delivered == 40:
                raise fault
            self.delivered += 1
            return {"id": self.delivered}

        def close(self) -> None:
            self.close_calls += 1

    source = CallerIterator()
    with pytest.raises(RuntimeError) as caught:
        normalize(source, {"kind": "table", "aggregation": "none"})
    assert caught.value is fault and caught.traceback is not None
    assert source.delivered == 40 and source.close_calls == 0
