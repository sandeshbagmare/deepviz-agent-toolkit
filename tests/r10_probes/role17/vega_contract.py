"""Portable real-Vega dashboard checks, independent of the existing matrix.

Visible text guards reject metadata/common hidden-text substitutes; actual paint
still needs the PNG/browser inspection documented in this probe's README.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib
import io
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import patch

import vl_convert as vlc

from deepviz.models import Artifact, ChartSpec
from deepviz.render import render

NS = "{http://www.w3.org/2000/svg}"
PARENT = 'Parent Ω & </title></script><script>window.__DV_XSS__=1</script>'
CHILDREN = ("Bars & <literal>", 'Points </script><script>window.__DV_XSS__=2</script>')
ROWS = [{"label": "A", "index": 0, "value": 2},
        {"label": "B", "index": 1, "value": 8},
        {"label": "C", "index": 10, "value": 4}]
NUMBER = r"[-+0-9.eE]+"


@dataclass(frozen=True)
class Dashboard:
    artifact: Artifact
    manifest: dict[str, Any]
    composed: dict[str, Any]
    svg: str
    svg_path: Path
    html_path: Path


def assert_inert_svg(svg: str) -> ET.Element:
    root = ET.fromstring(svg)
    assert root.tag == NS + "svg"
    for node in root.iter():
        assert node.tag.rsplit("}", 1)[-1].lower() not in {
            "script", "foreignobject", "iframe", "object", "embed", "image", "style",
        }, "executable/foreign/style SVG element"
        for name, value in node.attrib.items():
            local = name.rsplit("}", 1)[-1].lower()
            assert not local.startswith("on"), "executable SVG event attribute"
            if local == "href":
                assert value.startswith("#"), "external or executable SVG reference"
    return root


def assert_visible_title(svg: str, expected: str) -> None:
    root = assert_inert_svg(svg)
    parents = {child: parent for parent in root.iter() for child in parent}
    matches = [node for node in root.iter() if node.tag == NS + "text"
               and "".join(node.itertext()) == expected]
    assert matches, f"required visible text missing: {expected!r}"
    for node in matches:
        hidden = False
        inherited: dict[str, str] = {}
        current: ET.Element | None = node
        while current is not None:
            style = dict(part.split(":", 1) for part in current.get("style", "").split(";") if ":" in part)
            styles = {key.strip().lower(): value.strip().lower() for key, value in style.items()}
            attrs = {**current.attrib, **styles}
            hidden |= attrs.get("display") == "none" or float(attrs.get("opacity", "1")) == 0
            for key in ("fill", "stroke", "fill-opacity", "stroke-opacity", "stroke-width", "font-size", "visibility"):
                if key in attrs:
                    inherited.setdefault(key, attrs[key])
            current = parents.get(current)
        hidden |= inherited.get("visibility") in {"hidden", "collapse"}
        hidden |= bool(re.fullmatch(r"0(?:\.0*)?(?:px|pt|em)?", inherited.get("font-size", "")))
        fill_paints = inherited.get("fill", "black") != "none" and float(inherited.get("fill-opacity", "1")) > 0
        stroke_paints = (inherited.get("stroke", "none") != "none"
                         and float(inherited.get("stroke-opacity", "1")) > 0
                         and float(inherited.get("stroke-width", "1")) > 0)
        hidden |= not (fill_paints or stroke_paints)
        if not hidden:
            return
    raise AssertionError(f"required text is hidden: {expected!r}")


def encode_input(form: str, spec: ChartSpec) -> tuple[Any, ChartSpec]:
    updates: dict[str, Any] = {}
    if form == "records":
        source: Any = copy.deepcopy(ROWS)
    elif form == "columns":
        source = {key: [row[key] for row in ROWS] for key in ROWS[0]}
    elif form == "nested_json":
        source = {"payload": {"rows": copy.deepcopy(ROWS)}}
        updates["data_path"] = "payload.rows"
    elif form == "graphql":
        source = {"data": {"rows": {"edges": [{"node": row} for row in copy.deepcopy(ROWS)]}}}
    elif form == "csv":
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=list(ROWS[0]))
        writer.writeheader()
        writer.writerows(ROWS)
        source = stream.getvalue()
        updates["format"] = "csv"
    else:
        raise ValueError(f"unsupported probe form: {form}")
    if updates:
        spec = spec.model_copy(update={**updates, "charts": [child.model_copy(update=updates) for child in spec.charts]})
    return source, spec


def make_dashboard(directory: Path, theme: str = "light", form: str = "records") -> Dashboard:
    spec = ChartSpec(kind="dashboard", title=PARENT, width=640, height=400, theme=theme,
                     aggregation="none", max_points=10, charts=[
                         {"kind": "bar", "title": CHILDREN[0], "x": "label", "y": "value"},
                         {"kind": "scatter", "title": CHILDREN[1], "x": "index", "y": "value"},
                     ])
    source, spec = encode_input(form, spec)
    return render_dashboard(source, spec, directory)


def render_dashboard(source: Any, spec: ChartSpec, directory: Path) -> Dashboard:
    with patch.object(vlc, "vegalite_to_svg", wraps=vlc.vegalite_to_svg) as compiler:
        artifact = render(source, spec, "vega", directory)
    assert compiler.call_count == 1, "expected one real composed compilation"
    composed = copy.deepcopy(compiler.call_args.args[0])
    paths = [Path(path) for path in artifact.paths]
    svg_path = next(path for path in paths if path.suffix == ".svg")
    html_path = next(path for path in paths if path.suffix == ".html")
    manifest_path = next(path for path in paths if path.name == "manifest.json")
    return Dashboard(artifact, json.loads(manifest_path.read_text(encoding="utf-8")), composed,
                     svg_path.read_text(encoding="utf-8"), svg_path, html_path)


def assert_native_children(manifest: dict[str, Any]) -> None:
    assert len(manifest["native_specs"]) == len(manifest["charts"]) == 2
    for native, chart, title, xfield in zip(manifest["native_specs"], manifest["charts"], CHILDREN,
                                           ("label", "index"), strict=True):
        assert native["title"] == chart["spec"]["title"] == title, "wrong child title/scope"
        assert native["encoding"]["x"]["title"] == xfield
        expected = Counter((row[xfield], row["value"]) for row in ROWS)
        actual = Counter((row[native["encoding"]["x"]["field"]], row[native["encoding"]["y"]["field"]])
                         for row in native["data"]["values"])
        assert actual == expected, "native mapped values changed"
        standalone = vlc.vegalite_to_svg(native)
        assert_visible_title(standalone, title)
        assert all("".join(node.itertext()) != PARENT for node in ET.fromstring(standalone).iter()
                   if node.tag == NS + "text"), "child unexpectedly replaced its title with parent"


def assert_geometry_values(svg: str, manifest: dict[str, Any]) -> dict[str, Any]:
    root = assert_inert_svg(svg)
    groups = {}
    for role in ("bar", "point"):
        groups[role] = [node for node in root.iter() if node.get("aria-roledescription") == role]
        assert len(groups[role]) == len(ROWS), "wrong native mark count"
        labels = [dict(part.split(": ", 1) for part in node.attrib["aria-label"].split("; ")) for node in groups[role]]
        field = "label" if role == "bar" else "index"
        actual = Counter(((item[field] if role == "bar" else float(item[field])), float(item["value"])) for item in labels)
        assert actual == Counter((row[field], row["value"]) for row in ROWS), "SVG mapped values changed"
    width, height = (manifest["native_specs"][1][name] for name in ("width", "height"))
    coords = []
    for node, row in zip(groups["point"], ROWS, strict=True):
        match = re.fullmatch(rf"translate\(({NUMBER}),({NUMBER})\)", node.attrib["transform"])
        assert match, "non-native point coordinates"
        x, y = map(float, match.groups())
        assert math.isclose(x, width * row["index"] / 10, abs_tol=1e-8), "point x geometry changed"
        assert math.isclose(y, height * (1 - row["value"] / 8), abs_tol=1e-8), "point y geometry changed"
        coords.append([x, y])
    for node, row in zip(groups["bar"], ROWS, strict=True):
        match = re.fullmatch(rf"M({NUMBER}),({NUMBER})h({NUMBER})v({NUMBER})h({NUMBER})Z", node.attrib["d"])
        assert match, "non-native bar geometry"
        _, y, bar_width, bar_height, back_width = map(float, match.groups())
        assert bar_width > 0 and back_width == -bar_width
        assert math.isclose(bar_height, height * row["value"] / 8, abs_tol=1e-8), "bar height changed"
        assert math.isclose(y + bar_height, height, abs_tol=1e-8), "bar baseline changed"
    return {"bars": len(groups["bar"]), "points": len(groups["point"]), "point_coordinates": coords}


def assert_dashboard(output: Dashboard) -> dict[str, Any]:
    assert output.artifact.engine == "vega" and output.artifact.mime_type == "image/svg+xml"
    assert (output.artifact.input_count, output.artifact.output_count) == (3, 6)
    assert output.composed["title"] == PARENT
    assert [child["title"] for child in output.composed["concat"]] == list(CHILDREN)
    assert ET.fromstring(output.svg).get("width") == "640"
    assert ET.fromstring(output.svg).get("height") == "400"
    for title in (PARENT, *CHILDREN):
        assert_visible_title(output.svg, title)
    assert_native_children(output.manifest)
    return assert_geometry_values(output.svg, output.manifest)


def make_strict(directory: Path) -> Dashboard:
    field = "label </script><script>alert(1)</script>"
    spec = ChartSpec(kind="dashboard", title=PARENT, width=640, height=400, aggregation="none", charts=[
        {"kind": "bar", "title": CHILDREN[0], "x": field, "y": "value"},
        {"kind": "scatter", "title": CHILDREN[1], "x": "index", "y": "value"},
    ])
    return render_dashboard([{field: "<img onerror=x>", "index": 1, "value": 17}], spec, directory)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    ordinary = make_dashboard(args.output / "ordinary")
    strict = make_strict(args.output / "strict")
    geometry = assert_dashboard(ordinary)
    for title in (PARENT, *CHILDREN, "label </script><script>alert(1)</script>", "<img onerror=x>"):
        assert_visible_title(strict.svg, title)
    (args.output / "composed.svg").write_text(ordinary.svg, encoding="utf-8")
    (args.output / "composed.png").write_bytes(vlc.svg_to_png(ordinary.svg))
    (args.output / "composed-payload.json").write_text(json.dumps(ordinary.composed, ensure_ascii=False, indent=2), encoding="utf-8")
    modules = [importlib.import_module(name) for name in ("deepviz.render", "deepviz.engines", "deepviz.models", "vl_convert")]
    source_git = subprocess.run(["git", "-C", str(Path(modules[0].__file__).parent), "rev-parse", "HEAD"],
                                capture_output=True, text=True, timeout=20, check=False)
    summary = {"source_sha": source_git.stdout.strip() if source_git.returncode == 0 else None,
               "python": sys.executable, "vl_convert_version": vlc.__version__, "geometry": geometry,
               "input_count": 3, "output_count": 6, "parent_title": PARENT, "child_titles": CHILDREN,
               "artifacts": {name: {"svg": str(output.svg_path.relative_to(args.output)),
                                    "html": str(output.html_path.relative_to(args.output))}
                             for name, output in (("ordinary", ordinary), ("strict", strict))},
               "loaded_modules": [{"name": module.__name__, "file": module.__file__,
                                   "sha256": hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()} for module in modules]}
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True))


if __name__ == "__main__":
    main()
