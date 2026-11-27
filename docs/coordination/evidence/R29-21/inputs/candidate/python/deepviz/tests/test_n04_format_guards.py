"""Additional boundary cases for the independent N19 format findings."""

import io

import pytest

from deepviz.normalize import normalize


@pytest.mark.parametrize("format", ["json", "jsonl", "auto"])
def test_nested_duplicate_json_keys_are_rejected_before_path_selection(format):
    with pytest.raises(ValueError, match="Duplicate"):
        normalize(
            '{"rows":[{"nested":{"v":1,"v":2}}]}',
            {"kind": "table", "aggregation": "none", "format": format, "data_path": "rows"},
        )


def test_jsonl_duplicate_key_error_keeps_line_location():
    with pytest.raises(ValueError, match="line 2.*Duplicate"):
        normalize('{"v":1}\n{"v":2,"v":3}\n', {"kind": "table", "aggregation": "none", "format": "jsonl"})


def test_stream_bom_removal_does_not_strip_bom_inside_a_cell():
    result = normalize(
        io.StringIO('\ufeffid,label\n1,"\ufeffinside"\n'),
        {"kind": "table", "aggregation": "none", "format": "csv"},
    )
    assert result.records == [{"id": 1, "label": "\ufeffinside"}]


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("reader", [False, True])
def test_empty_arrow_schema_duplicates_are_rejected_before_any_batch_is_read(nested, reader):
    arrow = pytest.importorskip("pyarrow")
    schema = arrow.schema([("v", arrow.int64()), ("v", arrow.int64())])
    if nested:
        schema = arrow.schema([("payload", arrow.struct(list(schema)))])
    table = arrow.Table.from_batches([], schema=schema)
    with pytest.raises(ValueError, match="Duplicate"):
        normalize(table.to_reader() if reader else table, {"kind": "table", "aggregation": "none"})
