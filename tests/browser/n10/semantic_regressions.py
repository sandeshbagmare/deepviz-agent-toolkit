"""Known failing semantic gates over exact real-browser evidence, not mocks."""
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/local/N10"
summary = json.loads((OUT / "evidence-summary.json").read_text(encoding="utf-8"))
cases = {}
for folder in ["browser-python-default", "browser-ts-default"]:
    cases.update({c["id"]: c for c in json.loads((OUT / folder / "report.json").read_text(encoding="utf-8"))["cases"]})
checks = []


def check(id_, condition, expected, actual, screenshot):
    checks.append({"id": id_, "pass": bool(condition), "expected": expected, "actual": actual, "screenshot": screenshot})


line = next(f for f in summary["findings"] if f["id"] == "N05-F1")
check("N05-F1", line["python_colored_pixels"] < 10000, "Three-point line is unfilled; bounded known 800x460 thin line occupies <10K colored pixels", line, "browser-python-default/py-antv-line-region-0.png")
pie = next(f for f in summary["findings"] if f["id"] == "N05-F3")
samples = pie["pixel_samples"]
check("N05-F3", len({tuple(samples[key]) for key in ["Alpha-sector", "Beta-sector", "Gamma-sector"]}) == 3, "Three distinct pie-sector colors corresponding to distinct advertised legend categories", samples, "browser-python-default/py-antv-pie-region-0.png")
dark = next(f for f in summary["findings"] if f["id"] == "N18-F2")
check("N18-F2", dark["luminance_contrast_ratio"] >= 4.5, "Dark small axis-label contrast >=4.5 under this QA readability gate", dark, "browser-ts-default/ts-echarts-darkbar-region-0.png")

im = Image.open(OUT / "browser-ts-default/ts-antv-barseries-region-0.png").convert("RGB")
pixels = im.load()
columns = []
for x in range(min(im.width, 800)):
    amount = sum(max(pixels[x, y]) - min(pixels[x, y]) > 80 and min(pixels[x, y]) < 160 for y in range(100, min(im.height, 440)))
    columns.append(amount >= 20)
runs = []
start = None
for x, active in enumerate(columns + [False]):
    if active and start is None:
        start = x
    if not active and start is not None:
        if x - start > 10:
            runs.append([start, x - 1])
        start = None
check("N18-F1", len(runs) == 6, "Grouped two-series/three-category bar oracle: six horizontally disjoint visible bar bands; current G2 neither dodges nor stacks", {"visible_color_column_bands": runs, "legend_series": ["Red", "Blue"], "known_values": [[2, 5, 9], [6, 3, 7]], "limitation": "A deliberate documented stacked composition would need a distinct oracle, not silently this grouped one."}, "browser-ts-default/ts-antv-barseries-region-0.png")

for id_ in ["py-plotly-pie", "ts-plotly-pie", "ts-svg-pie"]:
    visible = " ".join(t["text"] or "" for t in cases[id_]["state"]["svgText"])
    check(id_ + " visible-category-identification", all(label in visible for label in ["Alpha", "Beta", "Gamma"]), "Pie has visible category labels or legend matching the three slices; percentages alone are insufficient", {"actual_svg_text": visible}, ("browser-python-default/" if id_.startswith("py-") else "browser-ts-default/") + id_ + "-region-0.png")

result = {"source_sha": summary["source_sha"], "status": "FAIL" if any(not c["pass"] for c in checks) else "PASS", "total": len(checks), "failed": sum(not c["pass"] for c in checks), "checks": checks,
          "limitations": "Regression gates run against captured original baseline artifacts, not a claimed final candidate or any unobserved producer fix. Screenshots were also visually opened and inspected."}
(OUT / "semantic-regressions.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(int(result["failed"] > 0))
