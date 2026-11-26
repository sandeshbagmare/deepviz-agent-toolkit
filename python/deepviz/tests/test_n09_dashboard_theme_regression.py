"""N09 visual regressions: explicit dashboard child themes must not be silent."""

from __future__ import annotations

from pathlib import Path

import pytest
from matplotlib.colors import to_rgb

from deepviz.engines import matplotlib_figure
from deepviz.models import ChartSpec
from deepviz.render import render


def _luminance(color) -> float:
    values = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in to_rgb(color)]
    return sum(value * weight for value, weight in zip(values, [0.2126, 0.7152, 0.0722], strict=True))


def _contrast(first, second) -> float:
    high, low = sorted([_luminance(first), _luminance(second)], reverse=True)
    return (high + 0.05) / (low + 0.05)


@pytest.mark.parametrize("parent_theme", ["light", "dark"])
def test_n09_matplotlib_mixed_theme_titles_contrast_with_their_actual_background(parent_theme: str) -> None:
    rows = [{"category": "Alpha", "value": 3}, {"category": "Beta", "value": 7}]
    parent = ChartSpec(kind="dashboard", theme=parent_theme, charts=[{"kind": "bar"}, {"kind": "bar"}])
    children = [ChartSpec(kind="bar", x="category", y="value", title=f"{theme} panel", theme=theme)
                for theme in ["dark", "light"]]
    figure, _ = matplotlib_figure([(rows, child) for child in children], parent)
    try:
        figure.canvas.draw()
        for axis in figure.axes:
            title = axis.title
            extent = title.get_window_extent(figure.canvas.get_renderer())
            center = ((extent.x0 + extent.x1) / 2, (extent.y0 + extent.y1) / 2)
            background = axis.get_facecolor() if axis.bbox.contains(*center) else figure.get_facecolor()
            backdrop = title.get_bbox_patch()
            if backdrop is not None and backdrop.get_visible() and backdrop.get_facecolor()[3] == 1:
                background = backdrop.get_facecolor()
            assert _contrast(title.get_color(), background) >= 4.5
    finally:
        figure.clear()


def test_n09_vega_dashboard_honors_or_discloses_dark_child_theme(tmp_path: Path) -> None:
    rows = [{"category": "Alpha", "value": 3}, {"category": "Beta", "value": 7}]
    spec = ChartSpec(kind="dashboard", x="category", y="value", theme="light", charts=[
        {"kind": "bar", "title": "Explicit dark child", "theme": "dark"},
        {"kind": "bar", "title": "Explicit light child", "theme": "light"},
    ])
    artifact = render(rows, spec, engine="vega", output_dir=tmp_path)
    svg = Path(next(path for path in artifact.paths if path.endswith(".svg"))).read_text(encoding="utf-8")
    assert "#171b26" in svg.lower() or any("theme" in warning.lower() for warning in artifact.warnings)
