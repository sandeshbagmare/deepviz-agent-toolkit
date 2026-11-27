import test from 'node:test';
import assert from 'node:assert/strict';
import {normalize, normalizeStream, ValidationError} from '../dist/index.js';

const identity = {kind:'table', aggregation:'none'};

for (const [name, text, records] of [
  ['JSONL', '{"v":1}\n\n{"v":2}', [{v:1},{v:2}]],
  ['numeric scalar', '3', [{index:0,value:3}]],
  ['boolean scalar', 'true', [{index:0,value:true}]],
  ['null scalar', 'null', [{index:0,value:null}]],
  ['string scalar', '"literal"', [{index:0,value:'literal'}]],
  ['BOM-prefixed JSON', '\uFEFF[{"v":1}]', [{v:1}]],
]) {
  test(`automatic text detection preserves ${name} rows`, () => {
    const result = normalize(text, identity);
    assert.deepEqual(result.records, records);
    assert.equal(result.input_count, records.length);
    assert.equal(result.strategy, 'none');
  });
}

test('automatic text detection rejects undelimited garbage instead of dropping it as a CSV header', () => {
  assert.throws(() => normalize('not valid input', identity), ValidationError);
});

test('automatic text detection does not reinterpret malformed JSON as delimited text', () => {
  assert.throws(() => normalize('{"v":1,', identity), ValidationError);
});

test('automatic empty content stays empty', () => {
  assert.deepEqual(normalize(' \n\t', identity).records, []);
});

test('CSV coercion matches Python without discarding all-empty records', () => {
  const result = normalize('g,v\n A, 2 \nB,NaN\nC,1e309\n,\nD,   ', {...identity,format:'csv'});
  assert.deepEqual(result.records, [
    {g:' A',v:2}, {g:'B',v:null}, {g:'C',v:null}, {g:null,v:null}, {g:'D',v:null},
  ]);
  assert.equal(result.input_count, 5);
  assert.ok(result.warnings.some(warning => /non-finite/i.test(warning)));
});

test('CSV quoted-empty and whitespace records are not blank physical lines', () => {
  const result = normalize('v\n""\n\n ', {...identity,format:'csv'});
  assert.deepEqual(result.records, [{v:null},{v:null}]);
  assert.equal(result.input_count, 2);
});

test('CSV rejects whitespace-only column names before coercing cells', () => {
  assert.throws(() => normalize('name,   \nA,2', {...identity,format:'csv'}), /header|column/i);
});

test('a standalone GraphQL edge has the same rows as an edge array', async () => {
  const edge = {cursor:'next',node:{v:2}};
  assert.deepEqual(normalize(edge,identity).records, [{v:2}]);
  assert.deepEqual((await normalizeStream([edge],identity)).records, [{v:2}]);
});

test('standalone null GraphQL edges are skipped with a warning', async () => {
  const result = await normalizeStream([{node:null,cursor:'next'}], identity);
  assert.equal(result.input_count, 0);
  assert.deepEqual(result.records, []);
  assert.ok(result.warnings.some(warning => /null.*node/i.test(warning)));
});

test('stream data_path missing branches warn when another page matches', async () => {
  const result = await normalizeStream([{data:{}},{data:{rows:[{v:2}]}},{data:{}}],
    {...identity,data_path:'data.rows'});
  assert.deepEqual(result.records, [{v:2}]);
  assert.equal(result.input_count, 1);
  assert.ok(result.warnings.some(warning => /missing.*components/i.test(warning)));
});

test('JSONL data_path missing branches are checked across the entire source', () => {
  const result = normalize('{"data":{}}\n{"data":{"rows":[{"v":2}]}}',
    {...identity,format:'jsonl',data_path:'data.rows'});
  assert.deepEqual(result.records, [{v:2}]);
  assert.ok(result.warnings.some(warning => /missing.*components/i.test(warning)));
});

test('stream data_path still rejects a wholly absent path', async () => {
  await assert.rejects(normalizeStream([{data:{}},{data:{}}], {...identity,data_path:'data.rows'}), /data_path/i);
});

test('an empty stream accepts an empty path selection like an empty page array', async () => {
  const result = await normalizeStream([], {...identity,data_path:'data.rows'});
  assert.deepEqual(result.records, []);
  assert.equal(result.input_count, 0);
});

test('CSV data_path selects values before normalization like JSONL data_path', () => {
  const result = normalize('g,v\nA,2\nB,3', {...identity,format:'csv',data_path:'v'});
  assert.deepEqual(result.records, [{index:0,value:2},{index:1,value:3}]);
  assert.equal(result.input_count, 2);
});

test('CSV data_path rejects a wholly absent field instead of returning unselected rows', () => {
  assert.throws(() => normalize('g,v\nA,2', {...identity,format:'csv',data_path:'absent'}), /data_path/i);
});

test('empty streams still validate data_path syntax', async () => {
  await assert.rejects(normalizeStream([], {...identity,data_path:'data..rows'}), /data_path/i);
});

test('mixed numeric and nonnumeric fields are disclosed even without grouped reduction', () => {
  const result = normalize([{v:1},{v:'unknown'},{v:false},{v:null}], identity);
  assert.deepEqual(result.records, [{v:1},{v:'unknown'},{v:false},{v:null}]);
  assert.ok(result.warnings.some(warning => /mixed numeric\/non-numeric.*v/i.test(warning)));
});

test('grouped sums retain small observations under large cancellation', () => {
  const result = normalize([{g:'A',v:1e16},{g:'A',v:1},{g:'A',v:-1e16}],
    {x:'g',y:'v',aggregation:'sum'});
  assert.deepEqual(result.records, [{g:'A',v:1}]);
});

test('the overflow bucket preserves compensated contributions from its evicted group', async () => {
  const rows = [
    ...Array.from({length:9}, (_,g) => ({g,v:0})),
    {g:9,v:1e16}, {g:9,v:1}, {g:10,v:-1e16},
  ];
  const result = await normalizeStream(rows,{x:'g',y:'v',aggregation:'sum',max_points:10});
  assert.deepEqual(result.records.at(-1), {g:'__deepviz_other__',v:1});
  assert.equal(result.records.length, 10);
  assert.equal(result.input_count, 12);
  assert.ok(result.warnings.some(warning => /other bucket/i.test(warning)));
});

test('selected GraphQL paths do not hide partial-error warnings', () => {
  const source = {data:{users:{nodes:[{v:2}]}},errors:[{message:'page incomplete'}]};
  const result = normalize(source,{...identity,data_path:'data.users.nodes'});
  assert.deepEqual(result.records, [{v:2}]);
  assert.equal(result.warnings.filter(warning => /errors alongside usable data/i.test(warning)).length, 1);
});

test('stream selected GraphQL pages preserve partial-error warnings once', async () => {
  const result = await normalizeStream([
    {data:{rows:[{v:1}]},errors:[{message:'partial first page'}]},
    {data:{rows:[{v:2}]},errors:[{message:'partial second page'}]},
  ],{...identity,data_path:'data.rows'});
  assert.deepEqual(result.records, [{v:1},{v:2}]);
  assert.equal(result.warnings.filter(warning => /errors alongside usable data/i.test(warning)).length, 1);
});

test('GraphQL error-only responses cannot become successful records by selecting errors', () => {
  assert.throws(() => normalize({errors:[{message:'unavailable'}]}, {...identity,data_path:'errors'}), /GraphQL.*errors|errors.*data/i);
  assert.throws(() => normalize({errors:[{message:'unavailable'}]}, identity), /GraphQL.*errors|errors.*data/i);
});

test('an empty GraphQL errors array is not a partial failure', () => {
  const result = normalize({data:{nodes:[{v:2}]},errors:[]}, identity);
  assert.deepEqual(result.records, [{v:2}]);
  assert.deepEqual(result.warnings, []);
});

test('wrapper-named record arrays do not discard sibling record identity', async () => {
  for (const key of ['items','records','rows','results','data','pages']) {
    const row = {id:1,[key]:['a','b']};
    const expected = [{id:1,[`${key}.0`]:'a',[`${key}.1`]:'b'}];
    assert.deepEqual(normalize([row],identity).records, expected, key);
    assert.deepEqual((await normalizeStream([row],identity)).records, expected, key);
  }
});

test('ambiguous GraphQL connection siblings require an explicit path', () => {
  const source = {data:{team:{nodes:[{id:1}]},version:1}};
  assert.throws(() => normalize(source,identity), /ambiguous|data_path/i);
  assert.deepEqual(normalize(source,{...identity,data_path:'data.team.nodes'}).records,[{id:1}]);
});
