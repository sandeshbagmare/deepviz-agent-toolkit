"""One sealed-source, same-process immutable 69-case ownership acceptance run."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PIN = "5ba860305dcc86ac2f95f01705b984d2b40f2799"
ORACLES = (
    (PIN, "python/deepviz/tests/test_r17_normalizer_boundaries.py",
     "4451d287cfba3cf2e18a3c5174341eeee30436b0304d6e6591c83125a0629068"),
    ("60599dd209e60eae559e721bc7bb200a47e3032f", "tests/r10_probes/role15/test_owned_input_cleanup.py",
     "43279c443d9eb76b22f39a80cd4bfcbfcca058193cf8e96780f7c5763c7729a0"),
    ("8a10108752567f6d0faac700240c4acf77b32556", "tests/r13_probes/role15/test_reducer_source_ownership.py",
     "5a9ebaba4968381624d20f646afbd8105531be4bfd179fe56fa5accb7118314e"),
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--oracles", type=Path, required=True)
    parser.add_argument("--site-packages", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    root, external = args.source.resolve(), args.oracles.resolve()
    out = args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)

    def save(name: str, data: Any) -> None:
        (out / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    save("attempt.json", {"argv": sys.argv, "pid": os.getpid(), "status": "PREFLIGHT"})

    def git(*argv: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *argv])

    assert sys.flags.no_site and sys.dont_write_bytecode, "Run with -B -S; no editable .pth processing"
    assert os.environ.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD") == "1"
    assert git("rev-parse", "HEAD").decode().strip() == PIN
    assert not git("status", "--porcelain").strip(), "Source must start clean, not producer dirty work"
    source_paths = [p for p in git("ls-tree", "-r", "--name-only", PIN).decode().splitlines()
                    if p.startswith("python/deepviz/src/") and p.endswith(".py")]
    config_paths = ["pyproject.toml", "schemas/chart-spec.schema.json"]
    raw_files = {p: git("show", f"{PIN}:{p}") for p in source_paths + config_paths}
    tests: list[Path] = []
    for index, (commit, relative, digest) in enumerate(ORACLES):
        raw = git("show", f"{commit}:{relative}")
        path = (root if index == 0 else external) / relative
        assert sha(raw) == digest and path.read_bytes() == raw, f"Immutable oracle mismatch: {relative}"
        tests.append(path)
    assert {p.relative_to(root).as_posix() for p in (root / "python/deepviz/src").rglob("*.py")} == set(source_paths)
    for relative, raw in raw_files.items():
        assert (root / relative).read_bytes() == raw, f"Pre-import source/config mismatch: {relative}"
    assert not list((root / "python/deepviz/src").rglob("*.pyc")), "No pre-existing source bytecode"
    for path in tests:
        assert not list((path.parent / "__pycache__").glob(path.stem + ".*.pyc")), path
    assert not any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules)
    sys.path[:0] = [str(root / "python/deepviz/src"), str(args.site_packages.resolve())]
    normalize_module = importlib.import_module("deepviz.normalize")
    package = importlib.import_module("deepviz")
    normalize_function = normalize_module.normalize

    def identity() -> dict[str, Any]:
        assert git("rev-parse", "HEAD").decode().strip() == PIN
        for relative, raw in raw_files.items():
            assert (root / relative).read_bytes() == raw, f"Source/config drift: {relative}"
        for path, (_, _, digest) in zip(tests, ORACLES, strict=True):
            assert sha(path.read_bytes()) == digest, f"Oracle drift: {path.name}"
        modules = {}
        for name, module in tuple(sys.modules.items()):
            if name == "deepviz" or name.startswith("deepviz."):
                filename = module.__file__
                assert filename is not None
                actual = Path(filename).resolve()
                relative = actual.relative_to(root).as_posix()
                assert relative in raw_files and actual.read_bytes() == raw_files[relative], name
                modules[name] = {"origin": str(actual), "sha256": sha(actual.read_bytes())}
        assert package.normalize is normalize_module.normalize is normalize_function
        assert Path(normalize_function.__code__.co_filename).resolve() == root / "python/deepviz/src/deepviz/normalize.py"
        return {"source_commit": PIN, "modules": modules,
                "raw_gitblob_exact": {p: sha(raw) for p, raw in raw_files.items()},
                "oracles": [{"file": str(path), "commit": commit, "sha256": digest}
                            for path, (commit, _, digest) in zip(tests, ORACLES, strict=True)]}

    before = identity()
    import pytest

    try:
        arrow = importlib.import_module("pyarrow")
        arrow_info = {"available": True, "version": arrow.__version__, "origin": arrow.__file__}
    except ImportError as error:
        arrow_info = {"available": False, "reason": str(error)}
    save("identity-before.json", {**before, "python": sys.version, "executable": sys.executable,
                                  "platform": platform.platform(), "pytest": pytest.__version__,
                                  "pyarrow": arrow_info, "no_site": sys.flags.no_site,
                                  "bytecode_disabled": sys.dont_write_bytecode})
    results: list[dict[str, Any]] = []
    origins: list[dict[str, Any]] = []

    class Guard:
        def pytest_collection_finish(self, session: Any) -> None:
            assert len(session.items) == 69, f"Expected immutable69, got {len(session.items)}"
            assert {Path(item.path).resolve() for item in session.items} == set(tests)
            save("collected.json", {"count": 69, "nodeids": [i.nodeid for i in session.items]})

        def pytest_runtest_setup(self, item: Any) -> None:
            current = identity()
            assert item.module.normalize is normalize_function, "Test function bound to wrong public API"
            origins.append({"nodeid": item.nodeid, "normalize_origin": current["modules"]["deepviz.normalize"],
                            "public_export_same_function": True})
            save("before-case-origins.json", origins)

        def pytest_runtest_logreport(self, report: Any) -> None:
            results.append({"nodeid": report.nodeid, "when": report.when, "outcome": report.outcome,
                            "duration": report.duration, "properties": list(report.user_properties),
                            "failure_or_skip": str(report.longrepr) if report.failed or report.skipped else None})
            save("case-reports.json", results)

    argv = [*(str(path) for path in tests), "-c", str(root / "pyproject.toml"), "--noconftest",
            "--import-mode=importlib", "-q", "--strict-markers", "--strict-config", "-rs", "--tb=short",
            "-p", "no:cacheprovider", "-o", "junit_family=legacy", "--basetemp", str(out / "pytest-temp"),
            "--junitxml", str(out / "strict69.xml")]
    save("pytest-command.json", {"process_argv": sys.argv, "same_process_pytest_main_argv": argv,
                                "cwd": str(Path.cwd()), "environment": {
                                    key: os.environ.get(key) for key in
                                    ("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "PYTHONDONTWRITEBYTECODE", "PYTHONPATH")}})
    started = time.perf_counter()
    code = int(pytest.main(argv, plugins=[Guard()]))
    elapsed = time.perf_counter() - started
    after = identity()
    save("identity-after.json", after)
    calls = [r for r in results if r["when"] == "call"]
    failed = [r for r in results if r["outcome"] == "failed"]
    skipped = [r for r in results if r["outcome"] == "skipped"]
    summary = {"source_commit": PIN, "pytest_exit": code, "elapsed_seconds": elapsed,
               "passed_calls": sum(r["outcome"] == "passed" for r in calls), "failed_reports": len(failed),
               "skipped_reports": len(skipped), "collected": 69, "guarded_before_cases": len(origins),
               "same_process_origin_guard": True, "source_oracles_unchanged_after": True,
               "pyarrow": arrow_info, "failures": failed, "skips": skipped,
               "scope": "Exact5ba ownership only; not later extraction/foundation/fullsuite/release approval"}
    save("summary.json", summary)
    print(json.dumps(summary, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
