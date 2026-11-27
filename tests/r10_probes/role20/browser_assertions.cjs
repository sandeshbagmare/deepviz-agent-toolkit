// Trusted test inspection only; input strings never become evaluated code.
const fs = require('node:fs/promises');
const path = require('node:path');
const {pathToFileURL} = require('node:url');

async function main() {
  const [requestPath, modules] = process.argv.slice(2);
  const request = JSON.parse(await fs.readFile(requestPath, 'utf8'));
  const {chromium} = require(path.join(modules, 'playwright'));
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1100, height: 850}, deviceScaleFactor: 1});
  const errors = [];
  const blocked = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.route('**/*', async route => {
    if (route.request().url() === pathToFileURL(request.html).href) await route.continue();
    else { blocked.push(route.request().url()); await route.abort('blockedbyclient'); }
  });
  try {
    await page.goto(pathToFileURL(request.html).href, {waitUntil: 'load', timeout: 45000});
    await page.evaluate(() => window.deepvizReady);
    const observed = await page.evaluate(({child_count, literal_strings, family}) => {
      const charts = Array.from({length: child_count}, (_, index) => {
        const graph = document.getElementById(`chart-${index}`);
        const text = [...graph.querySelectorAll('svg text')].map(node => node.textContent);
        const marks = [...graph.querySelectorAll(family === 'categorical'
          ? '.barlayer .point path' : '.scatterlayer .point')];
        return {
          x: graph.data[0].x, y: graph.data[0].y, text,
          anchors: [...graph.querySelectorAll('a')].map(node => node.outerHTML),
          handlers: [...graph.querySelectorAll('*')].flatMap(node => [...node.attributes]
            .filter(attr => /^on/i.test(attr.name)).map(attr => `${node.tagName}:${attr.name}=${attr.value}`)),
          missing_literal_strings: literal_strings.filter(value => !text.some(item => item.includes(value))),
          mark_count: marks.length,
          mark_centers: marks.map(mark => {
            const rect = mark.getBoundingClientRect();
            return {x: rect.x + rect.width / 2, y: rect.y + rect.height / 2};
          }),
        };
      });
      return {charts, table_cells: [...document.querySelectorAll('tbody td')].map(cell => cell.textContent),
        payload_json_bytes: new TextEncoder().encode(document.getElementById('deepviz-data').textContent).length};
    }, request);
    if (observed.payload_json_bytes > 50_000) throw new Error('Small native payload unexpectedly grew');
    await page.screenshot({path: request.screenshot, fullPage: true});
    await fs.writeFile(request.result, JSON.stringify({
      ...observed, errors, blocked, browser: browser.version(), node: process.version,
      playwright: require(path.join(modules, 'playwright/package.json')).version,
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error.stack); process.exitCode = 1; });
