"""Catch fixed-style categorical overrides and unsafe implicit heatmap scales."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pytest
from fixtures import cases

from deepviz import render


@pytest.mark.parametrize("fixture", cases(), ids=lambda fixture: fixture["id"])
def test_public_antv_color_preserves_values_and_native_semantics(
    fixture: dict[str, Any], tmp_path: Path,
) -> None:
    """A fixed categorical fill, implicit heatmap domain, or lost point fails."""
    artifact = render(fixture["rows"], fixture["spec"], "antv", tmp_path)
    manifest_path = next(Path(name) for name in artifact.paths if name.endswith("manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    native = manifest["native_specs"][0]
    assert manifest["charts"][0]["records"] == fixture["rows"]
    assert artifact.input_count == artifact.output_count == len(fixture["rows"])
    if fixture["mode"] == "category":
        assert native["encode"]["color"] == "_x"
        assert [[row["_x"], row["_y"]] for row in native["data"]] == fixture["expected"]
        assert native.get("legend") is not False, "A hidden legend is not a categorical color fix"
        assert not {"fill", "stroke"}.intersection(native.get("style", {})), (
            "Literal mark colors override encoded categories and disagree with the visible legend"
        )
    elif fixture["mode"] == "heatmap":
        assert native["encode"]["color"] == "_heat"
        assert [row["_heat"] for row in native["data"]] == fixture["expected"]
        assert [[row["_x"], row["_y"]] for row in native["data"]] == [["Mon", "AM"], ["Tue", "PM"]]
        assert not {"fill", "stroke"}.intersection(native.get("style", {}))
        assert native.get("legend") is not False, "Legend-off is only a diagnostic, not a fix"
        scale = native.get("scale", {}).get("color", {})
        assert scale.get("type") in {"linear", "sequential"}, (
            "Negative heatmaps need an explicit continuous color scale, not G2's implicit inference"
        )
        domain = scale.get("domain", [])
        assert len(domain) == 2 and all(isinstance(value, (int, float)) and math.isfinite(value)
                                        for value in domain)
        assert domain[0] < domain[1]
        assert domain[0] <= min(fixture["expected"]) <= max(fixture["expected"]) <= domain[1]
    elif fixture["id"] == "line":
        line, points = native["children"]
        assert native["type"] == "view"
        assert [child["type"] for child in native["children"]] == ["line", "point"]
        for child in (line, points):
            assert [[row["_x"], row["_y"]] for row in child["data"]] == fixture["expected"]
        assert line["style"]["stroke"] == points["style"]["fill"] == "#386cb0"
        assert "fill" not in line["style"], "Do not fill the ordinary positive line path"
    else:
        assert native["type"] == "point"
        assert [[row["_x"], row["_y"]] for row in native["data"]] == fixture["expected"]
        assert native["style"] == {"fill": "#386cb0", "stroke": "#386cb0"}
