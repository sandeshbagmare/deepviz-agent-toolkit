"""Pin product/import/SDK bytes without installing, changing, or exercising producer state."""
from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import inspect
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

PIN = "d65dfc0fd807d0335b858476de8cdf7c6b958711"
FILES = ("python/deepviz/src/deepviz/tools.py", "python/deepviz/src/deepviz/mcp_server.py",
         "python/deepviz/src/deepviz/normalize.py", "python/deepviz/src/deepviz/models.py",
         "python/deepviz/tests/test_r14_tool_json_boundary.py")


def main() -> None:
    root = Path(os.environ["R22_02_SOURCE"]).resolve()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, timeout=20)
    assert head.stdout.strip() == PIN
    status = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True, timeout=20)
    assert not status.stdout, status.stdout
    files = {}
    for relative in FILES:
        blob = subprocess.run(["git", "show", f"{PIN}:{relative}"], cwd=root, capture_output=True, check=True, timeout=20).stdout
        assert (root / relative).read_bytes() == blob, relative
        files[relative] = {"git_and_working_sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    origins = {}
    for name in ("tools", "mcp_server", "normalize", "models"):
        module = importlib.import_module(f"deepviz.{name}")
        assert module.__file__ is not None
        path = Path(module.__file__).resolve()
        assert path == root / "python/deepviz/src/deepviz" / f"{name}.py"
        origins[name] = path.relative_to(root).as_posix()
    sdks = {}
    for name in ("langchain_core.tools.base", "mcp.server.fastmcp.utilities.func_metadata", "mcp.server.fastmcp.server"):
        module = importlib.import_module(name)
        filename = inspect.getsourcefile(module)
        assert filename is not None
        path = Path(filename).resolve()
        sdks[name] = {"installed_source": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    result = {"observed_at": datetime.now(UTC).isoformat(), "source_commit": PIN,
              "source_clean": True, "files": files, "origins": origins,
              "dependencies": {name: importlib.metadata.version(name) for name in ("mcp", "langchain-core", "pydantic")},
              "installed_readonly_sdk_files": sdks, "python": sys.version,
              "scope": "P1 committed source only; no dirty P2 source, producer runtime/build/test borrowing"}
    with Path(sys.argv[1]).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
