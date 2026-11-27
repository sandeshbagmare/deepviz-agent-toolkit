"""Fail-closed identity for the detached SUM consumer and independently emitted JS."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

PIN = "ec9f669eff28cd5351da142765b7755e3b2f484f"
FILES = ("python/deepviz/src/deepviz/normalize.py", "packages/deepviz/src/normalize.ts",
         "python/deepviz/tests/test_r07_finite_overflow.py", "packages/deepviz/test/test_r07_finite_overflow.test.mjs")


def main() -> None:
    root = Path(os.environ["R16_02_SOURCE"]).resolve()
    build = Path(os.environ["R16_02_TS_BUILD"]).resolve()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, timeout=20)
    assert head.stdout.strip() == PIN
    status = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True, timeout=20)
    assert not status.stdout, status.stdout
    files = {}
    for relative in FILES:
        blob = subprocess.run(["git", "show", f"{PIN}:{relative}"], cwd=root, capture_output=True, check=True, timeout=20).stdout
        working = (root / relative).read_bytes()
        assert working == blob, relative
        files[relative] = {"git_and_working_sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    module = importlib.import_module("deepviz.normalize")
    assert module.__file__ is not None
    assert Path(module.__file__).resolve() == root / FILES[0]
    compiled = {name: hashlib.sha256((build / name).read_bytes()).hexdigest()
                for name in ("normalize.js", "normalize.js.map", "models.js")}
    result = {"observed_at": datetime.now(UTC).isoformat(), "source_commit": PIN,
              "clean_detached_source": True, "files": files, "compiled": compiled,
              "python": sys.version, "python_int_max_str_digits": sys.get_int_max_str_digits(),
              "source_scope": "Four committed SUM paths; Python import is own pin; TS emitted by own read-only compiler run"}
    with Path(sys.argv[1]).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
