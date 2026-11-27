"""Compare real static SVG geometry with independent known-value oracles."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/local/N10"
manifest = json.loads((OUT / "python-manifest.json").read_text(encoding="utf-8"))
checks = []
number = r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?"


def check(name, condition, evidence):
    checks.append({"name": name, "pass": bool(condition), "evidence": evidence})


for case in manifest["cases"]:
    if case["engine"] not in {"matplotlib", "vega"}:
        continue
    source = next(Path(p) for p in case["artifact"]["paths"] if p.endswith(".svg"))
    svg = ET.fromstring(source.read_text(encoding="utf-8"))
    if case["engine"] == "vega":
        mark_groups = [e for e in svg.iter() if "role-mark" in e.attrib.get("class", "").split()]
        marks = [p for g in mark_groups for p in g.iter() if p.tag.endswith("path") and "d" in p.attrib]
        info = [{"aria": e.attrib.get("aria-label"), "path": e.attrib.get("d"), "fill": e.attrib.get("fill"), "transform": e.attrib.get("transform")} for e in marks]
        expected = {"bar": 3, "scatter": 3, "pie": 3, "heatmap": 4, "barseries": 6, "darkbar": 3}.get(case["case"])
        if expected:
            check(case["id"] + " mark count", len(marks) == expected, info)
        if case["case"] in {"bar", "darkbar"}:
            heights = []
            for mark in marks:
                d = mark.attrib.get("d", "")
                height = re.search(r"v(" + number + ")", d)
                if height:
                    heights.append(abs(float(height.group(1))))
            check(case["id"] + " heights 2:5:9", len(heights) == 3 and all(abs(h / heights[0] - v / 2) < 1e-6 for h, v in zip(heights, [2, 5, 9], strict=True)), heights)
        if case["case"] == "heatmap":
            check(case["id"] + " 2x2 distinct cell colors", len({m.attrib.get("fill") for m in marks}) == 4, info)
    else:
        if case["case"] in {"bar", "barseries", "darkbar"}:
            colored = [e for e in svg.iter() if e.tag.endswith("path") and e.attrib.get("clip-path") and "stroke-width: 0.5" in e.attrib.get("style", "")]
            geometry = []
            for mark in colored:
                coords = list(map(float, re.findall(number, mark.attrib["d"])))
                geometry.append({"color": mark.attrib["style"], "xs": coords[0::2], "ys": coords[1::2], "height": max(coords[1::2]) - min(coords[1::2])})
            expected = [2, 5, 9, 6, 3, 7] if case["case"] == "barseries" else [2, 5, 9]
            check(case["id"] + " actual SVG bar count", len(geometry) == len(expected), geometry)
            heights = [g["height"] for g in geometry]
            check(case["id"] + " actual SVG heights", len(heights) == len(expected) and all(abs(h / heights[0] - v / 2) < 1e-6 for h, v in zip(heights, expected, strict=True)), heights)
        if case["case"] == "scatter":
            groups = [e for e in svg.iter() if e.attrib.get("id", "").startswith("PathCollection_")]
            paths = [p for g in groups for p in g if p.tag.endswith("path") and p.attrib.get("clip-path")]
            starts = [list(map(float, re.findall(number, p.attrib["d"])))[:2] for p in paths]
            check(case["id"] + " three actual glyphs", len(starts) == 3, starts)
            check(case["id"] + " numeric unequal x gaps 2:5", len(starts) == 3 and abs((starts[1][0] - starts[0][0]) / (starts[2][0] - starts[1][0]) - .4) < 1e-6, starts)
            check(case["id"] + " y order 3,9,2", len(starts) == 3 and starts[1][1] < starts[0][1] < starts[2][1], starts)

report = {"source_sha": manifest["identity"]["source_sha"], "checks": checks, "total": len(checks), "failed": sum(not c["pass"] for c in checks), "limitations": "Exact SVG bar ratios/scatter spacing/Vega counts and colors only; other semantics require screenshot/native browser review."}
(OUT / "static-semantics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(int(report["failed"] > 0))
