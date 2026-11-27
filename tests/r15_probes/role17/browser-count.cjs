// Two real Plotly SVG charts: strict baseline failure plus explicit-y control.
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require('playwright');
const root = path.resolve(process.argv[2] || '');
const output = path.resolve(process.argv[3] || '');
const summary = JSON.parse(fs.readFileSync(path.join(root, 'summary.json'), 'utf8'));
const expected = [2, 3, 1]; // Caller multiplicities, never inferred from chart data.
fs.mkdirSync(output, { recursive: false });

(async () => {
  const server = http.createServer((request, response) => {
    if (request.url === '/favicon.ico') { response.writeHead(204); response.end(); return; }
    const filename = path.resolve(root, '.' + decodeURIComponent(new URL(request.url, 'http://localhost').pathname));
    if (!filename.startsWith(root + path.sep)) { response.writeHead(403); response.end(); return; }
    try { response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); response.end(fs.readFileSync(filename)); }
    catch { response.writeHead(404); response.end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await chromium.launch({ channel: process.platform === 'win32' ? 'msedge' : undefined, headless: true });
    const origin = `http://127.0.0.1:${server.address().port}`;
    const results = [];
    for (const name of ['plotly', 'plotly-explicit-y-control']) {
      const page = await browser.newPage({ viewport: { width: 1080, height: 800 } });
      const errors = [], warnings = [], pageErrors = [], failedRequests = [], externalRequests = [];
      page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); if (message.type() === 'warning') warnings.push(message.text()); });
      page.on('pageerror', error => pageErrors.push(error.message));
      page.on('requestfailed', request => failedRequests.push(request.url()));
      page.on('request', request => { if (!request.url().startsWith(origin)) externalRequests.push(request.url()); });
      const response = await page.goto(origin + '/' + summary.artifacts[name].files.html, { waitUntil: 'load' });
      await page.waitForFunction(() => document.querySelectorAll('.barlayer .point path').length === 3);
      const state = await page.evaluate(wanted => {
        const chart = document.querySelector('.js-plotly-plot');
        const axis = chart._fullLayout.yaxis;
        const baseline = axis.l2p(0);
        const marks = [...chart.querySelectorAll('.barlayer .point path')].map((node, index) => ({
          path: node.getAttribute('d'), y: node.getBBox().y, height: node.getBBox().height,
          expectedTopFromLiteralCount: axis.l2p(wanted[index]),
          expectedHeightFromLiteralCount: Math.abs(baseline - axis.l2p(wanted[index])),
        }));
        return { values: chart.data.flatMap(trace => trace.y), groups: chart.data.flatMap(trace => trace.x),
          svgCount: chart.querySelectorAll('svg.main-svg').length, marks, baseline,
          normalizedTableCells: [...document.querySelectorAll('table tbody td')].map(node => node.textContent),
          ready: true };
      }, expected);
      const valuesCorrect = JSON.stringify(state.values) === JSON.stringify(expected);
      const geometryCorrect = state.marks.length === 3 && state.marks.every(mark =>
        Math.abs(mark.height - mark.expectedHeightFromLiteralCount) < 0.1 && Math.abs(mark.y - mark.expectedTopFromLiteralCount) < 0.1);
      fs.writeFileSync(path.join(output, `${name}-preinteraction.json`), JSON.stringify({ state, errors, warnings, pageErrors, failedRequests, externalRequests }, null, 2));
      const box = await page.locator('.barlayer .point path').first().boundingBox();
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.waitForSelector('.hoverlayer .hovertext');
      const hoverText = await page.locator('.hoverlayer').textContent();
      await page.mouse.move(1040, 760);
      await page.screenshot({ path: path.join(output, `${name}.png`), fullPage: true });
      const svg = await page.locator('svg.main-svg').first().evaluate(node => node.outerHTML);
      fs.writeFileSync(path.join(output, `${name}.svg`), svg);
      const infrastructureCorrect = response.status() === 200 && state.svgCount > 0 && !errors.length && !pageErrors.length
        && !failedRequests.length && !externalRequests.length && hoverText.length > 0;
      results.push({ name, status: response.status(), expectedCounts: expected, valuesCorrect, geometryCorrect,
        infrastructureCorrect, strictPass: infrastructureCorrect && valuesCorrect && geometryCorrect,
        hoverText, errors, warnings, pageErrors, failedRequests, externalRequests, state });
      fs.writeFileSync(path.join(output, 'browser-partial.json'), JSON.stringify(results, null, 2));
      await page.close();
    }
    const result = { source_sha: summary.source_sha, node: process.version, playwright: require('playwright/package.json').version,
      browser: browser.version(), actualEngine: 'Plotly bundled self-contained JavaScript; genuine interactive SVG; no fallback',
      favicon: 'Harness-only HTTP204', results };
    fs.writeFileSync(path.join(output, 'browser-results.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify({ navigations: results.length, strictPasses: results.filter(result => result.strictPass).length,
      infrastructurePasses: results.filter(result => result.infrastructureCorrect).length,
      consoleErrors: results.reduce((total, result) => total + result.errors.length, 0) }));
    if (results.some(result => !result.strictPass)) process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
