"""Literal checkpoint envelopes, not imports of production byte counters."""
from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize

CASES = json.loads(Path(__file__).with_name("utf8-envelope-cases.json").read_text(encoding="utf-8"))
UNITS = [(unit["id"], unit["text"], unit["utf8_width"]) for unit in CASES["units"]]
NONE: dict[str, Any] = {"kind": "table", "aggregation": "none", "max_points": 10}


def sized_text(size: int, unit: str, width: int) -> str:
    assert len(unit.encode("utf-8")) == width
    copies, padding = divmod(size, width)
    text = unit * copies + "x" * padding
    assert len(text.encode("utf-8")) == size
    return text


class ObservedRows(Iterator[dict[str, Any]]):
    def __init__(self, rows: Iterator[dict[str, Any]]) -> None:
        self.rows = rows
        self.pulled = 0
        self.exhausted = False

    def __next__(self) -> dict[str, Any]:
        try:
            row = next(self.rows)
        except StopIteration:
            self.exhausted = True
            raise
        self.pulled += 1
        return row


@pytest.mark.parametrize("_label,unit,width", UNITS)
@pytest.mark.parametrize("location", ["raw", "composite", "array-index"])
@pytest.mark.parametrize("case", CASES["names"], ids=lambda case: str(case["bytes"]))
def test_literal_field_name_envelope(
    _label: str, unit: str, width: int, location: str, case: dict[str, Any],
) -> None:
    size = case["bytes"]
    row: dict[str, Any]
    if location == "raw":
        field = sized_text(size, unit, width)
        row = {field: 7}
    elif location == "composite":
        left = (size - 1) // 2
        outer = sized_text(left, unit, width)
        inner = sized_text(size - left - 1, unit, width)
        field, row = outer + "." + inner, {outer: {inner: 7}}
        if size <= 4097:
            assert len(outer.encode("utf-8")) < 4096
            assert len(inner.encode("utf-8")) < 4096
    else:
        outer = sized_text(size - 2, unit, width)
        field, row = outer + ".0", {outer: [7]}
        if size <= 4097:
            assert len(outer.encode("utf-8")) <= 4095
    assert len(field.encode("utf-8")) == size
    source = ObservedRows(iter([row]))
    if case["python_accepts"]:
        result = normalize(source, NONE)
        assert result.records == [{field: 7}]
        assert result.input_count == source.pulled == 1 and source.exhausted
        assert result.strategy == "none" and result.warnings == []
    else:
        with pytest.raises(ValueError, match=r"field name exceeds 4096 UTF-8 bytes"):
            normalize(source, NONE)
        assert source.pulled == 1 and not source.exhausted


@pytest.mark.parametrize("_label,unit,width", UNITS)
@pytest.mark.parametrize("case", CASES["cells"], ids=lambda case: str(case["bytes"]))
def test_literal_cell_envelope_without_truncation(
    _label: str, unit: str, width: int, case: dict[str, Any],
) -> None:
    text = sized_text(case["bytes"], unit, width)
    source = ObservedRows(iter([{"payload": text}]))
    if case["accepts"]:
        result = normalize(source, NONE)
        assert result.records == [{"payload": text}]
        assert result.input_count == source.pulled == 1 and source.exhausted
        assert result.strategy == "none" and result.warnings == []
    else:
        with pytest.raises(ValueError, match=r"cell exceeds 65536 UTF-8 bytes"):
            normalize(source, NONE)
        assert source.pulled == 1 and not source.exhausted


@pytest.mark.parametrize("_label,unit,width", UNITS)
@pytest.mark.parametrize("location", ["name", "cell"])
@pytest.mark.parametrize("invalid_index", [0, 40])
def test_invalid_row_consumption_stops_before_tail(
    _label: str, unit: str, width: int, location: str, invalid_index: int,
) -> None:
    bad = sized_text(4097 if location == "name" else 65537, unit, width)
    source = ObservedRows(
        ({bad: index} if location == "name" else {"payload": bad})
        if index == invalid_index else {"safe": index}
        for index in range(80)
    )
    message = "field name exceeds 4096" if location == "name" else "cell exceeds 65536"
    with pytest.raises(ValueError, match=message):
        normalize(source, NONE)
    assert source.pulled == invalid_index + 1
    assert not source.exhausted


def wide_rows(grouped: bool) -> Iterator[dict[str, Any]]:
    for index in range(512):
        text = f"{index:04d}" + "é" * 30718
        assert len(text.encode("utf-8")) == 61440
        yield {"g": text, "v": 1} if grouped else {"seq": index, "payload": text}


@pytest.mark.parametrize("grouped", [False, True], ids=["reservoir", "group-state"])
def test_16mib_retained_state_rejects_incrementally(grouped: bool) -> None:
    source = ObservedRows(wide_rows(grouped))
    spec = {"x": "g", "y": "v", "aggregation": "sum", "max_points": 1000} if grouped else {
        **NONE, "max_points": 1000,
    }
    with pytest.raises(ValueError, match=r"retained data exceeds 16777216 bytes"):
        normalize(source, spec)
    assert 1 < source.pulled <= 274
    assert not source.exhausted
    print(f"state-budget grouped={grouped} pulled={source.pulled} exhausted={source.exhausted}")


@pytest.mark.parametrize("grouped", [False, True], ids=["reservoir", "group-state"])
def test_30mib_stream_with_small_retained_state_preserves_counts_and_loss_metadata(grouped: bool) -> None:
    assert 512 * 61440 == 31457280 > 16777216
    source = ObservedRows(wide_rows(grouped))
    spec = {"x": "g", "y": "v", "aggregation": "sum", "max_points": 10} if grouped else NONE
    result = normalize(source, spec)
    assert result.input_count == source.pulled == 512 and source.exhausted
    assert len(result.records) == 10
    if grouped:
        assert result.strategy == "sum"
        assert [row["v"] for row in result.records] == [1] * 9 + [503]
        assert result.records[-1]["g"] == "__deepviz_other__"
        assert any("cardinality" in warning.lower() for warning in result.warnings)
    else:
        assert result.strategy == "sample"
        indices = [row["seq"] for row in result.records]
        assert indices == sorted(set(indices))
        assert all(row["payload"] == f"{row['seq']:04d}" + "é" * 30718 for row in result.records)
        assert any("sampl" in warning.lower() for warning in result.warnings)
    assert not any("truncat" in warning.lower() for warning in result.warnings)
