"""N19 minimal data-loss regressions; source fixes belong to the N04 owner."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from test_n19_formats import ARROW_FORMS, RAW, _columnar_source

from deepviz.normalize import normalize


@pytest.mark.parametrize("form", ARROW_FORMS)
def test_duplicate_columnar_field_names_are_rejected_before_pylist_data_loss(form: str, tmp_path: Path) -> None:
    arrow = pytest.importorskip("pyarrow")
    table = arrow.Table.from_arrays([arrow.array([1, 2]), arrow.array([90, 99])], names=["v", "v"])
    source = _columnar_source(arrow, table, form, tmp_path)
    format = "parquet" if form.startswith("parquet") else "arrow"
    with pytest.raises(ValueError, match="[Dd]uplicate|unique|[Aa]mbiguous|[Mm]ultiple matches"):
        normalize(source, dict(RAW, format=format))


@pytest.mark.parametrize("format,content", [
    ("json", '[{"v":1,"v":99}]'),
    ("jsonl", '{"v":1,"v":99}\n'),
    ("auto", '[{"v":1,"v":99}]'),
    ("auto", '{"v":1}\n{"v":2,"v":99}\n'),
])
def test_duplicate_json_keys_are_rejected_instead_of_losing_original_fields(format: str, content: str) -> None:
    with pytest.raises(ValueError, match="[Dd]uplicate|[Aa]mbiguous"):
        normalize(content, dict(RAW, format=format))


@pytest.mark.parametrize("name", ["nodes", "edges"])
def test_reserved_name_columns_are_preserved_or_clearly_rejected_as_ambiguous(name: str) -> None:
    source = {name: [1, 2], "value": [3, 4]}
    try:
        result = normalize(source, RAW)
    except ValueError as error:
        assert any(term in str(error).lower() for term in ["ambiguous", "data_path", "graphql"])
    else:
        assert result.records == [{name: 1, "value": 3}, {name: 2, "value": 4}]
        assert result.input_count == 2


@pytest.mark.parametrize("path", ["data.feed", "data.feed.nodes"])
@pytest.mark.parametrize("pages", [False, True], ids=["single-response", "page-list"])
def test_explicit_graphql_mapping_does_not_hide_partial_response_errors(path: str, pages: bool) -> None:
    response: dict[str, Any] = {
        "data": {"feed": {"nodes": [{"id": 1}]}},
        "errors": [{"message": "a sibling resolver failed"}],
    }
    result = normalize([response] if pages else response, dict(RAW, data_path=path))
    assert result.records == [{"id": 1}]
    assert result.input_count == 1
    assert any("GraphQL" in warning and "errors" in warning for warning in result.warnings)
