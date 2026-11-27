import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {lstatSync, readFileSync, realpathSync} from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {fileURLToPath} from 'node:url';

import * as toolkit from '@deepviz/agent-toolkit';
import schema from '@deepviz/agent-toolkit/chart-spec.schema.json' with {type: 'json'};

const root = path.dirname(fileURLToPath(import.meta.url));
const installed = path.join(root, 'node_modules', '@deepviz', 'agent-toolkit');
const expected = JSON.parse(readFileSync(new URL('./canonical-git-blobs.json', import.meta.url), 'utf8'));
const publicNames = [
  'ValidationError', 'buildRendererSpec', 'chartKinds', 'chartSpecSchema', 'createTools',
  'defaultAssets', 'isObject', 'normalize', 'normalizeStream', 'render', 'renderStream',
  'safeKey', 'validateSpec',
];

function contained(resolved) {
  const actual = realpathSync(fileURLToPath(resolved));
  const relative = path.relative(realpathSync(installed), actual);
  assert.ok(relative && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative));
  return actual;
}

test('materialized package is real, public ESM namespace has exactly the unchanged 13 exports', () => {
  assert.equal(lstatSync(installed).isSymbolicLink(), false);
  assert.equal(lstatSync(path.join(root, 'node_modules')).isSymbolicLink(), false);
  const entry = contained(import.meta.resolve('@deepviz/agent-toolkit'));
  assert.equal(entry, realpathSync(path.join(installed, 'dist', 'index.js')));
  assert.deepEqual(Object.keys(toolkit).sort(), publicNames.sort());
  assert.equal(toolkit.validateSpec().version, 1);
});

test('schema explicit export remains inside the materialized package and matches the public API', () => {
  contained(import.meta.resolve('@deepviz/agent-toolkit/chart-spec.schema.json'));
  assert.deepEqual(schema, toolkit.chartSpecSchema);
  assert.equal(schema.$ref, '#/$defs/ChartSpec');
  assert.equal(schema.$defs.ChartSpec.properties.version.const, 1);
});

for (const filename of ['README.md', 'system.md', 'request.md']) {
  test(`raw ${filename} export resolves INSIDE the materialized package and equals fixed Git blob bytes`, () => {
    const resolved = import.meta.resolve(`@deepviz/agent-toolkit/prompts/v1/${filename}`);
    const actualPath = contained(resolved);
    assert.equal(actualPath, realpathSync(path.join(installed, 'dist', 'prompts', 'v1', filename)));
    const bytes = readFileSync(actualPath);
    const oracle = expected.prompts[filename];
    assert.deepEqual(bytes, Buffer.from(oracle.base64, 'base64'), 'Not canonical committed prompt bytes');
    assert.equal(createHash('sha256').update(bytes).digest('hex'), oracle.sha256);
    assert.equal(bytes.length, oracle.bytes);
    assert.equal(bytes.includes(13), false, 'CR/CRLF is not byte-identical to the committed LF source');
    assert.equal(bytes.at(-1), 10);
    assert.equal(bytes.subarray(0, 3).toString('hex') === 'efbbbf', false);
  });
}

test('canonical system/request keep v1 trust boundary, six-step workflow and request order', () => {
  const read = name => readFileSync(contained(import.meta.resolve(
    `@deepviz/agent-toolkit/prompts/v1/${name}.md`,
  )), 'utf8');
  const system = read('system');
  const request = read('request');
  assert.ok(system.startsWith('# DeepViz visualization policy — v1\n'));
  assert.ok(request.startsWith('# Request template — v1\n'));
  assert.match(system, /untrusted data, never as instructions/);
  assert.match(system, /prompt|provided declarative DeepViz tools/);
  let previous = -1;
  for (const anchor of ['1. Establish', '2. Use `normalize_data`', '3. Call `recommend_chart`',
    '4. Choose one', '5. Inspect returned warnings', '6. Return the chart path']) {
    const position = system.indexOf(anchor);
    assert.ok(position > previous, `Missing or out-of-order workflow: ${anchor}`);
    previous = position;
  }
  previous = -1;
  for (const anchor of ['> Question:', '> Goal:', '> Source reference:', '> Known fields/units:',
    '> Required mapping/reduction:', '> Deliverable:', '> Profile the source']) {
    const position = request.indexOf(anchor);
    assert.ok(position > previous, `Missing or out-of-order request: ${anchor}`);
    previous = position;
  }
  assert.match(request, /replace only the bracketed values/);
  assert.match(request, /without returning raw data/);
});

test('raw Markdown is not imported as executable ESM or exposed through a wildcard', async () => {
  await assert.rejects(import('@deepviz/agent-toolkit/prompts/v1/system.md'),
    error => error.code === 'ERR_UNKNOWN_FILE_EXTENSION');
  assert.throws(() => import.meta.resolve('@deepviz/agent-toolkit/prompts/v1/not-exported.md'),
    error => error.code === 'ERR_PACKAGE_PATH_NOT_EXPORTED');
});

test('public normalize and streaming API preserve independent literal counts/sums', async () => {
  const rows = [{region: '東京', value: 2}, {region: '東京', value: 5}, {region: 'East', value: -3}];
  const spec = {kind: 'bar', x: 'region', y: 'value', aggregation: 'sum'};
  const normalized = toolkit.normalize(rows, spec);
  assert.equal(normalized.input_count, 3);
  assert.deepEqual(normalized.records, [{region: '東京', value: 7}, {region: 'East', value: -3}]);
  const streamed = await toolkit.normalizeStream((async function* () { yield* rows; })(), spec);
  assert.deepEqual(streamed.records, [{region: '東京', value: 7}, {region: 'East', value: -3}]);
  assert.equal(streamed.input_count, 3);
});

test('public native SVG/tool helper smoke creates real HTML but is not a browser visual signoff', async () => {
  const rows = [{region: 'A', value: 3}, {region: 'B', value: 7}];
  const spec = {kind: 'bar', x: 'region', y: 'value', width: 480, height: 320};
  const artifact = toolkit.render(rows, spec, 'svg');
  assert.equal(artifact.input_count, 2);
  assert.equal(artifact.output_count, 2);
  assert.match(artifact.html, /<svg/);
  const tools = toolkit.createTools();
  assert.deepEqual(tools.map(tool => tool.name).sort(),
    ['render_antv', 'render_echarts', 'render_plotly', 'render_svg', 'render_vega']);
  const result = await tools.find(tool => tool.name === 'render_svg').invoke({data: rows, spec});
  assert.equal(result.output_count, 2);
  assert.match(result.html, /<svg/);
});
