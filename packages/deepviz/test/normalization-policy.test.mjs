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

test('generic column arrays preserve their field names when their cells are objects', () => {
  assert.deepEqual(normalize({payload:[{id:1},{id:2}]},identity).records,[{'payload.id':1},{'payload.id':2}]);
  assert.throws(() => normalize({users:[{id:1}],orders:[{id:2}]},identity), /ambiguous.*data_path/i);
});

test('reserved column names cannot discard their sibling column values', () => {
  for(const source of [{nodes:[1,2],v:[3,4]},{v:[3,4],nodes:[1,2]}]) {
    assert.deepEqual(normalize(source,identity).records,[{nodes:1,v:3},{nodes:2,v:4}]);
  }
});

test('single scalar-array columns keep names even when they resemble wrappers', () => {
  for(const key of ['items','rows','records','results','data','nodes']) {
    assert.deepEqual(normalize({[key]:[1,2]},identity).records,[{[key]:1},{[key]:2}]);
  }
});

test('records in lists retain wrapper-named arrays as nested record fields', async () => {
  const rows = [{items:['a','b']}];
  const expected = [{'items.0':'a','items.1':'b'}];
  assert.deepEqual(normalize(rows,identity).records,expected);
  assert.deepEqual((await normalizeStream(rows,identity)).records,expected);
});

test('ambiguous GraphQL siblings reject independently of object key order', () => {
  for(const source of [{version:1,team:{nodes:[{id:1}]}},{team:{nodes:[{id:1}]},version:1}]) {
    assert.throws(() => normalize(source,identity), /ambiguous.*(?:GraphQL|data_path)/i);
    assert.deepEqual(normalize(source,{...identity,data_path:'team.nodes'}).records,[{id:1}]);
  }
});

test('unknown mapping wrappers require a path instead of stripping parent identity', () => {
  const source = {payload:{rows:[{id:1}]}};
  assert.throws(() => normalize(source,identity), /(?:ambiguous|custom).*data_path/i);
  assert.deepEqual(normalize(source,{...identity,data_path:'payload.rows'}).records,[{id:1}]);
});

test('an all-null GraphQL nodes connection is skipped rather than inferred as a column', () => {
  const result = normalize({nodes:[null]},identity);
  assert.equal(result.input_count,0);
  assert.deepEqual(result.records,[]);
  assert.ok(result.warnings.some(warning => /null.*nodes.*skipped/i.test(warning)));
});
