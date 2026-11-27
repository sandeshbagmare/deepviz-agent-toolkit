import test from 'node:test';
import assert from 'node:assert/strict';
import {normalize, normalizeStream} from '../dist/index.js';

const CELL = 64 * 1024;
const identity = {kind:'table',aggregation:'none'};

test('ASCII cells at the 64 KiB UTF-8 ceiling are preserved without truncation', () => {
  const text = 'x'.repeat(CELL);
  assert.ok(normalize([{text}],identity).records[0].text === text);
});

test('ASCII cells over 64 KiB reject rather than truncate', () => {
  assert.throws(() => normalize([{text:'x'.repeat(CELL + 1)}],identity), /64.*KiB.*UTF-8/i);
});

test('cell limits count UTF-8 bytes rather than UTF-16 code units', () => {
  const text = '😀'.repeat(CELL / 4);
  assert.ok(normalize([{text}],identity).records[0].text === text);
  assert.throws(() => normalize([{text:text + '😀'}],identity), /64.*KiB.*UTF-8/i);
});

test('field names and flattened paths have the same UTF-8 cell ceiling', () => {
  assert.throws(() => normalize([{['k'.repeat(CELL + 1)]:1}],identity), /64.*KiB.*UTF-8/i);
  assert.throws(() => normalize([{['k'.repeat(CELL)]:{nested:1}}],identity), /64.*KiB.*UTF-8/i);
});

test('CSV headers reject oversized field names even when the file has no data rows', () => {
  assert.equal(normalize('k'.repeat(CELL),{...identity,format:'csv'}).input_count,0);
  assert.throws(() => normalize('k'.repeat(CELL + 1),{...identity,format:'csv'}), /64.*KiB.*UTF-8/i);
});

test('CSV field decoding counts UTF-8 after unquoting and preserves accepted contents', () => {
  const text = '😀'.repeat(CELL / 4);
  assert.ok(normalize(`text\n"${text}"\n`,{...identity,format:'csv'}).records[0].text === text);
  assert.throws(() => normalize(`text\n"${text}😀"\n`,{...identity,format:'csv'}), /64.*KiB.*UTF-8/i);
  const quotes = '"'.repeat(CELL);
  assert.ok(normalize(`text\n"${quotes.replaceAll('"','""')}"\n`,{...identity,format:'csv'}).records[0].text === quotes);
});

test('the 256 KiB flattened-record limit includes JSON field and punctuation bytes', () => {
  // Four empty string fields serialize to 29 ASCII bytes before their contents.
  const row = {a:'x'.repeat(CELL),b:'x'.repeat(CELL),c:'x'.repeat(CELL),d:'x'.repeat(CELL - 29)};
  assert.equal(Buffer.byteLength(JSON.stringify(row),'utf8'), 256 * 1024);
  const actual = normalize([row],identity).records[0];
  assert.ok(Object.keys(row).every(key => actual[key] === row[key]));
  assert.throws(() => normalize([{...row,d:row.d + 'x'}],identity), /record.*256.*KiB/i);
});

test('record accounting includes escaped JSON bytes, not only raw text bytes', () => {
  assert.throws(() => normalize([{a:'"'.repeat(CELL),b:'"'.repeat(CELL)}],identity), /record.*256.*KiB/i);
});

test('retained record state rejects incrementally before consuming a large stream', async () => {
  let consumed = 0;
  const text = 'x'.repeat(CELL);
  async function* rows() {
    for (let id=0;id<1000;id++) { consumed++; yield {id,text}; }
  }
  await assert.rejects(normalizeStream(rows(),{...identity,max_points:1000}), /retained.*16.*MiB/i);
  assert.ok(consumed < 300, `Consumed ${consumed} rows before rejecting`);
});

test('schema keys count against retained state even when most rows are sampled out', async () => {
  let consumed = 0;
  async function* rows() {
    const prefix = 'k'.repeat(CELL - 8);
    for (let id=0;id<1000;id++) { consumed++; yield {[`${prefix}${id}`]:id}; }
  }
  await assert.rejects(normalizeStream(rows(),{...identity,max_points:10}), /retained.*16.*MiB/i);
  assert.ok(consumed < 300, `Consumed ${consumed} schema keys before rejecting`);
});

test('grouping keys and group result state both count against retained bytes', async () => {
  let consumed = 0;
  async function* rows() {
    const prefix = 'g'.repeat(CELL - 8);
    for (let id=0;id<500;id++) { consumed++; yield {g:`${prefix}${id}`,v:1}; }
  }
  await assert.rejects(normalizeStream(rows(),{x:'g',y:'v',aggregation:'sum',max_points:1000}), /retained.*16.*MiB/i);
  assert.ok(consumed < 200, `Consumed ${consumed} groups before rejecting`);
});

test('small reservoirs still process all large-cell source rows without truncation', async () => {
  const text = 'x'.repeat(CELL);
  async function* rows() { for (let id=0;id<1000;id++) yield {id,text}; }
  const result = await normalizeStream(rows(),{...identity,max_points:10});
  assert.equal(result.input_count,1000);
  assert.equal(result.records.length,10);
  assert.equal(result.strategy,'sample');
  assert.ok(result.records.every(row => row.text === text));
  assert.ok(result.warnings.every(warning => !/truncat/i.test(warning)));
});
