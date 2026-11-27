import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
import {join, resolve} from 'node:path';
import {test} from 'node:test';
import {pathToFileURL} from 'node:url';
import {api, evidence, hash} from './source-proof.mjs';

// One literal public artifact, inspected as raw SVG and actual HTML. No renderer oracle helper.
test('R34 finite-only: actual signed 1e308 two-bar SVG and HTML paint', {timeout: 30000}, async () => {
  const rows = [{group: 'n', value: -1e308}, {group: 'p', value: 1e308}];
  const artifact = api.render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none',
    width: 240, height: 200, title: 'R34 finite ±1e308'}, 'svg');
  assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
  assert.equal(artifact.input_count, 2);
  assert.equal(artifact.output_count, 2);
  assert.equal(artifact.strategy, 'none');
  assert.deepEqual(artifact.warnings, []);
  assert.doesNotMatch(artifact.renderer_spec.spec.svg, /NaN|Infinity/);
  const output = join(evidence, 'bounded-browser');
  await mkdir(output); // Deliberately fresh; never overwrite another observation.
  const playwrightEntry = resolve(process.env.R34_PLAYWRIGHT);
  const {chromium} = await import(pathToFileURL(playwrightEntry).href);
  const browser = await chromium.launch({headless: true});
  const observations = [];
  try {
    for (const carrier of ['svg', 'html']) {
      const content = carrier === 'svg' ? artifact.renderer_spec.spec.svg : artifact.html;
      const input = join(output, `signed-extreme.${carrier}`);
      await writeFile(input, content, {flag: 'wx'});
      const context = await browser.newContext({viewport: {width: 900, height: 700}, offline: true, deviceScaleFactor: 1});
      try {
        const page = await context.newPage(), errors = [], external = [];
        page.setDefaultTimeout(5000);
        page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
        page.on('pageerror', error => errors.push(String(error)));
        page.on('requestfailed', request => errors.push(`requestfailed: ${request.url()}`));
        page.on('request', request => {if (/^https?:/.test(request.url())) external.push(request.url());});
        await page.route(/^https?:\/\//, route => route.abort());
        await page.goto(pathToFileURL(input).href, {waitUntil: 'load', timeout: 5000});
        if (carrier === 'html') await page.waitForFunction(() => globalThis.deepvizReady === true);
        await page.evaluate(() => document.fonts.ready);
        const svg = page.locator(carrier === 'html' ? '#chart-0 svg' : 'svg');
        const geometry = await svg.evaluate(element => ({
          width: element.viewBox.baseVal.width, height: element.viewBox.baseVal.height,
          actual: {width: element.getBoundingClientRect().width, height: element.getBoundingClientRect().height},
          marks: [...element.querySelectorAll('rect.mark')].map(mark => ({
            x: +mark.getAttribute('x'), y: +mark.getAttribute('y'), width: +mark.getAttribute('width'),
            height: +mark.getAttribute('height'), title: mark.querySelector('title').textContent,
            painted: {width: mark.getBoundingClientRect().width, height: mark.getBoundingClientRect().height},
          })),
          text: [...element.querySelectorAll('text')].map(text => {
            const box = text.getBBox(), matrix = text.getCTM();
            const points = [[box.x, box.y], [box.x + box.width, box.y], [box.x, box.y + box.height],
              [box.x + box.width, box.y + box.height]].map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
            return {literal: [...text.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(''),
              category: text.classList.contains('category-tick'),
              left: Math.min(...points.map(p => p.x)), right: Math.max(...points.map(p => p.x)),
              top: Math.min(...points.map(p => p.y)), bottom: Math.max(...points.map(p => p.y)),
              fontSize: Number.parseFloat(getComputedStyle(text).fontSize)};
          }),
        }));
        const runtime = carrier === 'html' ? await page.evaluate(() => globalThis.deepvizErrors) : [];
        const png = await svg.screenshot({timeout: 5000});
        await writeFile(join(output, `signed-extreme-${carrier}.png`), png, {flag: 'wx'});
        const observation = {carrier, geometry, errors, external, runtime, input_sha256: hash(content), png_sha256: hash(png)};
        observations.push(observation);
        await writeFile(join(output, `${carrier}.json`), JSON.stringify(observation, null, 2), {flag: 'wx'});
        assert.deepEqual([errors, external, runtime], [[], [], []]);
        assert.deepEqual([geometry.width, geometry.height, geometry.actual.width, geometry.actual.height], [240, 200, 240, 200]);
        assert.deepEqual(geometry.marks, [
          {x: 122.75, y: 100, width: 22, height: 35, title: 'n: -1e+308', painted: {width: 22, height: 35}},
          {x: 150.25, y: 65, width: 22, height: 35, title: 'p: 1e+308', painted: {width: 22, height: 35}},
        ]);
        assert.equal(geometry.marks[0].y, geometry.marks[1].y + geometry.marks[1].height);
        assert.deepEqual(geometry.text.filter(t => t.category).map(t => t.literal), ['n', 'p']);
        for (const text of geometry.text) assert.ok(text.fontSize >= 12 && text.left >= -0.05 && text.top >= -0.05 &&
          text.right <= 240.05 && text.bottom <= 200.05, JSON.stringify(text));
      } finally {await context.close();}
    }
    await writeFile(join(output, 'summary.json'), JSON.stringify({source_sha: 'c3ee1edbfc65406cef7fd809f5a6887471d576a5',
      node: process.version, chromium: browser.version(), playwright_entry: playwrightEntry,
      input: rows, input_count: 2, output_count: 2, observations}, null, 2), {flag: 'wx'});
  } finally {await browser.close();}
});
