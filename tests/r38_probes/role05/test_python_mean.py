"""Independent bounded mean oracles; no production-derived expected values."""
from __future__ import annotations

import json
import math
import random
import struct
import sys
from collections.abc import Callable, Iterator
from fractions import Fraction
from typing import Any

import pytest

from deepviz import normalize

TINY = float.fromhex("0x0.0000000000001p-1022")
MAX = float.fromhex("0x1.fffffffffffffp+1023")
Record = dict[str, Any]
Property = Callable[[str, Any], None]
SPEC = {"x": "g", "y": "v", "aggregation": "mean", "max_points": 10}
LITERALS = [
    ("positive-even-lower", [TINY, 4 * TINY], 2 * TINY),
    ("negative-even-lower", [-TINY, -4 * TINY], -2 * TINY),
    ("thirds-subnormal", [TINY, 2 * TINY, 4 * TINY], 2 * TINY),
    ("positive-even-upper", [0.0, 3 * TINY], 2 * TINY),
    ("negative-even-upper", [0.0, -3 * TINY], -2 * TINY),
    ("positive-rounded-zero", [0.0, TINY, 0.0], 0.0),
    ("negative-rounded-zero", [0.0, -TINY, 0.0], -0.0),
    ("largest-constant", [MAX, MAX], MAX),
    ("largest-third", [MAX, MAX, -MAX], float.fromhex("0x1.5555555555555p+1022")),
    ("normal-after-extremes", [MAX, MAX, -MAX, -MAX, 5.0], 1.0),
    ("epsilon-after-cancellation", [1.0, 2.0**-52, -1.0], float.fromhex("0x1.5555555555555p-54")),
    ("python-wide-int-residual", [2**1200, 3, -(2**1200)], 1.0),
    ("safe-boundary-integer", [2**53, 1, -(2**53), 3], 1.0),
    ("opposite-signed-zero", [-0.0, 0.0, -0.0, 0.0], 0.0),
    ("late-wide-beyond-inference", [0.0] * 36 + [MAX, MAX, -MAX, -MAX, 82 * TINY], 2 * TINY),
    ("negative-largest-constant", [-MAX, -MAX], -MAX),
]


def bits(value: float) -> str:
    return struct.pack(">d", value).hex()


def exact_mean(values: list[int | float]) -> float:
    """Standard-library exact rational and its final binary64 conversion only."""
    return float(sum((Fraction(value) for value in values), Fraction()) / len(values))


def snapshot(rows: list[Record]) -> str:
    return json.dumps(rows, ensure_ascii=False, sort_keys=True, allow_nan=True)


class OnePass:
    def __init__(self, rows: list[Record]):
        self.rows = rows
        self.iterations = 0
        self.yielded = 0

    def __iter__(self) -> Iterator[Record]:
        self.iterations += 1
        assert self.iterations == 1, "The caller's stream was iterated twice"
        for row in self.rows:
            self.yielded += 1
            yield row


def consume(rows: list[Record], stream: bool, spec: Record, prop: Property) -> Any:
    assert len(rows) <= 1024
    original = snapshot(rows)
    original_spec = snapshot([spec])
    source = OnePass(rows)
    try:
        result = normalize(source if stream else rows, spec)
    finally:
        assert snapshot(rows) == original, "Public normalization mutated caller records"
        assert snapshot([spec]) == original_spec, "Public normalization mutated its spec"
        prop("input_fixture_records", len(rows))
        prop("stream_iterations", source.iterations)
        prop("stream_yielded", source.yielded)
    assert result.input_count == len(rows)
    assert result.strategy == "mean"
    assert source.iterations == (1 if stream else 0)
    assert source.yielded == (len(rows) if stream else 0)
    json.dumps(result.records, allow_nan=False)
    prop("output_records", len(result.records))
    prop("warnings", json.dumps(result.warnings))
    return result


@pytest.mark.parametrize("stream", [False, True], ids=["records", "one-pass"])
@pytest.mark.parametrize("name,values,literal", LITERALS, ids=[case[0] for case in LITERALS])
def test_literal_binary64_mean(
    name: str, values: list[int | float], literal: float, stream: bool, record_property: Property,
) -> None:
    expected = exact_mean(values)
    assert bits(expected) == bits(literal), f"Literal and independent Fraction disagree: {name}"
    rows = [{"g": "all", "v": value, "meta": {"row": index}} for index, value in enumerate(values)]
    result = consume(rows, stream, dict(SPEC), record_property)
    assert len(result.records) == 1 and result.records[0]["g"] == "all"
    actual = result.records[0]["v"]
    assert type(actual) is float and bits(actual) == bits(literal)
    assert result.warnings == []
    record_property("expected_binary64", bits(literal))
    record_property("actual_binary64", bits(actual))


@pytest.mark.parametrize("stream", [False, True], ids=["records", "one-pass"])
@pytest.mark.parametrize("exponent", [-1074, -1022, -54, 0, 100, 1023])
def test_independent_fraction_reference_grid(exponent: int, stream: bool, record_property: Property) -> None:
    # Deterministic finite-input grids, not a statistical/performance claim.
    rng = random.Random(20261127 + exponent)
    values = [math.ldexp((rng.getrandbits(12) | 1) * (-1 if index % 3 else 1), exponent - 12)
              for index in range(13)]
    assert all(math.isfinite(value) for value in values)
    expected = exact_mean(values)
    result = consume([{"g": "rational", "v": value} for value in values], stream, dict(SPEC), record_property)
    actual = result.records[0]["v"]
    assert type(actual) is float and bits(actual) == bits(expected)
    assert result.records[0]["g"] == "rational" and result.warnings == []
    record_property("reference", "stdlib Fraction of actual finite binary floats; one final float conversion")
    record_property("expected_binary64", bits(expected))
    record_property("actual_binary64", bits(actual))


@pytest.mark.parametrize("sign", [1, -1], ids=["positive", "negative"])
def test_weighted_other_collision_null_and_numeric_counts(sign: int, record_property: Property) -> None:
    retained = ["__deepviz_other__", *(f"keep{index}" for index in range(1, 9))]
    rows = [{"g": key, "v": index} for index, key in enumerate(retained)]
    evicted = [sign * MAX, sign * MAX, -sign * MAX, -sign * MAX, sign * 2 * TINY]
    rows += [{"g": "evicted", "v": value} for value in evicted]
    rows += [{"g": "late", "v": sign * 3 * TINY} for _ in range(3)]
    rows += [{"g": "late", "v": value} for value in [None, True, False, "17"]]
    rows += [{"g": "late"}]
    valid = [*evicted, *([sign * 3 * TINY] * 3)]
    expected = sign * TINY
    assert bits(exact_mean(valid)) == bits(expected)
    result = consume(rows, True, dict(SPEC), record_property)
    assert len(result.records) == 10
    assert result.records[:9] == [{"g": key, "v": float(index)} for index, key in enumerate(retained)]
    assert result.records[-1]["g"] == "__deepviz_other___", "Reserved literal category must not collide"
    assert bits(result.records[-1]["v"]) == bits(expected)
    assert any("weighted mean" in message and "other" in message for message in result.warnings)
    assert any("3 non-numeric" in message for message in result.warnings)
    assert any("1 missing" in message for message in result.warnings)
    record_property("other_valid_observations", 8)
    record_property("expected_other_binary64", bits(expected))


@pytest.mark.parametrize("all_invalid", [False, True], ids=["valid-denominator-only", "all-invalid-null"])
def test_null_boolean_text_nonfinite_and_missing_denominator(all_invalid: bool, record_property: Property) -> None:
    values: list[Any] = [None, True, False, "8", float("nan"), float("inf"), -float("inf")]
    if not all_invalid:
        values += [4.0, 2.0]
    rows = [{"g": "all", "v": value} for value in values] + [{"g": "all"}]
    result = consume(rows, True, dict(SPEC), record_property)
    assert result.records == [{"g": "all", "v": None if all_invalid else 3.0}]
    assert any("3 non-finite" in message for message in result.warnings)
    assert any("3 non-numeric" in message for message in result.warnings)
    assert any("1 missing" in message for message in result.warnings)


def test_empty_mean_is_empty_without_invented_numeric_observation(record_property: Property) -> None:
    result = consume([], True, dict(SPEC), record_property)
    assert result.records == [] and result.warnings == []


def test_global_mean_without_group_mapping(record_property: Property) -> None:
    rows = [{"v": value} for value in [MAX, -MAX, 3.0]]
    result = consume(rows, True, {"kind": "scatter", "y": "v", "aggregation": "mean"}, record_property)
    assert result.records == [{"v": 1.0}] and result.warnings == []


def test_heatmap_mean_uses_color_measure_and_two_coordinates(record_property: Property) -> None:
    rows = [{"x": "c1", "y": "r1", "z": value} for value in [4.0, 8.0]]
    rows += [{"x": "c2", "y": "r1", "z": -MAX}]
    spec = {"kind": "heatmap", "x": "x", "y": "y", "color": "z", "aggregation": "mean"}
    result = consume(rows, True, spec, record_property)
    assert result.records == [{"x": "c1", "y": "r1", "z": 6.0}, {"x": "c2", "y": "r1", "z": -MAX}]
    assert result.warnings == []


def test_invalid_point_budget_rejects_before_stream_consumption(record_property: Property) -> None:
    rows = [{"g": "only", "v": TINY}]
    source = OnePass(rows)
    with pytest.raises(ValueError, match="max_points"):
        normalize(source, {**SPEC, "max_points": 9})
    assert source.iterations == source.yielded == 0
    record_property("stream_yielded", source.yielded)


def test_late_oversize_utf8_cell_raises_instead_of_returning_prefix(record_property: Property) -> None:
    rows = [{"g": "all", "v": TINY} for _ in range(32)]
    rows += [{"g": "all", "v": TINY, "note": "é" * 32769}]
    source = OnePass(rows)
    original = snapshot(rows)
    with pytest.raises(ValueError, match="cell exceeds 65536 UTF-8 bytes"):
        normalize(source, dict(SPEC))
    assert source.iterations == 1 and source.yielded == 33
    assert snapshot(rows) == original
    record_property("stream_yielded", source.yielded)


def test_oversize_record_is_not_silently_dropped_from_mean(record_property: Property) -> None:
    rows = [{"g": "all", "v": 2.0, **{f"note{index}": "q" * 65530 for index in range(5)}}]
    source = OnePass(rows)
    original = snapshot(rows)
    with pytest.raises(ValueError, match="record exceeds 262144 compact UTF-8 JSON bytes"):
        normalize(source, dict(SPEC))
    assert source.iterations == source.yielded == 1 and snapshot(rows) == original
    record_property("stream_yielded", source.yielded)


def test_real_retained_mean_state_budget_rejects_bounded_stream(record_property: Property) -> None:
    consumed = 0

    def rows() -> Iterator[Record]:
        nonlocal consumed
        for index in range(300):
            consumed += 1
            yield {"g": f"{index:04d}:" + "q" * 65520, "v": sys.float_info.max}

    with pytest.raises(ValueError, match="Normalized retained data exceeds 16777216 bytes"):
        normalize(rows(), {**SPEC, "max_points": 300})
    # Each category is individually legal; rejection must precede swallowing the full input.
    assert 32 <= consumed <= 257 < 300 <= 1024
    record_property("stream_yielded", consumed)
    record_property("advertised_input_records", 300)
    record_property("budget_method", "real public 16MiB retained-state guard; no patched constants or RSS claim")
