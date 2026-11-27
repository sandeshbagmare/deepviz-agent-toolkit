"""Collect exact-commit COUNT output; assertions, not collector exits, prove values."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import vl_convert as vlc

from deepviz.render import render


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--oracle-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.source.resolve(), args.output.resolve()
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == args.expected_sha
    modules = {}
    for name in ("models", "normalize", "engines", "render"):
        module = importlib.import_module("deepviz." + name)
        relative = f"python/deepviz/src/deepviz/{name}.py"
        loaded = Path(module.__file__).resolve()
        expected = subprocess.check_output(["git", "show", args.expected_sha + ":" + relative], cwd=root)
        assert loaded == root / relative and loaded.read_bytes() == expected
        modules[name] = {"origin": str(loaded), "bytes": len(expected), "sha256": hashlib.sha256(expected).hexdigest()}
    sys.path.insert(0, str(args.oracle_dir.resolve()))
    contract = importlib.import_module("count_contract")
    oracle_data = subprocess.check_output(["git", "show",
        "76cac9d05b0b4abc94e5ff316e3de4d3bc835b79:tests/r15_probes/role17/count_contract.py"], cwd=root)
    assert Path(contract.__file__).read_bytes() == oracle_data
    output.mkdir(exist_ok=False)
    records, spec = contract.normalized_count()
    expected_pairs = [("A", 2), ("B", 3), ("C", 1)]
    observed = {engine: contract.native_values(engine, records.records, spec) for engine in contract.ENGINES}
    assert all(values == expected_pairs for values in observed.values())
    summary = {"source_sha": args.expected_sha, "source_modules": modules,
               "expected_from_caller": expected_pairs, "observed_native_measures": observed,
               "count_fidelity": {engine: values == expected_pairs for engine, values in observed.items()},
               "collection_not_verification": False, "oracle_commit": "76cac9d05b0b4abc94e5ff316e3de4d3bc835b79",
               "artifacts": {}}
    for name in (*contract.ENGINES, "plotly-explicit-y-control"):
        engine = "plotly" if name.endswith("control") else name
        selected = contract.count_spec(y="measure", title="Explicit y COUNT control: A=2, B=3, C=1") if name.endswith("control") else spec
        artifact = render(copy.deepcopy(contract.ROWS), selected, engine, output / name)
        assert (artifact.input_count, artifact.output_count, artifact.strategy) == (6, 3, "count")
        manifest_path = next(Path(path) for path in artifact.paths if Path(path).name == "manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        chart = manifest["charts"][0]
        assert [row["measure" if name.endswith("control") else "count"] for row in chart["records"]] == [2, 3, 1]
        assert (chart["input_count"], chart["output_count"], chart["strategy"]) == (6, 3, "count")
        paths = {Path(path).suffix.lstrip("."): Path(path).relative_to(output).as_posix()
                 for path in artifact.paths if Path(path).name != "manifest.json"}
        if engine == "vega":
            source = output / paths["svg"]
            png = source.with_suffix(".png")
            png.write_bytes(vlc.svg_to_png(source.read_text(encoding="utf-8")))
            paths["png"] = png.relative_to(output).as_posix()
        summary["artifacts"][name] = {"engine": engine, "files": paths, "input_count": artifact.input_count,
            "output_count": artifact.output_count, "strategy": artifact.strategy, "warnings": artifact.warnings}
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha": args.expected_sha, "artifacts": 6, "count_fidelity": summary["count_fidelity"]}))


if __name__ == "__main__":
    main()
