// Only trusted inspection code runs; dataset strings are never evaluated.
const fs = require('node:fs/promises');
const path = require('node:path');
const {pathToFileURL} = require('node:url');

async function run() {
  const [input, modules] = process.argv.slice(2);
  const request = JSON.parse(await fs.readFile(input, 'utf8'));
  const {chromium} = require(path.join(modules, 'playwright'));
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1100, height: 900}, deviceScaleFactor: 1});
  const errors = [];
  const blocked = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.route('**/*', async route => {
    if (route.request().url() === pathToFileURL(request.html).href) await route.continue();
    else { blocked.push(route.request().url()); await route.abort('blockedbyclient'); }
  });
  const snapshot = () => page.evaluate(() => {
    const graph = document.getElementById('chart-0');
    const texts = selector => [...graph.querySelectorAll(selector)].map(node => node.textContent);
    return {
      x: graph.data[0].x, y: graph.data[0].y, trace_name: graph.data[0].name,
      trace_text: graph.data[0].text,
      legend_text: texts('.legendtext'), native_title: texts('.gtitle'),
      hover_text: texts('.hoverlayer text'),
      anchors: [...graph.querySelectorAll('svg a')].map(node => node.outerHTML),
      handlers: [...graph.querySelectorAll('*')].flatMap(node => [...node.attributes]
        .filter(attr => /^on/i.test(attr.name)).map(attr => `${node.tagName}:${attr.name}=${attr.value}`)),
      mark_centers: [...graph.querySelectorAll('.scatterlayer .point')].map(node => {
        const rect = node.getBoundingClientRect();
        return {x: rect.x + rect.width / 2, y: rect.y + rect.height / 2};
      }),
    };
  });
  try {
    await page.goto(pathToFileURL(request.html).href, {waitUntil: 'load', timeout: 45000});
    await page.evaluate(() => window.deepvizReady);
    const before = await snapshot();
    const hover_states = [];
    if (request.sink === 'hover') {
      for (let index = 0; index < before.mark_centers.length; index++) {
        const point = before.mark_centers[index];
        await page.mouse.move(point.x, point.y); // Native pointer only; never click.
        await page.waitForFunction(expected => document.getElementById('chart-0')._hoverdata
          ?.some(item => item.pointNumber === expected), index, {timeout: 10000});
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        hover_states.push(await snapshot());
        if (index === 0) await page.screenshot({path: request.image, fullPage: true});
      }
    } else await page.screenshot({path: request.image, fullPage: true});
    const native_json_bytes = await page.evaluate(() => new TextEncoder()
      .encode(document.getElementById('deepviz-data').textContent).length);
    await fs.writeFile(request.result, JSON.stringify({
      before, hover_states, native_json_bytes, html_bytes: (await fs.stat(request.html)).size,
      errors, blocked, browser: browser.version(), node: process.version,
      playwright: require(path.join(modules, 'playwright/package.json')).version,
    }, null, 2));
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error.stack); process.exitCode = 1; });
