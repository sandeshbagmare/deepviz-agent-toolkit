// Public API consumer only. No accumulator implementation or oracle algorithm.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = process.env.R16_SOURCE_ROOT;
assert.ok(root, 'Set R16_SOURCE_ROOT to the clean committed ec9 source consumer');
const entry = resolve(root, 'packages/deepviz/dist/index.js');
const { normalize, normalizeStream } = await import(pathToFileURL(entry).href);
const bits = value => value === null ? null : (() => {
  assert.equal(typeof value, 'number');
  assert.ok(Number.isFinite(value), 'Public output must be finite or explicit null');
  const buffer = Buffer.alloc(8);
  buffer.writeDoubleBE(value);
  return buffer.toString('hex');
})();
const inputs = JSON.parse(readFileSync(0, 'utf8'));
const results = [];
for (const item of inputs) {
  const array = normalize(item.rows, item.spec);
  let syncConsumed = 0, syncIterations = 0, syncExhausted = false;
  const sync = {
    *[Symbol.iterator]() {
      assert.equal(++syncIterations, 1, 'Sync input is one-pass');
      for (const row of item.rows) { syncConsumed++; yield row; }
      syncExhausted = true;
    },
  };
  const syncResult = await normalizeStream(sync, item.spec);
  let asyncConsumed = 0, asyncIterations = 0, asyncExhausted = false;
  const async = {
    async *[Symbol.asyncIterator]() {
      assert.equal(++asyncIterations, 1, 'Async input is one-pass');
      for (const row of item.rows) { asyncConsumed++; yield row; }
      asyncExhausted = true;
    },
  };
  const asyncResult = await normalizeStream(async, item.spec);
  const outputs = [array, syncResult, asyncResult].map(result => ({
    result,
    bits: result.records.map(row => bits(row.v)),
  }));
  results.push({
    name: item.name,
    input_bits: item.rows.map(row => bits(row.v)),
    outputs,
    syncConsumed, syncIterations, syncExhausted,
    asyncConsumed, asyncIterations, asyncExhausted,
  });
}
console.log(JSON.stringify({
  compiled_index_sha256: createHash('sha256').update(readFileSync(entry)).digest('hex'),
  compiled_normalize_sha256: createHash('sha256').update(readFileSync(resolve(root, 'packages/deepviz/dist/normalize.js'))).digest('hex'),
  results,
}));
