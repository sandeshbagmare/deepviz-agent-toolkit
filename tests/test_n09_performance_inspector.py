"""Independent artifact-inspector controls; structural checks are not visual signoff."""
from __future__ import annotations

import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from deepviz import ChartSpec, render
from scripts import performance_suite as suite


@pytest.fixture
def manifest() -> dict[str, Any]:
    return {"engine": "vega", "charts": [{
        "records": [{"category": "Alpha", "value": 3}, {"category": "Beta", "value": 7}],
        "input_count": 2, "output_count": 2,
    }]}


def _write_manifest(tmp_path: Path, value: Any, name: str = "manifest.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_real_public_artifact_sets_are_accepted_without_claiming_execution(engine: str, tmp_path: Path) -> None:
    artifact = render(
        [{"category": "Alpha", "value": 3}, {"category": "Beta", "value": 7}],
        ChartSpec(kind="bar", x="category", y="value", title="N09 inspector: 3 and 7", aggregation="none"),
        engine=engine, output_dir=tmp_path,
    )
    assert (artifact.input_count, artifact.output_count) == (2, 2)
    paths = [Path(path) for path in artifact.paths]
    expected = {".html", ".json"} | ({".png", ".svg"} if engine == "matplotlib" else
                                     {".svg"} if engine == "vega" else set())
    assert {path.suffix for path in paths} == expected
    for path in paths:
        before = path.read_bytes()
        inspected = suite.inspect_artifact(path)
        assert inspected["path"] == str(path)
        assert inspected["bytes"] == len(before) > 0
        assert "not_" in inspected["inspection"]
        assert path.read_bytes() == before, "Inspection must not rewrite its evidence"
        if path.suffix == ".html":
            assert "browser_execution_not_verified" in inspected["inspection"]
            if engine in {"matplotlib", "vega"}:
                assert "<script" not in before.decode("utf-8").lower()


def test_truthful_script_free_accessibility_table_and_manifest_are_accepted(
    tmp_path: Path, manifest: dict[str, Any],
) -> None:
    page = tmp_path / "chart.html"
    page.write_text(
        '<!doctype html><html lang="en"><head><title>Known values</title></head><body>'
        '<table><caption>Measurements</caption><thead><tr><th scope="col">category</th>'
        '<th scope="col">value</th></tr></thead><tbody><tr><th scope="row">Alpha</th><td>3</td>'
        '</tr><tr><th scope="row">Beta</th><td>7</td></tr></tbody></table></body></html>',
        encoding="utf-8",
    )
    data = _write_manifest(tmp_path, manifest)
    assert suite.inspect_artifact(page)["inspection"] == "html_structure_only_browser_execution_not_verified"
    assert suite.inspect_artifact(data)["inspection"] == (
        "manifest_json_structure_and_counts_only_semantics_not_verified"
    )


@pytest.mark.parametrize("case", ["reduced", "empty", "multiple-panels"])
def test_truthful_reduced_empty_and_independent_panel_counts_are_accepted(
    case: str, tmp_path: Path, manifest: dict[str, Any],
) -> None:
    first = manifest["charts"][0]
    if case == "reduced":
        first["input_count"] = 31
    elif case == "empty":
        first.update(records=[], input_count=0, output_count=0)
    else:
        manifest["charts"].append({"records": [{"category": "Gamma", "value": 11}],
                                   "input_count": 7, "output_count": 1})
    assert "semantics_not_verified" in suite.inspect_artifact(_write_manifest(tmp_path, manifest))["inspection"]


@pytest.mark.parametrize("bad", [
    None, [], {"arbitrary": [1, 2]}, {"engine": "unknown", "charts": [{}]},
    {"engine": "vega"}, {"engine": "vega", "charts": []},
    {"engine": "vega", "charts": {}}, {"engine": "vega", "charts": [None]},
    {"engine": "vega", "charts": [{"records": {}, "input_count": 0, "output_count": 0}]},
    {"engine": "vega", "charts": [{"records": [3], "input_count": 1, "output_count": 1}]},
    {"engine": "vega", "charts": [{"records": [], "input_count": 0}]},
], ids=["null", "array", "arbitrary-object", "unknown-engine", "missing-charts", "empty-charts",
        "charts-not-array", "chart-not-object", "records-not-array", "record-not-object", "missing-count"])
def test_arbitrary_json_and_invalid_manifest_shapes_cannot_pass(bad: Any, tmp_path: Path) -> None:
    with pytest.raises((AssertionError, ValueError)):
        suite.inspect_artifact(_write_manifest(tmp_path, bad))


@pytest.mark.parametrize("field", ["input_count", "output_count"])
@pytest.mark.parametrize("bad", [True, False, 2.0, "2", None, 1.25])
def test_counts_require_actual_integers_not_coercible_or_boolean_values(
    field: str, bad: Any, tmp_path: Path, manifest: dict[str, Any],
) -> None:
    manifest["charts"][0][field] = bad
    with pytest.raises((AssertionError, ValueError)):
        suite.inspect_artifact(_write_manifest(tmp_path, manifest))


@pytest.mark.parametrize("input_count,output_count", [(-1, 2), (1, 2), (2, -1), (2, 1), (2, 3), (0, 2)])
def test_negative_or_lying_counts_cannot_pass(
    input_count: int, output_count: int, tmp_path: Path, manifest: dict[str, Any],
) -> None:
    manifest["charts"][0].update(input_count=input_count, output_count=output_count)
    with pytest.raises((AssertionError, ValueError)):
        suite.inspect_artifact(_write_manifest(tmp_path, manifest))


@pytest.mark.parametrize("number", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_manifest_measurements_cannot_hide_behind_truthful_counts(number: str, tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        '{"engine":"vega","charts":[{"records":[{"x":"A","y":' + number
        + '}],"input_count":1,"output_count":1}]}', encoding="utf-8",
    )
    with pytest.raises((AssertionError, ValueError)):
        suite.inspect_artifact(path)


@pytest.mark.parametrize("field", ["input_count", "output_count"])
@pytest.mark.parametrize("number", ["1e9999", "-1e9999"])
def test_overflowing_number_literals_are_not_integer_counts(field: str, number: str, tmp_path: Path) -> None:
    text = '{"engine":"vega","charts":[{"records":[],"input_count":0,"output_count":0}]}'
    path = tmp_path / "manifest.json"
    path.write_text(text.replace(f'"{field}":0', f'"{field}":{number}'), encoding="utf-8")
    with pytest.raises((AssertionError, ValueError)):
        suite.inspect_artifact(path)


@pytest.mark.parametrize("contents", ['{"engine":', '{"engine":"vega",}', "not JSON"])
def test_malformed_manifest_json_is_not_a_success(contents: str, tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises((AssertionError, ValueError)):
        suite.inspect_artifact(path)


@pytest.mark.parametrize("name", ["arbitrary.json", "manifest.txt"])
def test_a_json_object_or_extension_alone_is_not_a_supported_artifact(
    name: str, tmp_path: Path, manifest: dict[str, Any],
) -> None:
    with pytest.raises(AssertionError):
        suite.inspect_artifact(_write_manifest(tmp_path, manifest, name))


@pytest.mark.parametrize("suffix,contents", [
    (".svg", '<html><path d="M0 0L2 2"/></html>'),
    (".svg", '<svg xmlns="http://www.w3.org/2000/svg"><g/></svg>'),
    (".svg", '<svg xmlns="http://www.w3.org/2000/svg"><text>Only text</text></svg>'),
    (".svg", '<svg><path></svg>'),
    (".html", '<html><p>No chart, script or accessible table</p></html>'),
    (".html", '<html><!-- <script>not a real tag</script> --></html>'),
    (".html", '<html><table><tr><th>Missing data cells</th></tr></table></html>'),
    (".html", '<script type="application/json">{}</script>'),
])
def test_missing_document_structure_or_marks_are_rejected(suffix: str, contents: str, tmp_path: Path) -> None:
    path = tmp_path / f"chart{suffix}"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises((AssertionError, ET.ParseError)):
        suite.inspect_artifact(path)


@pytest.mark.parametrize("geometry", [
    "<path/>", '<rect width="not-a-number" height="3"/>',
    '<circle cx="2" cy="2" r="-1"/>', '<polyline points="not-points"/>',
], ids=["empty-path", "nonnumeric-rectangle", "negative-radius", "invalid-points"])
def test_declared_drawable_geometry_must_not_accept_nondrawable_tags(geometry: str, tmp_path: Path) -> None:
    path = tmp_path / "chart.svg"
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" '
                    f'viewBox="0 0 64 64">{geometry}</svg>', encoding="utf-8")
    # Reject invalid marks or disclose structure-only inspection, never claim drawable geometry.
    try:
        inspected = suite.inspect_artifact(path)
    except (AssertionError, ValueError):
        return
    assert "drawable" not in inspected["inspection"], "A tag name alone does not prove drawable geometry"
    assert "not_visual_review" in inspected["inspection"]


@pytest.mark.parametrize("case", ["flat", "truncated", "wrong-signature"])
def test_pngs_must_decode_and_contain_nonuniform_pixels(case: str, tmp_path: Path) -> None:
    path = tmp_path / "chart.png"
    if case == "flat":
        Image.new("RGB", (8, 8), color=(31, 47, 63)).save(path)
    elif case == "truncated":
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 8 + struct.pack(">II", 8, 8))
    else:
        path.write_bytes(b"this is not a PNG image")
    with pytest.raises((AssertionError, OSError, ValueError)):
        suite.inspect_artifact(path)


@pytest.mark.parametrize("case", ["missing", "empty"])
def test_missing_or_empty_evidence_never_passes(case: str, tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    if case == "empty":
        path.write_bytes(b"")
    with pytest.raises(AssertionError):
        suite.inspect_artifact(path)
