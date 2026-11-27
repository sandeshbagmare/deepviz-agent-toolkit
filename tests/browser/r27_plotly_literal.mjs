// Trusted native DOM collection only; payload strings are never executable code.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const [input, modules] = process.argv.slice(2);
const request = JSON.parse(await fs.readFile(input, 'utf8'));
const require = createRequire(import.meta.url);
const {chromium} = require(path.join(modules, 'playwright'));
const browser = await chromium.launch({headless: true});
try {
  const page = await browser.newPage({viewport: {width: 1500, height: 1000}, deviceScaleFactor: 1});
  const errors = [], blocked = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.route('**/*', async route => {
    if (route.request().url() === pathToFileURL(request.html).href) await route.continue();
    else { blocked.push(route.request().url()); await route.abort('blockedbyclient'); }
  });
  await page.goto(pathToFileURL(request.html).href, {waitUntil: 'load', timeout: 45000});
  await page.evaluate(() => window.deepvizReady);
  const collect = index => page.evaluate(({index, literals}) => {
    const graph = document.getElementById(`chart-${index}`);
    const text = [...graph.querySelectorAll('svg text')].map(node => node.textContent);
    return {
      titles: [...graph.querySelectorAll('.gtitle')].map(node => node.textContent), text,
      missing: literals.filter(value => !text.some(item => item.includes(value))),
      anchors: [...graph.querySelectorAll('a')].map(node => node.outerHTML),
      handlers: [...graph.querySelectorAll('*')].flatMap(node => [...node.attributes]
        .filter(attribute => /^on/i.test(attribute.name)).map(attribute => `${node.tagName}:${attribute.name}`)),
      x: graph.data[0].x, y: graph.data[0].y,
      hover_text: [...graph.querySelectorAll('.hoverlayer text')].map(node => node.textContent),
      centers: [...graph.querySelectorAll('.scatterlayer .point')].map(node => {
        const r = node.getBoundingClientRect(); return {x: r.x + r.width / 2, y: r.y + r.height / 2};
      }),
    };
  }, {index, literals: request.literals});
  const snapshots = [];
  for (let index = 0; index < request.child_count; index++) snapshots.push(await collect(index));
  const hover_states = [];
  if (request.case === 'geo') {
    for (let index = 0; index < snapshots[0].centers.length; index++) {
      const point = snapshots[0].centers[index];
      await page.mouse.move(point.x, point.y);
      await page.waitForFunction(expected => document.getElementById('chart-0')._hoverdata
        ?.some(item => item.pointNumber === expected), index, {timeout: 10000});
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      hover_states.push(await collect(0));
      if (index === 0) await page.screenshot({path: request.image, fullPage: true});
    }
  } else await page.screenshot({path: request.image, fullPage: true});
  await fs.writeFile(request.result, JSON.stringify({snapshots, hover_states, errors, blocked,
    browser: browser.version(), node: process.version,
    playwright: require(path.join(modules, 'playwright/package.json')).version}, null, 2));
} finally { await browser.close(); }
