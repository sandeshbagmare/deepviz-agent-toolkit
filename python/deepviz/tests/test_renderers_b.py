"""ECharts/G2 native payloads preserve normalized values and color meaning."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest
from deepviz.engines import native_spec
from deepviz.models import ChartSpec
from deepviz.render import render


@pytest.mark.parametrize("engine", ["echarts", "antv"])
def test_public_browser_artifact_keeps_normalized_records_and_runtime_warning(engine, tmp_path):
    rows = [{"category": "North", "value": 7}, {"category": "South", "value": 19}]
    original = copy.deepcopy(rows)
    artifact = render(rows, ChartSpec(x="category", y="value"), engine, tmp_path)
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith("manifest.json")).read_text())
    assert (artifact.engine, artifact.input_count, artifact.output_count) == (engine, 2, 2)
    assert manifest["charts"][0]["records"] == original == rows
    assert artifact.mime_type == "text/html"
    assert any("exact-version pinned browser library" in note for note in artifact.warnings)


@pytest.mark.parametrize("kind", ["line", "area"])
@pytest.mark.parametrize("x,axis", [([0, 1, 10], "value"), (["2026-01-01", "2026-01-02", "2026-01-11"], "time")])
def test_echarts_continuous_x_keeps_unequal_spacing(kind, x, axis):
    rows = [{"x": value, "y": y} for value, y in zip(x, [2, 3, 5], strict=True)]
    native, _, _ = native_spec("echarts", rows, ChartSpec(kind=kind, x="x", y="y"))
    assert native["xAxis"]["type"] == axis
    assert native["series"][0]["data"] == [[x[0], 2], [x[1], 3], [x[2], 5]]


@pytest.mark.parametrize("kind", ["pie", "sunburst", "treemap", "gauge"])
def test_antv_categorical_colors_are_not_overridden_by_constant_paint(kind):
    rows = [{"category": "North", "value": 7}, {"category": "South", "value": 19}]
    native, _, _ = native_spec("antv", rows, ChartSpec(kind=kind, x="category", y="value"))
    assert native["encode"]["color"] == "_x"
    assert not {"fill", "stroke"}.intersection(native.get("style", {}))
    assert native.get("legend") is not False


@pytest.mark.parametrize("values", [
    [-7.0, -2.0], [-7.0, 2.0], [0.0, 0.0], [-8e-310, -2e-310], [5e-324, 2e-323],
    [-1.7976931348623157e308, 1.7976931348623157e308],
])
def test_antv_heatmap_keeps_finite_measure_and_truthful_color_domain(values):
    rows = [{"x": "West", "y": str(i), "heat": value} for i, value in enumerate(values)]
    native, _, _ = native_spec("antv", rows, ChartSpec(kind="heatmap", x="x", y="y", color="heat"))
    assert [row["_heat"] for row in native["data"]] == values
    assert native["encode"]["color"] == "_heat"
    assert not {"fill", "stroke"}.intersection(native.get("style", {}))
    domain = native["scale"]["color"]["domain"]
    assert all(math.isfinite(value) for value in domain)
    assert domain[0] <= min(values) <= max(values) <= domain[-1]
    assert domain[0] < domain[-1]
    assert native.get("legend") is not False
    json.dumps(native, allow_nan=False)


def test_antv_line_draws_points_without_filling_across_missing_values():
    rows = [{"x": "A", "y": 2}, {"x": "B", "y": None}, {"x": "C", "y": 5}]
    native, warnings, _ = native_spec("antv", rows, ChartSpec(kind="line", x="x", y="y"))
    line, points = native["children"]
    assert [row["_y"] for row in line["data"]] == [2, None, 5]
    assert [row["_y"] for row in points["data"]] == [2, 5]
    assert "fill" not in line["style"]
    assert any("gaps" in note for note in warnings)


def test_echarts_extreme_heatmap_keeps_raw_values_and_uses_a_finite_color_coordinate():
    values = [-1.7976931348623157e308, 0.0, 1.7976931348623157e308]
    rows = [{"x": label, "y": "A", "heat": value} for label, value in zip(["W", "C", "E"], values, strict=True)]
    native, _, _ = native_spec("echarts", rows, ChartSpec(kind="heatmap", x="x", y="y", color="heat"))
    assert [row[2] for row in native["series"][0]["data"]] == values
    assert [row[3] for row in native["series"][0]["data"]] == [0.0, 0.5, 1.0]
    assert native["series"][0]["encode"]["tooltip"] == [2]
    assert (native["visualMap"]["min"], native["visualMap"]["max"], native["visualMap"]["dimension"]) == (0, 1, 3)
