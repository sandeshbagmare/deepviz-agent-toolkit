// Independent bounded semantic oracles; original public HTML, exact real G2 cached locally.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const {createHash} = require('node:crypto');
const {createRequire} = require('node:module');
const {pathToFileURL} = require('node:url');
const sha = data => createHash('sha256').update(data).digest('hex');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const number = value => Number(String(value).replaceAll('\u2212', '-').replaceAll(',', ''));
const [directory] = process.argv.slice(2);
const CDN = 'https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js';

async function main() {
  const output = path.resolve(directory), input = JSON.parse(await fs.readFile(path.join(output, 'cases.json'), 'utf8'));
  const identity = input.identity, source = identity.source_root;
  assert.equal(identity.source, '3185e0d9936c7d6f1a9d30b94089b804d75fe991');
  async function proof() {
    for (const row of identity.Git_exact_source_files) assert.equal(sha(await fs.readFile(path.join(source, row.path))), row.sha256);
    for (const row of identity.own_probe_files) assert.equal(sha(await fs.readFile(row.path)), row.sha256);
    assert.equal(sha(await fs.readFile(identity.G2.path)), identity.G2.sha256);
  }
  await proof();
  const load = createRequire(path.join(identity.consumer_tools_root, 'package.json'));
  const playwrightFile = load.resolve('playwright'), playwrightPackage = load.resolve('playwright/package.json');
  const {chromium} = load('playwright'), browser = await chromium.launch({headless: true});
  const report = {source: identity.source, G2: identity.G2, node: process.version,
    playwright: {entry: playwrightFile, entry_sha256: sha(await fs.readFile(playwrightFile)),
      version: JSON.parse(await fs.readFile(playwrightPackage)).version}, chromium: browser.version(),
    method: 'Unmodified public HTML, two fresh navigations per fixture. Explicit route serves read-only exact real G2 5.4.8 bytes at original pinned URL; NOT CDN health. First native rendering unobserved, second constructor-return-only Proxy for scenegraph. No options, data, paint, legend, library or DOM modifications.',
    checks: [], cases: []};
  await fs.mkdir(path.join(output, 'screenshots'));
  function check(id, name, passed, actual) {report.checks.push({id, name, pass: Boolean(passed), actual});}
  function inside(box, chart) {return box && [box.x, box.y, box.width, box.height].every(Number.isFinite) &&
    box.x >= -0.01 && box.y >= -0.01 && box.x + box.width <= chart.width + .01 && box.y + box.height <= chart.height + .01;}

  async function visit(fixture, observed) {
    const page = await browser.newPage({viewport: {width: 1420, height: 1000}, deviceScaleFactor: 1});
    const result = {observed, errors: [], failedRequests: [], locallyServedAssets: []};
    const responses = [];
    page.on('console', message => {if (message.type() === 'error') result.errors.push({kind: 'console', message: message.text()});});
    page.on('pageerror', error => result.errors.push({kind: 'page', message: String(error)}));
    page.on('requestfailed', request => result.failedRequests.push({url: request.url(), error: request.failure()?.errorText}));
    page.on('response', response => {if (response.url().startsWith('https:')) responses.push(response);});
    await page.route(CDN, route => route.fulfill({status: 200, contentType: 'application/javascript', path: identity.G2.path}));
    if (observed) await page.addInitScript(() => {
      window.__role17Charts = [];
      let realLibrary;
      Object.defineProperty(window, 'G2', {configurable: true, get: () => realLibrary, set: value => {
        realLibrary = value;
        let chartConstructor;
        Object.defineProperty(value, 'Chart', {configurable: true, enumerable: true, get: () => chartConstructor, set: original => {
          chartConstructor = new Proxy(original, {construct(target, args, newTarget) {
            const chart = Reflect.construct(target, args, newTarget);
            window.__role17Charts.push(chart);
            return chart;
          }});
        }});
      }});
    });
    try {
      await page.goto(pathToFileURL(path.join(output, fixture.html)).href, {waitUntil: 'load', timeout: 30000});
      result.ready = await page.evaluate(async () => {
        if (!window.deepvizReady?.then) return {status: 'missing'};
        return Promise.race([window.deepvizReady.then(() => ({status: 'resolved'}), error => ({status: 'rejected', error: String(error)})),
          new Promise(resolve => setTimeout(() => resolve({status: 'timeout'}), 15000))]);
      });
      result.state = await page.evaluate(observed => {
        const payloads = JSON.parse(document.getElementById('deepviz-data').textContent);
        const colorContext = document.createElement('canvas').getContext('2d');
        function describe(node) {
          let box = null;
          try {const b = node.getBBox(); box = {x: b.x, y: b.y, width: b.width, height: b.height};} catch {}
          const fill = node.getAttribute('fill');
          colorContext.fillStyle = '#010203';
          if (typeof fill === 'string') colorContext.fillStyle = fill;
          return {node: node.nodeName, className: node.className, text: node.getAttribute('text'),
            fill, normalizedColor: colorContext.fillStyle, stroke: node.getAttribute('stroke'), box};
        }
        const charts = [...document.querySelectorAll('[role="img"]')].map((element, index) => {
          const canvas = element.querySelector('canvas'), ctx = canvas?.getContext('2d');
          let painted = 0;
          if (ctx) {const p = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
            for (let i = 0; i < p.length; i += 4) if (p[i + 3]) painted++;}
          const record = {id: element.id, width: element.clientWidth, height: element.clientHeight,
            canvasWidth: canvas?.width, canvasHeight: canvas?.height, paintedPixels: painted,
            background: getComputedStyle(element).backgroundColor, marks: [], legend: [], ticks: []};
          if (!observed || !window.__role17Charts[index]) return record;
          const root = window.__role17Charts[index].getContext().canvas.document.documentElement;
          record.marks = [...root.querySelectorAll('.element')].map(describe);
          record.legend = [...root.querySelectorAll('.g2-legend-item')].map(item => ({
            label: item.querySelector('text') ? describe(item.querySelector('text')) : null,
            marker: item.querySelector('.g2-legend-marker') ? describe(item.querySelector('.g2-legend-marker')) : null}));
          const continuous = root.querySelector('.legend-continuous');
          record.ticks = continuous ? [...continuous.querySelectorAll('text')].map(describe) : [];
          record.samples = record.marks.map(mark => {
            if (!ctx || !mark.box) return null;
            const x = Math.round(mark.box.x + mark.box.width / 2), y = Math.round(mark.box.y + mark.box.height / 2);
            return {x, y, rgba: [...ctx.getImageData(x, y, 1, 1).data]};
          });
          return record;
        });
        return {payloads, charts, bodyBackground: getComputedStyle(document.body).backgroundColor,
          title: document.querySelector('h1')?.textContent, renderError: document.body.dataset.renderError ?? null};
      }, observed);
      for (const response of responses) {
        const bytes = await response.body();
        result.locallyServedAssets.push({url: response.url(), status: response.status(), bytes: bytes.length, sha256: sha(bytes)});
      }
    } catch (error) {result.harnessError = String(error);}
    result.screenshot = fixture.id + (observed ? '-observed.png' : '-public.png');
    await page.screenshot({path: path.join(output, 'screenshots', result.screenshot), fullPage: true});
    result.screenshot_sha256 = sha(await fs.readFile(path.join(output, 'screenshots', result.screenshot)));
    await page.close();
    return result;
  }

  function categories(id, chart, native) {
    const marks = chart?.marks ?? [], legend = chart?.legend ?? [];
    check(id, 'four-real-positive-area-categorical-marks', marks.length === 4 && marks.every(mark => mark.box?.width > 1 && mark.box?.height > 1 && inside(mark.box, chart)), marks);
    check(id, 'four-distinct-actual-mark-colors', new Set(marks.map(mark => mark.normalizedColor)).size === 4, marks.map(mark => mark.normalizedColor));
    check(id, 'full-ordered-literal-legend-labels', same(legend.map(item => String(item.label?.text)), input.category_expected.map(row => row[0])), legend);
    check(id, 'visible-full-legend-labels-inside-canvas', legend.length === 4 && legend.every(item => inside(item.label?.box, chart) && item.label.box.width > 0), legend);
    check(id, 'each-actual-mark-color-matches-its-actual-legend-marker', marks.length === 4 && legend.length === 4 && marks.every((mark, i) => mark.normalizedColor === legend[i].marker?.normalizedColor), {marks, legend});
    if (native.type === 'rect') {
      const total = marks.reduce((sum, mark) => sum + mark.box.width, 0);
      check(id, 'native-tiles-preserve-literal-rational-widths', marks.length === 4 && marks.every((mark, i) => Math.abs(mark.box.width / total - input.category_ratios[i]) < 1e-6), marks.map(mark => mark.box));
    }
  }
  try {
    for (const fixture of input.cases) {
      assert.equal(sha(await fs.readFile(path.join(output, fixture.html))), fixture.html_sha256);
      const production = await visit(fixture, false), observed = await visit(fixture, true);
      check(fixture.id, 'real-public-html-ready-with-and-without-observer', production.ready?.status === 'resolved' && observed.ready?.status === 'resolved', {production: production.ready, observed: observed.ready});
      check(fixture.id, 'zero-unexpected-console-page-request-or-harness-errors', [production, observed].every(row => !row.errors.length && !row.failedRequests.length && !row.harnessError && !row.state?.renderError), {production: {errors: production.errors, requests: production.failedRequests, harness: production.harnessError}, observed: {errors: observed.errors, requests: observed.failedRequests, harness: observed.harnessError}});
      check(fixture.id, 'exact-real-G2-bytes-explicit-local-transport-NOT-CDN-health', [production, observed].every(row => row.locallyServedAssets.length === 1 && row.locallyServedAssets.every(asset => asset.url === CDN && asset.status === 200 && asset.sha256 === identity.G2.sha256 && asset.bytes === identity.G2.bytes)), {production: production.locallyServedAssets, observed: observed.locallyServedAssets});
      check(fixture.id, 'unmodified-public-native-payload-equals-manifest', same(production.state?.payloads, fixture.manifest.native_specs) && same(observed.state?.payloads, fixture.manifest.native_specs), observed.state?.payloads);
      check(fixture.id, 'actual-canvases-painted-and-counts-correct', production.state?.charts.length === fixture.manifest.native_specs.length && production.state.charts.every(chart => chart.canvasWidth > 0 && chart.canvasHeight > 0 && chart.paintedPixels > 0), production.state?.charts);
      const chart = observed.state?.charts[0], marks = chart?.marks ?? [], native = fixture.manifest.native_specs[0];
      if (fixture.mode === 'category') categories(fixture.id, chart, native);
      else if (fixture.mode === 'heat') {
        check(fixture.id, 'native-cell-count-is-retained-literal-value-count', marks.length === fixture.expected_values.length && marks.every(mark => mark.box?.width > 10 && mark.box?.height > 10 && inside(mark.box, chart)), marks);
        check(fixture.id, 'actual-cell-colors-distinguish-distinct-literal-values', new Set(marks.map(mark => mark.normalizedColor)).size === new Set(fixture.expected_values).size, marks.map(mark => mark.normalizedColor));
        check(fixture.id, 'native-ordered-grid-positions-preserve-literal-coordinates', marks.length === fixture.expected_grid_indices.length && marks.every((mark, i) => marks.every((other, j) => {
          const a = fixture.expected_grid_indices[i], b = fixture.expected_grid_indices[j];
          return Math.sign(mark.box.x - other.box.x) === Math.sign(a[0] - b[0]) && Math.sign(mark.box.y - other.box.y) === Math.sign(a[1] - b[1]);
        })), marks.map(mark => mark.box));
        if (fixture.expected_values.length) {
          const ticks = chart.ticks.map(row => number(row.text)).filter(Number.isFinite);
          check(fixture.id, 'visible-legend-endpoints-cover-full-literal-extent', ticks.length >= 2 && fixture.expected_values.every(value => Math.min(...ticks) <= value && value <= Math.max(...ticks)), chart.ticks);
          check(fixture.id, 'full-numeric-legend-labels-inside-real-canvas', chart.ticks.length >= 2 && chart.ticks.every(row => inside(row.box, chart)), chart.ticks);
          check(fixture.id, 'actual-painted-cell-centers-distinguish-distinct-values', new Set(chart.samples.map(sample => JSON.stringify(sample?.rgba))).size === new Set(fixture.expected_values).size, chart.samples);
        }
      } else if (fixture.mode === 'position') {
        const xs = marks.map(mark => mark.box.x + mark.box.width / 2), gaps = xs.slice(1).map((x, i) => x - xs[i]);
        check(fixture.id, 'four-original-fixed-blue-native-points', marks.length === 4 && marks.every(mark => mark.normalizedColor === '#386cb0'), marks);
        check(fixture.id, 'numeric-x-spacing-literal-three-six-nine', gaps.length === 3 && gaps.every((gap, i) => Math.abs(gap / gaps[0] - fixture.expected_spacing_ratios[i]) < 1e-6), {xs, gaps});
        check(fixture.id, 'numeric-y-order-keeps-true-signed-values', marks.length === 4 && marks[3].box.y < marks[1].box.y && marks[1].box.y < marks[0].box.y && marks[0].box.y < marks[2].box.y, marks.map(mark => mark.box));
      } else {
        const charts = observed.state?.charts ?? [];
        check(fixture.id, 'two-independent-actual-chart-containers', charts.length === 2 && new Set(charts.map(chart => chart.id)).size === 2, charts);
        check(fixture.id, 'explicit-parent-theme-preserved', production.state?.bodyBackground === fixture.expected_body, production.state?.bodyBackground);
        check(fixture.id, 'opposite-parent-child-themes-preserved', same(charts.map(row => row.background), fixture.expected_backgrounds), charts.map(row => row.background));
        for (let i = 0; i < charts.length; i++) categories(fixture.id + '/child' + i, charts[i], fixture.manifest.native_specs[i]);
      }
      assert.equal(sha(await fs.readFile(path.join(output, fixture.html))), fixture.html_sha256);
      report.cases.push({id: fixture.id, production, observed});
      await fs.writeFile(path.join(output, 'browser-results.json'), JSON.stringify(report, null, 2));
      console.log(fixture.id + ': ' + report.checks.filter(row => row.id.startsWith(fixture.id) && !row.pass).length + ' failed checks');
    }
  } finally {await browser.close();}
  await proof();
  report.source_probe_asset_before_after_exact = true;
  report.totals = {cases: report.cases.length, checks: report.checks.length, passed: report.checks.filter(row => row.pass).length,
    failed: report.checks.filter(row => !row.pass).length, skipped: 0};
  await fs.writeFile(path.join(output, 'browser-results.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({...report.totals, failures: report.checks.filter(row => !row.pass).map(row => ({id: row.id, name: row.name}))}));
  process.exitCode = report.totals.failed ? 1 : 0;
}
main().catch(error => {console.error(error.stack ?? String(error)); process.exitCode = 1;});
