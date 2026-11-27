"""Generate fresh real-render artifacts; never reuse another source's HTML."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import get_args

from deepviz.models import ChartKind
from deepviz.render import render


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="NEW directory, must not already exist")
    parser.add_argument("--case", action="append", default=[], help="Only emit these case IDs; may repeat")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    repo = Path(__file__).resolve().parents[3]
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    modules = []
    for name in ("deepviz", "deepviz.models", "deepviz.engines", "deepviz.render"):
        filename = importlib.import_module(name).__file__
        if filename is None:
            raise RuntimeError(f"{name} has no source filename")
        module_path = Path(filename).resolve()
        if not module_path.is_relative_to(repo):
            raise RuntimeError(f"{name} loaded outside this isolated source: {module_path}")
        modules.append({"name": name, "path": str(module_path.relative_to(repo)).replace("\\", "/"),
                        "sha256": hashlib.sha256(module_path.read_bytes()).hexdigest()})
    identity = {"source_sha": sha, "python": sys.version, "python_executable": sys.executable,
                "modules": modules, "source_not_final_frozen": True}
    cases = []
    rows = [{"label": "Alpha", "amount": 12}, {"label": "Beta", "amount": 31},
            {"label": "Gamma", "amount": 7}]

    def emit(engine: str, name: str, data: list[dict], spec: dict, checks: list[str]) -> None:
        if args.case and f"{engine}-{name}" not in args.case:
            return
        artifact = render(data, spec, engine, output / f"{engine}-{name}")
        html = next(Path(path) for path in artifact.paths if path.endswith(".html"))
        manifest = next(Path(path) for path in artifact.paths if path.endswith("manifest.json"))
        cases.append({"id": f"{engine}-{name}", "engine": engine, "name": name, "checks": checks,
                      "html": str(html.relative_to(output)).replace("\\", "/"),
                      "manifest": str(manifest.relative_to(output)).replace("\\", "/"),
                      "title": spec["title"], "expected_y": [row.get(spec.get("y")) for row in data],
                      "input_count": artifact.input_count, "output_count": artifact.output_count})

    for engine in ("plotly", "echarts", "antv"):
        for kind in get_args(ChartKind):
            if kind == "dashboard":
                continue
            data = rows
            spec = {"kind": kind, "x": "label", "y": "amount", "aggregation": "none",
                    "width": 900, "height": 480, "title": f"R10 {engine} {kind}"}
            checks = ["ready", "title", "metadata", "data-toggle", "paint"]
            if kind in {"line", "area"}:
                data = [{"label": 1, "amount": 2}, {"label": 2, "amount": 8},
                        {"label": 4, "amount": 5}]
                if kind == "line":
                    checks.append("numeric-spacing")
            if kind in {"scatter", "bubble", "geo"}:
                data = [{"label": -73, "amount": 40, "radius": 4},
                        {"label": 2, "amount": 49, "radius": 9}]
                if kind == "bubble":
                    spec["size"] = "radius"
            if kind == "heatmap":
                data = [{"label": "Mon", "amount": "AM", "value": -7},
                        {"label": "Tue", "amount": "PM", "value": -2}]
                spec["color"] = "value"
            if kind == "bar":
                checks.extend(["bar-values", "pointer-hover"])
            if engine == "antv" and kind in {"pie", "sunburst", "treemap", "gauge"}:
                checks.append("categorical-fill")
            emit(engine, kind, data, spec, checks)

        for theme in ("light", "dark"):
            children = [{"kind": "bar", "x": "label", "y": "amount", "theme": child,
                         "title": f"Explicit {child} child", "height": 380} for child in ("light", "dark")]
            emit(engine, f"mixed-{theme}", rows, {"kind": "dashboard", "theme": theme, "charts": children,
                 "columns": 2, "width": 1050, "title": f"R10 {engine} {theme} parent"},
                 ["ready", "title", "metadata", "data-toggle", "child-background"])
        data = [{"label": "A", "income": 9, "cost": 2}, {"label": "B", "income": 5, "cost": 4}]
        children = [{"kind": kind, "title": "Same title", "x": "label", "y": field, "height": 380}
                    for kind, field in (("bar", "income"), ("line", "cost"), ("pie", "income"))]
        emit(engine, "duplicate-dashboard", data, {"kind": "dashboard", "charts": children, "columns": 2,
             "width": 1050, "title": f"R10 {engine} duplicate titles"},
             ["ready", "title", "metadata", "data-toggle", "duplicate-containers"])
    if args.case and set(args.case) != {case["id"] for case in cases}:
        raise ValueError("Some requested case IDs do not exist")
    (output / "cases.json").write_text(json.dumps({"identity": identity, "cases": cases}, indent=2),
                                        encoding="utf-8")
    print(json.dumps({"output": str(output), "source_sha": sha, "cases": len(cases)}, indent=2))


if __name__ == "__main__":
    main()
