"""Generate real public artifacts from an explicitly pinned, clean source."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from fixtures import cases

from deepviz import render


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()

    def git(*arguments: str) -> bytes:
        return subprocess.run(["git", *arguments], cwd=source, check=True, capture_output=True).stdout

    assert git("rev-parse", "HEAD").decode().strip() == args.commit
    assert git("status", "--porcelain", "--", "python/deepviz/src", "schemas") == b""
    identity: dict[str, Any] = {"source": str(source), "commit": args.commit, "python": sys.version,
                                "python_executable": sys.executable, "modules": []}
    for name in ("deepviz", "deepviz.models", "deepviz.engines", "deepviz.render", "deepviz.normalize"):
        module = importlib.import_module(name)
        if module.__file__ is None:
            raise RuntimeError(f"{name} has no source file")
        file = Path(module.__file__).resolve()
        relative = file.relative_to(source).as_posix()
        blob = git("show", args.commit + ":" + relative)
        working = file.read_bytes()
        assert working.replace(b"\r\n", b"\n") == blob, relative
        identity["modules"].append({"name": name, "path": relative,
                                    "git_sha256": hashlib.sha256(blob).hexdigest(),
                                    "working_sha256": hashlib.sha256(working).hexdigest(),
                                    "newline_rule": "CRLF-to-LF only"})
    antv = inspect.getsource(importlib.import_module("deepviz.engines")._antv)
    identity["antv_function_sha256"] = hashlib.sha256(antv.encode()).hexdigest()
    output.mkdir(parents=True, exist_ok=False)
    emitted = []
    for fixture in cases():
        artifact = render(fixture["rows"], fixture["spec"], "antv", output / fixture["id"])
        html = next(Path(name) for name in artifact.paths if name.endswith(".html"))
        manifest = next(Path(name) for name in artifact.paths if name.endswith("manifest.json"))
        emitted.append({**fixture, "html": html.relative_to(output).as_posix(),
                        "manifest": manifest.relative_to(output).as_posix(), "artifact": artifact.to_dict(),
                        "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
                        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()})
    document = {"identity": identity, "cases": emitted, "unmodified_production_html": True,
                "limits": "New R18 execution, not final candidate or independent author approval"}
    (output / "cases.json").write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(json.dumps({"commit": args.commit, "cases": len(emitted), "output": str(output)}))


if __name__ == "__main__":
    main()
