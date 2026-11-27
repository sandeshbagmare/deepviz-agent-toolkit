"""Fixed helper-retest provenance, same-process Pytest, and report guards."""

from __future__ import annotations

import hashlib
import importlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CORE_FILES = ["test_models.py", "test_schema_contract.py", "test_cross_language_contract.py", "test_n12_authoritative_parity.py"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path, runners: Path, *, allow_dirty: bool = False) -> dict:
    def git(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(root), *args], encoding="utf-8").strip()

    dirty = git("status", "--porcelain", "--untracked-files=all")
    if dirty and not allow_dirty:
        raise AssertionError("Candidate dirty/unapproved untracked input: " + dirty)
    for name in ["deepviz", "deepviz.py", "deepviz.pyc"]:
        if (root / name).exists():
            raise AssertionError("Unexpected CWD Python shadow: " + name)
    paths = [name for name in git("ls-files", "-z").split("\0") if name]
    hashes = {}
    for name in paths:
        path = root / name
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise AssertionError("Tracked path escaped source or missing: " + name)
        hashes[name] = digest(path)
    return {"head": git("rev-parse", "HEAD"), "dirty": dirty, "tracked_sha256": hashes,
            "runner_sha256": {str(path.resolve()): digest(path) for path in sorted(runners.iterdir()) if path.suffix in {".py", ".ps1", ".mjs"}}}


def require_origin(root: Path, identity: dict) -> dict:
    observed = {}
    for name in ["deepviz", "deepviz.models", "deepviz.normalize"]:
        importlib.import_module(name)
    for name, module in list(sys.modules.items()):
        if name != "deepviz" and not name.startswith("deepviz."):
            continue
        origin = getattr(module, "__file__", None)
        if not origin:
            raise AssertionError("Python module has no file origin: " + name)
        path = Path(origin).resolve()
        if not path.is_relative_to(root / "python/deepviz/src/deepviz"):
            raise AssertionError("Python module outside requested checkout: " + name)
        relative = path.relative_to(root).as_posix()
        if identity["tracked_sha256"].get(relative) != digest(path):
            raise AssertionError("Python module source hash mismatch: " + name)
        observed[name] = {"path": str(path), "sha256": digest(path)}
    return observed


def junit(path: Path, minimum: int) -> dict:
    tree = ET.parse(path).getroot()
    suites = list(tree.iter("testsuite"))
    if not suites:
        raise AssertionError("Missing structured JUnit suite")
    totals = {key: sum(int(suite.get(key, "0")) for suite in suites) for key in ["tests", "failures", "errors", "skipped"]}
    totals["passed"] = totals["tests"] - sum(totals[key] for key in ["failures", "errors", "skipped"])
    cases = list(tree.iter("testcase"))
    actual = {"failures": sum(case.find("failure") is not None for case in cases),
              "errors": sum(case.find("error") is not None for case in cases),
              "skipped": sum(case.find("skipped") is not None for case in cases)}
    if any(value < 0 for value in totals.values()) or any(totals[key] != actual[key] for key in actual):
        raise AssertionError("JUnit case status contradicts suite totals")
    if totals["tests"] != len(cases) or totals["tests"] < minimum or totals["passed"] < minimum:
        raise AssertionError("Incomplete JUnit test/pass count: " + str(totals))
    if any(totals[key] for key in ["failures", "errors", "skipped"]):
        raise AssertionError("JUnit failed/error/unapproved skip: " + str(totals))
    return totals


def tap(path: Path, minimum: int) -> dict:
    raw = path.read_bytes()
    text = raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
    values = {}
    for key in ["tests", "pass", "fail", "cancelled", "skipped", "todo"]:
        matches = re.findall(r"^# " + key + r" (\d+)\s*$", text, re.MULTILINE)
        if len(matches) != 1:
            raise AssertionError("Missing/ambiguous structured TAP total: " + key)
        values[key] = int(matches[0])
    plans = re.findall(r"^1\.\.(\d+)\s*$", text, re.MULTILINE)
    suites = re.findall(r"^# suites (\d+)\s*$", text, re.MULTILINE)
    outer_cases = re.findall(r"^ok \d+\b", text, re.MULTILINE)
    all_cases = re.findall(r"^\s*ok \d+\b", text, re.MULTILINE)
    if "TAP version 13" not in text or len(plans) != 1 or int(plans[0]) != len(outer_cases) or len(suites) > 1:
        raise AssertionError("Missing/contradictory TAP header, plan or case records")
    if len(all_cases) != values["tests"] + (int(suites[0]) if suites else 0) or re.search(r"^\s*not ok\b|^\s*ok .*# (?:SKIP|TODO)\b", text, re.MULTILINE | re.IGNORECASE):
        raise AssertionError("TAP cases contradict totals or include failures/skips")
    if values["tests"] != values["pass"] or values["pass"] < minimum or any(values[key] for key in ["fail", "cancelled", "skipped", "todo"]):
        raise AssertionError("Incomplete/failed/unapproved-skipped TAP: " + str(values))
    return values


def guarded_pytest(root: Path, expected: Path, output: Path) -> int:
    import pytest

    identity = json.loads(expected.read_text(encoding="utf-8-sig"))
    record = {"status": "NOT_EXECUTED", "collected": 0, "modules": {}, "files": []}
    sys.path.insert(0, str(root))

    class Guard:
        def pytest_sessionstart(self, session):
            record["modules"] = require_origin(root, identity)

        def pytest_collection_finish(self, session):
            record["collected"] = len(session.items)
            record["files"] = sorted({Path(item.path).name for item in session.items})
            record["modules"] = require_origin(root, identity)

        def pytest_runtest_setup(self, item):
            record["modules"] = require_origin(root, identity)

    try:
        code = int(pytest.main([*("tests/" + name for name in CORE_FILES), "-q", "-o", "addopts=", "-p", "no:cacheprovider", "--junitxml=" + str(output / "core-parity.xml")], plugins=[Guard()]))
        record["modules"] = require_origin(root, identity)
        record["exit"] = code
        record["status"] = "EXECUTED_NOT_YET_VALIDATED"
        if code:
            return code
        totals = junit(output / "core-parity.xml", 4)
        if record["collected"] != totals["tests"] or record["files"] != sorted(CORE_FILES):
            raise AssertionError("Pytest collection identity incomplete")
        record["totals"] = totals
        record["status"] = "SAME_PROCESS_ORIGIN_AND_COUNTS_VERIFIED"
        return 0
    finally:
        (output / "python-origin.json").write_text(json.dumps(record, indent=2), encoding="utf-8")


def main() -> int:
    action = sys.argv[1]
    if action in {"snapshot", "snapshot-after"}:
        print(json.dumps(snapshot(Path(sys.argv[2]).resolve(), Path(__file__).parent, allow_dirty=action == "snapshot-after"), sort_keys=True))
    elif action == "tap":
        print(json.dumps(tap(Path(sys.argv[2]), int(sys.argv[3]))))
    elif action == "pytest":
        return guarded_pytest(Path(sys.argv[2]).resolve(), Path(sys.argv[3]), Path(sys.argv[4]))
    else:
        raise ValueError("Unsupported fixed guard action")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
