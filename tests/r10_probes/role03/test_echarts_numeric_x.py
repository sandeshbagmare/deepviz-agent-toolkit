"""Portable strict regressions; existing matrix assertions are deliberately untouched."""
from __future__ import annotations

import copy
import json
from html.parser import HTMLParser
from pathlib import Path

import pytest
from echarts_coordinate_oracle import assert_native_coordinates, fixture_rows

from deepviz.models import ChartSpec
from deepviz.render import render


class NativePayload(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_payload = False
        self.bodies: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("id") == "deepviz-data":
            assert attributes.get("type") == "application/json"
            self.in_payload = True
            self.bodies.append("")

    def handle_endtag(self, tag) -> None:
        if tag == "script":
            self.in_payload = False

    def handle_data(self, data) -> None:
        if self.in_payload:
            self.bodies[-1] += data


def rendered(rows, kind, tmp_path, *, group=None, theme="light"):
    spec = ChartSpec(kind=kind, title=f"strict {kind} coordinates", x="x", y="y", color=group,
                     aggregation="none", max_points=10, width=640, height=400, theme=theme)
    artifact = render(rows, spec, engine="echarts", output_dir=tmp_path)
    assert artifact.engine == "echarts" and artifact.input_count == len(rows)
    assert artifact.output_count == len(rows) and artifact.strategy == "none"
    paths = [Path(path) for path in artifact.paths]
    manifest = json.loads(next(path for path in paths if path.name == "manifest.json").read_text("utf-8"))
    parser = NativePayload()
    parser.feed(next(path for path in paths if path.suffix == ".html").read_text("utf-8"))
    assert len(parser.bodies) == 1
    assert json.loads(parser.bodies[0]) == manifest["native_specs"]
    assert len(manifest["native_specs"]) == 1
    assert manifest["charts"][0]["records"] == rows, "bounded source records were changed"
    return manifest["native_specs"][0]


@pytest.mark.parametrize("kind", ["line", "area"])
@pytest.mark.parametrize("axis", ["value", "category", "time"])
@pytest.mark.parametrize("grouped", [False, True], ids=["single", "grouped"])
def test_literal_domain_and_group_coordinates(kind, axis, grouped, tmp_path):
    rows = fixture_rows(axis, grouped=grouped)
    group = "cohort" if grouped else None
    payload = rendered(rows, kind, tmp_path, group=group, theme="dark" if grouped else "light")
    assert_native_coordinates(payload, rows, kind=kind, axis=axis, group=group)


@pytest.mark.parametrize("kind", ["line", "area"])
def test_exact_duplicate_multiplicity_is_preserved(kind, tmp_path):
    rows = fixture_rows("value")
    rows.insert(1, rows[0].copy())
    payload = rendered(rows, kind, tmp_path)
    assert_native_coordinates(payload, rows, kind=kind, axis="value")
    payload["series"][0]["data"].pop(0)
    with pytest.raises(AssertionError, match="multiplicity"):
        assert_native_coordinates(payload, rows, kind=kind, axis="value")


@pytest.mark.parametrize("kind", ["line", "area"])
@pytest.mark.parametrize("damage", [
    "category_axis", "stringified_x", "changed_y", "dropped_point", "duplicated_point", "swapped_y",
    "boolean_x", "extra_coordinate", "wrong_geometry",
])
def test_oracle_rejects_numeric_regressions_without_weakening_values(kind, damage, tmp_path):
    rows = fixture_rows("value")
    payload = copy.deepcopy(rendered(rows, kind, tmp_path))
    points = payload["series"][0]["data"]
    if damage == "category_axis":
        payload["xAxis"] = {"type": "category", "data": [str(row["x"]) for row in rows]}
        for point in points:
            point[0] = str(point[0])
    elif damage == "stringified_x":
        points[0][0] = str(points[0][0])
    elif damage == "changed_y":
        points[0][1] += 0.25
    elif damage == "dropped_point":
        points.pop()
    elif damage == "duplicated_point":
        points.append(points[0].copy())
    elif damage == "swapped_y":
        points[0][1], points[1][1] = points[1][1], points[0][1]
    elif damage == "boolean_x":
        points[0][0] = True
    elif damage == "extra_coordinate":
        points[0].append(999)
    elif kind == "area":
        payload["series"][0].pop("areaStyle")
    else:
        payload["series"][0]["areaStyle"] = {}
    with pytest.raises(AssertionError):
        assert_native_coordinates(payload, rows, kind=kind, axis="value")


@pytest.mark.parametrize("kind", ["line", "area"])
def test_oracle_rejects_changed_group_membership_even_when_global_pairs_match(kind, tmp_path):
    rows = fixture_rows("value", grouped=True)
    payload = rendered(rows, kind, tmp_path, group="cohort")
    assert_native_coordinates(payload, rows, kind=kind, axis="value", group="cohort")
    payload["series"][0]["data"], payload["series"][1]["data"] = (
        payload["series"][1]["data"], payload["series"][0]["data"],
    )
    with pytest.raises(AssertionError, match="group"):
        assert_native_coordinates(payload, rows, kind=kind, axis="value", group="cohort")


@pytest.mark.parametrize("axis", ["category", "time"])
def test_oracle_rejects_erasing_category_time_discriminator(axis, tmp_path):
    rows = fixture_rows(axis)
    payload = rendered(rows, "line", tmp_path)
    assert_native_coordinates(payload, rows, kind="line", axis=axis)
    payload["xAxis"]["type"] = "time" if axis == "category" else "category"
    with pytest.raises(AssertionError, match="domain"):
        assert_native_coordinates(payload, rows, kind="line", axis=axis)
