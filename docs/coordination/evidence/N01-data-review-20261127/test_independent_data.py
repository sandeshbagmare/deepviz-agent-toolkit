"""N01-owned independent reproductions; never edit production or sibling trees."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from deepviz.engines import native_spec
from deepviz.models import ChartSpec
from deepviz.normalize import normalize
from deepviz.render import render


def test_control_explicit_heatmap_color_uses_reduced_measure() -> None:
    rows = [{"day": "Mon", "region": "North", "amount": 3}]
    spec = ChartSpec(kind="heatmap", x="day", y="region", color="amount")
    prepared = normalize(rows, spec)
    native, _, _ = native_spec("echarts", prepared.records, spec)
    assert native["series"][0]["data"] == [[0, 0, 3]]


@pytest.mark.parametrize("engine", ["plotly", "echarts", "vega", "antv"])
def test_count_heatmap_color_is_the_coordinate_count(engine: str) -> None:
    rows = [{"day": "Mon", "region": "North"}] * 2 + [
        {"day": "Mon", "region": "South"}
    ]
    spec = ChartSpec(kind="heatmap", x="day", y="region")
    prepared = normalize(rows, spec)
    assert [row["count"] for row in prepared.records] == [2, 1]
    native, _, _ = native_spec(engine, prepared.records, spec)
    if engine == "plotly":
        actual = native["data"][0]["marker"]["color"]
    elif engine == "echarts":
        actual = [row[2] for row in native["series"][0]["data"]]
    else:
        data = native["data"]["values"] if engine == "vega" else native["data"]
        actual = [row["_heat"] for row in data]
    assert actual == [2, 1]


def test_missing_line_value_remains_a_gap_not_a_zero() -> None:
    spec = ChartSpec(kind="line", x="t", y="value", aggregation="none")
    prepared = normalize(
        [{"t": 0, "value": 7}, {"t": 1, "value": None}, {"t": 2, "value": 9}], spec
    )
    assert prepared.records[1]["value"] is None
    native, _, _ = native_spec("plotly", prepared.records, spec)
    assert native["data"][0]["y"] == [7, None, 9]


def test_inferred_scalar_histogram_bins_values_not_generated_indices() -> None:
    spec = ChartSpec(kind="histogram")
    prepared = normalize([10, 10, 10, 20], spec)
    native, _, _ = native_spec("plotly", prepared.records, spec)
    trace = native["data"][0]
    assert trace["x"] == [12.5, 17.5]
    assert trace["y"] == [3, 1]


def test_control_explicit_histogram_field_bins_observations() -> None:
    spec = ChartSpec(kind="histogram", x="value")
    prepared = normalize([10, 10, 10, 20], spec)
    native, _, _ = native_spec("plotly", prepared.records, spec)
    assert native["data"][0]["x"] == [12.5, 17.5]
    assert native["data"][0]["y"] == [3, 1]


def test_dashboard_iterator_preserves_supported_decimal_values(tmp_path: Path) -> None:
    rows = [{"category": "a", "value": Decimal("2.5")},
            {"category": "a", "value": Decimal("3.5")}]
    spec = {"kind": "dashboard", "charts": [
        {"x": "category", "y": "value", "aggregation": "sum"}
    ]}
    direct = render(rows, spec, engine="echarts", output_dir=tmp_path)
    replayed = render(iter(rows), spec, engine="echarts", output_dir=tmp_path)

    def records(artifact):
        manifest_path = next(Path(p) for p in artifact.paths if Path(p).name == "manifest.json")
        return json.loads(manifest_path.read_text(encoding="utf-8"))["charts"][0]["records"]

    assert records(direct) == [{"category": "a", "value": 6.0}]
    assert records(replayed) == records(direct)


def test_data_path_does_not_hide_partial_graphql_errors() -> None:
    response = {"data": {"users": {"nodes": [{"id": 1}]}},
                "errors": [{"message": "second page unavailable"}]}
    whole = normalize(response, {"aggregation": "none"})
    selected = normalize(response, {"aggregation": "none", "data_path": "data.users.nodes"})
    assert whole.records == selected.records == [{"id": 1}]
    assert any("errors alongside" in message for message in whole.warnings)
    assert any("errors alongside" in message for message in selected.warnings)
