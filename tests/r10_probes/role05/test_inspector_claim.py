"""Independent metadata regressions: structural inspection never certifies paint."""
from __future__ import annotations

import importlib.util
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(os.environ.get("R10_INSPECTOR_SOURCE_ROOT", ROOT)).resolve()
CASES = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
STRUCTURAL = "svg_xml_structure_only_not_visual_review"


@pytest.fixture(scope="module")
def inspector() -> ModuleType:
    path = SOURCE / "scripts/performance_suite.py"
    spec = importlib.util.spec_from_file_location("r10_role05_inspector", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.__file__ is not None
    assert Path(module.__file__).resolve() == path
    return module


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_original_invalid_and_visible_controls_only_claim_structure(
    case: dict[str, object], inspector: ModuleType, tmp_path: Path,
) -> None:
    path = tmp_path / "control.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" '
        f'viewBox="0 0 64 64">{case["geometry"]}</svg>', encoding="utf-8",
    )
    before = path.read_bytes()
    result = inspector.inspect_artifact(path)
    assert result == {"path": str(path), "bytes": len(before), "inspection": STRUCTURAL}
    assert path.read_bytes() == before
    # Acceptance here is XML/element presence, not a valid or painted SVG verdict.
    assert "drawable" not in result["inspection"]


@pytest.mark.parametrize("geometry", [
    '<g display="none"><rect width="20" height="20"/></g>',
    '<defs><path d="M4 4L48 48"/></defs>',
], ids=["hidden-rectangle", "uninstantiated-definition"])
def test_supported_elements_need_not_paint_for_structure_only_inspection(
    geometry: str, inspector: ModuleType, tmp_path: Path,
) -> None:
    path = tmp_path / "not-visible.svg"
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{geometry}</svg>', encoding="utf-8")
    assert inspector.inspect_artifact(path)["inspection"] == STRUCTURAL


@pytest.mark.parametrize("contents", [
    '<svg xmlns="http://www.w3.org/2000/svg"/>',
    '<svg xmlns="http://www.w3.org/2000/svg"><text>text only</text></svg>',
    '<html><path d="M0 0L2 2"/></html>',
    '<svg><path></svg>',
], ids=["empty-svg", "no-supported-element", "wrong-root", "malformed-xml"])
def test_real_structure_negative_controls_remain_rejected(
    contents: str, inspector: ModuleType, tmp_path: Path,
) -> None:
    path = tmp_path / "bad.svg"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises((AssertionError, ET.ParseError)):
        inspector.inspect_artifact(path)


def test_documentation_explicitly_limits_the_svg_claim() -> None:
    text = " ".join((SOURCE / "docs/verification/performance.md").read_text(encoding="utf-8").split())
    assert "contain a supported geometry element" in text
    assert "attributes, drawability and visible paint are not validated" in text
