"""Non-normative public path observations; output is not a test pass or policy."""
from __future__ import annotations

import json
from pathlib import Path

from deepviz import normalize

corpus = json.loads(Path(__file__).with_name("collision-cases.json").read_text(encoding="utf-8"))
observations = []
for case in corpus["observations"]:
    outcome = {"id": case["id"], "classification": case["classification"], "path": case["path"]}
    try:
        result = normalize(case["data"], {"kind": "table", "aggregation": "none", "data_path": case["path"]})
    except ValueError as error:
        outcome["outcome"] = {"error_type": type(error).__name__, "message": str(error)}
    else:
        outcome["outcome"] = {"records": result.records, "input_count": result.input_count,
                              "strategy": result.strategy, "warnings": result.warnings}
    observations.append(outcome)
print(json.dumps({"language": "python", "normative": False, "observations": observations}, ensure_ascii=True, indent=2))
