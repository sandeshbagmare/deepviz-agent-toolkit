"""Regressions for actual mapped values and reusable renderer artifacts."""
from __future__ import annotations

import importlib
import json
import math
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import vl_convert as vlc

from deepviz.engines import matplotlib_figure, native_spec
from deepviz.models import ChartSpec
from deepviz.normalize import normalize
from deepviz.render import render


def _marks(node: Any, kind: str) -> list[dict]:
    if isinstance(node, dict):
        if node.get("marktype") == kind and node.get("role") == "mark":
            return [node]
        return [mark for value in node.values() for mark in _marks(value, kind)]
    if isinstance(node, list):
        return [mark for value in node for mark in _marks(value, kind)]
    return []


@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_heatmap_without_color_displays_reduced_cell_counts(engine):
    rows = [{"day": "Mon", "team": "West"}] * 3 + [{"day": "Tue", "team": "East"}]
    spec = ChartSpec(kind="heatmap", x="day", y="team")
    reduced = normalize(rows, spec)
    assert reduced.records == [{"day": "Mon", "team": "West", "count": 3},
                               {"day": "Tue", "team": "East", "count": 1}]
    if engine == "matplotlib":
        figure, _ = matplotlib_figure([(reduced.records, spec)])
        try:
            assert list(figure.axes[0].collections[0].get_array()) == [3, 1]
        finally:
            figure.clear()
        return
    native, _, _ = native_spec(engine, reduced.records, spec)
    if engine == "plotly":
        assert native["data"][0]["marker"]["color"] == [3, 1]
    elif engine == "vega":
        assert [row["_heat"] for row in native["data"]["values"]] == [3, 1]
    elif engine == "echarts":
        assert native["series"][0]["data"] == [[0, 0, 3], [1, 1, 1]]
    else:
        assert [row["_heat"] for row in native["data"]] == [3, 1]


def test_vega_iso_dates_have_elapsed_time_spacing_in_actual_scene():
    spec = ChartSpec(kind="line", x="day", y="value", aggregation="none")
    native, _, _ = native_spec("vega", [
        {"day": "2026-01-01", "value": 1}, {"day": "2026-01-02", "value": 2},
        {"day": "2026-01-31", "value": 3},
    ], spec)
    line, = _marks(vlc.vegalite_to_scenegraph(native), "line")
    positions = [point["x"] for point in line["items"]]
    assert (positions[2] - positions[1]) / (positions[1] - positions[0]) == pytest.approx(29)


def test_vega_bubble_descriptions_name_the_mapped_size_measure():
    native, _, _ = native_spec("vega", [
        {"distance": 2, "cost": 17, "population": 4},
        {"distance": 10, "cost": 3, "population": 36},
    ], ChartSpec(kind="bubble", x="distance", y="cost", size="population"))
    marks = _marks(vlc.vegalite_to_scenegraph(native), "symbol")
    descriptions = [item["description"] for mark in marks for item in mark["items"]]
    assert any("population: 4" in description for description in descriptions)
    assert any("population: 36" in description for description in descriptions)


def test_vega_grouped_area_keeps_each_series_on_the_same_zero_baseline():
    native, _, _ = native_spec("vega", [
        {"t": 0, "value": 2, "region": "East"}, {"t": 1, "value": 6, "region": "East"},
        {"t": 0, "value": 5, "region": "West"}, {"t": 1, "value": 1, "region": "West"},
    ], ChartSpec(kind="area", x="t", y="value", color="region", aggregation="none"))
    areas = _marks(vlc.vegalite_to_scenegraph(native), "area")
    assert len(areas) == 2
    assert len({point["y2"] for area in areas for point in area["items"]}) == 1


def test_vega_dashboard_keeps_standalone_child_theme_and_schema(tmp_path: Path):
    artifact = render([{"category": "A", "value": 8}], {
        "kind": "dashboard", "x": "category", "y": "value", "charts": [
            {"kind": "bar", "theme": "dark", "title": "Dark standalone"},
            {"kind": "bar", "theme": "light", "title": "Light standalone"},
        ],
    }, "vega", tmp_path)
    manifest = json.loads(next(Path(path) for path in artifact.paths
                               if path.endswith("manifest.json")).read_text(encoding="utf-8"))
    dark, light = manifest["native_specs"]
    assert dark["$schema"].endswith("vega-lite/v5.json")
    assert dark["background"] == "#171b26"
    assert light["background"] == "#ffffff"
    assert dark["config"]["axis"]["labelColor"] == "#edf1f7"
    assert 'fill="#171b26"' in vlc.vegalite_to_svg(dark)


@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_missing_line_measure_is_a_gap_not_an_invented_zero(engine):
    rows = [{"t": 0, "value": 7}, {"t": 1, "value": None}, {"t": 2, "value": 9}]
    spec = ChartSpec(kind="line", x="t", y="value", aggregation="none")
    if engine == "matplotlib":
        figure, warnings = matplotlib_figure([(rows, spec)])
        try:
            values = figure.axes[0].lines[0].get_ydata()
            assert values[0] == 7 and values[2] == 9 and math.isnan(values[1])
        finally:
            figure.clear()
    else:
        native, warnings, _ = native_spec(engine, rows, spec)
        if engine == "plotly":
            assert native["data"][0]["y"] == [7, None, 9]
        elif engine == "echarts":
            assert native["series"][0]["data"] == [["0", 7], ["1", None], ["2", 9]]
        else:
            mapped = native["data"]["values"] if engine == "vega" else native["data"]
            assert [row["_y"] for row in mapped] == [7, None, 9]
    assert any("gap" in warning.lower() for warning in warnings)


@pytest.mark.parametrize("kind", ["box", "violin", "pie", "scatter", "gauge"])
@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_missing_numeric_measure_is_omitted_with_disclosure(engine, kind):
    rows = [{"x": 0, "value": 7}, {"x": 1, "value": None}, {"x": 2, "value": 9}]
    spec = ChartSpec(kind=kind, x="x", y="value", aggregation="none")
    if engine == "matplotlib":
        figure, warnings = matplotlib_figure([(rows, spec)])
        try:
            figure.canvas.draw()
        finally:
            figure.clear()
    else:
        native, warnings, _ = native_spec(engine, rows, spec)
        json.dumps(native, allow_nan=False)
        if engine == "plotly" and kind in {"box", "violin"}:
            assert native["data"][0]["y"] == [7, 9]
        if engine == "vega":
            vlc.vegalite_to_svg(native)
    assert any("omitt" in warning.lower() for warning in warnings)


@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_scalar_histogram_bins_observations_not_synthetic_row_positions(engine):
    spec = ChartSpec(kind="histogram")
    reduced = normalize([10, 10, 10, 20], spec)
    if engine == "matplotlib":
        figure, _ = matplotlib_figure([(reduced.records, spec)])
        try:
            bars = figure.axes[0].patches
            assert [bar.get_height() for bar in bars] == [3, 1]
            assert [bar.get_x() + bar.get_width() / 2 for bar in bars] == [12.5, 17.5]
        finally:
            figure.clear()
        return
    native, _, _ = native_spec(engine, reduced.records, spec)
    if engine == "plotly":
        assert native["data"][0]["x"] == [12.5, 17.5]
        assert native["data"][0]["y"] == [3, 1]
    elif engine == "echarts":
        assert native["series"][0]["data"] == [3, 1]
    else:
        mapped = native["data"]["values"] if engine == "vega" else native["data"]
        assert [row["_x"] for row in mapped] == [12.5, 17.5]
        assert [row["_y"] for row in mapped] == [3, 1]


def test_decimal_dashboard_list_and_one_shot_replay_have_identical_measurements(tmp_path: Path):
    rows = [{"category": "a", "value": Decimal("2.5")},
            {"category": "a", "value": Decimal("3.5")}]
    spec = {"kind": "dashboard", "charts": [{"x": "category", "y": "value", "aggregation": "sum"}]}
    direct = render(rows, spec, "echarts", tmp_path)
    replayed = render(iter(rows), spec, "echarts", tmp_path)
    manifests = [json.loads(next(Path(path) for path in artifact.paths
                                if path.endswith("manifest.json")).read_text(encoding="utf-8"))
                 for artifact in (direct, replayed)]
    assert [manifest["charts"][0]["records"] for manifest in manifests] == [
        [{"category": "a", "value": 6.0}], [{"category": "a", "value": 6.0}],
    ]


def test_dashboard_replay_rejects_unsupported_values_instead_of_stringifying(tmp_path: Path):
    with pytest.raises(TypeError, match="Unsupported"):
        render(iter([{"value": object()}]), {"kind": "dashboard", "charts": [{"kind": "table"}]},
               "echarts", tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("rows", [[{"value": "x" * (1024 * 1024 + 1)}], [{1: "invalid key"}]])
def test_dashboard_replay_rejects_oversized_or_invalid_records_before_rendering(tmp_path: Path, rows):
    with pytest.raises(ValueError, match="(byte|field names)"):
        render(iter(rows), {"kind": "dashboard", "charts": [{"kind": "table"}]}, "echarts", tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_dashboard_replay_stops_at_its_total_byte_budget(tmp_path: Path, monkeypatch):
    renderer = importlib.import_module("deepviz.render")
    monkeypatch.setattr(renderer, "_MAX_REPLAY_BYTES", 100, raising=False)
    consumed = []

    def source():
        for index in range(1000):
            consumed.append(index)
            yield {"value": "x" * 50}

    with pytest.raises(ValueError, match="replay.*byte"):
        render(source(), {"kind": "dashboard", "charts": [{"kind": "table"}]}, "echarts", tmp_path)
    assert len(consumed) == 2
    assert list(tmp_path.iterdir()) == []


def test_combined_child_payload_is_rejected_before_creating_render_artifacts(tmp_path: Path, monkeypatch):
    renderer = importlib.import_module("deepviz.render")
    monkeypatch.setattr(renderer, "_MAX_RENDER_BYTES", 500, raising=False)
    rows = [{"category": "a", "value": "x" * 200}]
    with pytest.raises(ValueError, match="(combined|payload).*byte"):
        render(iter(rows), {"kind": "dashboard", "charts": [{"kind": "table"}, {"kind": "table"}]},
               "echarts", tmp_path)
    assert list(tmp_path.iterdir()) == []
