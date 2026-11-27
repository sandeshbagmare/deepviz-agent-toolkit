"""Strict categorical paint/legend and quantitative-domain regressions for G2."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from deepviz import render


def browser_cases() -> list[dict[str, Any]]:
    """Literal expectations shared by the unit and real-library browser checks."""
    fixtures: list[dict[str, Any]] = []
    for kind in ("pie", "sunburst", "treemap", "gauge"):
        rows = [{"category": "Alpha", "value": 12}, {"category": "Beta", "value": 31},
                {"category": "Gamma", "value": 7}]
        expected = [["Alpha", 12], ["Beta", 31], ["Gamma", 7]]
        if kind == "gauge":
            rows, expected = [{"category": "Load", "value": 37}], [["Value", 37], ["Remaining", 63]]
        fixtures.append({"id": kind, "mode": "category", "rows": rows, "expected": expected,
                         "spec": {"kind": kind, "x": "category", "y": "value"}})
        if kind != "gauge":
            fixtures.append({"id": kind + "-single", "mode": "category", "expected": [["Only", 1]],
                             "rows": [{"category": "Only", "value": 1}],
                             "spec": {"kind": kind, "x": "category", "y": "value"}})
    for label, values in (("negative", [-7, -2]), ("positive", [2, 7]), ("signed", [-7, 2]),
                          ("constant", [1, 1]), ("zero", [0, 0]), ("constant-negative", [-3, -3]),
                          ("finite-extent", [-1e12, -1e-12]), ("tiny-negative", [-1e-6, -1e-9]),
                          ("missing", [-7, None, -2]), ("all-missing", [None, None])):
        rows = [{"day": "Mon", "slot": "AM", "heat": values[0]},
                {"day": "Tue", "slot": "PM", "heat": values[-1]}]
        if label == "missing":
            rows.insert(1, {"day": "Omitted", "slot": "NA", "heat": None})
        fixtures.append({"id": "heatmap-" + label, "mode": "heatmap", "rows": rows,
                         "expected": [value for value in values if value is not None],
                         "spec": {"kind": "heatmap", "x": "day", "y": "slot", "color": "heat"}})
    for kind in ("line", "scatter"):
        fixtures.append({"id": kind, "mode": "fixed", "expected": [[1, 2], [2, 8], [4, 5]],
                         "rows": [{"x": 1, "y": 2}, {"x": 2, "y": 8}, {"x": 4, "y": 5}],
                         "spec": {"kind": kind, "x": "x", "y": "y"}})
    for theme in ("light", "dark"):
        fixtures.append({"id": "dashboard-" + theme, "mode": "dashboard", "expected": [12, 31, 7],
                         "rows": [{"category": "Alpha", "value": 12, "cost": 2},
                                  {"category": "Beta", "value": 31, "cost": 8},
                                  {"category": "Gamma", "value": 7, "cost": 5}],
                         "spec": {"kind": "dashboard", "theme": theme, "columns": 3,
                                  "charts": [{"kind": "pie", "title": "Same title", "theme": "light"},
                                             {"kind": "line", "title": "Same title", "theme": "dark",
                                              "y": "cost"},
                                             {"kind": "treemap", "title": "Same title", "theme": "dark"}],
                                  "x": "category", "y": "value"}})
    for fixture in fixtures:
        fixture["spec"].update(aggregation="none", width=1050 if fixture["mode"] == "dashboard" else 900,
                               height=480, title="R20 AntV " + fixture["id"])
    return fixtures


def _artifact(fixture: dict[str, Any], output: Path) -> tuple[Any, dict[str, Any], Path]:
    artifact = render(fixture["rows"], fixture["spec"], "antv", output)
    manifest = next(Path(name) for name in artifact.paths if name.endswith("manifest.json"))
    html = next(Path(name) for name in artifact.paths if name.endswith(".html"))
    return artifact, json.loads(manifest.read_text(encoding="utf-8")), html


@pytest.mark.parametrize("fixture", browser_cases(), ids=lambda fixture: fixture["id"])
def test_antv_preserves_literal_geometry_without_overriding_encoded_color(
    fixture: dict[str, Any], tmp_path: Path,
) -> None:
    artifact, manifest, html = _artifact(fixture, tmp_path)
    assert manifest["charts"][0]["records"] == fixture["rows"]
    assert artifact.input_count == len(fixture["rows"])
    payload = manifest["native_specs"][0]
    if fixture["mode"] == "category":
        assert payload["encode"]["color"] == "_x"
        assert [[row["_x"], row["_y"]] for row in payload["data"]] == fixture["expected"]
        assert not {"fill", "stroke"}.intersection(payload.get("style", {})), (
            "Fixed paint overrides the category colors advertised in the visible legend"
        )
        assert payload.get("legend") is not False
    elif fixture["mode"] == "heatmap":
        assert payload["encode"]["color"] == "_heat"
        assert [row["_heat"] for row in payload["data"]] == fixture["expected"]
        expected_grid = [["Mon", "AM"], ["Tue", "PM"]] if fixture["expected"] else []
        assert [[row["_x"], row["_y"]] for row in payload["data"]] == expected_grid
        assert not {"fill", "stroke"}.intersection(payload.get("style", {}))
        scale = payload.get("scale", {}).get("color", {})
        assert scale.get("type") in {"linear", "sequential"}, "Use an explicit continuous color scale"
        domain = scale.get("domain", [])
        assert len(domain) == 2 and all(math.isfinite(value) for value in domain)
        assert domain[0] < domain[1]
        if fixture["expected"]:
            assert domain[0] <= min(fixture["expected"]) <= max(fixture["expected"]) <= domain[1]
        if len(set(fixture["expected"])) > 1:
            assert domain == [min(fixture["expected"]), max(fixture["expected"])]
        assert payload.get("legend") is not False
        if "missing" in fixture["id"]:
            assert any("omitted" in warning and "heatmap" in warning for warning in artifact.warnings)
    elif fixture["mode"] == "fixed":
        marks = payload["children"] if fixture["id"] == "line" else [payload]
        for mark in marks:
            assert [[row["_x"], row["_y"]] for row in mark["data"]] == fixture["expected"]
        if fixture["id"] == "line":
            assert [mark["type"] for mark in marks] == ["line", "point"]
            assert "fill" not in marks[0]["style"]
            assert marks[0]["style"]["stroke"] == marks[1]["style"]["fill"] == "#386cb0"
        else:
            assert payload["style"] == {"fill": "#386cb0", "stroke": "#386cb0"}
    else:
        pie, line, treemap = manifest["native_specs"]
        assert [child["type"] for child in (pie, line, treemap)] == ["interval", "view", "rect"]
        assert [[row["_x"], row["_y"]] for row in line["children"][0]["data"]] == [
            ["Alpha", 2], ["Beta", 8], ["Gamma", 5]]
        assert [row["_y"] for row in pie["data"]] == [row["_y"] for row in treemap["data"]] == [12, 31, 7]
        source = html.read_text(encoding="utf-8")
        assert [pie["theme"], line["theme"], treemap["theme"]] == ["light", "dark", "dark"]
        assert source.count('role="img"') == 3
        assert source.count("background:#171b26") >= 2
        assert "background:#ffffff" in source


def emit(output: Path, commit: str) -> None:
    """Generate exact public HTML plus source identity for the separate browser."""
    repo = Path(__file__).resolve().parents[3]
    output = output.resolve()
    assert not output.exists(), "Never overwrite prior evidence"

    def git(*args: str) -> bytes:
        return subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True).stdout

    assert git("rev-parse", "HEAD").decode().strip() == commit
    identity: dict[str, Any] = {"head": commit, "python": sys.version, "executable": sys.executable,
                                "status": git("status", "--porcelain").decode(), "modules": []}
    for name in ("deepviz", "deepviz.models", "deepviz.engines", "deepviz.render", "deepviz.normalize"):
        module = importlib.import_module(name)
        assert module.__file__ is not None
        file = Path(module.__file__).resolve()
        relative = file.relative_to(repo).as_posix()
        working, blob = file.read_bytes(), git("show", commit + ":" + relative)
        if name == "deepviz.engines":
            pattern = r"def _antv\([\s\S]*?(?=\n\ndef native_spec)"
            assert re.sub(pattern, "<OWN_ANTV_FUNCTION>", working.decode().replace("\r\n", "\n")) == re.sub(
                pattern, "<OWN_ANTV_FUNCTION>", blob.decode())
        else:
            assert working.replace(b"\r\n", b"\n") == blob
        identity["modules"].append({"name": name, "path": relative,
                                    "working_sha256": hashlib.sha256(working).hexdigest(),
                                    "head_git_sha256": hashlib.sha256(blob).hexdigest()})
    output.mkdir(parents=True)
    emitted = []
    for fixture in browser_cases():
        artifact, manifest, html = _artifact(fixture, output / fixture["id"])
        emitted.append({**fixture, "html": html.relative_to(output).as_posix(),
                        "manifest": manifest, "artifact": artifact.to_dict(),
                        "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest()})
    (output / "cases.json").write_text(json.dumps({"identity": identity, "cases": emitted}, indent=2),
                                      encoding="utf-8")
    print(json.dumps({"head": commit, "cases": len(emitted), "output": str(output)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Emit untouched public AntV HTML for real browser tests")
    parser.add_argument("--emit", required=True, type=Path)
    parser.add_argument("--commit", required=True)
    arguments = parser.parse_args()
    emit(arguments.emit, arguments.commit)
