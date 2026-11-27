const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const crypto = require('node:crypto');

async function main() {
  const [root, libraries] = process.argv.slice(2);
  const {chromium} = require(path.join(libraries, 'node_modules/playwright'));
  const report = JSON.parse(await fs.readFile(path.join(root, 'generation.json'), 'utf8'));
  const assets = {};
  for (const [url, file] of [
    ['https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js', 'echarts/dist/echarts.min.js'],
    ['https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js', '@antv/g2/dist/g2.min.js'],
  ]) assets[url] = await fs.readFile(path.join(libraries, 'node_modules', file));
  const browser = await chromium.launch({headless: true});
  const results = [];
  try {
    for (const item of report.cases) {
      const page = await browser.newPage({viewport: {width: 1000, height: 800}, deviceScaleFactor: 1});
      const errors = [], blocked = [];
      page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
      page.on('pageerror', error => errors.push(error.message));
      await page.route('**/*', route => {
        const url = route.request().url();
        if (url.startsWith('file:')) return route.continue();
        if (assets[url]) return route.fulfill({status: 200, contentType: 'application/javascript', body: assets[url]});
        blocked.push(url);
        return route.abort('blockedbyclient');
      });
      await page.goto(pathToFileURL(item.html).href, {waitUntil: 'load'});
      if (['plotly', 'echarts', 'antv'].includes(item.engine)) {
        await page.evaluate(async () => {await window.deepvizReady;});
      }
      await page.evaluate(async () => {await document.fonts.ready;});
      const observed = await page.evaluate(engine => {
        const chart = document.getElementById('chart-0');
        const details = document.querySelector('details');
        const svgText = [...(chart || document).querySelectorAll('svg text')].map(node => node.textContent);
        const images = [...document.images].map(image => ({width: image.naturalWidth, height: image.naturalHeight}));
        if (details) details.open = true;
        return {headings: [...document.querySelectorAll('thead th')].map(node => node.textContent),
          rows: [...document.querySelectorAll('tbody tr')].map(row => [...row.cells].map(cell => cell.textContent)),
          svgText, images, svg: chart?.querySelectorAll('svg').length || 0,
          canvas: chart?.querySelectorAll('canvas').length || 0,
          renderError: document.body.dataset.renderError || null};
      }, item.engine);
      assert.deepEqual(observed.headings, ['label', 'value']);
      assert.deepEqual(observed.rows, [['A', '3'], ['B', '7']]);
      assert.equal(observed.renderError, null);
      if (['matplotlib', 'vega'].includes(item.engine)) {
        assert.equal(observed.images.length, 1);
        assert(observed.images.every(image => image.width > 0 && image.height > 0));
      } else {
        assert(observed.svg + observed.canvas > 0);
        if (item.engine !== 'antv') {
          for (const text of ['label', 'value', 'A', 'B', '3', '7']) assert(observed.svgText.includes(text), text);
        }
      }
      assert.deepEqual(errors, []);
      assert.deepEqual(blocked, []);
      const screenshot = path.join(root, `${item.engine}-normal.png`);
      await page.screenshot({path: screenshot, fullPage: true});
      const bytes = await fs.readFile(screenshot);
      results.push({engine: item.engine, status: 'PASS', observed, errors, blocked, screenshot,
        sha256: crypto.createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length});
      await page.close();
    }
    const output = {browser: browser.version(), node: process.version,
      resource_mode: 'Exact generated pinned CDN URLs fulfilled by installed local asset bytes; all other network denied',
      assets: Object.entries(assets).map(([url, bytes]) => ({url, sha256: crypto.createHash('sha256').update(bytes).digest('hex')})),
      results, limits: 'Five small normal table outputs only; images require actual inspection, no CDN-health/all-kind/final acceptance claim'};
    await fs.writeFile(path.join(root, 'browser.json'), JSON.stringify(output, null, 2));
    console.log(JSON.stringify({captured: results.length, errors: 0, results: results.map(({engine, status}) => ({engine, status}))}));
  } finally {await browser.close();}
}
main().catch(error => {console.error(error.stack); process.exitCode = 1;});
