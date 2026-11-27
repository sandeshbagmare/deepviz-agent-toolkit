"""Caller-authored count expectations, independent of emitted native payloads."""
from __future__ import annotations

import copy
from typing import Any

from deepviz.engines import matplotlib_figure, native_spec
from deepviz.models import ChartSpec
from deepviz.normalize import normalize

SOURCE_SHA = "5340bc69b7203ad7a9166543062482d819f9b705"
ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")
ROWS = [
    {"group": "A", "position": 0, "series": 90, "weight": 900, "measure": 10},
    {"group": "A", "position": 0, "series": 90, "weight": 900, "measure": 10},
    {"group": "B", "position": 1, "series": 80, "weight": 800, "measure": 20},
    {"group": "B", "position": 1, "series": 80, "weight": 800, "measure": 20},
    {"group": "B", "position": 1, "series": 80, "weight": 800, "measure": 20},
    {"group": "C", "position": 10, "series": 70, "weight": 700, "measure": 30},
]
COUNT_RECORDS = [
    {"group": "A", "series": 90, "count": 2},
    {"group": "B", "series": 80, "count": 3},
    {"group": "C", "series": 70, "count": 1},
]
BUBBLE_RECORDS = [
    {"position": 0, "series": 90, "count": 2},
    {"position": 1, "series": 80, "count": 3},
    {"position": 10, "series": 70, "count": 1},
]
COUNT_PAIRS = [("A", 2), ("B", 3), ("C", 1)]
BUBBLE_PAIRS = [(0, 2), (1, 3), (10, 1)]
SUM_PAIRS = [("A", 20), ("B", 60), ("C", 30)]
NONE_ROWS = [
    {"group": "A", "series": 90, "weight": 900, "measure": 4},
    {"group": "B", "series": 80, "weight": 800, "measure": 7},
    {"group": "C", "series": 70, "weight": 700, "measure": 2},
]
NONE_PAIRS = [("A", 4), ("B", 7), ("C", 2)]


def count_spec(kind: str = "bar", **changes: Any) -> ChartSpec:
    config: dict[str, Any] = {
        "kind": kind, "title": "Requested COUNT: A=2, B=3, C=1", "x": "group", "color": "series",
        "aggregation": "count", "width": 720, "height": 440, "max_points": 10,
    }
    if kind == "bubble":
        config.update(x="position", size="series")
    return ChartSpec.model_validate(config | changes)


def normalized_count(kind: str = "bar"):
    spec = count_spec(kind)
    result = normalize(copy.deepcopy(ROWS), spec)
    assert result.records == (BUBBLE_RECORDS if kind == "bubble" else COUNT_RECORDS)
    assert (result.input_count, len(result.records), result.strategy, result.warnings) == (6, 3, "count", [])
    return result, spec


def native_values(engine: str, records: list[dict], spec: ChartSpec) -> list[tuple[Any, float]]:
    """Read actual engine measure/artist data; do not compute expected counts here."""
    if engine == "matplotlib":
        figure, notes = matplotlib_figure([(records, spec)])
        assert not notes
        try:
            axis = figure.axes[0]
            if spec.kind == "bar":
                values = [float(mark.get_height()) for mark in axis.patches]
            elif spec.kind == "line":
                values = [float(value) for line in axis.lines for value in line.get_ydata()]
            else:
                values = [float(point[1]) for collection in axis.collections for point in collection.get_offsets()]
            return [(row[spec.x], value) for row, value in zip(records, values, strict=True)]
        finally:
            figure.clear()
    native, notes, actual_kind = native_spec(engine, records, spec)
    assert not notes and actual_kind == spec.kind, "native kind changed/fallback"
    if engine == "plotly":
        return [(x, y) for trace in native["data"] for x, y in zip(trace["x"], trace["y"], strict=True)]
    if engine == "vega":
        assert native["encoding"]["y"]["type"] == "quantitative"
        return [(row[native["encoding"]["x"]["field"]], row[native["encoding"]["y"]["field"]])
                for row in native["data"]["values"]]
    if engine == "echarts":
        assert native["yAxis"]["type"] == "value"
        return [(item["value"][0], item["value"][1]) if isinstance(item, dict) else tuple(item[:2])
                for series in native["series"] for item in series["data"]]
    if spec.kind == "line":
        return [(row[child["encode"]["x"]], row[child["encode"]["y"]])
                for child in native["children"] if child["type"] == "line" for row in child["data"]]
    return [(row[native["encode"]["x"]], row[native["encode"]["y"]]) for row in native["data"]]
