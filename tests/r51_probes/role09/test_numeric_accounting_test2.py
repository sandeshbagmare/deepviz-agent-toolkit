"""Independent bounded TEST2 for the exact96 numeric-accounting replacement.

These cases do not import or execute producer tests. Expected public values are
literal/arithmetic controls; the wide-state bound is derived independently from
integer bit lengths. No cap, interpreter limit, source, or oracle is changed.
"""
from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize

SOURCE_COMMIT = "96b819aee5b01ba88b5a609b587331a528aaa070"
MAX_ROWS = 4096


class OnePassRows:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.iterations = 0
        self.pulled = 0

    def __iter__(self) -> Iterator[dict[str, Any]]:
        self.iterations += 1
        assert self.iterations == 1, "input must be consumed once"
        for row in self.rows:
            self.pulled += 1
            yield row


class LazyBudgetRows:
    """Finite rows generated on demand; no prebuilt wide dataset is retained."""

    def __init__(self) -> None:
        self.index = 0
        self.iterations = 0

    def __iter__(self) -> LazyBudgetRows:
        self.iterations += 1
        assert self.iterations == 1
        return self

    def __next__(self) -> dict[str, Any]:
        if self.index == MAX_ROWS:
            raise StopIteration
        index = self.index
        self.index += 1
        # The 4096-byte group value is within the documented field limit. The
        # natural reducer budget, not a monkeypatch, must stop the stream.
        return {"g": f"{index:04d}" + ("x" * (4096 - 4)), "v": 1}


def _module_path_guard() -> Path:
    module = importlib.import_module("deepviz.normalize")
    assert module.__file__ is not None
    path = Path(module.__file__).resolve()
    root = Path(__file__).resolve().parents[3]
    expected = root / "python/deepviz/src/deepviz/normalize.py"
    assert path == expected, f"unexpected normalizer import: {path}"
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip() == SOURCE_COMMIT
    assert path.read_bytes() == subprocess.check_output(
        ["git", "-C", str(root), "show", f"{SOURCE_COMMIT}:python/deepviz/src/deepviz/normalize.py"]
    )
    return path


def test_exact96_import_and_default_digit_limit_are_unchanged() -> None:
    _module_path_guard()
    assert sys.get_int_max_str_digits() == sys.int_info.default_max_str_digits == 4300


@pytest.mark.parametrize("strategy", ["mean", "sum"], ids=["mean", "sum"])
@pytest.mark.parametrize("sign", [1, -1], ids=["positive-first", "negative-first"])
@pytest.mark.parametrize("stream", [False, True], ids=["list", "one-pass"])
def test_huge_cancellation_returns_zero_without_decimalizing_private_state(
    strategy: str, sign: int, stream: bool,
) -> None:
    huge = sign * 10**4000
    values: list[int | float] = [huge, -huge] if strategy == "mean" else [huge, 0.0, -huge]
    rows = [{"g": "only", "v": value} for value in values]
    pristine = copy.deepcopy(rows)
    assert len(json.dumps(rows).encode("utf-8")) < 16 * 1024
    source = OnePassRows(rows)
    before_limit = sys.get_int_max_str_digits()
    result = normalize(source if stream else rows, {
        "x": "g", "y": "v", "aggregation": strategy, "max_points": 10,
    })
    assert result.records == [{"g": "only", "v": 0.0}]
    assert result.input_count == len(rows) and result.strategy == strategy and result.warnings == []
    assert rows == pristine and json.dumps(rows) == json.dumps(pristine)
    assert sys.get_int_max_str_digits() == before_limit == 4300
    if stream:
        assert (source.iterations, source.pulled) == (1, len(rows))


@pytest.mark.parametrize("strategy,values,expected", [
    ("sum", [2, 4], 6),
    ("sum", [-5, 3, -2], -4),
    ("mean", [2, 4], 3.0),
    ("mean", [-5.0, 3.0], -1.0),
    ("sum", [1e308, 1e308, -1e308], 1e308),
    ("count", [None, None, True, "not numeric"], 4),
], ids=["ordinary-sum", "signed-sum", "ordinary-mean", "signed-float-mean", "finite-float-sum", "natural-count"])
def test_ordinary_signed_float_and_count_outputs_are_preserved(
    strategy: str, values: list[Any], expected: int | float,
) -> None:
    rows = [{"g": "only", "v": value} for value in values]
    pristine = copy.deepcopy(rows)
    source = OnePassRows(rows)
    result = normalize(source, {"x": "g", "y": "v", "aggregation": strategy, "max_points": 10})
    assert result.records == [{"g": "only", "v": expected}]
    assert result.input_count == len(rows) and result.strategy == strategy and result.warnings == []
    assert rows == pristine and source.iterations == 1 and source.pulled == len(rows)


def test_bit_length_bound_is_independently_sufficient_for_decimal_state_charge() -> None:
    def independent_bound(value: int) -> int:
        # For b=3k+r, 2**b = 8**k * 2**r < 10**(k+1); sign is one
        # additional character. This oracle never calls production helpers.
        return value.bit_length() // 3 + 1 + (value < 0)

    manageable = [0, 1, -1, 7, -8, (1 << 96) - 1, -(1 << 96), (1 << 4095) - 1]
    for value in manageable:
        expected_bound = independent_bound(value)
        assert len(str(value)) <= expected_bound

    huge_units = (10**4000) << 1074
    bits = huge_units.bit_length()
    expected_bound = independent_bound(huge_units)
    assert bits > 14_000 and expected_bound < 5_000
    assert expected_bound == 4788
    assert independent_bound(-huge_units) == expected_bound + 1


def test_natural_retained_budget_rejects_incrementally_without_input_replay() -> None:
    source = LazyBudgetRows()
    with pytest.raises(ValueError, match="Normalized retained data exceeds 16777216 bytes") as caught:
        normalize(source, {"kind": "bar", "x": "g", "y": "v", "aggregation": "count", "max_points": MAX_ROWS})
    assert caught.traceback is not None
    assert source.iterations == 1
    assert 3000 < source.index < MAX_ROWS


def test_zero_result_and_input_objects_are_not_mutated() -> None:
    rows = [{"g": "only", "v": 10**4000}, {"g": "only", "v": -(10**4000)}]
    original = copy.deepcopy(rows)
    result = normalize(iter(rows), {"x": "g", "y": "v", "aggregation": "mean", "max_points": 10})
    assert result.records == [{"g": "only", "v": 0.0}]
    assert rows == original


def test_unsupported_value_error_is_strict_and_does_not_mutate_input() -> None:
    bad = object()
    rows: list[dict[str, Any]] = [{"g": "only", "v": 1}, {"g": "only", "v": bad}]
    original = rows.copy()
    with pytest.raises(TypeError, match="Unsupported record value") as caught:
        normalize(iter(rows), {"x": "g", "y": "v", "aggregation": "sum", "max_points": 10})
    assert caught.traceback is not None
    assert rows == original and rows[1]["v"] is bad
