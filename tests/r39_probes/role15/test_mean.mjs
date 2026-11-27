import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {api, artifacts, bits, record} from './preload.mjs';

const vectors = JSON.parse(fs.readFileSync(path.join(artifacts, 'reference-vectors.json'), 'utf8')).vectors;
const spec = Object.freeze({kind: 'bar', x: 'g', y: 'v', aggregation: 'mean', max_points: 10});
function freezeRows(rows) {return Object.freeze(rows.map(row => Object.freeze(row)));}
async function run(rows, specification, stream) {
  let consumed = 0, iterations = 0, closed = false;
  const iterable = {[Symbol.asyncIterator]() {
    iterations++; assert.equal(iterations, 1, 'input must not be replayed');
    return (async function* () {try {for (const row of rows) {consumed++; yield row;}} finally {closed = true;}})();
  }};
  const result = stream ? await api.normalizeStream(iterable, specification) : api.normalize(rows, specification);
  assert.equal(consumed, stream ? rows.length : 0); assert.equal(iterations, stream ? 1 : 0);
  assert.equal(closed, stream);
  return {result, consumed, iterations, closed};
}
for (const vector of vectors.filter(row => row.label !== 'weighted-tail-reference')) for (const stream of [false, true]) {
  test(`independent exact-rational ${vector.label} ${stream ? 'one-pass-stream' : 'records'}`, async () => {
    const rows = freezeRows(vector.values.map(v => ({g: 'only', v})));
    vector.values.forEach((value, i) => {if (typeof value === 'number') assert.equal(bits(value), vector.input_bits[i]);});
    const before = rows.map(row => ({...row, numeric_bits: typeof row.v === 'number' ? bits(row.v) : null}));
    const observed = await run(rows, spec, stream), result = observed.result;
    assert.equal(result.input_count, rows.length); assert.equal(result.strategy, 'mean'); assert.equal(result.records.length, 1);
    const value = result.records[0].v;
    assert.equal(result.records[0].g, 'only');
    if (vector.expected_bits === null) assert.equal(value, null);
    else {assert.equal(bits(value), vector.expected_bits); assert.ok(Number.isFinite(value));}
    assert.deepEqual(rows.map(row => ({...row, numeric_bits: typeof row.v === 'number' ? bits(row.v) : null})), before);
    assert.ok(!result.warnings.some(warning => /non-finite/i.test(warning)));
    if (vector.values.some(value => value !== null && typeof value !== 'number')) {
      assert.ok(result.warnings.some(warning => /non-numeric measure values excluded/i.test(warning)));
    }
    record({test: vector.label, stream, expected_bits: vector.expected_bits, actual_bits: value === null ? null : bits(value),
      valid_denominator: vector.valid_count, ...observed, input_not_mutated: true, spec_not_mutated: true});
  });
}
for (const stream of [false, true]) {
  test(`weighted other keeps valid-count weights ${stream}`, async () => {
    const head = Array.from({length: 9}, (_, i) => ({g: `g${i}`, v: i}));
    const rows = freezeRows([...head, ...[0, 0].map(v => ({g: 'tail0', v})),
      ...[12, 12, 12, 12].map(v => ({g: 'tail1', v})), ...[null, true, '4'].map(v => ({g: 'tail2', v}))]);
    const observed = await run(rows, spec, stream), result = observed.result;
    const expected = vectors.find(vector => vector.label === 'weighted-tail-reference');
    assert.equal(result.input_count, 18); assert.equal(result.records.length, 10); assert.equal(result.strategy, 'mean');
    assert.deepEqual(result.records.slice(0, 9), head);
    assert.equal(result.records[9].g, '__deepviz_other__'); assert.equal(bits(result.records[9].v), expected.expected_bits);
    assert.equal(result.records[9].v, 8); assert.ok(result.warnings.some(warning => /other/i.test(warning)));
    assert.ok(result.warnings.some(warning => /non-numeric measure values excluded/i.test(warning)));
    record({test: 'weighted-other', stream, ...observed, expected_bits: expected.expected_bits,
      actual_bits: bits(result.records[9].v), valid_denominator: 6, input_not_mutated: true});
  });
  test(`mean with inferred mapping and default point budget ${stream}`, async () => {
    const rows = freezeRows([{g: 'only', v: 1}, {g: 'only', v: 5}]);
    const specification = Object.freeze({aggregation: 'mean'}), observed = await run(rows, specification, stream);
    assert.deepEqual(observed.result, {records: [{g: 'only', v: 3}], input_count: 2, warnings: [], strategy: 'mean'});
    assert.deepEqual(specification, {aggregation: 'mean'});
    record({test: 'inferred-mapping-default-budget', stream, ...observed, input_not_mutated: true, spec_not_mutated: true});
  });
  test(`count remains all-record count not valid numeric denominator ${stream}`, async () => {
    const rows = freezeRows([1, null, '2', false].map(v => ({g: 'only', v})));
    const observed = await run(rows, Object.freeze({x: 'g', aggregation: 'count'}), stream);
    assert.equal(observed.result.input_count, 4); assert.equal(observed.result.strategy, 'count');
    assert.deepEqual(observed.result.records, [{g: 'only', count: 4}]);
    record({test: 'count-negative-control', stream, ...observed, input_not_mutated: true});
  });
  test(`empty mean keeps empty count and no fabricated value ${stream}`, async () => {
    const rows = freezeRows([]), observed = await run(rows, spec, stream);
    assert.deepEqual(observed.result, {records: [], input_count: 0, warnings: [], strategy: 'mean'});
    record({test: 'empty-mean', stream, ...observed, input_not_mutated: true});
  });
}
test('retained-budget negative stops bounded mean stream and closes once', async () => {
  let consumed = 0, iterations = 0, closed = false;
  const iterable = {[Symbol.asyncIterator]() {
    iterations++; assert.equal(iterations, 1);
    return (async function* () {try {for (let i = 0; i < 512; i++) {
      consumed++; yield Object.freeze({g: 'k'.repeat(32700) + i, v: 1});
    }} finally {closed = true;}})();
  }};
  let actualError;
  await assert.rejects(api.normalizeStream(iterable, Object.freeze({...spec, max_points: 512})), error => {
    actualError = {name: error.name, message: error.message};
    return error instanceof api.ValidationError && /Retained normalized state exceeds 16 MiB/i.test(error.message);
  });
  assert.equal(iterations, 1); assert.equal(closed, true); assert.ok(consumed > 32 && consumed < 512);
  record({test: 'retained-budget-negative', max_input_records: 512, consumed, iterations, closed,
    actual_error: actualError, expected_rejection: true, no_input_mutation: true});
});