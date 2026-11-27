"""C17-authorized JSON numeric identity and stable record-boundary rules."""

import pytest

from deepviz.normalize import normalize


@pytest.mark.parametrize("aggregation,expected", [("sum", 6), ("mean", 3), ("count", 2), ("min", 2), ("max", 4)])
def test_equal_int_float_categories_share_one_group_but_keep_first_representative(aggregation, expected):
    rows = [{"g": 1.0, "v": 2}, {"g": 1, "v": 4}, {"g": True, "v": 8}, {"g": "1", "v": 16}]
    result = normalize(rows, {"x": "g", "y": "v", "aggregation": aggregation})
    assert len(result.records) == 3
    assert result.records[0] == {"g": 1.0, "v": expected}
    assert type(result.records[0]["g"]) is float
    assert result.records[1]["g"] is True
    assert result.records[2]["g"] == "1"


@pytest.mark.parametrize("field", ["tags", "items", "data", "records", "rows", "results"])
def test_list_of_records_retains_array_field_names_instead_of_inferring_columns_or_wrappers(field):
    result = normalize([{field: ["a", "b"]}], {"kind": "table", "aggregation": "none"})
    assert result.input_count == 1
    assert result.records == [{f"{field}.0": "a", f"{field}.1": "b"}]


@pytest.mark.parametrize("reverse", [False, True])
def test_nested_connection_named_record_field_is_independent_of_key_order(reverse):
    pairs = [("metadata", {"nodes": [{"n": 1}]}), ("id", 1)]
    row = dict(reversed(pairs) if reverse else pairs)
    for source in (row, [row]):
        result = normalize(source, {"kind": "table", "aggregation": "none"})
        assert result.records == [{"metadata.nodes.0.n": 1, "id": 1}]
        assert result.input_count == 1


def test_custom_object_of_column_arrays_keeps_custom_column_name():
    result = normalize({"payload": [{"id": 1}, {"id": 2}]}, {"kind": "table", "aggregation": "none"})
    assert result.records == [{"payload.id": 1}, {"payload.id": 2}]
    assert result.input_count == 2


def test_custom_graphql_wrapper_needs_path_instead_of_stripping_wrapper_name():
    source = {"payload": {"nodes": [{"id": 1}]}}
    with pytest.raises(ValueError, match="[Cc]ustom|[Aa]mbiguous|data_path"):
        normalize(source, {"kind": "table", "aggregation": "none"})
    result = normalize(source, {"kind": "table", "aggregation": "none", "data_path": "payload.nodes"})
    assert result.records == [{"id": 1}]
