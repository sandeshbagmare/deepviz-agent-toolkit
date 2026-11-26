"""Native browser values/layout and confirmed visual failure evidence, baseline only."""
import hashlib
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/local/N10"
reports = [json.loads((OUT / name / "report.json").read_text(encoding="utf-8")) for name in ["browser-python-default", "browser-ts-default", "browser-scatter-disposition"]]
unique = {c["id"]: c for r in reports for c in r["cases"]}
checks = []
findings = []


def check(name, condition, evidence):
    checks.append({"name": name, "pass": bool(condition), "evidence": evidence})


def graph(id_):
    return unique[id_]["state"]["graphs"][0]


def ratio(values, expected):
    return len(values) == len(expected) and all(math.isclose(a / values[0], b / expected[0], rel_tol=1e-5, abs_tol=1e-5) for a, b in zip(values, expected, strict=True))


for id_, case in unique.items():
    check(id_ + " actual errors/resource loads", not case["consoleErrors"] and not case["pageErrors"] and not case["failedRequests"], {"console": case["consoleErrors"], "page": case["pageErrors"], "requests": case["failedRequests"]})
    if case["engine"] == "plotly":
        for index, g in enumerate(case["state"]["graphs"]):
            traces = g["plotly"]["data"]
            if case["case"] in {"bar", "darkbar", "dashboard"}:
                check(id_ + f" panel{index} native values", traces[0]["y"] == [2, 5, 9], traces)
            if case["case"] == "line":
                check(id_ + " native line data", traces[0]["x"] == [1, 2, 4] and traces[0]["y"] == [2, 8, 5], traces)
            if case["case"] == "scatter":
                check(id_ + " native scatter data", traces[0]["x"] == [1, 3, 8] and traces[0]["y"] == [3, 9, 2], traces)
            if case["case"] == "pie":
                check(id_ + " native pie values", traces[0]["labels"] == ["Alpha", "Beta", "Gamma"] and traces[0]["values"] == [2, 3, 5], traces)
            if case["case"] in {"barseries", "lineseries"}:
                check(id_ + " two native series", len(traces) == 2 and [t["name"] for t in traces] == ["Red", "Blue"] and [t["y"] for t in traces] == [[2, 5, 9], [6, 3, 7]], traces)
    if case["engine"] == "echarts":
        for index, g in enumerate(case["state"]["graphs"]):
            native = g["echarts"]["series"]
            if case["case"] in {"bar", "darkbar"} or (case["case"] == "dashboard" and index == 0):
                items = native[0]["items"]
                check(id_ + f" panel{index} native bar values", [x["values"][-1] for x in items] == [2, 5, 9], items)
                check(id_ + f" panel{index} actual bar heights", ratio([abs(x["layout"]["height"]) for x in items], [2, 5, 9]), items)
            if case["case"] in {"barseries", "lineseries"}:
                values = [[item["values"][-1] for item in s["items"]] for s in native]
                check(id_ + " actual native series data", len(native) == 2 and values == [[2, 5, 9], [6, 3, 7]], native)
                if case["case"] == "barseries":
                    layouts = [[item["layout"] for item in s["items"]] for s in native]
                    check(id_ + " actual native dodge non-overlap", all(layouts[0][i]["x"] + layouts[0][i]["width"] <= layouts[1][i]["x"] for i in range(3)), layouts)
    if case["engine"] in {"svg", "vega"} and case["language"] == "typescript" and case["case"] in {"bar", "darkbar"}:
        marks = [m for m in graph(id_)["marks"] if (m.get("cls") == "mark" or (m.get("aria") or "").startswith("x:")) and m["box"]["height"] > 0]
        check(id_ + " actual SVG bar heights", ratio([m["box"]["height"] for m in marks], [2, 5, 9]), marks)

def image(name):
    return Image.open(OUT / name).convert("RGB")


pie = image("browser-python-default/py-antv-pie-region-0.png")
pie_samples = {"Alpha-sector": pie.getpixel((428, 153)), "Beta-sector": pie.getpixel((455, 320)), "Gamma-sector": pie.getpixel((238, 250)), "Alpha-legend": pie.getpixel((716, 63)), "Beta-legend": pie.getpixel((716, 86)), "Gamma-legend": pie.getpixel((716, 109))}
findings.append({"id": "N05-F3", "description": "Three different pie categories have identical drawn sector RGB but legend has distinct colors", "pixel_samples": pie_samples})
line = unique["py-antv-line"]["rasters"][0]
ts_line = unique["ts-antv-line"]["rasters"][0]
findings.append({"id": "N05-F1", "description": "Uncolored Python G2 line fills a closed triangle; actual raster area, not mere spec inference", "python_colored_pixels": line["coloredPixels"], "typescript_native_line_colored_pixels": ts_line["coloredPixels"]})
for language in ["py", "ts"]:
    id_ = language + "-plotly-heatmap"
    traces = graph(id_)["plotly"]["data"]
    findings.append({"id": "N05-F2" if language == "py" else "TS-native-heatmap-control", "native_trace_type": traces[0]["type"], "native_data": traces})
axis = graph("ts-echarts-darkbar")["echarts"]["option"]["xAxis"][0]["axisLabel"]["color"]


def luminance(hex_):
    values = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return sum(a * b for a, b in zip(values, [.2126, .7152, .0722], strict=True))


contrast = (luminance(axis) + .05) / (luminance("#111827") + .05)
findings.append({"id": "N18-F2", "actual_canvas_text_fill": axis, "background": "#111827", "luminance_contrast_ratio": contrast, "small_text_QA_threshold": 4.5})
for id_ in ["py-echarts-line", "ts-echarts-line"]:
    option = graph(id_)["echarts"]["option"]["xAxis"][0]
    findings.append({"id": "numeric-line-axis-composition", "case": id_, "actual_axis_type": option["type"], "actual_categories": option["data"]})
findings.append({"id": "numeric-line-axis-composition", "case": "ts-svg-line", "actual_polyline": [m for m in graph("ts-svg-line")["marks"] if m["tag"] == "polyline"]})

scripts = {s["url"]: s for c in unique.values() for s in c["resources"] if s["type"] == "script" and not s["url"].startswith("http://127.")}
hashes = []
for folder in ["browser-python-default", "browser-ts-default", "browser-scatter-disposition", "contact-sheets"]:
    for file in (OUT / folder).glob("*.png"):
        hashes.append({"path": str(file.relative_to(OUT)).replace("\\", "/"), "bytes": file.stat().st_size, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
result = {"source_sha": reports[0]["source_sha"], "browser": reports[0]["browser"], "unique_cases": len(unique), "executions_default": sum(len(r["cases"]) for r in reports[:2]), "explicit_unsupported": ["ts-svg-heatmap"],
          "native_checks": checks, "native_check_total": len(checks), "native_check_failures": sum(not c["pass"] for c in checks), "semantic_acceptance": "FAIL; confirmed visual findings are separate from passing runtime/value checks", "findings": findings, "real_external_resources": list(scripts.values()), "screenshot_hashes": hashes}
(OUT / "evidence-summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"unique_cases": len(unique), "native_checks": len(checks), "native_check_failures": result["native_check_failures"], "screenshot_hashes": len(hashes), "dark_axis_contrast_ratio": contrast}, indent=2))
raise SystemExit(int(result["native_check_failures"] > 0))
