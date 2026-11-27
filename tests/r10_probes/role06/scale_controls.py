"""Diagnostic-only all-negative heatmap color scales, NOT production fixes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deepviz.engines import browser_html, native_spec
from deepviz.models import ChartSpec

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True, type=Path)
output = parser.parse_args().output.resolve()
output.mkdir(parents=True, exist_ok=False)
rows = [{"day": "Mon", "slot": "AM", "z": -7}, {"day": "Tue", "slot": "PM", "z": -2}]
cases = []
for scale_type in ("linear", "sequential"):
    spec = ChartSpec(kind="heatmap", x="day", y="slot", color="z", title=f"Negative {scale_type} scale control")
    native, _warnings, _kind = native_spec("antv", rows, spec)
    native["scale"] = {"color": {"type": scale_type, "domain": [-7, -2], "range": ["#2166ac", "#b2182b"]}}
    html = browser_html("antv", [native], [spec], spec, [{"records": rows, "input_count": 2,
                        "output_count": 2, "strategy": "none", "warnings": ["Diagnostic-only scale override"]}])
    (output / f"{scale_type}.html").write_text(html, encoding="utf-8")
    cases.append({"id": scale_type, "html": f"{scale_type}.html", "native": native,
                  "production_equivalent": False})
(output / "cases.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
print(json.dumps({"cases": len(cases), "output": str(output)}))
