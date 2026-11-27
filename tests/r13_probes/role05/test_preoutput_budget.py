"""Strict independent public API regressions on bounded sparse inputs."""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Any

import pytest
from budget_probe import ENGINES, observe, tree_snapshot

render = importlib.import_module("deepviz.render").render


@pytest.mark.parametrize("scope", ["table", "dashboard"])
@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("existing", [False, True], ids=["new-output", "caller-files"])
def test_oversized_public_render_rejects_before_any_output_allocation(
    scope: str, engine: str, existing: bool, tmp_path: Path,
) -> None:
    output = tmp_path / "caller-output"
    if existing:
        output.mkdir()
        (output / "chart.html").write_text("caller-owned; never replace", encoding="utf-8")
        (output / "manifest.json").write_bytes(b"caller-owned-manifest\x00\xff")
    result = observe(scope, engine, output)
    evidence = os.environ.get("R13_EVIDENCE_DIR")
    if evidence:
        Path(evidence).mkdir(parents=True, exist_ok=True)
        name = f'{scope}-{engine}-{"existing" if existing else "new"}.json'
        (Path(evidence) / name).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    # File preservation is independent of whether the missing guard is RED.
    for name, digest in result["files_before"].items():
        assert result["files_after"].get(name) == digest
    expected_rows = 128 if scope == "table" else 80
    assert all(n["input_count"] == n["output_count"] == expected_rows for n in result["normalizations"])
    assert all(n["strategy"] == "none" and n["warnings"] == [] for n in result["normalizations"])
    assert result["error"] is not None and result["error"]["type"] == "ValueError", result
    assert any(word in result["error"]["message"].lower() for word in ("budget", "limit", "exceed")), result
    assert result["events"] == [], result
    assert result["output_exists_after"] is existing
    assert result["files_after"] == result["files_before"]


@pytest.mark.parametrize("dashboard", [False, True], ids=["small-table", "small-dashboard"])
@pytest.mark.parametrize("engine", ENGINES)
def test_small_public_render_preserves_values_counts_warnings_and_caller_files(
    dashboard: bool, engine: str, tmp_path: Path,
) -> None:
    data = [{"label": "A", "value": 3}, {"label": "B", "value": 7}, {"label": "C", "value": 5}]
    table: dict[str, Any] = {"kind": "table", "title": "R13 small table", "aggregation": "none"}
    spec = table if not dashboard else {
        "kind": "dashboard", "title": "R13 small dashboard", "charts": [table, table],
    }
    output = tmp_path / "caller-output"
    output.mkdir()
    (output / "chart.html").write_text("caller sentinel", encoding="utf-8")
    before = tree_snapshot(output)
    artifact = render(data, spec, engine, output_dir=output)
    for name, digest in before.items():
        assert tree_snapshot(output)[name] == digest
    assert artifact.input_count == 3
    assert artifact.output_count == (6 if dashboard else 3)
    assert artifact.strategy == ("dashboard:none,none" if dashboard else "none")
    expected_warnings = [] if engine not in {"echarts", "antv"} else [
        "HTML requires network access to load its exact-version pinned browser library from jsDelivr."
    ]
    assert artifact.warnings == expected_warnings
    files = [Path(path) for path in artifact.paths]
    assert len({path.parent for path in files}) == 1
    assert files[0].parent.parent == output
    manifest = json.loads(next(path for path in files if path.name == "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["charts"]) == (2 if dashboard else 1)
    assert all(child["records"] == data for child in manifest["charts"])
    assert all(child["input_count"] == child["output_count"] == 3 for child in manifest["charts"])
    html = next(path for path in files if path.suffix == ".html").read_text(encoding="utf-8")
    assert html.count("<tbody>") == (2 if dashboard else 1)
    assert "<td>A</td><td>3</td>" in html and "<td>B</td><td>7</td>" in html
