"""Literal Plotly text at native and real-browser boundaries (issue36)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from deepviz.engines import native_spec
from deepviz.models import ChartKind, ChartSpec
from deepviz.render import render

LINK = '<a href="https://example.invalid/r27">A</a>'
ENTITY = "&lt;b&gt; B &amp; C"
TEXT = '<b>Q" & \' Ω</b>'
TITLE = 'R27 "Ω" & <b>Title</b>'
FIELD = 'axis "Ω" & <i>X</i>'
VALUE = 'value "Ω" & <b>Y</b>'
SERIES = '<b>Group" & Ω</b>'


@pytest.mark.parametrize("kind,channel", [
    ("bar", "x"), ("line", "x"), ("area", "x"), ("scatter", "x"),
    ("bubble", "x"), ("box", "x"), ("violin", "x"), ("pie", "labels"),
    ("treemap", "labels"), ("sunburst", "labels"), ("funnel", "y"), ("radar", "theta"),
])
def test_every_category_sink_encodes_literal_strings_once(kind: ChartKind, channel: str) -> None:
    rows = [{"x": value, "y": number} for value, number in zip([LINK, ENTITY, TEXT], [3, 7, 11], strict=True)]
    original = deepcopy(rows)
    payload, _, _ = native_spec("plotly", rows, ChartSpec(kind=kind, x="x", y="y", aggregation="none"))
    expected = ['&lt;a href="https://example.invalid/r27"&gt;A&lt;/a&gt;',
                "&amp;lt;b&amp;gt; B &amp;amp; C", '&lt;b&gt;Q" &amp; \' Ω&lt;/b&gt;']
    if kind == "radar":
        expected += expected[:1]
    assert rows == original
    assert payload["data"][0][channel] == expected


@pytest.mark.parametrize("xs", [[1, 2.5, 4], ["001", "002", "004"],
                               ["2026-02-01", "2026-02-02", "2026-02-04"]])
def test_coordinate_types_order_values_and_records_are_unchanged(xs: list) -> None:
    rows = [{"x": x, "y": y, "group": SERIES} for x, y in zip(xs, [3, -7, 11], strict=True)]
    original = deepcopy(rows)
    payload, _, _ = native_spec(
        "plotly", rows, ChartSpec(kind="line", x="x", y="y", color="group", aggregation="none"),
    )
    trace = payload["data"][0]
    assert rows == original
    assert trace["x"] == xs and list(map(type, trace["x"])) == list(map(type, xs))
    assert trace["y"] == [3, -7, 11]
    assert trace["name"] == '&lt;b&gt;Group" &amp; Ω&lt;/b&gt;'


def test_heatmap_text_axes_and_geo_hover_are_literal_with_numeric_values_intact() -> None:
    heat, _, _ = native_spec("plotly", [{"x": TEXT, "y": ENTITY, "z": 7}],
                             ChartSpec(kind="heatmap", x="x", y="y", color="z"))
    geo, _, _ = native_spec("plotly", [{"lon": -30, "lat": 7, "text": TEXT}],
                            ChartSpec(kind="geo", x="lon", y="lat", color="text"))
    assert heat["data"][0]["marker"]["color"] == [7]
    assert geo["data"][0]["x"] == [-30] and geo["data"][0]["y"] == [7]
    assert heat["data"][0]["x"] == ['&lt;b&gt;Q" &amp; \' Ω&lt;/b&gt;']
    assert heat["data"][0]["y"] == ["&amp;lt;b&amp;gt; B &amp;amp; C"]
    assert geo["data"][0]["text"] == ['&lt;b&gt;Q" &amp; \' Ω&lt;/b&gt;']


def test_title_fields_table_quotes_and_entities_have_text_not_attribute_encoding() -> None:
    rows = [{FIELD: TEXT, VALUE: 7, "entity": ENTITY}]
    original = deepcopy(rows)
    payload, _, _ = native_spec("plotly", rows, ChartSpec(kind="table", title=TITLE, x=FIELD, y=VALUE))
    assert rows == original
    assert payload["data"][0]["header"]["values"][:2] == [
        'axis "Ω" &amp; &lt;i&gt;X&lt;/i&gt;', 'value "Ω" &amp; &lt;b&gt;Y&lt;/b&gt;']
    assert payload["data"][0]["cells"]["values"] == [
        ['&lt;b&gt;Q" &amp; \' Ω&lt;/b&gt;'], ["7"], ["&amp;lt;b&amp;gt; B &amp;amp; C"]]
    assert payload["layout"]["title"]["text"] == 'R27 "Ω" &amp; &lt;b&gt;Title&lt;/b&gt;'
    assert payload["layout"]["xaxis"]["title"]["text"] == 'axis "Ω" &amp; &lt;i&gt;X&lt;/i&gt;'


@pytest.mark.parametrize("case", ["chart", "dashboard", "table", "geo"])
def test_public_render_native_dom_is_exact_literal_and_inert(case: str, tmp_path: Path) -> None:
    node = shutil.which("node")
    modules = Path(os.environ.get("R27_NODE_MODULES", "node_modules")).resolve()
    if node is None or not (modules / "playwright/package.json").is_file():
        pytest.skip("Requires existing Node/Playwright/Chromium; never installs")
    if case == "table":
        rows = [{FIELD: TEXT, VALUE: 7, "entity": ENTITY}]
        child = ChartSpec(kind="table", title=TITLE, width=1400, height=500)
        literals = [FIELD, VALUE, TEXT, ENTITY]
    elif case == "geo":
        rows = [{"lon": x, "lat": y, "label": label} for x, y, label in
                zip([-120, -60, 120], [10, 20, 35], [LINK, ENTITY, TEXT], strict=True)]
        child = ChartSpec(kind="geo", x="lon", y="lat", color="label", title=TITLE,
                          width=1400, height=500)
        literals = []
    else:
        rows = [{FIELD: x, VALUE: y, "series": SERIES} for x, y in
                zip([LINK, ENTITY, TEXT], [3, 7, 11], strict=True)]
        child = ChartSpec(kind="bar", x=FIELD, y=VALUE, color="series", title=TITLE,
                          aggregation="none", width=1400, height=500)
        literals = [LINK, ENTITY, TEXT, SERIES, FIELD, VALUE]
    spec = (ChartSpec(kind="dashboard", title=TITLE, charts=[child, child], columns=1, width=1400)
            if case == "dashboard" else child)
    original = deepcopy(rows)
    artifact = render(rows, spec, engine="plotly", output_dir=tmp_path / "out")
    html = next(Path(path) for path in artifact.paths if path.endswith("chart.html"))
    manifest = json.loads(next(Path(path) for path in artifact.paths if path.endswith("manifest.json"))
                          .read_text(encoding="utf-8"))
    count = 2 if case == "dashboard" else 1
    assert rows == original and all(chart["records"] == original for chart in manifest["charts"])
    assert artifact.input_count == len(rows) and artifact.output_count == len(rows) * count
    request = {"case": case, "html": str(html), "child_count": count, "literals": literals,
               "title": TITLE, "rows": rows, "hover": [LINK, ENTITY, TEXT] if case == "geo" else [],
               "result": str(tmp_path / "browser.json"), "image": str(tmp_path / "browser.png")}
    request_file = tmp_path / "request.json"
    request_file.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
    helper = Path(__file__).resolve().parents[3] / "tests/browser/r27_plotly_literal.mjs"
    process = subprocess.run([node, str(helper), str(request_file), str(modules)],
                             capture_output=True, text=True, timeout=120, check=False)
    assert process.returncode == 0, process.stderr[-3000:]
    result = json.loads((tmp_path / "browser.json").read_text(encoding="utf-8"))
    assert result["errors"] == [] and result["blocked"] == [], result
    failures = []
    for snapshot in result["snapshots"]:
        if snapshot["anchors"] or snapshot["handlers"] or snapshot["missing"]:
            failures.append(snapshot)
        assert snapshot["titles"] == [TITLE]
        if case == "geo":
            assert snapshot["x"] == [-120, -60, 120] and snapshot["y"] == [10, 20, 35]
    assert failures == [], failures
    if case == "geo":
        assert len(result["hover_states"]) == 3
        for snapshot, expected in zip(result["hover_states"], [LINK, ENTITY, TEXT], strict=True):
            assert snapshot["anchors"] == [] and snapshot["handlers"] == []
            assert any(expected in text for text in snapshot["hover_text"]), snapshot
