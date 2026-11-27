"""Real unmocked reject observations and fresh small-render artifact inspection."""
from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image

render = importlib.import_module("deepviz.render").render


def snapshot(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()} if root.exists() else {}


def collect(artifact: Path) -> dict[str, Any]:
    out = artifact / "collection"
    out.mkdir()  # Never overwrite an earlier observation.
    result: dict[str, Any] = {"source_commit": "1c721bb6497746641b897eb2eb938cfad52068d2",
                              "actual_rejections": [], "small_renders": [],
                              "limits": "No memory/latency measurement or later-head/full-release signoff."}
    for scope in ("table", "dashboard"):
        rows = 128 if scope == "table" else 80
        data = [{f"field{i}": i} for i in range(rows)]
        table: dict[str, Any] = {"kind": "table", "aggregation": "none", "max_points": 2000}
        spec = table if scope == "table" else {"kind": "dashboard", "aggregation": "none", "charts": [table, table]}
        caller = out / f"caller-{scope}"
        caller.mkdir()
        (caller / "chart.html").write_text("existing caller artifact", encoding="utf-8")
        (caller / "manifest.json").write_bytes(b"existing caller manifest\x00\xff")
        output = caller / "must-remain-absent"
        before = snapshot(caller)
        try:
            render(data, spec, "echarts", output_dir=output)  # No mocks or monkeypatches.
        except ValueError as exc:
            assert len(str(exc)) < 180 and "cell budget" in str(exc)
            rejection = {"type": type(exc).__name__, "message": str(exc)}
        else:
            raise AssertionError("Real oversized public render returned instead of rejecting")
        assert not output.exists() and snapshot(caller) == before
        result["actual_rejections"].append({"scope": scope, "engine": "echarts",
            "source_rows": rows, "source_compact_json_bytes": len(json.dumps(data, separators=(",", ":")).encode()),
            "error": rejection, "output_created": False, "caller_files_unchanged": True,
            "files_before": before, "files_after": snapshot(caller)})
        (out / "partial.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    targets = []
    for manifest_path in sorted((artifact / "pytest-unchanged-r13").rglob("deepviz-*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        children = manifest["charts"]
        assert children and all(c["records"] == [
            {"label": "A", "value": 3}, {"label": "B", "value": 7}, {"label": "C", "value": 5},
        ] for c in children)
        dashboard = len(children) == 2
        control = {"engine": manifest["engine"], "scope": "dashboard" if dashboard else "table",
                   "input_counts": [c["input_count"] for c in children],
                   "output_counts": [c["output_count"] for c in children],
                   "strategy": manifest["strategy"], "warnings": manifest["warnings"]}
        if manifest["engine"] == "matplotlib":
            directory = out / f'small-{control["scope"]}'
            directory.mkdir()
            for name in ("chart.png", "chart.svg", "chart.html", "manifest.json"):
                shutil.copyfile(manifest_path.with_name(name), directory / name)
            with Image.open(directory / "chart.png") as image:
                rgb = image.convert("RGB")
                control["png_size"] = list(rgb.size)
                small = rgb.resize((90, 52))
                assert len({small.getpixel((x, y)) for x in range(90) for y in range(52)}) > 2
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            labels = " ".join(ET.parse(directory / "chart.svg", parser).getroot().itertext())
            assert all(text in labels for text in ("R13 small table", "label", "value", "A", "B", "C", "3", "7", "5"))
            targets.append({"name": control["scope"], "html": str(directory / "chart.html")})
        result["small_renders"].append(control)
    assert len(result["small_renders"]) == 10 and len(targets) == 2
    (out / "browser-targets.json").write_text(json.dumps(targets, indent=2) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(collect(Path(sys.argv[1])), indent=2))
