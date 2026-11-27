import {readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const root = path.resolve(process.argv[2]);
const fixtures = JSON.parse(await readFile(path.join(root, 'cases.json'), 'utf8'));
if (process.argv[3]) fixtures.unshift({id: 'original-real-render-unobserved', html: path.resolve(process.argv[3]), production_equivalent: true});
const browser = await chromium.launch({headless: true});
const rows = [];
try {
  for (const fixture of fixtures) {
    const page = await browser.newPage({viewport: {width: 1100, height: 850}});
    const errors = [], network = [];
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('pageerror', error => errors.push(String(error)));
    page.on('requestfailed', request => network.push({url: request.url(), failure: request.failure()?.errorText}));
    page.on('response', response => { if (response.url().startsWith('https://')) network.push({url: response.url(), status: response.status()}); });
    await page.goto(pathToFileURL(path.resolve(root, fixture.html)).href, {waitUntil: 'load', timeout: 60000});
    const readiness = await page.evaluate(async () => {
      try { await window.deepvizReady; return {status: 'resolved'}; }
      catch (error) { return {status: 'rejected', error: String(error)}; }
    });
    const canvasSamples = await page.evaluate(() => {
      const canvas = document.querySelector('#chart-0 canvas');
      if (!canvas) return null;
      const context = canvas.getContext('2d');
      return [[0.25, 0.3], [0.75, 0.7]].map(([x, y]) => ({x: x * canvas.width, y: y * canvas.height,
        rgba: [...context.getImageData(x * canvas.width, y * canvas.height, 1, 1).data]}));
    });
    await page.screenshot({path: path.join(root, `${fixture.id}.png`), fullPage: true});
    rows.push({...fixture, readiness, errors, network, canvasSamples, chromium: browser.version(), observer: 'none'});
    await page.close();
  }
} finally { await browser.close(); }
await writeFile(path.join(root, 'diagnostic.json'), JSON.stringify(rows, null, 2));
console.log(JSON.stringify(rows.map(({id, readiness, errors, canvasSamples, production_equivalent}) => ({id, readiness, errors, canvasSamples, production_equivalent})), null, 2));
process.exitCode = rows.some(row => row.production_equivalent && (row.readiness.status !== 'resolved' || row.errors.length)) ? 1 : 0;
