"""Same-pytest-process identity proof for this narrow immutable cleanup retest."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

PIN = "5ba860305dcc86ac2f95f01705b984d2b40f2799"
ORIGINAL = "8a10108752567f6d0faac700240c4acf77b32556"
ORACLE = "tests/r13_probes/role15/test_reducer_source_ownership.py"
_BEFORE: dict[str, Any] = {}


def identity() -> dict[str, Any]:
    source = Path(os.environ["DEEPVIZ_R22_SOURCE_ROOT"]).resolve()
    run = Path(os.environ["DEEPVIZ_R22_EXTERNAL_CWD"]).resolve()
    original = Path(os.environ["DEEPVIZ_R22_ORIGINAL_TEST"]).resolve()
    assert Path.cwd().resolve() == run and not run.is_relative_to(source)
    assert not (run / "deepviz.py").exists() and not (run / "deepviz").exists()
    assert subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() == PIN
    assert subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"], text=True) == ""
    modules = {}
    for name in ("__init__", "models", "normalize", "render", "engines"):
        relative = f"python/deepviz/src/deepviz/{name}.py"
        expected = source / relative
        module = importlib.import_module("deepviz" if name == "__init__" else f"deepviz.{name}")
        assert module.__file__ is not None and Path(module.__file__).resolve() == expected
        raw = expected.read_bytes()
        assert raw == subprocess.check_output(["git", "-C", str(source), "show", f"{PIN}:{relative}"])
        modules[relative] = {"real_import_path": str(expected), "sha256": hashlib.sha256(raw).hexdigest()}
    checked = {}
    author = "python/deepviz/tests/test_r17_normalizer_boundaries.py"
    for path, ref in ((source / author, f"{PIN}:{author}"), (original, f"{ORIGINAL}:{ORACLE}"),
                      (source / "pyproject.toml", f"{PIN}:pyproject.toml")):
        raw = path.read_bytes()
        assert raw == subprocess.check_output(["git", "-C", str(source), "show", ref])
        checked[str(path)] = {"git_object": ref, "sha256": hashlib.sha256(raw).hexdigest()}
    for path in (Path(__file__).resolve(), Path(__file__).with_name("test_owned_unwind_review.py").resolve()):
        checked[str(path)] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    return {"target": PIN, "cwd": str(run), "modules": modules, "tests_and_config": checked}


def pytest_sessionstart(session: pytest.Session) -> None:
    global _BEFORE
    _BEFORE = identity()
    Path(os.environ["DEEPVIZ_R22_IDENTITY_RECEIPT"]).write_text(
        json.dumps({"before": _BEFORE, "after": "not yet executed"}, indent=2), encoding="utf-8",
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    after = identity()
    assert after == _BEFORE
    Path(os.environ["DEEPVIZ_R22_IDENTITY_RECEIPT"]).write_text(json.dumps({
        "before": _BEFORE, "after": after, "same_process_before_after_equal": True,
        "pytest_exit": int(exitstatus), "collected_tests": session.testscollected,
        "failed_tests": session.testsfailed,
    }, indent=2), encoding="utf-8")
