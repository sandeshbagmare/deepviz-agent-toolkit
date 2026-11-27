import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {existsSync, readFileSync, writeFileSync} from 'node:fs';
import {createServer} from 'node:http';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath, pathToFileURL} from 'node:url';

const bytes = value => Buffer.byteLength(typeof value === 'string' ? value : JSON.stringify(value));
const save = (directory, name, value) => writeFileSync(join(directory, name), typeof value === 'string' ? value : JSON.stringify(value, null, 2));
const project = result => Object.fromEntries(['paths', 'mime_type', 'engine', 'input_count', 'output_count', 'strategy', 'warnings'].map(key => [key, result[key]]));
const jsonRoundtrip = value => assert.deepEqual(JSON.parse(JSON.stringify(value)), value, 'Result is not literal JSON-compatible');
function stableArtifact(artifact) {
  const nonce = artifact.html.match(/<script nonce="([a-f0-9]{32})"/)[1];
  return {...artifact, html: artifact.html.split(nonce).join('CSP_NONCE')};
}

async function boundedSum(api, config) {
  const tool = api.createTools().find(tool => tool.name === 'render_vega');
  const data = [
    {team: 'A', sales: 10, note: 'source-only-A'}, {team: 'B', sales: 20},
    {team: 'C', sales: 30}, {team: 'D', sales: 40}, {team: 'E', sales: 50},
    {team: 'F', sales: 60}, {team: 'G', sales: 70}, {team: 'H', sales: 80},
    {team: 'I', sales: 90}, {team: 'J', sales: 100}, {team: 'K', sales: 110},
    {team: 'L', sales: 120}, {team: 'A', sales: 5}, {team: 'B', sales: 7},
  ];
  const expected = [
    {team: 'A', sales: 15}, {team: 'B', sales: 27}, {team: 'C', sales: 30},
    {team: 'D', sales: 40}, {team: 'E', sales: 50}, {team: 'F', sales: 60},
    {team: 'G', sales: 70}, {team: 'H', sales: 80}, {team: 'I', sales: 90},
    {team: '__deepviz_other__', sales: 330},
  ];
  const spec = {kind: 'bar', x: 'team', y: 'sales', aggregation: 'sum', max_points: 10, width: 900, height: 520, title: 'Sales by team (bounded)', theme: 'light'};
  const before = JSON.stringify({data, spec});
  const result = await tool.invoke({data, spec});
  const repeat = await tool.invoke({data, spec});
  assert.equal(JSON.stringify({data, spec}), before, 'Caller input was mutated');
  assert.deepEqual(stableArtifact(result), stableArtifact(repeat), 'Only the CSP nonce may differ');
  assert.deepEqual(result.renderer_spec.normalized.records, expected);
  assert.deepEqual(result.renderer_spec.spec.data.values, expected, 'Native renderer received unreduced or different values');
  assert.equal(result.renderer_spec.spec.encoding.x.field, 'team');
  assert.equal(result.renderer_spec.spec.encoding.y.field, 'sales');
  assert.deepEqual(project(result), {
    paths: [], mime_type: 'text/html', engine: 'vega', input_count: 14, output_count: 10, strategy: 'sum',
    warnings: ['Group cardinality exceeded max_points=10; first 9 groups are exact and all remaining contributions form the final other bucket'],
  });
  assert.equal(expected.reduce((sum, row) => sum + row.sales, 0), 792);
  assert.equal(JSON.stringify(result).includes('source-only-A'), false, 'Raw discarded source values leaked into serialized artifact');
  assert.ok(bytes(expected) < 1024);
  assert.ok(bytes(result) < 32 * 1024, 'Unexpectedly inflated response for this bounded task');
  assert.ok(bytes(project(result)) < 512, 'Caller-selected metadata projection is not concise');
  jsonRoundtrip(result);
  save(config.output, 'bounded-sum.native.json', result.renderer_spec);
  return {metadata: project(result), literal_retained_records: expected, total_sales: 792, retained_json_bytes: bytes(expected), artifact_json_bytes: bytes(result), caller_projection_json_bytes: bytes(project(result)), deterministic_except_csp_nonce: true, actual_return_fields: Object.keys(result), handle_api: 'none: paths is empty; the actual tool returns inline HTML and renderer_spec, not a retrieval handle'};
}

async function dashboard(api, config) {
  const data = {
    salesRows: [{region: 'East', sales: 4}, {region: 'West', sales: 9}],
    serviceRows: [{queue: 'Fast', minutes: 3}, {queue: 'Slow', minutes: 12}, {queue: 'Mixed', minutes: 6}],
  };
  const spec = {kind: 'dashboard', title: 'Team operating snapshot', columns: 2, theme: 'light', charts: [
    {kind: 'bar', title: 'Regional sales', x: 'region', y: 'sales', aggregation: 'none', max_points: 10, data_path: 'salesRows', theme: 'light'},
    {kind: 'bar', title: 'Queue minutes', x: 'queue', y: 'minutes', aggregation: 'none', max_points: 10, data_path: 'serviceRows', theme: 'dark'},
  ]};
  const before = JSON.stringify({data, spec});
  const result = await api.createTools().find(tool => tool.name === 'render_vega').invoke({data, spec});
  assert.equal(JSON.stringify({data, spec}), before);
  assert.deepEqual(project(result), {paths: [], mime_type: 'text/html', engine: 'vega', input_count: 3, output_count: 5, strategy: 'dashboard', warnings: ['Dashboard children select different input counts; input_count is the maximum child count']});
  const children = result.renderer_spec.children;
  assert.equal(children.length, 2);
  assert.deepEqual(children[0].normalized.records, [{region: 'East', sales: 4}, {region: 'West', sales: 9}]);
  assert.deepEqual(children[1].normalized.records, [{queue: 'Fast', minutes: 3}, {queue: 'Slow', minutes: 12}, {queue: 'Mixed', minutes: 6}]);
  assert.equal(children[0].normalized.input_count, 2);
  assert.equal(children[1].normalized.input_count, 3);
  for (const [index, title, x, y, theme, background] of [[0, 'Regional sales', 'region', 'sales', 'light', 'white'], [1, 'Queue minutes', 'queue', 'minutes', 'dark', '#111827']]) {
    const child = children[index];
    assert.equal(child.chart_spec.title, title);
    assert.equal(child.chart_spec.theme, theme);
    assert.equal(child.spec.encoding.x.field, x);
    assert.equal(child.spec.encoding.y.field, y);
    assert.equal(child.spec.config.background, background);
    assert.deepEqual(child.spec.data.values, child.normalized.records);
    assert.deepEqual(child.normalized.warnings, []);
    assert.equal(child.normalized.strategy, 'none');
    assert.ok(result.html.includes(`<h2 id="heading-${index}">${title}</h2>`));
  }
  assert.notEqual(children[0].normalized.records, children[1].normalized.records);
  assert.notDeepEqual(children[0].spec.data.values, children[1].spec.data.values);
  jsonRoundtrip(result);
  assert.ok(bytes(result) < 32 * 1024);
  save(config.output, 'dashboard.native.json', result.renderer_spec);
  return {metadata: project(result), children: children.map(child => ({title: child.chart_spec.title, theme: child.chart_spec.theme, data_path: child.chart_spec.data_path, records: child.normalized.records, input_count: child.normalized.input_count, x: child.spec.encoding.x.field, y: child.spec.encoding.y.field, background: child.spec.config.background})), artifact_json_bytes: bytes(result), visual_scope: 'Two-child Vega native payload/HTML headings only; this task does not claim browser paint of both native engines'};
}

async function discoveryErrors(api, config) {
  assert.ok(config.python, 'Supply the existing read-only Python interpreter with jsonschema; do not install packages');
  const tools = api.createTools();
  assert.deepEqual(tools.map(tool => tool.name), ['render_vega', 'render_echarts', 'render_antv', 'render_plotly', 'render_svg']);
  const metadata = tools.map(({name, description, inputSchema}) => ({name, description, inputSchema}));
  jsonRoundtrip(metadata);
  const request = {data: [{team: 'North', sales: 2}], spec: {kind: 'bar', x: 'team', y: 'sales', aggregation: 'sum', max_points: 10, title: 'Sales comparison'}};
  for (const item of metadata) {
    assert.ok(item.description.includes('bounded') && item.description.includes('No filesystem or arbitrary code execution'));
    assert.deepEqual(item.inputSchema.required, ['data']);
    assert.equal(item.inputSchema.additionalProperties, false);
    assert.equal(item.inputSchema.properties.spec.$ref, '#/$defs/ChartSpec');
    assert.equal(item.inputSchema.$defs.ChartSpec.additionalProperties, false);
  }
  const validation = spawnSync(config.python, [fileURLToPath(new URL('./validate-tool-schema.py', import.meta.url))], {input: JSON.stringify({tools: metadata, request}), encoding: 'utf8', timeout: 15_000});
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
  const schemaResult = JSON.parse(validation.stdout);
  assert.equal(schemaResult.schemas_checked, 5);
  assert.deepEqual(schemaResult.each_schema_controls, [true, false, false]);
  const tool = tools.find(tool => tool.name === 'render_svg');
  const errors = [];
  for (const [input, message] of [
    [{...request, spec: {...request.spec, y: 'sales_typo'}}, 'Requested field missing from input: sales_typo'],
    [{...request, spec: {...request.spec, typoY: 'sales'}}, 'Unknown ChartSpec property: typoY'],
    [{spec: request.spec}, 'Tool input requires data and optional spec only'],
  ]) {
    await assert.rejects(tool.invoke(input), error => { assert.ok(error instanceof api.ValidationError); assert.equal(error.message, message); errors.push({name: error.name, message: error.message}); return true; });
  }
  const result = await tool.invoke(request);
  assert.deepEqual(result.renderer_spec.normalized.records, [{team: 'North', sales: 2}]);
  assert.equal(result.input_count, 1);
  assert.equal(result.output_count, 1);
  jsonRoundtrip(result);
  assert.equal(/<script[^>]*src=/.test(result.html), false, 'SVG should have no external script dependency');
  save(config.output, 'discovery.json', metadata);
  return {discovered_tools: metadata.map(tool => ({name: tool.name, description: tool.description, required: tool.inputSchema.required, properties: Object.keys(tool.inputSchema.properties)})), schema_validation: schemaResult, valid_explicit_request: true, errors, recovered_valid_call: project(result), integration_boundary: 'Framework-neutral public TS invoke/inputSchema helpers; no model, paid provider, Deep Agent SDK or artifact retrieval service is invoked'};
}

async function browserControl(api, config) {
  const modulePath = config.tooling && join(config.tooling, 'playwright/index.mjs');
  if (!modulePath || !existsSync(modulePath)) return {skipped: true, reason: 'Optional installed Playwright module unavailable; no browser claim'};
  const {chromium} = await import(pathToFileURL(modulePath).href);
  if (!existsSync(chromium.executablePath())) return {skipped: true, reason: 'Optional installed Chromium executable unavailable; no browser claim'};
  const result = await api.createTools().find(tool => tool.name === 'render_svg').invoke({
    data: [{category: 'Amber', units: 3}, {category: 'Jade', units: 7}, {category: 'Plum', units: 5}],
    spec: {kind: 'bar', x: 'category', y: 'units', aggregation: 'none', max_points: 10, width: 720, height: 400, title: 'Daily orders: Amber 3, Jade 7, Plum 5', theme: 'light'},
  });
  assert.equal(result.input_count, 3);
  assert.equal(result.output_count, 3);
  assert.equal(/<script[^>]*src=/.test(result.html), false);
  save(config.output, 'daily-orders.html', result.html);
  const server = createServer((request, response) => {
    if (request.url === '/control') { response.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'}); response.end(result.html); }
    else if (request.url === '/favicon.ico') { response.writeHead(204); response.end(); }
    else { response.writeHead(404); response.end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({headless: true});
    const page = await browser.newPage({viewport: {width: 1100, height: 850}, deviceScaleFactor: 1});
    const errors = [], unexpectedRequests = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    await page.route('**/*', route => {
      const url = route.request().url();
      if (url === `${base}/control` || url === `${base}/favicon.ico`) return route.continue();
      unexpectedRequests.push(url); return route.abort();
    });
    await page.goto(`${base}/control`);
    await page.waitForFunction(() => globalThis.deepvizReady === true);
    await page.evaluate(() => document.fonts.ready);
    const state = await page.locator('#chart-0 > svg').evaluate(svg => {
      const svgBox = svg.getBoundingClientRect();
      return {title: svg.getAttribute('aria-label'), errors: globalThis.deepvizErrors,
        marks: [...svg.querySelectorAll('rect.mark')].map(mark => { const box = mark.getBBox(); return {title: mark.querySelector('title').textContent, x: box.x, y: box.y, width: box.width, height: box.height}; }),
        category_labels: [...svg.querySelectorAll('.category-tick')].map(label => { const box = label.getBoundingClientRect(); return {text: label.querySelector('title').textContent, x: box.x, y: box.y, width: box.width, height: box.height}; }),
        all_text_inside_svg: [...svg.querySelectorAll('text')].every(text => { const box = text.getBoundingClientRect(); return box.left >= svgBox.left - 1 && box.right <= svgBox.right + 1 && box.top >= svgBox.top - 1 && box.bottom <= svgBox.bottom + 1; })};
    });
    const png = join(config.output, 'daily-orders.png');
    await page.screenshot({path: png, fullPage: true});
    save(config.output, 'browser-state.json', {chromium: browser.version(), state, errors, unexpectedRequests});
    assert.deepEqual(state.errors, []);
    assert.deepEqual(errors, [], 'Browser console/page errors are failures');
    assert.deepEqual(unexpectedRequests, [], 'Unexpected browser request');
    assert.equal(state.title, 'Daily orders: Amber 3, Jade 7, Plum 5');
    assert.deepEqual(state.marks.map(mark => mark.title), ['Amber: 3', 'Jade: 7', 'Plum: 5']);
    assert.deepEqual(state.category_labels.map(label => label.text), ['Amber', 'Jade', 'Plum']);
    assert.equal(state.all_text_inside_svg, true, 'A visible text label is clipped by the SVG boundary');
    for (let index = 0; index < 3; index++) {
      const mark = state.marks[index];
      assert.ok(mark.width > 0 && mark.height > 0);
      assert.ok(Math.abs(mark.height / state.marks[1].height - [3 / 7, 1, 5 / 7][index]) < 1e-6, 'Actual bar height ratio differs from caller values');
      if (index > 0) {
        assert.ok(state.marks[index - 1].x + state.marks[index - 1].width < mark.x, 'Bars overlap or changed category order');
        const previous = state.category_labels[index - 1], label = state.category_labels[index];
        assert.ok(previous.x + previous.width < label.x, 'Category labels overlap');
      }
    }
    return {metadata: project(result), chromium: browser.version(), native_geometry: state, console_page_errors: errors, unexpected_requests: unexpectedRequests, screenshot: png, screenshot_sha256: createHash('sha256').update(readFileSync(png)).digest('hex'), image_opened_by_tester: 'Pending separate image read; capture alone is not visual approval'};
  } finally { if (browser) await browser.close(); await new Promise(resolve => server.close(resolve)); }
}

export async function runTask(api, config) {
  const functions = {'bounded-sum': boundedSum, dashboard, 'discovery-errors': discoveryErrors, browser: browserControl};
  let result;
  try { result = {...await functions[config.task](api, config), task: config.task}; if (!result.skipped) result.passed = true; }
  catch (error) { result = {task: config.task, passed: false, failure: `${error.name}: ${error.message}`}; process.exitCode = 1; }
  save(config.output, `${config.task}.result.json`, result);
  process.stdout.write(JSON.stringify(result));
}
