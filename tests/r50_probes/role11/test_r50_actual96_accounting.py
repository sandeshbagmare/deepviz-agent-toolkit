"""Independent bounded public tests of the sealed numeric-accounting repair."""
from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from typing import Any

import pytest

from deepviz import normalize


class OnePass:
    def __init__(self, rows: Iterator[dict[str, Any]]) -> None:
        self.rows = rows
        self.iterations = 0
        self.pulled = 0

    def __iter__(self) -> Iterator[dict[str, Any]]:
        self.iterations += 1
        assert self.iterations == 1, "The input must not be replayed"
        for row in self.rows:
            self.pulled += 1
            yield row


@pytest.mark.parametrize("strategy", ["mean", "sum"])
@pytest.mark.parametrize("sign", [1, -1], ids=["positive-first", "negative-first"])
@pytest.mark.parametrize("as_stream", [False, True], ids=["native", "one-pass"])
def test_accepted_4000_digit_cancellation_returns_exact_zero_without_global_change(
    strategy, sign, as_stream,
):
    assert sys.get_int_max_str_digits() == 4300
    large = sign * 10**4000
    values = [large, -large] if strategy == "mean" else [large, 0.0, -large]
    rows = [{"g": "only", "v": value} for value in values]
    original = json.dumps(rows)
    assert len(original.encode("utf-8")) < 16_384
    source = OnePass(iter(rows)) if as_stream else rows

    result = normalize(source, {"x": "g", "y": "v", "aggregation": strategy, "max_points": 10})

    assert result.records == [{"g": "only", "v": 0.0}]
    assert result.input_count == len(values)
    if as_stream:
        assert result.input_count == source.pulled == len(values)
        assert source.iterations == 1
    assert result.strategy == strategy and result.warnings == []
    assert json.dumps(rows) == original
    assert sys.get_int_max_str_digits() == 4300


@pytest.mark.parametrize(("values", "expected"), [
    ([2, 4], 3.0),
    ([-5.0, 3.0], -1.0),
    ([-5, 3, -2], -4.0),
])
def test_small_signed_mean_and_promoted_sum_outputs_remain_unchanged(values, expected):
    strategy = "sum" if len(values) == 3 else "mean"
    rows = [{"g": "only", "v": value} for value in values]
    result = normalize(iter(rows), {"x": "g", "y": "v", "aggregation": strategy})

    assert result.records == [{"g": "only", "v": expected}]
    assert result.input_count == len(rows) and result.strategy == strategy
    assert result.warnings == []


def test_natural_retained_budget_rejects_at_measured_exact_head_boundary():
    source = OnePass(
        {"g": f"g{index}-" + "x" * 16_384, "v": 1}
        for index in range(1024)
    )

    with pytest.raises(ValueError, match="Normalized retained data exceeds 16777216 bytes"):
        normalize(source, {"x": "g", "y": "v", "aggregation": "mean", "max_points": 2000})

    assert source.iterations == 1
    # Producer96's conservative private-charge upper bound rejects two rows
    # earlier than546, whose exact previous 1003-pull control remains preserved.
    assert source.pulled == 1001
    assert sys.get_int_max_str_digits() == 4300


def test_borrowed_generator_remains_open_and_usable_after_planning_error():
    closed: list[bool] = []

    def rows() -> Iterator[dict[str, str]]:
        try:
            for _ in range(40):
                yield {"label": "a", "note": "b"}
        finally:
            closed.append(True)

    source = rows()
    try:
        with pytest.raises(ValueError, match="numeric y"):
            normalize(source, {"kind": "bar", "aggregation": "sum"})
        assert closed == []
        assert next(source) == {"label": "a", "note": "b"}
        assert closed == []
    finally:
        source.close()
    assert closed == [True]


@pytest.mark.parametrize(("strategy", "expected"), [("mean", 2.0), ("sum", 6), ("count", 4)])
def test_weighted_overflow_bucket_retains_raw_counts_with_large_cancellation(strategy, expected):
    large = 10**4000
    rows = [{"g": f"keep-{index}", "v": 2} for index in range(9)] + [
        {"g": "later-a", "v": large},
        {"g": "later-b", "v": -large},
        {"g": "later-c", "v": 6},
        {"g": "later-null", "v": None},
    ]
    source = OnePass(iter(rows))

    result = normalize(
        source, {"x": "g", "y": "v", "aggregation": strategy, "max_points": 10},
    )

    retained_value = 1 if strategy == "count" else 2
    assert result.records == [
        *[{"g": f"keep-{index}", "v": retained_value} for index in range(9)],
        {"g": "__deepviz_other__", "v": expected},
    ]
    assert result.input_count == source.pulled == 13
    assert source.iterations == 1
    assert len(result.warnings) == 1 and "all non-retained groups" in result.warnings[0]
