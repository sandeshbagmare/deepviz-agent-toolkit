"""Run documented local flows with installed tools; save UTF-8 command evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from deepviz import render

ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="checkout-", dir=args.output_dir)).resolve()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "python/deepviz/src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    commands = []
    for action, extra in (
        ("render", ["--spec", "examples/data/chart.json", "--engine", "matplotlib", "--output-dir", str(output / "cli")]),
        ("normalize", ["--spec", "examples/data/chart.json"]),
        ("recommend", ["--goal", "comparison"]),
    ):
        commands.append((f"module-{action}", [sys.executable, "-m", "deepviz.cli", action, "examples/data/sales.csv", *extra]))
        entry = Path(sys.executable).with_name("deepviz.exe" if os.name == "nt" else "deepviz")
        if entry.is_file():
            commands.append((f"entry-{action}", [str(entry), action, "examples/data/sales.csv", *extra]))
    for name, script in (
        ("seven-tools", "multi_tool_flow.py"), ("deep-agent-local", "deep_agent_local.py"),
        ("mcp-client", "mcp_client.py"),
    ):
        commands.append((name, [sys.executable, f"examples/{script}", "--output-dir", str(output / name)]))
    commands.append(("live-provider-help-only", [sys.executable, "examples/deep_agent.py", "--help"]))

    modules = {}
    for name in ("__init__", "models", "normalize", "engines", "render", "tools", "mcp_server"):
        module = importlib.import_module("deepviz" if name == "__init__" else f"deepviz.{name}")
        module_file = module.__file__
        assert module_file is not None, f"Expected a concrete source module: {name}"
        path = Path(module_file).resolve()
        assert path.is_relative_to(ROOT / "python/deepviz/src/deepviz")
        modules[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    summary: dict[str, Any] = {
        "checkpoint": "3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab", "output_dir": str(output),
        "interpreter": sys.executable, "python_version": sys.version, "modules": modules,
        "versions": {name: importlib.metadata.version(name) for name in ("deepagents", "langchain-core", "mcp", "plotly", "matplotlib", "vl-convert-python")},
        "install_probe": {name: importlib.util.find_spec(name) is not None for name in ("build", "hatchling")},
        "skips": ["No dependency installation authorized", "No live provider call", "No browser/CDN execution", "No clean installed consumer or package-publication claim"],
        "commands": [],
    }
    rows = [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}, {"month": "Mar", "revenue": 15}]
    summary["direct_api"] = render(rows, {
        "version": 1, "kind": "bar", "title": "Monthly revenue (USD)", "x": "month",
        "y": "revenue", "max_points": 2000, "aggregation": "auto",
    }, engine="matplotlib", output_dir=output / "api").to_dict()
    failed = []
    for name, command in commands:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=120, check=False)
        stdout, stderr = output / f"{name}.stdout.txt", output / f"{name}.stderr.txt"
        stdout.write_text(result.stdout, encoding="utf-8")
        stderr.write_text(result.stderr, encoding="utf-8")
        summary["commands"].append({"name": name, "argv": command, "exit": result.returncode, "stdout": str(stdout), "stderr": str(stderr)})
        if result.returncode:
            failed.append(name)
    (output / "run-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"summary": str(output / "run-summary.json"), "commands": len(commands), "failed": failed}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
