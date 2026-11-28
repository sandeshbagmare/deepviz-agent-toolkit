"""Public normalization contracts for GraphQL responses and connections."""

import pytest
from deepviz.models import ChartSpec, NormalizedData
from deepviz.normalize import normalize


@pytest.fixture
def raw_spec() -> ChartSpec:
    return ChartSpec(kind="table", aggregation="none")


def test_nested_collection_edges_extract_only_node_records(raw_spec: ChartSpec) -> None:
    response = {
        "data": {
            "collection": {
                "edges": [
                    {"cursor": "cursor-a", "node": {"id": "a", "value": 12}},
                    {"cursor": "cursor-b", "node": {"id": "b", "value": 7}},
                ]
            }
        }
    }

    result = normalize(response, raw_spec)

    assert isinstance(result, NormalizedData)
    assert result.records == [{"id": "a", "value": 12}, {"id": "b", "value": 7}]
    assert result.input_count == 2
    assert result.strategy == "none"
    assert result.warnings == []


def test_direct_nodes_connection_needs_no_edges_wrapper(raw_spec: ChartSpec) -> None:
    response = {"nodes": [{"id": "a", "value": 4}, {"id": "b", "value": 9}]}

    result = normalize(response, raw_spec)

    assert result.records == [{"id": "a", "value": 4}, {"id": "b", "value": 9}]
    assert result.input_count == 2


def test_paginated_full_responses_preserve_all_pages_in_order(raw_spec: ChartSpec) -> None:
    pages = [
        {
            "data": {
                "collection": {
                    "edges": [{"cursor": "one", "node": {"id": "a", "value": 1}}],
                    "pageInfo": {"hasNextPage": True, "endCursor": "one"},
                }
            }
        },
        {
            "data": {
                "collection": {
                    "nodes": [{"id": "b", "value": 2}, {"id": "c", "value": 3}],
                    "pageInfo": {"hasNextPage": False, "endCursor": "three"},
                }
            }
        },
    ]

    result = normalize(pages, raw_spec)

    assert result.records == [
        {"id": "a", "value": 1},
        {"id": "b", "value": 2},
        {"id": "c", "value": 3},
    ]
    assert result.input_count == 3


def test_page_info_is_not_flattened_into_rows_or_counted(raw_spec: ChartSpec) -> None:
    response = {
        "data": {
            "collection": {
                "nodes": [{"id": "a", "value": 6}],
                "pageInfo": {
                    "hasNextPage": True,
                    "hasPreviousPage": False,
                    "startCursor": "before-a",
                    "endCursor": "after-a",
                },
            }
        }
    }

    result = normalize(response, raw_spec)

    assert result.records == [{"id": "a", "value": 6}]
    assert result.input_count == 1
    assert result.warnings == []


def test_partial_data_is_retained_with_deterministic_error_warning(raw_spec: ChartSpec) -> None:
    response = {
        "data": {"collection": {"nodes": [{"id": "available", "value": 8}]}},
        "errors": [
            {
                "message": "A sibling field could not be resolved",
                "path": ["unavailableField"],
                "extensions": {"code": "UPSTREAM_UNAVAILABLE"},
            }
        ],
    }

    result = normalize(response, raw_spec)
    repeated = normalize(response, raw_spec)

    assert result.records == [{"id": "available", "value": 8}]
    assert result.input_count == 1
    assert any("graphql" in warning.lower() and "error" in warning.lower() for warning in result.warnings)
    assert repeated == result


@pytest.mark.parametrize("wrapper", [None, "items", "data", "records"])
def test_partial_response_errors_inside_wrappers_are_reported_once(
    wrapper: str | None, raw_spec: ChartSpec,
) -> None:
    response = {
        "data": {"feed": {"nodes": [{"id": "available", "value": 8}]}},
        "errors": [{"message": "A sibling field failed"}],
    }
    source = response if wrapper is None else {wrapper: response}
    result = normalize(source, raw_spec)
    assert result.records == [{"id": "available", "value": 8}]
    assert result.warnings == ["1 GraphQL responses contained errors alongside usable data."]


def test_null_edge_and_direct_nodes_are_skipped_not_counted(raw_spec: ChartSpec) -> None:
    pages = [
        {
            "data": {
                "collection": {
                    "edges": [
                        {"node": None},
                        {"node": {"id": "a", "value": 2}},
                    ]
                }
            }
        },
        {"data": {"collection": {"nodes": [{"id": "b", "value": 3}, None]}}},
    ]

    result = normalize(pages, raw_spec)

    assert result.records == [{"id": "a", "value": 2}, {"id": "b", "value": 3}]
    assert result.input_count == 2
    assert any("null" in warning.lower() and "skip" in warning.lower() for warning in result.warnings)


def test_empty_connection_returns_zero_records_without_metadata_row(raw_spec: ChartSpec) -> None:
    response = {
        "data": {
            "collection": {
                "edges": [],
                "totalCount": 0,
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }
    }

    result = normalize(response, raw_spec)

    assert result.records == []
    assert result.input_count == 0
    assert result.strategy == "none"
    assert result.warnings == []


def test_custom_dot_path_broadcasts_through_multiple_array_levels() -> None:
    """Dot components traverse every array element, not just its first item."""
    response = {
        "data": {
            "departments": [
                {
                    "collection": {
                        "edges": [
                            {"node": {"id": "a", "value": 1}},
                            {"node": {"id": "b", "value": 2}},
                        ]
                    }
                },
                {"collection": {"edges": []}},
                {"collection": {"edges": [{"node": {"id": "c", "value": 3}}]}},
            ],
            "unselected": {"nodes": [{"id": "not-selected", "value": 100}]},
        }
    }
    spec = ChartSpec(
        kind="table",
        aggregation="none",
        data_path="data.departments.collection.edges.node",
    )

    result = normalize(response, spec)

    assert result.records == [
        {"id": "a", "value": 1},
        {"id": "b", "value": 2},
        {"id": "c", "value": 3},
    ]
    assert result.input_count == 3
    assert result.warnings == []


def test_node_parent_relationship_is_flattened_into_mapped_fields() -> None:
    response = {
        "data": {
            "collection": {
                "edges": [
                    {
                        "node": {
                            "id": "child",
                            "parent": {
                                "id": "parent",
                                "name": "Parent label",
                                "parent": {"id": "grandparent"},
                            },
                            "measure": {"amount": 11},
                        }
                    }
                ]
            }
        }
    }
    spec = ChartSpec(kind="scatter", x="parent.name", y="measure.amount", aggregation="none")

    result = normalize(response, spec)

    assert result.records == [
        {
            "id": "child",
            "parent.id": "parent",
            "parent.name": "Parent label",
            "parent.parent.id": "grandparent",
            "measure.amount": 11,
        }
    ]
    assert result.input_count == 1
    assert result.warnings == []


def test_aggregation_totals_and_input_count_use_rows_not_page_or_server_totals() -> None:
    pages = [
        {
            "data": {
                "collection": {
                    "totalCount": 500,
                    "edges": [
                        {"node": {"team": "A", "score": 1}},
                        {"node": {"team": "B", "score": 4}},
                    ],
                    "pageInfo": {"hasNextPage": True, "endCursor": "page-one"},
                }
            }
        },
        {
            "data": {
                "collection": {
                    "totalCount": 500,
                    "nodes": [
                        {"team": "A", "score": 2},
                        {"team": "B", "score": 5},
                        {"team": "A", "score": 3},
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": "page-two"},
                }
            }
        },
    ]
    spec = ChartSpec(kind="bar", x="team", y="score", aggregation="sum")

    result = normalize(pages, spec)

    assert result.records == [{"team": "A", "score": 6}, {"team": "B", "score": 9}]
    assert result.input_count == 5
    assert result.strategy == "sum"
    assert result.warnings == []
