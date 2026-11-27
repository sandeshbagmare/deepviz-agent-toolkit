"""R12 bounded normal-render and sparse-rejection evidence, not a benchmark suite."""
from __future__ import annotations

import gc
import hashlib
import importlib
import json
import subprocess
import sys
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from deepviz import render
from deepviz.tools import ToolSession

source, output = (Path(value).resolve() for value in sys.argv[1:])
output.mkdir(parents=True, exist_ok=False)
modules = {}
for name in ("models", "normalize", "render", "engines", "tools"):
    module = Path(importlib.import_module("deepviz." + name).__file__).resolve()
    assert module.is_relative_to(source / "python/deepviz/src")
    modules[name] = {"path": str(module), "sha256": hashlib.sha256(module.read_bytes()).hexdigest()}

rows = [{"label": "A", "value": 3}, {"label": "B", "value": 7}]
cases = []
for engine in ("matplotlib", "plotly", "vega", "echarts", "antv"):
    spec = {"kind": "table", "aggregation": "none", "title": "R12 table: A=3, B=7",
            "width": 700, "height": 400}
    artifact = render(rows, spec, engine, output / engine)
    paths = [Path(value) for value in artifact.paths]
    manifest = json.loads(next(path for path in paths if path.name == "manifest.json").read_text())
    assert artifact.input_count == artifact.output_count == 2
    assert manifest["charts"][0]["records"] == rows
    cases.append({"engine": engine, "artifact": asdict(artifact),
                  "html": str(next(path for path in paths if path.suffix == ".html")),
                  "files": [{"path": str(path), "bytes": path.stat().st_size,
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]})

sparse = [{f"f{i}": i} for i in range(128)]
rejections = []
for engine in ("matplotlib", "plotly", "vega", "echarts", "antv"):
    rejected_output = output / ("reject-" + engine)
    gc.collect()
    tracemalloc.start()
    started = perf_counter()
    try:
        render(sparse, {"kind": "table", "aggregation": "none"}, engine, rejected_output)
    except ValueError as error:
        message = str(error)
        assert "Dense table" in message and "cell budget" in message
    else:
        raise AssertionError("Sparse grid was rendered without a preflight rejection")
    elapsed = perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert not rejected_output.exists()
    rejections.append({"engine": engine, "input_rows": 128, "input_bytes": len(json.dumps(sparse).encode()),
                       "planned_cells": 16_512, "error": message, "output_exists": False,
                       "elapsed_seconds": elapsed, "tracemalloc_peak_bytes": peak,
                       "tracemalloc_current_bytes": current})

session = ToolSession(output / "tool-output")
session.output_dir.mkdir()
sentinel = session.output_dir / "caller.txt"
sentinel.write_text("preserve", encoding="utf-8")
before = set(session.output_dir.iterdir())
gc.collect()
tracemalloc.start()
started = perf_counter()
try:
    session.render_chart("echarts", sparse, {"kind": "table", "aggregation": "none", "max_points": 1000})
except ValueError as error:
    message = str(error)
    assert "Dense table" in message and "cell budget" in message
else:
    raise AssertionError("ToolSession accepted the sparse amplification")
elapsed = perf_counter() - started
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
assert before == set(session.output_dir.iterdir())
assert sentinel.read_text(encoding="utf-8") == "preserve"
tool = {"api": "ToolSession.render_chart", "input_bytes": 1700, "input_rows": 128,
        "planned_cells": 16_512, "status": "rejected", "error": message,
        "new_artifacts": 0, "caller_preserved": True, "elapsed_seconds": elapsed,
        "tracemalloc_current": current, "tracemalloc_peak": peak}
report = {"source_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip(),
          "tracked_source_diff": subprocess.check_output(["git", "diff", "--name-only", "--",
                                                         "python/deepviz/src"], cwd=source, text=True).splitlines(),
          "modules": modules, "cases": cases, "rejections": rejections, "tool": tool,
          "memory_method": "tracemalloc Python allocator peak, per-call after gc; not OS RSS/native/browser peak",
          "limits": "Bounded two-row table controls plus one128-row sparse fixture; not all kinds,10M or final signoff"}
(output / "generation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({"source_sha": report["source_sha"], "tracked_source_diff": report["tracked_source_diff"],
                  "rendered": len(cases), "rejected": len(rejections), "tool": tool}))
