"""Regressions for bounded accumulation and selected GraphQL envelopes."""

import json
import math

import pytest

from deepviz.normalize import normalize


def test_sum_keeps_small_float_contributions_across_repeated_cancellation():
    rows = ({"group": "a", "value": value} for value in [1e16, 1.0, -1e16] * 40)
    result = normalize(rows, {"x": "group", "y": "value", "aggregation": "sum"})

    assert result.records == [{"group": "a", "value": 40.0}]
    assert result.input_count == 120
    assert result.warnings == []


def test_overflow_bucket_keeps_compensation_from_evicted_and_late_rows():
    rows = [{"group": f"g{i}", "value": i} for i in range(9)]
    rows += [
        {"group": "evicted", "value": 1e16},
        {"group": "evicted", "value": 1.0},
        {"group": "late", "value": -1e16},
        {"group": "later", "value": 2.0},
    ]
    result = normalize(
        iter(rows), {"x": "group", "y": "value", "aggregation": "sum", "max_points": 10}
    )

    assert result.input_count == 13
    assert len(result.records) == 10
    assert result.records[-1]["value"] == 3.0
    assert math.fsum(row["value"] for row in result.records) == 39.0
    assert any("other" in warning for warning in result.warnings)


def test_sum_preserves_integer_precision_and_nonfinite_output_policy():
    result = normalize(
        [{"group": "integer", "value": value} for value in (10**100, 1, -(10**100))]
        + [{"group": "overflow", "value": 1e308}] * 2,
        {"x": "group", "y": "value", "aggregation": "sum"},
    )

    assert result.records == [{"group": "integer", "value": 1}, {"group": "overflow", "value": None}]
    assert type(result.records[0]["value"]) is int
    assert any("non-finite" in warning for warning in result.warnings)
    json.dumps(result.records, allow_nan=False)


@pytest.mark.parametrize("data_path", ["data.users", "data.users.nodes", "data.users.nodes.id"])
def test_data_path_retains_graphql_partial_error_warning(data_path):
    response = {
        "data": {"users": {"nodes": [{"id": 1}]}},
        "errors": [{"message": "A sibling field failed"}],
    }
    result = normalize(response, {"kind": "table", "aggregation": "none", "data_path": data_path})

    assert result.input_count == 1
    assert result.records == ([{"index": 0, "value": 1}] if data_path.endswith(".id") else [{"id": 1}])
    assert result.warnings == ["1 GraphQL responses contained errors alongside usable data."]


def test_data_path_counts_each_partial_graphql_page_once():
    pages = (
        {"data": {"users": {"nodes": [{"id": i}]}}, "errors": [{"message": "partial"}]}
        for i in range(3)
    )
    result = normalize(
        pages, {"kind": "table", "aggregation": "none", "data_path": "data.users.nodes"}
    )

    assert result.records == [{"id": 0}, {"id": 1}, {"id": 2}]
    assert result.input_count == 3
    assert result.warnings == ["3 GraphQL responses contained errors alongside usable data."]


@pytest.mark.parametrize("data_path", ["data.users.nodes", "errors"])
def test_data_path_cannot_hide_graphql_error_only_response(data_path):
    with pytest.raises(ValueError, match="GraphQL.*errors.*no data"):
        normalize(
            {"data": None, "errors": [{"message": "unavailable"}]},
            {"kind": "table", "aggregation": "none", "data_path": data_path},
        )


def test_mean_keeps_small_residual_after_large_cancellation():
    result = normalize(
        [{"group": "a", "value": value} for value in (1e16, 1.0, -1e16)],
        {"x": "group", "y": "value", "aggregation": "mean"},
    )

    assert result.records[0]["value"] == pytest.approx(1 / 3, rel=1e-15)
    assert result.input_count == 3
    assert result.warnings == []


def test_mean_keeps_finite_answer_when_raw_sum_exceeds_float_range():
    result = normalize(
        [{"group": "a", "value": value} for value in (1e308, 1e308, -1e308)],
        {"x": "group", "y": "value", "aggregation": "mean"},
    )

    assert result.records[0]["value"] == pytest.approx(1e308 / 3, rel=1e-15)
    assert result.warnings == []
    json.dumps(result.records, allow_nan=False)


@pytest.mark.parametrize("text", ["a" * (64 * 1024 + 1), "\U0001f600" * (16 * 1024 + 1)])
def test_oversize_string_cells_are_rejected_by_utf8_bytes(text):
    with pytest.raises(ValueError, match="cell.*bytes|bytes.*cell"):
        normalize([{"text": text}], {"kind": "table", "aggregation": "none"})


def test_oversize_flattened_field_names_are_rejected():
    with pytest.raises(ValueError, match="field.*bytes|bytes.*field"):
        normalize([{"name" * 1025: 1}], {"kind": "table", "aggregation": "none"})


def test_record_byte_budget_catches_many_individually_valid_cells():
    row = {f"field{i}": "a" * (60 * 1024) for i in range(5)}
    with pytest.raises(ValueError, match="record.*bytes|bytes.*record"):
        normalize([row], {"kind": "table", "aggregation": "none"})


@pytest.mark.parametrize("aggregation", ["none", "sum"])
def test_retained_byte_budget_stops_wide_stream_before_consuming_it_all(aggregation):
    consumed = 0

    def rows():
        nonlocal consumed
        for i in range(1000):
            consumed += 1
            yield {"group": f"{i}:" + "a" * (63 * 1024), "value": 1}

    with pytest.raises(ValueError, match="retained.*bytes|bytes.*retained"):
        normalize(rows(), {"x": "group", "y": "value", "aggregation": aggregation, "max_points": 1000})
    assert consumed < 300


def test_large_total_stream_can_reduce_to_a_small_retained_payload():
    result = normalize(
        ({"group": "a", "unused": "x" * (32 * 1024), "value": 1} for _ in range(600)),
        {"x": "group", "y": "value", "aggregation": "sum"},
    )

    assert result.input_count == 600
    assert result.records == [{"group": "a", "value": 600}]
    assert result.warnings == []


def test_mean_preserves_scaled_compensation_after_group_eviction():
    rows = [{"group": f"g{i}", "value": 0} for i in range(9)]
    rows += [
        {"group": "evicted", "value": 1e308},
        {"group": "evicted", "value": 1e308},
        {"group": "late", "value": -1e308},
    ]
    result = normalize(
        rows, {"x": "group", "y": "value", "aggregation": "mean", "max_points": 10}
    )

    assert result.input_count == 12
    assert len(result.records) == 10
    assert result.records[-1]["value"] == pytest.approx(1e308 / 3, rel=1e-15)
    assert any("other" in warning for warning in result.warnings)
    assert not any("non-finite" in warning for warning in result.warnings)


def test_string_cell_at_utf8_byte_limit_is_preserved_without_truncation():
    text = "\U0001f600" * (16 * 1024)
    result = normalize([{"text": text}], {"kind": "table", "aggregation": "none"})

    assert result.records == [{"text": text}]
    assert result.warnings == []


def test_record_byte_budget_includes_json_escape_expansion():
    with pytest.raises(ValueError, match="record.*bytes|bytes.*record"):
        normalize([{"text": "\x00" * (64 * 1024)}], {"kind": "table", "aggregation": "none"})


def test_record_compact_json_budget_is_inclusive_at_exact_boundary():
    row = dict.fromkeys("abc", "x" * (64 * 1024)) | {"d": "y" * (64 * 1024 - 29)}
    assert len(json.dumps(row, separators=(",", ":")).encode()) == 256 * 1024
    assert normalize([row], {"kind": "table", "aggregation": "none"}).records == [row]
    with pytest.raises(ValueError, match="record.*bytes|bytes.*record"):
        normalize([dict(row, d=row["d"] + "y")], {"kind": "table", "aggregation": "none"})


def test_retained_compact_json_budget_includes_array_delimiters():
    text = "x" * (64 * 1024)
    rows = [{"value": text} for _ in range(255)] + [{"value": text[:-3329]}]
    assert len(json.dumps(rows, separators=(",", ":")).encode()) == 16 * 1024 * 1024
    spec = {"kind": "table", "aggregation": "none", "max_points": 256}
    assert normalize(rows, spec).records == rows
    with pytest.raises(ValueError, match="retained.*bytes|bytes.*retained"):
        normalize([*rows[:-1], {"value": rows[-1]["value"] + "x"}], spec)


def test_reservoir_replacement_checks_growth_in_retained_payload():
    rows = ({"text": "x" * ((40 if i < 300 else 63) * 1024)} for i in range(3000))
    with pytest.raises(ValueError, match="retained.*bytes|bytes.*retained"):
        normalize(rows, {"kind": "table", "aggregation": "none", "max_points": 300})


def test_reducer_accounts_for_large_numeric_states_before_full_stream_consumption():
    consumed = 0
    value = 10**2000

    def rows():
        nonlocal consumed
        for i in range(10000):
            consumed += 1
            yield {"group": f"g{i}", "value": value}

    with pytest.raises(ValueError, match="retained.*bytes|bytes.*retained"):
        normalize(rows(), {"x": "group", "y": "value", "aggregation": "sum", "max_points": 10000})
    assert consumed < 10000
