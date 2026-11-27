import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir, mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {after, before, test} from 'node:test';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {render} from '../../packages/deepviz/dist/index.js';

const root = fileURLToPath(new URL('../../', import.meta.url));
const output = process.env.DEEPVIZ_R11_OUTPUT
  ? resolve(process.env.DEEPVIZ_R11_OUTPUT) : await mkdtemp(join(tmpdir(), 'deepviz-r11-ticks-'));
await mkdir(output, {recursive: true});
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const save = (name, data) => writeFile(join(output, name), JSON.stringify(data, null, 2), {flag: 'wx'});
const cases = [
  {name: 'small-positive', values: [1, 2, 3, 4, 5, 6, 7, 8]},
  {name: 'measured-aggregate', values: [6249996250000, 6249997500000, 6249998750000,
    6250000000000, 6250001250000, 6250002500000, 6250003750000, 6250005000000]},
  {name: 'signed-scientific', values: [-9.999e120, -6e120, -3e120, -1e120, 1e120, 3e120, 6e120, 9.999e120]},
  {name: 'negative', values: [-1, -2, -3, -4, -5, -6, -7, -8]},
  {name: 'fixed-small-negative', values: [-0.000001, 1, 2, 3, 4, 5, 6, 7]},
];
let browser;
before(async () => {
  const playwright = process.env.DEEPVIZ_PLAYWRIGHT_ENTRY
    ? await import(pathToFileURL(resolve(process.env.DEEPVIZ_PLAYWRIGHT_ENTRY)).href) : await import('playwright');
  const executable = playwright.chromium.executablePath();
  browser = await playwright.chromium.launch({headless: true, executablePath: executable});
  await save('identity.json', {
    source_commit: execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(),
    source_dirty: execFileSync('git', ['diff', '--name-only'], {cwd: root, encoding: 'utf8'}).trim(),
    node: process.version, browser: browser.version(), executable,
    renderer_source_sha256: sha256(await readFile(join(root, 'packages/deepviz/src/renderers.ts'))),
    imported_build_sha256: sha256(await readFile(join(root, 'packages/deepviz/dist/renderers.js'))),
    test_sha256: sha256(await readFile(fileURLToPath(import.meta.url))), no_scale_rerun: true,
  });
});
after(async () => {await browser?.close();});

for (const fixture of cases) for (const [width, height] of [[960, 540], [240, 200]]) for (const carrier of ['html', 'svg']) {
  test(`R11 ${fixture.name} ${width}x${height} ${carrier}: native ticks fit and values remain exact`, async t => {
    const rows = fixture.values.map((value, i) => ({group: `g${i}`, value}));
    const artifact = render(rows, {kind: 'bar', title: `R11 ${fixture.name}`, x: 'group', y: 'value',
      aggregation: 'none', max_points: 10, width, height}, 'svg');
    assert.equal(artifact.input_count, 8);
    assert.equal(artifact.output_count, 8);
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    const stem = `${fixture.name}-${width}-${carrier}`;
    const content = carrier === 'html' ? artifact.html : artifact.renderer_spec.spec.svg;
    const inputPath = join(output, `${stem}.${carrier}`);
    await writeFile(inputPath, content, {flag: 'wx'});
    const context = await browser.newContext({viewport: {width: 1100, height: 850}, deviceScaleFactor: 1, offline: true});
    try {
      const page = await context.newPage();
      const consoleErrors = [], pageErrors = [], externalRequests = [], failedRequests = [];
      page.on('console', message => {if (message.type() === 'error') consoleErrors.push(message.text());});
      page.on('pageerror', error => pageErrors.push(String(error)));
      page.on('request', request => {if (/^https?:/.test(request.url())) externalRequests.push(request.url());});
      page.on('requestfailed', request => failedRequests.push(request.url()));
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto(pathToFileURL(inputPath).href, {waitUntil: 'load'});
      if (carrier === 'html') await page.waitForFunction(() => globalThis.deepvizReady === true);
      await page.evaluate(() => document.fonts.ready);
      const geometry = await page.locator(carrier === 'html' ? '#chart-0 svg' : 'svg').evaluate(svg => {
        const outer = svg.getBoundingClientRect();
        return {width: svg.viewBox.baseVal.width, height: svg.viewBox.baseVal.height,
          texts: [...svg.querySelectorAll('text')].map(text => {
            const box = text.getBBox(), matrix = text.getScreenCTM(), style = getComputedStyle(text);
            const corners = [[box.x, box.y], [box.x + box.width, box.y], [box.x, box.y + box.height], [box.x + box.width, box.y + box.height]]
              .map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
            return {text: [...text.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(''),
              x: Math.min(...corners.map(point => point.x)) - outer.x,
              y: Math.min(...corners.map(point => point.y)) - outer.y,
              right: Math.max(...corners.map(point => point.x)) - outer.x,
              bottom: Math.max(...corners.map(point => point.y)) - outer.y,
              width: box.width, height: box.height, font_size: parseFloat(style.fontSize),
              display: style.display, visibility: style.visibility};
          }),
          bars: [...svg.querySelectorAll('rect.mark')].map(mark => ({
            title: mark.querySelector('title')?.textContent, x: +mark.getAttribute('x'), y: +mark.getAttribute('y'),
            width: +mark.getAttribute('width'), height: +mark.getAttribute('height'),
            visibility: getComputedStyle(mark).visibility, rects: mark.getClientRects().length,
          }))};
      });
      // SVGDocument has no HTML body; viewport capture avoids full-page sizing timeout.
      const png = await page.screenshot({fullPage: carrier === 'html'});
      await writeFile(join(output, `${stem}.png`), png, {flag: 'wx'});
      const runtimeErrors = carrier === 'html' ? await page.evaluate(() => globalThis.deepvizErrors) : [];
      const clipped = geometry.texts.filter(text => text.x < -0.05 || text.y < -0.05 ||
        text.right > width + 0.05 || text.bottom > height + 0.05);
      await save(`${stem}.json`, {fixture: fixture.name, width, height, carrier,
        input_sha256: sha256(content), png_sha256: sha256(png), geometry, clipped,
        consoleErrors, pageErrors, runtimeErrors, externalRequests, failedRequests});
      t.diagnostic(JSON.stringify({stem, marks: geometry.bars.length, clipped, console_errors: consoleErrors.length, page_errors: pageErrors.length}));
      assert.deepEqual([consoleErrors, pageErrors, runtimeErrors, externalRequests, failedRequests], [[], [], [], [], []]);
      assert.equal(geometry.bars.length, 8);
      const min = Math.min(0, ...fixture.values), max = Math.max(1, ...fixture.values);
      const unit = geometry.bars[0].height / Math.abs(fixture.values[0]);
      const zero = geometry.bars[0].y + (fixture.values[0] >= 0 ? geometry.bars[0].height : 0);
      geometry.bars.forEach((bar, i) => {
        assert.equal(bar.title, `g${i}: ${fixture.values[i]}`);
        assert.ok(bar.width > 0 && bar.height > 0 && bar.rects > 0 && bar.visibility !== 'hidden');
        assert.ok(bar.x >= 0 && bar.x + bar.width <= width && bar.y >= 0 && bar.y + bar.height <= height);
        assert.ok(Math.abs(bar.height - Math.abs(fixture.values[i]) * unit) < 1e-6);
        assert.ok(Math.abs(bar.y + (fixture.values[i] >= 0 ? bar.height : 0) - zero) < 1e-6);
      });
      for (const label of ['group', 'value', ...rows.map(row => row.group), min.toPrecision(4), max.toPrecision(4)]) {
        const text = geometry.texts.find(item => item.text === label);
        assert.ok(text, `expected literal label absent: ${label}`);
        assert.ok(text.width > 0 && text.height > 0 && text.font_size >= 10 && text.display !== 'none' && text.visibility !== 'hidden');
      }
      assert.deepEqual(clipped, [], `labels must fit without hiding or truncation: ${stem}`);
    } finally {
      await context.close();
    }
  });
}
