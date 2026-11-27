"""Positive/negative controls for N09 repairs to historical acceptance oracles."""

from __future__ import annotations

import copy
import importlib.util
import json
import math
import sys
from html import escape
from pathlib import Path

import pytest

from deepviz.models import ChartSpec

ROOT = Path(__file__).resolve().parents[3]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ACCEPTANCE = _load("_n09_acceptance_helper", "tests/test_acceptance_matrix.py")
ANTV = _load("_n09_antv_helper", "python/deepviz/tests/test_backend_antv.py")
PLOTLY = _load("_n09_plotly_helper", "python/deepviz/tests/test_backend_plotly.py")
VEGA = _load("_n09_vega_helper", "python/deepviz/tests/test_backend_vega.py")


@pytest.mark.parametrize("mutation", ["missing", "altered", "script", "event"])
def test_n09_wrapped_svg_title_oracle_still_rejects_corruption(mutation: str) -> None:
    valid = ('<svg xmlns="http://www.w3.org/2000/svg"><!-- Very longti\ntle &amp; safe -->'
             '<path d="M0 0L2 2"/><path d="M2 0L0 2"/><rect width="2" height="2"/>'
             '<circle cx="1" cy="1" r="1"/></svg>')
    ACCEPTANCE.assert_svg_semantics(valid, "matplotlib", "Very longtitle & safe")
    if mutation == "missing":
        invalid = valid.replace("Very longti\ntle &amp; safe", "")
    elif mutation == "altered":
        invalid = valid.replace("longti", "wrongti")
    elif mutation == "script":
        invalid = valid.replace("</svg>", "<script>window.N09_BAD=1</script></svg>")
    else:
        invalid = valid.replace('<rect width="2"', '<rect onclick="bad()" width="2"')
    with pytest.raises(AssertionError):
        ACCEPTANCE.assert_svg_semantics(invalid, "matplotlib", "Very longtitle & safe")


def _browser_case():
    spec = ChartSpec(kind="bar", title=ACCEPTANCE.TITLE, x="category", y="y")
    payload = {"data": [{"type": "bar", "x": ["A"], "y": [2]}], "layout": {}}
    manifest = {"native_specs": [payload]}
    body = json.dumps([payload]).replace("<", "\\u003c").replace(">", "\\u003e")
    html = (f'<html><title>{escape(spec.title)}</title>'
            f'<script id="deepviz-data" type="application/json">{body}</script>'
            '<script>Plotly.newPlot(el,p.data,p.layout);</script></html>')
    return spec, manifest, html


@pytest.mark.parametrize("mutation", ["no_payload", "different_payload", "event", "script", "empty_traces"])
def test_n09_browser_oracle_rejects_manifest_only_corruption_and_xss(mutation: str) -> None:
    spec, manifest, html = _browser_case()
    ACCEPTANCE.assert_browser_semantics("plotly", html, [manifest], spec, [])
    if mutation == "no_payload":
        html = html.replace('id="deepviz-data"', 'id="not-the-bootstrap-payload"')
    elif mutation == "different_payload":
        html = html.replace('"y": [2]', '"y": [999]')
    elif mutation == "event":
        html += '<img src="x" onerror="bad()">'
    elif mutation == "script":
        html += '<script>window.__DV_XSS__=1</script>'
    else:
        manifest["native_specs"][0]["data"] = []
        html = html.replace('{"type": "bar", "x": ["A"], "y": [2]}', "")
    with pytest.raises(AssertionError):
        ACCEPTANCE.assert_browser_semantics("plotly", html, [manifest], spec, [])


@pytest.mark.parametrize("engine", ["plotly", "vega", "echarts", "antv"])
@pytest.mark.parametrize("mutation", ["wrong_value", "missing", "duplicate"])
def test_n09_native_coordinate_oracle_rejects_wrong_values_and_row_loss(engine: str, mutation: str) -> None:
    rows = [{"label": "A", "value": -4}, {"label": "B", "value": 0}, {"label": "C", "value": 8}]
    spec = ChartSpec(kind="bar", x="label", y="value", aggregation="none")
    chart = {"spec": spec.model_dump(), "records": rows}
    if engine == "plotly":
        payload = {"data": [{"x": ["A", "B", "C"], "y": [-4, 0, 8]}]}
    elif engine == "vega":
        payload = {"encoding": {"x": {"field": "u"}, "y": {"field": "v"}},
                   "data": {"values": [{"u": row["label"], "v": row["value"]} for row in rows]}}
    elif engine == "echarts":
        payload = {"series": [{"data": [[row["label"], row["value"]] for row in rows]}]}
    else:
        payload = {"encode": {"x": "u", "y": "v"},
                   "data": [{"u": row["label"], "v": row["value"]} for row in rows]}
    ACCEPTANCE.assert_native_xy_values(engine, payload, chart)
    wrong_rows = copy.deepcopy(rows)
    if mutation == "wrong_value":
        wrong_rows[0]["value"] = 999
    elif mutation == "missing":
        wrong_rows.pop()
    else:
        wrong_rows.append(copy.deepcopy(wrong_rows[0]))
    # Mutate the independent expected data, not production code; a symmetric
    # equality oracle must reject either side being numerically corrupted.
    with pytest.raises(AssertionError, match="changed a mapped observation"):
        ACCEPTANCE.assert_native_xy_values(engine, payload, chart | {"records": wrong_rows})


@pytest.mark.parametrize("mutation", ["marker_only", "wrong_value", "reordered"])
def test_n09_plotly_line_oracle_allows_markers_but_not_disconnected_or_wrong_data(mutation: str) -> None:
    trace = {"type": "scatter", "mode": "lines+markers", "x": ["third", "first"], "y": [30, 10]}
    expected = [("third", 30), ("first", 10)]
    PLOTLY._assert_line_trace(trace, expected)
    if mutation == "marker_only":
        trace["mode"] = "markers"
    elif mutation == "wrong_value":
        trace["y"][0] = 999
    else:
        trace["x"].reverse()
        trace["y"].reverse()
    with pytest.raises(AssertionError):
        PLOTLY._assert_line_trace(trace, expected)


@pytest.mark.parametrize("mutation", ["no_line", "wrong_value", "reordered", "stack"])
def test_n09_antv_layered_line_oracle_rejects_missing_or_corrupted_connected_marks(mutation: str) -> None:
    mark = {"type": "line", "encode": {"x": "u", "y": "v", "color": "c"},
            "data": [{"u": "third", "v": 30, "c": "B"}, {"u": "first", "v": 10, "c": "B"}]}
    payload = {"type": "view", "children": [mark, {**copy.deepcopy(mark), "type": "point"}]}
    expected = {"B": [("third", 30), ("first", 10)]}
    ANTV._assert_connected_series(payload, "line", expected)
    if mutation == "no_line":
        payload["children"] = payload["children"][1:]
    elif mutation == "wrong_value":
        mark["data"][0]["v"] = 999
    elif mutation == "reordered":
        mark["data"].reverse()
    else:
        mark["transform"] = [{"type": "stackY"}]
    with pytest.raises(AssertionError):
        ANTV._assert_connected_series(payload, "line", expected)


def test_n09_unicode_minus_parser_preserves_the_sign() -> None:
    assert VEGA._number("\N{MINUS SIGN}7.25") == VEGA._number("-7.25") == -7.25
    assert VEGA._number("0") == 0
    assert VEGA._number("7.25") == 7.25
    with pytest.raises(ValueError):
        VEGA._number("not-a-number")


def test_n09_mean_rounding_tolerance_does_not_accept_wrong_values_or_small_residual_loss() -> None:
    ACCEPTANCE.assert_aggregate_values({"A": -2.7e-17}, {"A": 0.0}, "mean")
    for actual, expected in [({"A": 1e-8}, {"A": 0.0}), ({"A": 0.0}, {"A": 1.0})]:
        with pytest.raises(AssertionError):
            ACCEPTANCE.assert_aggregate_values(actual, expected, "mean")
    with pytest.raises(AssertionError):
        ACCEPTANCE.assert_aggregate_values({"A": 0.0}, {"A": 1}, "sum")
    with pytest.raises(AssertionError):
        ACCEPTANCE.assert_aggregate_values({"A": 1.0}, {"A": 1}, "count")


@pytest.mark.parametrize("kind", ["radar", "treemap", "sunburst", "gauge", "table"])
def test_n09_native_kind_remaps_require_the_actual_specialized_geometry(kind: str) -> None:
    spec = ChartSpec(kind=kind, title=ACCEPTANCE.TITLE)
    if kind == "radar":
        payload = {"type": "line", "coordinate": {"type": "polar"},
                   "data": [{"u": "A", "v": 2}, {"u": "B", "v": 6}, {"u": "A", "v": 2}],
                   "encode": {"x": "u", "y": "v"}}
    elif kind == "treemap":
        payload = {"type": "rect", "encode": {"x": ["left", "right"], "y": ["bottom", "top"]},
                   "data": [{"left": 0, "right": 0.25, "bottom": 0, "top": 1},
                            {"left": 0.25, "right": 1, "bottom": 0, "top": 1}]}
    elif kind in {"sunburst", "gauge"}:
        payload = {"type": "interval", "coordinate": {"type": "theta", "innerRadius": 0.5},
                   "transform": [{"type": "stackY"}], "encode": {"y": "v"},
                   "data": [{"v": 25}, {"v": 75}]}
        if kind == "gauge":
            payload["coordinate"].update(startAngle=-math.pi, endAngle=0)
    else:
        payload = {"type": "text", "data": [{"u": "A", "v": 2, "label": "A: 2"}],
                   "encode": {"x": "u", "y": "v", "text": "label"}}

    def check(options):
        encoded = json.dumps([options])
        page = (f'<html><title>{escape(spec.title)}</title>'
                f'<script id="deepviz-data" type="application/json">{encoded}</script>'
                '<script>const c=new G2.Chart({});c.render();</script></html>')
        ACCEPTANCE.assert_browser_semantics("antv", page, [{"native_specs": [options]}], spec, [])

    check(payload)
    invalid = copy.deepcopy(payload)
    if kind in {"radar", "sunburst", "gauge"}:
        invalid.pop("coordinate")
    elif kind == "treemap":
        invalid["data"][1]["right"] = 0.5
    else:
        invalid["encode"].pop("text")
    with pytest.raises(AssertionError):
        check(invalid)
