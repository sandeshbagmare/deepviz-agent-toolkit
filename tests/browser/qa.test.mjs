import assert from 'node:assert/strict';
import { createHash, randomUUID } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
import { analyzeRaster, cdnEntries, loadCdnAssets, validateCoverage, validateManifest } from './qa.mjs';

const commit = 'a'.repeat(40);
const chart = (id, engine = 'plotly', extra = {}) => ({
  id, engine, format: 'html', path: `${id}.html`, title: 'QA revenue',
  labels: ['North', 'South'], numbers: ['0', '10'],
  regions: [{ selector: '#chart', minMarks: 3 }], ...extra,
});

test('manifest rejects path traversal and duplicate case IDs', () => {
  assert.throws(() => validateManifest({ version: 1, sourceCommit: commit,
    cases: [chart('safe', 'plotly', { path: '../private.html' })] }), /relative artifact path/);
  assert.throws(() => validateManifest({ version: 1, sourceCommit: commit,
    cases: [chart('safe'), chart('safe')] }), /duplicate/i);
});

test('manifest requires real source provenance, visible regions, and numeric expectations', () => {
  for (const sourceCommit of ['HEAD', 'pending', 'a'.repeat(7)]) {
    assert.throws(() => validateManifest({ version: 1, sourceCommit, cases: [chart('safe')] }), /sourceCommit/);
  }
  for (const extra of [{ regions: [] }, { numbers: [] }, { numbers: ['0', '0'] }, { numbers: ['not numeric'] },
    { dashboard: true, regions: [{ selector: '#same' }, { selector: '#same' }] }]) {
    assert.throws(() => validateManifest({ version: 1, sourceCommit: commit,
      cases: [chart('safe', 'plotly', extra)] }));
  }
  assert.equal(validateManifest({ version: 1, sourceCommit: commit,
    cases: [chart('safe')] }).cases.length, 1);
});

test('acceptance cannot silently omit a renderer, security case, dashboard panel, or static engine', () => {
  const cases = ['plotly', 'echarts', 'antv'].flatMap(engine => [
    chart(`${engine}-bar`, engine), chart(`${engine}-unsafe`, engine, { security: true }),
  ]);
  cases.push(chart('dashboard', 'plotly', { dashboard: true,
    regions: [{ selector: '#a' }, { selector: '#b' }] }));
  cases.push(chart('dashboard-unsafe', 'plotly', { dashboard: true, security: true,
    regions: [{ selector: '#a' }, { selector: '#b' }] }));
  for (const engine of ['vega', 'matplotlib']) cases.push({ id: engine, engine,
    format: 'svg', path: `${engine}.svg`, title: 'QA revenue' });
  assert.doesNotThrow(() => validateCoverage(cases));
  for (const missing of ['echarts-bar', 'antv-unsafe', 'dashboard', 'dashboard-unsafe', 'vega', 'matplotlib']) {
    assert.throws(() => validateCoverage(cases.filter(item => item.id !== missing)), /coverage/i);
  }
  assert.throws(() => validateManifest({ version: 1, sourceCommit: commit,
    cases: [chart('dashboard', 'plotly', { dashboard: true })] }), /two regions/);
});

test('CDN routes accept exact installed semver only, never major aliases or arbitrary URLs', () => {
  const entries = cdnEntries('@antv/g2', '5.4.5', '/local/g2.min.js', 'dist/g2.min.js');
  assert.ok(entries.some(item => item.url === 'https://cdn.jsdelivr.net/npm/@antv/g2@5.4.5/dist/g2.min.js'));
  assert.ok(entries.every(item => item.url.includes('@5.4.5/')));
  assert.ok(!entries.some(item => item.url.includes('@5/')));
  assert.throws(() => cdnEntries('echarts', '5', '/local/e.js', 'dist/echarts.min.js'), /exact semver/);
  const plotly = cdnEntries('plotly.js-dist-min', '3.1.0', '/local/p.js', 'plotly.min.js');
  assert.ok(plotly.some(item => item.url === 'https://cdn.plot.ly/plotly-3.1.0.min.js'));
});

test('raster checks distinguish colored marks from white or monochrome output', async () => {
  const white = Array(32 * 32 * 4).fill(255);
  const blank = await analyzeRaster({ rgba: white, width: 32, height: 32 });
  assert.equal(blank.coloredPixels, 0);
  assert.equal(blank.inkPixels, 0);
  const colored = [...white];
  for (let i = 0; i < colored.length; i += 4) {
    colored[i] = i % 256;
    colored[i + 1] = 80;
    colored[i + 2] = 160;
  }
  const marks = await analyzeRaster({ rgba: colored, width: 32, height: 32 });
  assert.ok(marks.coloredPixels > 800);
  assert.ok(marks.colorBuckets >= 4);
  assert.ok(marks.activeTiles >= 6);
});

test('regression comparison measures pixels, catches blanking, and rejects dimension drift', async () => {
  const white = Array(16 * 16 * 4).fill(255);
  const black = white.map((value, index) => index % 4 === 3 ? value : 0);
  const exact = await analyzeRaster({ rgba: black, width: 16, height: 16,
    baselineRgba: black, baselineWidth: 16, baselineHeight: 16 });
  assert.equal(exact.diffRatio, 0);
  const regression = await analyzeRaster({ rgba: white, width: 16, height: 16,
    baselineRgba: black, baselineWidth: 16, baselineHeight: 16 });
  assert.equal(regression.diffRatio, 1);
  const resized = await analyzeRaster({ rgba: white, width: 16, height: 16,
    baselineRgba: white, baselineWidth: 32, baselineHeight: 8 });
  assert.equal(resized.dimensionsMatch, false);
});

test('thin colored font fringes cannot stand in for solid chart marks', async () => {
  const rgba = Array(32 * 32 * 4).fill(255);
  for (let y = 0; y < 32; y += 4) for (let x = 0; x < 32; x++) {
    const offset = (y * 32 + x) * 4;
    rgba[offset] = 30;
    rgba[offset + 1] = 80;
    rgba[offset + 2] = 160;
  }
  const fringes = await analyzeRaster({ rgba, width: 32, height: 32 });
  assert.ok(fringes.coloredPixels > 150);
  assert.equal(fringes.solidColoredPixels, 0);
  for (let y = 5; y < 25; y++) for (let x = 5; x < 25; x++) {
    const offset = (y * 32 + x) * 4;
    rgba[offset] = 30;
    rgba[offset + 1] = 80;
    rgba[offset + 2] = 160;
  }
  const marks = await analyzeRaster({ rgba, width: 32, height: 32 });
  assert.ok(marks.solidColoredPixels > 300);
});

test('asset loader takes version and JS bytes from resolved local packages, including scoped packages', async () => {
  const root = path.resolve(`tests/browser/results/asset-loader-${randomUUID()}`);
  const definitions = [
    ['plotly.js-dist-min', 'plotly.min.js'], ['echarts', 'dist/echarts.min.js'],
    ['@antv/g2', 'dist/g2.min.js'], ['vega', 'build/vega.min.js'],
    ['vega-lite', 'build/vega-lite.min.js'], ['vega-embed', 'build/vega-embed.min.js'],
  ];
  for (const [name, asset] of definitions) {
    const packageDir = path.join(root, 'node_modules', name);
    await mkdir(path.dirname(path.join(packageDir, asset)), { recursive: true });
    await writeFile(path.join(packageDir, 'package.json'), JSON.stringify({ name, version: '1.2.3', main: asset }));
    await writeFile(path.join(packageDir, asset), `/* synthetic test package ${name} */`);
  }
  const assets = await loadCdnAssets(root);
  assert.equal(assets.size, 13);
  for (const [url, asset] of assets) {
    assert.equal(asset.version, '1.2.3');
    assert.ok(url.includes('@1.2.3/') || url.includes('plotly-1.2.3.min.js'));
    assert.equal(asset.body.toString(), `/* synthetic test package ${asset.name} */`);
    assert.equal(asset.sha256, createHash('sha256').update(asset.body).digest('hex'));
  }
});

test('a long thin diagonal chart line is meaningful even without filled interiors', async () => {
  const width = 256;
  const rgba = Array(width * width * 4).fill(255);
  for (let x = 10; x < 240; x++) for (let offsetY = 0; offsetY < 2; offsetY++) {
    const offset = ((x + offsetY) * width + x) * 4;
    rgba[offset] = 30;
    rgba[offset + 1] = 80;
    rgba[offset + 2] = 160;
  }
  const line = await analyzeRaster({ rgba, width, height: width });
  assert.ok(line.solidColoredPixels < 150);
  assert.ok(line.largestColoredComponentPixels > 400);
  assert.ok(line.largestColoredComponentSpan > 0.8);
});
