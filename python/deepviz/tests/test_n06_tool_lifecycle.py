"""Regressions for host-owned tool artifacts and invalid inline JSON."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from deepviz.tools import ToolSession

ROWS = [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}]
SPEC = {"kind": "bar", "x": "month", "y": "revenue"}


def test_failed_render_removes_only_its_new_destination(tmp_path: Path):
    """A rejected mapping must not leave one directory per failed request."""
    output = tmp_path / "out"
    output.mkdir()
    existing = output / "host-owned.txt"
    existing.write_text("preserve this artifact", encoding="utf-8")
    session = ToolSession(output)

    with pytest.raises(ValueError, match="missing"):
        session.render_chart("echarts", ROWS, {**SPEC, "x": "missing"})

    assert list(output.iterdir()) == [existing]
    assert existing.read_text(encoding="utf-8") == "preserve this artifact"


def test_rejected_artifact_size_cleans_partial_render(tmp_path: Path, monkeypatch):
    """Post-render byte validation owns cleanup too, not only render exceptions."""
    from deepviz import tools

    monkeypatch.setattr(tools, "MAX_ARTIFACT_BYTES", 100)
    session = ToolSession(tmp_path / "out")

    with pytest.raises(ValueError, match="Artifact exceeds"):
        session.render_chart("echarts", ROWS, SPEC)

    assert list(session.output_dir.iterdir()) == []


@pytest.mark.parametrize("encoded", [False, True], ids=["python-json", "json-text"])
def test_overdeep_inline_json_has_actionable_validation_error(tmp_path: Path, encoded: bool):
    """Both parser paths must reject depth without leaking a RecursionError."""
    data = []
    for _ in range(1500):
        data = [data]
    if encoded:
        data = "[" * 1500 + "]" * 1500

    with pytest.raises(ValueError, match="deep|nest"):
        ToolSession(tmp_path).normalize_data(data)


def test_valid_render_keeps_downloadable_artifacts(tmp_path: Path):
    """Success must retain real files rather than using an auto-deleting tempdir."""
    result = ToolSession(tmp_path).render_chart("echarts", ROWS, SPEC)

    assert result["input_count"] == result["output_count"] == 2
    manifest = next(Path(value) for value in result["paths"] if value.endswith("manifest.json"))
    assert json.loads(manifest.read_text(encoding="utf-8"))["charts"][0]["records"] == ROWS
    assert all(Path(value).is_file() for value in result["paths"])


def test_handle_copy_survives_original_eviction_but_not_a_new_tool_session(tmp_path: Path):
    """Cache eviction must expire the old handle, not leave dangling alias chains."""
    from deepviz.tools import create_tools

    pytest.importorskip("langchain_core")
    tools = {tool.name: tool for tool in create_tools(tmp_path)}
    original = tools["normalize_data"].invoke({"data": ROWS})["dataset_id"]
    copied = tools["normalize_data"].invoke({"data": {"dataset_id": original}})["dataset_id"]
    for _ in range(31):
        tools["normalize_data"].invoke({"data": ROWS})

    with pytest.raises(ValueError, match="expired"):
        tools["recommend_chart"].invoke({"data": {"dataset_id": original}})
    recommendation = tools["recommend_chart"].invoke({"data": {"dataset_id": copied}})
    artifact = tools["render_echarts"].invoke({"data": {"dataset_id": copied}, "spec": recommendation["spec"]})
    assert artifact["input_count"] == artifact["output_count"] == 2
    assert all(Path(value).is_file() for value in artifact["paths"])

    new_tools = {tool.name: tool for tool in create_tools(tmp_path)}
    with pytest.raises(ValueError, match="expired"):
        new_tools["recommend_chart"].invoke({"data": {"dataset_id": copied}})


def test_cli_failed_mapping_is_json_stdout_clean_and_leaves_no_artifacts(tmp_path: Path):
    """CLI errors after schema validation must share the per-call cleanup path."""
    data = tmp_path / "data.json"
    spec = tmp_path / "spec.json"
    data.write_text(json.dumps(ROWS), encoding="utf-8")
    spec.write_text(json.dumps({**SPEC, "x": "missing"}), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "deepviz.cli", "render", str(data), "--spec", str(spec),
         "--engine", "echarts", "--output-dir", str(tmp_path / "out")],
        capture_output=True, text=True, timeout=60,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "missing" in result.stderr
    assert "Traceback" not in result.stderr
    assert not list((tmp_path / "out").rglob("*"))
