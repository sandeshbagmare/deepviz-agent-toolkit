"""ONE new opposite-sign MAX heatmap; no browser, matrix, install or oracle change.
Usage: python -B -S this.py EXISTING_SITE_PACKAGES NEW_OUTPUT
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

from source_audit import PIN, ROOT, audit

identity = audit()  # Check all reviewed source bytes BEFORE product imports.
sys.path.insert(0, str(ROOT / "python/deepviz/src"))
sys.path.append(str(Path(sys.argv[1]).resolve()))
out = Path(sys.argv[2]).resolve()
assert not out.exists(), "Preserve previous evidence; select a NEW output directory"
modules = []
for name in ("deepviz", "deepviz.models", "deepviz.engines", "deepviz.render", "deepviz.normalize"):
    module = importlib.import_module(name)
    file = Path(module.__file__).resolve()
    rel = file.relative_to(ROOT).as_posix()
    expected = next(item for item in identity["files"] if item["path"] == rel)
    assert hashlib.sha256(file.read_bytes()).hexdigest() == expected["raw_sha256"]
    modules.append({"module": name, "path": rel, "raw_sha256": expected["raw_sha256"]})

# Endpoint expectations are literal input/range contracts, not adapter-derived values.
values = [-sys.float_info.max, 0.0, sys.float_info.max]
rows = [{"column": label, "row": "Only", "heat": value} for label, value in zip(("Low", "Middle", "High"), values, strict=True)]
spec = {"kind": "heatmap", "x": "column", "y": "row", "color": "heat", "aggregation": "none", "title": "R38-18 opposite-sign MAX endpoint counterexample"}
artifact = importlib.import_module("deepviz.render").render(rows, spec, "antv", out)
manifest_path = next(Path(name) for name in artifact.paths if name.endswith("manifest.json"))
html_path = next(Path(name) for name in artifact.paths if name.endswith(".html"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
assert manifest["charts"][0]["records"] == rows
native = manifest["native_specs"][0]
assert [row["_heat"] for row in native["data"]] == values
assert native["scale"]["color"]["domain"] == [values[0], values[-1]]
result = {"source": PIN, "identity": identity, "actually_imported_modules": modules, "rows": rows, "spec": spec, "native": native, "expected_high_endpoint_rgb": "rgb(8, 29, 88)", "expected_low_endpoint_rgb": "rgb(255, 255, 217)", "limits": "One source-guided public render plus native-scale consumer; NO browser/paint/readiness/console/CDN health or full finite acceptance result.", "artifacts": [{"path": p.relative_to(out).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (manifest_path, html_path)]}
(out / "counterexample.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
print(json.dumps({"source": PIN, "public_render": "completed", "rows": 3, "input_count": artifact.input_count, "output_count": artifact.output_count, "output": str(out), "browser_runs": 0}))
