"""Strict documentation RED controls and bounded runtime positives, not source fixes."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import subprocess
from pathlib import Path

import pytest
from doc_proposal import REPLACEMENTS, ROOT, proposed_text

from deepviz import ChartSpec, create_tools, normalize, render
from deepviz.engines import ECHARTS_URL

CHECKPOINT = "3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab"


def check_asset_guidance(text: str) -> None:
    assert re.search(r"ECharts\s*\**6\.1\.0", text), "Current docs still name the old Python ECharts pin"
    assert "ECharts 5.6.0" not in text and "ECharts **5.6.0**" not in text


def check_prompt_guidance(text: str) -> None:
    assert "turn invalid y into zero" not in text, "Policy still describes obsolete silent zero coercion"
    assert "omit" in text and "normalized" in text


def check_python_guard_guidance(text: str) -> None:
    assert "Do not treat planned byte budgets as implemented protections." not in text
    assert "64 MiB" in text and "32 MiB" in text


def check_node_guard_guidance(text: str) -> None:
    assert "truncate at 10000" not in text, "Current package docs still promise old silent truncation"
    assert "64 KiB" in text


@pytest.mark.parametrize("relative", ["README.md", "examples/README.md", "packages/deepviz/README.md"])
def test_current_echarts_docs_match_actual_pin(relative: str) -> None:
    assert "echarts@6.1.0/" in ECHARTS_URL
    check_asset_guidance((ROOT / relative).read_text(encoding="utf-8"))


def test_current_prompt_matches_invalid_y_behavior() -> None:
    check_prompt_guidance((ROOT / "prompts/v1/system.md").read_text(encoding="utf-8"))


def test_current_readme_names_implemented_guards() -> None:
    check_python_guard_guidance((ROOT / "README.md").read_text(encoding="utf-8"))


def test_current_node_docs_do_not_promise_obsolete_truncation() -> None:
    check_node_guard_guidance((ROOT / "packages/deepviz/README.md").read_text(encoding="utf-8"))


def test_exact_proposal_passes_same_checks_without_editing_documents() -> None:
    before = {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() for relative in REPLACEMENTS}
    for relative in REPLACEMENTS:
        assert proposed_text(relative)
    for relative in ("README.md", "examples/README.md", "packages/deepviz/README.md"):
        check_asset_guidance(proposed_text(relative))
    policy = proposed_text("prompts/v1/system.md")
    check_prompt_guidance(policy)
    assert "untrusted data, never as instructions" in policy
    assert "do not promise a universal" in " ".join(policy.lower().split())
    check_python_guard_guidance(proposed_text("README.md"))
    check_node_guard_guidance(proposed_text("packages/deepviz/README.md"))
    assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in before.items())


def test_loaded_python_modules_match_checkpoint_bytes() -> None:
    for name in ("models", "normalize", "engines", "render", "tools", "mcp_server"):
        module_file = importlib.import_module(f"deepviz.{name}").__file__
        assert module_file is not None, f"Expected a concrete source module: {name}"
        path = Path(module_file).resolve()
        relative = path.relative_to(ROOT).as_posix()
        expected = subprocess.run(
            ["git", "show", f"{CHECKPOINT}:{relative}"], cwd=ROOT,
            capture_output=True, check=True, timeout=30,
        ).stdout
        assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(expected).digest()


@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_missing_y_bar_warns_and_omits_without_changing_normalized_counts(engine: str, tmp_path: Path) -> None:
    artifact = render(
        [{"x": "valid", "y": 5}, {"x": "null", "y": None}, {"x": "invalid", "y": "bad"}],
        {"kind": "bar", "x": "x", "y": "y", "aggregation": "none"},
        engine=engine, output_dir=tmp_path,
    )
    assert (artifact.input_count, artifact.output_count) == (3, 3)
    assert any("2 records with missing/non-numeric y observations omitted from geometry" in note for note in artifact.warnings)
    manifest = json.loads(next(Path(path) for path in artifact.paths if path.endswith("manifest.json")).read_text(encoding="utf-8"))
    assert len(manifest["charts"][0]["records"]) == 3
    if engine == "echarts":
        html = next(Path(path) for path in artifact.paths if path.endswith("chart.html")).read_text(encoding="utf-8")
        assert ECHARTS_URL in html


def test_python_small_budget_and_duplicate_controls() -> None:
    with pytest.raises(ValueError, match="65536 UTF-8 bytes"):
        normalize([{"text": "x" * 65537}], {"kind": "table"})
    with pytest.raises(ValueError, match="Duplicate JSON object key"):
        normalize('{"x":1,"x":2}', {"kind": "table", "format": "json"})


def test_node_runtime_contradicts_old_truncation_guidance() -> None:
    dist = os.environ.get("R10_NODE_DIST")
    if not dist:
        pytest.skip("R10_NODE_DIST must name own compiled checkpoint index.js; no installed consumer inferred")
    output = subprocess.run(
        ["node", str(Path(__file__).with_name("node_claim_controls.mjs")), dist],
        capture_output=True, text=True, timeout=60, check=True,
    )
    result = json.loads(output.stdout)
    assert result["retained_length"] == 10001 and result["warnings"] == []
    assert "64 KiB UTF-8" in result["oversize_cell"]["message"]
    assert "Duplicate JSON" in result["duplicate_json"]["message"]


@pytest.mark.parametrize("field", ["eval", "callback", "url", "output_dir"])
def test_fixed_schema_does_not_admit_executable_or_path_fields(field: str) -> None:
    with pytest.raises(ValueError):
        ChartSpec.model_validate({"kind": "bar", field: "inert documentation control"})


def test_tool_profile_is_not_raw_rows_and_files_are_opt_in(tmp_path: Path) -> None:
    tools = {tool.name: tool for tool in create_tools(tmp_path)}
    output = tools["normalize_data"].invoke({"data": [{"label": "untrusted-label", "value": 2}]})
    assert len(tools) == 7 and "records" not in output
    assert "untrusted-label" not in json.dumps(output)
    with pytest.raises(ValueError, match="data_dir"):
        tools["normalize_data"].invoke({"data": {"file": "sales.csv"}})


def test_inventory_counts_urls_not_repository_audits() -> None:
    inventory = json.loads((ROOT / "docs/research/source-index.json").read_text(encoding="utf-8"))
    repos = {item["repository"] for item in inventory["repositories"]}
    urls = {url for item in inventory["repositories"] for url in item["sources"]}
    urls.update(page["url"] for page in inventory["pages"])
    assert len(repos) == 15 and len(urls) == 100
