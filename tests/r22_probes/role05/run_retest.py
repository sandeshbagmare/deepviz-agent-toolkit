"""One clean build, immutable36 tests, and unchanged original40 comparisons."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PIN = "7d8ccdce22430a9ddf3a14a9e64bf15b2373ae57"
TEST = "packages/deepviz/test/test_r07_tool_spec_null.test.mjs"
TEST_HASH = "08be1d15661d6bd5bf87bdcec7db11ba3097d9eee294db654369564716e32227"
ORACLE_HASH = "9b4846c4858ae6f098567245fcce1cc9b4c396ee75cb9315d898bea0bdb1fbde"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True).stdout


def source_identity(root: Path) -> dict[str, Any]:
    assert git(root, "rev-parse", "HEAD").decode().strip() == PIN, "Wrong frozen source"
    assert not git(root, "diff", "HEAD", "--name-only").strip(), "Tracked changes"
    paths = git(root, "ls-tree", "-r", "--name-only", PIN, "--", "packages/deepviz/src",
                "packages/deepviz/package.json", "packages/deepviz/tsconfig.json", "package.json",
                "package-lock.json", TEST, "schemas", "python/deepviz/src").decode().splitlines()
    result = {}
    for name in paths:
        raw, blob = (root / name).read_bytes(), git(root, "show", PIN + ":" + name)
        assert raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), name
        result[name] = {"working_sha256": digest(raw), "git_blob_sha256": digest(blob),
                        "raw_gitblob_exact": raw == blob, "working_crlf": raw.count(b"\r\n"),
                        "git_crlf": blob.count(b"\r\n")}
    assert digest((root / TEST).read_bytes()) == TEST_HASH
    return {"source_commit": PIN, "files": result}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--node", required=True, type=Path)
    parser.add_argument("--tsc", required=True, type=Path)
    parser.add_argument("--wrong-package", required=True, type=Path)
    parser.add_argument("--resume-completed-build", action="store_true")
    args = parser.parse_args()
    root, out = args.source.resolve(), args.artifacts.resolve()
    if args.resume_completed_build:
        assert out.is_dir(), "No completed-build evidence to resume"
    else:
        out.mkdir(exist_ok=False)
    before = source_identity(root)
    if not args.resume_completed_build:
        assert not git(root, "status", "--porcelain").strip(), "Initial checkout not clean"
        assert not (root / "packages/deepviz/dist").exists(), "Stale dist refused"
    assert not (root / "node_modules").exists() and not (root / "packages/deepviz/node_modules").exists()
    assert (args.wrong_package / "dist/index.js").is_file(), "Wrong-origin negative control needs a real other dist"
    oracle = args.oracle.read_bytes()
    assert digest(oracle) == ORACLE_HASH, "Original40 oracle changed"
    probe = root / "tests/r22_probes/role05/probe_tool_schema_refs.py"
    if args.resume_completed_build:
        assert probe.read_bytes() == oracle
    else:
        probe.parent.mkdir(parents=True, exist_ok=False)
        probe.write_bytes(oracle)  # Unchanged original, same parents[3] root semantics.
    assert probe.resolve().parents[3] == root
    tool_paths = [args.node.resolve(), args.tsc.resolve(),
                  args.tsc.resolve().parent.parent / "lib/tsc.js",
                  args.tsc.resolve().parent.parent / "package.json"]
    tools_before = {str(p): digest(p.read_bytes()) for p in tool_paths}
    env = dict(os.environ)
    for key in list(env):
        if key.upper() in {"NODE_OPTIONS", "NODE_PATH", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME"}:
            del env[key]
    env["PATH"] = str(args.node.resolve().parent) + os.pathsep + env["PATH"]
    assert Path(shutil.which("node", path=env["PATH"]) or "").resolve() == args.node.resolve()
    env.update(PYTHONPATH=str(root / "python/deepviz/src"), PYTHONDONTWRITEBYTECODE="1")
    commands: list[dict[str, Any]] = json.loads((out / "commands.json").read_text()) if args.resume_completed_build else []
    if args.resume_completed_build:
        assert [c["name"] for c in commands] == ["fresh-build", "wrong-origin-refused"]
        assert commands[0]["exit"] == 0 and commands[1]["exit"] != 0
        saved_before = json.loads((out / "identity-before.json").read_text())
        assert before == {k: saved_before[k] for k in ["source_commit", "files"]}
        assert tools_before == saved_before["tools"] and digest(oracle) == saved_before["original40_sha256"]

    def run(name: str, argv: list[str], cwd: Path, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=120, check=False)
        (out / (name + ".stdout.log")).write_text(completed.stdout, encoding="utf-8")
        (out / (name + ".stderr.log")).write_text(completed.stderr, encoding="utf-8")
        commands.append({"name": name, "argv": argv, "cwd": str(cwd), "exit": completed.returncode,
                         "expected_exit": expected})
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
        print(name + " exit=" + str(completed.returncode), flush=True)
        assert (completed.returncode == 0) if expected == 0 else (completed.returncode != 0), name
        return completed

    before["tools"] = tools_before
    before["original40_sha256"] = digest(oracle)
    before["own_dist_absent_before_build"] = True
    if not args.resume_completed_build:
        (out / "identity-before.json").write_text(json.dumps(before, indent=2) + "\n", encoding="utf-8")
        run("fresh-build", [str(args.node), str(args.tsc), "-p", str(root / "packages/deepviz/tsconfig.json")], root)
    dist = root / "packages/deepviz/dist"
    built = {p.relative_to(dist).as_posix(): digest(p.read_bytes()) for p in sorted(dist.rglob("*")) if p.is_file()}
    manifest = {"source_commit": PIN, "dist": str(dist), "fresh_build": True, "files": built}
    manifest_path = out / "fresh-build-files.json"
    if args.resume_completed_build:
        assert json.loads(manifest_path.read_text()) == manifest, "Fresh completed build changed before resume"
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    guard = Path(__file__).with_name("guard-imports.mjs").resolve()
    env.update(R22_SOURCE=str(root), R22_DIST_MANIFEST=str(manifest_path),
               R22_IMPORT_LOG=str(out / "imports-positive.ndjson"), NODE_OPTIONS="--import=" + guard.as_uri())
    # Wrong expected public origin must fail before any API call, not redirect it.
    env["R22_IMPORT_LOG"] = str(out / "imports-negative.ndjson")
    negative_name = "wrong-origin-refused-fileuri" if args.resume_completed_build else "wrong-origin-refused"
    negative = run(negative_name, [str(args.node), "--input-type=module", "--eval",
                   "import '@deepviz/agent-toolkit';throw new Error('API sentinel should be unreachable')"],
                   args.wrong_package.resolve(), expected=1)
    assert "R22 public package resolved outside own fresh build" in negative.stderr
    assert "wrong-public-origin-rejected" in (out / "imports-negative.ndjson").read_text()
    env["R22_IMPORT_LOG"] = str(out / "imports-positive.ndjson")
    tests = run("immutable36", [str(args.node), "--test", "--test-reporter=tap", str(root / TEST)], root)
    totals = {}
    for key in ["tests", "pass", "fail", "skipped"]:
        match = re.search(r"^# " + key + r" (\d+)$", tests.stdout, re.M)
        assert match is not None, "Missing actual test total: " + key
        totals[key] = int(match.group(1))
    assert totals == {"tests": 36, "pass": 36, "fail": 0, "skipped": 0}, totals
    (root / "artifacts/r03-09-schema-parity-20261127").mkdir(parents=True, exist_ok=False)
    # Prove loaded Python origins BEFORE unchanged original code executes.
    original_guard = (
        "import hashlib,importlib,pathlib,runpy;"
        f"r=pathlib.Path({str(root / 'python/deepviz/src')!r});"
        "m=importlib.import_module('deepviz.models');t=importlib.import_module('deepviz.tools');"
        "assert pathlib.Path(m.__file__).is_relative_to(r);assert pathlib.Path(t.__file__).is_relative_to(r);"
        f"p=pathlib.Path({str(probe)!r});assert hashlib.sha256(p.read_bytes()).hexdigest()=={ORACLE_HASH!r};"
        "print('Python-before-original40-origins:',m.__file__,t.__file__);"
        "runpy.run_path(str(p),run_name='__main__')"
    )
    wrapper = run("original40", [sys.executable, "-B", "-c", original_guard], root)
    assert '"mismatches": []' in wrapper.stdout
    results = json.loads((root / "artifacts/r03-09-schema-parity-20261127/tool-schema-results.json").read_text())
    assert len(results["outputs"]) == 5 and sum(len(t["results"]) for t in results["outputs"]) == 40
    assert not results["mismatches"] and not results["directNullAccepted"]
    run("python-import-origin", [sys.executable, "-B", "-c", "import importlib,pathlib;"
        "m=importlib.import_module('deepviz.models');t=importlib.import_module('deepviz.tools');"
        f"r=pathlib.Path({str(root / 'python/deepviz/src')!r});"
        "assert pathlib.Path(m.__file__).is_relative_to(r);assert pathlib.Path(t.__file__).is_relative_to(r);"
        "print(m.__file__);print(t.__file__)"], root)
    after = source_identity(root)
    assert after == {k: before[k] for k in ["source_commit", "files"]}
    assert digest(probe.read_bytes()) == ORACLE_HASH
    assert all(digest(p.read_bytes()) == tools_before[str(p)] for p in tool_paths)
    assert built == {p.relative_to(dist).as_posix(): digest(p.read_bytes()) for p in dist.rglob("*") if p.is_file()}
    imports = [json.loads(line) for line in (out / "imports-positive.ndjson").read_text().splitlines()]
    assert sum(i["kind"] == "public-own-dist" for i in imports) >= 2
    summary = {"source_commit": PIN, "source_and_tools_unchanged_after": True,
               "immutable36": totals, "original40": {"compared": 40, "agreed": 40, "mismatches": 0},
               "original40_sha256": ORACLE_HASH, "immutable36_sha256": TEST_HASH,
               "fresh_build_once": True, "public_imports_before_execution": [i for i in imports if i["kind"] == "public-own-dist"],
               "verified_connected_dist_files": sorted({i["relative"] for i in imports if "relative" in i}),
               "wrong_origin_guard_refused_before_api": True, "optional_browser": "NOT_RUN_YET",
               "limits": "Scoped helper/source acceptance, not fullnpm/core689/oldbudget38/integration/CI/release."}
    (out / "identity-after.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
