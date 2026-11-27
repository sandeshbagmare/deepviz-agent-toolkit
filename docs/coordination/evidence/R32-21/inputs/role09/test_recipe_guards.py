"""Synthetic recipe fixtures only: no DeepViz build, product tests or scale run."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
RECIPE = Path(os.environ.get("R22_RECIPE", str(Path(__file__).with_name("retest-helper-null.ps1"))))
SHELL = shutil.which("powershell.exe")
REGRESSION = "packages/deepviz/test/test_r07_tool_spec_null.test.mjs"
SCHEMAS = ["schemas/chart-spec.schema.json", "packages/deepviz/src/chart-spec.schema.json"]


def run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=40)


def git(root: Path, *args: str) -> str:
    result = run(["git", "-C", str(root), *args], root)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def write(root: Path, name: str, text: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def candidate(tmp_path: Path) -> Path:
    root = tmp_path / "SYNTHETIC-NOT-DEEPVIZ"
    root.mkdir()
    git(root, "init", "-q")
    write(root, ".gitattributes", "* text=auto eol=lf\n")
    write(root, ".gitignore", "__pycache__/\n.pytest_cache/\npackages/deepviz/dist/\n")
    for name in [REGRESSION, *SCHEMAS]:
        data = subprocess.check_output(["git", "-C", str(ROOT), "show", "5d57692731949cf98bcf92a319eb25ebc85fc62b:docs/coordination/evidence/R16-21/inputs/role09/" + name])
        expected = "08be1d15661d6bd5bf87bdcec7db11ba3097d9eee294db654369564716e32227" if name == REGRESSION else "3bfc9e4e4351e1d51984a62dcc67ed42eda6a02d61eb718f511a5451d11c4a71"
        assert hashlib.sha256(data).hexdigest() == expected
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    write(root, "packages/deepviz/src/render.ts", "// SYNTHETIC source sentinel\n")
    for name in ["__init__.py", "models.py", "normalize.py"]:
        write(root, "python/deepviz/src/deepviz/" + name, "SYNTHETIC = True\n")
    write(root, "scripts/export_schema.py", "# SYNTHETIC no-op; not a product schema check\n")
    for name in ["test_models.py", "test_schema_contract.py", "test_cross_language_contract.py", "test_n12_authoritative_parity.py"]:
        write(root, "tests/" + name,
              "import os\nimport pytest\nimport deepviz.normalize\n"
              "@pytest.mark.skipif(os.environ.get('R22_SKIP_ALL') == '1', reason='synthetic optional dependency')\n"
              "def test_synthetic_only():\n    assert deepviz.normalize.SYNTHETIC\n")
    write(root, "pytest.ini", "[pytest]\naddopts = --junitxml=" + (root.parent / "old-core.xml").as_posix() + "\n")
    git(root, "add", ".")
    git(root, "-c", "user.name=SyntheticFixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Synthetic only")
    return root


def invoke(root: Path, *, execute: bool = False, mode: str = "pass", duplicate: bool = False, mutation: Path | None = None) -> tuple[subprocess.CompletedProcess[str], Path]:
    assert SHELL
    tools = root.parent / "explicit-tools"
    tools.mkdir(exist_ok=True)
    npm = "@echo off\necho SYNTHETIC TOOL STUB, not a compiler or product test\n"
    if mode == "mutate":
        npm += 'echo // changed>> "%R22_MUTATE_FILE%"\n'
    if mode == "head-change":
        npm += 'git -C "%R22_SOURCE%" -c user.name=Synthetic -c user.email=fixture@example.invalid commit --allow-empty -qm "Synthetic HEAD changed"\n'
    npm += "echo TAP version 13\nfor /L %%i in (1,1,282) do echo ok %%i - SYNTHETIC NOT PRODUCT\necho 1..282\necho # tests 282\necho # pass 282\necho # fail 0\necho # cancelled 0\necho # skipped 0\necho # todo 0\nexit /b 0\n"
    node = "@echo off\necho SYNTHETIC node stub, not product test\necho TAP version 13\nfor /L %%i in (1,1,36) do echo ok %%i - SYNTHETIC NOT PRODUCT\necho 1..36\necho # tests 36\necho # pass 36\necho # fail 0\necho # cancelled 0\necho # skipped 0\necho # todo 0\nexit /b 0\n"
    write(tools, "npm.cmd", npm)
    write(tools, "node.cmd", node)
    evidence = root.parent / "evidence"
    env = os.environ.copy()
    if not duplicate:
        git_exe = shutil.which("git")
        assert git_exe
        windows = Path(os.environ["SystemRoot"])
        env["PATH"] = os.pathsep.join([str(Path(git_exe).parent), str(windows / "System32"), str(windows)])
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["R22_SKIP_ALL"] = "1" if mode == "skip" else "0"
    env["R22_MUTATE_FILE"] = str(mutation or root / "packages/deepviz/src/render.ts")
    env["R22_SOURCE"] = str(root)
    args = [SHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RECIPE),
            "-Candidate", str(root), "-ExpectedSha", git(root, "rev-parse", "HEAD"),
            "-EvidenceDirectory", str(evidence), "-Python", sys.executable, "-ToolsBin", str(tools)]
    if execute:
        args.append("-Run")
    return run(args, root.parent, env), evidence


def receipt(path: Path) -> dict:
    return json.loads((path / "result.json").read_text(encoding="utf-8-sig"))


def test_source_change_after_preflight_is_rejected(candidate: Path) -> None:
    before = hashlib.sha256((candidate / "packages/deepviz/src/render.ts").read_bytes()).hexdigest()
    done, evidence = invoke(candidate, execute=True, mode="mutate")
    assert hashlib.sha256((candidate / "packages/deepviz/src/render.ts").read_bytes()).hexdigest() != before
    assert done.returncode != 0, "Recipe falsely accepted source changed after preflight"
    assert receipt(evidence)["status"] != "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL"


def test_untracked_cwd_shadow_is_rejected_even_in_plan(candidate: Path) -> None:
    write(candidate, "deepviz/__init__.py", "SHADOW = True\n")
    done, evidence = invoke(candidate)
    assert done.returncode != 0, "Recipe accepted an unexpected CWD import shadow"
    assert not evidence.exists()


def test_actual_four_skipped_pytests_are_not_scoped_pass(candidate: Path) -> None:
    done, evidence = invoke(candidate, execute=True, mode="skip")
    assert done.returncode != 0, "Actual all-skipped Pytest became scoped PASS"
    assert receipt(evidence)["status"] != "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL"
    xml_path = evidence / "core-parity.xml"
    if not xml_path.exists():
        xml_path = candidate.parent / "old-core.xml"
    suite = ET.parse(xml_path).getroot().find("testsuite")
    assert suite is not None and suite.get("tests") == suite.get("skipped") == "4"


def test_explicit_one_tool_succeeds_with_duplicate_path(candidate: Path) -> None:
    done, evidence = invoke(candidate, execute=True, duplicate=True)
    assert done.returncode == 0, done.stdout + done.stderr
    actual = receipt(evidence)
    assert actual["status"] == "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL"
    assert all(step["state"] == "EXECUTED" for step in actual["steps"])
    if "r22_probes" in str(RECIPE):
        for step in actual["steps"]:
            if step["name"] not in {"python-schema-check", "core-parity"}:
                assert Path(step["executable"]).parent == candidate.parent / "explicit-tools"
        core = actual["steps"][7]["provenance"]
        assert core["collected"] == core["totals"]["passed"] == 4
        assert all(Path(item["path"]).is_relative_to(candidate / "python/deepviz/src") for item in core["modules"].values())


def test_plan_never_claims_execution_or_creates_evidence(candidate: Path) -> None:
    done, evidence = invoke(candidate)
    assert done.returncode == 0, done.stderr
    plan = json.loads(done.stdout)
    assert plan["status"] == "PLAN_ONLY_NOT_EXECUTED"
    assert len(plan["steps"]) == 9
    assert all(step["state"] == "NOT_RUN" for step in plan["steps"])
    assert not evidence.exists()


def test_actual_collection_error_stays_failed(candidate: Path) -> None:
    write(candidate, "tests/test_models.py", "def invalid syntax\n")
    git(candidate, "add", ".")
    git(candidate, "-c", "user.name=SyntheticFixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Synthetic collection error")
    done, evidence = invoke(candidate, execute=True)
    assert done.returncode != 0
    assert receipt(evidence)["steps"][-1]["state"] == "NOT_RUN"


def guard_module():
    spec = importlib.util.spec_from_file_location("own_fixed_recipe_guard", Path(__file__).with_name("recipe_guard.py"))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("case", ["missing", "malformed", "no-cases", "lying-skips", "below-minimum"])
def test_junit_missing_incomplete_or_contradictory_totals_reject(tmp_path: Path, case: str) -> None:
    path = tmp_path / "SYNTHETIC-report.xml"
    values = {"malformed": "not XML", "no-cases": '<testsuite tests="1"/>',
              "lying-skips": '<testsuite tests="1" skipped="0"><testcase><skipped/></testcase></testsuite>',
              "below-minimum": '<testsuite tests="0"/>'}
    if case != "missing":
        path.write_text(values[case], encoding="utf-8")
    with pytest.raises((AssertionError, FileNotFoundError, ET.ParseError)):
        guard_module().junit(path, 1)


def test_tap_totals_without_actual_case_and_plan_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "SYNTHETIC-incomplete.tap"
    path.write_text("# tests 1\n# pass 1\n# fail 0\n# cancelled 0\n# skipped 0\n# todo 0\n", encoding="utf-8")
    with pytest.raises(AssertionError):
        guard_module().tap(path, 1)


def test_actual_fixed_public_origin_supports_import_only_package(candidate: Path) -> None:
    node = shutil.which("node")
    assert node
    package = candidate / "packages/deepviz"
    write(package, "package.json", json.dumps({"name": "@deepviz/agent-toolkit", "type": "module", "exports": {".": {"import": "./dist/index.js"}}}))
    write(package, "dist/index.js", "export const SYNTHETIC = true;\n")
    git(candidate, "add", ".")
    git(candidate, "-c", "user.name=SyntheticFixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Synthetic import-only package")
    plan, _ = invoke(candidate)
    assert plan.returncode == 0, plan.stderr
    args = json.loads(plan.stdout)["steps"][1]["arguments"]
    done = run([node, *args], package)
    assert done.returncode == 0, done.stdout + done.stderr


@pytest.mark.parametrize("skip", [False, True])
def test_actual_tiny_node_tap_pass_and_skip_policy(tmp_path: Path, skip: bool) -> None:
    node = shutil.which("node")
    assert node
    path = tmp_path / "SYNTHETIC-tiny.test.mjs"
    path.write_text("import test from 'node:test';test" + (".skip" if skip else "") + "('synthetic only',()=>{});", encoding="utf-8")
    result = run([node, "--test", "--test-reporter=tap", str(path)], tmp_path)
    assert result.returncode == 0
    report = tmp_path / "actual.tap"
    report.write_text(result.stdout, encoding="utf-8")
    if skip:
        with pytest.raises(AssertionError):
            guard_module().tap(report, 1)
    else:
        assert guard_module().tap(report, 1)["pass"] == 1


@pytest.mark.parametrize("target", ["tests/test_models.py", "pytest.ini", "scripts/export_schema.py"])
def test_tracked_test_config_or_runner_change_rejects(candidate: Path, target: str) -> None:
    done, evidence = invoke(candidate, execute=True, mode="mutate", mutation=candidate / target)
    assert done.returncode != 0
    assert "identity" in receipt(evidence)["failure"].lower()


def test_head_change_after_gate_rejects(candidate: Path) -> None:
    before = git(candidate, "rev-parse", "HEAD")
    done, evidence = invoke(candidate, execute=True, mode="head-change")
    assert before != git(candidate, "rev-parse", "HEAD")
    assert done.returncode != 0
    assert "identity" in receipt(evidence)["failure"].lower()


def test_same_test_process_rejects_foreign_module_origin(candidate: Path) -> None:
    module = guard_module()
    identity = module.snapshot(candidate, Path(__file__).parent)
    expected = candidate.parent / "identity.json"
    expected.write_text(json.dumps(identity), encoding="utf-8")
    write(candidate, "tests/test_models.py", "import sys, types\nm = types.ModuleType('deepviz.normalize')\nm.__file__ = 'C:/foreign/normalize.py'\nsys.modules['deepviz.normalize'] = m\ndef test_synthetic(): assert True\n")
    output = candidate.parent / "origin-control"
    output.mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(candidate / "python/deepviz/src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    done = run([sys.executable, str(Path(__file__).with_name("recipe_guard.py")), "pytest", str(candidate), str(expected), str(output)], candidate, env)
    assert done.returncode != 0
    assert "outside requested checkout" in done.stdout + done.stderr


def test_same_test_process_rejects_source_hash_change(candidate: Path) -> None:
    module = guard_module()
    expected = candidate.parent / "identity.json"
    expected.write_text(json.dumps(module.snapshot(candidate, Path(__file__).parent)), encoding="utf-8")
    write(candidate, "python/deepviz/src/deepviz/models.py", "SYNTHETIC = False\n")
    output = candidate.parent / "hash-control"
    output.mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(candidate / "python/deepviz/src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    done = run([sys.executable, str(Path(__file__).with_name("recipe_guard.py")), "pytest", str(candidate), str(expected), str(output)], candidate, env)
    assert done.returncode != 0
    assert "source hash mismatch" in done.stdout + done.stderr


def test_external_verification_runner_changed_after_preflight_rejects(candidate: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runners = candidate.parent / "copied-NEW-verification"
    runners.mkdir()
    for name in ["recipe_guard.py", "public-origin.mjs", "retest-helper-null.ps1"]:
        shutil.copyfile(Path(__file__).with_name(name), runners / name)
    monkeypatch.setattr(sys.modules[__name__], "RECIPE", runners / "retest-helper-null.ps1")
    done, evidence = invoke(candidate, execute=True, mode="mutate", mutation=runners / "public-origin.mjs")
    assert done.returncode != 0
    assert "identity changed" in receipt(evidence)["failure"].lower()


def test_failed_mutation_receipt_records_actual_post_hash_and_dirty(candidate: Path) -> None:
    done, evidence = invoke(candidate, execute=True, mode="mutate")
    assert done.returncode != 0
    actual = receipt(evidence)["source_after"]
    assert actual["dirty"]
    expected_hash = hashlib.sha256((candidate / "packages/deepviz/src/render.ts").read_bytes()).hexdigest()
    assert actual["tracked_sha256"]["packages/deepviz/src/render.ts"] == expected_hash


@pytest.mark.parametrize("case", ["wrong-head", "dirty", "wrong-test", "wrong-schema"])
def test_original_preflight_gates_are_retained(candidate: Path, case: str) -> None:
    if case == "wrong-head":
        done = run([SHELL or "", "-NoProfile", "-File", str(RECIPE), "-Candidate", str(candidate),
                    "-ExpectedSha", "0" * 40, "-EvidenceDirectory", str(candidate.parent / "evidence"),
                    "-Python", sys.executable, "-ToolsBin", str(candidate.parent)], candidate.parent)
        assert done.returncode != 0
        return
    name = "pytest.ini" if case == "dirty" else REGRESSION if case == "wrong-test" else SCHEMAS[0]
    write(candidate, name, "synthetic changed input\n")
    if case != "dirty":
        git(candidate, "add", ".")
        git(candidate, "-c", "user.name=SyntheticFixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Invalid immutable hash")
    done, evidence = invoke(candidate)
    assert done.returncode != 0
    assert not evidence.exists()
