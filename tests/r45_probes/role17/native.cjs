// Read-only observation of the actual unmodified public HTML and real G2 library.
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const {pathToFileURL} = require('node:url');
const {createHash} = require('node:crypto');
const assert = require('node:assert/strict');
const [html, tools, resultFile] = process.argv.slice(2);
const load = createRequire(path.join(path.resolve(tools), 'package.json'));
const asset = path.join(tools, 'node_modules/@antv/g2/dist/g2.min.js');
const sha = value => createHash('sha256').update(value).digest('hex');
const beforeHTML = sha(fs.readFileSync(html)), beforeAsset = sha(fs.readFileSync(asset));
assert.equal(beforeAsset, '7e7d346cab68c002a889dc6145bfc1f9ae1391be82ce8d514fb106ef3a6e6412');
async function main() {
  const {chromium} = load('playwright'), browser = await chromium.launch({headless: true});
  const result = {node: process.version, chromium: browser.version(), assetSHA256: beforeAsset,
    method: 'Exact existing G2 5.4.8 body locally fulfilled at unchanged pinned URL; NOT CDN-health. Constructor-return-only observation; no options, DOM, scale, library or paint mutation.', errors: [], requests: []};
  const page = await browser.newPage({viewport: {width: 1200, height: 900}, deviceScaleFactor: 1});
  page.on('console', message => {if (message.type() === 'error') result.errors.push({kind: 'console', message: message.text()});});
  page.on('pageerror', error => result.errors.push({kind: 'page', message: String(error)}));
  page.on('requestfailed', request => result.errors.push({kind: 'request', message: request.url() + ': ' + request.failure()?.errorText}));
  await page.route('https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js', async route => {
    result.requests.push({url: route.request().url(), locallyFulfilledSHA256: beforeAsset});
    await route.fulfill({path: asset, contentType: 'application/javascript'});
  });
  await page.addInitScript(() => {
    let realG2;
    window.__nativeCharts = [];
    Object.defineProperty(window, 'G2', {configurable: true, get: () => realG2, set: value => {
      realG2 = value;
      let constructor;
      Object.defineProperty(value, 'Chart', {configurable: true, enumerable: true, get: () => constructor, set: original => {
        constructor = new Proxy(original, {construct(target, args, newTarget) {
          const chart = Reflect.construct(target, args, newTarget); window.__nativeCharts.push(chart); return chart;
        }});
      }});
    }});
  });
  try {
    await page.goto(pathToFileURL(path.resolve(html)).href, {waitUntil: 'load'});
    result.ready = await page.evaluate(async () => Promise.race([
      window.deepvizReady.then(() => 'resolved', error => 'rejected: ' + error),
      new Promise(resolve => setTimeout(() => resolve('timeout'), 15000))]));
    result.state = await page.evaluate(() => {
      const chart = window.__nativeCharts[0], element = document.querySelector('[role="img"]');
      const canvas = element.querySelector('canvas'), ctx = canvas.getContext('2d');
      const context = chart.getContext(), root = context.canvas.document.documentElement;
      const color = document.createElement('canvas').getContext('2d');
      const describe = node => {
        const b = node.getBBox(); color.fillStyle = '#010203'; color.fillStyle = node.getAttribute('fill');
        return {text: node.getAttribute('text'), fill: node.getAttribute('fill'), normalizedColor: color.fillStyle,
          box: {x: b.x, y: b.y, width: b.width, height: b.height}};
      };
      const marks = [...root.querySelectorAll('.element')].map(describe);
      const legend = root.querySelector('.legend-continuous');
      const payloads = JSON.parse(document.getElementById('deepviz-data').textContent);
      const values = payloads[0].data.map(row => row._heat);
      const views = (context.views ?? []).map(view => ({layout: view.layout, color: {
        options: view.scale.color.getOptions(), map: values.map(value => view.scale.color.map(value)), ticks: view.scale.color.getTicks()}}));
      return {payloads, marks, views,
        width: canvas.width, height: canvas.height,
        ticks: legend ? [...legend.querySelectorAll('text')].map(describe) : [],
        pixels: marks.map(mark => [...ctx.getImageData(Math.round(mark.box.x + mark.box.width / 2), Math.round(mark.box.y + mark.box.height / 2), 1, 1).data])};
    });
  } catch (error) {result.harnessError = String(error.stack ?? error);}
  result.screenshot = resultFile.replace(/\.json$/, '.png');
  await page.screenshot({path: result.screenshot, fullPage: true});
  result.screenshotSHA256 = sha(fs.readFileSync(result.screenshot));
  await browser.close();
  assert.equal(sha(fs.readFileSync(html)), beforeHTML);
  assert.equal(sha(fs.readFileSync(asset)), beforeAsset);
  result.HTMLbeforeAfterSHA256 = beforeHTML;
  fs.writeFileSync(resultFile, JSON.stringify(result, (_key, value) => typeof value === 'number' && !Number.isFinite(value) ? {nonfinite: String(value)} : value, 2));
  console.log(JSON.stringify({ready: result.ready, marks: result.state?.marks.length, errors: result.errors.length, harness: result.harnessError}));
}
main().catch(error => {console.error(error); process.exitCode = 1;});
