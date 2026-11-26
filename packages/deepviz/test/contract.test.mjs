import test from 'node:test';
import assert from 'node:assert/strict';
import { validateSpec, normalize, normalizeStream } from '../dist/index.js';

test('spec defaults and dashboard validation match the Python contract', () => {
  assert.deepEqual(validateSpec({}), {
    version: 1, kind: 'bar', title: 'Visualization', description: '',
    x: null, y: null, color: null, size: null, data_path: null,
    format: 'auto', aggregation: 'auto', max_points: 2000,
    width: 900, height: 520, theme: 'light', charts: [], columns: 2,
  });
  for (const spec of [{kind:'unknown'}, {max_points:9}, {max_points:100001}, {width:239},
    {height:4097}, {columns:7}, {version:2}, {script:'alert(1)'}, {title:'x'.repeat(501)},
    {charts:[{}]}, {charts:null}, {kind:'dashboard'}, {kind:'dashboard',charts:[{kind:'dashboard',charts:[{}]}]}]) {
    assert.throws(() => validateSpec(spec));
  }
  assert.equal(validateSpec({kind:'dashboard',charts:[{kind:'line'}]}).charts[0].kind, 'line');
});

test('a single nested record is flattened, never mistaken for a wrapper', () => {
  assert.deepEqual(normalize({id:1,profile:{name:'Ada'}}).records,[{id:1,'profile.name':'Ada'}]);
  assert.deepEqual(normalize({id:1,tags:['admin','staff']},{aggregation:'none'}).records,[{id:1,'tags.0':'admin','tags.1':'staff'}]);
  assert.throws(()=>normalize([{'a.b':1,a:{b:2}}]),/collid/i);
});

test('GraphQL null nodes are skipped, malformed edges fail, and GraphQL errors are not hidden',()=>{
  const result=normalize({data:{users:{edges:[{node:null},{node:{x:'A',y:2}}]}}},{aggregation:'none'});
  assert.deepEqual(result.records,[{x:'A',y:2}]);
  assert.equal(result.input_count,1);
  assert.ok(result.warnings.length);
  assert.throws(()=>normalize({edges:[{cursor:'bad'}]}),/edge|node/i);
  assert.throws(()=>normalize({data:null,errors:[{message:'failed'}]}),/GraphQL|errors/i);
  assert.ok(normalize({data:{nodes:[{x:1}]},errors:[{message:'partial'}]}).warnings.length);
});

test('data_path supports numeric indices and warns for missing page branches like Python',()=>{
  assert.deepEqual(normalize({data:{rows:[{x:1},{x:2}]}},{data_path:'data.rows.1',aggregation:'none'}).records,[{x:2}]);
  const result=normalize({pages:[{data:{rows:[{x:1}]}},{data:{}},{data:{rows:[{x:2}]}}]},{data_path:'pages.data.rows',aggregation:'none'});
  assert.deepEqual(result.records,[{x:1},{x:2}]);
  assert.ok(result.warnings.length);
  assert.throws(()=>normalize({data:{}},{data_path:'data.rows'}),/data_path/i);
});

test('scalar rows have index/value fields and overflow remains non-finite until final null conversion',()=>{
  assert.deepEqual(normalize([1,2],{aggregation:'none'}).records,[{index:0,value:1},{index:1,value:2}]);
  const result=normalize([{x:'A',y:1e308},{x:'A',y:1e308},{x:'A',y:1}],{x:'x',y:'y',aggregation:'sum'});
  assert.deepEqual(result.records,[{x:'A',y:null}]);
  assert.ok(result.warnings.length);
});

test('normalization retains a finite character budget rather than only a row limit', () => {
  const row=Object.fromEntries(Array.from({length:1000},(_,i)=>[`field${i}`,'x'.repeat(10000)]));
  assert.throws(()=>normalize([row]),/budget/i);
});

test('normalizes records, columns, nested JSON, GraphQL edges and page lists without row loss', () => {
  assert.deepEqual(normalize([{a:1,profile:{name:'Ada'}}]).records, [{a:1,'profile.name':'Ada'}]);
  assert.deepEqual(normalize({x:['a','b'],y:[2,3]}).records, [{x:'a',y:2},{x:'b',y:3}]);
  assert.deepEqual(normalize({data:{users:{edges:[{node:{x:'a',y:2}},{node:{x:'b',y:3}}]}}}).records,
    [{x:'a',y:2},{x:'b',y:3}]);
  assert.deepEqual(normalize([{data:{users:{nodes:[{x:1}]}}},{data:{users:{nodes:[{x:2}]}}}]).records, [{x:1},{x:2}]);
  assert.deepEqual(normalize({pages:[{data:{users:[{x:1}]}},{data:{users:[{x:2}]}}]}, {data_path:'pages.data.users'}).records, [{x:1},{x:2}]);
  assert.throws(() => normalize({x:[1,2],y:[1]}), /length/i);
  assert.throws(() => normalize({users:[{id:1}],orders:[{id:2}]}), /ambiguous/i);
});

test('quoted CSV, TSV, JSON and JSONL preserve values and reject malformed rows', () => {
  assert.deepEqual(normalize('name,note,value\r\n"A, B","first\nsecond",2\r\nC,"a ""quote""",3', {format:'csv',aggregation:'none'}).records,
    [{name:'A, B',note:'first\nsecond',value:2},{name:'C',note:'a "quote"',value:3}]);
  assert.deepEqual(normalize('x\ty\na\t2',{format:'tsv'}).records,[{x:'a',y:2}]);
  assert.deepEqual(normalize('[{"x":1}]',{format:'json'}).records,[{x:1}]);
  assert.deepEqual(normalize('{"x":1}\n\n{"x":2}',{format:'jsonl'}).records,[{x:1},{x:2}]);
  assert.throws(() => normalize('x,x\n1,2',{format:'csv'}), /header/i);
  assert.throws(() => normalize('x,y\n1',{format:'csv'}), /column/i);
  assert.throws(() => normalize('x\n"never closed',{format:'csv'}), /quote/i);
  assert.throws(() => normalize('bytes',{format:'parquet'}), /adapter|unsupported/i);
});

test('deterministic reservoir sampling keeps a strict row bound and accurate metadata', () => {
  const data = Array.from({length:10000},(_,x)=>({x,y:x}));
  const a = normalize(data,{max_points:10,aggregation:'sample'});
  assert.deepEqual(a, normalize(data,{max_points:10,aggregation:'sample'}));
  assert.equal(a.records.length,10);
  assert.equal(a.input_count,10000);
  assert.equal(a.strategy,'sample');
  assert.ok(a.records.some(row=>row.x>5000));
  assert.ok(a.warnings.length);
  const bounded=normalize(data,{max_points:10,aggregation:'none'});
  assert.equal(bounded.records.length,10);
  assert.equal(bounded.strategy,'sample');
  assert.ok(bounded.warnings.length);
});

test('group aggregation agrees with Python including missing measures and overflow bucket', () => {
  const data = [{x:'a',y:2},{x:'b',y:3},{x:'a',y:4}];
  assert.deepEqual(normalize(data,{x:'x',y:'y',aggregation:'sum'}).records,[{x:'a',y:6},{x:'b',y:3}]);
  assert.deepEqual(normalize(data,{x:'x',y:'y',aggregation:'mean'}).records,[{x:'a',y:3},{x:'b',y:3}]);
  assert.deepEqual(normalize(data,{x:'x',aggregation:'count'}).records,[{x:'a',count:2},{x:'b',count:1}]);
  assert.deepEqual(normalize(data,{x:'x',y:'y',aggregation:'min'}).records,[{x:'a',y:2},{x:'b',y:3}]);
  assert.deepEqual(normalize(data,{x:'x',y:'y',aggregation:'max'}).records,[{x:'a',y:4},{x:'b',y:3}]);
  const excluded=normalize([{x:'a',y:'bad'},{x:'a',y:null}],{x:'x',y:'y',aggregation:'sum'});
  assert.deepEqual(excluded.records,[{x:'a',y:null}]);
  assert.ok(excluded.warnings.length);
  const overflow=normalize(Array.from({length:12},(_,x)=>({x,y:x})),{x:'x',y:'y',aggregation:'sum',max_points:10});
  assert.deepEqual(overflow.records.slice(-1),[{x:'__deepviz_other__',y:30}]);
  assert.equal(overflow.records.length,10);
  assert.ok(overflow.warnings.length);
});

test('async records are consumed incrementally and agree with sync reduction', async () => {
  let consumed=0;
  async function* rows() { for(let x=0;x<100000;x++) { consumed++; yield {x,y:x}; } }
  const result=await normalizeStream(rows(),{max_points:10,aggregation:'sample'});
  assert.equal(consumed,100000);
  assert.equal(result.input_count,100000);
  assert.equal(result.records.length,10);
  assert.deepEqual(result,normalize(Array.from({length:100000},(_,x)=>({x,y:x})),{max_points:10,aggregation:'sample'}));
});

test('unsafe keys, cycles, non-finite values and oversized fields have explicit behavior', () => {
  assert.throws(() => normalize(JSON.parse('[{"__proto__":{"polluted":true}}]')), /unsafe/i);
  assert.throws(() => normalize([{x:1}],{data_path:'__proto__.x'}), /unsafe/i);
  const cycle={}; cycle.self=cycle;
  assert.throws(() => normalize([cycle]), /cyclic|depth/i);
  const result=normalize([{x:NaN,y:Infinity,text:'a'.repeat(20000)}],{aggregation:'none'});
  assert.equal(result.records[0].x,null);
  assert.equal(result.records[0].y,null);
  assert.ok(result.records[0].text.length<=10000);
  assert.ok(result.warnings.length);
  assert.equal({}.polluted,undefined);
});

test('Python categorical auto semantics sum duplicates or count when there is no measure',()=>{
  assert.deepEqual(normalize([{x:'A',y:1},{x:'A',y:2}],{kind:'bar',x:'x',y:'y'}).records,[{x:'A',y:3}]);
  assert.deepEqual(normalize([{x:'A'},{x:'A'},{x:'B'}],{kind:'bar',x:'x'}).records,[{x:'A',count:2},{x:'B',count:1}]);
  assert.equal(normalize([{x:'A',y:1}],{kind:'bar',x:'x',y:'y'}).strategy,'sum');
  const result=normalize([{x:'A',y:1},{x:'A',y:null},{x:'A'},{x:'A',y:5}],{x:'x',y:'y',aggregation:'mean'});
  assert.deepEqual(result.records,[{x:'A',y:3}]);
  assert.ok(result.warnings.length);
  assert.throws(()=>normalize([{x:'A'}],{x:'x',y:'absent'}),/missing/i);
  assert.throws(()=>normalize([{x:1}],{x:'x',y:'x',aggregation:'sum'}),/group/i);
});

test('heatmap reductions match Python: coordinates group together and color is the measure',()=>{
  const data=[{x:'Mon',y:'AM',value:1},{x:'Mon',y:'AM',value:2},{x:'Tue',y:'AM',value:4}];
  assert.deepEqual(normalize(data,{kind:'heatmap',x:'x',y:'y',color:'value'}).records,[{x:'Mon',y:'AM',value:3},{x:'Tue',y:'AM',value:4}]);
  assert.deepEqual(normalize(data,{kind:'heatmap',x:'x',y:'y'}).records,[{x:'Mon',y:'AM',count:2},{x:'Tue',y:'AM',count:1}]);
  assert.throws(()=>normalize(data,{kind:'heatmap',x:'x',y:'y',aggregation:'sum'}),/color|measure/i);
});
