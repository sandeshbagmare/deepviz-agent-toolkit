import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir, mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {join, resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {test} from 'node:test';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {render} from '../dist/index.js';

const outputRoot = process.env.DEEPVIZ_R52_OUTPUT ? resolve(process.env.DEEPVIZ_R52_OUTPUT) : tmpdir();
await mkdir(outputRoot, {recursive: true});
const output = await mkdtemp(join(outputRoot, 'run-'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const root = resolve('.');
const sourceBytes = await readFile(join(root, 'packages/deepviz/src/renderers.ts'));
const distPath = fileURLToPath(import.meta.resolve('../dist/renderers.js'));
const distBytes = await readFile(distPath);
const identity = {head: execFileSync('git', ['rev-parse', 'HEAD'], {encoding: 'utf8'}).trim(), node: process.version,
  source_sha256: hash(sourceBytes), dist_sha256: hash(distBytes),
  imported_file: fileURLToPath(import.meta.resolve('../dist/index.js')),
  probe_sha256: hash(await readFile(fileURLToPath(import.meta.url)))};

const rows = Array.from({length: 40}, (_, i) => ({category: `Common long category name ${i}`, value: i + 1}));
const artifact = render(rows, {kind: 'bar', x: 'category', y: 'value', aggregation: 'none', width: 240, height: 200,
  title: 'R52 dense category boxes'}, 'svg');

for (const carrier of ['svg', 'html']) test(`R52 ${carrier} keeps dense category label boxes separate`, async () => {
  const browser = await chromium.launch({headless: true});
  try {
    const browserVersion = browser.version();
    const page = await browser.newPage({viewport: {width: 800, height: 700}, deviceScaleFactor: 1});
    const errors = [];
    page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
    page.on('pageerror', error => errors.push(String(error)));
    page.on('request', request => {if (/^https?:/.test(request.url())) errors.push(request.url());});
    page.on('requestfailed', request => errors.push(request.url()));
    const content = carrier === 'svg' ? artifact.renderer_spec.spec.svg : artifact.html;
    await page.setContent(content, {waitUntil: 'load'});
    if (carrier === 'html') await page.waitForFunction(() => globalThis.deepvizReady === true);
    const result = await page.locator(carrier === 'html' ? '#chart-0 svg' : 'svg').evaluate(svg => {
      const origin = svg.getBoundingClientRect();
      const categories = [...svg.querySelectorAll('text.category-tick')].map(text => {
        const rect = text.getBoundingClientRect();
        return {label: [...text.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(''),
          title: text.querySelector('title')?.textContent, left: rect.left - origin.left, right: rect.right - origin.left,
          top: rect.top - origin.top, bottom: rect.bottom - origin.top};
      });
      const bars = [...svg.querySelectorAll('rect.mark')].map(bar => ({title: bar.querySelector('title')?.textContent,
        x: Number(bar.getAttribute('x')), y: Number(bar.getAttribute('y')), width: Number(bar.getAttribute('width')),
        height: Number(bar.getAttribute('height'))}));
      return {viewBox: svg.getAttribute('viewBox'), categories, bars};
    });
    const png = await page.screenshot({fullPage: true});
    const stem = `dense-categories-${carrier}`;
    await writeFile(join(output, `${stem}.png`), png, {flag: 'wx'});
    await writeFile(join(output, `${stem}.json`), JSON.stringify({carrier, identity: {...identity, chromium: browserVersion},
      source_html_sha256: hash(Buffer.from(content)), png_sha256: hash(png), result, errors}, null, 2), {flag: 'wx'});
    assert.deepEqual(errors, []);
    assert.equal(result.viewBox, '0 0 240 200');
    assert.ok(result.categories.length >= 5 && result.categories.length <= 15);
    assert.equal(new Set(result.categories.map(item => item.label)).size, result.categories.length);
    assert.ok(result.categories.every(item => item.label.includes('…')));
    for (const item of result.categories) {
      assert.ok(item.left >= -0.1 && item.top >= -0.1 && item.right <= 240.1 && item.bottom <= 200.1,
        `clipped category label ${item.title}: ${JSON.stringify(item)}`);
    }
    assert.deepEqual(result.bars.map(bar => bar.title), rows.map(row => `${row.category}: ${row.value}`));
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    assert.equal(artifact.input_count, rows.length);
    assert.equal(artifact.output_count, rows.length);
    for (let i = 0; i < result.categories.length; i++) for (let j = i + 1; j < result.categories.length; j++) {
      const a = result.categories[i], b = result.categories[j];
      assert.ok(Math.min(a.right, b.right) <= Math.max(a.left, b.left) + 0.1 ||
        Math.min(a.bottom, b.bottom) <= Math.max(a.top, b.top) + 0.1,
      `category boxes overlap for ${a.title} (${a.label}) and ${b.title} (${b.label})`);
    }
  } finally { await browser.close(); }
});

console.log(`R52 browser evidence: ${output}`);
