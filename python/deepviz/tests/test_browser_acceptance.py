"""Run generated ECharts/G2 artifacts with local, version-matched runtimes.

Enable with DEEPVIZ_BROWSER_TESTS=1 and point DEEPVIZ_BROWSER_DEPS at an npm
project containing echarts and @antv/g2. Playwright/Chromium and Pillow must
already be installed. Tests never fetch a runtime from the network.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration
_ORIGIN = "https://deepviz-browser.invalid"
_ROWS = [
    {"category": "North", "value": 7},
    {"category": "South", "value": 19},
    {"category": "East", "value": 31},
]
_COUNTS = [
    {"category": "North", "value": 999},
    {"category": "North", "value": 999},
    {"category": "South", "value": 999},
    {"category": "East", "value": 999},
    {"category": "East", "value": 999},
    {"category": "East", "value": 999},
]
_OBSERVE = """() => {
  const state = window.__deepvizAcceptance = {status: 'unassigned', drawnText: [], charts: []};
  let g2;
  Object.defineProperty(window, 'G2', {
    configurable: true, get: () => g2, set: value => {
      g2 = value;
      const observe = original => new Proxy(original, {construct(target, args, newTarget) {
        const chart = Reflect.construct(target, args, newTarget); state.charts.push(chart); return chart;
      }});
      let constructor = value.Chart ? observe(value.Chart) : undefined;
      Object.defineProperty(value, 'Chart', {configurable: true, enumerable: true,
        get: () => constructor, set: original => { constructor = observe(original); }});
    }
  });
  let readiness;
  Object.defineProperty(window, 'deepvizReady', {
    configurable: true,
    get: () => readiness,
    set: value => {
      readiness = value;
      state.status = value && typeof value.then === 'function' ? 'pending' : 'not-thenable';
      if (state.status === 'pending') value.then(
        () => { state.status = 'fulfilled'; },
        error => { state.status = 'rejected'; state.error = String(error); }
      );
    }
  });
  for (const type of [window.CanvasRenderingContext2D, window.OffscreenCanvasRenderingContext2D]) {
    if (!type) continue;
    for (const name of ['fillText', 'strokeText']) {
      const original = type.prototype[name];
      type.prototype[name] = function(...args) {
        if (Number.isFinite(args[1]) && Number.isFinite(args[2])) state.drawnText.push(String(args[0]));
        return Reflect.apply(original, this, args);
      };
    }
  }
}"""


@pytest.fixture(scope="module")
def browser():
    if os.environ.get("DEEPVIZ_BROWSER_TESTS") != "1":
        pytest.skip("Set DEEPVIZ_BROWSER_TESTS=1 to run local Chromium acceptance")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        with playwright.chromium.launch(headless=True) as instance:
            yield instance


@pytest.fixture(scope="module")
def runtimes(browser):
    root = Path(os.environ.get("DEEPVIZ_BROWSER_DEPS", Path(__file__).resolve().parents[3]))
    result = {}
    for engine, package, asset in (
        ("echarts", "echarts", "dist/echarts.min.js"),
        ("antv", "@antv/g2", "dist/g2.min.js"),
    ):
        directory = root / "node_modules" / package
        metadata = directory / "package.json"
        if not metadata.is_file():
            pytest.fail(f"Install {package} under DEEPVIZ_BROWSER_DEPS before browser acceptance")
        version = json.loads(metadata.read_text(encoding="utf-8"))["version"]
        body = (directory / asset).read_bytes()
        result[engine] = {
            "url": f"https://cdn.jsdelivr.net/npm/{package}@{version}/{asset}",
            "body": body,
            "version": version,
            "sha256": hashlib.sha256(body).hexdigest(),
        }
    return result


def _artifact(tmp_path, engine, specs, rows):
    from deepviz.models import ChartSpec
    from deepviz.render import render

    spec = specs[0] if len(specs) == 1 else ChartSpec(
        kind="dashboard", charts=specs, title="Browser dashboard", columns=2, width=1100,
    )
    artifact = render(rows, spec, engine, tmp_path)
    path = next(Path(path) for path in artifact.paths if Path(path).suffix == ".html")
    return path, artifact


@contextmanager
def _open(browser, path, runtime, engine, failure=None):
    context = browser.new_context(
        viewport={"width": 1200, "height": 900}, device_scale_factor=1,
        locale="en-US", timezone_id="UTC", service_workers="block", accept_downloads=False,
    )
    context.set_offline(True)
    context.add_init_script(f"({_OBSERVE})();")
    observations = {"page_errors": [], "console_errors": [], "unexpected_requests": [], "runtime_requests": []}
    page = context.new_page()
    page.on("pageerror", lambda error: observations["page_errors"].append(str(error)))
    page.on("console", lambda message: observations["console_errors"].append(message.text)
            if message.type == "error" else None)

    def route_request(route):
        url = route.request.url
        if url == f"{_ORIGIN}/chart.html":
            route.fulfill(body=path.read_bytes(), content_type="text/html")
        elif url == f"{_ORIGIN}/favicon.ico":
            route.fulfill(status=204)
        elif url == runtime["url"]:
            observations["runtime_requests"].append(url)
            if failure == "denied":
                route.abort("blockedbyclient")
            elif failure == "sync-init":
                body = (
                    "window.echarts={init(){throw new Error('Controlled initialization failure')}};"
                    if engine == "echarts" else
                    "window.G2={Chart:class{constructor(){throw new Error('Controlled initialization failure')}}};"
                )
                route.fulfill(body=body, content_type="application/javascript")
            else:
                route.fulfill(body=runtime["body"], content_type="application/javascript")
        else:
            observations["unexpected_requests"].append(url)
            route.abort("blockedbyclient")

    context.route("**/*", route_request)
    try:
        page.goto(f"{_ORIGIN}/chart.html", wait_until="load")
        observations["thenable"] = page.evaluate(
            "!!window.deepvizReady && typeof window.deepvizReady.then === 'function'"
        )
        if observations["thenable"]:
            page.wait_for_function("window.__deepvizAcceptance.status !== 'pending'", timeout=15000)
        observations.update(page.evaluate("""() => ({
            readiness: window.__deepvizAcceptance.status,
            rejection: window.__deepvizAcceptance.error || null,
            render_error: document.body.dataset.renderError || null,
            drawn_text: [...window.__deepvizAcceptance.drawnText,
                ...[...document.querySelectorAll('svg text')].map(el => el.textContent)]
        })"""))
        yield page, observations
    finally:
        try:
            page.screenshot(path=str(path.parent / "browser.png"), full_page=True, animations="disabled")
            observations["artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            observations["runtime"] = {key: value for key, value in runtime.items() if key != "body"}
            observations["chromium"] = browser.version
            (path.parent / "browser-observations.json").write_text(
                json.dumps(observations, indent=2, ensure_ascii=False), encoding="utf-8",
            )
        finally:
            context.close()


def _table(page, index, expected):
    details = page.locator("details").nth(index)
    if details.get_attribute("open") is None:
        details.locator("summary").focus()
        page.keyboard.press("Enter")
    table = details.locator("table")
    assert table.is_visible(), "Chart data must remain keyboard-discoverable"
    assert [row.locator("td").all_text_contents() for row in table.locator("tbody tr").all()] == expected


def _native_bars(page, engine, index, values):
    from PIL import Image

    graph = page.locator(f"#chart-{index}")
    image = Image.open(io.BytesIO(graph.screenshot(animations="disabled"))).convert("RGB")
    pixels = image.load()
    mask = bytearray(
        all(abs(pixels[x, y][i] - color) <= 16 for i, color in enumerate((56, 108, 176)))
        for y in range(image.height) for x in range(image.width)
    )
    bands = []
    for start in range(len(mask)):
        if not mask[start]:
            continue
        stack, component = [start], []
        mask[start] = 0
        while stack:
            point = stack.pop()
            component.append(point)
            x, y = point % image.width, point // image.width
            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            for nx, ny in neighbors:
                if 0 <= nx < image.width and 0 <= ny < image.height:
                    position = ny * image.width + nx
                    if mask[position]:
                        mask[position] = 0
                        stack.append(position)
        xs, ys = [p % image.width for p in component], [p // image.width for p in component]
        if len(component) >= 100 and max(xs) - min(xs) >= 4:
            bands.append({"left": min(xs), "right": max(xs), "top": min(ys), "bottom": max(ys)})
    bands.sort(key=lambda band: band["left"])
    assert len(bands) == len(values), f"Expected three real native bars, got {bands}"
    heights = [band["bottom"] - band["top"] + 1 for band in bands]
    scale = max(heights) / max(values)
    assert heights == pytest.approx([value * scale for value in values], abs=3)
    if engine == "echarts":
        data = page.evaluate("""index => echarts.getInstanceByDom(
            document.getElementById('chart-' + index)).getOption().series[0].data""", index)
    else:
        data = page.evaluate("""index => [...window.__deepvizAcceptance.charts[index]
            .getContext().canvas.document.documentElement.querySelectorAll('.element')]
            .map(node => [node.__data__.data._x, node.__data__.data._y])""", index)
    assert sorted(data) == sorted([["North", values[0]], ["South", values[1]], ["East", values[2]]])
    return {"bands": bands, "native_data": data}


@pytest.mark.parametrize("engine", ["echarts", "antv"])
@pytest.mark.parametrize("aggregation,values,rows", [
    ("none", [7, 19, 31], _ROWS),
    ("count", [2, 1, 3], _COUNTS),
])
def test_local_runtime_renders_native_bar_values(browser, runtimes, tmp_path, engine, aggregation, values, rows):
    from deepviz.models import ChartSpec

    spec = ChartSpec(kind="bar", title="Regional observations", x="category",
                     y="value" if aggregation == "none" else None, aggregation=aggregation,
                     width=900, height=420)
    path, artifact = _artifact(tmp_path, engine, [spec], rows)
    assert (artifact.input_count, artifact.output_count) == (len(rows), 3)
    with _open(browser, path, runtimes[engine], engine) as (page, seen):
        assert seen["thenable"] and seen["readiness"] == "fulfilled", seen
        assert seen["render_error"] is None
        assert seen["runtime_requests"] == [runtimes[engine]["url"]]
        assert seen["page_errors"] == seen["console_errors"] == seen["unexpected_requests"] == []
        for label in ("North", "South", "East"):
            assert label in seen["drawn_text"], f"Category {label} is not drawn in the chart"
        seen["bars"] = _native_bars(page, engine, 0, values)
        _table(page, 0, [["North", str(values[0])], ["South", str(values[1])], ["East", str(values[2])]])
        assert f"3 displayed records from {len(rows)} input records" in page.locator("#chart-summary-0").inner_text()


@pytest.mark.parametrize("engine", ["echarts", "antv"])
def test_local_runtime_renders_every_dashboard_panel(browser, runtimes, tmp_path, engine):
    from deepviz.models import ChartSpec

    specs = [
        ChartSpec(kind="bar", title="Observation counts", x="category", aggregation="count", height=420),
        ChartSpec(kind="bar", title="Observation totals", x="category", y="value", aggregation="sum", height=420),
    ]
    path, _ = _artifact(tmp_path, engine, specs, _COUNTS)
    with _open(browser, path, runtimes[engine], engine) as (page, seen):
        assert seen["thenable"] and seen["readiness"] == "fulfilled", seen
        assert seen["render_error"] is None
        assert seen["page_errors"] == seen["console_errors"] == seen["unexpected_requests"] == []
        seen["panels"] = []
        for index, values in enumerate(([2, 1, 3], [1998, 999, 2997])):
            seen["panels"].append(_native_bars(page, engine, index, values))
            _table(page, index, [["North", str(values[0])], ["South", str(values[1])], ["East", str(values[2])]])
            assert "3 displayed records from 6 input records" in page.locator(f"#chart-summary-{index}").inner_text()


@pytest.mark.parametrize("engine", ["echarts", "antv"])
@pytest.mark.parametrize("failure", ["denied", "sync-init"])
def test_runtime_failure_rejects_readiness_and_retains_data(browser, runtimes, tmp_path, engine, failure):
    from deepviz.models import ChartSpec

    spec = ChartSpec(kind="bar", x="category", y="value", aggregation="none", title="Runtime failure")
    path, _ = _artifact(tmp_path, engine, [spec], _ROWS)
    with _open(browser, path, runtimes[engine], engine, failure) as (page, seen):
        assert seen["thenable"], "A synchronous initializer failure must not lose the readiness Promise"
        assert seen["readiness"] == "rejected", seen
        assert seen["rejection"] and seen["render_error"]
        if failure == "sync-init":
            assert "Controlled initialization failure" in seen["rejection"]
            assert seen["console_errors"] == []
        else:
            assert all("ERR_BLOCKED_BY_CLIENT" in message for message in seen["console_errors"])
        assert seen["page_errors"] == seen["unexpected_requests"] == []
        alert = page.get_by_role("alert")
        assert alert.count() > 0 and alert.first.is_visible()
        assert alert.first.inner_text().strip()
        _table(page, 0, [["North", "7"], ["South", "19"], ["East", "31"]])


@pytest.mark.parametrize("width,values", [
    (960, [-7.0, -2.0]), (960, [-8e-310, -2e-310]), (960, [5e-324, 1e-323, 2e-323]),
    (960, [-1.7976931348623157e308, 0.0, 1.7976931348623157e308]),
    (240, [-1.7976931348623157e308, 0.0, 1.7976931348623157e308]),
    (240, [1.7976931348623157e308, 1.7976931348623157e308]),
])
def test_antv_finite_heatmap_paints_truthful_cells_and_readable_legend(browser, runtimes, tmp_path, width, values):
    from deepviz.models import ChartSpec

    rows = [{"column": label, "row": "A", "heat": value}
            for label, value in zip(["West", "Center", "East"], values, strict=False)]
    spec = ChartSpec(kind="heatmap", x="column", y="row", color="heat", aggregation="none",
                     width=width, height=420, title="Heat observations")
    path, _ = _artifact(tmp_path, "antv", [spec], rows)
    with _open(browser, path, runtimes["antv"], "antv") as (page, seen):
        assert seen["readiness"] == "fulfilled" and seen["render_error"] is None, seen
        assert seen["page_errors"] == seen["console_errors"] == seen["unexpected_requests"] == []
        state = page.evaluate("""() => {
          const context = window.__deepvizAcceptance.charts[0].getContext();
          const root = context.canvas.document.documentElement;
          const canvas = document.querySelector('#chart-0 canvas');
          const pixels = canvas.getContext('2d');
          const describe = node => {
            const b = node.getBBox();
            return {text: node.getAttribute('text'), fill: node.getAttribute('fill'),
              box: {x: b.x, y: b.y, width: b.width, height: b.height}};
          };
          const marks = [...root.querySelectorAll('.element')].map(describe);
          const legend = root.querySelector('.legend-continuous');
          return {marks, width: canvas.width, height: canvas.height,
            labels: legend ? [...legend.querySelectorAll('text')].map(describe) : [],
            pixels: marks.map(mark => [...pixels.getImageData(
              Math.round(mark.box.x + mark.box.width / 2), Math.round(mark.box.y + mark.box.height / 2),
              1, 1).data])};
        }""")
        seen["heatmap"] = state
        assert len(state["marks"]) == len(values)
        assert len({tuple(pixel) for pixel in state["pixels"]}) == len(set(values))
        assert all(mark["box"]["width"] > 10 and mark["box"]["height"] > 10 for mark in state["marks"])
        assert state["labels"], "The quantitative color domain needs a visible legend"
        for label in state["labels"]:
            box = label["box"]
            assert box["x"] >= 0 and box["y"] >= 0
            assert box["x"] + box["width"] <= state["width"]
            assert box["y"] + box["height"] <= state["height"]
        ticks = [float(label["text"].replace("−", "-").replace(",", ""))
                 for label in state["labels"] if label["text"] not in {None, "_heat"}]
        assert len(ticks) == 2, "Both domain endpoints must remain readable"
        assert min(ticks) <= min(values) <= max(values) <= max(ticks)
        for index, label in enumerate(state["labels"]):
            assert label["text"] in "".join(seen["drawn_text"]), "Wrapped legend text must be fully drawn"
            a = label["box"]
            for other in state["labels"][index + 1:]:
                b = other["box"]
                assert (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"]
                        or a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])


@pytest.mark.parametrize("engine", ["echarts", "antv"])
def test_every_declared_kind_executes_a_real_native_chart(browser, runtimes, tmp_path, engine):
    from typing import get_args

    from deepviz.models import ChartKind, ChartSpec

    specs = []
    for kind in get_args(ChartKind):
        if kind == "dashboard":
            continue
        numeric = kind in {"scatter", "bubble", "geo"}
        specs.append(ChartSpec(kind=kind, title=kind, x="position" if numeric else "category",
                               y="slot" if kind == "heatmap" else "value",
                               color="value" if kind == "heatmap" else None,
                               size="value" if kind == "bubble" else None,
                               width=500, height=320, aggregation="none"))
    rows = [dict(row, position=index, slot="A") for index, row in enumerate(_ROWS)]
    path, _ = _artifact(tmp_path, engine, specs, rows)
    with _open(browser, path, runtimes[engine], engine) as (page, seen):
        assert seen["readiness"] == "fulfilled" and seen["render_error"] is None, seen
        assert seen["page_errors"] == seen["console_errors"] == seen["unexpected_requests"] == []
        seen["native_kinds"] = []
        for index, spec in enumerate(specs):
            if engine == "antv":
                boxes = page.evaluate("""index => [...window.__deepvizAcceptance.charts[index]
                    .getContext().canvas.document.documentElement.querySelectorAll('.element')]
                    .map(node => {const b=node.getBBox(); return [b.width,b.height];})""", index)
                assert boxes and any(width > 0 and (height > 0 or spec.kind in {"box", "violin"})
                                     for width, height in boxes), spec.kind
                seen["native_kinds"].append({"kind": spec.kind, "boxes": boxes})
            else:
                assert page.locator(f"#chart-{index} svg path, #chart-{index} svg text").count() > 0, spec.kind


@pytest.mark.parametrize("values", [[-7.0, 0.0, 2.0], [-8e-310, 0.0, 2e-310],
                                   [-1.7976931348623157e308, 0.0, 1.7976931348623157e308]])
def test_echarts_heatmap_paints_distinct_finite_values(browser, runtimes, tmp_path, values):
    from deepviz.models import ChartSpec

    rows = [{"column": label, "row": "A", "heat": value}
            for label, value in zip(["West", "Center", "East"], values, strict=True)]
    spec = ChartSpec(kind="heatmap", x="column", y="row", color="heat", aggregation="none")
    path, _ = _artifact(tmp_path, "echarts", [spec], rows)
    with _open(browser, path, runtimes["echarts"], "echarts") as (page, seen):
        assert seen["readiness"] == "fulfilled" and seen["render_error"] is None, seen
        assert seen["page_errors"] == seen["console_errors"] == seen["unexpected_requests"] == []
        actual = page.evaluate("""() => {
          const chart=echarts.getInstanceByDom(document.getElementById('chart-0'));
          const data=chart.getModel().getSeriesByIndex(0).getData();
          const marks=Array.from({length:data.count()},(_,i)=>data.getItemGraphicEl(i));
          return {values:chart.getOption().series[0].data.map(row=>row[2]),
            colors:marks.map(mark=>mark.style.fill),
            boxes:marks.map(mark=>{const b=mark.getBoundingRect();return [b.width,b.height];})};
        }""")
        seen["heatmap"] = actual
        assert actual["values"] == values
        assert len(set(actual["colors"])) == len(set(values))
        assert len(actual["boxes"]) == 3 and all(width > 10 and height > 10 for width, height in actual["boxes"])


@pytest.mark.parametrize("dashboard", [False, True])
def test_antv_hover_keeps_series_markup_literal(browser, runtimes, tmp_path, dashboard):
    from deepviz.models import ChartSpec

    literal = '<span data-deepviz-literal="series">Literal series</span>'
    rows = [{"position": 0, "value": 7, "series": literal},
            {"position": 1, "value": 19, "series": literal}]
    spec = ChartSpec(kind="line", x="position", y="value", color="series", aggregation="none")
    path, _ = _artifact(tmp_path, "antv", [spec, spec] if dashboard else [spec], rows)
    with _open(browser, path, runtimes["antv"], "antv") as (page, seen):
        assert seen["readiness"] == "fulfilled", seen
        point = page.evaluate("""() => {
          const chart=window.__deepvizAcceptance.charts[0];
          const root=chart.getContext().canvas.document.documentElement;
          const mark=[...root.querySelectorAll('.element')].find(node=>node.__data__.data?._y===7);
          const box=mark.getBBox(), canvas=document.querySelector('#chart-0 canvas').getBoundingClientRect();
          return {x:canvas.x+box.x+box.width/2, y:canvas.y+box.y+box.height/2};
        }""")
        page.mouse.move(point["x"], point["y"])
        page.wait_for_timeout(150)  # Exercise the pinned runtime's 50 ms tooltip interaction throttle.
        assert page.locator("[data-deepviz-literal]").count() == 0, "Series text became active tooltip HTML"
        assert seen["page_errors"] == seen["console_errors"] == seen["unexpected_requests"] == []
        _table(page, 0, [["0", "7", literal], ["1", "19", literal]])
