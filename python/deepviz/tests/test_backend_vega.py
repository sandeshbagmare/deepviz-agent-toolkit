"""Vega-Lite acceptance checks through the public renderer and real vl-convert."""
from __future__ import annotations

import importlib
import importlib.util
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest
import vl_convert as vlc
from matplotlib.colors import to_rgb

from deepviz.models import Artifact


def _render(data: Any, spec: dict[str, Any], tmp_path: Path) -> tuple[Artifact, dict, ET.Element]:
    assert importlib.util.find_spec("deepviz.render"), "The public deepviz.render module is missing"
    render = importlib.import_module("deepviz.render").render
    artifact = render(data, spec, engine="vega", output_dir=tmp_path)
    assert isinstance(artifact, Artifact)
    assert artifact.engine == "vega"
    assert artifact.mime_type == "image/svg+xml"
    paths = [Path(path) for path in artifact.paths]
    assert paths and all(path.is_file() and path.is_relative_to(tmp_path) for path in paths)
    svg_paths = [path for path in paths if path.suffix == ".svg"]
    assert len(svg_paths) == 1
    root = ET.fromstring(svg_paths[0].read_text(encoding="utf-8"))
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    manifest_path, = [path for path in paths if path.name == "manifest.json"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["engine"] == "vega"
    assert manifest["warnings"] == artifact.warnings
    for native in manifest["native_specs"]:
        compiled = vlc.vegalite_to_vega(native)
        assert compiled["$schema"].startswith("https://vega.github.io/schema/vega/")
        ET.fromstring(vlc.vega_to_svg(compiled))
    return artifact, manifest, root


def _values(native: dict, channel: str) -> list[Any]:
    field = native["encoding"][channel]["field"]
    return [row[field] for row in native["data"]["values"]]


def _channel_title(native: dict, channel: str) -> str:
    encoding = native["encoding"][channel]
    return encoding.get("title", encoding["field"])


def _labels(root: ET.Element, role: str) -> list[dict[str, str]]:
    return [dict(part.split(": ", 1) for part in element.attrib["aria-label"].split("; "))
            for element in root.iter() if element.get("aria-roledescription") == role
            and "aria-label" in element.attrib]


def _text(root: ET.Element) -> set[str]:
    return {"".join(element.itertext()) for element in root.iter()
            if element.tag == "{http://www.w3.org/2000/svg}text"}


def _scene_marks(node: Any, marktype: str) -> list[dict]:
    if isinstance(node, dict):
        if node.get("marktype") == marktype and node.get("role") == "mark":
            return [node]
        return [mark for value in node.values() for mark in _scene_marks(value, marktype)]
    if isinstance(node, list):
        return [mark for value in node for mark in _scene_marks(value, marktype)]
    return []


def _luminance(color: str) -> float:
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
              for value in to_rgb(color)]
    return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear, strict=True))


def test_categorical_bars_keep_exact_labels_signed_values_and_zero(tmp_path):
    rows = [{"code": "001", "margin": -7.25}, {"code": "1e3", "margin": 0},
            {"code": "FY24 & East", "margin": 14.5}]
    artifact, manifest, svg = _render(rows, {"kind": "bar", "x": "code", "y": "margin"}, tmp_path)
    native = manifest["native_specs"][0]
    assert native["encoding"]["x"]["type"] == "nominal"
    assert native["encoding"]["y"]["type"] == "quantitative"
    assert _values(native, "x") == ["001", "1e3", "FY24 & East"]
    assert _values(native, "y") == [-7.25, 0, 14.5]
    assert {"001", "1e3", "FY24 & East"} <= _text(svg)
    labels = _labels(svg, "bar")
    assert [(row["code"], float(row["margin"])) for row in labels] == [
        ("001", -7.25), ("1e3", 0), ("FY24 & East", 14.5),
    ]
    assert (artifact.input_count, artifact.output_count) == (3, 3)
    assert not artifact.warnings


def test_iso_date_line_uses_temporal_spacing_instead_of_category_slots(tmp_path):
    rows = [{"day": "2026-01-31", "sales": 31}, {"day": "2026-01-01", "sales": 1},
            {"day": "2026-01-02", "sales": 2}]
    _, manifest, svg = _render(rows, {"kind": "line", "x": "day", "y": "sales"}, tmp_path)
    native = manifest["native_specs"][0]
    assert native["encoding"]["x"]["type"] == "temporal"
    assert native["encoding"]["y"]["type"] == "quantitative"
    assert _values(native, "x") == ["2026-01-31", "2026-01-01", "2026-01-02"]
    scene = vlc.vegalite_to_scenegraph(native)
    line, = _scene_marks(scene, "line")
    points = line["items"]
    assert len(points) == 3
    positions = [point["x"] for point in points]
    assert positions == sorted(positions)
    assert (positions[2] - positions[1]) / (positions[1] - positions[0]) == pytest.approx(29)
    assert any("time scale" in element.get("aria-label", "").lower()
               or "utc scale" in element.get("aria-label", "").lower() for element in svg.iter())


def test_bubble_coordinates_size_and_series_have_distinct_correct_types(tmp_path):
    rows = [{"distance": 2, "cost": 17, "population": 4, "region": "North"},
            {"distance": 10, "cost": 3, "population": 36, "region": "South"}]
    _, manifest, svg = _render(rows, {"kind": "bubble", "x": "distance", "y": "cost",
                                    "size": "population", "color": "region"}, tmp_path)
    native = manifest["native_specs"][0]
    assert {name: native["encoding"][name]["type"] for name in ("x", "y", "size", "color")} == {
        "x": "quantitative", "y": "quantitative", "size": "quantitative", "color": "nominal",
    }
    assert _values(native, "x") == [2, 10]
    assert _values(native, "y") == [17, 3]
    assert _values(native, "size") == [4, 36]
    assert _values(native, "color") == ["North", "South"]
    labels = _labels(svg, "point")
    assert {(float(row["distance"]), float(row["cost"]), float(row[_channel_title(native, "size")]),
             row[_channel_title(native, "color")]) for row in labels} == {
        (2, 17, 4, "North"), (10, 3, 36, "South"),
    }


def test_heatmap_colors_encode_measure_not_row_count_or_category_number(tmp_path):
    rows = [{"day": "Mon", "team": "West", "revenue": 3.5},
            {"day": "Tue", "team": "West", "revenue": 19},
            {"day": "Mon", "team": "East", "revenue": 41}]
    _, manifest, svg = _render(rows, {"kind": "heatmap", "x": "day", "y": "team",
                                    "color": "revenue"}, tmp_path)
    native = manifest["native_specs"][0]
    assert [native["encoding"][name]["type"] for name in ("x", "y", "color")] == [
        "nominal", "nominal", "quantitative",
    ]
    assert _values(native, "y") == ["West", "West", "East"]
    assert _values(native, "color") == [3.5, 19, 41]
    labels = _labels(svg, "rect")
    assert {(row["day"], row["team"], float(row[_channel_title(native, "color")]))
            for row in labels} == {("Mon", "West", 3.5), ("Tue", "West", 19), ("Mon", "East", 41)}
    assert {"Mon", "Tue", "West", "East"} <= _text(svg)


def test_boxplot_renders_group_quartiles_medians_and_outlier_without_aggregation(tmp_path):
    rows = [{"cohort": group, "score": value} for group, values in [
        ("Control", [0, 2, 4, 6, 100]), ("Treated", [10, 12, 14, 16, 18]),
    ] for value in values]
    artifact, manifest, svg = _render(rows, {"kind": "box", "x": "cohort", "y": "score",
                                           "aggregation": "none"}, tmp_path)
    native = manifest["native_specs"][0]
    assert _values(native, "y") == [0, 2, 4, 6, 100, 10, 12, 14, 16, 18]
    boxes = _labels(svg, "box")
    assert len(boxes) == 2
    statistics = {row["cohort"]: tuple(float(next(value for key, value in row.items()
                                                if key.startswith(prefix)))
                                      for prefix in ("Min of ", "Q1 of ", "Median of ", "Q3 of ", "Max of "))
                  for row in boxes}
    assert statistics == {"Control": (0, 2, 4, 6, 100), "Treated": (10, 12, 14, 16, 18)}
    assert any(row["cohort"] == "Control" and float(row["score"]) == 100
               for row in _labels(svg, "point"))
    assert artifact.output_count == 10
    assert manifest["charts"][0]["rendered_kind"] == "box"


def test_violin_estimates_separate_densities_with_modes_at_each_group_center(tmp_path):
    rows = [{"cohort": group, "score": value} for group, values in [
        ("Control", [0, 1, 2, 3, 4]), ("Treated", [20, 21, 22, 23, 24]),
    ] for value in values]
    artifact, manifest, svg = _render(rows, {"kind": "violin", "x": "cohort", "y": "score",
                                           "aggregation": "none"}, tmp_path)
    native = manifest["native_specs"][0]
    assert manifest["charts"][0]["rendered_kind"] == "violin"
    assert not any("fallback" in warning.lower() for warning in artifact.warnings)
    assert len(native["data"]["values"]) == 10
    density, = [transform for transform in native["transform"] if "density" in transform]
    assert density.get("groupby"), "One global KDE is not a grouped violin plot"
    assert sorted({row[density["groupby"][0]] for row in native["data"]["values"]}) == [
        "Control", "Treated",
    ]
    areas = _scene_marks(vlc.vegalite_to_scenegraph(native), "area")
    assert len(areas) == 2
    modes = []
    for area in areas:
        samples = [dict(part.split(": ", 1) for part in item["description"].split("; "))
                   for item in area["items"]]
        assert len(samples) >= 20
        pairs = [(float(sample[_channel_title(native, "x")]), float(sample[_channel_title(native, "y")]))
                 for sample in samples]
        assert all(math.isfinite(density_value) and density_value >= 0 for density_value, _ in pairs)
        modes.append(max(pairs)[1])
    assert sorted(modes) == pytest.approx([2, 22], abs=0.3)
    assert {"Control", "Treated"} <= _text(svg)
    assert len(_labels(svg, "area mark")) == 2


def test_dark_theme_reaches_svg_background_axes_title_and_legend(tmp_path):
    _, manifest, svg = _render([{"label": "North", "value": 12, "region": "East"}], {
        "kind": "bar", "x": "label", "y": "value", "color": "region",
        "theme": "dark", "title": "Readable dark chart",
    }, tmp_path)
    native = manifest["native_specs"][0]
    background = native["background"]
    assert _luminance(background) < 0.05
    background_rects = [element for element in svg
                        if element.tag.endswith("}rect") and element.get("fill") == background]
    assert background_rects, "The exported SVG, not just the manifest, needs the dark background"
    labels = [element for element in svg.iter() if element.tag.endswith("}text") and element.text]
    assert {"North", "East", "Readable dark chart"} <= _text(svg)
    assert labels
    assert all((_luminance(element.attrib["fill"]) + 0.05) / (_luminance(background) + 0.05) >= 4.5
               for element in labels)


def test_exported_svg_uses_requested_outer_dimensions(tmp_path):
    _, _, svg = _render([{"label": "A", "value": 3}], {
        "kind": "bar", "x": "label", "y": "value", "width": 720, "height": 420,
    }, tmp_path)
    assert float(svg.attrib["width"].removesuffix("px")) == pytest.approx(720)
    assert float(svg.attrib["height"].removesuffix("px")) == pytest.approx(420)
    assert [float(value) for value in svg.attrib["viewBox"].split()] == [0, 0, 720, 420]


def test_untrusted_title_field_and_category_are_inert_svg_text(tmp_path):
    attack = '</script><script>alert("vega")</script>&'
    field = "label </script><script>alert(1)</script>"
    _, manifest, svg = _render([{field: attack, "amount": 17}], {
        "kind": "bar", "x": field, "y": "amount", "title": attack, "description": attack,
    }, tmp_path)
    native = manifest["native_specs"][0]
    assert native["title"] == attack
    assert _values(native, "x") == [attack]
    bar, = _labels(svg, "bar")
    assert bar[field] == attack
    assert float(bar["amount"]) == 17
    for element in svg.iter():
        assert element.tag.rsplit("}", 1)[-1].lower() not in {
            "script", "image", "foreignobject", "iframe", "object", "embed",
        }
        assert not any(key.rsplit("}", 1)[-1].lower().startswith("on") for key in element.attrib)
        assert not any(value.lstrip().lower().startswith("javascript:") for value in element.attrib.values())


def test_radar_fallback_is_named_in_artifact_and_manifest_warnings(tmp_path):
    rows = [{"metric": "Latency", "score": 37}, {"metric": "Throughput", "score": 84},
            {"metric": "Reliability", "score": 61}]
    artifact, manifest, svg = _render(rows, {
        "kind": "radar", "x": "metric", "y": "score",
    }, tmp_path)
    chart, = manifest["charts"]
    assert chart["requested_kind"] == "radar"
    assert chart["rendered_kind"] == "line"
    assert any(all(word in warning.lower() for word in ("fallback", "radar", "line"))
               for warning in artifact.warnings)
    assert _values(manifest["native_specs"][0], "y") == [37, 84, 61]
    assert {"Latency", "Throughput", "Reliability"} <= _text(svg)
    line, = _scene_marks(vlc.vegalite_to_scenegraph(manifest["native_specs"][0]), "line")
    assert len(line["items"]) == 3


def test_dashboard_normalizes_each_child_data_path_and_mapping_independently(tmp_path):
    data = {"revenue": {"rows": [{"product": "Widget", "usd": 7}, {"product": "Gadget", "usd": 19}]},
            "quality": {"rows": [{"team": "North", "rate": 0.91}, {"team": "South", "rate": 0.82},
                                 {"team": "West", "rate": 0.76}]}}
    artifact, manifest, svg = _render(data, {"kind": "dashboard", "title": "Independent sources", "charts": [
        {"kind": "bar", "title": "Revenue", "x": "product", "y": "usd", "data_path": "revenue.rows"},
        {"kind": "bar", "title": "Quality", "x": "team", "y": "rate", "data_path": "quality.rows"},
    ]}, tmp_path)
    revenue, quality = manifest["native_specs"]
    assert _values(revenue, "x") == ["Widget", "Gadget"]
    assert _values(revenue, "y") == [7, 19]
    assert _values(quality, "x") == ["North", "South", "West"]
    assert _values(quality, "y") == [0.91, 0.82, 0.76]
    assert (artifact.input_count, artifact.output_count) == (3, 5)
    labels = _labels(svg, "bar")
    assert {(row["product"], float(row["usd"])) for row in labels if "product" in row} == {
        ("Widget", 7), ("Gadget", 19),
    }
    assert {(row["team"], float(row["rate"])) for row in labels if "team" in row} == {
        ("North", 0.91), ("South", 0.82), ("West", 0.76),
    }


def test_dashboard_manifest_preserves_standalone_child_schemas_for_recompilation(tmp_path):
    _, manifest, svg = _render({"first": [{"category": "A", "amount": 8}],
                              "second": [{"category": "B", "other": 13}]}, {
        "kind": "dashboard", "title": "Composition", "charts": [
            {"kind": "bar", "title": "First panel", "x": "category", "y": "amount",
             "theme": "dark", "data_path": "first"},
            {"kind": "bar", "title": "Second panel", "x": "category", "y": "other", "data_path": "second"},
        ],
    }, tmp_path)
    children = manifest["native_specs"]
    assert len(children) == 2
    for child, expected_title in zip(children, ("First panel", "Second panel"), strict=True):
        assert child.get("$schema", "").startswith("https://vega.github.io/schema/vega-lite/")
        assert child.get("$schema", "").endswith(".json")
        standalone = ET.fromstring(vlc.vegalite_to_svg(child))
        assert expected_title in _text(standalone)
    assert children[0]["background"] != children[1]["background"]
    assert {"First panel", "Second panel", "Composition"} <= _text(svg)
