"""Private numeric accounting must not decimal-render an exact accumulator."""
from __future__ import annotations

import importlib
import json
import sys
from collections import Counter
from collections.abc import Iterator
from typing import Any

import pytest

from deepviz import normalize

normalizer = importlib.import_module("deepviz.normalize")


class OnePass:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.iterations = 0
        self.yielded = 0

    def __iter__(self) -> Iterator[dict[str, Any]]:
        assert self.iterations == 0, "The caller's data must not be replayed"
        self.iterations += 1
        for row in self.rows:
            self.yielded += 1
            yield row


@pytest.mark.parametrize("strategy", ["mean", "sum"])
@pytest.mark.parametrize("sign", [1, -1], ids=["positive-first", "negative-first"])
@pytest.mark.parametrize("stream", [False, True], ids=["native", "one-pass"])
def test_accepted_large_integer_cancellation_avoids_private_decimal_encoding(
    strategy: str, sign: int, stream: bool,
) -> None:
    large = sign * 10**4000
    values = [large, -large] if strategy == "mean" else [large, 0.0, -large]
    rows = [{"g": "only", "v": value} for value in values]
    pristine = json.dumps(rows)
    assert len(pristine.encode("utf-8")) < 16384
    digit_limit = sys.get_int_max_str_digits()
    once = OnePass(rows)
    result = normalize(
        once if stream else rows,
        {"x": "g", "y": "v", "aggregation": strategy, "max_points": 10},
    )
    assert result.records == [{"g": "only", "v": 0.0}]
    assert result.input_count == len(rows) and result.strategy == strategy
    assert result.warnings == []
    assert json.dumps(rows) == pristine
    assert sys.get_int_max_str_digits() == digit_limit
    if stream:
        assert (once.iterations, once.yielded) == (1, len(rows))


@pytest.mark.parametrize("strategy,values,expected", [
    ("mean", [2, 4], 3.0),
    ("sum", [-5, 3, -2], -4),
    ("mean", [-5.0, 3.0], -1.0),
    ("sum", [1e308, 1e308, -1e308], 1e308),
    ("count", [None, None, True, "not numeric"], 4),
])
def test_private_charge_preserves_literal_numeric_and_count_results(
    strategy: str, values: list[Any], expected: int | float,
) -> None:
    rows = [{"g": "only", "v": value} for value in values]
    result = normalize(iter(rows), {"x": "g", "y": "v", "aggregation": strategy})
    assert result.records == [{"g": "only", "v": expected}]
    assert result.input_count == len(rows) and result.strategy == strategy
    assert result.warnings == []


@pytest.mark.parametrize("strategy,expected", [("mean", 2.0), ("sum", 6), ("count", 4)])
def test_large_integer_state_moves_to_other_without_losing_count_or_weight(
    strategy: str, expected: int | float,
) -> None:
    large = 10**4000
    rows = [{"g": f"keep-{index}", "v": 2} for index in range(9)] + [
        {"g": "later-a", "v": large}, {"g": "later-b", "v": -large},
        {"g": "later-c", "v": 6}, {"g": "later-null", "v": None},
    ]
    once = OnePass(rows)
    result = normalize(
        once, {"x": "g", "y": "v", "aggregation": strategy, "max_points": 10},
    )
    retained_value = 1 if strategy == "count" else 2
    assert result.records == [
        *[{"g": f"keep-{index}", "v": retained_value} for index in range(9)],
        {"g": "__deepviz_other__", "v": expected},
    ]
    assert result.input_count == 13 and result.strategy == strategy
    assert (once.iterations, once.yielded) == (1, 13)
    assert len(result.warnings) == 1 and "all non-retained groups" in result.warnings[0]


def test_private_wide_state_is_charged_then_releases_its_budget_on_cancellation() -> None:
    reducer = normalizer._Reducer("mean", ["g"], "v", 10, Counter())
    reducer.add({"g": "only", "v": 0})
    state = next(iter(reducer.groups.values()))
    original = state.copy()
    retained = reducer.retained_bytes
    wide = (10**4000) << 1074
    assert 10**4323 <= wide < 10**4324  # Independent digit bound, never repr(wide).
    reducer._store(state, wide, exponent=-1074)
    assert state[1] is wide and state[4] >= 4324
    assert reducer.retained_bytes - retained == state[4] - original[4]
    assert state[0] == 1
    reducer._store(state, 0, exponent=-1074)
    assert reducer.retained_bytes == retained and state == original
    assert reducer.finish() == [{"g": "only", "v": 0.0}]


def test_private_oversize_charge_rejects_before_retaining_or_mutating_state() -> None:
    reducer = normalizer._Reducer("mean", ["g"], "v", 10, Counter())
    reducer.add({"g": "only", "v": 0})
    state = next(iter(reducer.groups.values()))
    original = state.copy()
    retained = reducer.retained_bytes
    # One bounded private integer already exceeds the unchanged 16 MiB payload budget.
    oversized = 1 << (8 * 16 * 1024 * 1024)
    with pytest.raises(ValueError, match="Normalized retained data exceeds"):
        reducer._store(state, oversized, exponent=-1074)
    assert state == original and reducer.retained_bytes == retained
