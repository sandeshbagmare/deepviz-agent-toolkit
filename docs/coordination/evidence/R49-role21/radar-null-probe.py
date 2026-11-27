import hashlib
import json
import sys
import traceback
from pathlib import Path
from importlib import import_module

root = Path(__file__).parent
source = (root / "source-3eab/python/deepviz/src").resolve()
sys.path.insert(0, str(source))
expected_package = source / "deepviz"
import deepviz
import deepviz.engines as engines
rendering = import_module("deepviz.render")
assert Path(deepviz.__file__).resolve().parent == expected_package
assert Path(engines.__file__).resolve() == expected_package / "engines.py"
assert Path(rendering.__file__).resolve() == expected_package / "render.py"
assert hashlib.sha256(Path(engines.__file__).read_bytes()).hexdigest() == "a5c39893b011623ea0813b448a988e59f767412d96d4af9b2c07b86b38cae225"

spec = deepviz.models.ChartSpec(kind="radar", x="metric", y="score", aggregation="none")
cases = [("ordinary_finite_control", [{"metric": "A", "score": 4}, {"metric": "B", "score": 7}]),
         ("one_missing_y_observation", [{"metric": "A", "score": 4}, {"metric": "B", "score": None}])]
results=[]
for name, rows in cases:
    try:
        artifact=rendering.render(rows,spec,engine="echarts",output_dir=root/"actual"/name)
        manifest_path=next(Path(p) for p in artifact.paths if Path(p).name=="manifest.json")
        manifest=json.loads(manifest_path.read_text(encoding="utf-8")); native=manifest["native_specs"][0]
        results.append({"case":name,"status":"ARTIFACT_RETURNED","input_count":artifact.input_count,
          "output_count":artifact.output_count,"normalized_records":manifest["charts"][0]["records"],
          "warnings":manifest["charts"][0]["warnings"],"radar":native.get("radar"),
          "series":native.get("series"),"paths":artifact.paths})
    except Exception as error:
        results.append({"case":name,"status":"EXCEPTION","error_type":type(error).__name__,
          "error":str(error),"traceback_tail":traceback.format_exc().splitlines()[-7:]})
counts={"cases":len(results),"passed":sum(r["status"]=="ARTIFACT_RETURNED" for r in results),
        "failed":sum(r["status"]=="EXCEPTION" for r in results),"skipped":0}
report={"product_source":"3eab699b61850a20e91132e16caf8c589085f9ee","method":"ordinary package render API; isolated selected-source imports; no test harness patches",
 "python":sys.version,"module_origins":{"deepviz":deepviz.__file__,"engines":engines.__file__,"render":rendering.__file__},
 "source_sha256":{"engines.py":hashlib.sha256(Path(engines.__file__).read_bytes()).hexdigest(),"render.py":hashlib.sha256(Path(rendering.__file__).read_bytes()).hexdigest()},"cases":results,"counts":counts,
 "oracle_basis":"_geometry emits a radar warning that missing/non-numeric y remains a gap, not zero; expected public result is handled chart or explicitly documented rejection, not unhandled TypeError before artifact."}
(root/"radar-null-result.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2));raise SystemExit(1 if counts["failed"] else 0)
