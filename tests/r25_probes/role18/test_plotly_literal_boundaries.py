"""Three NEW native-boundary controls; no browser or old QA20 probe replay.

These are intentionally strict RED until the source owner grants and implements
the literal-text fix. They complement, not replace, QA20's real DOM/hover tests.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from subprocess import check_output
from typing import Any

import pytest

import deepviz.engines
import deepviz.models
from deepviz.engines import native_spec
from deepviz.models import ChartKind, ChartSpec


@pytest.fixture(scope="module", autouse=True)
def exact_source_guard() -> None:
    """Fail closed if a broader installed candidate or modified engine is used."""
    root = Path(__file__).resolve().parents[3]
    base = "7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6"
    for module in (deepviz.engines, deepviz.models):
        assert module.__file__ is not None
        path = Path(module.__file__).resolve()
        relative = path.relative_to(root).as_posix()
        assert relative.startswith("python/deepviz/src/deepviz/")
        blob = check_output(["git", "show", f"{base}:{relative}"], cwd=root)
        assert path.read_bytes().replace(b"\r\n", b"\n") == blob


def test_entity_like_categories_remain_distinct_without_coercing_coordinates() -> None:
    """Catch raw entity decoding or a broad sanitizer that changes typed data."""
    xs = ['<b>"A" & B</b>', '&lt;b&gt;"A" &amp; B&lt;/b&gt;', 1, 2.5,
          "001", "2026-03-01T00:00:00Z"]
    rows = [{"x": x, "value": index} for index, x in enumerate(xs)]
    original = deepcopy(rows)
    payload, warnings, kind = native_spec(
        "plotly", rows, ChartSpec(kind="bar", x="x", y="value", aggregation="none"),
    )
    trace = payload["data"][0]
    assert rows == original
    assert warnings == [] and kind == "bar"
    assert trace["y"] == list(range(6))
    assert [type(value) for value in trace["x"]] == [str, str, int, float, str, str]
    assert trace["x"][2:] == [1, 2.5, "001", "2026-03-01T00:00:00Z"]
    assert trace["x"][:2] == [
        '&lt;b&gt;"A" &amp; B&lt;/b&gt;',
        '&amp;lt;b&amp;gt;"A" &amp;amp; B&amp;lt;/b&amp;gt;',
    ], "Entity-looking source labels must not collapse into markup-looking labels"


def test_noncartesian_labels_and_both_heatmap_axes_have_literal_boundaries() -> None:
    """Catch a bar-only fix that leaves other user-authored native labels raw."""
    label = '<a href="https://example.invalid/r25">Q & R</a>'
    expected = '&lt;a href="https://example.invalid/r25"&gt;Q &amp; R&lt;/a&gt;'
    failures = []
    cases: tuple[tuple[ChartKind, str], ...] = (
        ("pie", "labels"), ("treemap", "labels"), ("sunburst", "labels"),
        ("funnel", "y"), ("radar", "theta"), ("box", "x"), ("violin", "x"),
    )
    for chart_kind, channel in cases:
        rows: list[dict[str, Any]] = [{"x": label, "value": 3}, {"x": "safe", "value": 7}]
        original = deepcopy(rows)
        payload, _, _ = native_spec(
            "plotly", rows, ChartSpec(kind=chart_kind, x="x", y="value", aggregation="none"),
        )
        assert rows == original
        values = payload["data"][0][channel]
        want = [expected, "safe", expected] if chart_kind == "radar" else [expected, "safe"]
        if values != want:
            failures.append((chart_kind, channel, values))
    heat_rows = [{"x": label, "y": '<b>"South" & West</b>', "intensity": 7}]
    original_heat = deepcopy(heat_rows)
    heat, _, _ = native_spec(
        "plotly", heat_rows,
        ChartSpec(kind="heatmap", x="x", y="y", color="intensity", aggregation="none"),
    )
    assert heat_rows == original_heat
    assert heat["data"][0]["marker"]["color"] == [7]
    if heat["data"][0]["x"] != [expected]:
        failures.append(("heatmap", "x", heat["data"][0]["x"]))
    if heat["data"][0]["y"] != ['&lt;b&gt;"South" &amp; West&lt;/b&gt;']:
        failures.append(("heatmap", "y", heat["data"][0]["y"]))
    assert failures == [], failures


def test_native_field_titles_and_table_cells_do_not_turn_quotes_into_entities() -> None:
    """Catch HTML-attribute escaping reused at Plotly's text-only sinks."""
    field = 'cost "quoted" & <b>net</b>'
    expected_field = 'cost "quoted" &amp; &lt;b&gt;net&lt;/b&gt;'
    title = 'R25 "quoted" & \'single\' <b>title</b>'
    expected_title = 'R25 "quoted" &amp; \'single\' &lt;b&gt;title&lt;/b&gt;'
    rows = [{field: 1, "value": 3}]
    original = deepcopy(rows)
    payload, _, _ = native_spec(
        "plotly", rows,
        ChartSpec(kind="line", x=field, y="value", title=title, aggregation="none"),
    )
    table_rows = [{field: '\'cell\' "quoted" & <i>value</i>', "amount": 7}]
    original_table = deepcopy(table_rows)
    table, _, _ = native_spec("plotly", table_rows, ChartSpec(kind="table", title=title))
    assert rows == original and table_rows == original_table
    assert payload["data"][0]["x"] == [1] and payload["data"][0]["y"] == [3]
    assert table["data"][0]["cells"]["values"][1] == ["7"]
    observations = {
        "title": (payload["layout"]["title"]["text"], expected_title),
        "axis": (payload["layout"]["xaxis"]["title"]["text"], expected_field),
        "table-title": (table["layout"]["title"]["text"], expected_title),
        "table-header": (table["data"][0]["header"]["values"], [expected_field, "amount"]),
        "table-cell": (table["data"][0]["cells"]["values"][0],
                       ['\'cell\' "quoted" &amp; &lt;i&gt;value&lt;/i&gt;']),
    }
    failures = {name: (got, want) for name, (got, want) in observations.items() if got != want}
    assert failures == {}, failures
