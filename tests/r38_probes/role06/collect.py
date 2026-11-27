"""Collect SAVED independent observations; never rerender, browse or edit HTML."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    sys.path.append(str(args.site.resolve()))
    from PIL import Image, ImageChops

    assert not any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules)
    root, evidence = args.run.resolve(), args.evidence.resolve()
    generated = root / "generated"
    fixtures = json.loads((generated / "cases.json").read_text(encoding="utf-8"))
    report = json.loads((generated / "browser-results.json").read_text(encoding="utf-8"))
    assert report["totals"] == {"cases": 21, "checks": 254, "passed": 254, "failed": 0, "skipped": 0}
    unit = ET.parse(root / "unit.xml").getroot()
    suites = [unit] if unit.tag == "testsuite" else list(unit)
    unit_totals = {name: sum(int(suite.get(name, 0)) for suite in suites)
                   for name in ("tests", "failures", "errors", "skipped")}
    assert unit_totals == {"tests": 21, "failures": 0, "errors": 0, "skipped": 0}
    index = {case["id"]: case for case in report["cases"]}
    captures, summary, navs, errors, request_failures = [], [], 0, [], []
    expected_cdn = "https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js"
    expected_g2 = "7e7d346cab68c002a889dc6145bfc1f9ae1391be82ce8d514fb106ef3a6e6412"
    for fixture in fixtures["cases"]:
        html = generated / fixture["html"]
        assert hashlib.sha256(html.read_bytes()).hexdigest() == fixture["html_sha256"]
        case = index[fixture["id"]]
        for key in ("production", "observed"):
            item = case[key]
            assert item["ready"]["status"] == "resolved" and not item.get("harnessError")
            errors.extend(item["errors"])
            request_failures.extend(item["failedRequests"])
            assert len(item["assets"]) == 1
            asset = item["assets"][0]
            assert asset == {"url": expected_cdn, "status": 200, "bytes": 1083414, "sha256": expected_g2}
            image = generated / "screenshots" / item["screenshot"]
            assert hashlib.sha256(image.read_bytes()).hexdigest() == item["screenshotSha256"]
            captures.append({"id": fixture["id"], "mode": key, "path": str(image),
                             "bytes": image.stat().st_size, "sha256": item["screenshotSha256"]})
            navs += 1
        first = generated / "screenshots" / case["production"]["screenshot"]
        second = generated / "screenshots" / case["observed"]["screenshot"]
        with Image.open(first) as a, Image.open(second) as b:
            assert a.size == b.size
            assert ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox() is None
        charts = case["observed"]["state"]["charts"]
        summary.append({"id": fixture["id"], "literal_expected": fixture["expected"],
                        "artifact_input_count": fixture["artifact"]["input_count"],
                        "artifact_output_count": fixture["artifact"]["output_count"],
                        "warnings": fixture["artifact"]["warnings"],
                        "html_sha256_unchanged": fixture["html_sha256"],
                        "unobserved_observed_RGB_identical": True,
                        "native_charts": [{"id": chart["id"], "width": chart["width"], "height": chart["height"],
                                           "background": chart["background"], "marks": chart["marks"],
                                           "legend": chart["legend"], "ticks": chart["ticks"],
                                           "samples": chart.get("samples", [])} for chart in charts]})
    assert navs == 42 and not errors and not request_failures
    proof = json.loads((evidence / "pre-consumer-source.json").read_text(encoding="utf-8"))
    assert fixtures["identity"]["head"] == proof["source_SHA"]
    for item in proof["proof"]:
        assert hashlib.sha256((args.source / item["file"]).read_bytes()).hexdigest() == item["Git_sha256"]
    assert subprocess.run(["git", "-C", str(args.source), "status", "--porcelain"],
                          capture_output=True, check=True).stdout == b""
    selected = ["pie", "sunburst", "treemap", "gauge", "heatmap-negative", "heatmap-signed",
                "heatmap-finite-extent", "heatmap-zero", "heatmap-missing", "dashboard-dark"]
    compact = evidence / "actual"
    compact.mkdir(exist_ok=False)
    for name in selected:
        shutil.copyfile(generated / "screenshots" / index[name]["production"]["screenshot"], compact / (name + ".png"))
    for name in ("pie", "heatmap-negative", "heatmap-finite-extent"):
        fixture = next(row for row in fixtures["cases"] if row["id"] == name)
        shutil.copyfile(generated / fixture["html"], compact / (name + ".html"))
    for name in ("unit-before.json", "unit-after.json", "emit-before.json", "emit-after.json", "unit.xml", "commands.json"):
        shutil.copyfile(root / name, evidence / name)
    for file in root.glob("*.log"):
        shutil.copyfile(file, evidence / file.name)
    output = {"collected_at": datetime.now(timezone.utc).isoformat(), "source_SHA": proof["source_SHA"],
              "method": "Saved measurements only; no product import, rerender, browser replay or HTML changes",
              "unit_totals": unit_totals, "browser_totals": report["totals"], "actual_navigations": navs,
              "errors": errors, "request_failures": request_failures,
              "exact_real_CDN_asset": {"url": expected_cdn, "bytes": 1083414, "sha256": expected_g2, "responses": 42},
              "node": report["node"], "playwright": report["playwright"], "chromium": report["chromium"],
              "all_21_HTML_hashes_unchanged": True, "all_21_observer_pairs_RGB_identical": True,
              "all_7_source_test_hashes_rechecked": True, "source_worktree_clean": True,
              "checks": [{key: check[key] for key in ("id", "name", "pass")} for check in report["checks"]],
              "cases": summary, "captures": captures,
              "raw_browser_result": {"path": str(generated / "browser-results.json"),
                                     "sha256": hashlib.sha256((generated / "browser-results.json").read_bytes()).hexdigest()},
              "image_reader_OPEN_status": "PENDING; actual PNGs copied unchanged for model inspection, not approval"}
    (evidence / "acceptance.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key not in ("checks", "cases", "captures")}, indent=2))


if __name__ == "__main__":
    main()
