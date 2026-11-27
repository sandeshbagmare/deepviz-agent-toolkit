// Real G2 CDN, untouched render() HTML, native scenegraph and actual screenshots.
const assert = require('node:assert/strict');
const {createHash} = require('node:crypto');
const {readFile, writeFile, mkdir} = require('node:fs/promises');
const {createRequire} = require('node:module');
const path = require('node:path');
const {pathToFileURL} = require('node:url');

const [directory, toolRoot] = process.argv.slice(2);
assert.ok(directory && toolRoot, 'Usage: node r20-antv-color-scale.cjs NEW_GENERATED_DIR EXISTING_NODE_TOOLS');
const output = path.resolve(directory), load = createRequire(path.join(path.resolve(toolRoot), 'package.json'));
const hash = value => createHash('sha256').update(value).digest('hex');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const cdn = 'https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js';
const number = text => Number(String(text).replaceAll(',', '').replaceAll('\u2212', '-'));

async function main() {
  const {chromium} = load('playwright'), input = JSON.parse(await readFile(path.join(output, 'cases.json'), 'utf8'));
  const screenshots = path.join(output, 'screenshots'); await mkdir(screenshots);
  const browser = await chromium.launch({headless: true});
  const report = {identity: input.identity, node: process.version, playwright: load('playwright/package.json').version,
    chromium: browser.version(), method: 'Unchanged HTML first without observer, then separately constructor-return-only observation. Real CDN, no routes, payload changes, legend suppression or fake assets.',
    cases: [], checks: []};
  const check = (id, name, pass, observed) => report.checks.push({id, name, pass: Boolean(pass), observed});

  async function open(fixture, observe) {
    const page = await browser.newPage({viewport: {width: 1200, height: 900}, deviceScaleFactor: 1});
    const result = {mode: observe ? 'constructor-return-only' : 'unmodified', errors: [], assets: [], failedRequests: []};
    const responses = [];
    page.on('console', message => {if (message.type() === 'error') result.errors.push({kind: 'console', message: message.text()});});
    page.on('pageerror', error => result.errors.push({kind: 'page', message: String(error)}));
    page.on('requestfailed', request => result.failedRequests.push({url: request.url(), error: request.failure()?.errorText}));
    page.on('response', response => {if (response.url().startsWith('https:')) responses.push(response);});
    if (observe) await page.addInitScript(() => {
      window.__r20Charts = []; let library;
      Object.defineProperty(window, 'G2', {configurable: true, get: () => library, set: value => {
        library = value; let constructor;
        Object.defineProperty(value, 'Chart', {configurable: true, enumerable: true, get: () => constructor, set: original => {
          constructor = new Proxy(original, {construct(target, args, newTarget) {
            const chart = Reflect.construct(target, args, newTarget); window.__r20Charts.push(chart); return chart;
          }});
        }});
      }});
    });
    try {
      await page.goto(pathToFileURL(path.join(output, fixture.html)).href, {waitUntil: 'load', timeout: 60000});
      result.ready = await page.evaluate(async () => {
        if (!window.deepvizReady?.then) return {status: 'missing'};
        return Promise.race([window.deepvizReady.then(() => ({status: 'resolved'}), error => ({status: 'rejected', error: String(error)})),
          new Promise(resolve => setTimeout(() => resolve({status: 'timeout'}), 20000))]);
      });
      result.state = await page.evaluate(observe => {
        const options = JSON.parse(document.getElementById('deepviz-data').textContent);
        const charts = [...document.querySelectorAll('[role="img"]')].map((element, index) => {
          const canvas = element.querySelector('canvas'), ctx = canvas?.getContext('2d');
          const pixels = ctx?.getImageData(0, 0, canvas.width, canvas.height).data;
          let painted = 0;
          if (pixels) for (let i = 0; i < pixels.length; i += 4) if (pixels[i + 3] && pixels[i] + pixels[i + 1] + pixels[i + 2] < 650) painted++;
          const base = {id: element.id, width: element.clientWidth, height: element.clientHeight,
            background: getComputedStyle(element).backgroundColor, painted, marks: [], legend: [], texts: [], ticks: []};
          if (!observe || !window.__r20Charts[index]) return base;
          const root = window.__r20Charts[index].getContext().canvas.document.documentElement;
          const colorContext = document.createElement('canvas').getContext('2d');
          function describe(node) {
            let box; try {const b = node.getBBox(); box = {x: b.x, y: b.y, width: b.width, height: b.height};} catch {box = null;}
            const fill = node.getAttribute('fill'), stroke = node.getAttribute('stroke');
            colorContext.fillStyle = '#010203'; if (typeof fill === 'string') colorContext.fillStyle = fill;
            const fillColor = colorContext.fillStyle;
            return {node: node.nodeName, className: node.className, text: node.getAttribute('text'), fill, stroke, fillColor, box};
          }
          base.marks = [...root.querySelectorAll('.element')].map(describe);
          base.texts = [...root.querySelectorAll('text')].map(describe);
          base.legend = [...root.querySelectorAll('.g2-legend-item')].map(item => ({
            label: String(item.querySelector('text')?.getAttribute('text')),
            marker: item.querySelector('.g2-legend-marker') ? describe(item.querySelector('.g2-legend-marker')) : null,
          }));
          const continuous = root.querySelector('.legend-continuous');
          base.ticks = continuous ? [...continuous.querySelectorAll('text')].map(describe) : [];
          base.samples = base.marks.map(mark => {
            if (!ctx || !mark.box) return null;
            const x = Math.round(mark.box.x + mark.box.width / 2), y = Math.round(mark.box.y + mark.box.height / 2);
            return {x, y, rgba: [...ctx.getImageData(x, y, 1, 1).data]};
          });
          return base;
        });
        return {options, charts, title: document.querySelector('h1')?.textContent, bodyBackground: getComputedStyle(document.body).backgroundColor};
      }, observe);
      for (const response of responses) {
        const body = await response.body(); result.assets.push({url: response.url(), status: response.status(), bytes: body.length, sha256: await hash(body)});
      }
    } catch (error) {result.harnessError = String(error);}
    result.screenshot = fixture.id + (observe ? '-observed' : '-production') + '.png';
    await page.screenshot({path: path.join(screenshots, result.screenshot), fullPage: true});
    result.screenshotSha256 = hash(await readFile(path.join(screenshots, result.screenshot)));
    await page.close(); return result;
  }

  function categorical(id, native, expected) {
    const marks = native?.marks ?? [], legend = native?.legend ?? [];
    check(id, 'one-positive-area-mark-per-ordered-category', marks.length === expected.length && marks.every(mark => mark.box?.width > 1 && mark.box?.height > 1), marks);
    check(id, 'actual-categorical-fills-distinct', marks.length === expected.length && new Set(marks.map(mark => mark.fillColor)).size === expected.length, marks.map(mark => mark.fill));
    check(id, 'visible-legend-preserves-ordered-labels', same(legend.map(item => item.label), expected.map(item => item[0])), legend);
    check(id, 'actual-fills-match-actual-legend-colors', marks.length === legend.length && marks.length > 0 && legend.every((item, i) => item.marker?.fillColor === marks[i].fillColor), {legend, fills: marks.map(mark => mark.fillColor)});
  }

  try {
    for (const fixture of input.cases) {
      assert.equal(hash(await readFile(path.join(output, fixture.html))), fixture.html_sha256);
      const production = await open(fixture, false), observed = await open(fixture, true);
      check(fixture.id, 'unmodified-public-html-ready', production.ready?.status === 'resolved', production.ready ?? production.harnessError);
      check(fixture.id, 'zero-console-or-page-errors', !production.errors.length && !observed.errors.length, {production: production.errors, observed: observed.errors});
      check(fixture.id, 'real-exact-CDN-bytes', [production, observed].every(row => !row.harnessError && !row.failedRequests.length && row.assets.length === 1 && row.assets.every(asset => asset.url === cdn && asset.status === 200 && asset.bytes > 100000)) && production.assets[0].sha256 === observed.assets[0].sha256, {production: production.assets, observed: observed.assets});
      check(fixture.id, 'observation-preserves-readiness', production.ready?.status === observed.ready?.status, {production: production.ready, observed: observed.ready});
      check(fixture.id, 'native-payload-equals-public-manifest', same(production.state?.options, fixture.manifest.native_specs) && same(observed.state?.options, fixture.manifest.native_specs), fixture.manifest.native_specs);
      check(fixture.id, 'literal-public-input-records-unchanged', same(fixture.manifest.charts[0].records, fixture.rows), fixture.manifest.charts[0].records);
      const native = observed.state?.charts[0], marks = native?.marks ?? [], payload = fixture.manifest.native_specs[0];
      if (fixture.mode === 'category') {
        check(fixture.id, 'literal-category-values', same(payload.data.map(row => [row._x, row._y]), fixture.expected), payload.data);
        categorical(fixture.id, native, fixture.expected);
        if (payload.type === 'rect') {
          const total = fixture.expected.reduce((sum, row) => sum + row[1], 0), width = marks.reduce((sum, mark) => sum + (mark.box?.width ?? 0), 0);
          check(fixture.id, 'treemap-widths-preserve-values', marks.length === fixture.expected.length && marks.every((mark, i) => Math.abs(mark.box.width / width - fixture.expected[i][1] / total) < 1e-6), marks.map(mark => mark.box));
        }
      } else if (fixture.mode === 'heatmap') {
        check(fixture.id, 'literal-quantitative-values', same(payload.data.map(row => row._heat), fixture.expected), payload.data);
        check(fixture.id, 'exact-number-of-positive-area-cells', marks.length === fixture.expected.length && marks.every(mark => mark.box?.width > 10 && mark.box?.height > 10), marks);
        const unequal = new Set(fixture.expected).size > 1;
        check(fixture.id, 'actual-cell-colors-distinct-iff-values-differ', marks.length === fixture.expected.length && new Set(marks.map(mark => mark.fillColor)).size === (fixture.expected.length ? unequal ? 2 : 1 : 0), marks.map(mark => mark.fill));
        if (fixture.expected.length) {
          const texts = (native?.ticks ?? []).map(row => row.text), ticks = texts.map(number).filter(Number.isFinite);
          check(fixture.id, 'visible-quantitative-legend-covers-literal-extent', ticks.length > 0 && fixture.expected.every(value => Math.min(...ticks) <= value && Math.max(...ticks) >= value), {texts, ticks});
          const labels = (native?.ticks ?? []).filter(row => Number.isFinite(number(row.text)));
          check(fixture.id, 'visible-legend-labels-stay-inside-real-canvas', labels.length >= 2 && labels.every(row => row.box && row.box.x >= 0 && row.box.y >= 0 && row.box.x + row.box.width <= native.width && row.box.y + row.box.height <= native.height), {width: native?.width, height: native?.height, labels});
          check(fixture.id, 'literal-ordered-grid-cells', marks.length === 2 && marks[0].box?.x < marks[1].box?.x && marks[0].box?.y < marks[1].box?.y, marks.map(mark => mark.box));
          if (unequal) check(fixture.id, 'actual-painted-cell-centers-differ', !same(native?.samples?.[0]?.rgba, native?.samples?.[1]?.rgba), native?.samples);
        }
      } else if (fixture.mode === 'fixed') {
        const points = fixture.id === 'line' ? marks.filter(mark => mark.box?.width === 6 && mark.box?.height === 6) : marks;
        check(fixture.id, 'three-original-fixed-blue-points', points.length === 3 && points.every(mark => mark.fillColor === '#386cb0'), points);
        const xs = points.map(mark => mark.box.x + mark.box.width / 2), ratio = (xs[2] - xs[1]) / (xs[1] - xs[0]);
        check(fixture.id, 'literal-1-to-2-numeric-x-spacing', Math.abs(ratio - 2) < 1e-6, {xs, ratio});
      } else {
        const charts = observed.state?.charts ?? [];
        check(fixture.id, 'three-independent-native-chart-containers', charts.length === 3 && new Set(charts.map(chart => chart.id)).size === 3 && charts.every(chart => chart.marks.length > 0), charts.map(chart => ({id: chart.id, count: chart.marks.length})));
        check(fixture.id, 'child-theme-backgrounds-preserved', same(charts.map(chart => chart.background), ['rgb(255, 255, 255)', 'rgb(23, 27, 38)', 'rgb(23, 27, 38)']), charts.map(chart => chart.background));
        check(fixture.id, 'parent-theme-background-preserved', production.state?.bodyBackground === (fixture.spec.theme === 'dark' ? 'rgb(23, 27, 38)' : 'rgb(255, 255, 255)'), production.state?.bodyBackground);
        const expected = [['Alpha', 12], ['Beta', 31], ['Gamma', 7]];
        categorical(fixture.id + '/pie', charts[0], expected); categorical(fixture.id + '/treemap', charts[2], expected);
        check(fixture.id, 'line-control-has-connected-plus-point-marks', charts[1]?.marks.length === 4, charts[1]?.marks);
      }
      assert.equal(hash(await readFile(path.join(output, fixture.html))), fixture.html_sha256);
      report.cases.push({id: fixture.id, production, observed});
      await writeFile(path.join(output, 'browser-results.json'), JSON.stringify(report, null, 2));
      console.log(fixture.id + ': ready=' + production.ready?.status + ' failures=' + report.checks.filter(row => row.id.startsWith(fixture.id) && !row.pass).length);
    }
  } finally {await browser.close();}
  report.totals = {cases: report.cases.length, checks: report.checks.length, passed: report.checks.filter(row => row.pass).length, failed: report.checks.filter(row => !row.pass).length, skipped: 0};
  await writeFile(path.join(output, 'browser-results.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({...report.totals, failures: report.checks.filter(row => !row.pass).map(({id, name}) => ({id, name}))}));
  process.exitCode = report.totals.failed ? 1 : 0;
}
main().catch(error => {console.error(String(error)); process.exitCode = 1;});
