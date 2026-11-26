// Independent browser check of files actually retrieved through MCP, not regenerated charts.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const {pathToFileURL} = require('node:url');

async function main() {
  const [dependencyRoot, retrievedRoot, outputRoot] = process.argv.slice(2);
  assert(dependencyRoot && retrievedRoot && outputRoot, 'Pass dependency root, retrieved root, output root');
  const {chromium} = require(path.join(dependencyRoot, 'node_modules/playwright'));
  await fs.mkdir(outputRoot, {recursive: true});
  const browser = await chromium.launch({headless: true});
  const results = [];
  try {
    for (const engine of ['matplotlib', 'plotly', 'vega', 'echarts', 'antv']) {
      const page = await browser.newPage({viewport: {width: 1100, height: 850}, deviceScaleFactor: 1});
      const errors = [];
      const requests = [];
      page.on('pageerror', error => errors.push(`pageerror: ${error.message}`));
      page.on('console', message => { if (message.type() === 'error') errors.push(`console: ${message.text()}`); });
      page.on('requestfailed', request => errors.push(`requestfailed: ${request.url()}: ${request.failure()?.errorText}`));
      page.on('response', response => {
        if (response.status() >= 400) errors.push(`http ${response.status()}: ${response.url()}`);
        if (response.url().startsWith('https:')) requests.push({url: response.url(), status: response.status()});
      });
      const result = {engine, errors, requests};
      try {
        await page.goto(pathToFileURL(path.join(retrievedRoot, engine, 'chart.html')).href, {
          waitUntil: 'load', timeout: 45000,
        });
        await page.evaluate(() => {
          if (window.deepvizReady) {
            window.deepvizReady.then(() => { window.__n13Ready = true; }, error => {
              window.__n13Failure = String(error);
            });
          } else if ([...document.images].every(image => image.complete && image.naturalWidth > 0)) {
            window.__n13Ready = true;
          }
        });
        await page.waitForFunction(() => window.__n13Ready || window.__n13Failure, null, {timeout: 45000});
        result.runtime = await page.evaluate(engineName => {
          const dataElement = document.getElementById('deepviz-data');
          const state = {
            title: document.title,
            renderError: document.body.dataset.renderError || window.__n13Failure || null,
            summary: document.getElementById('chart-summary-0')?.textContent,
            table: [...document.querySelectorAll('tbody tr')].map(row => [...row.cells].map(cell => cell.textContent)),
            svgCount: document.querySelectorAll('svg').length,
            canvasCount: document.querySelectorAll('canvas').length,
            images: [...document.images].map(image => ({src: image.getAttribute('src'), width: image.naturalWidth})),
            payload: dataElement ? JSON.parse(dataElement.textContent) : null,
          };
          if (engineName === 'plotly') {
            const graph = document.getElementById('chart-0');
            state.renderedData = graph.data.map(trace => ({x: trace.x, y: trace.y}));
            state.barPaths = [...document.querySelectorAll('.barlayer .point path')].map(mark => mark.getAttribute('d'));
          }
          if (engineName === 'echarts') {
            const chart = window.echarts.getInstanceByDom(document.getElementById('chart-0'));
            state.renderedData = chart.getOption().series.map(series => series.data);
            state.barPaths = [...document.querySelectorAll('#chart-0 svg path[fill="#386cb0"]')].map(mark => mark.getAttribute('d'));
            const svg = document.querySelector('#chart-0 svg');
            const axisTitle = [...svg.querySelectorAll('text')].find(text => text.textContent === 'category');
            const svgRect = svg.getBoundingClientRect();
            const titleRect = axisTitle.getBoundingClientRect();
            state.xAxisTitleBounds = {text: axisTitle.textContent, left: titleRect.left, right: titleRect.right,
              svgLeft: svgRect.left, svgRight: svgRect.right};
          }
          return state;
        }, engine);
        assert.equal(result.runtime.renderError, null);
        assert.deepEqual(result.runtime.table, [['Alpha', '7'], ['Beta', '11'], ['Gamma', '-3']]);
        assert.match(result.runtime.summary, /3 displayed records from 4 input records/);
        if (engine === 'plotly') {
          assert.deepEqual(result.runtime.renderedData, [{x: ['Alpha', 'Beta', 'Gamma'], y: [7, 11, -3]}]);
          assert.equal(result.runtime.barPaths.length, 3);
        } else if (engine === 'echarts') {
          assert.deepEqual(result.runtime.renderedData, [[['Alpha', 7], ['Beta', 11], ['Gamma', -3]]]);
          assert.equal(result.runtime.barPaths.length, 3);
          const bounds = result.runtime.xAxisTitleBounds;
          assert(bounds.left >= bounds.svgLeft && bounds.right <= bounds.svgRight,
            `ECharts x-axis title is clipped: ${JSON.stringify(bounds)}`);
        } else if (engine === 'antv') {
          assert(result.runtime.canvasCount > 0 || result.runtime.svgCount > 0);
          assert.deepEqual(result.runtime.payload[0].data.map(row => row._y), [7, 11, -3]);
        } else {
          assert(result.runtime.images.some(image => image.width > 0));
        }
        assert.deepEqual(errors, [], `${engine} browser errors`);
        result.status = 'PASS';
      } catch (error) {
        result.status = 'FAIL';
        result.error = error.stack;
      }
      await page.screenshot({path: path.join(outputRoot, `${engine}.png`), fullPage: true});
      results.push(result);
      await fs.writeFile(path.join(outputRoot, 'browser-results.json'), JSON.stringify(results, null, 2));
      await page.close();
    }
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify(results.map(({engine, status, errors, error}) => ({engine, status, errors, error})), null, 2));
  assert(results.every(result => result.status === 'PASS'), 'At least one browser acceptance failed');
}

main().catch(error => { console.error(error.stack); process.exitCode = 1; });
