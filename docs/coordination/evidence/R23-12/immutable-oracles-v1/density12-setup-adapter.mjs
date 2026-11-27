import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir, mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {after, before, test} from 'node:test';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {render} from "file:///C:/Users/bagma/AppData/Local/Temp/opencode/r23-12-svg-finite-density-ses_de5678115ffewUEpZFi8faBW8C/packages/deepviz/dist/index.js";

const root = "C:\\Users\\bagma\\AppData\\Local\\Temp\\opencode\\r23-12-svg-finite-density-ses_de5678115ffewUEpZFi8faBW8C";
const output = process.env.DEEPVIZ_R17_OUTPUT
  ? resolve(process.env.DEEPVIZ_R17_OUTPUT) : await mkdtemp(join(tmpdir(), 'deepviz-r17-density-'));
await mkdir(output, {recursive: true});
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const save = (name, value) => writeFile(join(output, name), JSON.stringify(value, null, 2), {flag: 'wx'});
const fixtures = [
  {name: 'ordinary-eight', labels: Array.from({length: 8}, (_, i) => `g${i}`)},
  // Finite multilingual branch names, below the renderer's existing 18-character abbreviation threshold.
  {name: 'unicode-eight', labels: Array.from({length: 8}, (_, i) => `東京都東部支店${i + 1}`)},
];
function intersections(boxes) {
  const result = [];
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const width = Math.min(boxes[i].right, boxes[j].right) - Math.max(boxes[i].x, boxes[j].x);
    const height = Math.min(boxes[i].bottom, boxes[j].bottom) - Math.max(boxes[i].y, boxes[j].y);
    if (width > 0.1 && height > 0.1) result.push({a: boxes[i].text, b: boxes[j].text, width, height});
  }
  return result;
}
let browser;
before(async () => {
  const playwright = process.env.DEEPVIZ_PLAYWRIGHT_ENTRY
    ? await import(pathToFileURL(resolve(process.env.DEEPVIZ_PLAYWRIGHT_ENTRY)).href) : await import('playwright');
  browser = await playwright.chromium.launch({headless: true});
  await save('identity.json', {observed_head: execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(),
    renderer_source_sha256: hash(await readFile(join(root, 'packages/deepviz/src/renderers.ts'))),
    imported_renderer_sha256: hash(await readFile(join(root, 'packages/deepviz/dist/renderers.js'))),
    probe_sha256: hash(await readFile(fileURLToPath(import.meta.url))), node: process.version, chromium: browser.version(),
    output, reused_existing_build: true, no_scale_rerun: true});
});
after(async () => {await browser?.close();});

test('R17 pairwise oracle rejects overlap but not edge contact or separate rows', () => {
  const a = {text: 'a', x: 0, y: 0, right: 10, bottom: 10};
  assert.equal(intersections([a, {...a, text: 'b', x: 9, right: 19}]).length, 1);
  assert.deepEqual(intersections([a, {...a, text: 'b', x: 10, right: 20}]), []);
  assert.deepEqual(intersections([a, {...a, text: 'b', y: 11, bottom: 21}]), []);
});

for (const fixture of fixtures) for (const [width, height] of [[240, 200], [960, 540]]) for (const carrier of ['svg', 'html']) {
  test(`R17 ${fixture.name} ${width}x${height} ${carrier}: complete category labels do not overlap`, async t => {
    const rows = fixture.labels.map((group, i) => ({group, value: i + 1}));
    const artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none', max_points: 10,
      width, height, title: `R17 ${fixture.name}`}, 'svg');
    assert.equal(artifact.input_count, 8);
    assert.equal(artifact.output_count, 8);
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    const stem = `${fixture.name}-${width}-${carrier}`;
    const content = carrier === 'html' ? artifact.html : artifact.renderer_spec.spec.svg;
    const input = join(output, `${stem}.${carrier}`);
    await writeFile(input, content, {flag: 'wx'});
    const context = await browser.newContext({viewport: {width: 1100, height: 850}, deviceScaleFactor: 1, offline: true});
    try {
      const page = await context.newPage();
      const consoleErrors = [], pageErrors = [], externalRequests = [], failedRequests = [];
      page.on('console', message => {if (message.type() === 'error') consoleErrors.push(message.text());});
      page.on('pageerror', error => pageErrors.push(String(error)));
      page.on('request', request => {if (/^https?:/.test(request.url())) externalRequests.push(request.url());});
      page.on('requestfailed', request => failedRequests.push(request.url()));
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto(pathToFileURL(input).href, {waitUntil: 'load'});
      if (carrier === 'html') await page.waitForFunction(() => globalThis.deepvizReady === true);
      await page.evaluate(() => document.fonts.ready);
      const geometry = await page.locator(carrier === 'html' ? '#chart-0 svg' : 'svg').evaluate(svg => {
        const origin = svg.getBoundingClientRect();
        const texts = [...svg.querySelectorAll('text')].map(text => {
          const box = text.getBBox(), matrix = text.getScreenCTM(), style = getComputedStyle(text);
          const corners = [[box.x, box.y], [box.x + box.width, box.y], [box.x, box.y + box.height], [box.x + box.width, box.y + box.height]]
            .map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
          return {text: [...text.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(''),
            category: text.classList.contains('category-tick'), center: +text.getAttribute('x'),
            x: Math.min(...corners.map(p => p.x)) - origin.x, right: Math.max(...corners.map(p => p.x)) - origin.x,
            y: Math.min(...corners.map(p => p.y)) - origin.y, bottom: Math.max(...corners.map(p => p.y)) - origin.y,
            width: box.width, height: box.height, font_family: style.fontFamily, font_size: parseFloat(style.fontSize),
            visibility: style.visibility, display: style.display, opacity: style.opacity};
        });
        const bars = [...svg.querySelectorAll('rect.mark')].map(bar => ({title: bar.querySelector('title')?.textContent,
          x: +bar.getAttribute('x'), y: +bar.getAttribute('y'), width: +bar.getAttribute('width'), height: +bar.getAttribute('height'),
          visibility: getComputedStyle(bar).visibility, opacity: getComputedStyle(bar).opacity, client_rects: bar.getClientRects().length}));
        return {width: svg.viewBox.baseVal.width, height: svg.viewBox.baseVal.height, texts, bars};
      });
      const labels = geometry.texts.filter(text => text.category);
      const overlap = intersections(labels);
      const adjacentGaps = labels.slice(1).map((text, i) => text.x - labels[i].right);
      const slot = labels[1].center - labels[0].center;
      const layout = {plot_left: labels[0].center - slot / 2, plot_width: slot * labels.length, category_slot_width: slot,
        adjacent_gaps: adjacentGaps, min_adjacent_gap: Math.min(...adjacentGaps), overlapping_pairs: overlap};
      const runtimeErrors = carrier === 'html' ? await page.evaluate(() => globalThis.deepvizErrors) : [];
      const png = await page.screenshot({fullPage: carrier === 'html'});
      await writeFile(join(output, `${stem}.png`), png, {flag: 'wx'});
      const clipped = geometry.texts.filter(text => text.x < -0.05 || text.y < -0.05 || text.right > width + 0.05 || text.bottom > height + 0.05);
      await save(`${stem}.json`, {fixture, width, height, carrier, geometry, layout, clipped, consoleErrors, pageErrors,
        externalRequests, failedRequests, runtimeErrors, input_sha256: hash(content), png_sha256: hash(png)});
      t.diagnostic(JSON.stringify({stem, ...layout, clipped: clipped.length, console_errors: consoleErrors.length, page_errors: pageErrors.length}));
      assert.deepEqual([consoleErrors, pageErrors, runtimeErrors, externalRequests, failedRequests], [[], [], [], [], []]);
      assert.equal(geometry.width, width);
      assert.equal(geometry.height, height);
      assert.deepEqual(labels.map(text => text.text), fixture.labels);
      assert.equal(geometry.bars.length, 8);
      const unit = geometry.bars[0].height;
      const zero = geometry.bars[0].y + geometry.bars[0].height;
      geometry.bars.forEach((bar, i) => {
        assert.equal(bar.title, `${fixture.labels[i]}: ${i + 1}`);
        assert.ok(bar.width > 0 && bar.height > 0 && bar.client_rects > 0 && bar.visibility === 'visible' && +bar.opacity > 0);
        assert.ok(Math.abs(bar.height - (i + 1) * unit) < 1e-6);
        assert.ok(Math.abs(bar.y + bar.height - zero) < 1e-6);
        assert.ok(Math.abs(bar.x + bar.width / 2 - labels[i].center) < 1e-6);
      });
      for (const text of labels) assert.ok(text.width > 0 && text.height > 0 && text.font_size >= 10 &&
        text.visibility === 'visible' && text.display !== 'none' && +text.opacity > 0);
      assert.deepEqual(clipped, [], 'containment is necessary but not sufficient for readable labels');
      assert.deepEqual(overlap, [], `category glyph boxes overlap: ${stem}, minimum horizontal gap ${layout.min_adjacent_gap}px`);
    } finally {
      await context.close();
    }
  });
}
