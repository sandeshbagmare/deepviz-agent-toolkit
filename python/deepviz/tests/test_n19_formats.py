"""Independent row/value oracles for supported formats; no production helpers reused."""
from __future__ import annotations

import copy
import csv
import io
import json
import math
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from deepviz.normalize import normalize

RAW = {"kind": "table", "aggregation": "none", "max_points": 10000}
ARROW_FORMS = [
    "table", "batch", "reader", "ipc-file-bytes", "ipc-stream-bytes",
    "ipc-file-path", "ipc-stream-path", "parquet-bytes", "parquet-path",
]


def _columnar_source(arrow: Any, table: Any, form: str, directory: Path) -> Any:
    if form == "table":
        return table
    if form == "batch":
        return table.combine_chunks().to_batches()[0]
    if form == "reader":
        return table.to_reader(max_chunksize=701)
    sink = arrow.BufferOutputStream()
    if form.startswith("parquet"):
        import pyarrow.parquet as parquet

        parquet.write_table(table, sink, row_group_size=701)
    else:
        writer_factory = arrow.ipc.new_stream if "stream" in form else arrow.ipc.new_file
        with writer_factory(sink, table.schema) as writer:
            writer.write_table(table, max_chunksize=701)
    content = sink.getvalue().to_pybytes()
    if form.endswith("bytes"):
        return content
    path = directory / ("source.parquet" if form.startswith("parquet") else "source.arrow")
    path.write_bytes(content)
    return path


@pytest.mark.parametrize("format", ["json", "jsonl", "csv", "tsv"])
@pytest.mark.parametrize("form", ["str", "bytes", "bytearray", "memoryview", "stream", "path"])
@pytest.mark.parametrize("explicit", [False, True], ids=["auto", "explicit"])
def test_text_adapters_preserve_quoted_unicode_null_and_identifiers(
    format: str, form: str, explicit: bool, tmp_path: Path,
) -> None:
    expected: list[dict[str, Any]] = [
        {"id": "001", "label": 'Montréal, "north"\nsecond\tline', "amount": 1.25},
        {"id": "002", "label": "東京", "amount": None},
        {"id": "003", "label": "final", "amount": -1250},
    ]
    if format == "json":
        text = json.dumps(expected, ensure_ascii=False)
    elif format == "jsonl":
        text = "\n\n".join(json.dumps(row, ensure_ascii=False) for row in expected) + "\n"
    else:
        sink = io.StringIO(newline="")
        writer = csv.DictWriter(sink, expected[0], delimiter="\t" if format == "tsv" else ",")
        writer.writeheader()
        writer.writerows(expected)
        text = sink.getvalue()
    text = "\ufeff" + text
    content = text.encode("utf-8")
    data: Any = text
    if form in {"bytes", "bytearray", "memoryview"}:
        data = {"bytes": bytes, "bytearray": bytearray, "memoryview": memoryview}[form](content)
    elif form == "stream":
        data = io.StringIO(text)
    elif form == "path":
        data = tmp_path / f"records.{format}"
        data.write_bytes(content)
    result = normalize(data, dict(RAW, format=format if explicit else "auto"))
    assert result.records == expected
    assert result.input_count == len(expected)
    assert result.strategy == "none"
    assert result.warnings == []


@pytest.mark.parametrize("form", ARROW_FORMS)
def test_columnar_batches_preserve_every_typed_row_across_4096_boundary(
    form: str, tmp_path: Path,
) -> None:
    arrow = pytest.importorskip("pyarrow")
    start = datetime(2026, 1, 1, tzinfo=UTC)
    raw = []
    expected = []
    for index in range(4103):
        value = math.inf if index in {0, 4095, 4096} else float(index) / 4
        instant = start + timedelta(seconds=index)
        amount = Decimal(index) / 100
        note = None if index % 3 == 0 else f"row-{index}"
        raw.append({
            "id": index, "code": f"{index:05d}", "value": value,
            "amount": amount, "instant": instant, "note": note,
            "parent": {"id": index // 3}, "tags": ["a", "b"],
        })
        expected.append({
            "id": index, "code": f"{index:05d}", "value": None if not math.isfinite(value) else value,
            "amount": float(amount), "instant": instant.isoformat(), "note": note,
            "parent.id": index // 3, "tags.0": "a", "tags.1": "b",
        })
    table = arrow.Table.from_pylist(raw)
    source = _columnar_source(arrow, table, form, tmp_path)
    format = "parquet" if form.startswith("parquet") else "arrow"
    result = normalize(source, dict(RAW, format=format))
    assert result.records == expected
    assert result.input_count == 4103
    assert result.strategy == "none"
    assert result.warnings == ["3 non-finite numeric values replaced by null."]
    json.dumps(result.records, allow_nan=False)


@pytest.mark.parametrize("connection", ["edges", "nodes", "mixed"])
@pytest.mark.parametrize("one_shot", [False, True], ids=["list", "iterator"])
@pytest.mark.parametrize("path", [None, "data.feed"])
def test_graphql_many_pages_match_flat_reference_without_cursor_or_total_rows(
    connection: str, one_shot: bool, path: str | None,
) -> None:
    pages: list[dict[str, Any]] = []
    expected: list[dict[str, Any]] = []
    for page in range(19):
        rows = [{"id": page * 3 + offset, "parent": {"id": page}} for offset in range(3)]
        expected.extend({"id": row["id"], "parent.id": page} for row in rows)
        key = "edges" if connection == "mixed" and page % 2 == 0 else connection
        key = "nodes" if key == "mixed" else key
        nodes: list[Any] = [{"node": row, "cursor": str(row["id"])} for row in rows] if key == "edges" else rows
        nodes.insert(1, {"node": None} if key == "edges" else None)
        pages.append({"data": {"feed": {
            key: nodes, "totalCount": 999999,
            "pageInfo": {"hasNextPage": page != 18, "endCursor": f"page-{page}"},
        }}})
    original = copy.deepcopy(pages)
    source = iter(pages) if one_shot else pages
    result = normalize(source, dict(RAW, data_path=path))
    assert result.records == expected
    assert result.input_count == 57
    assert result.warnings == ["19 null GraphQL/path nodes skipped."]
    assert pages == original
    if one_shot:
        assert list(source) == []


@pytest.mark.parametrize("form", ["records", "columns", "column-generators", "json", "jsonl"])
def test_mixed_nullable_columns_preserve_positions_and_original_types(form: str) -> None:
    values: list[Any] = [0, None, 1.5, "2.5", False, math.nan, math.inf, -math.inf]
    expected = [
        {"position": index, "value": None if isinstance(value, float) and not math.isfinite(value) else value}
        for index, value in enumerate(values)
    ]
    records = [{"position": index, "value": value} for index, value in enumerate(values)]
    source: Any = records
    if form == "columns":
        source = {"position": list(range(len(values))), "value": values}
    elif form == "column-generators":
        source = {"position": iter(range(len(values))), "value": iter(values)}
    elif form == "json":
        source = json.dumps(records)
    elif form == "jsonl":
        source = "\n".join(json.dumps(row) for row in records)
    result = normalize(source, dict(RAW, x="position", y="value"))
    assert result.records == expected
    assert result.input_count == 8
    assert result.warnings == [
        "3 non-finite numeric values replaced by null.",
        "Fields contain mixed numeric/non-numeric values: value.",
    ]
    assert type(result.records[3]["value"]) is str
    assert type(result.records[4]["value"]) is bool
    json.dumps(result.records, allow_nan=False)


def test_sparse_fields_discovered_after_inference_prefix_keep_every_row() -> None:
    source = [{"position": index, **({"value": index * 2} if index % 37 == 0 else {})} for index in range(111)]
    expected = [{"position": index, "value": index * 2 if index % 37 == 0 else None} for index in range(111)]
    result = normalize(iter(source), dict(RAW, x="position", y="value"))
    assert result.records == expected
    assert result.input_count == 111
    assert result.warnings == ["108 missing mapped field values filled with null."]
    assert "value" not in source[1]


def test_typed_time_series_preserves_offsets_dates_and_source_order() -> None:
    source = [
        {"t": datetime.fromisoformat("2026-11-27T01:00:00+05:30"), "day": date(2026, 11, 27), "v": Decimal("1.25")},
        {"t": datetime.fromisoformat("2026-11-26T23:00:00-08:00"), "day": date(2026, 11, 26), "v": Decimal("2.50")},
    ]
    result = normalize(source, dict(RAW, kind="line", x="t", y="v"))
    assert result.records == [
        {"t": "2026-11-27T01:00:00+05:30", "day": "2026-11-27", "v": 1.25},
        {"t": "2026-11-26T23:00:00-08:00", "day": "2026-11-26", "v": 2.5},
    ]
    assert result.input_count == 2
    assert result.warnings == []


def test_hierarchy_children_use_explicit_mapping_without_sibling_loss() -> None:
    source = {"name": "root", "children": [
        {"name": "north", "value": 2, "parent": {"name": "root"}},
        {"name": "south", "value": 5, "parent": {"name": "root"}},
    ]}
    result = normalize(source, dict(RAW, data_path="children", x="name", y="value"))
    assert result.records == [
        {"name": "north", "value": 2, "parent.name": "root"},
        {"name": "south", "value": 5, "parent.name": "root"},
    ]
    assert result.input_count == 2


def test_geojson_features_use_explicit_mapping_and_keep_longitude_latitude() -> None:
    source = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": "west"}, "geometry": {"type": "Point", "coordinates": [-122.4, 37.8]}},
        {"type": "Feature", "properties": {"name": "east"}, "geometry": {"type": "Point", "coordinates": [139.7, 35.7]}},
    ]}
    result = normalize(source, dict(RAW, data_path="features", x="geometry.coordinates.0", y="geometry.coordinates.1"))
    assert result.records == [
        {"type": "Feature", "properties.name": "west", "geometry.type": "Point", "geometry.coordinates.0": -122.4, "geometry.coordinates.1": 37.8},
        {"type": "Feature", "properties.name": "east", "geometry.type": "Point", "geometry.coordinates.0": 139.7, "geometry.coordinates.1": 35.7},
    ]
    assert result.input_count == 2
    assert result.warnings == []


@pytest.mark.parametrize("format,content,match", [
    ("csv", 'a,b\n1,"unterminated\n', "line|delimited"),
    ("csv", "a,b\n1,2,3\n", "column.*line 2"),
    ("tsv", "a\tb\n1\n", "column.*line 2"),
    ("csv", "a,\n1,2\n", "empty column"),
    ("csv", "a,a\n1,2\n", "duplicate"),
    ("json", "[{", "Invalid JSON"),
    ("jsonl", '\n{"v":1}\n\nnot-json\n', "line 4"),
])
def test_malformed_text_is_rejected_without_returning_partial_rows(
    format: str, content: str, match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        normalize(content, dict(RAW, format=format))


def test_malformed_jsonl_after_prefix_is_not_hidden_by_reservoir_sampling() -> None:
    source = "\n".join([*(json.dumps({"v": index}) for index in range(100)), "malformed"])
    with pytest.raises(ValueError, match="line 101"):
        normalize(source, dict(RAW, format="jsonl", max_points=10))


def test_ragged_column_iterators_after_prefix_are_not_silently_truncated() -> None:
    with pytest.raises(ValueError, match="equal length"):
        normalize({"x": iter(range(100)), "y": iter(range(99))}, dict(RAW, max_points=10))


@pytest.mark.parametrize("value", [object(), complex(1, 2), b"opaque"])
def test_opaque_cell_values_require_an_explicit_supported_representation(value: Any) -> None:
    with pytest.raises(TypeError, match="Unsupported record value"):
        normalize([{"id": 1, "value": value}], RAW)


@pytest.mark.parametrize("path", ["missing", "a..b", "a.9", "a.0.missing"])
def test_invalid_data_paths_are_clear_and_never_fall_back_to_another_branch(path: str) -> None:
    with pytest.raises(ValueError, match="data_path"):
        normalize({"a": [{"value": 1}], "other": [{"value": 999}]}, dict(RAW, data_path=path))


@pytest.mark.parametrize("connection", [
    {"edges": [{"cursor": "missing-node"}]},
    {"edges": "not-an-array"},
    {"nodes": {"id": 1}},
    {"edges": [], "nodes": [{"id": 1}]},
])
def test_malformed_or_ambiguous_graphql_connections_fail_clearly(connection: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="GraphQL|data_path"):
        normalize({"data": {"feed": connection}}, RAW)


@pytest.mark.parametrize("form", ARROW_FORMS)
def test_empty_columnar_source_keeps_zero_rows_not_a_schema_row(form: str, tmp_path: Path) -> None:
    arrow = pytest.importorskip("pyarrow")
    table = arrow.table({"id": arrow.array([], type=arrow.int64())})
    if form == "batch":
        source = arrow.record_batch([arrow.array([], type=arrow.int64())], names=["id"])
    else:
        source = _columnar_source(arrow, table, form, tmp_path)
    format = "parquet" if form.startswith("parquet") else "arrow"
    result = normalize(source, dict(RAW, format=format))
    assert result.records == []
    assert result.input_count == 0
    assert result.warnings == []


@pytest.mark.parametrize("nested_list", [False, True], ids=["struct", "list-of-struct"])
def test_nested_duplicate_arrow_fields_are_rejected_without_silent_loss(nested_list: bool) -> None:
    arrow = pytest.importorskip("pyarrow")
    duplicate = arrow.StructArray.from_arrays([arrow.array([1, 2]), arrow.array([90, 99])], names=["v", "v"])
    values = arrow.ListArray.from_arrays(arrow.array([0, 1, 2]), duplicate) if nested_list else duplicate
    table = arrow.Table.from_arrays([arrow.array([0, 1]), values], names=["id", "payload"])
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        normalize(table, RAW)


@pytest.mark.parametrize("format", ["arrow", "parquet"])
def test_corrupt_columnar_bytes_fail_instead_of_becoming_scalar_rows(format: str) -> None:
    pytest.importorskip("pyarrow")
    with pytest.raises(ValueError, match="[Aa]rrow|[Pp]arquet|[Ii][Pp][Cc]|[Ff]ile|magic|schema|metadata bytes"):
        normalize(b"not a columnar file", dict(RAW, format=format))


def test_invalid_utf8_is_not_silently_replaced_or_guessed_as_a_file() -> None:
    with pytest.raises(ValueError, match="UTF-8"):
        normalize(b'[{"label":"\xff"}]', RAW)
