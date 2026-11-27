"""Prove the exact R34 source dependency and own imports before unchanged tests."""
from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

BASE = "bff9384d1ebe5c8f6f8f0f994300264b32bb98d8"
SOURCE = "9ce04fcc0e91c1896979e3efb9740294dae38240"
NORMALIZER = "c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19"
ANCESTOR = "5ba860305dcc86ac2f95f01705b984d2b40f2799"


def main() -> int:
    root = Path(sys.argv[1]).resolve()

    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=root)

    assert git("rev-parse", "HEAD").decode().strip() == SOURCE, "Use a fresh exact product-head worktree"
    assert not git("status", "--porcelain"), "Do not test dirty source or write probes into the source tree"
    assert git("rev-parse", "c1b0b29").decode().strip() == NORMALIZER
    git("merge-base", "--is-ancestor", ANCESTOR, NORMALIZER)
    sys.path.insert(0, str(root / "python/deepviz/src"))
    origins = {}
    for name, relative, commit in (
        ("deepviz", "python/deepviz/src/deepviz/__init__.py", SOURCE),
        ("deepviz.models", "python/deepviz/src/deepviz/models.py", BASE),
        ("deepviz.normalize", "python/deepviz/src/deepviz/normalize.py", NORMALIZER),
    ):
        module = importlib.import_module(name)
        assert module.__file__ is not None, name
        actual = Path(module.__file__).resolve()
        assert actual == (root / relative).resolve(), name
        raw = actual.read_bytes()
        expected = git("show", commit + ":" + relative)
        assert raw.replace(b"\r\n", b"\n") == expected, name
        origins[name] = {"path": str(actual), "raw_sha256": hashlib.sha256(raw).hexdigest(),
                         "git_blob": git("rev-parse", commit + ":" + relative).decode().strip()}
    print(json.dumps({"source": SOURCE, "normalizer": NORMALIZER, "required_ancestor": ANCESTOR,
                      "same_process_imports": origins}), flush=True)
    import pytest

    return int(pytest.main(sys.argv[2:]))


if __name__ == "__main__":
    raise SystemExit(main())
