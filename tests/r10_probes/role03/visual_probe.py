"""Portable opt-in ECharts probe. Generate with DeepViz; capture with installed Playwright.

No dependency installation, interception, saved capture prerequisite, or model code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from echarts_coordinate_oracle import assert_native_coordinates, fixture_rows


def generate(destination: Path) -> None:
    from deepviz.models import ChartSpec
    from deepviz.render import render

    destination.mkdir(parents=True, exist_ok=False)
    cases = []
    for kind in ("line", "area"):
        for axis in ("value", "category", "time"):
            rows = fixture_rows(axis)
            name = f"{kind}-{axis}"
            artifact = render(rows, ChartSpec(kind=kind, title=name, x="x", y="y",
                                             aggregation="none", max_points=10, width=640, height=400),
                              engine="echarts", output_dir=destination / name)
            html_path = next(path for path in map(Path, artifact.paths) if path.suffix == ".html")
            cases.append({"name": name, "kind": kind, "axis": axis, "rows": rows,
                          "html": html_path.relative_to(destination).as_posix(),
                          "html_sha256": hashlib.sha256(html_path.read_bytes()).hexdigest()})
    (destination / "fixtures.json").write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    print(f"GENERATED={len(cases)}; FIXTURES={destination / 'fixtures.json'}")


def capture(fixtures: Path) -> None:
    from playwright.sync_api import sync_playwright

    root = fixtures.resolve().parent
    cases = json.loads(fixtures.read_text(encoding="utf-8"))
    errors = []
    dependencies = []
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        version = browser.version
        for case in cases:
            html = (root / case["html"]).resolve()
            assert html.is_relative_to(root), "fixture artifact escaped its owned directory"
            assert hashlib.sha256(html.read_bytes()).hexdigest() == case["html_sha256"]
            page = browser.new_page(viewport={"width": 900, "height": 600}, device_scale_factor=1)
            name = case["name"]
            page.on("pageerror", lambda error, name=name: errors.append([name, "pageerror", str(error)]))
            page.on("console", lambda message, name=name: errors.append([name, "console", message.text])
                    if message.type == "error" else None)
            page.on("requestfailed", lambda request, name=name: errors.append([
                name, "requestfailed", request.failure or "unknown",
            ]))

            def observe_response(response, name=name):
                if "echarts@" in response.url:
                    body = response.body()
                    dependencies.append({"case": name, "url": response.url, "status": response.status,
                                         "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})

            page.on("response", observe_response)
            page.goto(html.as_uri(), wait_until="load", timeout=30000)
            page.wait_for_function("window.deepvizReady && document.querySelector('#chart-0 svg path')",
                                   timeout=30000)
            observed = page.evaluate("""async () => {
              await window.deepvizReady;
              const el = document.getElementById('chart-0');
              const c = echarts.getInstanceByDom(el), option = c.getOption();
              const data = option.series[0].data;
              const paths = [...el.querySelectorAll('svg path')]
                .filter(p => p.getAttribute('stroke') === '#386cb0')
                .map(p => p.getAttribute('d'));
              return {version: echarts.version, axis: option.xAxis[0].type, data,
                      payload: JSON.parse(document.getElementById('deepviz-data').textContent)[0],
                      pixels: data.map(point => c.convertToPixel({seriesIndex: 0}, point)), paths};
            }""")
            assert_native_coordinates(observed.pop("payload"), case["rows"],
                                      kind=case["kind"], axis=case["axis"])
            assert observed["axis"] == case["axis"]
            assert observed["data"] == [[row["x"], row["y"]] for row in case["rows"]]
            xs = [point[0] for point in observed["pixels"]]
            ratio = (xs[2] - xs[1]) / (xs[1] - xs[0])
            assert abs(ratio - (1 if case["axis"] == "category" else 2)) < 1e-10
            assert len(observed["paths"]) == 1
            actual = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", observed["paths"][0])]
            expected = [value for point in observed["pixels"] for value in point]
            assert len(actual) == len(expected) == 6
            assert all(abs(left - right) <= 0.00006 for left, right in zip(actual, expected, strict=True))
            screenshot = root / f"{name}.png"
            page.locator("#chart-0").screenshot(path=str(screenshot))
            results.append({"case": name, **observed, "gap_ratio": ratio, "png": screenshot.name,
                            "png_sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest()})
            page.close()
        browser.close()
    result = {"browser_version": version, "cases": results, "errors": errors,
              "dependencies": dependencies, "claim": "six finite coordinate controls, not final visual signoff"}
    (root / "browser-results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert not errors, "browser console/page/request errors are failures"
    assert len(dependencies) == len(cases) and all(item["status"] == 200 for item in dependencies)
    print(f"CAPTURED={len(results)}; ERRORS={len(errors)}; RESULTS={root / 'browser-results.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("generate", "capture"))
    parser.add_argument("path", type=Path, help="new output directory for generate, fixtures.json for capture")
    arguments = parser.parse_args()
    if arguments.action == "generate":
        generate(arguments.path.resolve())
    else:
        capture(arguments.path)


if __name__ == "__main__":
    main()
