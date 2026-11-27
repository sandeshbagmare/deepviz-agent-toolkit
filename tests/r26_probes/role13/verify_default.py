"""Run one bounded default-branch probe with source and import provenance."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

OBSERVATIONS: list[dict[str, object]] = []


def git(source: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", *arguments], cwd=source, check=True, capture_output=True
    ).stdout


def validate_identity(
    source: Path, expected_sha: str, expected_model_hash: str, model_origin: Path
) -> None:
    """Reject a different commit, unexpected module origin or altered model."""
    if git(source, "rev-parse", "HEAD").decode().strip() != expected_sha:
        raise RuntimeError("Default source HEAD differs from the pinned SHA")
    expected_origin = source / "python/deepviz/src/deepviz/models.py"
    if model_origin.resolve() != expected_origin.resolve():
        raise RuntimeError("Imported model is outside the default snapshot")
    if hashlib.sha256(model_origin.read_bytes()).hexdigest() != expected_model_hash:
        raise RuntimeError("Imported model bytes differ from the recorded snapshot")
    if git(source, "status", "--porcelain"):
        raise RuntimeError("Default source snapshot is dirty")


def snapshot(source: Path, runner: Path, probe: Path) -> dict[str, str]:
    files = git(source, "ls-files", "-z").decode().split("\0")
    result = {}
    for name in filter(None, files):
        raw = (source / name).read_bytes()
        committed = git(source, "show", "HEAD:" + name)
        if raw.replace(b"\r\n", b"\n") != committed:
            raise RuntimeError("Tracked source bytes differ: " + name)
        result[name] = hashlib.sha256(raw).hexdigest()
    result["OWN_RUNNER"] = hashlib.sha256(runner.read_bytes()).hexdigest()
    result["OWN_PROBE"] = hashlib.sha256(probe.read_bytes()).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--site-packages", required=True, type=Path)
    parser.add_argument("--probe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=("shipped", "probe"), required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    probe = args.probe.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sys.dont_write_bytecode = True
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"  # Child process only.
    if not sys.flags.isolated or not sys.flags.no_site:
        raise RuntimeError("Use python -I -S; do not load editable-install hooks")
    sys.path[:0] = [str(source / "python/deepviz/src"), str(args.site_packages.resolve())]
    runner = Path(__file__).resolve()
    before = snapshot(source, runner, probe)
    models = importlib.import_module("deepviz.models")
    origin = Path(models.__file__).resolve()
    model_hash = before["python/deepviz/src/deepviz/models.py"]
    validate_identity(source, args.sha, model_hash, origin)
    import jsonschema
    import pydantic
    import pytest

    for module in (jsonschema, pydantic, pytest):
        if not Path(module.__file__).resolve().is_relative_to(args.site_packages.resolve()):
            raise RuntimeError("Dependency origin outside explicit read-only site-packages")
    global CONTEXT
    CONTEXT = {"source": source, "sha": args.sha, "model_hash": model_hash, "origin": origin}
    sys.modules["r26_default_guard"] = sys.modules[__name__]
    schema = models.ChartSpec.model_json_schema()
    (output / "generated-schema.json").write_text(
        json.dumps(schema, indent=2) + "\n", encoding="utf-8"
    )
    arguments = [
        str(source if args.mode == "shipped" else probe),
        "-q", "-p", "no:cacheprovider", "--import-mode=importlib",
        "--confcutdir=" + str(source if args.mode == "shipped" else probe.parent),
        "--rootdir=" + str(source if args.mode == "shipped" else probe.parent),
        "--junitxml=" + str(output / "results.xml"),
    ]
    exit_code = int(pytest.main(arguments))
    validate_identity(source, args.sha, model_hash, origin)
    after = snapshot(source, runner, probe)
    if before != after:
        raise RuntimeError("Source/config/test/runner bytes changed during execution")
    suites = ET.parse(output / "results.xml").getroot()
    totals = {
        key: sum(int(s.get(key, "0")) for s in suites.iter("testsuite"))
        for key in ("tests", "failures", "errors", "skipped")
    }
    if args.mode == "probe" and totals["tests"] == 0:
        raise RuntimeError("Probe collected no tests; cannot count process exit as success")
    if args.mode == "shipped" and totals["tests"] == 0 and exit_code != 5:
        raise RuntimeError("Unexpected no-tests exit; foundation is not a passing test suite")
    receipt = {
        "source_commit": args.sha, "source": str(source), "mode": args.mode,
        "python": sys.version, "executable": sys.executable,
        "pytest_version": pytest.__version__, "pydantic_version": pydantic.__version__,
        "jsonschema_origin": str(jsonschema.__file__), "model_origin": str(origin),
        "namespace_paths": list(importlib.import_module("deepviz").__path__),
        "pytest_arguments": arguments, "exit": exit_code, "totals": totals,
        "passed": totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"],
        "all_tracked_and_own_probe_runner_raw_hashes_before": before,
        "all_tracked_and_own_probe_runner_raw_hashes_after": after,
        "same_process_identity_before_after": True, "observations": OBSERVATIONS,
        "no_editable_site_hooks": True, "source_clean": True,
        "scope": "Actual current default foundation only; no PR33/candidate imports",
        "no_shipped_tests_is_not_green": args.mode == "shipped" and totals["tests"] == 0,
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
