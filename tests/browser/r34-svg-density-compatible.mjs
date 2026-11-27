// Removing density layout must fail actual glyph-box checks, not just an SVG-text assertion.
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {join, resolve} from 'node:path';
import {after, before, test} from 'node:test';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {render} from '../../packages/deepviz/dist/index.js';

const root = fileURLToPath(new URL('../../', import.meta.url));
const output = resolve(process.env.DEEPVIZ_R34_OUTPUT);
await mkdir(output, {recursive: true});
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const save = (name, value) => writeFile(join(output, name), JSON.stringify(value, null, 2), {flag: 'wx'});
const measured = [6249996250000, 6249997500000, 6249998750000, 6250000000000,
  6250001250000, 6250002500000, 6250003750000, 6250005000000];
const cases = [
  {name: 'measured-eight', values: measured},
  {name: 'signed-eight', values: [-9.999e120, -6e120, -3e120, -1e120, 1e120, 3e120, 6e120, 9.999e120]},
  {name: 'fixed-negative-eight', values: [-0.000001, 1, 2, 3, 4, 5, 6, 7]},
  {name: 'forty-accessible', width: 960, height: 540, values: Array.from({length: 40}, (_, i) => i),
    labels: Array.from({length: 40}, (_, i) => `Common long category name ${i}`)},
  {name: 'forty-minimum', values: Array.from({length: 40}, (_, i) => i),
    labels: Array.from({length: 40}, (_, i) => `Common long category name ${i}`)},
  {name: 'unicode-large-eight', values: Array.from({length: 8}, (_, i) => (i + 1) * 1e307),
    labels: Array.from({length: 8}, (_, i) => `東京都東部支店${i + 1}`)},
  {name: 'legacy-thousand', values: Array.from({length: 1000}, (_, i) => i),
    labels: Array.from({length: 1000}, (_, i) => `Common long category name ${i}`)},
  {name: 'two-finite-35px', values: [-1e308, 1e308], labels: ['negative', 'positive']},
];
let browser;
before(async () => {
  const playwright = await import(pathToFileURL(resolve(process.env.DEEPVIZ_PLAYWRIGHT_ENTRY)).href);
  browser = await playwright.chromium.launch({headless: true});
  await save('identity.json', {head: execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(),
    source_sha256: hash(await readFile(join(root, 'packages/deepviz/src/renderers.ts'))),
    imported_dist_sha256: hash(await readFile(join(root, 'packages/deepviz/dist/renderers.js'))),
    imported_file: fileURLToPath(import.meta.resolve('../../packages/deepviz/dist/index.js')),
    probe_sha256: hash(await readFile(fileURLToPath(import.meta.url))), node: process.version, chromium: browser.version()});
});
after(async () => {await browser?.close();});

for (const fixture of cases) for (const carrier of ['svg', 'html']) {
  test(`R34 ${fixture.name} ${carrier}: readable boxes and unchanged literal measures`, async () => {
    const width = fixture.width ?? 240, height = fixture.height ?? 200;
    const labels = fixture.labels ?? fixture.values.map((_, i) => `g${i}`);
    const rows = fixture.values.map((value, i) => ({group: labels[i], value}));
    const beforeRows = JSON.stringify(rows);
    const artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none', width, height,
      title: `R34 ${fixture.name}`}, 'svg');
    assert.equal(JSON.stringify(rows), beforeRows);
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    assert.equal(artifact.input_count, rows.length);
    assert.equal(artifact.output_count, rows.length);
    const stem = `${fixture.name}-${carrier}`, input = join(output, `${stem}.${carrier}`);
    const content = carrier === 'svg' ? artifact.renderer_spec.spec.svg : artifact.html;
    await writeFile(input, content, {flag: 'wx'});
    const context = await browser.newContext({viewport: {width: 1100, height: 850}, offline: true, deviceScaleFactor: 1});
    try {
      const page = await context.newPage(), errors = [];
      page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
      page.on('pageerror', error => errors.push(String(error)));
      page.on('request', request => {if (/^https?:/.test(request.url())) errors.push(request.url());});
      page.on('requestfailed', request => errors.push(request.url()));
      await page.goto(pathToFileURL(input).href, {waitUntil: 'load'});
      if (carrier === 'html') await page.waitForFunction(() => globalThis.deepvizReady === true);
      await page.evaluate(() => document.fonts.ready);
      const geometry = await page.locator(carrier === 'html' ? '#chart-0 svg' : 'svg').evaluate(svg => {
        const origin = svg.getBoundingClientRect();
        const texts = [...svg.querySelectorAll('text')].map(text => {
          const box = text.getBBox(), matrix = text.getScreenCTM(), style = getComputedStyle(text);
          const corners = [[box.x, box.y], [box.x + box.width, box.y], [box.x, box.y + box.height],
            [box.x + box.width, box.y + box.height]].map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
          return {text: [...text.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(''),
            title: text.querySelector('title')?.textContent, category: text.classList.contains('category-tick'),
            x: Math.min(...corners.map(p => p.x)) - origin.x, right: Math.max(...corners.map(p => p.x)) - origin.x,
            y: Math.min(...corners.map(p => p.y)) - origin.y, bottom: Math.max(...corners.map(p => p.y)) - origin.y,
            font_size: parseFloat(style.fontSize), visible: style.display !== 'none' && style.visibility === 'visible' && +style.opacity > 0};
        });
        const bars = [...svg.querySelectorAll('rect.mark')].map(bar => ({title: bar.querySelector('title').textContent,
          x: +bar.getAttribute('x'), y: +bar.getAttribute('y'), width: +bar.getAttribute('width'), height: +bar.getAttribute('height')}));
        return {width: svg.viewBox.baseVal.width, height: svg.viewBox.baseVal.height, texts, bars};
      });
      const overlap = [];
      for (let i = 0; i < geometry.texts.length; i++) for (let j = i + 1; j < geometry.texts.length; j++) {
        const a = geometry.texts[i], b = geometry.texts[j];
        if (Math.min(a.right, b.right) - Math.max(a.x, b.x) > 0.1 &&
            Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y) > 0.1) overlap.push([a.text, b.text]);
      }
      const runtimeErrors = carrier === 'html' ? await page.evaluate(() => globalThis.deepvizErrors) : [];
      if (carrier === 'html' && fixture.values.length > 12) await page.locator('summary').click();
      const png = await page.screenshot({fullPage: carrier === 'html'});
      await writeFile(join(output, `${stem}.png`), png, {flag: 'wx'});
      await save(`${stem}.json`, {fixture, carrier, geometry, overlap, errors, runtimeErrors,
        input_sha256: hash(content), png_sha256: hash(png)});
      assert.deepEqual(errors, []);
      assert.deepEqual(runtimeErrors, []);
      assert.equal(geometry.width, width); assert.equal(geometry.height, height);
      assert.deepEqual(geometry.bars.map(bar => bar.title), labels.map((label, i) => `${label}: ${fixture.values[i]}`));
      const unitIndex = fixture.values.findIndex(value => value !== 0);
      const unit = geometry.bars[unitIndex].height / Math.abs(fixture.values[unitIndex]);
      const zero = geometry.bars[unitIndex].y + (fixture.values[unitIndex] > 0 ? geometry.bars[unitIndex].height : 0);
      geometry.bars.forEach((bar, i) => {
        assert.ok(bar.width > 0 && bar.x >= 0 && bar.x + bar.width <= width);
        assert.ok(fixture.values[i] === 0 ? bar.height === 0 : bar.height > 0);
        assert.ok(Math.abs(bar.height - Math.abs(fixture.values[i]) * unit) < 1e-6);
        assert.ok(Math.abs(bar.y + (fixture.values[i] > 0 ? bar.height : 0) - zero) < 1e-6);
      });
      if (fixture.name === 'two-finite-35px') assert.deepEqual(geometry.bars.map(bar => bar.height), [35, 35]);
      const categories = geometry.texts.filter(text => text.category);
      if (fixture.values.length > 12) {
        assert.ok(categories.length >= 5 && categories.length <= 15);
        assert.equal(new Set(categories.map(text => text.text)).size, categories.length);
        assert.ok(categories.some(text => text.text.includes('…')));
        for (const category of categories) assert.ok(labels.includes(category.title));
        if (carrier === 'html') assert.deepEqual(await page.locator('tbody tr td:first-child').allTextContents(), labels);
      } else assert.deepEqual(categories.map(text => text.text), labels);
      for (const text of geometry.texts) {
        assert.ok(text.visible && text.font_size >= 12);
        assert.ok(text.x >= -0.05 && text.y >= -0.05 && text.right <= width + 0.05 && text.bottom <= height + 0.05,
          `clipped text ${text.text}: ${JSON.stringify(text)}`);
      }
      assert.deepEqual(overlap, [], 'actual label/numeric/axis-title boxes must not overlap');
    } finally {await context.close();}
  });
}
