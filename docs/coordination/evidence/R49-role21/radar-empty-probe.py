import hashlib
import json
import sys
import traceback
from pathlib import Path
from importlib import import_module

root = Path(__file__).parent
expected_root = (root / "source-3eab/python/deepviz/src/deepviz").resolve()
import deepviz
import deepviz.engines as engines
rendering = import_module("deepviz.render")
from deepviz.models import ChartSpec

assert Path(deepviz.__file__).resolve().parent == expected_root
assert Path(engines.__file__).resolve() == expected_root / "engines.py"
assert Path(rendering.__file__).resolve() == expected_root / "render.py"
assert hashlib.sha256(Path(engines.__file__).read_bytes()).hexdigest() == "a5c39893b011623ea0813b448a988e59f767412d96d4af9b2c07b86b38cae225"

spec = ChartSpec(kind="radar", x="metric", y="score", aggregation="none")
cases = []
for name, rows in (("ordinary_one_record", [{"metric": "A", "score": 4}]), ("empty_records", [])):
    try:
        artifact = rendering.render(rows, spec, engine="echarts", output_dir=root / "actual" / name)
        manifest_path = next(Path(p) for p in artifact.paths if Path(p).name == "manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        native = manifest["native_specs"][0]
        cases.append({"case": name, "status": "RETURNED_ARTIFACT", "input_count": artifact.input_count,
                      "output_count": artifact.output_count, "records": manifest["charts"][0]["records"],
                      "indicator_count": len(native.get("radar", {}).get("indicator", [])),
                      "series_data": native.get("series", [{}])[0].get("data"), "paths": artifact.paths})
    except Exception as error:
        cases.append({"case": name, "status": "RAISED", "error_type": type(error).__name__,
                      "error": str(error), "traceback_tail": traceback.format_exc().splitlines()[-5:]})
result = {"source": "3eab699b61850a20e91132e16caf8c589085f9ee", "adapter": "public render(..., engine='echarts')",
          "module_origins": {"engines": str(Path(engines.__file__).resolve()), "render": str(Path(rendering.__file__).resolve())},
          "cases": cases, "counts": {"cases": len(cases), "returned": sum(c["status"] == "RETURNED_ARTIFACT" for c in cases),
          "raised": sum(c["status"] == "RAISED" for c in cases), "skipped": 0}}
(root / "radar-empty-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(1 if result["counts"]["raised"] else 0)
