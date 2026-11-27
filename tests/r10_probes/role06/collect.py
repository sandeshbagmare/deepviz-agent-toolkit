"""Combine same-source actual runs, preserving RED and replacing only a named own-harness error."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("initial", "correction", "diagnostic", "scales", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    original = load(args.initial / "browser-report.json")
    corrected = load(args.correction / "browser-report.json")
    if original["identity"] != corrected["identity"]:
        raise ValueError("Refusing to combine different-source browser runs")
    if [row["id"] for row in corrected["runtimeCases"]] != ["plotly-bar"]:
        raise ValueError("Only the explicitly documented own Plotly hover error may be replaced")
    if any(not check["pass"] for check in corrected["checks"]):
        raise ValueError("Corrected actual pointer control did not pass; cannot replace previous result")
    rows = [row for row in original["runtimeCases"] if row["id"] != "plotly-bar"] + corrected["runtimeCases"]
    checks = [check for check in original["checks"] if check["case"] != "plotly-bar"] + corrected["checks"]
    if len(rows) != 60 or len({row["id"] for row in rows}) != 60:
        raise ValueError("Missing/duplicate current-source cases")
    for row in rows:
        if row["id"].split("-", 1)[1] not in {"bar", "line"}:
            continue
        labels = row["state"]["charts"][0]["labels"]
        title = f"R10 {row['engine']} {row['id'].split('-', 1)[1]}"
        checks.append({"case": row["id"], "name": "observed-native-title", "pass": title in labels,
                       "observed": labels})
        if row["id"].endswith("-bar"):
            checks.append({"case": row["id"], "name": "observed-category-labels",
                           "pass": {"Alpha", "Beta", "Gamma"}.issubset(labels), "observed": labels})
    failures = [check for check in checks if not check["pass"]]
    diagnostics = load(args.diagnostic / "diagnostic.json")
    scales = load(args.scales / "diagnostic.json")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    selected = [
        (args.correction / "browser/plotly-bar.png", "plotly-real-pointer-tooltip.png"),
        (args.initial / "browser/antv-pie.png", "antv-pie-fixed-fill-RED.png"),
        (args.initial / "browser/antv-mixed-light.png", "antv-mixed-light-current.png"),
        (args.initial / "browser/antv-mixed-dark.png", "antv-mixed-dark-current.png"),
        (args.diagnostic / "original-real-render-unobserved.png", "antv-negative-unobserved-RED.png"),
        (args.scales / "linear.png", "antv-explicit-linear-diagnostic-ONLY.png"),
        (args.scales / "linear.html", "antv-explicit-linear-diagnostic-ONLY.html"),
        (args.diagnostic / "negative.html", "antv-negative-production-equivalent-RED.html"),
    ]
    artifacts = []
    for source, name in selected:
        shutil.copyfile(source, output / name)
        artifacts.append({"file": name, **digest(output / name), "source_relative": source.name})
    image = Image.open(output / "antv-pie-fixed-fill-RED.png").convert("RGB")
    pie_samples = [image.getpixel(point) for point in ((470, 260), (420, 400), (350, 260))]
    legend_samples = [image.getpixel(point) for point in ((836, 201), (836, 225), (836, 248))]
    summary = {
        "identity": original["identity"], "node": original["node"], "chromium": original["chromium"],
        "status": "RED: no visual acceptance or final-source signoff",
        "case_count": len(rows), "runtime_pass": sum(row["runtime"] == "PASS" for row in rows),
        "runtime_fail": sum(row["runtime"] != "PASS" for row in rows),
        "check_count": len(checks), "pass": len(checks) - len(failures), "fail": len(failures),
        "skips": 0, "failures": failures,
        "superseded_own_harness_error": {
            "case": "plotly-bar", "reason": "SVG-mark locator hover intercepted by native drag overlay",
            "replacement": "Real page.mouse.move at actual mark bounds yields native Alpha12 tooltip",
            "raw_original_preserved": True, "corrected_pass_checks": len(corrected["checks"]),
        },
        "checks": checks,
        "cases": [{key: row.get(key) for key in ("id", "engine", "runtime", "error", "errors",
                    "failedRequests", "responses", "tooltipLimit", "state")} for row in rows],
        "unobserved_heatmap_diagnostics": diagnostics, "diagnostic_only_scale_controls": scales,
        "current_pie_pixel_controls": {"sector_RGBs": pie_samples, "legend_RGBs": legend_samples,
            "same_sectors_distinct_legend": len(set(pie_samples)) == 1 and len(set(legend_samples)) == 3},
        "artifacts": artifacts,
        "limits": [
            "Checkpoint3aa521a5, not latest frozen/final source; no full project signoff",
            "Python optional suite3fail missingPythonPlaywright beforelaunch; Node execution is separate",
            "Tiny fixtures, not scale/build/package/MCP/DeepAgent certification",
            "Actual pinned CDN HTTP200, no interception/fakeCDNbodies; availability needs network",
            "AntV tooltip explicitly disabled; data table mouse+keyboard tested, not nonexistent hover",
            "Legend-off avoids crash but loses legend and negative-cell distinction; NOT a fix",
            "Explicit scale examples are diagnostic-only native-payload overrides, production unchanged",
            "Collector exits1 on genuine RED; successful collection is NOT passing product semantics",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("status", "case_count", "runtime_pass", "runtime_fail",
                                                   "check_count", "pass", "fail", "failures")}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
