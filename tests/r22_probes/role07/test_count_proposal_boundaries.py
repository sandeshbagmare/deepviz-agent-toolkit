"""Six novel boundary cases; no old COUNT/native/browser matrix replay."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict

import pytest

from deepviz.engines import channels
from deepviz.models import ChartSpec
from deepviz.normalize import normalize


def test_auto_count_uses_real_planner_not_numeric_color_reinterpretation():
    rows = [{"label": "A", "shade": "east"}, {"label": "A", "shade": "east"},
            {"label": "B", "shade": "west"}]
    spec = ChartSpec(x="label", color="shade", aggregation="auto")
    result = normalize(rows, spec)
    assert asdict(result) == {"records": [{"label": "A", "shade": "east", "count": 2},
                                         {"label": "B", "shade": "west", "count": 1}],
                              "input_count": 3, "warnings": [], "strategy": "count"}
    before = deepcopy(asdict(result))
    assert [row["_y"] for row in channels(result.records, spec)] == [2, 1]
    assert [row["_color"] for row in channels(result.records, spec)] == ["east", "west"]
    assert asdict(result) == before and spec.aggregation == "auto" and spec.y is None
    numeric_color = [{**row, "shade": 90 if row["shade"] == "east" else 80} for row in rows]
    # Auto infers SUM from that numeric field; its grouping collision must reject.
    with pytest.raises(ValueError, match="measure must differ from grouping fields"):
        normalize(numeric_color, spec)


def test_missing_generated_measure_is_not_filled_from_retained_numeric_size():
    # Direct helper boundary, intentionally not a valid reducer output: fail closed.
    rows = [{"label": "zero", "series": 90, "count": 0},
            {"label": "null", "series": 80, "count": None},
            {"label": "missing", "series": 70}]
    spec = ChartSpec(kind="bubble", x="label", color="series", size="series", aggregation="count")
    before, spec_before = deepcopy(rows), spec.model_dump()
    mapped = channels(rows, spec)
    assert [row["_color"] for row in mapped] == ["90", "80", "70"]
    assert [row["_size"] for row in mapped] == [90, 80, 70]
    assert rows == before and spec.model_dump() == spec_before
    assert [row["_y"] for row in mapped] == [0, None, None]


@pytest.mark.parametrize("mappings", [{"x": "count"}, {"x": "label", "color": "count"}])
def test_generated_count_cannot_overwrite_a_retained_group_key(mappings):
    rows = [{"label": "A", "count": 90}, {"label": "A", "count": 90}, {"label": "B", "count": 80}]
    before = deepcopy(rows)
    with pytest.raises(ValueError, match="measure must differ from grouping fields"):
        normalize(rows, ChartSpec(aggregation="count", **mappings))
    assert rows == before


def test_heatmap_count_uses_heat_not_the_implicit_y_coordinate():
    rows = [{"east": "E", "north": 0}, {"east": "E", "north": 0}, {"east": "W", "north": 1}]
    spec = ChartSpec(kind="heatmap", x="east", aggregation="count")
    result = normalize(rows, spec)
    assert asdict(result) == {"records": [{"east": "E", "north": 0, "count": 2},
                                         {"east": "W", "north": 1, "count": 1}],
                              "input_count": 3, "warnings": [], "strategy": "count"}
    before, spec_before = deepcopy(asdict(result)), spec.model_dump()
    mapped = channels(result.records, spec)
    assert [row["_x"] for row in mapped] == ["E", "W"]
    assert [row["_y"] for row in mapped] == [0, 1]
    assert [row["_heat"] for row in mapped] == [2, 1]
    assert asdict(result) == before and spec.model_dump() == spec_before


def test_none_with_user_count_field_preserves_zero_null_missing_and_inputs():
    rows = [{"label": "zero", "measure": 0, "count": 90},
            {"label": "null", "measure": None, "count": 80},
            {"label": "missing", "count": 70}]
    raw_before = deepcopy(rows)
    spec = ChartSpec(kind="line", x="label", aggregation="none")
    spec_before = spec.model_dump()
    result = normalize(rows, spec)
    assert asdict(result) == {"records": raw_before, "input_count": 3, "warnings": [], "strategy": "none"}
    before = deepcopy(asdict(result))
    mapped = channels(result.records, spec)
    assert [row["_y"] for row in mapped] == [0, None, None]
    assert [row["count"] for row in result.records] == [90, 80, 70]
    assert rows == raw_before and asdict(result) == before and spec.model_dump() == spec_before
