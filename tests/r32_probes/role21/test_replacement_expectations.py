"""Four independent original semantics on SYNTHETIC fixtures, not DeepViz gates."""
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
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
ORIGINAL = ROOT / "tests/r16_probes/role21/test_retest_preflight.py"
INPUTS = ROOT / "docs/coordination/evidence/R32-21/inputs/role09"
RECIPE = INPUTS / "retest-helper-null.ps1"
EXPECTED_ORACLE = "b9c301946f9b30c6961e7549e3c66ed77be245681f020359d5920503c1200e0a"
PASS = "SCOPED_GATES_PASS_NOT_FINAL_APPROVAL"
SOURCE = "packages/deepviz/src/render.ts"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


assert digest(ORIGINAL) == EXPECTED_ORACLE
spec = importlib.util.spec_from_file_location("immutable_R16_fixture_only", ORIGINAL)
assert spec and spec.loader
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)  # Definitions/fixture only; no old test is executed.


def run(args: list[str], cwd: Path, *, home: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    done = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)
    with (home / "commands.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"argv": args, "cwd": str(cwd), "exit": done.returncode,
                                 "stdout": done.stdout, "stderr": done.stderr}) + "\n")
    return done


@pytest.fixture
def source(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> Path:
    home = tmp_path_factory.mktemp("c")
    root = original.fixture_repo.__wrapped__(home)
    # Reuse original fixture, not any author's test expectation or fixture builder.
    original.write(root, "packages/deepviz/package.json", json.dumps({
        "name": "@deepviz/agent-toolkit", "type": "module",
        "exports": {".": {"import": "./dist/index.js"}},
    }))
    original.write(root, "packages/deepviz/dist/index.js", "export const SYNTHETIC = true;\n")
    original.write(root, "tests/conftest.py", """import hashlib,json,os,sys
from pathlib import Path
import pytest

def pytest_sessionfinish(session,exitstatus):
    modules={}
    for name,module in list(sys.modules.items()):
        if name=='deepviz' or name.startswith('deepviz.'):
            p=Path(module.__file__).resolve()
            modules[name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    Path(os.environ['R32_CHILD_AUDIT']).write_text(json.dumps({
        'pid':os.getpid(),'executable':sys.executable,'pytest_path':pytest.__file__,
        'collected':session.testscollected,'pytest_exit':int(exitstatus),'modules':modules,
    },indent=2),encoding='utf-8')
""")
    original.git(root, "add", ".")
    original.git(root, "-c", "user.name=OfflineFixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Independent SYNTHETIC consumer adapter only")
    manifest = json.loads((ROOT / "docs/coordination/evidence/R32-21/source-manifest.json").read_text())
    assert all(digest(ROOT / row["saved"]) == row["sha256"] for row in manifest)
    (home / "fixture.json").write_text(json.dumps({"test": request.node.nodeid,
        "synthetic_not_DeepViz": True, "head": original.git(root, "rev-parse", "HEAD"),
        "old_oracle_sha256": digest(ORIGINAL), "runner_hashes": {row["source"]: row["sha256"] for row in manifest},
    }, indent=2), encoding="utf-8")
    return root


def invoke(root: Path, *, mode: str, execute: bool = True, duplicate: bool = False) -> tuple[subprocess.CompletedProcess[str], Path]:
    home = root.parent
    shell, node = shutil.which("powershell.exe"), shutil.which("node")
    assert shell and node
    tools = home / "explicit"
    tools.mkdir()
    trace = home / "dispatch.txt"
    npm = '@echo off\necho SYNTHETIC npm stub, no build or product test\necho NPM:%*>>"%R32_TRACE%"\n'
    if mode == "mutate":
        npm += 'echo // independent fixture mutation>>"%R32_SOURCE%"\n'
    npm += ('echo TAP version 13\nfor /L %%i in (1,1,282) do echo ok %%i - SYNTHETIC NOT PRODUCT\n'
            'echo 1..282\necho # tests 282\necho # pass 282\necho # fail 0\necho # cancelled 0\necho # skipped 0\necho # todo 0\nexit /b 0\n')
    node_cmd = ('@echo off\necho NODE:%*>>"%R32_TRACE%"\n'
                'if "%~1"=="--conditions" goto public\n'
                'echo SYNTHETIC node test stub, no product test\necho TAP version 13\n'
                'for /L %%i in (1,1,36) do echo ok %%i - SYNTHETIC NOT PRODUCT\n'
                'echo 1..36\necho # tests 36\necho # pass 36\necho # fail 0\necho # cancelled 0\necho # skipped 0\necho # todo 0\nexit /b 0\n:public\n"%R32_REAL_NODE%" %*\nexit /b %errorlevel%\n')
    original.write(tools, "npm.cmd", npm)
    original.write(tools, "node.cmd", node_cmd)
    env = os.environ.copy()
    env.update(R16_SKIP_ALL="1" if mode == "skip" else "0", R32_SOURCE=str(root / SOURCE),
               R32_TRACE=str(trace), R32_REAL_NODE=node, R32_CHILD_AUDIT=str(home / "child.json"),
               PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    if duplicate:
        duplicates = []
        for name in ["rogue1", "rogue2"]:
            rogue = home / name
            for tool in ["npm.cmd", "node.cmd"]:
                original.write(rogue, tool, '@echo off\necho ROGUE>>"%R32_TRACE%"\nexit /b 97\n')
            duplicates.append(str(rogue))
        env["PATH"] = os.pathsep.join([*duplicates, env["PATH"]])
        where = str(Path(os.environ["SystemRoot"]) / "System32/where.exe")
        for tool in ["npm.cmd", "node.cmd"]:
            found = run([where, tool], home, home=home, env=env)
            assert found.returncode == 0 and all(str(home / name) in found.stdout for name in ["rogue1", "rogue2"])
    evidence = home / "evidence"
    args = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RECIPE),
            "-Candidate", str(root), "-ExpectedSha", original.git(root, "rev-parse", "HEAD"),
            "-EvidenceDirectory", str(evidence), "-Python", sys.executable, "-ToolsBin", str(tools)]
    if execute:
        args.append("-Run")
    tool_paths = [Path(shell), Path(node), Path(sys.executable), tools / "npm.cmd", tools / "node.cmd"]
    before = {str(p): digest(p) for p in tool_paths}
    result = run(args, home, home=home, env=env)
    after = {str(p): digest(p) for p in tool_paths}
    assert before == after and digest(ORIGINAL) == EXPECTED_ORACLE
    (home / "tool-identity.json").write_text(json.dumps({"before": before, "after": after,
        "explicit_args": args, "trace": trace.read_text() if trace.exists() else "",
        "real_Node_only_public_resolution_not_product": node,
    }, indent=2), encoding="utf-8")
    return result, evidence


def receipt(path: Path) -> dict[str, Any]:
    return json.loads((path / "result.json").read_text(encoding="utf-8-sig"))


def test_source_mutation_rejects_and_preserves_pre_post_receipt(source: Path) -> None:
    before = digest(source / SOURCE)
    done, evidence = invoke(source, mode="mutate")
    after = digest(source / SOURCE)
    actual = receipt(evidence)
    pre = json.loads((evidence / "source-before.json").read_text(encoding="utf-8-sig"))
    assert before != after and original.git(source, "status", "--porcelain")
    assert done.returncode != 0 and actual["status"] != PASS
    assert "identity changed" in actual["failure"].lower()
    assert pre["tracked_sha256"][SOURCE] == before
    assert actual["source_after"]["tracked_sha256"][SOURCE] == after and actual["source_after"]["dirty"]
    assert actual["steps"][0]["state"] == "EXECUTED"
    assert all(step["state"] == "NOT_RUN" for step in actual["steps"][1:])


def test_untracked_CWD_shadow_rejects_plan(source: Path) -> None:
    original.write(source, "deepviz/__init__.py", "SHADOW_FIXTURE = True\n")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(source / "python/deepviz/src")
    child = run([sys.executable, "-c", "import deepviz;print(deepviz.__file__)"], source, home=source.parent, env=env)
    assert child.returncode == 0 and Path(child.stdout.strip()) == source / "deepviz/__init__.py"
    done, evidence = invoke(source, mode="shadow", execute=False)
    assert done.returncode != 0 and not evidence.exists()
    assert "shadow" in done.stderr.lower() or "untracked" in done.stderr.lower()


def test_REAL_four_skipped_Pytests_are_rejected(source: Path) -> None:
    done, evidence = invoke(source, mode="skip")
    actual = receipt(evidence)
    suite = ET.parse(evidence / "core-parity.xml").getroot().find("testsuite")
    assert suite is not None and suite.get("tests") == suite.get("skipped") == "4"
    assert suite.get("failures") == suite.get("errors") == "0"
    assert done.returncode != 0 and actual["status"] != PASS
    child = json.loads((source.parent / "child.json").read_text())
    assert child["pytest_exit"] == 0 and child["collected"] == 4
    origin = json.loads((evidence / "python-origin.json").read_text())
    assert origin["exit"] == 0 and origin["collected"] == 4
    assert actual["steps"][7]["exit"] != 0 and actual["steps"][8]["state"] == "NOT_RUN"


def test_duplicate_PATH_dispatches_ONE_explicit_tool_and_real_child_origin(source: Path) -> None:
    done, evidence = invoke(source, mode="pass", duplicate=True)
    assert done.returncode == 0, done.stdout + done.stderr
    actual = receipt(evidence)
    assert actual["status"] == PASS and all(s["state"] == "EXECUTED" for s in actual["steps"])
    for step in actual["steps"]:
        expected = Path(sys.executable) if step["name"] in {"python-schema-check", "core-parity"} else source.parent / "explicit" / ("node.cmd" if step["name"] in {"public-origin", "immutable-regression"} else "npm.cmd")
        assert Path(step["executable"]) == expected
    audit = json.loads((source.parent / "child.json").read_text())
    provenance = actual["steps"][7]["provenance"]
    assert audit["pid"] != os.getpid() and Path(audit["executable"]) == Path(sys.executable)
    assert audit["pytest_exit"] == 0 and audit["collected"] == provenance["totals"]["passed"] == 4
    for name, item in provenance["modules"].items():
        path = Path(item["path"])
        assert path.is_relative_to(source / "python/deepviz/src/deepviz")
        assert item["sha256"] == digest(path) == audit["modules"][name]["sha256"]
    trace = (source.parent / "dispatch.txt").read_text()
    assert "ROGUE" not in trace and trace.count("NODE:") == 2 and trace.count("NPM:") == 5
    assert "Requested candidate public package entry verified" in (evidence / "public-origin.log").read_text(encoding="utf-16")
