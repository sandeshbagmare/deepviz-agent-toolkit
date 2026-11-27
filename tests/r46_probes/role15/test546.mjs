import assert from 'node:assert/strict';
import test from 'node:test';
import {api, bits, record} from './preload.mjs';

const T = Number.MIN_VALUE, M = Number.MAX_VALUE, H = 2 ** 900;
const numericCases = [
  ['safe-integer-prefix-promotes-before-fraction', 'sum', [2 ** 52, 1, -(2 ** 52), 2 ** -1022, -(2 ** -1022)], 1],
  ['finite-prefix-residue-no-overflow', 'sum', [H, 3, -H], 3],
  ['residue-before-later-overflow', 'sum', [H, 3, -H, M, M, -M, -M], 3],
  ['subnormal-retained-without-overflow', 'sum', [H, T, -H], T],
  ['negative-subnormal-retained', 'sum', [-H, -T, H], -T],
  ['normal-tie-even-lower', 'sum', [1, 2 ** -53], 1],
  ['normal-tie-even-upper', 'sum', [1, 3 * 2 ** -53], 1 + 2 ** -51],
  ['subnormal-three-quarters-rounds-up', 'mean', [H, T, -H, 2 * T], T],
  ['negative-subnormal-three-quarters', 'mean', [-H, -T, H, -2 * T], -T],
  ['maximum-finite-three-term-mean', 'mean', [M, M, M], M],
  ['negative-exact-half-subnormal', 'mean', [-3 * T, 0, 0, 0, 0, 0], -0],
  ['wide-cancellation-rational-three-sevenths', 'mean', [H, 3, -H, M, M, -M, -M], 3 / 7, '3fdb6db6db6db6db'],
  ['true-sum-overflow-remains-null', 'sum', [M, M], null],
];
const freeze = value => {
  if (value && typeof value === 'object') {for (const child of Object.values(value)) freeze(child); Object.freeze(value);}
  return value;
};
const snapshot = value => JSON.stringify(value, (_, child) => typeof child === 'number' ? {$binary64: bits(child)} : child);
async function invoke(input, spec, stream) {
  freeze(input); freeze(spec);
  const before = snapshot(input), specBefore = snapshot(spec);
  let consumed = 0, iterations = 0, closed = false;
  const iterator = {[Symbol.asyncIterator]() {
    iterations++; assert.equal(iterations, 1, 'source must not be replayed');
    return (async function* () {try {for (const row of input) {consumed++; yield row;}} finally {closed = true;}})();
  }};
  const result = stream ? await api.normalizeStream(iterator, spec) : api.normalize(input, spec);
  assert.equal(iterations, Number(stream)); assert.equal(consumed, stream ? input.length : 0); assert.equal(closed, stream);
  assert.equal(snapshot(input), before); assert.equal(snapshot(spec), specBefore);
  return {result, consumed, iterations, closed, input_not_mutated: true, spec_not_mutated: true};
}
for (const [name, aggregation, values, expected, explicitBits] of numericCases) for (const stream of [false, true]) {
  test(`546 independent ${name} ${stream ? 'one-pass-async' : 'records'}`, async () => {
    const expectedBits = expected === null ? null : bits(expected);
    if (explicitBits) assert.equal(expectedBits, explicitBits);
    const observed = await invoke(values.map(v => ({g: 'only', v})), {x: 'g', y: 'v', aggregation}, stream);
    const result = observed.result; assert.equal(result.input_count, values.length); assert.equal(result.strategy, aggregation);
    assert.equal(result.records.length, 1); assert.equal(result.records[0].g, 'only');
    const actual = result.records[0].v;
    if (expected === null) {assert.equal(actual, null); assert.ok(result.warnings.some(warning => /non-finite/i.test(warning)));}
    else {assert.equal(bits(actual), expectedBits); assert.ok(Number.isFinite(actual)); assert.deepEqual(result.warnings, []);}
    record({test: name, stream, aggregation, literal_input_bits: values.map(bits), expected_bits: expectedBits,
      actual_bits: actual === null ? null : bits(actual), ...observed});
  });
}
for (const aggregation of ['sum', 'mean']) for (const stream of [false, true]) {
  test(`546 independent weighted-other prefix ${aggregation} ${stream}`, async () => {
    const head = Array.from({length: 9}, (_, i) => ({g: `head${i}`, v: i}));
    const rows = [...head, ...[H, 3, -H].map(v => ({g: 'tailA', v})),
      ...[M, M, -M, -M].map(v => ({g: 'tailB', v})), ...[null, true, '8'].map(v => ({g: 'ignored', v}))];
    const observed = await invoke(rows, {x: 'g', y: 'v', aggregation, max_points: 10}, stream), result = observed.result;
    assert.equal(result.input_count, 19); assert.equal(result.records.length, 10); assert.deepEqual(result.records.slice(0, 9), head);
    const expected = aggregation === 'sum' ? 3 : 3 / 7;
    assert.equal(result.records[9].g, '__deepviz_other__'); assert.equal(bits(result.records[9].v), bits(expected));
    assert.ok(result.warnings.some(warning => /other bucket/.test(warning)));
    assert.ok(result.warnings.some(warning => /non-numeric measure values excluded/i.test(warning)));
    record({test: 'weighted-other-prefix', aggregation, stream, valid_denominator: 7, expected_bits: bits(expected), actual_bits: bits(result.records[9].v), ...observed});
  });
}
for (const stream of [false, true]) test(`546 independent count preserves missing/null/flags ${stream}`, async () => {
  const rows = [...[true, null, 3, '4'].map(v => ({g: 'only', v})), {g: 'only'}];
  const observed = await invoke(rows, {x: 'g', aggregation: 'count'}, stream);
  assert.equal(observed.result.input_count, 5); assert.equal(observed.result.strategy, 'count');
  assert.deepEqual(observed.result.records, [{g: 'only', count: 5}]);
  record({test: 'count-preserves-all-five', stream, ...observed});
});
test('546 independent partial-error selected pages drain once and deduplicate warning', async () => {
  const pages = [
    {data: {batch: {nodes: [{g: 'only', v: H}, {g: 'only', v: 3}]}}, errors: [{message: 'partial-a'}]},
    {data: {batch: {nodes: [{g: 'only', v: -H}, {g: 'only', v: 2}]}}, errors: [{message: 'partial-b'}]},
    {data: {batch: {nodes: []}}},
  ];
  const observed = await invoke(pages, {x: 'g', y: 'v', aggregation: 'sum', data_path: 'data.batch.nodes'}, true);
  assert.equal(observed.result.input_count, 4); assert.deepEqual(observed.result.records, [{g: 'only', v: 5}]);
  assert.equal(observed.result.warnings.filter(warning => /errors alongside usable data/i.test(warning)).length, 1);
  assert.equal(observed.consumed, 3);
  record({test: 'partial-selected-error-drain', stream: true, consumed_unit: 'pages', ...observed});
});
test('546 independent late fatal error after initialized SUM closes without tail overread', async () => {
  let consumed = 0, iterations = 0, closed = false, tailTouched = false, actualError;
  const source = {[Symbol.asyncIterator]() {
    iterations++; assert.equal(iterations, 1);
    return (async function* () {try {
      for (let i = 0; i < 33; i++) {consumed++; yield Object.freeze({g: 'only', v: i ? 0 : 0.125});}
      consumed++; yield freeze({data: null, errors: [{message: 'terminal'}]});
      tailTouched = true; throw new Error('tail must not be drained after fatal page');
    } finally {closed = true;}})();
  }};
  await assert.rejects(api.normalizeStream(source, {x: 'g', y: 'v', aggregation: 'sum'}), error => {
    actualError = {name: error.name, message: error.message};
    return error instanceof api.ValidationError && /GraphQL response contains errors and no data/.test(error.message);
  });
  assert.equal(consumed, 34); assert.equal(iterations, 1); assert.equal(closed, true); assert.equal(tailTouched, false);
  record({test: 'late-fatal-error-no-tail-overread', consumed, consumed_unit: 'pages', iterations, closed, tailTouched, actual_error: actualError, expected_rejection: true});
});
test('546 independent exact SUM state-budget rejection closes bounded one-pass source', async () => {
  let consumed = 0, iterations = 0, closed = false, actualError;
  const source = {[Symbol.asyncIterator]() {
    iterations++; assert.equal(iterations, 1);
    return (async function* () {try {for (let i = 0; i < 512; i++) {
      consumed++; yield Object.freeze({g: 'q'.repeat(30000) + i, v: 0.125});
    }} finally {closed = true;}})();
  }};
  await assert.rejects(api.normalizeStream(source, {x: 'g', y: 'v', aggregation: 'sum', max_points: 512}), error => {
    actualError = {name: error.name, message: error.message};
    return error instanceof api.ValidationError && /Retained normalized state exceeds 16 MiB/i.test(error.message);
  });
  assert.ok(consumed > 32 && consumed < 512); assert.equal(iterations, 1); assert.equal(closed, true);
  record({test: 'exact-SUM-state-budget', max_input_records: 512, consumed, consumed_unit: 'records', iterations, closed, actual_error: actualError, expected_rejection: true});
});