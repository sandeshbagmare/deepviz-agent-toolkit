"""Run all seven tools without an LLM; save actual outputs and a compact manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from deepviz import create_tools

DATA = [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}, {"month": "Mar", "revenue": 15}]
SPEC = {"kind": "bar", "x": "month", "y": "revenue", "title": "Monthly revenue"}


def run(output_dir: str | Path) -> dict:
    tools = {tool.name: tool for tool in create_tools(output_dir)}
    normalized = tools["normalize_data"].invoke({"data": DATA, "spec": SPEC})
    reference = {"dataset_id": normalized["dataset_id"]}
    advice = tools["recommend_chart"].invoke({"data": reference, "goal": "comparison"})
    outputs = {"normalize_data": normalized, "recommend_chart": advice}
    for engine in ("matplotlib", "plotly", "vega", "echarts", "antv"):
        outputs[f"render_{engine}"] = tools[f"render_{engine}"].invoke({"data": reference, "spec": SPEC})
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="artifacts/local/integrations")
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), indent=2))


if __name__ == "__main__":
    main()
