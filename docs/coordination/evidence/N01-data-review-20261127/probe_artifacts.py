"""Generate actual N01-owned figures and capture source/data boundary evidence."""
from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from deepviz.normalize import normalize
from deepviz.render import render

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).resolve().parent


def source_identity() -> dict[str, Any]:
    modules = [importlib.import_module(f"deepviz.{name}") for name in ("models", "normalize", "render", "engines")]
    return {
        "python": sys.version,
        "executable": sys.executable,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
        "sources": {
            str(module.__file__): hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
            for module in modules
        },
    }


def main() -> None:
    evidence: dict[str, Any] = {"before": source_identity()}
    cases = {
        "count-heatmap": (
            [{"day": "Mon", "region": "North"}] * 2 + [{"day": "Mon", "region": "South"}],
            {"kind": "heatmap", "x": "day", "y": "region", "title": "Counts should be North=2, South=1"},
        ),
        "missing-line": (
            [{"t": 0, "value": 7}, {"t": 1, "value": None}, {"t": 2, "value": 9}],
            {"kind": "line", "x": "t", "y": "value", "title": "Missing t=1 should be a gap, not zero"},
        ),
        "scalar-histogram": (
            [10, 10, 10, 20],
            {"kind": "histogram", "title": "Observations are 10, 10, 10, 20"},
        ),
    }
    evidence["artifacts"] = {}
    for name, (data, spec) in cases.items():
        artifact = render(data, spec, engine="matplotlib", output_dir=OUTPUT / "figures" / name)
        evidence["artifacts"][name] = artifact.to_dict()

    long_cell = "x" * (2 * 1024 * 1024)
    prepared = normalize([{"value": long_cell}], {"kind": "table", "max_points": 10})
    evidence["byte_limit_probe"] = {
        "input_cell_bytes": len(long_cell.encode()),
        "retained_cell_bytes": len(prepared.records[0]["value"].encode()),
        "input_count": prepared.input_count,
        "warnings": prepared.warnings,
        "qualification": "Small 2 MiB cell, not a stress/denial-of-service or peak-memory claim",
    }
    evidence["after"] = source_identity()
    destination = OUTPUT / "artifact-evidence.json"
    destination.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
