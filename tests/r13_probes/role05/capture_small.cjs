// Inspect static companion HTML using already-rendered controls, with no CDN dependency.
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { createRequire } = require('node:module');
const requireDeps = createRequire(path.resolve(process.env.DEEPVIZ_NODE_DEPS_ROOT || '.', 'package.json'));
const { chromium } = requireDeps('playwright');

async function main() {
  const collection = path.resolve(process.argv[2]);
  const output = path.join(collection, 'browser');
  await fs.mkdir(output);
  const targets = JSON.parse(await fs.readFile(path.join(collection, 'browser-targets.json'), 'utf8'));
  const browser = await chromium.launch({ headless: true });
  const results = { chromium: browser.version(), controls: [] };
  try {
    for (const target of targets) {
      const page = await browser.newPage({ viewport: { width: 1100, height: 1000 }, deviceScaleFactor: 1 });
      const errors = [], externalRequests = [];
      page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
      page.on('pageerror', error => errors.push(String(error)));
      await page.route('**/*', route => {
        if (route.request().url().startsWith('file:')) return route.continue();
        externalRequests.push('nonlocal request');
        return route.abort();
      });
      await page.goto(pathToFileURL(target.html).href);
      await page.locator('img').waitFor();
      await page.locator('details').evaluateAll(items => items.forEach(item => { item.open = true; }));
      const visible = await page.locator('img').evaluate(image => image.complete && image.naturalWidth > 0);
      const tables = await page.locator('tbody').allTextContents();
      if (!visible || errors.length || externalRequests.length) throw new Error('Small static control failed');
      const expected = target.name === 'dashboard' ? 2 : 1;
      if (tables.length !== expected || tables.some(text => !text.includes('A3') || !text.includes('B7'))) {
        throw new Error('Small table values/count incorrect in actual browser');
      }
      await page.screenshot({ path: path.join(output, `${target.name}.png`), fullPage: true });
      results.controls.push({ name: target.name, visible, table_count: tables.length, errors, external_requests: externalRequests });
      await page.close();
    }
  } finally { await browser.close(); }
  await fs.writeFile(path.join(output, 'verified.json'), `${JSON.stringify(results, null, 2)}\n`);
  console.log(JSON.stringify(results, null, 2));
}
main().catch(error => { console.error(error); process.exitCode = 1; });
