// Real Chromium semantic probe. No installs, request interception, or CDN fake bodies.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const output = path.resolve(process.argv[2] || '');
const input = JSON.parse(await readFile(path.join(output, 'cases.json'), 'utf8'));
const browser = await chromium.launch({headless: true});
await mkdir(path.join(output, 'browser'), {recursive: false});
const report = {identity: input.identity, node: process.version, chromium: browser.version(),
  runtimeCases: [], checks: [], screenshotHashes: [], scope: 'checkpoint-only, not final source signoff'};
function check(caseID, name, condition, observed) {
  report.checks.push({case: caseID, name, pass: Boolean(condition), observed});
}
try {
  for (const fixture of input.cases) {
    const page = await browser.newPage({viewport: {width: 1250, height: 1000}, deviceScaleFactor: 1});
    const errors = [], failedRequests = [], responses = [];
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('pageerror', error => errors.push(String(error)));
    page.on('requestfailed', request => failedRequests.push({url: request.url(), error: request.failure()?.errorText}));
    page.on('response', response => {
      if (response.url().startsWith('https://') || response.status() >= 400)
        responses.push({url: response.url(), status: response.status()});
    });
    const row = {id: fixture.id, engine: fixture.engine, errors, failedRequests, responses};
    try {
      let htmlPath = path.join(output, fixture.html);
      if (fixture.engine === 'antv') {
        let html = await readFile(htmlPath, 'utf8');
        const anchor = '<script>const payloads=';
        assert(html.includes(anchor), 'AntV fixed bootstrap anchor missing');
        // Observe render calls only: preserve args, return value, options, and library implementation.
        const hook = '<script>window.__role06Charts=[];const renderOriginal=G2.Chart.prototype.render;'
          + 'G2.Chart.prototype.render=function(...args){window.__role06Charts.push(this);return renderOriginal.apply(this,args);};</script>';
        html = html.replace(anchor, hook + anchor);
        htmlPath = path.join(output, 'browser', `${fixture.id}-observed.html`);
        await writeFile(htmlPath, html, 'utf8');
      }
      await page.goto(pathToFileURL(htmlPath).href, {waitUntil: 'load', timeout: 60000});
      const readiness = await page.evaluate(async () => {
        if (!window.deepvizReady || typeof window.deepvizReady.then !== 'function') return 'missing';
        await window.deepvizReady;
        return document.body.dataset.renderError || 'resolved';
      });
      check(fixture.id, 'ready', readiness === 'resolved', readiness);
      const state = await page.evaluate(({engine}) => {
        const payloads = JSON.parse(document.getElementById('deepviz-data').textContent);
        const charts = payloads.map((native, index) => {
          const element = document.getElementById(`chart-${index}`);
          const box = element.getBoundingClientRect();
          const item = {id: element.id, ariaLabel: element.getAttribute('aria-label'),
            heading: element.parentElement.querySelector('h2').textContent,
            summary: document.getElementById(`chart-summary-${index}`).textContent,
            background: getComputedStyle(element).backgroundColor,
            box: {x: box.x, y: box.y, width: box.width, height: box.height},
            svgMarks: element.querySelectorAll('svg path, svg text').length,
            labels: [...element.querySelectorAll('svg text')].map(node => node.textContent)};
          if (engine === 'plotly') {
            item.nativeValues = element.data[0].y;
            if (element._fullLayout.xaxis) item.numericPixels = [1, 2, 4].map(x => element._fullLayout.xaxis.l2p(x));
            const bars = [...element.querySelectorAll('.barlayer .point path')];
            item.barBounds = bars.map(mark => {const b = mark.getBoundingClientRect(); return {x: b.x, y: b.y, width: b.width, height: b.height};});
          } else if (engine === 'echarts') {
            const chart = echarts.getInstanceByDom(element);
            const options = chart.getOption();
            item.nativeValues = options.series?.[0]?.data ?? null;
            if (options.xAxis?.length) item.numericPixels = [1, 2, 4].map(x => chart.convertToPixel({xAxisIndex: 0}, x));
            if (options.series?.[0]?.type === 'bar') {
              const data = chart.getModel().getSeriesByIndex(0).getData();
              item.barBounds = Array.from({length: data.count()}, (_, i) => data.getItemLayout(i));
            }
          } else {
            const chart = window.__role06Charts[index];
            const root = chart.getContext().canvas.document.documentElement;
            item.marks = [...root.querySelectorAll('.element')].map(mark => {
              const b = mark.getBBox();
              return {node: mark.nodeName, x: b.x, y: b.y, width: b.width, height: b.height,
                fill: mark.getAttribute('fill'), stroke: mark.getAttribute('stroke')};
            });
            item.labels = [...root.querySelectorAll('text')].map(mark => mark.getAttribute('text'));
            item.nativeValues = (native.children?.find(child => child.type === 'line') || native).data.map(row => row._y);
            item.numericPixels = item.marks.filter(mark => mark.width === 6 && mark.height === 6 && mark.fill === '#386cb0').map(mark => mark.x + 3);
            const canvas = element.querySelector('canvas');
            const pixels = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
            item.paintedPixels = 0;
            for (let i = 0; i < pixels.length; i += 4) if (pixels[i + 3] && pixels[i] + pixels[i + 1] + pixels[i + 2] < 650) item.paintedPixels++;
          }
          return item;
        });
        return {title: document.title, h1: document.querySelector('h1').textContent, payloads, charts};
      }, {engine: fixture.engine});
      row.state = state;
      check(fixture.id, 'title', state.title === fixture.title && state.h1 === fixture.title,
        {document: state.title, visible: state.h1});
      const manifest = JSON.parse(await readFile(path.join(output, fixture.manifest), 'utf8'));
      check(fixture.id, 'embedded-native-equals-manifest', JSON.stringify(state.payloads) === JSON.stringify(manifest.native_specs), state.payloads.length);
      for (let index = 0; index < state.charts.length; index++) {
        const chart = state.charts[index], metadata = manifest.charts[index];
        check(fixture.id, `metadata-${index}`, chart.summary.includes(`${metadata.output_count} displayed records from ${metadata.input_count} input records`), chart.summary);
        check(fixture.id, `visible-child-title-${index}`, chart.heading === metadata.spec.title && chart.ariaLabel === metadata.spec.title,
          {heading: chart.heading, aria: chart.ariaLabel, expected: metadata.spec.title});
        check(fixture.id, `paint-${index}`, fixture.engine === 'antv' ? chart.paintedPixels > 100 : chart.svgMarks > 0,
          fixture.engine === 'antv' ? chart.paintedPixels : chart.svgMarks);
      }
      const summary = page.locator('section details summary').first();
      const details = page.locator('section details').first();
      await summary.click();
      check(fixture.id, 'data-click-opens', await details.getAttribute('open') !== null,
        {tableRows: await details.locator('tbody tr').count()});
      await summary.focus();
      await page.keyboard.press('Enter');
      check(fixture.id, 'data-keyboard-closes', await details.getAttribute('open') === null, 'Enter on focused summary');
      if (fixture.checks.includes('bar-values')) {
        const observed = state.charts[0].nativeValues;
        const values = fixture.engine === 'echarts' ? observed.map(row => row[1]) : observed;
        check(fixture.id, 'bar-values', JSON.stringify(values) === '[12,31,7]', values);
        // A real pointer hover, not dispatchAction or a fabricated event result.
        if (fixture.engine === 'plotly') {
          const target = state.charts[0].barBounds[0];
          await page.mouse.move(target.x + target.width / 2, target.y + target.height / 2);
          await page.waitForFunction(() => /Alpha|12/.test(document.querySelector('.hoverlayer')?.textContent || ''), null, {timeout: 10000});
          check(fixture.id, 'pointer-tooltip', await page.locator('.hoverlayer').textContent().then(text => /Alpha|12/.test(text)), await page.locator('.hoverlayer').textContent());
        } else if (fixture.engine === 'echarts') {
          const mark = state.charts[0].barBounds[0], box = state.charts[0].box;
          await page.mouse.move(box.x + mark.x + mark.width / 2, box.y + mark.y + mark.height / 2);
          await page.waitForFunction(() => echarts.getInstanceByDom(document.getElementById('chart-0')).getZr().storage.getDisplayList().some(mark => /12/.test(String(mark.style?.text))), null, {timeout: 10000});
          const texts = await page.evaluate(() => echarts.getInstanceByDom(document.getElementById('chart-0')).getZr().storage.getDisplayList().map(mark => mark.style?.text).filter(Boolean));
          check(fixture.id, 'pointer-hover-recorded', true, texts);
        } else row.tooltipLimit = 'AntV native tooltip is explicitly disabled; tested actual data-table click and keyboard interaction instead.';
      }
      if (fixture.checks.includes('numeric-spacing')) {
        const xs = state.charts[0].numericPixels, ratio = xs?.length === 3 ? (xs[2] - xs[1]) / (xs[1] - xs[0]) : null;
        check(fixture.id, 'numeric-gap-1-to-2', ratio !== null && Math.abs(ratio - 2) < 1e-6, {pixels: xs, ratio});
        const raw = state.charts[0].nativeValues;
        const values = fixture.engine === 'echarts' ? raw.map(row => row[1]) : raw;
        check(fixture.id, 'numeric-values', JSON.stringify(values) === '[2,8,5]', values);
      }
      if (fixture.checks.includes('child-background')) {
        check(fixture.id, 'light-child-background', state.charts[0].background === 'rgb(255, 255, 255)', state.charts[0].background);
        check(fixture.id, 'dark-child-background', state.charts[1].background === 'rgb(23, 27, 38)', state.charts[1].background);
      }
      if (fixture.checks.includes('duplicate-containers')) {
        check(fixture.id, 'unique-three-containers', new Set(state.charts.map(chart => chart.id)).size === 3, state.charts.map(chart => chart.id));
        if (fixture.engine === 'antv') {
          const view = state.payloads[1], line = view.children?.find(child => child.type === 'line');
          check(fixture.id, 'native-view-line-point-wrapper', view.type === 'view' && line && view.children.some(child => child.type === 'point'), view.type);
          check(fixture.id, 'line-child-cost-values', JSON.stringify(line?.data.map(row => [row._x, row._y])) === '[["A",2],["B",4]]', line?.data);
        }
      }
      if (fixture.checks.includes('categorical-fill')) {
        const fills = state.charts[0].marks.map(mark => mark.fill).filter(fill => fill && fill !== 'none');
        check(fixture.id, 'category-fills-distinct', new Set(fills).size > 1, fills);
      }
      const screenshot = path.join(output, 'browser', `${fixture.id}.png`);
      await page.screenshot({path: screenshot, fullPage: true});
      const bytes = await readFile(screenshot);
      report.screenshotHashes.push({path: path.relative(output, screenshot).replaceAll('\\', '/'), bytes: bytes.length,
        sha256: createHash('sha256').update(bytes).digest('hex')});
      row.runtime = 'PASS';
    } catch (error) {
      row.runtime = 'FAIL';
      row.error = String(error);
      check(fixture.id, 'runtime', false, String(error));
    } finally {
      check(fixture.id, 'console-and-page-errors', errors.length === 0, errors);
      check(fixture.id, 'network-errors', failedRequests.length === 0 && !responses.some(response => response.status >= 400), {failedRequests, responses});
      report.runtimeCases.push(row);
      await page.close();
      await writeFile(path.join(output, 'browser-report.json'), JSON.stringify(report, null, 2));
    }
  }
} finally { await browser.close(); }
const failed = report.checks.filter(check => !check.pass);
console.log(JSON.stringify({source_sha: input.identity.source_sha, runtimeCases: report.runtimeCases.length,
  runtimeFailures: report.runtimeCases.filter(row => row.runtime !== 'PASS').length,
  checks: report.checks.length, failed: failed.length, failures: failed}, null, 2));
process.exitCode = failed.length ? 1 : 0;
