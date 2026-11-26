import test from 'node:test';
import assert from 'node:assert/strict';
import {normalize, normalizeStream} from '../dist/index.js';

const identity = {kind:'table',aggregation:'none'};

for (const format of ['auto','json','jsonl']) {
  test(`${format} rejects repeated encoded object keys before overwrite`, () => {
    assert.throws(() => normalize('{"x":1,"x":2}',{...identity,format}), /duplicate.*(?:JSON|object).*key/i);
  });
}

test('nested encoded objects reject duplicate keys at every depth', () => {
  assert.throws(() => normalize('{"record":{"x":1,"x":2}}',identity), /duplicate.*key/i);
});

test('encoded key escapes cannot disguise a duplicate property', () => {
  assert.throws(() => normalize(String.raw`{"x":1,"\u0078":2}`,identity), /duplicate.*key/i);
});

test('JSONL checks duplicates on later rows without confusing separate row keys', () => {
  assert.throws(() => normalize('{"x":1}\n{"x":2,"x":3}',{...identity,format:'jsonl'}), /duplicate.*key/i);
  assert.deepEqual(normalize('{"x":1}\n{"x":2}',identity).records,[{x:1},{x:2}]);
});

test('JSON structural-looking text does not create false duplicate keys', () => {
  const row = {x:'},"x":3, { [ \\ "',nested:{x:2},other:{x:3}};
  assert.deepEqual(normalize(JSON.stringify([row]),identity).records,[{x:row.x,'nested.x':2,'other.x':3}]);
});

test('JSON numeric category identity is canonical while booleans and strings stay distinct', async () => {
  const rows = [{g:1,v:2},{g:1.0,v:3},{g:true,v:4},{g:'1',v:5}];
  const spec = {x:'g',y:'v',aggregation:'sum'};
  const expected = [{g:1,v:5},{g:true,v:4},{g:'1',v:5}];
  assert.deepEqual(normalize(rows,spec).records,expected);
  assert.deepEqual((await normalizeStream(rows,spec)).records,expected);
});
