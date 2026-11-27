"""Small independent caller literals; no production-derived numeric expectations."""
from __future__ import annotations

import copy
import io
import json
import math
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize

RAW = {"kind": "table", "aggregation": "none", "max_points": 10}


@pytest.mark.parametrize("encoded", [False, True])
@pytest.mark.parametrize("selected", [False, True])
def test_protocol_named_columns_keep_zero_false_and_null(encoded: bool, selected: bool) -> None:
    columns = {"records": [0, False, None], "items": ["z", "y", "x"]}
    data = {"outer": columns} if selected else columns
    original = copy.deepcopy(data)
    result = normalize(json.dumps(data) if encoded else data, RAW | ({"data_path": "outer"} if selected else {}))
    assert result.records == [{"records": 0, "items": "z"}, {"records": False, "items": "y"}, {"records": None, "items": "x"}]
    assert (result.input_count, result.strategy, result.warnings) == (3, "none", [])
    assert data == original


@pytest.mark.parametrize("encoded", [False, True])
def test_selected_record_arrays_do_not_reinterpret_protocol_cells(encoded: bool) -> None:
    data = {"outer": [{"nodes": [0, False], "items": [None]}, {"nodes": [-2], "items": [True]}]}
    original = copy.deepcopy(data)
    result = normalize(json.dumps(data) if encoded else data, RAW | {"data_path": "outer"})
    assert result.records == [{"nodes.0": 0, "nodes.1": False, "items.0": None}, {"nodes.0": -2, "items.0": True}]
    assert (result.input_count, result.strategy, result.warnings) == (2, "none", [])
    assert data == original


@pytest.mark.parametrize("carrier", ["list", "json", "one-pass"])
def test_business_error_details_remain_repeated_record_fields(carrier: str) -> None:
    data = [{"ref": "audit", "errors": [{"reason": "local", "ok": False}], "value": 0}] * 2
    original = copy.deepcopy(data)
    source = json.dumps(data) if carrier == "json" else iter(data) if carrier == "one-pass" else data
    result = normalize(source, RAW)
    assert result.records == [{"ref": "audit", "errors.0.reason": "local", "errors.0.ok": False, "value": 0}] * 2
    assert (result.input_count, result.strategy, result.warnings) == (2, "none", [])
    assert data == original


@pytest.mark.parametrize("carrier", ["object", "json", "one-pass"])
def test_graphql_null_metadata_empty_middle_and_late_warning(carrier: str) -> None:
    pages = [{"data": {"feed": {"nodes": [{"id": "r", "value": 0}, None, {"id": "r", "value": 0}], "pageInfo": None, "totalCount": None}}, "extensions": None},
             {"data": {"feed": {"nodes": []}}},
             {"data": {"feed": {"edges": [{"node": {"id": "z", "value": -0.5}}, {"node": None}], "pageInfo": None, "totalCount": None}}, "errors": [{"message": "partial flag"}]}]
    original = copy.deepcopy(pages)
    source = json.dumps({"pages": pages}) if carrier == "json" else iter(pages) if carrier == "one-pass" else {"pages": pages}
    result = normalize(source, RAW)
    assert result.records == [{"id": "r", "value": 0}, {"id": "r", "value": 0}, {"id": "z", "value": -0.5}]
    assert (result.input_count, result.strategy) == (3, "none")
    assert len(result.warnings) == 2
    assert sum("null" in value.lower() for value in result.warnings) == 1
    assert sum("errors" in value.lower() for value in result.warnings) == 1
    assert pages == original


def test_error_only_null_metadata_stops_without_closing_borrowed_generator() -> None:
    pulled: list[int] = []
    closed: list[bool] = []
    pages: list[dict[str, Any]] = [{"data": {"feed": {"nodes": [{"id": index} for index in range(35)]}}},
             {"data": {"feed": {"nodes": []}}}, {"data": None, "errors": [{"message": "unavailable"}], "extensions": None}]
    original = copy.deepcopy(pages)

    def supplied() -> Generator[dict[str, Any], None, None]:
        try:
            for index, page in enumerate(pages):
                pulled.append(index)
                yield page
            yield {"host_tail": "still caller-owned"}
        finally:
            closed.append(True)

    source = supplied()
    try:
        with pytest.raises(ValueError, match=r"(?i)graphql.*errors.*data") as caught:
            normalize(source, RAW)
        assert len(str(caught.value)) <= 512
        assert pulled == [0, 1, 2] and not closed
        assert next(source) == {"host_tail": "still caller-owned"}
        assert pages == original
    finally:
        source.close()
    assert closed == [True]


@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("sign", [-1, 1])
@pytest.mark.parametrize("tiny", [False, True])
def test_new_exact_prefix_literals_preserve_signed_fraction_or_subnormal(stream: bool, sign: int, tiny: bool) -> None:
    values = [float(2**52), 3 * math.ulp(0.0), -float(2**52), 4 * math.ulp(0.0), -math.ulp(0.0)] if tiny else [float(2**54), 0.375, -float(2**54), float(2**54), -float(2**54)]
    rows = [{"g": "r", "v": sign * value} for value in values]
    original = copy.deepcopy(rows)
    result = normalize(iter(rows) if stream else rows, {"x": "g", "y": "v", "aggregation": "sum"})
    assert result.records == [{"g": "r", "v": sign * (6 * math.ulp(0.0) if tiny else 0.375)}]
    assert (result.input_count, result.strategy, result.warnings) == (5, "sum", [])
    assert rows == original


@pytest.mark.parametrize("aggregation", ["sum", "count"])
def test_counts_include_input_while_numeric_sum_excludes_boolean_null_and_string(aggregation: str) -> None:
    rows = [{"g": "r", "v": value} for value in [0, False, None, "0", -2]]
    original = copy.deepcopy(rows)
    result = normalize(rows, {"x": "g", "y": "v", "aggregation": aggregation})
    assert result.records == [{"g": "r", "v": -2 if aggregation == "sum" else 5}]
    assert result.input_count == 5 and result.strategy == aggregation
    assert len(result.warnings) == (1 if aggregation == "sum" else 0)
    if aggregation == "sum":
        assert "non-numeric" in result.warnings[0].lower()
    assert rows == original


@pytest.mark.parametrize("owned", [False, True], ids=["borrowed-reader", "owned-path"])
def test_positive_jsonl_lifetime_and_host_content_preserved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, owned: bool) -> None:
    text = '{"v":0}\n{"v":false}\n{"v":null}\n'
    path = tmp_path / "owned.jsonl"
    path.write_text(text, encoding="utf-8")
    handles: list[Any] = []
    original_open = Path.open

    def opened(self: Path, *args: Any, **kwargs: Any) -> Any:
        handle = original_open(self, *args, **kwargs)
        if self == path:
            handles.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", opened)
    borrowed = io.StringIO(text)
    try:
        result = normalize(path if owned else borrowed, RAW | {"format": "jsonl"})
        assert result.records == [{"v": 0}, {"v": False}, {"v": None}]
        assert (result.input_count, result.strategy, result.warnings) == (3, "none", [])
        if owned:
            assert handles and all(handle.closed for handle in handles)
            path.rename(path.with_suffix(".released"))
            assert path.with_suffix(".released").read_text(encoding="utf-8") == text
        else:
            assert not borrowed.closed
            borrowed.seek(0)
            assert borrowed.read() == text
    finally:
        borrowed.close()
