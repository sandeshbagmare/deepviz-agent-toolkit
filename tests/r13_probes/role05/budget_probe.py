"""Bounded public-render observations; tripwire failures are never budget passes."""
from __future__ import annotations

import hashlib
import importlib
import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

render_module = importlib.import_module("deepviz.render")
normalize_module = importlib.import_module("deepviz.normalize")
ENGINES = ("matplotlib", "plotly", "vega", "echarts", "antv")


class AllocationReached(RuntimeError):
    """A test-only safe stop, NOT a production resource rejection."""


def fixture(scope: str) -> tuple[list[dict[str, int]], dict[str, Any]]:
    # Both dashboard children fit individually, but their request total exceeds10K.
    rows = 128 if scope == "table" else 80
    data = [{f"field{i}": i} for i in range(rows)]
    table = {"kind": "table", "aggregation": "none", "max_points": 2000}
    spec = table if scope == "table" else {
        "kind": "dashboard", "aggregation": "none", "charts": [table, table],
    }
    return data, spec


def tree_snapshot(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def observe(scope: str, engine: str, output: Path) -> dict[str, Any]:
    data, spec = fixture(scope)
    events: list[str] = []
    normalizations: list[dict[str, Any]] = []
    original_normalize = normalize_module.normalize
    original_mkdir = Path.mkdir
    original_mkdtemp = tempfile.mkdtemp

    def normalize(*args: Any, **kwargs: Any) -> Any:
        result = original_normalize(*args, **kwargs)
        fields = set().union(*(row.keys() for row in result.records))
        normalizations.append({
            "input_count": result.input_count, "output_count": len(result.records),
            "union_fields": len(fields), "expanded_cells_with_header": (len(result.records) + 1) * len(fields),
            "strategy": result.strategy, "warnings": result.warnings,
        })
        return result

    def mkdir(path: Path, *args: Any, **kwargs: Any) -> None:
        if path == output or output in path.parents:
            events.append("output_root_mkdir")
        original_mkdir(path, *args, **kwargs)

    def mkdtemp(*args: Any, **kwargs: Any) -> str:
        if kwargs.get("dir") is not None and Path(kwargs["dir"]) == output:
            events.append("artifact_directory_mkdtemp")
        return original_mkdtemp(*args, **kwargs)

    def tripwire(*args: Any, **kwargs: Any) -> Any:
        events.append("native_or_figure_allocation_reached")
        raise AllocationReached("Missing preflight reached instrumented renderer boundary")

    before = tree_snapshot(output)
    existed = output.exists()
    error = None
    with (
        patch.object(normalize_module, "normalize", normalize),
        patch.object(Path, "mkdir", mkdir),
        patch.object(tempfile, "mkdtemp", mkdtemp),
        patch.object(render_module, "native_spec", tripwire),
        patch.object(render_module, "matplotlib_figure", tripwire),
    ):
        try:
            render_module.render(data, spec, engine, output_dir=output)
        except Exception as exc:
            error = {"type": type(exc).__name__, "message": str(exc)}
    return {
        "scope": scope, "engine": engine, "source_rows": len(data),
        "source_json_bytes": len(json.dumps(data, separators=(",", ":")).encode()),
        "normalizations": normalizations, "events": events, "error": error,
        "output_existed_before": existed, "output_exists_after": output.exists(),
        "files_before": before, "files_after": tree_snapshot(output),
        "limitation": "AllocationReached is a test safety stop, not a production budget ValueError.",
    }
