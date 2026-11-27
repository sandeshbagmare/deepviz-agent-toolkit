"""Actual immutable recipe tests on tiny Git fixtures, NOT product/scale runs."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
INPUTS = ROOT / "docs/coordination/evidence/R16-21/inputs"
RECIPE = INPUTS / "role09_recipe/tests/r13_probes/role09/retest-helper-null.ps1"
SCALE = INPUTS / "role11/tests/r10_probes/role11/verify_scale_receipt.py"
PERFORMANCE = INPUTS / "product/scripts/performance_suite.py"
PIN = "5340bc69b7203ad7a9166543062482d819f9b705"
PYTHON = Path(sys.executable)
SHELL = shutil.which("powershell.exe")
REGRESSION = "packages/deepviz/test/test_r07_tool_spec_null.test.mjs"
SCHEMAS = ["schemas/chart-spec.schema.json", "packages/deepviz/src/chart-spec.schema.json"]


def run(argv: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=30)


def git(root: Path, *args: str) -> str:
    argv = ["git", "-c", "core.autocrlf=false", "-C", str(root), *args]
    done = run(argv, root)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def write(root: Path, path: str, text: str) -> None:
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    root = tmp_path / "synthetic-source"
    root.mkdir()
    git(root, "init", "-q")
    write(root, ".gitattributes", "* text=auto eol=lf\n")
    write(root, ".gitignore", "packages/deepviz/dist/\n__pycache__/\n")
    for name in [REGRESSION, *SCHEMAS]:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((INPUTS / "role09" / name).read_bytes())
    write(root, "packages/deepviz/src/render.ts", "export const SYNTHETIC = true;\n")
    write(root, "python/deepviz/src/deepviz/__init__.py", "SYNTHETIC = True\n")
    write(root, "python/deepviz/src/deepviz/models.py", "ChartSpec = object\n")
    write(root, "python/deepviz/src/deepviz/normalize.py", "def normalize(*args): return None\n")
    write(root, "scripts/performance_suite.py", "# Synthetic tracked harness sentinel, never run.\n")
    write(root, "scripts/export_schema.py", "# Synthetic schema command, no product imported.\n")
    for name in ["test_models.py", "test_schema_contract.py", "test_cross_language_contract.py", "test_n12_authoritative_parity.py"]:
        write(root, "tests/" + name, "import os\nimport pytest\n@pytest.mark.skipif(os.environ.get(\"R16_SKIP_ALL\") == \"1\", reason=\"Synthetic dependency unavailable\")\ndef test_synthetic_only():\n    assert True\n")
    write(root, "pytest.ini", "[pytest]\naddopts = --junitxml=" + (root.parent / "tiny-pytest.xml").as_posix() + "\n")
    git(root, "add", ".")
    git(root, "-c", "user.name=OfflineFixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "Synthetic fixture only, not DeepViz")
    return root


def invoke09(root: Path, *, expected: str | None = None, execute: bool = False,
             mode: str = "zero", cwd: Path | None = None, duplicate_path: bool = False) -> tuple[subprocess.CompletedProcess[str], Path]:
    assert SHELL is not None, "WindowsPowerShell is required; no skipped acceptance"
    tools = root.parent / "owned-tools"
    tools.mkdir(exist_ok=True)
    body = "@echo off\necho SYNTHETIC STUB: no product tests or compiler executed\n"
    if mode == "mutate":
        body += "echo // fixture changed during run>> \"%R16_FIXTURE_SOURCE%\"\n"
    if mode in {"skipped", "errors"}:
        body += "copy /Y \"%R16_XML_INPUT%\" \"%R16_XML_OUTPUT%\" >nul\n"
        body += "echo SYNTHETIC structured test totals are not all-pass\n"
    body += "exit /b 0\n"
    for name in ["npm.cmd", "node.cmd", "python.cmd"]:
        write(tools, name, body)
    evidence = root.parent / "new-external-evidence"
    env = os.environ.copy()
    if not duplicate_path:
        git_exe = shutil.which("git")
        assert git_exe is not None
        windows = Path(os.environ["SystemRoot"])
        env["PATH"] = os.pathsep.join([str(Path(git_exe).parent), str(windows / "System32"), str(windows)])
    env["R16_FIXTURE_SOURCE"] = str(root / "packages/deepviz/src/render.ts")
    env["R16_XML_INPUT"] = str(root.parent / "synthetic-results.xml")
    env["R16_XML_OUTPUT"] = str(root.parent / "observed-results.xml")
    if mode in {"skipped", "errors"}:
        totals = "tests=\"1\" failures=\"0\" errors=\"0\" skipped=\"1\"" if mode == "skipped" else "tests=\"1\" failures=\"0\" errors=\"1\" skipped=\"0\""
        Path(env["R16_XML_INPUT"]).write_text("<testsuite " + totals + "/>", encoding="utf-8")
    if mode in {"real-pass", "real-skipped", "real-error"}:
        env["R16_SKIP_ALL"] = "1" if mode == "real-skipped" else "0"
        env["PYTEST_ADDOPTS"] = "--junitxml=" + (root.parent / "tiny-pytest.xml").as_posix()
    args = [SHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RECIPE),
            "-Candidate", str(root), "-ExpectedSha", expected or git(root, "rev-parse", "HEAD"),
            "-EvidenceDirectory", str(evidence), "-Python", str(PYTHON if mode.startswith("real-") else tools / "python.cmd"),
            "-ToolsBin", str(tools)]
    if execute:
        args.append("-Run")
    return run(args, cwd or root.parent, env), evidence


def result(evidence: Path) -> dict[str, Any]:
    return json.loads((evidence / "result.json").read_text(encoding="utf-8-sig"))


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_clean_fixture_is_only_a_nine_gate_not_run_plan(fixture_repo: Path) -> None:
    done, evidence = invoke09(fixture_repo)
    assert done.returncode == 0, done.stderr
    plan = json.loads(done.stdout)
    assert plan["status"] == "PLAN_ONLY_NOT_EXECUTED"
    assert len(plan["steps"]) == 9
    assert all(step["state"] == "NOT_RUN" for step in plan["steps"])
    assert not evidence.exists()


@pytest.mark.parametrize("case", ["wrong-sha", "tracked-dirty", "wrong-test-hash", "wrong-schema-hash"])
def test_existing09_preflight_guards(fixture_repo: Path, case: str) -> None:
    expected = git(fixture_repo, "rev-parse", "HEAD")
    if case == "wrong-sha":
        expected = "0" * 40
    elif case == "tracked-dirty":
        write(fixture_repo, "packages/deepviz/src/render.ts", "// dirty fixture\n")
    else:
        name = REGRESSION if case == "wrong-test-hash" else SCHEMAS[0]
        write(fixture_repo, name, "changed immutable fixture\n")
        git(fixture_repo, "add", name)
        git(fixture_repo, "-c", "user.name=OfflineFixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "Synthetic invalid hash")
        expected = git(fixture_repo, "rev-parse", "HEAD")
    done, evidence = invoke09(fixture_repo, expected=expected)
    assert done.returncode != 0
    assert not evidence.exists()


def test09_rejects_untracked_cwd_import_shadow(fixture_repo: Path) -> None:
    write(fixture_repo, "deepviz/__init__.py", "SHADOW_FIXTURE = True\n")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(fixture_repo / "python/deepviz/src")
    observed = run([str(PYTHON), "-c", "import deepviz;print(deepviz.__file__)"], fixture_repo, env)
    assert observed.returncode == 0
    assert str(fixture_repo / "deepviz/__init__.py") == observed.stdout.strip()
    done, _ = invoke09(fixture_repo)
    assert done.returncode != 0, "Actual preflight accepted an untracked package that shadows PYTHONPATH"


def test09_rejects_source_changed_after_preflight(fixture_repo: Path) -> None:
    before = hashlib.sha256((fixture_repo / "packages/deepviz/src/render.ts").read_bytes()).hexdigest()
    done, evidence = invoke09(fixture_repo, execute=True, mode="mutate")
    after = hashlib.sha256((fixture_repo / "packages/deepviz/src/render.ts").read_bytes()).hexdigest()
    assert before != after and git(fixture_repo, "status", "--porcelain")
    receipt = result(evidence)
    assert all(step["state"] == "EXECUTED" for step in receipt["steps"]), receipt
    assert receipt["status"] != "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL", receipt
    assert done.returncode != 0


@pytest.mark.parametrize("mode", ["zero", "skipped", "errors"])
def test09_trusted_zero_exit_stub_has_no_structured_totals_check(fixture_repo: Path, mode: str) -> None:
    done, evidence = invoke09(fixture_repo, execute=True, mode=mode)
    receipt = result(evidence)
    assert all(step["state"] == "EXECUTED" for step in receipt["steps"]), receipt
    assert receipt["status"] == "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL", receipt
    assert done.returncode == 0


def test09_noop_trusted_build_does_not_independently_bind_artifact(fixture_repo: Path) -> None:
    stale = fixture_repo / "packages/deepviz/dist/render.js"
    write(fixture_repo, "packages/deepviz/dist/render.js", "// stale synthetic output\n")
    before = hashlib.sha256(stale.read_bytes()).hexdigest()
    done, evidence = invoke09(fixture_repo, execute=True)
    assert hashlib.sha256(stale.read_bytes()).hexdigest() == before
    receipt = result(evidence)
    assert all(step["state"] == "EXECUTED" for step in receipt["steps"]), receipt
    assert receipt.get("built_render_sha256") == before
    assert receipt["status"] == "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL", receipt
    assert done.returncode == 0


@pytest.mark.parametrize("case", ["normalizer-change", "commit-change"])
def test_existing11_source_change_guards(fixture_repo: Path, case: str) -> None:
    module = load(PERFORMANCE, "role21_actual_performance")
    before = module.source_snapshot(fixture_repo)
    write(fixture_repo, "python/deepviz/src/deepviz/normalize.py", "# changed source fixture\n")
    if case == "commit-change":
        git(fixture_repo, "add", ".")
        git(fixture_repo, "-c", "user.name=OfflineFixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "Synthetic changed commit")
    with pytest.raises(AssertionError, match="Source changed"):
        module.require_same_source(before, module.source_snapshot(fixture_repo))


def test11_clean_fixture_snapshot_guard_passes_only_preflight(fixture_repo: Path) -> None:
    module = load(PERFORMANCE, "role21_clean_source_guard")
    before = module.source_snapshot(fixture_repo)
    assert before["dirty_paths"] == []
    module.require_same_source(before, module.source_snapshot(fixture_repo))


def test11_rejects_tracked_harness_change_during_run(fixture_repo: Path) -> None:
    module = load(PERFORMANCE, "role21_actual_harness_guard")
    before = module.source_snapshot(fixture_repo)
    write(fixture_repo, "scripts/performance_suite.py", "# changed trusted runner\n")
    after = module.source_snapshot(fixture_repo)
    assert before["dirty_paths"] == [] and after["dirty_paths"]
    with pytest.raises(AssertionError, match="Source changed"):
        module.require_same_source(before, after)


def synthetic_receipt() -> dict[str, Any]:
    source = {"commit": PIN, "dirty_paths": [], "sha256": {
        "python/deepviz/src/deepviz/normalize.py": "a" * 64,
        "python/deepviz/src/deepviz/models.py": "b" * 64}}
    rows = []
    for case in ["numeric_sample", "category_sum", "category_mean"]:
        for count in [10, 1000, 100000, 1000000, 10000000]:
            for repeat in ([1, 2] if case == "numeric_sample" else [1]):
                row: dict[str, Any] = {"case": case, "count": count, "status": "passed",
                    "input_count": count, "consumed_count": count, "source_exhausted": True,
                    "max_points": 2000, "scope": "inclusive_process_high_water_mark",
                    "method": "GetProcessMemoryInfo.PeakWorkingSetSize", "peak_rss_bytes": 2,
                    "baseline_peak_rss_bytes": 1, "peak_high_water_growth_bytes": 1,
                    "growth_scope": "difference_of_process_high_water_marks_not_operation_peak_allocation",
                    "elapsed_seconds": 0.0, "subprocess_wall_seconds": 0.0,
                    "output_sha256": "c" * 64, "repeat": repeat}
                if case == "numeric_sample":
                    row.update(strategy="sample", output_count=min(count, 2000),
                               warnings=["synthetic lossy sample"] if count > 2000 else [])
                else:
                    values = {}
                    for category in range(7):
                        size = (count - category + 6) // 7
                        first = category + 1
                        last = first + 7 * (size - 1)
                        values[f"group-{category}"] = size * (first + last) // 2 if case == "category_sum" else (first + last) / 2
                    row.update(strategy=case.removeprefix("category_"), output_count=7,
                               category_values=values, observed_grand_total=count * (count + 1) // 2)
                rows.append(row)
    return {"status": "passed", "errors": [], "source": source, "platform": "Windows synthetic",
            "requested_counts": [10, 1000, 100000, 1000000, 10000000],
            "requested_cases": ["numeric_sample", "category_sum", "category_mean"],
            "numeric_repeats": 2, "render_counts": [], "results": rows,
            "memory_growth_checks": [{"case": c, "inclusive_peak_growth_bytes": 0,
                "limit_bytes": 64 * 1024**2} for c in ["numeric_sample", "category_sum", "category_mean"]]}


def test11_synthetic_metadata_control_is_not_a_measurement() -> None:
    module = load(SCALE, "role21_receipt_metadata")
    checked = module.validate_receipt(synthetic_receipt(), PIN)
    assert checked["workers"] == 20
    assert sum(1 for _ in synthetic_receipt()["results"]) == 20


@pytest.mark.parametrize("case", ["wrong-sha", "dirty", "error", "skip", "incomplete"])
def test_existing11_metadata_rejections(case: str) -> None:
    module = load(SCALE, "role21_receipt_negative")
    data = copy.deepcopy(synthetic_receipt())
    if case == "wrong-sha":
        data["source"]["commit"] = "0" * 40
    elif case == "dirty":
        data["source"]["dirty_paths"] = [" M tracked-source.py"]
    elif case == "error":
        data["errors"] = ["synthetic runtime error"]
    elif case == "skip":
        data["results"][0]["status"] = "skipped"
    else:
        data["results"].pop()
    with pytest.raises(AssertionError):
        module.validate_receipt(data, PIN)


def test09_explicit_tool_shadow_uses_one_resolved_executable(fixture_repo: Path) -> None:
    done, evidence = invoke09(fixture_repo, execute=True, duplicate_path=True)
    receipt = result(evidence)
    assert all(step["state"] == "EXECUTED" for step in receipt["steps"]), receipt
    assert done.returncode == 0, done.stderr


def test09_real_tiny_pytest_skips_are_not_scoped_gate_pass(fixture_repo: Path) -> None:
    import xml.etree.ElementTree as ET
    done, evidence = invoke09(fixture_repo, execute=True, mode="real-skipped")
    xml = ET.parse(fixture_repo.parent / "tiny-pytest.xml").getroot()
    suite = xml.find("testsuite")
    assert suite is not None and int(suite.get("skipped", "0")) == 4
    assert int(suite.get("errors", "0")) == int(suite.get("failures", "0")) == 0
    receipt = result(evidence)
    assert all(step["state"] == "EXECUTED" for step in receipt["steps"]), receipt
    assert receipt["status"] != "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL", receipt
    assert done.returncode != 0


def test09_real_tiny_pass_does_not_claim_product_pass(fixture_repo: Path) -> None:
    done, evidence = invoke09(fixture_repo, execute=True, mode="real-pass")
    assert done.returncode == 0, done.stderr
    receipt = result(evidence)
    assert all(step["state"] == "EXECUTED" for step in receipt["steps"])
    assert "4 passed" in (evidence / "core-parity.log").read_text(encoding="utf-16")


def test09_real_tiny_collection_error_is_gate_failure(fixture_repo: Path) -> None:
    write(fixture_repo, "tests/test_models.py", "def invalid syntax\n")
    git(fixture_repo, "add", ".")
    git(fixture_repo, "-c", "user.name=OfflineFixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Synthetic collection error")
    done, evidence = invoke09(fixture_repo, execute=True, mode="real-error")
    receipt = result(evidence)
    assert done.returncode != 0
    assert receipt["status"] == "GATE_FAILURE_REMAINING_STEPS_NOT_RUN"
    assert receipt["steps"][-1]["state"] == "NOT_RUN"


def test11_wrong_import_origin_is_rejected_in_actual_worker_loader(fixture_repo: Path) -> None:
    write(fixture_repo, "foreign/deepviz/__init__.py", "# Synthetic wrong checkout package\n")
    write(fixture_repo, "foreign/deepviz/models.py", "ChartSpec = object\n")
    write(fixture_repo, "foreign/deepviz/normalize.py", "def normalize(*args): return None\n")
    code = ("import importlib.util,sys;from pathlib import Path;"
            "s=importlib.util.spec_from_file_location(\"actual_runner\",sys.argv[1]);"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "sys.path[:0]=[sys.argv[2],sys.argv[3]];"
            "m.load_api(Path(sys.argv[4]))")
    done = run([str(PYTHON), "-c", code, str(PERFORMANCE),
                str(fixture_repo / "foreign"), str(fixture_repo / "python/deepviz/src"),
                str(fixture_repo)], fixture_repo.parent)
    assert done.returncode != 0
    assert "Refusing source outside requested checkout" in done.stderr


def test09_git_LF_worktree_control_matches_raw_hashes(fixture_repo: Path) -> None:
    git_blob = subprocess.run(["git", "-C", str(fixture_repo), "show", "HEAD:" + REGRESSION], capture_output=True, check=True).stdout
    assert hashlib.sha256(git_blob).hexdigest() == hashlib.sha256((fixture_repo / REGRESSION).read_bytes()).hexdigest()
