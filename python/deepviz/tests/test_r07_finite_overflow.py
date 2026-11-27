"""Finite-final SUMs must survive transient overflow without unbounded partials."""
import json
import math
import sys
from fractions import Fraction
from itertools import permutations

import pytest

from deepviz import normalize

SUM = {"kind": "table", "x": "g", "y": "v", "aggregation": "sum"}
TINY = float.fromhex("0x0.0000000000001p-1022")


@pytest.mark.parametrize("values", sorted(set(permutations([1e308, 1e308, -1e308]))))
@pytest.mark.parametrize("sign", [1, -1])
def test_finite_final_sum_survives_every_transient_overflow_permutation(values, sign):
    values = [sign * value for value in values]
    expected = float(sum(map(Fraction.from_float, values), Fraction()))
    assert expected == sign * 1e308
    result = normalize(({"g": "all", "v": value} for value in values), SUM)
    assert result.records == [{"g": "all", "v": expected}]
    assert result.input_count == 3
    assert result.warnings == []


@pytest.mark.parametrize("residual", [0.0, 1.0, -1.0, TINY, -TINY])
def test_overflow_cancellation_keeps_even_subnormal_residuals(residual):
    values = [1e308, 1e308, residual, -1e308, -1e308]
    result = normalize([{"g": "all", "v": value} for value in values], SUM)
    assert result.records == [{"g": "all", "v": residual}]
    assert result.input_count == len(values)
    assert result.warnings == []


def test_overflow_fallback_retains_existing_compensation_and_group_identity():
    rows = [{"g": "a", "v": v} for v in [1e308, 1.0, 1e308, -1e308, -1e308]]
    rows += [{"g": "b", "v": v} for v in [-1e308, -1e308, 1e308]]
    rows += [{"g": "empty", "v": None}]
    result = normalize(iter(rows), SUM)
    assert result.records == [{"g": "a", "v": 1.0}, {"g": "b", "v": -1e308}, {"g": "empty", "v": None}]
    assert result.input_count == len(rows)
    assert result.warnings == []


@pytest.mark.parametrize("tail,expected", [
    ([1.0, 2.0**-53], 1.0),
    ([1.0, 2.0**-53, TINY], math.nextafter(1.0, math.inf)),
    ([1.0, 3 * 2.0**-53], math.nextafter(math.nextafter(1.0, math.inf), math.inf)),
    ([sys.float_info.max], sys.float_info.max),
    ([2.0**-1022, -TINY], math.nextafter(2.0**-1022, 0)),
])
def test_fallback_rounds_once_including_even_ties_and_normal_subnormal_boundary(tail, expected):
    values = [1e308, 1e308, -1e308, -1e308, *tail]
    oracle = float(sum(map(Fraction.from_float, values), Fraction()))
    assert oracle == expected
    assert normalize([{"g": "all", "v": value} for value in values], SUM).records == [{"g": "all", "v": expected}]


def test_fallback_state_moves_with_evicted_group_to_other_bucket():
    rows = [{"g": f"keep{i}", "v": i} for i in range(9)]
    rows += [{"g": "evicted", "v": v} for v in [1e308, 1e308, TINY]]
    rows += [{"g": "new", "v": v} for v in [-1e308, -1e308]]
    rows += [{"g": "keep0", "v": 7}]
    result = normalize(iter(rows), dict(SUM, max_points=10))
    assert len(result.records) == 10
    assert result.records[0] == {"g": "keep0", "v": 7}
    assert result.records[-1] == {"g": "__deepviz_other__", "v": TINY}
    assert result.input_count == len(rows)
    assert any("other bucket" in warning for warning in result.warnings)
    assert not any("non-finite" in warning for warning in result.warnings)


@pytest.mark.parametrize("sign", [1, -1])
def test_truly_unrepresentable_final_sum_remains_disclosed_json_safe_null(sign):
    result = normalize([{"g": "all", "v": sign * sys.float_info.max}] * 2, SUM)
    assert result.records == [{"g": "all", "v": None}]
    assert any("non-finite" in warning for warning in result.warnings)
    json.dumps(result.records, allow_nan=False)


def test_sum_fix_preserves_integer_compensation_mean_count_and_input_nonfinite_policy():
    exact = normalize([{"g": "all", "v": v} for v in [10**100, 1, -(10**100)]], SUM)
    assert exact.records == [{"g": "all", "v": 1}]
    ordinary = normalize([{"g": "all", "v": v} for v in [1e16, 1.0, -1e16]], SUM)
    assert ordinary.records == [{"g": "all", "v": 1.0}]
    rows = [{"g": "all", "v": v} for v in [1e308, 1e308, -1e308, None, "bad", math.nan]]
    mean = normalize(rows, dict(SUM, aggregation="mean"))
    assert mean.records[0]["v"] == pytest.approx(1e308 / 3, rel=1e-15, abs=0)
    assert any("non-finite" in warning for warning in mean.warnings)
    assert normalize(rows, dict(SUM, aggregation="count")).records == [{"g": "all", "v": 6}]
    assert normalize([{"g": "all", "v": TINY}] * 2, dict(SUM, aggregation="mean")).records[0]["v"] == TINY


def test_fallback_reduces_a_one_pass_stream_without_retaining_partials():
    consumed = 0

    def rows():
        nonlocal consumed
        for _ in range(2000):
            for value in [1e308, 1e308, TINY, -1e308, -1e308]:
                consumed += 1
                yield {"g": "all", "v": value}

    result = normalize(rows(), SUM)
    assert result.input_count == consumed == 10000
    assert result.records == [{"g": "all", "v": 2000 * TINY}]


def test_fallback_state_counts_toward_incremental_retained_budget():
    consumed = 0

    def rows():
        nonlocal consumed
        for group in range(100000):
            for value in [1e308, 1e308, -1e308]:
                consumed += 1
                yield {"g": str(group), "v": value}

    with pytest.raises(ValueError, match="retained.*bytes|bytes.*retained"):
        normalize(rows(), dict(SUM, max_points=100000))
    assert consumed < 150000
