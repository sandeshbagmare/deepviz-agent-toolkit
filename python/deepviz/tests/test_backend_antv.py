"""G2 semantics through public render artifacts; browser execution is tested separately.

Missing renderer/normalizer modules are integration blockers, not optional skips.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from deepviz.models import ChartSpec
from deepviz.render import render


class _HTML(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.scripts = []
        self._script = None
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        if tag == "script":
            self._script = {"attrs": attributes, "text": ""}
            self.scripts.append(self._script)

    def handle_endtag(self, tag):
        if tag == "script":
            self._script = None

    def handle_data(self, data):
        if self._script is not None:
            self._script["text"] += data


def _render(tmp_path, data, **options):
    artifact = render(data, ChartSpec(aggregation="none", **options), engine="antv", output_dir=tmp_path)
    paths = [Path(path) for path in artifact.paths]
    html = next(path for path in paths if path.suffix == ".html").read_text(encoding="utf-8")
    manifest = json.loads(next(path for path in paths if path.name == "manifest.json").read_text(encoding="utf-8"))
    return artifact, manifest, html


def _values(payload, channel):
    # Resolve the emitted field encoding, not the adapter's private channel names.
    field = payload["encode"][channel]
    if isinstance(field, dict):
        assert field["type"] == "field"
        field = field["value"]
    assert isinstance(field, str)
    return [row[field] for row in payload["data"]]


def _embedded_payloads(document):
    scripts = [script for script in document.scripts if script["attrs"].get("type") == "application/json"]
    assert len(scripts) == 1, "Browser chart options must be available as inert JSON"
    return json.loads(scripts[0]["text"])


def _assert_connected_series(payload, kind, expected):
    marks = [mark for mark in payload.get("children", []) if mark.get("type") == kind]
    if payload.get("type") == "view":
        assert marks, "A layered view must contain the requested connected marks"
    else:
        assert payload["type"] == kind
        marks = [payload]
    grouped = {}
    for mark in marks:
        assert not {"sortX", "sortY", "stackY"}.intersection(
            transform["type"] for transform in mark.get("transform", [])
        )
        for x, y, color in zip(_values(mark, "x"), _values(mark, "y"), _values(mark, "color"), strict=True):
            grouped.setdefault(color, []).append((x, y))
    assert grouped == expected
    assert not {"sortX", "sortY", "stackY"}.intersection(
        transform["type"] for transform in payload.get("transform", [])
    )


def test_scatter_encodes_explicit_fields_not_first_numeric_columns(tmp_path):
    rows = [
        {"decoy": 999, "longitude": 12.5, "latitude": -3, "segment": "east"},
        {"decoy": 888, "longitude": -8, "latitude": 7.25, "segment": "west"},
    ]
    _, manifest, _ = _render(tmp_path, rows, kind="scatter", x="longitude", y="latitude", color="segment")
    payload = manifest["native_specs"][0]
    assert payload["type"] == "point"
    assert _values(payload, "x") == [12.5, -8]
    assert _values(payload, "y") == [-3, 7.25]
    assert _values(payload, "color") == ["east", "west"]


def test_bubble_size_is_a_separate_quantitative_channel(tmp_path):
    rows = [{"x": 1, "y": 90, "volume": 4}, {"x": 2, "y": 10, "volume": 25}]
    _, manifest, _ = _render(tmp_path, rows, kind="bubble", x="x", y="y", size="volume")
    payload = manifest["native_specs"][0]
    assert payload["type"] == "point"
    assert _values(payload, "x") == [1, 2]
    assert _values(payload, "y") == [90, 10]
    assert _values(payload, "size") == [4, 25]
    assert all(type(value) in (int, float) for value in _values(payload, "size"))


def test_bar_uses_interval_without_accidental_transposition(tmp_path):
    rows = [{"category": "B", "amount": 7}, {"category": "A", "amount": -2}]
    _, manifest, _ = _render(tmp_path, rows, kind="bar", x="category", y="amount")
    payload = manifest["native_specs"][0]
    assert payload["type"] == "interval"
    assert _values(payload, "x") == ["B", "A"]
    assert _values(payload, "y") == [7, -2]
    coordinate = payload.get("coordinate", {})
    assert coordinate.get("type", "cartesian") == "cartesian"
    assert "transpose" not in [transform["type"] for transform in coordinate.get("transform", [])]


def test_pie_stacks_measure_in_theta_and_colors_by_slice(tmp_path):
    rows = [{"slice": "Small", "value": 2}, {"slice": "Large", "value": 6}]
    _, manifest, _ = _render(tmp_path, rows, kind="pie", x="slice", y="value")
    payload = manifest["native_specs"][0]
    assert payload["type"] == "interval"
    assert payload["coordinate"]["type"] == "theta"
    assert "stackY" in [transform["type"] for transform in payload.get("transform", [])]
    assert "x" not in payload["encode"]
    assert _values(payload, "y") == [2, 6]
    assert _values(payload, "color") == ["Small", "Large"]


@pytest.mark.parametrize("kind", ["line", "area"])
def test_connected_marks_preserve_source_order_within_each_series(tmp_path, kind):
    rows = [
        {"phase": "third", "amount": 30, "series": "B"},
        {"phase": "third", "amount": 3, "series": "A"},
        {"phase": "first", "amount": 10, "series": "B"},
        {"phase": "first", "amount": 1, "series": "A"},
        {"phase": "second", "amount": 20, "series": "B"},
        {"phase": "second", "amount": 2, "series": "A"},
    ]
    _, manifest, _ = _render(tmp_path, rows, kind=kind, x="phase", y="amount", color="series")
    payload = manifest["native_specs"][0]
    # Accessible lines use a view containing per-series line and marker layers.
    # Check every connected layer's exact ordered coordinates, not its wrapper.
    _assert_connected_series(payload, kind, {
        "B": [("third", 30), ("first", 10), ("second", 20)],
        "A": [("third", 3), ("first", 1), ("second", 2)],
    })


def test_heatmap_color_is_numeric_measure_not_stringified_category(tmp_path):
    rows = [
        {"day": "Mon", "shift": "AM", "temperature": -5.5},
        {"day": "Mon", "shift": "PM", "temperature": 12.25},
        {"day": "Tue", "shift": "AM", "temperature": 0},
    ]
    _, manifest, _ = _render(tmp_path, rows, kind="heatmap", x="day", y="shift", color="temperature")
    payload = manifest["native_specs"][0]
    assert payload["type"] == "cell"
    assert _values(payload, "x") == ["Mon", "Mon", "Tue"]
    assert _values(payload, "y") == ["AM", "PM", "AM"]
    assert _values(payload, "color") == [-5.5, 12.25, 0]
    assert all(type(value) in (int, float) for value in _values(payload, "color"))
    assert payload.get("scale", {}).get("color", {}).get("type") not in {"ordinal", "band", "point"}
    assert "fill" not in payload.get("style", {}), "A fixed fill overrides G2's quantitative color channel"


def test_dark_theme_reaches_native_options_and_html_background(tmp_path):
    _, manifest, html = _render(tmp_path, [{"x": "A", "y": 1}], x="x", y="y", theme="dark")
    theme = manifest["native_specs"][0]["theme"]
    assert theme == "dark" or isinstance(theme, dict) and theme.get("type") == "dark"
    body_style = re.search(r"body\s*\{([^}]+)\}", html)
    assert body_style is not None
    background = re.search(r"background(?:-color)?\s*:\s*#([0-9a-fA-F]{6})\b", body_style[1])
    foreground = re.search(r"(?:^|;)\s*color\s*:\s*#([0-9a-fA-F]{6})\b", body_style[1])
    assert background is not None and foreground is not None
    assert all(int(background[1][offset:offset + 2], 16) < 128 for offset in (0, 2, 4))
    assert all(int(foreground[1][offset:offset + 2], 16) > 128 for offset in (0, 2, 4))


def test_dashboard_duplicate_titles_get_unique_containers_and_independent_options(tmp_path):
    children = [
        ChartSpec(kind="bar", title="Same title", x="label", y="income"),
        ChartSpec(kind="line", title="Same title", x="label", y="cost"),
        ChartSpec(kind="pie", title="Same title", x="label", y="income"),
    ]
    rows = [{"label": "A", "income": 9, "cost": 2}, {"label": "B", "income": 5, "cost": 4}]
    _, manifest, html = _render(tmp_path, rows, kind="dashboard", charts=children, columns=2)
    document = _HTML(html)
    ids = [attrs["id"] for _, attrs in document.elements if "id" in attrs]
    containers = [attrs for _, attrs in document.elements if attrs.get("role") == "img"]
    assert len(ids) == len(set(ids)), "Duplicate DOM IDs can render several charts into one container"
    assert len(containers) == 3
    assert len({attrs["id"] for attrs in containers}) == 3
    payloads = _embedded_payloads(document)
    assert payloads == manifest["native_specs"]
    assert [payload["type"] for payload in payloads] == ["interval", "line", "interval"]
    assert [_values(payload, "y") for payload in payloads] == [[9, 5], [2, 4], [9, 5]]


def test_untrusted_titles_labels_field_names_and_table_cells_remain_inert(tmp_path):
    malicious = '</script><svg onload="alert(9)"><!--&\u2028\u2029'
    field = 'name</script><img src=x onerror="alert(8)">'
    rows = [{field: malicious, "value": 4, "label": malicious}]
    children = [
        ChartSpec(x=field, y="value", color="label", title=malicious, description=malicious),
        ChartSpec(kind="table", title=malicious, description=malicious),
    ]
    _, manifest, html = _render(tmp_path, rows, kind="dashboard", charts=children, title=malicious)
    document = _HTML(html)
    assert malicious not in html and field not in html
    # These are valid inert HTML text characters; only script contexts need
    # escaping so a JavaScript line separator cannot affect a script grammar.
    assert all("\u2028" not in script["text"] and "\u2029" not in script["text"] for script in document.scripts)
    assert not {"svg", "img"}.intersection(tag for tag, _ in document.elements)
    assert not any(name.lower().startswith("on") for _, attrs in document.elements for name in attrs)
    payloads = _embedded_payloads(document)
    assert payloads == manifest["native_specs"], "Escaping must not corrupt the data passed to G2"
    assert _values(payloads[0], "x") == [malicious]
    assert _values(payloads[0], "color") == [malicious]
    assert malicious in _values(payloads[1], "text")
    assert field in _values(payloads[1], "text")
    assert any(attrs.get("aria-label") == malicious for _, attrs in document.elements)


def test_native_antv_artifact_bootstraps_g2_and_discloses_network_dependency(tmp_path):
    artifact, manifest, html = _render(tmp_path, [{"x": "A", "y": 3}], x="x", y="y")
    assert artifact.engine == manifest["engine"] == "antv"
    assert artifact.mime_type == "text/html"
    assert artifact.input_count == artifact.output_count == 1
    chart = manifest["charts"][0]
    assert chart["engine"] == "antv"
    assert chart["requested_kind"] == chart["rendered_kind"] == "bar"
    document = _HTML(html)
    sources = [script["attrs"].get("src", "") for script in document.scripts]
    assert any(re.search(r"/@antv/g2@\d+\.\d+\.\d+/", source) for source in sources)
    bootstrap = "\n".join(script["text"] for script in document.scripts if not script["attrs"].get("src"))
    assert "new G2.Chart(" in bootstrap and ".options(" in bootstrap and ".render(" in bootstrap
    assert not any(engine in bootstrap for engine in ("Plotly.newPlot", "echarts.init", "vegaEmbed"))
    assert _embedded_payloads(document) == manifest["native_specs"]
    assert not any("fallback" in warning.lower() for warning in artifact.warnings)
    assert any("network" in warning.lower() for warning in artifact.warnings)


def test_violin_box_fallback_is_disclosed_and_uses_distribution_statistics(tmp_path):
    rows = [{"group": "A", "value": value} for value in [5, 1, 4, 2, 3]]
    artifact, manifest, _ = _render(tmp_path, rows, kind="violin", x="group", y="value")
    chart = manifest["charts"][0]
    assert chart["requested_kind"] == "violin"
    assert chart["rendered_kind"] == "box"
    payload = manifest["native_specs"][0]
    assert payload["type"] == "box"
    assert _values(payload, "x") == ["A"]
    assert _values(payload, "y") == [[1, 2, 3, 4, 5]]
    for warnings in (artifact.warnings, manifest["warnings"]):
        assert any(all(word in warning.lower() for word in ("fallback", "violin", "box")) for warning in warnings)
