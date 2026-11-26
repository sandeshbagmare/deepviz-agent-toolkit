"""N09 independent regression for same-spec grouped-area meaning across engines."""

from __future__ import annotations

from typing import Any

import pytest
import vl_convert

from deepviz.engines import native_spec
from deepviz.models import ChartSpec


def _area_marks(value: Any) -> list[dict]:
    if isinstance(value, dict):
        if value.get("marktype") == "area" and value.get("role") == "mark":
            return [value]
        return [mark for child in value.values() for mark in _area_marks(child)]
    if isinstance(value, list):
        return [mark for child in value for mark in _area_marks(child)]
    return []


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_n09_vega_grouped_area_keeps_independent_zero_baselines(theme: str) -> None:
    rows = [
        {"t": 0, "value": 2, "region": "East"},
        {"t": 1, "value": 6, "region": "East"},
        {"t": 0, "value": 5, "region": "West"},
        {"t": 1, "value": 1, "region": "West"},
    ]
    spec = ChartSpec(kind="area", x="t", y="value", color="region", aggregation="none", theme=theme)
    native, warnings, _ = native_spec("vega", rows, spec)
    assert not warnings
    areas = _area_marks(vl_convert.vegalite_to_scenegraph(native))
    assert len(areas) == 2
    points = [point for area in areas for point in area["items"]]
    assert len(points) == 4
    # Matplotlib and Plotly use a zero baseline for every series. Hidden Vega
    # stacking instead moves East's baseline to West's observations and draws
    # a misleading constant total of seven despite no requested stack mode.
    assert [point["y2"] for point in points] == pytest.approx([native["height"]] * 4)
