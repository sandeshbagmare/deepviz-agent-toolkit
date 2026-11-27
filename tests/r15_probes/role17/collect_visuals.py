"""Collect genuine baseline output; exit0 means collection, not count fidelity."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
from pathlib import Path

import vl_convert as vlc
from count_contract import COUNT_PAIRS, ENGINES, ROWS, SOURCE_SHA, count_spec, native_values, normalized_count

from deepviz.render import render


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    reduced, spec = normalized_count()
    observed = {engine: native_values(engine, reduced.records, spec) for engine in ENGINES}
    artifacts = {}
    for name in (*ENGINES, "plotly-explicit-y-control"):
        engine = "plotly" if name.endswith("control") else name
        selected = count_spec(y="measure", title="Explicit y COUNT control: A=2, B=3, C=1") if name.endswith("control") else spec
        artifact = render(copy.deepcopy(ROWS), selected, engine, output / name)
        paths = {Path(path).suffix.lstrip("."): Path(path).relative_to(output).as_posix()
                 for path in artifact.paths if Path(path).name != "manifest.json"}
        artifacts[name] = {"engine": engine, "files": paths, "input_count": artifact.input_count,
                           "output_count": artifact.output_count, "strategy": artifact.strategy,
                           "warnings": artifact.warnings}
        if engine == "vega":
            source = output / paths["svg"]
            png = source.with_suffix(".png")
            png.write_bytes(vlc.svg_to_png(source.read_text(encoding="utf-8")))
            paths["png"] = png.relative_to(output).as_posix()
    modules = [importlib.import_module("deepviz." + name) for name in ("normalize", "models", "engines", "render")]
    summary = {"source_sha": SOURCE_SHA, "expected_from_caller": COUNT_PAIRS,
               "observed_native_measures": observed, "count_fidelity": {engine: value == COUNT_PAIRS for engine, value in observed.items()},
               "collection_not_verification": True, "artifacts": artifacts,
               "modules": [{"name": module.__name__, "file": module.__file__,
                            "sha256": hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()} for module in modules]}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"source_sha": SOURCE_SHA, "artifacts": len(artifacts),
                      "count_fidelity": summary["count_fidelity"], "collector_exit_not_fidelity": True}))


if __name__ == "__main__":
    main()
