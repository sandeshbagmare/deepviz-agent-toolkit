import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {before, test} from 'node:test';

const source=resolve(process.env.DEEPVIZ_R16_SOURCE);
const expectedCommit=process.env.DEEPVIZ_R16_EXPECTED_COMMIT??'ec9f669eff28cd5351da142765b7755e3b2f484f';
const {normalize,normalizeStream}=await import(pathToFileURL(join(source,'packages/deepviz/dist/index.js')).href);
before(()=>{
  assert.equal(execFileSync('git',['-C',source,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),expectedCommit);
  const relative='packages/deepviz/src/normalize.ts';
  assert.deepEqual(readFileSync(join(source,relative)),execFileSync('git',['-C',source,'show',`HEAD:${relative}`]));
});

const tiny=Number.MIN_VALUE;
// These are literal mathematical means of the finite binary64 fixtures, not reducer-derived expectations.
const meanCases=[
  ['split-subnormal-positive',[1,tiny,-1,tiny,tiny],tiny],
  ['split-subnormal-negative',[-1,-tiny,1,-tiny,-tiny],-tiny],
  ['overflow-then-tiny-tail',[1e308,1e308,-1e308,-1e308,4*tiny],tiny],
  ['late-overflow-after-prefix',[...Array(32).fill(8*tiny),1e308,1e308,-1e308,-1e308],7*tiny],
  ['constant-subnormal-control',Array(5).fill(tiny),tiny],
  ['tie-even-subnormal-control',[tiny,2*tiny],2*tiny],
  ['half-to-zero-control',[0,tiny],0],
  ['late-wide-numerator-control',[...Array(32).fill(0),1e308,1e308],5.882352941176471e306],
];
for(const [name,values,expected] of meanCases)for(const stream of [false,true]) {
  test(`exact finite mean ${name} ${stream?'async-records':'records'}`,async()=>{
    const rows=values.map(v=>({g:'only',v}));
    const spec={kind:'bar',x:'g',y:'v',aggregation:'mean',max_points:10};
    async function* records(){yield* rows;}
    const result=stream?await normalizeStream(records(),spec):normalize(rows,spec);
    assert.equal(result.input_count,values.length);
    assert.equal(result.strategy,'mean');
    assert.deepEqual(result.warnings,[]);
    assert.ok(result.records.every(row=>typeof row.v==='number' && Number.isFinite(row.v)));
    assert.deepEqual(result.records,[{g:'only',v:expected}],`${name}: representable finite mean rounded away`);
    assert.deepEqual(JSON.parse(JSON.stringify(result.records)),result.records);
  });
}
for(const name of ['rows','records','items','results','data'])for(const mapped of [false,true]) {
  test(`scalar column ${name} ${mapped?'explicit-y':'named-column'}`,()=>{
    const result=normalize({[name]:[1,2]},{kind:'table',aggregation:'none',max_points:10,...(mapped?{y:name}:{})});
    assert.equal(result.input_count,2);
    assert.equal(result.strategy,'none');
    assert.deepEqual(result.warnings,[]);
    assert.deepEqual(result.records,[{[name]:1},{[name]:2}]);
  });
}
const controls=[
  ['record-wrapper',{rows:[{v:1},{v:2}]},{y:'v'},[{v:1},{v:2}]],
  ['explicit-scalar-array-path',{rows:[1,2]},{data_path:'rows',y:'value'},[{index:0,value:1},{index:1,value:2}]],
  ['custom-scalar-column',{payload:[1,2]},{y:'payload'},[{payload:1},{payload:2}]],
  ['two-explicit-columns',{rows:[1,2],quality:[3,4]},{x:'rows',y:'quality'},[{rows:1,quality:3},{rows:2,quality:4}]],
  ['explicit-column-object-path',{outer:{payload:[1,2]}},{data_path:'outer',y:'payload'},[{payload:1},{payload:2}]],
];
for(const [name,data,spec,expected] of controls)test(`valid path/column control ${name}`,()=>{
  const result=normalize(data,{kind:'table',aggregation:'none',max_points:10,...spec});
  assert.deepEqual(result.records,expected);
  assert.equal(result.input_count,2);
  assert.equal(result.strategy,'none');
  assert.deepEqual(result.warnings,[]);
});
