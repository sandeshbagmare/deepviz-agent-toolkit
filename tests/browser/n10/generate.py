"""Independent N10 known-value artifact producer; no production modifications."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

import deepviz
from deepviz import render

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/local/N10"
OUT.mkdir(parents=True, exist_ok=True)
CASES = json.loads(Path(__file__).with_name("cases.json").read_text())
SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
identity = {
    "source_sha": SHA,
    "source_file": str(Path(deepviz.__file__).resolve()),
    "python": sys.version,
    "packages": {name: importlib.metadata.version(name) for name in ["matplotlib", "plotly", "vl-convert-python", "pydantic"]},
    "schema_sha256": hashlib.sha256((ROOT / "schemas/chart-spec.schema.json").read_bytes()).hexdigest(),
    "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
}
assert str(ROOT / "python/deepviz/src") in identity["source_file"], identity
results = []
for engine in ["matplotlib", "plotly", "vega", "echarts", "antv"]:
    for case in CASES:
        title = f"N10 Python {engine} {case['id']}"
        spec = {"title": title, "width": 800, "height": 460, "aggregation": "none", **case["spec"]}
        result = {"id": f"py-{engine}-{case['id']}", "language": "python", "engine": engine,
                  "case": case["id"], "spec": spec, "oracle": case["oracle"], "input": case["data"]}
        try:
            artifact = render(case["data"], spec, engine=engine, output_dir=OUT / "python" / engine / case["id"])
            result["artifact"] = artifact.to_dict()
            result["path"] = str(next(Path(p) for p in artifact.paths if p.endswith(".html")).relative_to(OUT)).replace("\\", "/")
            result["manifest"] = json.loads(next(Path(p) for p in artifact.paths if p.endswith("manifest.json")).read_text(encoding="utf-8"))
            result["status"] = "generated-not-accepted"
        except Exception as exc:
            result.update(status="generation-failed", error=f"{type(exc).__name__}: {exc}")
        results.append(result)
        print(result["id"], result["status"], result.get("error", ""), flush=True)
        (OUT / "python-manifest.json").write_text(json.dumps({"identity": identity, "cases": results}, indent=2), encoding="utf-8")
print(json.dumps(identity, indent=2))
sys.exit(int(any(item["status"] == "generation-failed" for item in results)))
