// Synthetic controls test the tester, never product acceptance or engine rendering.
import assert from 'node:assert/strict';
import { randomUUID, createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { CANARY, PAYLOAD, cdnEntries, playwrightFrom, runArtifactSuite } from './qa.mjs';

const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  assert.ok(['--deps', '--output'].includes(process.argv[i]) && process.argv[i + 1], 'Use --deps <npm-root> [--output <new-dir>]');
  options[process.argv[i].slice(2)] = process.argv[i + 1];
}
const root = path.resolve(options.output ?? `tests/browser/results/selftest-${randomUUID()}`);
await mkdir(path.dirname(root), { recursive: true });
await mkdir(root);
const baselineDir = path.join(root, 'baselines');
const { chromium, version } = playwrightFrom(options.deps ?? '.');
const browser = await chromium.launch({ headless: true, args: ['--disable-background-networking'] });
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="700" height="420" viewBox="0 0 700 420">
<rect width="700" height="420" fill="white"/><text x="40" y="28">QA revenue</text>
<text x="40" y="390">North</text><text x="230" y="390">South</text>
<text x="10" y="365">0</text><text x="5" y="240">10</text>
<rect x="40" y="210" width="140" height="150" fill="#2466b0"/>
<rect x="230" y="100" width="140" height="260" fill="#2466b0"/>
<rect x="420" y="50" width="140" height="310" fill="#2466b0"/></svg>`;
const safePayload = JSON.stringify(PAYLOAD).replaceAll('<', '\\u003c');
const healthy = `<html><head><style>body{margin:0;background:white}#chart{width:700px;height:420px}</style></head>
<body><div id="chart">${svg}</div><script>const hostileData=${safePayload};</script></body></html>`;
const item = { id: 'control', engine: 'plotly', format: 'html', path: 'control.html', title: 'QA revenue',
  labels: ['North', 'South'], numbers: ['0', '10'], regions: [{ selector: '#chart', minMarks: 3 }], security: true };
const assets = new Map();
const cases = [];
let counter = 0;

async function run(html, { record = false, entry = item, expectation } = {}) {
  await writeFile(path.join(root, entry.path), html);
  const report = await runArtifactSuite({ manifest: { version: 1, sourceCommit: '0'.repeat(40), cases: [entry] },
    artifactRoot: root, browser, playwrightVersion: version, assets, baselineDir,
    outputDir: path.join(root, `run-${++counter}`), record, selfTest: true });
  const result = report.cases[0];
  if (expectation) {
    assert.equal(result.status, 'failed', JSON.stringify(result));
    assert.match(result.errors.join('\n'), expectation);
  } else assert.equal(result.status, record ? 'recorded-not-accepted' : 'passed', JSON.stringify(result));
  return result;
}

try {
  await run(healthy, { record: true });
  const exact = await run(healthy);
  assert.equal(exact.regression.diffRatio, 0);
  cases.push('SVG marks / visible title, labels, numbers / single-accent raster / exact baseline');
  await run(healthy.replaceAll('#2466b0', '#bd315b'), { expectation: /visual regression exceeds/i });
  cases.push('changed-color pixel regression rejected');
  await run(healthy.replace('y="210" width="140" height="150"', 'y="200" width="140" height="160"'),
    { expectation: /Region 0 visual regression exceeds/ });
  cases.push('small bar-height regression rejected within chart crop, not diluted by page whitespace');
  await run(healthy.replaceAll('#2466b0', 'white'), { expectation: /meaningful colored chart marks/ });
  cases.push('blank marks rejected despite unchanged title, axes, and real SVG');
  await run(healthy.replace('>10</text>', '>11</text>'), { expectation: /Missing drawn numeric axis label/ });
  await run(healthy.replace('>QA revenue<', '>Wrong title<'), { expectation: /Missing visible title/ });
  cases.push('missing title and incorrect numeric axis labels rejected');
  const thrown = await run(healthy.replace('</body>', '<script>throw new Error("QA_EXCEPTION")</script></body>'),
    { expectation: /Uncaught page exceptions/ });
  assert.deepEqual(thrown.pageErrors, ['QA_EXCEPTION']);
  const logged = await run(healthy.replace('</body>', '<script>console.error("QA_CONSOLE")</script></body>'),
    { expectation: /Browser console errors/ });
  assert.deepEqual(logged.consoleErrors, ['QA_CONSOLE']);
  cases.push('uncaught exceptions and console errors rejected');
  const injected = await run(`${healthy}${PAYLOAD}`, { expectation: /Hostile data executed a script/ });
  assert.ok(injected.unexpectedRequests.some(url => url.includes(CANARY)));
  cases.push('script breakout / injected DOM and outbound image blocked and rejected');
  const unexpected = await run(`${healthy}<script>fetch('https://qa.invalid/outbound').catch(()=>{})</script>`,
    { expectation: /Browser console errors|Unexpected requests/ });
  assert.ok(unexpected.unexpectedRequests.some(url => url.includes('qa.invalid/outbound')));
  const unpinned = await run(`${healthy}<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>`,
    { expectation: /Browser console errors|Unexpected requests/ });
  assert.ok(unpinned.unexpectedRequests.some(url => url.includes('echarts@5/')));
  cases.push('outbound fetch and unpinned CDN blocked and rejected');
  const ws = await run(`${healthy}<script>new WebSocket('wss://qa.invalid/socket')</script>`,
    { expectation: /Unexpected requests|Browser console errors/ });
  assert.ok(ws.unexpectedRequests.some(url => url.includes('WebSocket')));
  cases.push('outbound WebSocket blocked and rejected');
  const body = Buffer.from('globalThis.__qa_local_asset=32635;');
  for (const asset of cdnEntries('echarts', '5.6.0', 'synthetic-local.js', 'dist/echarts.min.js')) assets.set(asset.url,
    { ...asset, body, sha256: createHash('sha256').update(body).digest('hex') });
  const pinnedHtml = healthy.replace('<body>', `<body><script src="https://cdn.jsdelivr.net/npm/echarts@5.6.0/dist/echarts.min.js"></script>
<script>if(globalThis.__qa_local_asset!==32635)throw new Error('Local asset substitution failed')</script>`);
  const routed = await run(pinnedHtml);
  assert.equal(routed.fulfilledAssets.length, 1);
  assert.equal(routed.fulfilledAssets[0].version, '5.6.0');
  cases.push('exact pinned CDN fulfilled locally with context offline and no network');
  const canvas = healthy.replace(`<div id="chart">${svg}</div>`, `<div id="chart"><canvas width="700" height="420"></canvas></div>
<script>const context=document.querySelector('canvas').getContext('2d');
context.fillStyle='white';context.fillRect(0,0,700,420);context.fillStyle='#2466b0';
context.fillRect(40,210,140,150);context.fillRect(230,100,140,260);context.fillRect(420,50,140,310);
context.fillStyle='black';context.font='16px Arial';context.fillText('QA revenue',40,28);
context.fillText('North',40,390);context.fillText('South',230,390);context.fillText('0',10,365);context.fillText('10',5,240);</script>`);
  await run(canvas, { record: true, entry: { ...item, id: 'canvas-control' } });
  const canvasResult = await run(canvas, { entry: { ...item, id: 'canvas-control' } });
  assert.equal(canvasResult.regions[0].canvases, 1);
  assert.ok(canvasResult.drawnNumbers.includes('10'));
  cases.push('canvas marks and fillText numeric/title instrumentation verified');
  const lineCanvas = canvas.replace('context.fillRect(40,210,140,150);context.fillRect(230,100,140,260);context.fillRect(420,50,140,310);',
    "context.strokeStyle='#2466b0';context.lineWidth=2;context.beginPath();context.moveTo(40,330);context.lineTo(230,250);context.lineTo(560,60);context.stroke();");
  await run(lineCanvas, { record: true, entry: { ...item, id: 'line-control' } });
  const lineResult = await run(lineCanvas, { entry: { ...item, id: 'line-control' } });
  assert.ok(lineResult.regions[0].largestColoredComponentPixels > 150);
  cases.push('legitimate thin diagonal canvas line is accepted without mistaking text fringes for a chart');
  const quoteAttribute = value => value.replaceAll('&', '&amp;').replaceAll('"', '&quot;');
  const dashboard = `<html><body style="margin:0"><h1>QA dashboard</h1>
<iframe id="first" style="display:block;width:720px;height:440px" srcdoc="${quoteAttribute(healthy)}"></iframe>
<iframe id="second" style="display:block;width:720px;height:440px" srcdoc="${quoteAttribute(healthy)}"></iframe></body></html>`;
  const dashboardEntry = { ...item, id: 'dashboard-control', dashboard: true, title: 'QA dashboard',
    regions: [{ frame: '#first', selector: '#chart' }, { frame: '#second', selector: '#chart' }] };
  await run(dashboard, { record: true, entry: dashboardEntry });
  const dashboardResult = await run(dashboard, { entry: dashboardEntry });
  assert.equal(dashboardResult.regions.length, 2);
  await run(dashboard.replace(quoteAttribute(healthy), quoteAttribute(healthy.replaceAll('#2466b0', 'white'))),
    { entry: dashboardEntry, expectation: /meaningful colored chart marks/ });
  cases.push('iframe dashboard title/numbers and independent nonempty panel checks verified');
  const staticEntry = { id: 'static-svg', engine: 'matplotlib', format: 'svg', path: 'control.svg', title: 'QA revenue' };
  await run(svg, { record: true, entry: staticEntry });
  await run(svg, { entry: staticEntry });
  const png = await readFile(path.join(root, `run-${counter}`, 'static-svg-region-0.png'));
  const pngEntry = { ...staticEntry, id: 'static-png', format: 'png', path: 'control.png' };
  await run(png, { record: true, entry: pngEntry });
  await run(png, { entry: pngEntry });
  cases.push('actual SVG and PNG raster decoding / baseline comparison verified (synthetic, not engine output)');
  const missing = await run(healthy, { entry: { ...item, id: 'missing-baseline' }, expectation: /ENOENT/ });
  assert.equal(missing.status, 'failed');
  cases.push('missing baseline fails closed');
  console.log(JSON.stringify({ status: 'HARNESS SELF-TEST ONLY; NOT PRODUCT ACCEPTANCE',
    passedControls: cases.length, cases, evidence: root }, null, 2));
  await writeFile(path.join(root, 'selftest.json'), JSON.stringify({ cases, environment: { playwright: version,
    chromium: browser.version(), node: process.version }, synthetic: true }, null, 2));
} finally { await browser.close(); }
