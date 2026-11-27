"""Native transparent charts need their explicit child theme's real backdrop."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

import pytest

from deepviz.render import render


class ChartContainers(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.styles: dict[str, dict[str, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        identity = values.get("id") or ""
        if tag == "div" and identity.startswith("chart-"):
            self.styles[identity] = dict(
                part.split(":", 1) for part in (values.get("style") or "").split(";") if ":" in part
            )


@pytest.mark.parametrize("engine", ["antv", "echarts", "plotly"])
@pytest.mark.parametrize("parent_theme", ["light", "dark"])
def test_transparent_native_child_uses_its_own_theme_backdrop(
    tmp_path: Path, engine: str, parent_theme: str,
) -> None:
    rows = [{"category": "A", "value": 3}, {"category": "B", "value": 7}]
    spec = {"kind": "dashboard", "theme": parent_theme, "x": "category", "y": "value",
            "charts": [{"kind": "bar", "theme": "light", "title": "Light child"},
                       {"kind": "bar", "theme": "dark", "title": "Dark child"}]}
    artifact = render(rows, spec, engine=engine, output_dir=tmp_path)
    html = Path(next(path for path in artifact.paths if path.endswith(".html"))).read_text(encoding="utf-8")
    parser = ChartContainers()
    parser.feed(html)
    assert set(parser.styles) == {"chart-0", "chart-1"}
    assert parser.styles["chart-0"].get("background") == "#ffffff"
    assert parser.styles["chart-1"].get("background") == "#171b26"
    parent_background = "#171b26" if parent_theme == "dark" else "#ffffff"
    assert f"body{{background:{parent_background};" in html
    assert (artifact.input_count, artifact.output_count) == (2, 4)
