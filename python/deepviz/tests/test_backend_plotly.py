"""Assert Plotly's emitted trace semantics, not just artifact creation."""
from __future__ import annotations

import json
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from matplotlib.colors import to_rgb

from deepviz.models import Artifact, ChartSpec
from deepviz.render import render


@dataclass
class _Script:
    attributes: dict[str, str | None]
    text: str = ""


class _Page(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.scripts: list[_Script] = []
        self.dependencies: list[str] = []
        self.title: list[str] = []
        self._script: _Script | None = None
        self._in_title = False
        self.feed(source)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script":
            self._script = _Script(attributes)
            self.scripts.append(self._script)
            if attributes.get("src"):
                self.dependencies.append(str(attributes["src"]))
        elif tag == "link" and "stylesheet" in str(attributes.get("rel", "")).split():
            self.dependencies.append(str(attributes.get("href", "")))
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._script = None
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._script.text += data
        elif self._in_title:
            self.title.append(data)


def _render_plotly(
    rows: list[dict[str, Any]], spec: ChartSpec, tmp_path: Path,
) -> tuple[dict[str, Any], _Page]:
    artifact = render(rows, spec, engine="plotly", output_dir=tmp_path)
    assert isinstance(artifact, Artifact)
    assert artifact.engine == "plotly"
    assert artifact.mime_type == "text/html"
    assert (artifact.input_count, artifact.output_count) == (len(rows), len(rows))
    html_paths = [Path(path) for path in artifact.paths if Path(path).suffix == ".html"]
    assert len(html_paths) == 1
    page = _Page(html_paths[0].read_text(encoding="utf-8"))
    embedded = [script for script in page.scripts if script.attributes.get("id") == "deepviz-data"]
    assert len(embedded) == 1
    assert embedded[0].attributes.get("type") == "application/json"
    payloads = json.loads(embedded[0].text)
    assert len(payloads) == 1
    return payloads[0], page


def test_scatter_uses_mapped_coordinates_instead_of_row_indices(tmp_path: Path) -> None:
    payload, _ = _render_plotly(
        [
            {"decoy": 999, "distance": 140, "profit": 7.5},
            {"decoy": 888, "distance": -30, "profit": -2.25},
            {"decoy": 777, "distance": 41, "profit": 18},
        ],
        ChartSpec(kind="scatter", x="distance", y="profit"), tmp_path,
    )
    assert len(payload["data"]) == 1
    trace = payload["data"][0]
    assert (trace["type"], trace["mode"]) == ("scatter", "markers")
    assert list(zip(trace["x"], trace["y"], strict=True)) == [(140, 7.5), (-30, -2.25), (41, 18)]
    assert payload["layout"]["xaxis"]["title"]["text"] == "distance"
    assert payload["layout"]["yaxis"]["title"]["text"] == "profit"


def test_bar_retains_negative_zero_and_repeated_category_observations(tmp_path: Path) -> None:
    payload, _ = _render_plotly(
        [{"category": "net", "amount": -9}, {"category": "net", "amount": 0},
         {"category": "gross", "amount": 12.5}],
        ChartSpec(kind="bar", x="category", y="amount", aggregation="none"), tmp_path,
    )
    assert len(payload["data"]) == 1
    trace = payload["data"][0]
    assert trace["type"] == "bar"
    assert trace["x"] == ["net", "net", "gross"]
    assert trace["y"] == [-9, 0, 12.5]


def test_line_preserves_supplied_timestamp_order_and_value_pairing(tmp_path: Path) -> None:
    # There is no sort channel: silently sorting would change the supplied path.
    payload, _ = _render_plotly(
        [{"when": "2026-03-10T12:00:00Z", "reading": 4},
         {"when": "2026-01-01T00:00:00Z", "reading": 90},
         {"when": "2026-03-10T12:00:01Z", "reading": -3}],
        ChartSpec(kind="line", x="when", y="reading", aggregation="none"), tmp_path,
    )
    assert len(payload["data"]) == 1
    trace = payload["data"][0]
    assert (trace["type"], trace["mode"]) == ("scatter", "lines")
    assert list(zip(trace["x"], trace["y"], strict=True)) == [
        ("2026-03-10T12:00:00Z", 4), ("2026-01-01T00:00:00Z", 90),
        ("2026-03-10T12:00:01Z", -3),
    ]


def test_color_groups_partition_interleaved_points_without_repairing_by_index(tmp_path: Path) -> None:
    payload, _ = _render_plotly(
        [{"x": 11, "y": 101, "team": "west"}, {"x": 22, "y": 202, "team": "east"},
         {"x": 33, "y": -303, "team": "west"}, {"x": 44, "y": 404, "team": "east"}],
        ChartSpec(kind="scatter", x="x", y="y", color="team"), tmp_path,
    )
    traces = payload["data"]
    assert len(traces) == 2
    assert {trace["name"]: list(zip(trace["x"], trace["y"], strict=True)) for trace in traces} == {
        "west": [(11, 101), (33, -303)], "east": [(22, 202), (44, 404)],
    }
    assert len({trace["marker"]["color"] for trace in traces}) == 2
    assert payload["layout"]["showlegend"] is True


def test_bubble_size_follows_mapped_field_not_coordinate_magnitude(tmp_path: Path) -> None:
    payload, _ = _render_plotly(
        [{"x": 800, "y": 9, "population": 1}, {"x": 20, "y": 4, "population": 25},
         {"x": 300, "y": 1, "population": 9}],
        ChartSpec(kind="bubble", x="x", y="y", size="population"), tmp_path,
    )
    assert len(payload["data"]) == 1
    trace = payload["data"][0]
    assert trace["mode"] == "markers"
    assert list(zip(trace["x"], trace["y"], strict=True)) == [(800, 9), (20, 4), (300, 1)]
    sizes = dict(zip(trace["x"], trace["marker"]["size"], strict=True))
    # Allow diameter or area scaling, but not a constant or row-index size.
    assert 0 < sizes[800] < sizes[300] < sizes[20]


def test_heatmap_intensities_match_both_category_axes_including_zero(tmp_path: Path) -> None:
    payload, _ = _render_plotly(
        [{"day": "Wed", "team": "South", "intensity": -6},
         {"day": "Mon", "team": "North", "intensity": 0},
         {"day": "Wed", "team": "North", "intensity": 14},
         {"day": "Mon", "team": "South", "intensity": 3.5}],
        ChartSpec(kind="heatmap", x="day", y="team", color="intensity"), tmp_path,
    )
    assert len(payload["data"]) == 1
    trace = payload["data"][0]
    if trace["type"] == "heatmap":
        assert len(trace["x"]) == len(set(trace["x"])) == 2
        assert len(trace["y"]) == len(set(trace["y"])) == 2
        cells = {
            (x, y): intensity
            for y, row in zip(trace["y"], trace["z"], strict=True)
            for x, intensity in zip(trace["x"], row, strict=True)
        }
    else:
        # A sparse square-marker representation avoids an unbounded dense grid.
        assert (trace["type"], trace["mode"]) == ("scatter", "markers")
        assert trace["marker"]["symbol"] == "square"
        assert trace["marker"]["colorscale"]
        cells = {(x, y): intensity for x, y, intensity in zip(
            trace["x"], trace["y"], trace["marker"]["color"], strict=True,
        )}
    assert cells == {("Wed", "South"): -6, ("Mon", "North"): 0,
                     ("Wed", "North"): 14, ("Mon", "South"): 3.5}


def test_table_cells_and_headers_are_escaped_without_transposing_rows(tmp_path: Path) -> None:
    payload, page = _render_plotly(
        [{"name <b>": '<img src=x onerror="alert(1)"> & "quoted"', "score": 12},
         {"name <b>": "plain & simple"}],
        ChartSpec(kind="table"), tmp_path,
    )
    assert len(payload["data"]) == 1
    trace = payload["data"][0]
    assert trace["type"] == "table"
    assert trace["header"]["values"] == ["name &lt;b&gt;", "score"]
    assert trace["cells"]["values"] == [
        ["&lt;img src=x onerror=&quot;alert(1)&quot;&gt; &amp; &quot;quoted&quot;", "plain &amp; simple"],
        ["12", ""],
    ]
    assert '<img src=x onerror="alert(1)">' not in page.source


def test_dark_theme_has_dark_plot_and_paper_with_readable_foreground(tmp_path: Path) -> None:
    rows = [{"label": "one", "amount": 8}]
    light, _ = _render_plotly(rows, ChartSpec(x="label", y="amount", theme="light"), tmp_path)
    dark, _ = _render_plotly(rows, ChartSpec(x="label", y="amount", theme="dark"), tmp_path)
    dark_layout, light_layout = dark["layout"], light["layout"]
    for key in ("paper_bgcolor", "plot_bgcolor"):
        assert sum(to_rgb(dark_layout[key])) / 3 < 0.2
        assert sum(to_rgb(light_layout[key])) / 3 > 0.8
    assert sum(to_rgb(dark_layout["font"]["color"])) / 3 > 0.8
    assert sum(to_rgb(light_layout["font"]["color"])) / 3 < 0.3
    assert dark["data"][0]["y"] == light["data"][0]["y"] == [8]


def test_self_contained_html_embeds_runtime_without_script_or_stylesheet_dependencies(tmp_path: Path) -> None:
    payload, page = _render_plotly(
        [{"label": "offline", "amount": 17}], ChartSpec(x="label", y="amount"), tmp_path,
    )
    assert page.dependencies == []
    executable = [script.text for script in page.scripts
                  if script.attributes.get("type", "") not in {"application/json", "application/ld+json"}]
    assert any("Plotly" in script and len(script) > 100_000 for script in executable), "Missing inline runtime"
    assert any("Plotly.newPlot" in script for script in executable), "Embedded data is never rendered"
    assert payload["data"][0]["x"] == ["offline"]
    assert payload["data"][0]["y"] == [17]


def test_closing_script_title_remains_data_and_cannot_add_executable_scripts(tmp_path: Path) -> None:
    attack = '</script><script>globalThis.__deepviz_title_attack__=true</script>'
    rows = [{"label": "safe", "amount": 5}]
    _, clean_page = _render_plotly(rows, ChartSpec(x="label", y="amount", title="Control"), tmp_path)
    payload, page = _render_plotly(
        rows, ChartSpec(x="label", y="amount", title=attack, description=attack), tmp_path,
    )
    assert attack not in page.source
    assert "".join(page.title) == attack
    assert unescape(payload["layout"]["title"]["text"]) == attack
    assert [script.attributes for script in page.scripts] == [script.attributes for script in clean_page.scripts]
    for script in page.scripts:
        if script.attributes.get("type") == "application/json":
            assert "</script" not in script.text.lower()
        else:
            assert "__deepviz_title_attack__" not in script.text
