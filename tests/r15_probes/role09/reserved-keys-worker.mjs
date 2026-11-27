import assert from 'node:assert/strict';

function snapshot(root) {
  const seen = new Map();
  const visit = value => {
    if (value === null || typeof value !== 'object' || seen.has(value)) return;
    const descriptors = Object.getOwnPropertyDescriptors(value);
    seen.set(value, {prototype: Object.getPrototypeOf(value), descriptors});
    const prototype = Object.getPrototypeOf(value);
    if (prototype !== null && prototype !== Object.prototype && prototype !== Array.prototype) visit(prototype);
    for (const descriptor of Object.values(descriptors)) if ('value' in descriptor) visit(descriptor.value);
  };
  visit(root);
  return () => {
    for (const [value, before] of seen) {
      assert.equal(Object.getPrototypeOf(value), before.prototype, 'input prototype changed');
      assert.deepEqual(Object.getOwnPropertyDescriptors(value), before.descriptors, 'input own descriptors changed');
    }
  };
}

function fixture(scenario, key) {
  const ordinary = [{id: 'r15-row-A', value: 17}, {id: 'r15-row-B', value: 29}];
  const reserved = JSON.parse(JSON.stringify(ordinary.map((row, i) => Object.fromEntries([
    ...Object.entries(row), [key, `r15-inert-${key}-${i}`],
  ]))));
  const spec = {kind: 'table', aggregation: 'none'};
  if (scenario === 'own-record') return {data: reserved, expected: reserved, spec, policyRejection: true};
  if (scenario === 'own-null-prototype') {
    return {data: reserved.map(row => Object.assign(Object.create(null), row)), expected: reserved, spec, policyRejection: true};
  }
  if (scenario === 'mapped-own-field') {
    return {data: reserved, expected: reserved, spec: {...spec, x: key, y: 'value'}, policyRejection: true};
  }
  if (scenario === 'own-data-path') {
    return {data: Object.fromEntries([[key, ordinary]]), expected: ordinary, spec: {...spec, data_path: key}, policyRejection: true, pages: true};
  }
  if (scenario === 'inherited-data-path') {
    const privatePrototype = Object.fromEntries([[key, ordinary]]);
    const data = Object.assign(Object.create(privatePrototype), {id: 'r15-own-envelope'});
    assert.equal(Object.hasOwn(data, key), false);
    assert.equal(data[key], ordinary);
    return {data, expected: ordinary, spec: {...spec, data_path: key}, mustReject: true, pages: true};
  }
  if (scenario === 'missing-mapped-field') {
    assert.equal(Object.hasOwn(ordinary[0], key), false);
    return {data: ordinary, expected: ordinary, spec: {...spec, x: key, y: 'value'}, mustReject: true};
  }
  if (scenario === 'ordinary') return {data: ordinary, expected: ordinary, spec};
  if (scenario === 'ordinary-null-prototype') {
    return {data: ordinary.map(row => Object.assign(Object.create(null), row)), expected: ordinary, spec};
  }
  if (scenario === 'omitted-spec') return {data: ordinary, expected: ordinary, omitted: true};
  if (scenario === 'null-spec') return {data: ordinary, expected: ordinary, spec: null, mustReject: true};
  throw new Error(`Unknown test fixture ${scenario}`);
}

export async function run(api, candidate) {
  const {normalize, normalizeStream, createTools, ValidationError} = api;
  const data = fixture(candidate.scenario, candidate.key);
  const unchangedInput = snapshot(data.data);
  const unchangedSpec = snapshot(data.spec);
  const prototypeDescriptors = Object.getOwnPropertyDescriptors(Object.prototype);
  const objectPrototypeParent = Object.getPrototypeOf(Object.prototype);
  const summary = {...candidate, pid: process.pid, accepted: false, consumed: 0};
  let actual;
  let productError;
  try {
    if (candidate.route === 'normalize') {
      actual = data.omitted ? normalize(data.data) : normalize(data.data, data.spec);
    } else if (candidate.route === 'stream') {
      async function* records() {
        for (const item of data.pages ? [data.data] : data.data) { summary.consumed++; yield item; }
      }
      actual = data.omitted ? await normalizeStream(records()) : await normalizeStream(records(), data.spec);
    } else {
      const tool = createTools().find(tool => tool.name === 'render_svg');
      assert.ok(tool, 'real public render_svg helper is missing');
      const artifact = await tool.invoke(data.omitted ? {data: data.data} : {data: data.data, spec: data.spec});
      actual = artifact.renderer_spec.normalized;
      summary.artifact_counts = {input: artifact.input_count, output: artifact.output_count};
      assert.equal(artifact.input_count, 2);
      assert.equal(artifact.output_count, 2);
    }
  } catch (error) { productError = error; }
  try {
    unchangedInput();
    unchangedSpec();
    assert.deepEqual(Object.getOwnPropertyDescriptors(Object.prototype), prototypeDescriptors, 'Object.prototype changed');
    assert.equal(Object.getPrototypeOf(Object.prototype), objectPrototypeParent, 'Object.prototype parent changed');
    summary.input_and_global_prototype_unchanged = true;
    if (productError) {
      assert.ok(productError instanceof ValidationError, `unexpected ${productError.name}: ${productError.message}`);
      assert.ok(data.mustReject || data.policyRejection, `positive fixture rejected: ${productError.message}`);
      summary.disposition = data.mustReject ? 'validated-boundary-rejection' : 'explicit-reserved-key-policy-rejection';
      summary.error = {name: productError.name, message: productError.message};
    } else {
      assert.equal(data.mustReject ?? false, false, 'inherited/missing data or explicit null ChartSpec was accepted');
      assert.equal(actual.input_count, 2, 'input count differs from the literal two-row fixture');
      assert.equal(actual.records.length, 2, 'unexpected row loss/reduction');
      assert.deepEqual(JSON.parse(JSON.stringify(actual.records)), data.expected, 'own field/value loss or invented field');
      for (let i = 0; i < data.expected.length; i++) for (const [key, value] of Object.entries(data.expected[i])) {
        assert.equal(Object.hasOwn(actual.records[i], key), true, `own field lost: ${key}`);
        assert.equal(actual.records[i][key], value, `own field changed: ${key}`);
      }
      if (!data.omitted) { assert.equal(actual.strategy, 'none'); assert.deepEqual(actual.warnings, []); }
      if (candidate.route === 'stream') assert.equal(summary.consumed, data.pages ? 1 : 2, 'source not consumed exactly');
      summary.accepted = true;
      summary.disposition = 'literal-own-fields-and-counts-preserved';
      summary.result = {records: actual.records, input_count: actual.input_count, strategy: actual.strategy, warnings: actual.warnings};
    }
    summary.assertions_passed = true;
  } catch (error) { summary.assertions_passed = false; summary.assertion_failure = error.message; }
  process.stdout.write(JSON.stringify(summary));
  if (!summary.assertions_passed) process.exitCode = 1;
}
