"""Bounded 546 controls and pure proposal checks; no normalizer patch applied."""
from collections import Counter

import pytest
from proposed_state_charge import _state_number_bytes

from deepviz import normalize
from deepviz.normalize import _Reducer

OBSERVATIONS = []


class Once:
    def __init__(self, rows):
        self.rows = rows
        self.iterations = 0
        self.pulled = 0

    def __iter__(self):
        self.iterations += 1
        assert self.iterations == 1
        for row in self.rows:
            self.pulled += 1
            yield row


def proposed_size(count, value, correction=0, exponent=0):
    size = 128
    if any(isinstance(item, int) and item.bit_length() > 96
           for item in (count, value, correction)):
        size = max(size, sum(_state_number_bytes(item)
                             for item in (count, value, correction, exponent)))
    return size


def test_actual_546_positive_means_preserve_one_pass_valid_counts_and_input():
    large = 1 << 4096
    cases = [([1, 3, None, True, "2"], 2.0), ([large, -large], 0.0),
             ([1e308, 1e308], 1e308)]
    for values, expected in cases:
        rows = [{"g": "only", "v": value} for value in values]
        pristine = [dict(row) for row in rows]
        stream = Once(rows)
        result = normalize(stream, {"x": "g", "y": "v", "aggregation": "mean", "max_points": 10})
        assert result.records == [{"g": "only", "v": expected}]
        assert result.input_count == stream.pulled == len(rows)
        assert stream.iterations == 1 and result.strategy == "mean"
        assert rows == pristine
        OBSERVATIONS.append({"kind": "literal_mean", "input_count": result.input_count,
                             "source_pulls": stream.pulled, "source_iterations": stream.iterations,
                             "output_count": len(result.records), "expected_value": expected})
        if any(type(value) not in (int, float) and value is not None for value in values):
            assert any("non-numeric" in warning for warning in result.warnings)
        else:
            assert result.warnings == []


def test_actual_546_natural_retained_budget_rejects_before_1024_rows():
    stream = Once({"g": f"g{index}-" + "x" * 16384, "v": 1} for index in range(1024))
    with pytest.raises(ValueError, match="retained.*bytes"):
        normalize(stream, {"x": "g", "y": "v", "aggregation": "mean", "max_points": 2000})
    assert stream.iterations == 1 and 0 < stream.pulled < 1024
    OBSERVATIONS.append({"kind": "natural_budget_rejection", "source_pulls": stream.pulled,
                         "source_iterations": stream.iterations, "source_upper_bound": 1024,
                         "result_returned": False, "caps_injected": False})


def test_proposal_bound_covers_decimal_and_sign_boundaries_without_input_mutation():
    values = [0, 1, -1, True, False, None, 0.0, -0.0, 1e308]
    values += [sign * value for digits in (1, 2, 9, 29, 30, 127, 128, 1000)
               for value in (10**digits - 1, 10**digits, 10**digits + 1) for sign in (-1, 1)]
    for value in values:
        expected_bytes = len(repr(value))
        bound = _state_number_bytes(value)
        assert expected_bytes <= bound <= expected_bytes + 1
        assert type(bound) is int


def test_proposal_preserves_small_state_floor_and_96_bit_switch():
    reducer = _Reducer("sum", [], "v", 10, Counter())
    for bits in (0, 1, 95, 96, 97):
        for sign in (-1, 1):
            value = sign * ((1 << bits) - 1)
            state = [1, None, 0, 0, 128]
            reducer._store(state, value)
            assert state[4] == proposed_size(1, value) == 128
    assert proposed_size(1, 1 << 4096) >= 128


def test_proposal_huge_unit_bound_is_safe_without_decimal_conversion():
    units = (10**4000) << 1074
    for value in (units, -units):
        bound = _state_number_bytes(value)
        digits = bound - int(value < 0)
        assert abs(value) < 10**digits
        assert 4324 <= digits <= 4325
        assert proposed_size(1, value, exponent=-1074) < 16384
