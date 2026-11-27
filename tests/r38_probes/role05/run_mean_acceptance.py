"""Run one pinned mean-only gate with same-process BEFORE-consumer provenance."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import FrameType
from typing import Any

PIN = "c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19"
PRODUCER = "python/deepviz/tests/test_r17_normalizer_boundaries.py"
PRODUCER_SHA = "95e9bd99773fcc0729215dc4605e78aad35158c68579fe7f31c6516bcb8a8a11"
NORMALIZE_SHA = "f3cc6e78e188ed97f62133a954154dbfdd416128c97cd4b154144ae62f778296"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--site-packages", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    root = args.source.resolve()
    out = args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    probe = Path(__file__).with_name("test_python_mean.py").resolve()

    def save(name: str, obj: Any) -> None:
        (out / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    def git(*argv: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *argv])

    save("attempt.json", {"argv": sys.argv, "pid": os.getpid(), "state": "PREFLIGHT"})
    assert sys.flags.no_site and sys.dont_write_bytecode, "Use -B -S; never process editable hooks"
    assert git("rev-parse", "HEAD").decode().strip() == PIN
    assert not git("status", "--porcelain").strip(), "The exact source checkout must be clean"
    paths = [p for p in git("ls-tree", "-r", "--name-only", PIN).decode().splitlines()
             if p.startswith("python/deepviz/src/") and p.endswith(".py")]
    paths += ["pyproject.toml", "schemas/chart-spec.schema.json", PRODUCER]
    raw = {p: git("show", f"{PIN}:{p}") for p in paths}
    assert sha(raw[PRODUCER]) == PRODUCER_SHA
    assert sha(raw["python/deepviz/src/deepviz/normalize.py"]) == NORMALIZE_SHA
    assert not list((root / "python/deepviz/src").rglob("*.pyc"))
    assert not any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules)
    probe_raw = probe.read_bytes()
    wrapper_raw = Path(__file__).read_bytes()

    def disk_guard() -> None:
        for relative, expected in raw.items():
            assert (root / relative).read_bytes() == expected, f"RAW Gitblob drift: {relative}"
        assert probe.read_bytes() == probe_raw and Path(__file__).read_bytes() == wrapper_raw

    disk_guard()  # BEFORE any product import.
    sys.path[:0] = [str(root / "python/deepviz/src"), str(args.site_packages.resolve())]
    module = importlib.import_module("deepviz.normalize")
    package = importlib.import_module("deepviz")
    function = module.normalize
    code_object = function.__code__

    def identity() -> dict[str, Any]:
        disk_guard()
        loaded = {}
        for name, obj in tuple(sys.modules.items()):
            if name == "deepviz" or name.startswith("deepviz."):
                filename = obj.__file__
                assert filename is not None, f"Unexpected namespace product module: {name}"
                path = Path(filename).resolve()
                relative = path.relative_to(root).as_posix()
                assert relative in raw and path.read_bytes() == raw[relative], name
                loaded[name] = {"path": str(path), "sha256": sha(raw[relative])}
        assert package.normalize is module.normalize is function and function.__code__ is code_object
        assert Path(code_object.co_filename).resolve() == root / "python/deepviz/src/deepviz/normalize.py"
        return {"commit": PIN, "loaded_modules": loaded,
                "raw_Gitblob_SHA256": {p: sha(value) for p, value in raw.items()},
                "raw_equals_Git_LF": True, "newline_conversion": "NONE; exact bytes required",
                "probe_sha256": sha(probe_raw), "wrapper_sha256": sha(wrapper_raw)}

    before = identity()
    import pytest

    save("identity-before.json", {**before, "python": sys.version, "executable": sys.executable,
                                  "pytest": pytest.__version__, "no_site": sys.flags.no_site,
                                  "bytecode_disabled": sys.dont_write_bytecode,
                                  "env_mutations": 0, "editable_hooks_processed": 0})
    results: list[dict[str, Any]] = []
    consumers: list[dict[str, Any]] = []
    collected: list[str] = []
    current = "BEFORE_TESTS"

    def profile(frame: FrameType, event: str, arg: Any) -> None:
        if event == "call" and frame.f_code is code_object:
            actual = identity()  # Before the first instruction of EVERY public consumer call.
            consumers.append({"nodeid": current, "sequence": len(consumers) + 1,
                              "normalize_origin": actual["loaded_modules"]["deepviz.normalize"],
                              "all_source_config_schema_producer_probe_bytes_verified": True})

    class Guard:
        def pytest_collection_finish(self, session: Any) -> None:
            assert len(session.items) == 76, f"Expected21producer+55NEW, got{len(session.items)}"
            for item in session.items:
                path = Path(item.path).resolve()
                assert path in {root / PRODUCER, probe}
                if path == root / PRODUCER:
                    assert item.originalname in {
                        "test_mean_rounds_exact_finite_rational_once",
                        "test_other_mean_uses_all_numeric_contributions_not_boolean_or_null",
                    }, "No lifetime/SUM/full-format replay"
            collected.extend(item.nodeid for item in session.items)
            save("collected.json", {"count": len(collected), "nodeids": collected})

        def pytest_runtest_setup(self, item: Any) -> None:
            nonlocal current
            current = item.nodeid
            identity()
            assert item.module.normalize is function

        def pytest_runtest_logreport(self, report: Any) -> None:
            results.append({"nodeid": report.nodeid, "when": report.when, "outcome": report.outcome,
                            "duration": report.duration, "properties": list(report.user_properties),
                            "failure_or_skip": str(report.longrepr) if report.failed or report.skipped else None})

    argv = [str(root / PRODUCER) + "::test_mean_rounds_exact_finite_rational_once",
            str(root / PRODUCER) + "::test_other_mean_uses_all_numeric_contributions_not_boolean_or_null",
            str(probe), "-c", str(root / "pyproject.toml"), "--noconftest", "--disable-plugin-autoload",
            "--import-mode=importlib", "-q", "--strict-markers", "--strict-config", "-rs", "--tb=short",
            "-p", "no:cacheprovider", "-o", "junit_family=legacy", "--basetemp", str(out / "pytest-temp"),
            "--junitxml", str(out / "mean.xml")]
    save("pytest-command.json", {"process_argv": sys.argv, "same_process_pytest_argv": argv,
                                "cwd": str(Path.cwd()), "env_mutations": 0})
    started = time.perf_counter()
    sys.setprofile(profile)
    try:
        exit_code = int(pytest.main(argv, plugins=[Guard()]))
    finally:
        sys.setprofile(None)
        save("before-consumer-origins.json", consumers)
        save("case-reports.json", results)
    elapsed = time.perf_counter() - started
    after = identity()
    assert git("rev-parse", "HEAD").decode().strip() == PIN and not git("status", "--porcelain").strip()
    save("identity-after.json", after)
    calls = [item for item in results if item["when"] == "call"]
    summary = {"source_commit": PIN, "pytest_exit": exit_code, "elapsed_seconds": elapsed,
               "collected": len(collected), "passed_calls": sum(item["outcome"] == "passed" for item in calls),
               "failed_reports": [item for item in results if item["outcome"] == "failed"],
               "skipped_reports": [item for item in results if item["outcome"] == "skipped"],
               "before_consumer_guards": len(consumers), "fresh_product_gate_executions": 1,
               "unchanged_after": before == after, "source_tree_clean_after": True,
               "scope": "Exact c1b mean ONLY; not later546c, scalar/GraphQL/prefixSUM, integrated package or release"}
    save("summary.json", summary)
    print(json.dumps(summary, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
