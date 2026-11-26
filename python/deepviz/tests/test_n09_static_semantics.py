"""Independent known-value static-output oracles; no production monkeypatches.

Set N09_ARTIFACT_ROOT to preserve an image gallery outside pytest's temporary
directories. This file intentionally exercises the public renderer as well as
the actual Matplotlib artists backing its SVG and PNG outputs.
"""

from __future__ import annotations

import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pytest
from matplotlib.colors import to_rgba
from PIL import Image, ImageStat

from deepviz.engines import matplotlib_figure
from deepviz.models import ChartSpec
from deepviz.normalize import normalize
from deepviz.render import render

KINDS = ("bar", "line", "scatter", "area", "pie", "heatmap", "dashboard")
THEMES = ("light", "dark")
STATIC_ENGINES = ("matplotlib", "vega")
SVG_NS = "{http://www.w3.org/2000/svg}"
HOSTILE = '</script><script>window.N09_ATTACK=1</script><img src=x onerror="N09_ATTACK=2">& Ω $x$'


def example(kind: str, theme: str = "light") -> tuple[list[dict], ChartSpec]:
    """Known measurements are intentionally unequal, include zero, and are ordered."""
    rows = [
        {"category": "Alpha", "t": 0, "value": 2, "region": "East"},
        {"category": "Beta", "t": 1, "value": 0, "region": "East"},
        {"category": "Gamma", "t": 2, "value": 6, "region": "East"},
        {"category": "Alpha", "t": 0, "value": 5, "region": "West"},
        {"category": "Beta", "t": 1, "value": 3, "region": "West"},
        {"category": "Gamma", "t": 2, "value": 1, "region": "West"},
    ]
    settings = dict(
        kind=kind, theme=theme, title=f"N09 {kind}: known values ({theme})",
        x="category" if kind == "bar" else "t", y="value", color="region",
        aggregation="none", width=800, height=500,
    )
    if kind == "pie":
        rows = [{"category": name, "value": value} for name, value in zip("ABC", [1, 3, 4], strict=True)]
        settings.update(x="category", color=None)
    if kind == "heatmap":
        rows = [
            {"site": "North", "day": "Mon", "intensity": 1},
            {"site": "South", "day": "Mon", "intensity": 2},
            {"site": "North", "day": "Tue", "intensity": 3},
            {"site": "South", "day": "Tue", "intensity": 4},
        ]
        settings.update(x="site", y="day", color="intensity")
    if kind == "dashboard":
        settings.update(
            width=1100, height=800, columns=2,
            charts=[
                {"kind": "bar", "x": "category", "title": "Grouped bars: East 2,0,6 / West 5,3,1"},
                {"kind": "line", "title": "Lines: East 2,0,6 / West 5,3,1"},
                {"kind": "scatter", "title": "Six measured points"},
                {"kind": "area", "title": "Independent areas, not cumulative totals"},
            ],
        )
    return rows, ChartSpec(**settings)


def svg_text(svg: str) -> str:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return "".join(ET.fromstring(svg, parser=parser).itertext())


def assert_svg_inert(svg: str) -> ET.Element:
    root = ET.fromstring(svg)
    assert root.tag == SVG_NS + "svg"
    for element in root.iter():
        assert element.tag.rsplit("}", 1)[-1] not in {"script", "foreignObject"}
        assert not any(key.rsplit("}", 1)[-1].lower().startswith("on") for key in element.attrib)
        assert not any(str(value).strip().lower().startswith("javascript:") for value in element.attrib.values())
    return root


@pytest.mark.parametrize("kind", KINDS[:-1])
@pytest.mark.parametrize("theme", THEMES)
def test_n09_matplotlib_artist_measurements(kind: str, theme: str) -> None:
    rows, spec = example(kind, theme)
    normalized = normalize(rows, spec)
    figure, warnings = matplotlib_figure([(normalized.records, spec)])
    try:
        figure.canvas.draw()
        axis = figure.axes[0]
        assert not warnings
        assert figure.get_facecolor() == to_rgba("#171b26" if theme == "dark" else "#ffffff")
        assert axis.get_title() == spec.title
        if kind == "bar":
            assert [patch.get_height() for patch in axis.patches] == [2, 0, 6, 5, 3, 1]
            assert [tick.get_text() for tick in axis.get_xticklabels()] == ["Alpha", "Beta", "Gamma"]
            assert axis.get_ylim()[0] <= 0 < axis.get_ylim()[1]
        elif kind in {"line", "area"}:
            assert len(axis.lines) == 2
            assert list(axis.lines[0].get_xdata()) == [0, 1, 2]
            assert list(axis.lines[0].get_ydata()) == [2, 0, 6]
            assert list(axis.lines[1].get_ydata()) == [5, 3, 1]
            if kind == "area":
                assert len(axis.collections) == 2
                # A series must not acquire the other region's measurement.
                assert max(axis.collections[0].get_paths()[0].vertices[:, 1]) == 6
                assert max(axis.collections[1].get_paths()[0].vertices[:, 1]) == 5
        elif kind == "scatter":
            assert len(axis.collections) == 2
            np.testing.assert_array_equal(axis.collections[0].get_offsets(), [[0, 2], [1, 0], [2, 6]])
            np.testing.assert_array_equal(axis.collections[1].get_offsets(), [[0, 5], [1, 3], [2, 1]])
        elif kind == "pie":
            assert [patch.theta2 - patch.theta1 for patch in axis.patches] == pytest.approx([45, 135, 180])
            assert [text.get_text() for text in axis.texts] == ["A", "B", "C"]
        else:
            assert len(figure.axes) == 2, "Heat intensity requires a visible numeric color scale"
            np.testing.assert_array_equal(axis.collections[0].get_array(), [1, 2, 3, 4])
            np.testing.assert_array_equal(axis.collections[0].get_offsets(), [[0, 0], [1, 0], [0, 1], [1, 1]])
            assert [tick.get_text() for tick in axis.get_xticklabels()] == ["North", "South"]
            assert [tick.get_text() for tick in axis.get_yticklabels()] == ["Mon", "Tue"]
        if kind in {"bar", "line", "area", "scatter"}:
            assert [text.get_text() for text in axis.get_legend().get_texts()] == ["East", "West"]
            assert axis.get_xlabel() == spec.x and axis.get_ylabel() == spec.y
    finally:
        figure.clear()


@pytest.mark.parametrize("engine", STATIC_ENGINES)
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("kind", KINDS)
def test_n09_public_static_gallery(engine: str, theme: str, kind: str, tmp_path: Path) -> None:
    rows, spec = example(kind, theme)
    root = Path(os.environ.get("N09_ARTIFACT_ROOT", str(tmp_path))) / f"{engine}-{kind}-{theme}"
    artifact = render(rows, spec, engine=engine, output_dir=root)
    assert artifact.engine == engine
    assert artifact.input_count == len(rows)
    assert artifact.output_count == len(rows) * (4 if kind == "dashboard" else 1)
    paths = {Path(path).suffix: Path(path) for path in artifact.paths}
    manifest = json.loads(paths[".json"].read_text(encoding="utf-8"))
    assert len(manifest["charts"]) == (4 if kind == "dashboard" else 1)
    svg = paths[".svg"].read_text(encoding="utf-8")
    svg_root = assert_svg_inert(svg)
    assert spec.title in svg_text(svg)
    assert int(float(svg_root.attrib["width"].removesuffix("pt"))) > 200
    assert int(float(svg_root.attrib["height"].removesuffix("pt"))) > 150
    if engine == "vega":
        marks = [node for node in svg_root.iter() if node.attrib.get("role") == "graphics-symbol"]
        labels = " ".join(node.attrib.get("aria-label", "") for node in marks)
        if kind in {"bar", "line", "scatter", "area", "dashboard"}:
            assert "East" in labels and "West" in labels
        elif kind == "heatmap":
            assert all(word in labels for word in ["North", "South", "Mon", "Tue"])
        else:
            assert all(word in labels for word in ["A", "B", "C"])
        # This PNG is explicitly a rasterization of actual public SVG, not a
        # claim that the Vega renderer itself exposes PNG as an artifact.
        import vl_convert

        raster = paths[".svg"].with_name("n09-svg-preview.png")
        raster.write_bytes(vl_convert.svg_to_png(svg))
    else:
        raster = paths[".png"]
    with Image.open(raster) as image:
        assert image.size == (spec.width, spec.height)
        background = (23, 27, 38) if theme == "dark" else (255, 255, 255)
        # SVG preserveAspectRatio may leave transparent viewport padding. Treat
        # that as transparent, not as the black invented by RGBA.convert('RGB').
        canvas = Image.new("RGBA", image.size, (*background, 255))
        canvas.alpha_composite(image.convert("RGBA"))
        rgb = canvas.convert("RGB")
        assert max(ImageStat.Stat(rgb).var) > 100
        assert rgb.getpixel((0, 0)) == background
    evidence = {
        "engine": engine, "kind": kind, "theme": theme, "expected_records": rows,
        "artifact": artifact.to_dict(), "preview": str(raster),
        "sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths.values()},
    }
    (root / "n09-evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")


class InertHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict]] = []
        self.script_bodies: list[str] = []
        self.in_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        if tag == "script":
            self.in_script = True
            self.script_bodies.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_script = False

    def handle_data(self, data: str) -> None:
        if self.in_script:
            self.script_bodies[-1] += data


@pytest.mark.parametrize("engine", [*STATIC_ENGINES, "plotly", "echarts", "antv"])
def test_n09_hostile_labels_and_output_boundaries(engine: str, tmp_path: Path) -> None:
    sentinel = tmp_path / "chart.svg"
    sentinel.write_text("user-owned sentinel", encoding="utf-8")
    rows = [{"category": HOSTILE, "value": 2, "region": HOSTILE}]
    spec = ChartSpec(kind="bar", title=HOSTILE, x="category", y="value", color="region", aggregation="none")
    first = render(rows, spec, engine=engine, output_dir=tmp_path)
    hashes = {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in first.paths}
    second = render(rows, spec, engine=engine, output_dir=tmp_path)
    assert set(first.paths).isdisjoint(second.paths)
    assert sentinel.read_text(encoding="utf-8") == "user-owned sentinel"
    for name in first.paths:
        path = Path(name)
        assert path.resolve().is_relative_to(tmp_path.resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == hashes[name]
        if path.suffix == ".svg":
            assert_svg_inert(path.read_text(encoding="utf-8"))
        elif path.suffix == ".html":
            page = InertHTML()
            page.feed(path.read_text(encoding="utf-8"))
            assert not any(key.startswith("on") for _, attrs in page.tags for key in attrs)
            assert not any(tag == "img" and attrs.get("src") == "x" for tag, attrs in page.tags)
            assert not any(body.lstrip().startswith("window.N09_ATTACK=") for body in page.script_bodies)


@pytest.mark.parametrize("engine", STATIC_ENGINES)
def test_n09_static_negative_bar_is_not_clamped(engine: str, tmp_path: Path) -> None:
    rows = [{"name": "loss", "value": -4}, {"name": "zero", "value": 0}, {"name": "gain", "value": 8}]
    spec = ChartSpec(kind="bar", x="name", y="value", aggregation="none", title="Loss, zero, gain")
    artifact = render(rows, spec, engine=engine, output_dir=tmp_path)
    manifest_path = next(Path(path) for path in artifact.paths if path.endswith("manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert [row["value"] for row in manifest["charts"][0]["records"]] == [-4, 0, 8]
    if engine == "vega":
        svg_path = next(Path(path) for path in artifact.paths if path.endswith(".svg"))
        root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
        labels = " ".join(node.attrib.get("aria-label", "") for node in root.iter()).replace("\N{MINUS SIGN}", "-")
        assert "-4" in labels and "gain" in labels and "loss" in labels
    else:
        figure, _ = matplotlib_figure([(rows, spec)])
        try:
            assert [patch.get_height() for patch in figure.axes[0].patches] == [-4, 0, 8]
            assert figure.axes[0].get_ylim()[0] < -4 < 0 < 8 < figure.axes[0].get_ylim()[1]
        finally:
            figure.clear()
