"""Semantic renderer contracts: mapped values, actual engines, and safe artifacts."""
from __future__ import annotations

import importlib
import importlib.util
import json
import os
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import get_args

import numpy as np
import pytest
from deepviz.models import ChartKind, ChartSpec

ENGINES = ["matplotlib", "plotly", "vega", "echarts", "antv"]
KINDS = [kind for kind in get_args(ChartKind) if kind != "dashboard"]
ROWS = [
    {"label": "Alpha", "amount": 12, "group": "north", "radius": 4},
    {"label": "Beta", "amount": 31, "group": "south", "radius": 9},
    {"label": "Gamma", "amount": 7, "group": "north", "radius": 16},
]


def module(name):
    assert importlib.util.find_spec(f"deepviz.{name}"), f"Missing renderer module deepviz.{name}"
    return importlib.import_module(f"deepviz.{name}")


def render(*args, **kwargs):
    return module("render").render(*args, **kwargs)


@pytest.mark.parametrize("engine", ENGINES)
def test_every_engine_preserves_mapped_values_and_own_identity(engine, tmp_path):
    artifact = render(ROWS, {"kind": "bar", "x": "label", "y": "amount"}, engine, tmp_path)
    assert artifact.engine == engine
    assert (artifact.input_count, artifact.output_count) == (3, 3)
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith("manifest.json")).read_text(encoding="utf-8"))
    assert [r["amount"] for r in manifest["charts"][0]["records"]] == [12, 31, 7]
    assert manifest["charts"][0]["engine"] == engine
    assert all(Path(p).parent == Path(artifact.paths[0]).parent for p in artifact.paths)
    if engine == "matplotlib":
        assert {Path(p).suffix for p in artifact.paths} >= {".png", ".svg"}
        svg = next(Path(p) for p in artifact.paths if p.endswith(".svg")).read_text(encoding="utf-8")
        assert "Alpha" in svg and "Beta" in svg
    elif engine == "vega":
        svg = next(Path(p) for p in artifact.paths if p.endswith(".svg")).read_text(encoding="utf-8")
        assert "Alpha" in svg and "31" in svg
        assert ET.fromstring(svg).get("width") == "900"
        assert ET.fromstring(svg).get("height") == "520"
    else:
        html = next(Path(p) for p in artifact.paths if p.endswith(".html")).read_text(encoding="utf-8")
        assert "deepviz-data" in html and "Alpha" in html and "31" in html


def test_matplotlib_bars_have_mapped_heights_and_dark_dimensions():
    fig, warnings = module("engines").matplotlib_figure(
        [(ROWS, ChartSpec(x="label", y="amount", theme="dark", width=700, height=400))]
    )
    try:
        assert [patch.get_height() for patch in fig.axes[0].patches] == [12, 31, 7]
        assert list(fig.get_size_inches()) == pytest.approx([7, 4])
        assert fig.get_facecolor()[0] < 0.2
        assert not warnings
    finally:
        fig.clear()


def test_dashboard_respects_explicit_child_theme():
    light = ChartSpec(x="label", y="amount", theme="light")
    dark = ChartSpec(x="label", y="amount", theme="dark")
    parent = ChartSpec(kind="dashboard", charts=[light, dark], theme="dark")
    fig, _ = module("engines").matplotlib_figure([(ROWS, light), (ROWS, dark)], parent)
    try:
        assert fig.axes[0].get_facecolor()[0] > .9
        assert fig.axes[1].get_facecolor()[0] < .2
    finally:
        fig.clear()


def test_dark_heatmap_colorbar_ticks_have_readable_contrast():
    fig, _ = module("engines").matplotlib_figure([
        (ROWS, ChartSpec(kind="heatmap", x="label", y="amount", theme="dark"))
    ])
    try:
        fig.canvas.draw()
        from matplotlib.colors import to_rgb

        for label in fig.axes[-1].get_yticklabels():
            assert min(to_rgb(label.get_color())) > .7
    finally:
        fig.clear()


def test_grouped_bars_have_disjoint_rectangles_for_each_category():
    records = [{"q": "Q1", "n": 10, "region": "East"}, {"q": "Q2", "n": 20, "region": "East"},
               {"q": "Q1", "n": 25, "region": "West"}, {"q": "Q2", "n": 5, "region": "West"}]
    fig, _ = module("engines").matplotlib_figure([(records, ChartSpec(x="q", y="n", color="region"))])
    try:
        east, west = fig.axes[0].patches[0], fig.axes[0].patches[2]
        assert east.get_x() + east.get_width() <= west.get_x()
        assert [p.get_height() for p in fig.axes[0].patches] == [10, 20, 25, 5]
    finally:
        fig.clear()


def test_long_titles_and_category_labels_fit_without_horizontal_overlap():
    records = [{"name": f"North America Enterprise Acquisition segment number {i}", "value": i + 1}
               for i in range(4)]
    fig, _ = module("engines").matplotlib_figure([
        (records, ChartSpec(x="name", y="value", title=("Very long chart title " * 20)[:407]))
    ])
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        title = fig.axes[0].title.get_window_extent(renderer)
        assert title.x0 >= 0 and title.x1 <= 900
        boxes = [label.get_window_extent(renderer) for label in fig.axes[0].get_xticklabels()]
        assert all(a.x1 < b.x0 for a, b in zip(boxes, boxes[1:], strict=False))
    finally:
        fig.clear()


def test_seven_series_use_redundant_marker_and_line_styles():
    records = [{"x": i, "y": i + j, "series": f"Series {j}"} for j in range(7) for i in range(2)]
    fig, _ = module("engines").matplotlib_figure([
        (records, ChartSpec(kind="line", x="x", y="y", color="series"))
    ])
    try:
        first, seventh = fig.axes[0].lines[0], fig.axes[0].lines[6]
        assert (first.get_marker(), first.get_linestyle()) != (seventh.get_marker(), seventh.get_linestyle())
        assert first.get_marker() not in {None, "None", "", " "}
        assert len(fig.axes[0].get_legend().get_texts()) == 7
    finally:
        fig.clear()


@pytest.mark.parametrize("engine", ["plotly", "vega", "echarts", "antv"])
def test_browser_seven_series_have_noncolor_distinctions(engine):
    records = [{"x": i, "y": i + j, "series": f"Series {j}"} for j in range(7) for i in range(2)]
    native, _, _ = module("engines").native_spec(
        engine, records, ChartSpec(kind="line", x="x", y="y", color="series")
    )
    if engine == "plotly":
        assert native["data"][0]["line"]["dash"] != native["data"][6]["line"]["dash"]
        assert native["data"][0]["mode"] == "lines+markers"
    elif engine == "echarts":
        assert native["series"][0]["symbol"] != native["series"][6]["symbol"]
        assert native["legend"]["show"] is True
    elif engine == "vega":
        styles = native["encoding"]["strokeDash"]["scale"]["range"]
        assert styles[0] != styles[6]
        assert native["mark"]["point"] is True
    else:
        lines = [child for child in native["children"] if child["type"] == "line"]
        assert lines[0]["style"]["lineDash"] != lines[6]["style"]["lineDash"]
        assert any(child["type"] == "point" for child in native["children"])


def _contrast(a, b):
    from matplotlib.colors import to_rgb

    def luminance(color):
        channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in to_rgb(color)]
        return sum(v * w for v, w in zip(channels, [.2126, .7152, .0722], strict=True))

    l1, l2 = sorted([luminance(a), luminance(b)])
    return (l2 + .05) / (l1 + .05)


def test_palette_marks_and_treemap_labels_have_accessible_contrast():
    adapter = module("engines")
    assert all(_contrast(color, "white") >= 3 for color in adapter.PALETTE)
    records = [{"name": str(i), "value": i + 1} for i in range(6)]
    fig, _ = adapter.matplotlib_figure([(records, ChartSpec(kind="treemap", x="name", y="value"))])
    try:
        assert all(_contrast(text.get_color(), patch.get_facecolor()) >= 4.5
                   for text, patch in zip(fig.axes[0].texts, fig.axes[0].patches, strict=True))
    finally:
        fig.clear()


def test_browser_data_alternatives_include_real_values_and_reduction_context():
    adapter = module("engines")
    spec = ChartSpec(x="label", y="amount", title="Revenue <safe>")
    payload = adapter.native_spec("echarts", ROWS, spec)[0]
    context = [{"records": ROWS, "input_count": 100, "output_count": 3, "strategy": "sample",
                "warnings": ["Reduced <100> rows"]}]
    html = adapter.browser_html("echarts", [payload], [spec], spec, metadata=context)

    class Semantics(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tags, self.text, self.descriptions = [], [], []

        def handle_starttag(self, tag, attrs):
            self.tags.append(tag)
            attrs = dict(attrs)
            if "aria-describedby" in attrs:
                self.descriptions.append(attrs["aria-describedby"])

        def handle_data(self, data):
            self.text.append(data)

    parser = Semantics()
    parser.feed(html)
    assert all(tag in parser.tags for tag in ["details", "summary", "table", "caption", "thead", "th", "tbody", "td"])
    text = " ".join(parser.text)
    assert all(value in text for value in ["Alpha", "31", "100", "3", "sample", "Reduced <100> rows"])
    assert parser.descriptions == ["chart-summary-0"]
    assert "Revenue &lt;safe&gt;" in html


def test_antv_grouped_bar_dodges_series_and_uses_mapped_axis_titles():
    native, _, _ = module("engines").native_spec(
        "antv", ROWS, ChartSpec(x="label", y="amount", color="group")
    )
    assert {"type": "dodgeX"} in native["transform"]
    assert native["axis"]["x"]["title"] == "label"
    assert native["axis"]["y"]["title"] == "amount"


def test_vega_dashboard_dark_theme_survives_composition(tmp_path):
    artifact = render(ROWS, {"kind": "dashboard", "theme": "dark", "charts": [
        {"kind": "bar", "x": "label", "y": "amount"},
    ]}, "vega", tmp_path)
    svg = next(Path(p) for p in artifact.paths if p.endswith(".svg")).read_text(encoding="utf-8")
    root = ET.fromstring(svg)
    assert any(element.get("fill") == "#171b26" for element in root.iter())


@pytest.mark.parametrize("engine", ENGINES)
def test_every_engine_exposes_accessible_real_data_companion(engine, tmp_path):
    artifact = render(ROWS, {"x": "label", "y": "amount", "aggregation": "none"}, engine, tmp_path)
    html = next(Path(p) for p in artifact.paths if p.endswith(".html")).read_text(encoding="utf-8")
    assert "<details>" in html and "<caption>" in html and '<th scope="col">amount</th>' in html
    assert "<td>31</td>" in html and "Reduction strategy: none" in html
    if engine in {"matplotlib", "vega"}:
        assert 'src="chart.svg"' in html
        assert 'src="C:' not in html
    if engine in {"echarts", "antv"}:
        assert "HTML requires network access" in html


def test_literal_math_like_labels_never_invoke_matplotlib_math_parser():
    fig, _ = module("engines").matplotlib_figure([
        (ROWS, ChartSpec(x="label", y="amount", title=r"Untrusted $\\notacommand$"))
    ])
    try:
        fig.canvas.draw()
    finally:
        fig.clear()


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("kind", KINDS)
def test_entire_standard_set_has_real_render_path(engine, kind, tmp_path):
    rows = ROWS
    spec = {"kind": kind, "x": "label", "y": "amount", "width": 480, "height": 320}
    if kind in {"scatter", "bubble", "geo"}:
        rows = [{"label": -73, "amount": 40, "radius": 4}, {"label": 2, "amount": 49, "radius": 9}]
        spec["size"] = "radius"
    artifact = render(rows, spec, engine, tmp_path)
    assert artifact.engine == engine
    assert artifact.output_count == len(rows)
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith("manifest.json")).read_text(encoding="utf-8"))
    chart = manifest["charts"][0]
    assert chart["requested_kind"] == kind
    assert chart["rendered_kind"]
    if chart["rendered_kind"] != kind:
        assert any("fallback" in message.lower() for message in artifact.warnings)
    assert all(Path(p).stat().st_size > 50 for p in artifact.paths)


def test_invalid_engine_is_rejected_without_consuming_input_or_creating_files(tmp_path):
    def stream():
        raise AssertionError("invalid engine consumed data")
        yield {}

    with pytest.raises(ValueError, match="engine"):
        render(stream(), {"kind": "bar"}, "unknown", tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("engine", ["plotly", "echarts", "antv"])
def test_untrusted_strings_cannot_end_json_script_or_html_title(engine, tmp_path):
    attack = '</script><img src=x onerror="alert(1)">&\u2028\u2029'
    artifact = render([{"label": attack, "amount": 12}], {
        "x": "label", "y": "amount", "title": attack, "description": attack,
    }, engine, tmp_path)
    html = next(Path(p) for p in artifact.paths if p.endswith(".html")).read_text(encoding="utf-8")
    assert "<img src=x" not in html
    start = html.index('<script id="deepviz-data" type="application/json">')
    payload = html[start:].split(">", 1)[1].split("</script>", 1)[0]
    assert "<" not in payload and ">" not in payload and "&" not in payload
    assert "\u2028" not in payload and "\u2029" not in payload
    def strings(value):
        if isinstance(value, dict):
            for child in value.values():
                yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)
        elif isinstance(value, str):
            yield value

    assert attack in strings(json.loads(payload))


@pytest.mark.parametrize("engine", ENGINES)
def test_dashboard_consumes_generator_once_and_preserves_child_mappings(engine, tmp_path):
    seen = []

    def stream():
        for i in range(23):
            seen.append(i)
            yield {"label": f"row-{i}", "amount": i + 1, "other": 100 - i}

    spec = {"kind": "dashboard", "width": 800, "height": 600, "charts": [
        {"kind": "bar", "x": "label", "y": "amount", "max_points": 10, "aggregation": "sample"},
        {"kind": "line", "x": "label", "y": "other", "max_points": 10, "aggregation": "sample"},
    ]}
    artifact = render(stream(), spec, engine, tmp_path)
    assert seen == list(range(23))
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith("manifest.json")).read_text(encoding="utf-8"))
    assert len(manifest["charts"]) == 2
    assert manifest["charts"][0]["spec"]["y"] == "amount"
    assert manifest["charts"][1]["spec"]["y"] == "other"
    assert all(len(c["records"]) <= 10 for c in manifest["charts"])
    assert artifact.input_count == 23


def test_dashboard_inherits_common_mapping_and_theme_but_preserves_child_override(tmp_path):
    artifact = render(ROWS, {"kind": "dashboard", "theme": "dark", "x": "label", "y": "amount", "charts": [
        {"kind": "bar"}, {"kind": "line", "y": "radius", "theme": "light"},
    ]}, "vega", tmp_path)
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith("manifest.json")).read_text(encoding="utf-8"))
    first, second = (c["spec"] for c in manifest["charts"])
    assert (first["x"], first["y"], first["theme"]) == ("label", "amount", "dark")
    assert (second["x"], second["y"], second["theme"]) == ("label", "radius", "light")


def test_two_renders_never_replace_existing_artifacts(tmp_path):
    a = render(ROWS, {"x": "label", "y": "amount"}, "vega", tmp_path)
    before = {p: Path(p).read_bytes() for p in a.paths}
    b = render(ROWS, {"x": "label", "y": "amount", "title": "Second"}, "vega", tmp_path)
    assert set(a.paths).isdisjoint(b.paths)
    assert {p: Path(p).read_bytes() for p in a.paths} == before


def test_native_browser_specs_encode_values_colors_and_bubble_size():
    engines = module("engines")
    spec = ChartSpec(kind="bubble", x="amount", y="radius", color="group", size="radius")
    for engine in ["plotly", "vega", "echarts", "antv"]:
        native, warnings, kind = engines.native_spec(engine, ROWS, spec)
        assert kind == "bubble"
        serialized = json.dumps(native)
        assert "31" in serialized and "north" in serialized and "south" in serialized
        assert not warnings


@pytest.mark.parametrize("engine", ["plotly", "vega", "echarts", "antv"])
def test_composition_negative_values_have_consistent_nonnegative_geometry(engine):
    records = [{"label": "A", "amount": -8}, {"label": "B", "amount": 21}]
    native, warnings, _ = module("engines").native_spec(engine, records, ChartSpec(kind="pie", x="label", y="amount"))
    if engine == "plotly":
        assert native["data"][0]["values"] == [0, 21]
    elif engine == "vega":
        assert [r["_y"] for r in native["data"]["values"]] == [0, 21]
    elif engine == "echarts":
        assert [r["value"] for r in native["series"][0]["data"]] == [0, 21]
    else:
        assert [r["_y"] for r in native["data"]] == [0, 21]
    assert any("negative" in warning.lower() for warning in warnings)


@pytest.mark.parametrize("kind", KINDS)
def test_vega_native_spec_compiles_all_kinds(kind):
    import vl_convert

    spec = ChartSpec(kind=kind, x="label", y="amount", width=480, height=320)
    payload, warnings, actual = module("engines").native_spec("vega", ROWS, spec)
    svg = vl_convert.vegalite_to_svg(payload)
    assert "<svg" in svg and len(svg) > 100
    if actual != kind:
        assert any("fallback" in message for message in warnings)


@pytest.mark.parametrize("kind", KINDS)
def test_matplotlib_draws_entire_standard_set(kind):
    adapter = module("engines")
    fig, _ = adapter.matplotlib_figure([(ROWS, ChartSpec(kind=kind, x="label", y="amount"))])
    try:
        assert len(fig.axes) >= 1
        fig.canvas.draw()
        pixels = np.asarray(fig.canvas.buffer_rgba())
        assert ((pixels[:, :, :3] < 200).any(axis=2)).sum() > 100
    finally:
        fig.clear()


def test_heatmap_keeps_both_category_coordinates_and_numeric_color():
    records = [{"day": "Mon", "team": "A", "sales": 8}, {"day": "Tue", "team": "B", "sales": 21}]
    spec = ChartSpec(kind="heatmap", x="day", y="team", color="sales")
    native, _, _ = module("engines").native_spec("echarts", records, spec)
    assert native["xAxis"]["data"] == ["Mon", "Tue"]
    assert native["yAxis"]["data"] == ["A", "B"]
    assert native["series"][0]["data"] == [[0, 0, 8], [1, 1, 21]]


def test_echarts_never_discards_repeated_category_values():
    records = [{"label": "A", "amount": 8}, {"label": "A", "amount": 21}]
    native, _, _ = module("engines").native_spec("echarts", records, ChartSpec(x="label", y="amount"))
    assert native["series"][0]["data"] == [["A", 8], ["A", 21]]


def test_sparse_heatmap_does_not_expand_cartesian_product():
    records = [{"day": f"day-{i}", "team": f"team-{i}", "sales": i} for i in range(1200)]
    native, _, _ = module("engines").native_spec(
        "plotly", records, ChartSpec(kind="heatmap", x="day", y="team", color="sales")
    )
    assert len(json.dumps(native)) < 150_000
    assert native["data"][0]["marker"]["color"][-1] == 1199


@pytest.mark.integration
@pytest.mark.parametrize("engine", ["plotly", "echarts", "antv"])
def test_browser_executes_all_native_kinds(engine, tmp_path):
    if not os.getenv("DEEPVIZ_BROWSER_TESTS"):
        pytest.skip("Set DEEPVIZ_BROWSER_TESTS=1 for installed Chromium + pinned CDN integration checks")
    from playwright.sync_api import sync_playwright

    adapter = module("engines")
    specs, payloads = [], []
    for kind in KINDS:
        spec = ChartSpec(kind=kind, x="label", y="amount", title=kind, width=480, height=320)
        rows = ROWS
        if kind in {"scatter", "bubble", "geo"}:
            rows = [{"label": -73, "amount": 40, "radius": 4}, {"label": 2, "amount": 49, "radius": 9}]
            spec = spec.model_copy(update={"size": "radius"})
        payloads.append(adapter.native_spec(engine, rows, spec)[0])
        specs.append(spec)
    series_records = [{"x": i, "y": i + j, "series": f"Series {j}"} for j in range(7) for i in range(2)]
    series_spec = ChartSpec(kind="line", x="x", y="y", color="series", width=480, height=320)
    payloads.append(adapter.native_spec(engine, series_records, series_spec)[0])
    specs.append(series_spec)
    html = adapter.browser_html(engine, payloads, specs, ChartSpec(kind="dashboard", charts=specs, columns=3))
    path = tmp_path / "native.html"
    path.write_text(html, encoding="utf-8")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1200})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(path.as_uri())
        page.evaluate("async () => await window.deepvizReady")
        assert not errors
        for i, spec in enumerate(specs):
            kind = spec.kind
            if engine == "antv":
                pixels = page.locator(f"#chart-{i} canvas").evaluate("""canvas => {
                  const data = canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
                  let count=0; for(let j=0;j<data.length;j+=4) if(data[j+3] && data[j]+data[j+1]+data[j+2]<650) count++;
                  return count;
                }""")
                assert pixels > 100, kind
            else:
                assert page.locator(f"#chart-{i} svg path, #chart-{i} svg text").count() > 0, kind
        if engine == "plotly":
            assert page.evaluate("document.getElementById('chart-0').data[0].y") == [12, 31, 7]
        elif engine == "echarts":
            assert page.evaluate("echarts.getInstanceByDom(document.getElementById('chart-0')).getOption().series[0].data") == [
                ["Alpha", 12], ["Beta", 31], ["Gamma", 7]
            ]
        browser.close()
