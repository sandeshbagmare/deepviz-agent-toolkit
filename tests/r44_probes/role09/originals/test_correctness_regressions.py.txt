"""Strict R10-01 contract oracles; RED is intentional until source owners fix it."""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from deepviz import normalize
from deepviz.engines import channels, native_spec
from deepviz.models import ChartSpec

IDENTITY = {"kind": "table", "aggregation": "none"}
COLUMN_NAMES = ("rows", "records", "items", "results", "data")
COUNT_SPEC = {"kind": "bar", "x": "g", "color": "s", "aggregation": "count"}


def connection(key: str) -> dict:
    rows = [{"id": 1}] if key == "nodes" else [{"node": {"id": 1}}]
    return {key: rows}


def test_imports_come_from_this_checkout() -> None:
    root = Path(__file__).resolve().parents[3]
    for name in ("normalize", "models", "engines"):
        actual = Path(importlib.import_module(f"deepviz.{name}").__file__).resolve()
        assert actual == root / "python" / "deepviz" / "src" / "deepviz" / f"{name}.py"


@pytest.mark.parametrize("key", ("nodes", "edges"))
@pytest.mark.parametrize("sibling", ({"version": 7}, {"audit": {"source": "left"}}))
def test_f1_connection_siblings_require_explicit_selection(key: str, sibling: dict) -> None:
    with pytest.raises(ValueError, match=r"(?i)ambiguous.*data_path"):
        normalize(connection(key) | sibling, IDENTITY)


@pytest.mark.parametrize("key", ("nodes", "edges"))
def test_f1_explicit_connection_path_preserves_rows(key: str) -> None:
    result = normalize(connection(key) | {"version": 7}, IDENTITY | {"data_path": key})
    assert result.records == [{"id": 1}]
    assert result.input_count == 1
    assert result.warnings == []


@pytest.mark.parametrize("key", ("nodes", "edges"))
def test_f1_metadata_is_not_mistaken_for_an_ambiguous_sibling(key: str) -> None:
    result = normalize(connection(key) | {"totalCount": 7}, IDENTITY)
    assert result.records == [{"id": 1}]
    assert result.input_count == 1


def test_f1_custom_graphql_wrapper_requires_a_path() -> None:
    with pytest.raises(ValueError, match=r"(?i)custom.*data_path"):
        normalize({"payload": {"nodes": [{"id": 1}]}}, IDENTITY)


def test_f1_custom_graphql_wrapper_explicit_path_is_valid() -> None:
    result = normalize({"payload": {"nodes": [{"id": 1}]}}, IDENTITY | {"data_path": "payload.nodes"})
    assert result.records == [{"id": 1}]


@pytest.mark.parametrize("key", COLUMN_NAMES)
def test_f3_named_scalar_columns_survive_explicit_mapping(key: str) -> None:
    result = normalize({key: [1, 2]}, IDENTITY | {"y": key})
    assert result.records == [{key: 1}, {key: 2}]
    assert result.input_count == 2


@pytest.mark.parametrize("key", COLUMN_NAMES)
def test_f3_record_arrays_keep_the_parent_and_array_field(key: str) -> None:
    result = normalize([{"id": 7, key: [1, 2]}], IDENTITY)
    assert result.records == [{"id": 7, f"{key}.0": 1, f"{key}.1": 2}]
    assert result.input_count == 1


def test_f3_custom_scalar_column_keeps_its_name() -> None:
    assert normalize({"payload": [1, 2]}, IDENTITY).records == [{"payload": 1}, {"payload": 2}]


def test_f2_reducer_itself_preserves_the_exact_count() -> None:
    result = normalize([{"g": "a", "s": 100}] * 2, COUNT_SPEC)
    assert result.records == [{"g": "a", "s": 100, "count": 2}]
    assert result.input_count == 2
    assert result.warnings == []
    json.dumps(result.records, allow_nan=False)


@pytest.mark.parametrize("series", (0, 100, -4))
def test_f2_count_channels_use_count_not_numeric_series(series: int) -> None:
    result = normalize([{"g": "a", "s": series}] * 2, COUNT_SPEC)
    mapped = channels(result.records, ChartSpec.model_validate(COUNT_SPEC))
    assert [row["_y"] for row in mapped] == [2]


@pytest.mark.parametrize("engine", ("echarts", "plotly", "antv", "vega"))
def test_f2_native_count_values_match_the_reduced_measure(engine: str) -> None:
    result = normalize([{"g": "a", "s": 100}] * 2, COUNT_SPEC)
    native, _, _ = native_spec(engine, result.records, ChartSpec.model_validate(COUNT_SPEC))
    if engine == "echarts":
        actual = [point[1] for series in native["series"] for point in series["data"]]
    elif engine == "plotly":
        actual = [value for trace in native["data"] for value in trace["y"]]
    else:
        rows = native["data"] if engine == "antv" else native["data"]["values"]
        actual = [row["_y"] for row in rows]
    assert actual == [2]


def test_f2_explicit_count_measure_is_not_renamed() -> None:
    spec = COUNT_SPEC | {"y": "v"}
    result = normalize([{"g": "a", "s": 100, "v": None}] * 2, spec)
    assert result.records == [{"g": "a", "s": 100, "v": 2}]
    assert [row["_y"] for row in channels(result.records, ChartSpec.model_validate(spec))] == [2]


def test_f2_categorical_color_count_is_a_working_control() -> None:
    result = normalize([{"g": "a", "s": "blue"}] * 2, COUNT_SPEC)
    assert [row["_y"] for row in channels(result.records, ChartSpec.model_validate(COUNT_SPEC))] == [2]


def test_f2_heatmap_count_preserves_y_coordinate_and_color_measure() -> None:
    spec = {"kind": "heatmap", "x": "g", "y": "coordinate", "color": "v", "aggregation": "count"}
    result = normalize([{"g": "a", "coordinate": 100, "v": None}] * 2, spec)
    mapped = channels(result.records, ChartSpec.model_validate(spec))
    assert result.records == [{"g": "a", "coordinate": 100, "v": 2}]
    assert mapped[0]["_y"] == 100
    assert mapped[0]["_heat"] == 2