"""Prove exact immutable module/test bytes before one unchanged producer consumer.

Run with -B -I -S; explicitly add read-only dependencies without editable .pth
hooks. This wrapper changes no production, fixture, browser or environment file.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import runpy
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["unit", "emit"])
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    proof = json.loads(args.proof.read_text(encoding="utf-8"))
    sha = proof["source_SHA"]

    def verify() -> list[dict]:
        head = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                              capture_output=True, check=True).stdout.decode().strip()
        assert head == sha
        checked = []
        for item in proof["proof"]:
            file = source / item["file"]
            body = file.read_bytes()
            digest = hashlib.sha256(body).hexdigest()
            assert digest == item["Git_sha256"] == item["working_sha256"]
            checked.append({"file": item["file"], "sha256": digest})
        return checked

    before = verify()
    sys.path.insert(0, str(source / "python/deepviz/src"))
    sys.path.append(str(args.site.resolve()))
    origins = []
    for name in ("deepviz", "deepviz.models", "deepviz.normalize", "deepviz.engines", "deepviz.render"):
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        assert path.is_relative_to(source / "python/deepviz/src")
        expected = next(item for item in proof["proof"] if source / item["file"] == path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected["Git_sha256"]
        origins.append({"module": name, "path": str(path), "raw_Git_sha256": expected["Git_sha256"]})
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = {"stage": args.stage, "source_SHA": sha, "python": sys.version,
               "isolated": sys.flags.isolated, "no_site": sys.flags.no_site,
               "before_consumer": before, "actual_module_origins": origins,
               "test_and_browser_unchanged": True, "editable_site_hooks_processed": False}
    (args.output / f"{args.stage}-before.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    test = source / "python/deepviz/tests/test_r20_antv_color_scale.py"
    try:
        if args.stage == "unit":
            import pytest

            result = pytest.main([str(test), "--disable-plugin-autoload", "-q", "--tb=short",
                                  "--basetemp", str(args.output / "pytest-temp"),
                                  "--junitxml", str(args.output / "unit.xml"),
                                  "-o", "cache_dir=" + str(args.output / "pytest-cache")])
            return int(result)
        sys.argv = [str(test), "--emit", str(args.output / "generated"), "--commit", sha]
        runpy.run_path(str(test), run_name="__main__")
        return 0
    finally:
        receipt["after_consumer"] = verify()
        (args.output / f"{args.stage}-after.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
