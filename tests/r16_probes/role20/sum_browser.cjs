// Native browser readback only; fixture data contains no code or HTML payloads.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const {pathToFileURL} = require('node:url');

async function run() {
  const [input, modules] = process.argv.slice(2);
  const request = JSON.parse(await fs.readFile(input, 'utf8'));
  const {chromium} = require(path.join(modules, 'playwright'));
  const assets = {};
  for (const [name, relative, url] of [
    ['echarts', 'echarts', 'https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js'],
    ['antv', '@antv/g2', 'https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js'],
  ]) {
    const file = path.join(modules, relative, 'dist', name === 'echarts' ? 'echarts.min.js' : 'g2.min.js');
    const bytes = await fs.readFile(file);
    assets[name] = {url, bytes, version: require(path.join(modules, relative, 'package.json')).version,
      sha256: crypto.createHash('sha256').update(bytes).digest('hex')};
  }
  if (assets.echarts.version !== '6.1.0' || assets.antv.version !== '5.4.8') throw new Error('Pinned assets differ');
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1050, height: 850}, deviceScaleFactor: 1});
  const errors = [];
  const blocked = [];
  const fulfilled = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.route('**/*', async route => {
    const url = route.request().url();
    if (url === pathToFileURL(request.html).href) await route.continue();
    else if (assets[request.engine]?.url === url) {
      fulfilled.push(url);
      await route.fulfill({status: 200, contentType: 'application/javascript', body: assets[request.engine].bytes});
    } else { blocked.push(url); await route.abort('blockedbyclient'); }
  });
  try {
    await page.goto(pathToFileURL(request.html).href, {waitUntil: 'load', timeout: 45000});
    const native_ready = await page.evaluate(async () => { await window.deepvizReady; return true; });
    const observed = await page.evaluate(engine => {
      const el = document.getElementById('chart-0');
      const payload = JSON.parse(document.getElementById('deepviz-data').textContent)[0];
      const result = {render_error: document.body.dataset.renderError || null,
        table_cells: [...document.querySelectorAll('tbody td')].map(node => node.textContent),
        svg_count: el.querySelectorAll('svg').length, canvas_count: el.querySelectorAll('canvas').length};
      if (engine === 'plotly') {
        result.native_values = el.data[0].y;
        result.bar_heights = [...el.querySelectorAll('.barlayer .point path')]
          .map(node => node.getBoundingClientRect().height);
      } else if (engine === 'echarts') {
        const instance = window.echarts.getInstanceByDom(el);
        result.native_values = instance.getOption().series[0].data.map(row => row[1]);
        result.bar_heights = [...el.querySelectorAll('svg path')]
          .filter(node => getComputedStyle(node).fill === 'rgb(56, 108, 176)')
          .map(node => node.getBoundingClientRect().height).filter(height => height > 5);
      } else {
        result.native_values = payload.data.map(row => row._y);
        const canvas = el.querySelector('canvas');
        const context = canvas.getContext('2d');
        const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
        const columns = [];
        for (let x = 0; x < canvas.width; x++) {
          const ys = [];
          for (let y = 0; y < canvas.height; y++) {
            const offset = (y * canvas.width + x) * 4;
            if (Math.abs(pixels[offset] - 56) < 2 && Math.abs(pixels[offset + 1] - 108) < 2
              && Math.abs(pixels[offset + 2] - 176) < 2 && pixels[offset + 3] > 240) ys.push(y);
          }
          if (ys.length >= 3) columns.push({x, min: Math.min(...ys), max: Math.max(...ys)});
        }
        const runs = [];
        for (const column of columns) {
          const last = runs.at(-1);
          if (!last || column.x > last.right + 1) runs.push({left: column.x, right: column.x, min: column.min, max: column.max});
          else { last.right = column.x; last.min = Math.min(last.min, column.min); last.max = Math.max(last.max, column.max); }
        }
        result.canvas_color_runs = runs;
        result.bar_heights = runs.map(run => run.max - run.min + 1);
      }
      return result;
    }, request.engine);
    await page.screenshot({path: request.image, fullPage: true});
    await fs.writeFile(request.result, JSON.stringify({...observed, native_ready, errors, blocked, fulfilled,
      browser: browser.version(), node: process.version,
      playwright: require(path.join(modules, 'playwright/package.json')).version,
      assets: Object.fromEntries(Object.entries(assets).map(([name, asset]) => [name,
        {version: asset.version, sha256: asset.sha256, url: asset.url}])),
    }, null, 2));
  } finally { await browser.close(); }
}

run().catch(error => { console.error(error.stack); process.exitCode = 1; });
