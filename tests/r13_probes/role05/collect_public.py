"""Collect actual bounded public output and reuse already-produced small renders."""
from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import subprocess
import sys
import time
import tracemalloc
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from budget_probe import fixture, tree_snapshot
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PIN = "5340bc69b7203ad7a9166543062482d819f9b705"
render = importlib.import_module("deepviz.render").render


def collect(artifact: Path, resume: bool = False) -> dict[str, Any]:
    out = artifact / "collection"
    out.mkdir(exist_ok=resume)  # Existing artifacts are read, never rerendered, on resume.
    source = {}
    for module in ("render", "engines", "normalize", "models"):
        loaded = importlib.import_module("deepviz." + module)
        assert loaded.__file__ is not None
        path = Path(loaded.__file__).resolve()
        relative = f"python/deepviz/src/deepviz/{module}.py"
        assert path == ROOT / relative
        original = subprocess.run(["git", "-C", str(ROOT), "show", f"{PIN}:{relative}"],
                                  capture_output=True, check=True).stdout
        assert path.read_text(encoding="utf-8").splitlines() == original.decode().splitlines()
        source[relative] = {"working_bytes_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "pinned_git_blob_sha256": hashlib.sha256(original).hexdigest()}
    summary: dict[str, Any] = {
        "source_checkpoint": PIN, "own_head": subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
        ).stdout.strip(), "source": source, "actual_public_oversize": [], "small_renders": [],
        "memory_method": "tracemalloc started/reset immediately before each render; Python allocations only, NOT RSS/native/process peak",
    }
    for scope in ("table", "dashboard"):
        data, spec = fixture(scope)
        output = out / f"oversize-{scope}"
        metrics: dict[str, Any]
        if resume:
            directories = list(output.glob("deepviz-*"))
            assert len(directories) == 1
            paths = [directories[0] / name for name in ("chart.html", "manifest.json")]
            before = {name: hashlib.sha256(value.encode()).hexdigest() for name, value in (
                ("chart.html", "caller-owned-sentinel"), ("manifest.json", "caller-owned-manifest"),
            )}
            metrics = {"seconds": None, "traced_current_bytes": None, "traced_peak_bytes": None,
                       "note": "Completed artifacts reused after collector failure; first-run in-memory metrics were not persisted."}
        else:
            output.mkdir()
            (output / "chart.html").write_text("caller-owned-sentinel", encoding="utf-8")
            (output / "manifest.json").write_text("caller-owned-manifest", encoding="utf-8")
            before = tree_snapshot(output)
            tracemalloc.start()
            tracemalloc.reset_peak()
            start = time.perf_counter()
            result = render(data, spec, "echarts", output_dir=output)
            seconds = time.perf_counter() - start
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            paths = [Path(p) for p in result.paths]
            metrics = {"seconds": seconds, "traced_current_bytes": current, "traced_peak_bytes": peak}
        manifest = json.loads(next(p for p in paths if p.name == "manifest.json").read_text(encoding="utf-8"))
        after = tree_snapshot(output)
        assert all(after[name] == digest for name, digest in before.items())
        summary["actual_public_oversize"].append({
            "scope": scope, "engine": "echarts", "returned_artifact_instead_of_rejecting": True,
            "source_rows": len(data), "input_count": max(c["input_count"] for c in manifest["charts"]),
            "output_count": sum(c["output_count"] for c in manifest["charts"]),
            "strategy": manifest["strategy"], "warnings": manifest["warnings"],
            "native_graphics": sum(len(p["graphic"]) for p in manifest["native_specs"]),
            **metrics,
            "created_new_artifact_directory": True, "caller_files_preserved": True,
            "artifact_bytes": {p.name: p.stat().st_size for p in paths},
            "limit": "This is a bounded missing-preflight reproduction, NOT a permitted oversized-render pass; browser not executed.",
        })
        (out / "summary-partial.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    targets = []
    for manifest_path in sorted((artifact / "pytest-public").rglob("deepviz-*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not manifest["charts"] or manifest["charts"][0]["spec"]["title"] != "R13 small table":
            continue
        engine = manifest["engine"]
        dashboard = len(manifest["charts"]) == 2
        row = {"engine": engine, "scope": "dashboard" if dashboard else "table",
               "charts": len(manifest["charts"]), "input_counts": [c["input_count"] for c in manifest["charts"]],
               "output_counts": [c["output_count"] for c in manifest["charts"]],
               "warnings": manifest["warnings"], "strategy": manifest["strategy"]}
        if engine == "matplotlib":
            directory = out / f'small-{row["scope"]}'
            directory.mkdir(exist_ok=resume)
            for name in ("chart.png", "chart.svg", "chart.html", "manifest.json"):
                shutil.copyfile(manifest_path.with_name(name), directory / name)
            with Image.open(directory / "chart.png") as image:
                rgb = image.convert("RGB")
                row["png_size"] = list(rgb.size)
                small = rgb.resize((90, 52))
                assert len({small.getpixel((x, y)) for x in range(90) for y in range(52)}) > 2
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            text = " ".join(ET.parse(directory / "chart.svg", parser).getroot().itertext())
            assert "R13 small table" in text and "label" in text and "value" in text
            for literal in ("A", "B", "C", "3", "7", "5"):
                assert literal in text
            targets.append({"name": row["scope"], "html": str(directory / "chart.html")})
        summary["small_renders"].append(row)
    assert len(summary["small_renders"]) == 10 and len(targets) == 2
    (out / "browser-targets.json").write_text(json.dumps(targets, indent=2) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(collect(Path(sys.argv[1]), "--resume-existing" in sys.argv[2:]), indent=2))
