"""Compile public tool schema references and compare schema/runtime acceptance."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import jsonschema

from deepviz.tools import NormalizeInput, RenderInput

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "artifacts" / "r03-09-schema-parity-20261127" / "tool-schema-results.json"
NODE_RUNNER = r"""
import {createTools,validateSpec} from '@deepviz/agent-toolkit';
const data=[{category:'A',value:2},{category:'B',value:3}];
const cases=[
  {id:'spec-omitted',input:{data}},
  {id:'spec-empty',input:{data,spec:{}}},
  {id:'spec-null',input:{data,spec:null}},
  {id:'spec-boolean',input:{data,spec:true}},
  {id:'valid-dashboard',input:{data,spec:{kind:'dashboard',charts:[{}]}}},
  {id:'empty-dashboard',input:{data,spec:{kind:'dashboard',charts:[]}}},
  {id:'nested-dashboard',input:{data,spec:{kind:'dashboard',charts:[{kind:'dashboard',charts:[{}]}]}}},
  {id:'child-extra',input:{data,spec:{kind:'dashboard',charts:[{expression:'datum.value'}]}}},
];
const outputs=[];
for(const tool of createTools()) {
  const results=[];
  for(const test of cases) {
    let accepted=false,error;
    try { await tool.invoke(test.input); accepted=true; }
    catch (e) { error=String(e); }
    results.push({...test,accepted,...(error?{error}:{})});
  }
  outputs.push({name:tool.name,schema:tool.inputSchema,results});
}
let directNullAccepted=false;
try {validateSpec(null);directNullAccepted=true;} catch {}
process.stdout.write(JSON.stringify({outputs,directNullAccepted}));
"""


def main() -> None:
    for model in (RenderInput, NormalizeInput):
        schema = model.model_json_schema()
        validator = jsonschema.Draft202012Validator(schema)
        jsonschema.Draft202012Validator.check_schema(schema)
        valid = {"data": [], "spec": {"kind": "dashboard", "charts": [{}]}}
        invalid = {"data": [], "spec": {"kind": "dashboard", "charts": []}}
        assert validator.is_valid(valid)
        assert not validator.is_valid(invalid)
    print("Python RenderInput/NormalizeInput internal references and dashboard controls: PASS", flush=True)

    completed = subprocess.run(
        ["node", "--input-type=module", "--eval", NODE_RUNNER],
        cwd=ROOT / "packages" / "deepviz", text=True, encoding="utf-8",
        capture_output=True, timeout=120, check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"Public npm tools failed ({completed.returncode}): {completed.stderr}")
    results: dict[str, Any] = json.loads(completed.stdout)
    mismatches = []
    for tool in results["outputs"]:
        jsonschema.Draft202012Validator.check_schema(tool["schema"])
        validator = jsonschema.Draft202012Validator(tool["schema"])
        for test in tool["results"]:
            test["schema_accepted"] = validator.is_valid(test["input"])
            if test["schema_accepted"] is not test["accepted"]:
                mismatches.append({
                    "tool": tool["name"], "case": test["id"],
                    "schema_accepted": test["schema_accepted"],
                    "runtime_accepted": test["accepted"],
                })
    results["mismatches"] = mismatches
    ARTIFACT.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"tools": len(results["outputs"]), "cases_per_tool": 8, "directNullAccepted": results["directNullAccepted"], "mismatches": mismatches}, indent=2), flush=True)
    assert not mismatches, "Public tool schema/runtime acceptance differs; see tool-schema-results.json"


if __name__ == "__main__":
    main()
