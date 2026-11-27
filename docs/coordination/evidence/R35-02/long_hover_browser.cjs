// ONE trusted Cartesian-series hover inspection; no payload execution/clicks.
const fs = require('node:fs/promises');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
async function main() {
  const [requestPath, modules] = process.argv.slice(2);
  const request = JSON.parse(await fs.readFile(requestPath, 'utf8'));
  const {chromium} = require(path.join(modules, 'playwright'));
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1400, height: 900}, deviceScaleFactor: 1});
    const errors = [], blocked = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
    await page.route('**/*', async route => {
      if (route.request().url() === pathToFileURL(request.html).href) await route.continue();
      else {blocked.push(route.request().url()); await route.abort('blockedbyclient');}
    });
    await page.goto(pathToFileURL(request.html).href, {waitUntil: 'load', timeout: 45000});
    await page.evaluate(() => window.deepvizReady);
    const point = await page.evaluate(() => {
      const mark = document.querySelector('#chart-0 .scatterlayer .point');
      if (!mark) throw new Error('Expected real Cartesian point');
      const r = mark.getBoundingClientRect(); return {x: r.x + r.width / 2, y: r.y + r.height / 2};
    });
    await page.mouse.move(point.x, point.y);
    await page.waitForFunction(() => document.getElementById('chart-0')._hoverdata?.some(item => item.pointNumber === 0), {timeout: 10000});
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    const observed = await page.evaluate(() => {
      const graph = document.getElementById('chart-0');
      return {
        hover_names: [...graph.querySelectorAll('.hoverlayer .name')].map(n => n.textContent),
        hover_text: [...graph.querySelectorAll('.hoverlayer text')].map(n => n.textContent),
        legend: [...graph.querySelectorAll('.legendtext')].map(n => n.textContent),
        anchors: [...graph.querySelectorAll('a')].map(n => n.outerHTML),
        handlers: [...graph.querySelectorAll('*')].flatMap(n => [...n.attributes].filter(a => /^on/i.test(a.name)).map(a => a.name)),
        native_name: graph.data[0].name, x: graph.data[0].x, y: graph.data[0].y,
        actual_hover_namelength: graph._fullData[0].hoverlabel.namelength, actual_hoverinfo: graph._fullData[0].hoverinfo,
        titles: [...graph.querySelectorAll('.gtitle')].map(n => n.textContent),
      };
    });
    await page.screenshot({path: request.image, fullPage: true});
    await fs.writeFile(request.result, JSON.stringify({...observed, errors, blocked,
      browser: browser.version(), node: process.version,
      playwright: require(path.join(modules, 'playwright/package.json')).version}, null, 2));
  } finally {await browser.close();}
}
main().catch(error => {console.error(error.stack); process.exitCode = 1;});
