"""Small independent statistical oracles for the public normalization contract."""

import math
import statistics
from collections import defaultdict

import pytest
from deepviz.models import ChartSpec
from deepviz.normalize import normalize

REDUCERS = ("sum", "mean", "count", "min", "max")
NUMERIC_REDUCERS = ("sum", "mean", "min", "max")


def _reference(rows, aggregation, group_fields=("category",)):
    """Use stdlib reducers over raw observations, never normalized group means."""
    groups = defaultdict(list)
    for row in rows:
        values = groups[tuple(row.get(field) for field in group_fields)]
        value = row.get("value")
        if aggregation == "count":
            values.append(1)
        elif type(value) in (int, float) and math.isfinite(value):
            values.append(value)
    reduce_values = {
        "sum": math.fsum,
        "mean": statistics.mean,
        "count": len,
        "min": min,
        "max": max,
    }[aggregation]
    return {key: reduce_values(values) if values else None for key, values in groups.items()}


def _by_group(records, group_fields=("category",), value_field="value"):
    actual = {
        tuple(row.get(field) for field in group_fields): row[value_field]
        for row in records
    }
    assert len(actual) == len(records), "The reducer emitted duplicate group keys"
    return actual


def _assert_matches(actual, expected, aggregation):
    assert actual.keys() == expected.keys()
    for key, value in expected.items():
        if aggregation == "count":
            assert type(actual[key]) is int
            assert actual[key] == value
        elif value is None:
            assert actual[key] is None
        else:
            assert actual[key] == pytest.approx(value, rel=1e-12, abs=1e-12)


@pytest.fixture
def mixed_rows():
    return [
        {"category": "a", "value": value}
        for value in (10, -2, 0, "6", "invalid", True, False, None, math.nan, math.inf, -math.inf)
    ] + [{"category": "b", "value": -7}, {"category": "b", "value": 0}]


@pytest.fixture
def overflow_rows():
    # Retained keys recur after overflow; the evicted tenth key also recurs.
    return (
        [{"category": f"g{index}", "value": index - 4} for index in range(9)]
        + [{"category": "g9", "value": 100}]
        + [{"category": "g10", "value": 0} for _ in range(20)]
        + [{"category": "g11", "value": value} for value in (-10, -20)]
        + [{"category": "g12", "value": value} for value in (4, 5, 6, 7)]
        + [
            {"category": "g0", "value": 100},
            {"category": "g9", "value": 200},
            {"category": "g12", "value": None},
        ]
    )


def _assert_overflow(result, rows, aggregation):
    assert result.input_count == len(rows) == 39
    assert result.strategy == aggregation
    assert len(result.records) == 10
    assert any(
        "group" in warning.lower()
        and "max_points" in warning.lower()
        and ("other" in warning.lower() or "merg" in warning.lower())
        for warning in result.warnings
    ), "Loss of category identity must be disclosed, not just the reduction name"
    retained = {f"g{index}" for index in range(9)}
    other = [row for row in result.records if row["category"] not in retained]
    assert len(other) == 1
    assert other[0]["category"] not in {row["category"] for row in rows}
    expected = _reference(rows, aggregation)
    actual = _by_group(result.records)
    retained_expected = {key: value for key, value in expected.items() if key[0] in retained}
    _assert_matches(
        {key: value for key, value in actual.items() if key[0] in retained},
        retained_expected,
        aggregation,
    )
    return other[0]["value"], [row for row in rows if row["category"] not in retained]


@pytest.mark.parametrize("aggregation", REDUCERS)
def test_explicit_reducers_match_reference_for_interleaved_repeated_categories(aggregation):
    rows = [
        {"category": category, "value": value}
        for category, value in (
            ("b", 10), ("a", -2), ("c", -8), ("b", 0), ("c", -4),
            ("a", 0), ("c", -2), ("b", 8), ("c", -10),
        )
    ]
    result = normalize(iter(rows), ChartSpec(x="category", y="value", aggregation=aggregation))

    assert result.input_count == 9
    assert result.strategy == aggregation
    assert len(result.records) == 3
    _assert_matches(_by_group(result.records), _reference(rows, aggregation), aggregation)
    assert result.warnings == []


def test_count_without_y_counts_rows_instead_of_inferred_numeric_measure():
    rows = [
        {"category": category, "value": value}
        for category, value in (("a", 100), ("b", -50), ("a", 0), ("a", 1), ("b", 2))
    ]
    result = normalize(rows, ChartSpec(x="category", aggregation="count"))

    assert result.input_count == 5
    assert result.strategy == "count"
    _assert_matches(_by_group(result.records, value_field="count"), {("a",): 3, ("b",): 2}, "count")


def test_count_with_y_includes_null_nonnumeric_and_nonfinite_rows(mixed_rows):
    result = normalize(mixed_rows, ChartSpec(x="category", y="value", aggregation="count"))

    assert result.input_count == 13
    _assert_matches(_by_group(result.records), {("a",): 11, ("b",): 2}, "count")
    assert sum(row["value"] for row in result.records) == result.input_count


@pytest.mark.parametrize("aggregation", NUMERIC_REDUCERS)
def test_numeric_reducers_exclude_strings_booleans_null_and_nonfinite_values(mixed_rows, aggregation):
    result = normalize(mixed_rows, ChartSpec(x="category", y="value", aggregation=aggregation))

    assert result.input_count == 13
    _assert_matches(_by_group(result.records), _reference(mixed_rows, aggregation), aggregation)
    assert all(math.isfinite(row["value"]) for row in result.records)
    assert any("non-finite" in warning.lower() for warning in result.warnings)
    assert any("non-numeric" in warning.lower() for warning in result.warnings)


@pytest.mark.parametrize("aggregation", NUMERIC_REDUCERS)
def test_missing_y_does_not_become_zero_or_remove_an_all_missing_group(aggregation):
    rows = [
        {"category": "a", "value": -4}, {"category": "a"},
        {"category": "a", "value": 2}, {"category": "b"},
        {"category": "b", "value": None}, {"category": "c", "value": 0},
    ]
    result = normalize(rows, ChartSpec(x="category", y="value", aggregation=aggregation))

    assert result.input_count == 6
    _assert_matches(_by_group(result.records), _reference(rows, aggregation), aggregation)
    assert any("missing" in warning.lower() for warning in result.warnings)


def test_explicit_y_mapping_absent_from_every_record_is_rejected():
    with pytest.raises(ValueError, match="[Mm]issing"):
        normalize(
            [{"category": "a"}, {"category": "a"}],
            ChartSpec(x="category", y="value", aggregation="sum"),
        )


@pytest.mark.parametrize("aggregation", NUMERIC_REDUCERS)
def test_numeric_reduction_without_any_measure_cannot_silently_count(aggregation):
    with pytest.raises(ValueError, match="numeric|measure| y"):
        normalize([{"category": "a"}], ChartSpec(x="category", aggregation=aggregation))


@pytest.mark.parametrize("aggregation", REDUCERS)
def test_color_series_are_distinct_groups_even_with_the_same_x(aggregation):
    rows = [
        {"category": category, "series": series, "value": value}
        for category, series, value in (
            ("mon", "red", 1), ("mon", "blue", 100), ("mon", "red", 2),
            ("tue", "red", -1), ("tue", "blue", 3), ("tue", "blue", 7),
            ("mon", "blue", 0),
        )
    ]
    result = normalize(
        rows, ChartSpec(x="category", y="value", color="series", aggregation=aggregation)
    )

    assert result.input_count == 7
    assert len(result.records) == 4
    fields = ("category", "series")
    _assert_matches(_by_group(result.records, fields), _reference(rows, aggregation, fields), aggregation)
    assert result.warnings == []


def test_overflow_sum_is_bounded_and_conserves_late_and_evicted_contributions(overflow_rows):
    result = normalize(
        iter(overflow_rows), ChartSpec(x="category", y="value", aggregation="sum", max_points=10)
    )

    other, tail = _assert_overflow(result, overflow_rows, "sum")
    assert other == pytest.approx(math.fsum(row["value"] for row in tail if row["value"] is not None))
    assert math.fsum(row["value"] for row in result.records) == pytest.approx(392)


def test_overflow_count_is_bounded_and_conserves_every_row_exactly(overflow_rows):
    result = normalize(
        iter(overflow_rows), ChartSpec(x="category", y="value", aggregation="count", max_points=10)
    )

    other, tail = _assert_overflow(result, overflow_rows, "count")
    assert type(other) is int
    assert other == len(tail) == 29
    assert all(type(row["value"]) is int for row in result.records)
    assert sum(row["value"] for row in result.records) == 39


def test_overflow_mean_weights_raw_observations_not_unequal_group_means(overflow_rows):
    result = normalize(
        iter(overflow_rows), ChartSpec(x="category", y="value", aggregation="mean", max_points=10)
    )

    other, tail = _assert_overflow(result, overflow_rows, "mean")
    values = [row["value"] for row in tail if row["value"] is not None]
    assert len(values) == 28
    expected = statistics.mean(values)
    unweighted_group_mean = statistics.mean(_reference(tail, "mean").values())
    assert abs(expected - unweighted_group_mean) > 20
    assert other == pytest.approx(expected, rel=1e-12, abs=1e-12)


@pytest.mark.parametrize("aggregation", ("min", "max"))
def test_overflow_extrema_include_all_nonretained_groups(overflow_rows, aggregation):
    result = normalize(
        iter(overflow_rows), ChartSpec(x="category", y="value", aggregation=aggregation, max_points=10)
    )

    other, tail = _assert_overflow(result, overflow_rows, aggregation)
    values = [row["value"] for row in tail if row["value"] is not None]
    assert other == (min(values) if aggregation == "min" else max(values))


def test_sum_preserves_small_residual_under_large_cancellation_with_documented_tolerance():
    rows = [
        {"category": category, "value": value}
        for category, values in (
            ("integer", (10**16, 1, -(10**16))),
            ("float", (1e16, 1.0, -1e16)),
        )
        for value in values
    ]
    result = normalize(rows, ChartSpec(x="category", y="value", aggregation="sum"))

    assert result.input_count == 6
    # Compare the residual, not the 1e16 operands: rel=abs=1e-12 allows rounding,
    # but must not conceal the entire lost unit through an operand-scaled bound.
    _assert_matches(_by_group(result.records), _reference(rows, "sum"), "sum")


def test_sampling_is_deterministic_and_returns_selected_rows_in_original_order():
    rows = [{"index": index, "value": (-1) ** index * index} for index in range(75)]
    spec = ChartSpec(kind="scatter", x="index", y="value", aggregation="sample", max_points=10)
    first = normalize(iter(rows), spec)
    second = normalize(iter(rows), spec)

    assert first.input_count == second.input_count == 75
    assert first.strategy == second.strategy == "sample"
    assert first.records == second.records
    assert first.warnings == second.warnings
    assert len(first.records) == 10
    indices = [row["index"] for row in first.records]
    assert indices == sorted(set(indices))
    assert any(index >= 10 for index in indices)
    assert first.records == [rows[index] for index in indices]
    assert any(
        "sampl" in warning.lower() and "75" in warning and "10" in warning
        for warning in first.warnings
    )


def test_sampling_at_limit_keeps_every_row_in_input_order_without_loss_warning():
    rows = [{"index": index, "value": -index} for index in (9, 0, 8, 1, 7, 2, 6, 3, 5, 4)]
    result = normalize(
        iter(rows), ChartSpec(kind="scatter", x="index", y="value", aggregation="sample", max_points=10)
    )

    assert result.input_count == 10
    assert result.records == rows
    assert result.warnings == []
