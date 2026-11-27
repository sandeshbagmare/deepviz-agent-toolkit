"""Capture actual imports and source bytes for a portable, independently run probe."""
from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, timeout=20,
    ).stdout.strip()
    modules = {}
    for name in ("models", "normalize", "tools", "mcp_server", "engines", "render"):
        module = importlib.import_module(f"deepviz.{name}")
        filename = module.__file__
        assert filename is not None, name
        path = Path(filename).resolve()
        assert path == root / "python" / "deepviz" / "src" / "deepviz" / f"{name}.py", name
        modules[name] = {"path": path.relative_to(root).as_posix(),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    result = {
        "observed_at": datetime.now(UTC).isoformat(), "tested_git_head": commit,
        "python": sys.version, "modules": modules,
        "dependencies": {name: importlib.metadata.version(name) for name in ("mcp", "pydantic", "langchain-core")},
    }
    with Path(sys.argv[1]).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
