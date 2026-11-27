"""Ingestion contracts, including streaming reductions rather than head truncation."""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tracemalloc
from pathlib import Path
from typing import Any

import pytest

from deepviz.models import ChartSpec, NormalizedData
from deepviz.normalize import normalize as normalize_impl


def normalize(data: Any, spec: ChartSpec | dict[str, Any] | None = None) -> NormalizedData:
    return normalize_impl(data, spec if spec is not None else {"aggregation": "none"})


def test_scalar_array_has_stable_index_and_value_fields() -> None:
    result = normalize([1, 3, 5])
    assert result.records == [
        {"index": 0, "value": 1}, {"index": 1, "value": 3}, {"index": 2, "value": 5},
    ]
    assert result.input_count == 3
    assert result.strategy == "none"
    assert result.warnings == []


def test_records_are_flattened_without_mutating_input() -> None:
    data = [{"person": {"name": "A"}, "samples": [{"value": 2}, 3]}]
    result = normalize(data)
    assert result.records == [{"person.name": "A", "samples.0.value": 2, "samples.1": 3}]
    assert data[0]["person"] == {"name": "A"}


def test_column_mapping_is_zipped_and_unequal_columns_are_rejected() -> None:
    assert normalize({"x": [1, 2], "y": [3, 4]}).records == [{"x": 1, "y": 3}, {"x": 2, "y": 4}]
    with pytest.raises(ValueError, match="length"):
        normalize({"x": [1, 2], "y": [3]})


def test_column_generators_are_consumed_once() -> None:
    result = normalize({"x": iter([1, 2]), "y": iter([3, 4])})
    assert result.records == [{"x": 1, "y": 3}, {"x": 2, "y": 4}]


def test_data_path_fans_out_arrays_and_keeps_all_pages() -> None:
    pages = [
        {"data": {"shops": [{"sales": [{"v": 1}, {"v": 2}]}, {"sales": [{"v": 3}]}]}},
        {"data": {"shops": [{"sales": [{"v": 4}]}]}},
    ]
    result = normalize(iter(pages), {"data_path": "data.shops.sales", "aggregation": "none"})
    assert result.records == [{"v": 1}, {"v": 2}, {"v": 3}, {"v": 4}]
    assert result.input_count == 4


def test_data_path_supports_explicit_array_indices() -> None:
    result = normalize({"groups": [[{"v": 1}], [{"v": 2}]]}, {"data_path": "groups.1"})
    assert result.records == [{"v": 2}]


@pytest.mark.parametrize("connection", ["edges", "nodes"])
def test_graphql_connections_across_pages_are_not_truncated(connection: str) -> None:
    def page(value: int) -> dict[str, Any]:
        rows = [{"node": {"id": value}}] if connection == "edges" else [{"id": value}]
        return {"data": {"users": {connection: rows, "pageInfo": {"hasNextPage": True}}}}

    result = normalize([page(1), page(2), page(3)])
    assert result.records == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert result.input_count == 3


def test_graphql_edge_node_path_and_null_nodes() -> None:
    data = {"data": {"users": {"edges": [{"node": {"v": 1}}, {"node": None}]}}}
    result = normalize(data, {"data_path": "data.users.edges.node"})
    assert result.records == [{"v": 1}]
    assert any("null" in warning.lower() for warning in result.warnings)


@pytest.mark.parametrize("text,format", [
    ('[{"a":1},{"a":2}]', "json"),
    ('{"a":1}\n\n{"a":2}\n', "jsonl"),
    ('a,b\n1,"hello, world"\n2,ok\n', "csv"),
    ('a\tb\n1\thello\n2\tok\n', "tsv"),
])
def test_text_formats_preserve_records_and_parse_numeric_cells(text: str, format: str) -> None:
    result = normalize(text, {"format": format, "aggregation": "none"})
    assert result.input_count == 2
    assert [row["a"] for row in result.records] == [1, 2]


def test_delimited_empty_cells_are_none_and_identifiers_keep_leading_zeroes() -> None:
    result = normalize("code,value\n001,2.5\n002,\n", {"format": "csv"})
    assert result.records == [{"code": "001", "value": 2.5}, {"code": "002", "value": None}]


def test_path_is_explicit_opt_in_and_plain_strings_are_not_opened(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("x,y\n1,2\n3,4\n", encoding="utf-8")
    assert normalize(path).records == [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
    with pytest.raises(ValueError, match="content|format|JSON|delimited"):
        normalize(str(path))


def test_bytes_and_jsonl_path_use_utf8_and_preserve_all_lines(tmp_path: Path) -> None:
    path = tmp_path / "data.jsonl"
    path.write_text('{"v":1}\n{"v":2}\n', encoding="utf-8")
    assert normalize(path).input_count == 2
    assert normalize(b'\xef\xbb\xbf[{"v":1}]').records == [{"v": 1}]


def test_missing_nonfinite_and_mixed_values_are_reported_not_silently_dropped() -> None:
    data = [{"x": 1, "y": math.inf}, {"x": 2, "y": math.nan}, {"x": 3}, {"x": 4, "y": "bad"}]
    result = normalize(data, {"kind": "scatter", "x": "x", "y": "y", "aggregation": "none"})
    assert result.records == [
        {"x": 1, "y": None}, {"x": 2, "y": None}, {"x": 3, "y": None}, {"x": 4, "y": "bad"},
    ]
    assert result.input_count == 4
    assert any("non-finite" in warning for warning in result.warnings)
    assert any("missing" in warning for warning in result.warnings)


def test_mixed_numeric_and_text_values_are_warned() -> None:
    result = normalize([{"v": 1}, {"v": "one"}])
    assert any("mixed" in warning for warning in result.warnings)


@pytest.mark.parametrize("reduction,expected", [
    ("sum", [{"category": "a", "value": 8}, {"category": "b", "value": 2}]),
    ("mean", [{"category": "a", "value": 4}, {"category": "b", "value": 2}]),
    ("count", [{"category": "a", "value": 3}, {"category": "b", "value": 1}]),
    ("min", [{"category": "a", "value": 3}, {"category": "b", "value": 2}]),
    ("max", [{"category": "a", "value": 5}, {"category": "b", "value": 2}]),
])
def test_grouped_reductions_have_explicit_null_and_count_semantics(reduction: str, expected: Any) -> None:
    data = [
        {"category": "a", "value": 3}, {"category": "a", "value": None},
        {"category": "b", "value": 2}, {"category": "a", "value": 5},
    ]
    result = normalize(data, {"x": "category", "y": "value", "aggregation": reduction})
    assert result.records == expected
    assert result.input_count == 4
    assert result.strategy == reduction


def test_reductions_preserve_color_groups() -> None:
    data = [{"x": "a", "series": "one", "y": 1}, {"x": "a", "series": "two", "y": 2}]
    result = normalize(data, {"x": "x", "y": "y", "color": "series", "aggregation": "sum"})
    assert result.records == [{"x": "a", "series": "one", "y": 1}, {"x": "a", "series": "two", "y": 2}]


def test_all_null_numeric_groups_are_none_not_zero() -> None:
    result = normalize([{"x": "a", "y": None}], {"x": "x", "y": "y", "aggregation": "sum"})
    assert result.records == [{"x": "a", "y": None}]


def test_invalid_numeric_values_are_excluded_from_mean_denominator_with_warning() -> None:
    rows = [{"x": "a", "y": 4}, {"x": "a", "y": "bad"}, {"x": "a", "y": True}]
    result = normalize(rows, {"x": "x", "y": "y", "aggregation": "mean"})
    assert result.records == [{"x": "a", "y": 4}]
    assert any("non-numeric" in warning for warning in result.warnings)


def test_auto_categorical_sum_and_count_are_explicit() -> None:
    result = normalize([{"x": "a", "y": 2}, {"x": "a", "y": 4}], {"x": "x", "y": "y"})
    assert result.records == [{"x": "a", "y": 6}]
    assert result.strategy == "sum"
    counted = normalize([{"x": "a"}, {"x": "a"}], {"x": "x"})
    assert counted.records == [{"x": "a", "count": 2}]
    assert counted.strategy == "count"


@pytest.mark.parametrize("reduction,total", [("sum", 4950), ("count", 100)])
def test_high_cardinality_reductions_keep_all_contributions_in_other_bucket(reduction: str, total: int) -> None:
    result = normalize(
        ({"x": str(index), "y": index} for index in range(100)),
        {"x": "x", "y": "y", "aggregation": reduction, "max_points": 10},
    )
    assert len(result.records) == 10
    assert sum(row["y"] for row in result.records) == total
    assert result.input_count == 100
    assert any("other" in warning.lower() and "cardinality" in warning.lower() for warning in result.warnings)


def test_other_mean_is_weighted_from_raw_rows_not_mean_of_means() -> None:
    data = [{"x": str(i), "y": 0} for i in range(9)]
    data += [{"x": "a", "y": 10}] + [{"x": "b", "y": 20}] * 3
    result = normalize(data, {"x": "x", "y": "y", "aggregation": "mean", "max_points": 10})
    assert len(result.records) == 10
    assert result.records[-1]["y"] == 17.5


def test_other_bucket_cannot_collide_with_a_real_category() -> None:
    data = [{"x": "__deepviz_other__", "y": 5}] + [{"x": str(i), "y": 1} for i in range(20)]
    result = normalize(data, {"x": "x", "y": "y", "aggregation": "sum", "max_points": 10})
    assert len({row["x"] for row in result.records}) == 10
    assert sum(row["y"] for row in result.records) == 25


@pytest.mark.parametrize("aggregation", ["auto", "sample", "none"])
def test_numeric_stream_is_bounded_deterministic_and_not_head_truncated(aggregation: str) -> None:
    spec = {"kind": "scatter", "x": "x", "y": "y", "aggregation": aggregation, "max_points": 10}
    result = normalize(({"x": i, "y": i * 2} for i in range(10000)), spec)
    repeated = normalize(({"x": i, "y": i * 2} for i in range(10000)), spec)
    assert result.records == repeated.records
    assert len(result.records) == 10
    assert result.input_count == 10000
    assert max(row["x"] for row in result.records) > 5000
    assert result.strategy == "sample"
    assert result.warnings


def test_generator_is_never_eagerly_materialized() -> None:
    tracemalloc.start()
    try:
        result = normalize(
            ({"x": i, "y": i * 2} for i in range(50000)),
            {"kind": "scatter", "x": "x", "y": "y", "max_points": 10},
        )
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result.input_count == 50000
    assert peak < 4_000_000


@pytest.mark.parametrize("data", [[], iter(()), {}, "[]"])
def test_empty_inputs_have_zero_count(data: Any) -> None:
    result = normalize(data)
    assert result.records == []
    assert result.input_count == 0


@pytest.mark.parametrize("data,spec,match", [
    ([{"a": 1}], {"x": "missing"}, "missing"),
    ({"a": []}, {"data_path": "not.there"}, "data_path"),
    ([{"a": 1, "a.b": 2, "b": {"c": 3}}], {"y": "missing"}, "missing"),
    ([{"a.b": 1, "a": {"b": 2}}], {}, "collision|duplicate"),
    ('{"x":1}\nnot json', {"format": "jsonl"}, "line 2"),
    ("a,b\n1\n", {"format": "csv"}, "line|column"),
    ("a,a\n1,2\n", {"format": "csv"}, "duplicate"),
    ({"edges": [{"cursor": "a"}]}, {}, "node"),
    ({"errors": [{"message": "failed"}]}, {}, "GraphQL|errors"),
    ([{"v": object()}], {}, "unsupported|Unsupported"),
])
def test_malformed_inputs_fail_clearly(data: Any, spec: dict[str, Any], match: str) -> None:
    with pytest.raises((ValueError, TypeError), match=match):
        normalize(data, spec)


def test_explicit_global_reduction_needs_no_category() -> None:
    result = normalize([1, 2, 3], {"y": "value", "aggregation": "mean"})
    assert result.records == [{"value": 2}]
    assert result.input_count == 3


def test_json_serializable_records_never_contain_nan_or_infinity() -> None:
    result = normalize([{"x": math.inf, "nested": {"y": -math.inf}}])
    assert json.dumps(result.records, allow_nan=False)


def test_optional_arrow_table_and_parquet_path(tmp_path: Path) -> None:
    arrow = pytest.importorskip("pyarrow")
    parquet = pytest.importorskip("pyarrow.parquet")
    table = arrow.table({"x": [1, 2], "y": [3, 4]})
    assert normalize(table).records == [{"x": 1, "y": 3}, {"x": 2, "y": 4}]
    path = tmp_path / "data.parquet"
    parquet.write_table(table, path)
    assert normalize(path).input_count == 2


def test_models_are_accepted_without_mutation() -> None:
    spec = ChartSpec(kind="scatter", x="x", y="y")
    before = spec.model_dump()
    assert normalize([{"x": 1, "y": 2}], spec).records == [{"x": 1, "y": 2}]
    assert spec.model_dump() == before


def test_scalar_reductions_infer_value_not_the_synthetic_index() -> None:
    assert normalize([10, 20, 30], {"aggregation": "sum"}).records == [{"value": 60}]


def test_count_without_explicit_measure_is_named_count() -> None:
    result = normalize([{"x": "a", "y": 3}, {"x": "a", "y": None}], {"x": "x", "aggregation": "count"})
    assert result.records == [{"x": "a", "count": 2}]


def test_empty_field_mappings_are_rejected() -> None:
    with pytest.raises(ValueError, match="field|empty"):
        normalize([{"x": 1}], {"x": ""})


def test_discovered_fields_are_validated_across_entire_stream_not_only_sample() -> None:
    rows = [{"x": i} for i in range(50)] + [{"x": 50, "late": 3}]
    result = normalize(iter(rows), {"kind": "scatter", "x": "x", "y": "late", "max_points": 10})
    assert result.input_count == 51
    assert any("missing" in warning for warning in result.warnings)


def test_schema_width_limit_prevents_unbounded_key_accumulation() -> None:
    with pytest.raises(ValueError, match="fields"):
        normalize(({f"field{i}": i} for i in range(1100)), {"max_points": 10})


def test_cyclic_records_fail_with_bounded_depth() -> None:
    row: dict[str, Any] = {"x": 1}
    row["self"] = row
    with pytest.raises(ValueError, match="deeply|cyclic"):
        normalize([row])


def test_null_scalar_values_are_rows_not_lost_pages() -> None:
    assert normalize([None, 3]).records == [{"index": 0, "value": None}, {"index": 1, "value": 3}]


def test_float_reduction_overflow_does_not_escape_as_nonfinite_json() -> None:
    result = normalize([{"x": "a", "y": 1e308}] * 2, {"x": "x", "y": "y", "aggregation": "sum"})
    assert result.records == [{"x": "a", "y": None}]
    assert result.warnings
    assert json.dumps(result.records, allow_nan=False)


def test_optional_arrow_ipc_file_and_stream_bytes(tmp_path: Path) -> None:
    arrow = pytest.importorskip("pyarrow")
    table = arrow.table({"x": [1, 2], "y": [3, 4]})
    for writer_factory in (arrow.ipc.new_file, arrow.ipc.new_stream):
        sink = arrow.BufferOutputStream()
        with writer_factory(sink, table.schema) as writer:
            writer.write_table(table)
        content = sink.getvalue().to_pybytes()
        assert normalize(content, {"format": "arrow"}).records == [{"x": 1, "y": 3}, {"x": 2, "y": 4}]
        path = tmp_path / "table.arrow"
        path.write_bytes(content)
        assert normalize(path).input_count == 2


def test_scale_benchmark_measures_real_inputs_in_isolated_processes() -> None:
    script = Path(__file__).resolve().parents[3] / "scripts" / "benchmark_scale.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--sizes", "100", "--modes", "sample", "sum"],
        capture_output=True, text=True, check=True,
    )
    results = [json.loads(line) for line in completed.stdout.splitlines()]
    assert len(results) == 2
    assert all(result["input_count"] == 100 for result in results)
    assert all(result["output_count"] <= 2000 for result in results)
    assert all(result["elapsed_seconds"] > 0 for result in results)
    assert all(result["peak_rss_bytes"] > 0 for result in results)


def test_empty_record_rows_are_counted_instead_of_disappearing() -> None:
    result = normalize([{}, {"v": 1}, {}])
    assert result.input_count == 3
    assert result.records == [{}, {"v": 1}, {}]


def test_missing_field_on_only_empty_records_is_still_invalid() -> None:
    with pytest.raises(ValueError, match="missing"):
        normalize([{}, {}], {"x": "missing"})


def test_path_through_empty_connection_is_valid_and_empty() -> None:
    result = normalize({"data": {"users": {"edges": []}}}, {"data_path": "data.users.edges.node"})
    assert result.input_count == 0
    assert result.records == []


def test_ambiguous_graphql_connections_require_an_explicit_path() -> None:
    data = {"data": {"users": {"nodes": [{"id": 1}]}, "posts": {"nodes": [{"id": 2}]}}}
    with pytest.raises(ValueError, match="data_path|ambiguous|Multiple"):
        normalize(data)
    assert normalize(data, {"data_path": "data.users"}).records == [{"id": 1}]


def test_high_cardinality_grouped_stream_has_bounded_memory_and_exact_total() -> None:
    tracemalloc.start()
    try:
        result = normalize(
            ({"x": str(i), "y": i} for i in range(20000)),
            {"x": "x", "y": "y", "aggregation": "sum", "max_points": 10},
        )
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result.input_count == 20000
    assert sum(row["y"] for row in result.records) == 199990000
    assert peak < 4_000_000


@pytest.mark.parametrize("aggregation,expected", [("min", 9), ("max", 99)])
def test_overflow_bucket_extrema_include_every_overflow_row(aggregation: str, expected: int) -> None:
    result = normalize(
        ({"x": str(i), "y": i} for i in range(100)),
        {"x": "x", "y": "y", "aggregation": aggregation, "max_points": 10},
    )
    assert result.records[-1]["y"] == expected


def test_auto_scalar_categories_count_rows_instead_of_summing_synthetic_indices() -> None:
    result = normalize(["a", "a", "b"], {})
    assert result.records == [{"value": "a", "count": 2}, {"value": "b", "count": 1}]
    assert result.strategy == "count"


def test_auto_mixed_scalar_values_do_not_map_same_field_to_group_and_measure() -> None:
    result = normalize([1, "a", None, 2], {})
    assert result.input_count == 4
    assert [row["value"] for row in result.records] == [1, "a", None, 2]
    assert any("mixed" in warning for warning in result.warnings)


def test_reductions_cannot_silently_remove_a_mapped_size_field() -> None:
    with pytest.raises(ValueError, match="size|sample"):
        normalize([{"x": "a", "y": 1, "s": 3}], {"x": "x", "y": "y", "size": "s", "aggregation": "sum"})


def test_json_path_index_selects_same_rows_from_content_and_path(tmp_path: Path) -> None:
    data = [[{"v": 1}], [{"v": 2}]]
    path = tmp_path / "nested.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert normalize(path, {"data_path": "1"}).records == [{"v": 2}]
    assert normalize(path, {"data_path": "1"}).records == normalize(data, {"data_path": "1"}).records


def test_graphql_both_edges_and_nodes_cannot_silently_prefer_one() -> None:
    data = {"data": {"users": {"edges": [], "nodes": [{"v": 1}]}}}
    with pytest.raises(ValueError, match="data_path|both|ambiguous"):
        normalize(data)
    assert normalize(data, {"data_path": "data.users.nodes"}).records == [{"v": 1}]


def test_path_ending_at_graphql_edges_unwraps_each_node() -> None:
    data = {"data": {"users": {"edges": [{"cursor": "1", "node": {"id": 1}}]}}}
    result = normalize(data, {"data_path": "data.users.edges", "x": "id"})
    assert result.records == [{"id": 1}]


@pytest.mark.parametrize("kind", ["line", "area"])
def test_connected_samples_keep_source_order_and_warn_that_peaks_can_be_missed(kind: str) -> None:
    result = normalize(
        ({"source_position": i, "x": 10000 - i, "y": i % 13} for i in range(10000)),
        {"kind": kind, "x": "x", "y": "y", "max_points": 10},
    )
    positions = [row["source_position"] for row in result.records]
    assert positions == sorted(positions)
    assert [row["x"] for row in result.records] == sorted((row["x"] for row in result.records), reverse=True)
    assert len(result.records) == 10
    assert result.input_count == 10000
    assert any("peak" in warning.lower() for warning in result.warnings)


def test_heatmap_reduction_preserves_both_coordinates_and_aggregates_color() -> None:
    rows = [
        {"day": "Mon", "region": "North", "temperature": 10},
        {"day": "Mon", "region": "South", "temperature": 20},
        {"day": "Tue", "region": "North", "temperature": 30},
        {"day": "Tue", "region": "South", "temperature": 40},
    ]
    spec = {"kind": "heatmap", "x": "day", "y": "region", "color": "temperature"}
    result = normalize(rows, spec)
    assert result.records == rows
    assert result.input_count == 4
    assert result.strategy == "sum"
    assert result.warnings == []
    duplicated = normalize([*rows, {"day": "Mon", "region": "North", "temperature": 2}], spec)
    assert duplicated.records == [dict(rows[0], temperature=12), *rows[1:]]
    assert duplicated.input_count == 5


def test_heatmap_without_color_counts_each_coordinate_pair() -> None:
    rows = [{"day": "Mon", "region": "North"}] * 2 + [{"day": "Mon", "region": "South"}]
    result = normalize(rows, {"kind": "heatmap", "x": "day", "y": "region"})
    assert result.records == [
        {"day": "Mon", "region": "North", "count": 2},
        {"day": "Mon", "region": "South", "count": 1},
    ]
    assert result.strategy == "count"


def test_heatmap_mean_uses_valid_color_observations_not_coordinate_values() -> None:
    rows = [
        {"day": "Mon", "region": "North", "temperature": 10},
        {"day": "Mon", "region": "North", "temperature": None},
        {"day": "Mon", "region": "North", "temperature": 20},
    ]
    result = normalize(rows, {
        "kind": "heatmap", "x": "day", "y": "region", "color": "temperature", "aggregation": "mean",
    })
    assert result.records == [{"day": "Mon", "region": "North", "temperature": 15}]


def test_heatmap_numeric_reduction_without_color_is_rejected_instead_of_summing_coordinates() -> None:
    with pytest.raises(ValueError, match="color|measure"):
        normalize([{"x": 1, "y": 2}], {"kind": "heatmap", "x": "x", "y": "y", "aggregation": "sum"})
