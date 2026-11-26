"""Independent C17 resource-policy oracles; intentional RED until implemented.

Limits come from docs/coordination/tasks/C17-resource-policy.md, not production
constants. These finite lazy probes check byte policy and source consumption,
not process RSS. No 10M source or prebuilt large record list is used.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from deepviz import normalize

LIMIT_MESSAGE = r"(?i)(byte|utf.?8|kib|limit|budget)"


class ObservedRows(Iterator[dict[str, Any]]):
    """Count real pulls from a one-shot source without retaining its records."""

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


@pytest.mark.parametrize("unit,copies", [("x", 65536), ("é", 32768), ("🙂", 16384)],
                         ids=["ascii", "two-byte", "four-byte"])
@pytest.mark.parametrize("location", ["key", "cell"])
def test_exact_64kib_utf8_key_or_cell_is_preserved(unit: str, copies: int, location: str) -> None:
    text = unit * copies
    assert len(text.encode("utf-8")) == 65536
    row = {text: 7} if location == "key" else {"payload": text}
    source = ObservedRows(iter([row]))
    result = normalize(source, {"kind": "table", "aggregation": "none", "max_points": 10})
    assert result.records == [{text: 7} if location == "key" else {"payload": text}]
    assert result.input_count == source.pulled == 1 and source.exhausted
    assert result.strategy == "none" and result.warnings == []


@pytest.mark.parametrize("unit,copies", [("x", 65536), ("é", 32768), ("🙂", 16384)],
                         ids=["ascii", "two-byte", "four-byte"])
@pytest.mark.parametrize("location", ["key", "cell"])
def test_64kib_plus_one_utf8_byte_is_rejected(unit: str, copies: int, location: str) -> None:
    text = unit * copies + "!"
    assert len(text.encode("utf-8")) == 65537
    row = {text: 7} if location == "key" else {"payload": text}
    source = ObservedRows(iter([row]))
    with pytest.raises(ValueError, match=LIMIT_MESSAGE):
        normalize(source, {"kind": "table", "aggregation": "none", "max_points": 10})
    assert source.pulled == 1


def test_flattened_multibyte_key_at_64kib_is_preserved() -> None:
    outer, inner = "é" * 16384, "界" * 10922 + "q"
    field = outer + "." + inner
    assert len(field.encode("utf-8")) == 65536
    result = normalize(iter([{outer: {inner: 7}}]), {"kind": "table", "aggregation": "none"})
    assert result.records == [{field: 7}] and result.input_count == 1
    assert result.strategy == "none" and result.warnings == []


def test_flattened_multibyte_key_over_64kib_is_rejected() -> None:
    outer, inner = "é" * 16384, "界" * 10922 + "qq"
    assert len((outer + "." + inner).encode("utf-8")) == 65537
    with pytest.raises(ValueError, match=LIMIT_MESSAGE):
        normalize(iter([{outer: {inner: 7}}]), {"kind": "table", "aggregation": "none"})


def test_oversized_later_cell_is_rejected_after_reservoir_is_full() -> None:
    source = ObservedRows({"id": index, "payload": "🙂" * 16384 + "!" if index == 40 else "ok"}
                          for index in range(80))
    with pytest.raises(ValueError, match=LIMIT_MESSAGE):
        normalize(source, {"kind": "table", "aggregation": "none", "max_points": 10})
    assert source.pulled <= 41 and not source.exhausted


@pytest.mark.parametrize("aggregation", ["none", "sum"])
def test_sub_256kib_flattened_record_is_accepted(aggregation: str) -> None:
    # Three individually safe cells total 180 KiB, leaving ample key/JSON overhead.
    row = {"g": "a", "v": 1, "nested": {f"f{i}": "é" * 30720 for i in range(3)}}
    result = normalize(iter([row]), {"kind": "table", "x": "g", "y": "v", "aggregation": aggregation})
    expected = {"g": "a", "v": 1}
    if aggregation == "none":
        expected.update({f"nested.f{i}": "é" * 30720 for i in range(3)})
    assert result.records == [expected] and result.input_count == 1
    assert result.strategy == aggregation and result.warnings == []


@pytest.mark.parametrize("aggregation", ["none", "sum"])
def test_over_256kib_record_is_rejected_before_reduction_discards_cells(aggregation: str) -> None:
    # Five safe 60-KiB cells exceed 256 KiB even before counting keys or JSON.
    row = {"g": "a", "v": 1, "nested": {f"f{i}": "é" * 30720 for i in range(5)}}
    source = ObservedRows(iter([row]))
    with pytest.raises(ValueError, match=LIMIT_MESSAGE):
        normalize(source, {"kind": "table", "x": "g", "y": "v", "aggregation": aggregation})
    assert source.pulled == 1


def long_rows(*, grouped: bool) -> Iterator[dict[str, Any]]:
    for index in range(512):
        # Unique strings are allocated only on demand; each payload is 60 KiB.
        text = f"{index:04d}" + "x" * 61436
        yield {"g": text, "v": 1} if grouped else {"id": index, "payload": text}


@pytest.mark.parametrize("grouped", [False, True], ids=["reservoir", "group-state"])
def test_retained_state_16mib_limit_rejects_incrementally(grouped: bool) -> None:
    source = ObservedRows(long_rows(grouped=grouped))
    spec = {"kind": "bar", "x": "g", "y": "v", "aggregation": "sum", "max_points": 1000} if grouped else {
        "kind": "table", "aggregation": "none", "max_points": 1000,
    }
    with pytest.raises(ValueError, match=LIMIT_MESSAGE):
        normalize(source, spec)
    # 274 * 60 KiB = 16,834,560 bytes > 16 MiB, without container/key overhead.
    # Reading all 512 rows before checking would violate the incremental policy.
    assert source.pulled <= 274 and not source.exhausted


@pytest.mark.parametrize("grouped", [False, True], ids=["reservoir", "group-state"])
def test_over_16mib_stream_with_small_retained_state_is_not_rejected(grouped: bool) -> None:
    source = ObservedRows(long_rows(grouped=grouped))
    spec = {"kind": "bar", "x": "g", "y": "v", "aggregation": "sum", "max_points": 10} if grouped else {
        "kind": "table", "aggregation": "none", "max_points": 10,
    }
    result = normalize(source, spec)
    assert result.input_count == source.pulled == 512 and source.exhausted
    assert len(result.records) == 10
    if grouped:
        assert result.strategy == "sum"
        assert [row["v"] for row in result.records] == [1] * 9 + [503]
        assert any("cardinality" in warning.lower() for warning in result.warnings)
    else:
        assert result.strategy == "sample"
        indices = [row["id"] for row in result.records]
        assert indices == sorted(set(indices))
        assert all(row["payload"] == f"{row['id']:04d}" + "x" * 61436 for row in result.records)
        assert any("sampl" in warning.lower() for warning in result.warnings)


@pytest.mark.parametrize("aggregation,exact,other", [
    ("sum", [900, 910, 920, 930, 940, 950, 960, 970, 980], 11440),
    ("mean", [90, 91, 92, 93, 94, 95, 96, 97, 98], 104),
    ("count", [10] * 9, 110),
])
def test_policy_checks_preserve_one_pass_counts_and_reduction_metadata(
    aggregation: str, exact: list[int], other: int,
) -> None:
    # 200 integers 0..199, twenty groups, ten contributions per group.
    source = ObservedRows({"g": f"g-{index % 20}", "v": index} for index in range(200))
    result = normalize(source, {"x": "g", "y": "v", "aggregation": aggregation, "max_points": 10})
    assert result.input_count == source.pulled == 200 and source.exhausted
    assert result.strategy == aggregation and len(result.records) == 10
    assert [row["g"] for row in result.records[:9]] == [f"g-{index}" for index in range(9)]
    assert [row["v"] for row in result.records[:9]] == pytest.approx(exact)
    assert result.records[-1]["g"] == "__deepviz_other__"
    assert result.records[-1]["v"] == pytest.approx(other)
    assert any("cardinality" in warning.lower() for warning in result.warnings)
