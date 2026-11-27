"""Role06 candidate oracle, never edits the existing acceptance matrix."""
from __future__ import annotations

import copy
import json
from html.parser import HTMLParser
from pathlib import Path

import pytest

from deepviz.render import render


class Document(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.containers: list[str] = []
        self.data_parts: list[str] = []
        self.in_data = False
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("role") == "img":
            self.containers.append(str(attributes["id"]))
        if tag == "script" and attributes.get("id") == "deepviz-data":
            self.in_data = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_data = False

    def handle_data(self, data: str) -> None:
        if self.in_data:
            self.data_parts.append(data)


def assert_uncolored_connected_view(payload: dict, expected: list[tuple[str, float]]) -> None:
    assert payload["type"] == "view"
    assert len(payload["children"]) == 2
    lines = [child for child in payload["children"] if child["type"] == "line"]
    points = [child for child in payload["children"] if child["type"] == "point"]
    assert len(lines) == len(points) == 1
    for child in [*lines, *points]:
        encoding = child["encode"]
        actual = [(row[encoding["x"]], row[encoding["y"]]) for row in child["data"]]
        assert actual == expected
        assert not {"sortX", "sortY", "stackY"}.intersection(item["type"] for item in child.get("transform", []))
    assert not lines[0].get("style", {}).get("fill")


@pytest.fixture
def rendered_dashboard(tmp_path: Path) -> tuple[dict, Document]:
    rows = [{"label": "A", "income": 9, "cost": 2}, {"label": "B", "income": 5, "cost": 4}]
    children = [{"kind": kind, "title": "Same title", "x": "label", "y": field}
                for kind, field in (("bar", "income"), ("line", "cost"), ("pie", "income"))]
    artifact = render(rows, {"kind": "dashboard", "charts": children, "columns": 2,
                             "aggregation": "none"}, "antv", tmp_path)
    manifest = json.loads(next(Path(path) for path in artifact.paths if path.endswith("manifest.json")).read_text(encoding="utf-8"))
    document = Document(next(Path(path) for path in artifact.paths if path.endswith(".html")).read_text(encoding="utf-8"))
    return manifest, document


def test_same_fixture_unique_containers_and_exact_child_values(rendered_dashboard: tuple[dict, Document]) -> None:
    manifest, document = rendered_dashboard
    assert len(document.containers) == len(set(document.containers)) == 3
    payloads = json.loads("".join(document.data_parts))
    assert payloads == manifest["native_specs"]
    assert payloads[0]["type"] == payloads[2]["type"] == "interval"
    for payload in (payloads[0], payloads[2]):
        assert [row[payload["encode"]["y"]] for row in payload["data"]] == [9, 5]
    assert_uncolored_connected_view(payloads[1], [("A", 2), ("B", 4)])


@pytest.mark.parametrize("mutation", ["missing-line", "missing-points", "wrong-cost", "reordered", "filled-line"])
def test_candidate_view_oracle_rejects_corruption(rendered_dashboard: tuple[dict, Document], mutation: str) -> None:
    manifest, _ = rendered_dashboard
    payload = copy.deepcopy(manifest["native_specs"][1])
    if mutation == "missing-line":
        payload["children"] = [child for child in payload["children"] if child["type"] != "line"]
    elif mutation == "missing-points":
        payload["children"] = [child for child in payload["children"] if child["type"] != "point"]
    elif mutation == "wrong-cost":
        child = next(child for child in payload["children"] if child["type"] == "line")
        child["data"][0][child["encode"]["y"]] = 999
    elif mutation == "reordered":
        child = next(child for child in payload["children"] if child["type"] == "line")
        child["data"].reverse()
    else:
        next(child for child in payload["children"] if child["type"] == "line")["style"]["fill"] = "red"
    with pytest.raises(AssertionError):
        assert_uncolored_connected_view(payload, [("A", 2), ("B", 4)])
