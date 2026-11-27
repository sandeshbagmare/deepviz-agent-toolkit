import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir, mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {after, before, test} from 'node:test';
import {pathToFileURL} from 'node:url';
import {render} from '../../packages/deepviz/dist/index.js';

const output = process.env.R23_OUTPUT ? resolve(process.env.R23_OUTPUT) : await mkdtemp(join(tmpdir(), 'deepviz-r23-svg-'));
await mkdir(output, {recursive: true});
const save = (name, value) => writeFile(join(output, name), JSON.stringify(value, null, 2), {flag: 'wx'});
const hash = value => createHash('sha256').update(value).digest('hex');
let browser;
before(async () => {
  const playwright = process.env.R23_PLAYWRIGHT ? await import(pathToFileURL(resolve(process.env.R23_PLAYWRIGHT)).href) : await import('playwright');
  browser = await playwright.chromium.launch({headless: true});
  await save('identity.json', {head: execFileSync('git', ['rev-parse', 'HEAD'], {encoding: 'utf8'}).trim(), node: process.version,
    chromium: browser.version(), source_sha256: hash(await readFile('packages/deepviz/src/renderers.ts')),
    build_sha256: hash(await readFile('packages/deepviz/dist/renderers.js')), probe_sha256: hash(await readFile(new URL(import.meta.url)))});
});
after(async () => {await browser?.close();});

async function observe(stem, artifact, carrier) {
  const input = join(output, `${stem}.${carrier}`), content = carrier === 'svg' ? artifact.renderer_spec.spec.svg : artifact.html;
  await writeFile(input, content, {flag: 'wx'});
  const context = await browser.newContext({viewport: {width: 1100, height: 850}, deviceScaleFactor: 1, offline: true});
  try {
    const page = await context.newPage(), errors = [], requests = [];
    page.setDefaultTimeout(5000);
    page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
    page.on('pageerror', error => errors.push(String(error)));
    page.on('requestfailed', request => errors.push(`requestfailed: ${request.url()}`));
    page.on('request', request => {if (/^https?:/.test(request.url())) requests.push(request.url());});
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(pathToFileURL(input).href, {waitUntil: 'load'});
    if (carrier === 'html') await page.waitForFunction(() => globalThis.deepvizReady === true);
    await page.evaluate(() => document.fonts.ready);
    const geometry = await page.locator(carrier === 'html' ? '#chart-0 svg' : 'svg').evaluate(svg => {
      const origin = svg.getBoundingClientRect();
      const texts = [...svg.querySelectorAll('text')].map(text => {
        const box = text.getBBox(), matrix = text.getScreenCTM();
        const corners = [[box.x, box.y], [box.x + box.width, box.y], [box.x, box.y + box.height], [box.x + box.width, box.y + box.height]]
          .map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
        return {text: [...text.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(''),
          category: text.classList.contains('category-tick'), x: Math.min(...corners.map(p => p.x)) - origin.x,
          right: Math.max(...corners.map(p => p.x)) - origin.x, y: Math.min(...corners.map(p => p.y)) - origin.y,
          bottom: Math.max(...corners.map(p => p.y)) - origin.y, size: +getComputedStyle(text).fontSize.replace('px', '')};
      });
      const marks = [...svg.querySelectorAll('.mark')].map(mark => ({tag: mark.tagName,
        attrs: Object.fromEntries([...mark.attributes].map(a => [a.name, a.value])), title: mark.querySelector('title')?.textContent}));
      return {width: svg.viewBox.baseVal.width, height: svg.viewBox.baseVal.height, texts, marks};
    });
    const runtime = carrier === 'html' ? await page.evaluate(() => globalThis.deepvizErrors) : [];
    const png = await page.screenshot({fullPage: carrier === 'html'});
    await writeFile(join(output, `${stem}.png`), png, {flag: 'wx'});
    await save(`${stem}.json`, {geometry, errors, requests, runtime, input_sha256: hash(content), png_sha256: hash(png)});
    assert.deepEqual([errors, requests, runtime], [[], [], []]);
    for (const text of geometry.texts) {
      assert.ok(text.size >= 12 && text.x >= -0.05 && text.y >= -0.05 && text.right <= geometry.width + 0.05 && text.bottom <= geometry.height + 0.05,
        `text outside requested viewport: ${JSON.stringify(text)}`);
    }
    return geometry;
  } finally {await context.close();}
}

for (const kind of ['bar', 'line', 'area', 'scatter', 'bubble']) for (const carrier of ['svg', 'html']) {
  test(`R23 actual finite ${kind} ${carrier}: literal ±1e308 with finite quantitative geometry`, {timeout: 15000}, async () => {
    const rows = [{group: kind === 'bar' ? 'n' : 0, value: -1e308, size: 1}, {group: kind === 'bar' ? 'p' : 1, value: 1e308, size: 4}];
    const artifact = render(rows, {kind, x: 'group', y: 'value', aggregation: 'none', width: 240, height: 200,
      ...(kind === 'bubble' ? {size: 'size'} : {})}, 'svg');
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    assert.equal(artifact.input_count, 2);
    assert.equal(artifact.output_count, 2);
    const geometry = await observe(`finite-${kind}-${carrier}`, artifact, carrier);
    assert.equal(geometry.width, 240);
    assert.equal(geometry.height, 200);
    assert.deepEqual(geometry.texts.filter(text => text.category).map(text => text.text), kind === 'bar' ? ['n', 'p'] : ['0', '1']);
    assert.equal(geometry.marks.length, ['line', 'area'].includes(kind) ? 1 : 2);
    assert.ok(geometry.marks.every(mark => !/NaN|Infinity/.test(JSON.stringify(mark.attrs))));
    if (kind === 'bar') {
      assert.deepEqual(geometry.marks.map(mark => [+mark.attrs.y, +mark.attrs.height]), [[100, 35], [65, 35]]);
      assert.deepEqual(geometry.marks.map(mark => mark.title), ['n: -1e+308', 'p: 1e+308']);
    } else if (kind === 'line' || kind === 'area') {
      assert.equal(geometry.marks[0].attrs.points, kind === 'area' ? '120,100 120,135 175,65 175,100' : '120,135 175,65');
    } else {
      assert.deepEqual(geometry.marks.map(mark => [+mark.attrs.cx, +mark.attrs.cy, +mark.attrs.r]), kind === 'bubble' ? [[120, 135, 15], [175, 65, 30]] : [[120, 135, 4], [175, 65, 4]]);
    }
  });
}

for (const [fixture, width] of [['ordinary', 240], ['ordinary', 960], ['unicode', 960]]) for (const carrier of ['svg', 'html']) {
  test(`R23 actual ${fixture} eight ${width}px ${carrier}: full text readable with all values`, {timeout: 15000}, async () => {
    const rows = Array.from({length: 8}, (_, i) => ({group: fixture === 'ordinary' ? `g${i}` : `東京都東部支店${i + 1}`, value: i + 1}));
    const artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none', width,
      height: width === 240 ? 200 : 540}, 'svg');
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    assert.deepEqual([artifact.input_count, artifact.output_count], [8, 8]);
    const geometry = await observe(`density-${fixture}-${width}-${carrier}`, artifact, carrier);
    const ticks = geometry.texts.filter(text => text.category), other = geometry.texts.filter(text => !text.category);
    assert.deepEqual(ticks.map(text => text.text), rows.map(row => row.group));
    const overlaps = (a, b) => Math.min(a.right, b.right) - Math.max(a.x, b.x) > 0.05 && Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y) > 0.05;
    for (let i = 0; i < ticks.length; i++) {
      for (let j = i + 1; j < ticks.length; j++) assert.equal(overlaps(ticks[i], ticks[j]), false, `actual full label overlap: ${i},${j}`);
      for (const axis of other) assert.equal(overlaps(ticks[i], axis), false, 'category label overlaps numeric or axis-title text');
    }
    assert.equal(geometry.marks.length, 8);
    for (let i = 0; i < 8; i++) {
      const bar = geometry.marks[i];
      assert.equal(bar.title, `${rows[i].group}: ${rows[i].value}`);
      assert.ok(+bar.attrs.width > 0 && +bar.attrs.height > 0);
      assert.ok(Math.abs(+bar.attrs.height / +geometry.marks[0].attrs.height - (i + 1)) < 1e-9);
      assert.ok(Math.abs(+bar.attrs.y + +bar.attrs.height - (width === 240 ? 135 : 475)) < 1e-9);
    }
  });
}

test('R23 actual Unicode 240px density is a clear pre-artifact rejection, not a chart pass', () => {
  const rows = Array.from({length: 8}, (_, i) => ({group: `東京都東部支店${i + 1}`, value: i + 1}));
  let artifact;
  assert.throws(() => {artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none', width: 240, height: 200}, 'svg');},
    /category density cannot fit at requested dimensions.*larger dimensions/);
  assert.equal(artifact, undefined);
});
