"""Real G2 regression: finite heat values must produce honest visible cells."""
from __future__ import annotations

import copy
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from deepviz import render

MAX = 1.7976931348623157e308
CASES = [
    ("negative-subnormal", [-8e-310, -6e-310, -4e-310, -2e-310]),
    ("positive-subnormal", [2e-310, 4e-310, 6e-310, 8e-310]),
    ("minimum-subnormal", [5e-324, 1e-323, 1.5e-323, 2e-323]),
    ("constant-subnormal", [-8e-310] * 4),
    ("signed-MAX", [-MAX, 0, MAX]),
    ("constant-MAX", [MAX] * 4),
    ("negative-constant-MAX", [-MAX] * 4),
    ("zero", [0] * 4),
    ("signed-ordinary", [-12, -3, 3, 12]),
    ("signed-1e308", [-1e308, 1e308]),
]


@pytest.mark.parametrize(("name", "values"), CASES, ids=[case[0] for case in CASES])
def test_finite_heatmap_real_cells_keep_values_colors_and_grid(name, values, tmp_path):
    repo = Path(__file__).resolve().parents[3]
    candidates = [repo, Path(sys.executable).resolve().parents[2]]
    tools = next((directory for directory in candidates if
                  (directory / "node_modules/playwright/package.json").is_file() and
                  (directory / "node_modules/@antv/g2/dist/g2.min.js").is_file()), None)
    if shutil.which("node") is None or tools is None:
        pytest.skip("Real G2 browser regression requires existing Node, Playwright/Chromium and G2 5.4.8; no install")
    coordinates = [("West", "North"), ("East", "North"), ("West", "South"), ("East", "South")]
    rows = [{"column": coordinate[0], "row": coordinate[1], "heat": value}
            for coordinate, value in zip(coordinates, values, strict=False)]
    original = copy.deepcopy(rows)
    artifact = render(rows, {"kind": "heatmap", "title": name, "x": "column", "y": "row", "color": "heat",
                             "aggregation": "none", "width": 960, "height": 520}, "antv", tmp_path)
    manifest = json.loads(next(Path(name) for name in artifact.paths if name.endswith("manifest.json")).read_text())
    native = manifest["native_specs"][0]
    assert rows == original == manifest["charts"][0]["records"]
    assert [row["_heat"] for row in native["data"]] == values
    assert [[row["_x"], row["_y"]] for row in native["data"]] == [list(pair) for pair in coordinates[:len(values)]]
    html = next(name for name in artifact.paths if name.endswith(".html"))
    output = tmp_path / "actual-native.json"
    subprocess.run(["node", str(repo / "tests/r45_probes/role17/native.cjs"), html, str(tools), str(output)], check=True)
    actual = json.loads(output.read_text())
    assert actual["ready"] == "resolved" and not actual["errors"] and not actual.get("harnessError")
    state = actual["state"]
    marks = state["marks"]
    # The original four strict subnormal conditions: cell count, colors, grid and actual pixel paint.
    assert len(marks) == len(values) and all(mark["box"]["width"] > 10 and mark["box"]["height"] > 10 for mark in marks)
    assert len({mark["normalizedColor"] for mark in marks}) == len(set(values))
    assert math.isfinite(state["views"][0]["layout"]["innerHeight"])
    if len(set(values)) > 1:
        assert marks[0]["normalizedColor"] == "#ffffd9"
        assert marks[-1]["normalizedColor"] == "#081d58"
    grid = [(0, 0), (1, 0), (0, 1), (1, 1)][:len(values)]
    for i, mark in enumerate(marks):
        for j, other in enumerate(marks):
            for axis, component in [("x", 0), ("y", 1)]:
                difference = mark["box"][axis] - other["box"][axis]
                assert (difference > 0) - (difference < 0) == (grid[i][component] > grid[j][component]) - (grid[i][component] < grid[j][component])
    assert len({tuple(pixel) for pixel in state["pixels"]}) == len(set(values))
    labels = [label for label in state["ticks"] if label.get("text") not in [None, "_heat"]]
    ticks = [float(str(label["text"]).replace("−", "-").replace(",", "")) for label in labels]
    assert ticks and all(math.isfinite(value) for value in ticks)
    assert min(ticks) <= min(values) <= max(values) <= max(ticks)
    assert all(label["box"]["x"] >= 0 and label["box"]["y"] >= 0 and
               label["box"]["x"] + label["box"]["width"] <= state["width"] and
               label["box"]["y"] + label["box"]["height"] <= state["height"] for label in labels)
    for i, label in enumerate(labels):
        for other in labels[i + 1:]:
            a, b = label["box"], other["box"]
            assert (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"] or
                    a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])
