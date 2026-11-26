import assert from 'node:assert/strict';
import test from 'node:test';
import {buildRendererSpec,normalize,normalizeStream,render,ValidationError} from '../dist/index.js';

// Independent C17-resource-policy oracles, not imports of producer byte counters.
const CELL=65_536,RECORD=262_144,STATE=16_777_216,DASHBOARD=33_554_432;
const utf8=value=>Buffer.byteLength(value,'utf8');
const jsonBytes=value=>utf8(JSON.stringify(value));
const none={aggregation:'none',max_points:1000};
function resourceError(error){
  assert.ok(error instanceof ValidationError,'resource rejection must be a public ValidationError');
  assert.ok(/byte|budget|KiB|MiB|UTF.?8/i.test(error.message),'resource error must identify a byte/resource ceiling');
  assert.ok(/exceed|limit|budget|maximum|too (?:large|big)/i.test(error.message),'resource error must explain the limit');
  return true;
}
function generated(total,rowAt){
  const state={yielded:0,iterations:0,closed:false};
  const input={*[Symbol.iterator](){
    assert.equal(++state.iterations,1,'a streaming source must not be replayed');
    try{for(let i=0;i<total;i++){state.yielded++;yield rowAt(i);}}
    finally{state.closed=true;}
  }};
  return {input,state};
}
async function rejectIncrementally(t,source,spec,lastAllowed){
  try{
    await assert.rejects(normalizeStream(source.input,spec),resourceError);
    assert.ok(source.state.yielded<=lastAllowed,`budget rejection was late: ${source.state.yielded}>${lastAllowed}`);
    assert.equal(source.state.iterations,1);
    assert.equal(source.state.closed,true,'resource rejection must close its source');
  } finally {t.diagnostic(JSON.stringify({source:source.state,last_allowed_yields:lastAllowed}));}
}

for(const [name,value] of [
  ['ASCII','a'.repeat(65_536)],
  ['three-byte BMP','界'.repeat(21_845)+'a'],
  ['four-byte astral','😀'.repeat(16_384)],
]){
  test(`N21 policy: exactly 64KiB ${name} cell survives unchanged`,()=>{
    assert.equal(utf8(value),CELL);
    const result=normalize([{payload:value}],none);
    assert.equal(result.input_count,1);
    assert.equal(result.records.length,1);
    assert.ok(result.records[0].payload===value,'valid text must not be silently truncated');
    assert.doesNotMatch(result.warnings.join(' '),/truncat/i);
  });
  test(`N21 policy: 64KiB+1 ${name} cell rejects rather than truncates`,()=>{
    assert.equal(utf8(value+'z'),65_537);
    assert.throws(()=>normalize([{payload:value+'z'}],none),resourceError);
  });
}

test('N21 policy: an oversized late cell rejects even beyond the reservoir',async t=>{
  const oversized='界'.repeat(22_000);
  assert.equal(utf8(oversized),66_000);
  const source=generated(1000,i=>({payload:i===128?oversized:'safe',seq:i}));
  await rejectIncrementally(t,source,{aggregation:'sample',max_points:10},129);
  assert.equal(source.state.yielded,129,'the 129th row is the first invalid cell');
});

test('N21 policy: a sub-4KiB UTF8 field name is preserved verbatim',()=>{
  const key='鍵'.repeat(1365);
  assert.equal(utf8(key),4095);
  const result=normalize([{[key]:7}],none);
  assert.equal(result.input_count,1);
  assert.equal(Object.keys(result.records[0]).length,1);
  assert.ok(Object.hasOwn(result.records[0],key));
  assert.equal(result.records[0][key],7);
});

for(const [name,key,bytes] of [
  ['ASCII','k'.repeat(65_537),65_537],
  ['multibyte','鍵'.repeat(22_000),66_000],
]) test(`N21 policy: oversized ${name} key rejects before being retained`,()=>{
  assert.equal(utf8(key),bytes);
  assert.ok(bytes>CELL);
  assert.throws(()=>normalize([{[key]:1}],none),resourceError);
});

test('N21 policy: flattening cannot bypass the generated key byte ceiling',()=>{
  const parent='p'.repeat(40_000),child='q'.repeat(40_000);
  assert.equal(utf8(parent+'.'+child),80_001);
  assert.throws(()=>normalize([{[parent]:{[child]:1}}],none),resourceError);
});

test('N21 policy: a safe multibyte flattened key remains usable',()=>{
  const parent='界'.repeat(600),child='鍵'.repeat(700),flat=parent+'.'+child;
  assert.equal(utf8(flat),3901);
  const result=normalize([{[parent]:{[child]:3}}],none);
  assert.equal(result.input_count,1);
  assert.ok(Object.hasOwn(result.records[0],flat));
  assert.equal(result.records[0][flat],3);
});

function boundaryRecord(extra=0){
  // Four single-character keys contribute exactly 29 JSON punctuation/key bytes.
  return {a:'a'.repeat(65_536),b:'b'.repeat(65_536),c:'c'.repeat(65_536),d:'d'.repeat(65_507+extra)};
}
test('N21 policy: an exactly 256KiB flattened JSON record keeps every byte',()=>{
  const row=boundaryRecord();
  assert.equal(jsonBytes(row),RECORD);
  const result=normalize([row],none);
  assert.equal(result.input_count,1);
  assert.equal(result.records.length,1);
  assert.equal(jsonBytes(result.records[0]),262_144);
  for(const field of ['a','b','c','d'])assert.ok(result.records[0][field]===row[field],`field ${field} changed`);
});

test('N21 policy: 256KiB+1 record rejects although every cell fits',()=>{
  const row=boundaryRecord(1);
  assert.equal(jsonBytes(row),262_145);
  assert.ok(Object.values(row).every(value=>utf8(value)<=CELL));
  assert.throws(()=>normalize([row],none),resourceError);
});

for(const [name,value,bytes] of [
  ['backslash','\\'.repeat(40_000),320_029],
  ['NUL','\0'.repeat(12_000),288_029],
]) test(`N21 policy: ${name} JSON escaping counts toward the record ceiling`,()=>{
  const row={a:value,b:value,c:value,d:value};
  assert.ok(utf8(value)<CELL);
  assert.equal(jsonBytes(row),bytes);
  assert.ok(bytes>RECORD);
  assert.throws(()=>normalize([row],none),resourceError);
});

test('N21 policy: mapped null insertion cannot bypass the record ceiling',()=>{
  const fields=['a','b','c','d'].map(letter=>letter.repeat(65_536));
  assert.equal(jsonBytes(Object.fromEntries(fields.map(field=>[field,null]))),262_177);
  const [x,y,color,size]=fields;
  assert.throws(()=>normalize([{}],{...none,x,y,color,size}),resourceError);
});

test('N21 policy: cumulative input bytes do not reject a safe small reservoir',async()=>{
  const payload='界'.repeat(8192);
  assert.equal(utf8(payload),24_576);
  assert.equal(2000*utf8(payload),49_152_000);
  assert.ok(2000*utf8(payload)>STATE);
  const source=generated(2000,i=>({payload,seq:i}));
  const result=await normalizeStream(source.input,{aggregation:'sample',max_points:10});
  assert.deepEqual(source.state,{yielded:2000,iterations:1,closed:true});
  assert.equal(result.input_count,2000);
  assert.equal(result.records.length,10);
  assert.equal(result.strategy,'sample');
  assert.ok(result.records.every(row=>row.payload===payload));
  assert.ok(jsonBytes(result.records)<STATE);
  assert.match(result.warnings.join(' '),/sample/i);
  assert.doesNotMatch(result.warnings.join(' '),/truncat/i);
});

test('N21 policy: retained UTF8 rows reject incrementally, not by UTF16 units',async t=>{
  const payload='界'.repeat(8192),row={payload};
  assert.equal(jsonBytes(row),24_590);
  const lastAllowed=Math.floor(STATE/24_590)+1;
  const source=generated(800,()=>({payload}));
  assert.ok(lastAllowed<800);
  await rejectIncrementally(t,source,{aggregation:'none',max_points:1000},lastAllowed);
});

test('N21 policy: schema names remain charged after reservoir replacement',async t=>{
  const prefix='鍵'.repeat(16_000);
  assert.equal(utf8(prefix),48_000);
  const source=generated(400,i=>({[prefix+String(i).padStart(6,'0')]:i}));
  // Distinct schema keys alone cross 16MiB by this row, independently of row/group overhead.
  const lastAllowed=Math.floor(STATE/48_006)+1;
  assert.ok(lastAllowed<400);
  await rejectIncrementally(t,source,{aggregation:'sample',max_points:10},lastAllowed);
});

test('N21 policy: retained group keys reject before the raw key bytes exceed 16MiB',async t=>{
  const prefix='g'.repeat(60_000);
  const source=generated(400,i=>({bucket:prefix+String(i).padStart(6,'0'),value:1}));
  const lastAllowed=Math.floor(STATE/60_006)+1;
  assert.ok(lastAllowed<400);
  await rejectIncrementally(t,source,{x:'bucket',y:'value',aggregation:'sum',max_points:1000},lastAllowed);
});

test('N21 policy: safe dashboard control preserves counts and UTF8 data',()=>{
  const payload='界'.repeat(100),rows=Array.from({length:32},(_,value)=>({payload,value}));
  const chart={kind:'table',aggregation:'none',max_points:32};
  const artifact=render(rows,{kind:'dashboard',charts:[chart,chart]},'vega');
  assert.equal(artifact.input_count,32);
  assert.equal(artifact.output_count,64);
  assert.equal(artifact.renderer_spec.children.length,2);
  assert.ok(artifact.renderer_spec.children.every(child=>child.normalized.records.every(row=>row.payload===payload)));
  assert.ok(utf8(artifact.html)<DASHBOARD);
  assert.ok(artifact.html.includes(payload));
});

test('N21 policy: combined dashboard rejects over 32MiB before top-level HTML serialization',()=>{
  // Caller-owned input is already allocated; this is a payload contract, not an RSS assertion.
  const payload='界'.repeat(8192),row={payload,value:1};
  assert.equal(jsonBytes(row),24_600);
  const oneChildBytes=512*(24_600+1)+1;
  assert.equal(oneChildBytes,12_595_713);
  assert.ok(oneChildBytes<STATE);
  assert.ok(3*oneChildBytes>DASHBOARD);
  assert.ok(3*512*payload.length<20_000_000,'a UTF16 character cap cannot enforce this UTF8 ceiling');
  const rows=Array.from({length:512},()=>({payload,value:1}));
  const child={kind:'table',aggregation:'none',max_points:512};
  // Public builder has no final HTML-size fallback: all children must share the budget here.
  assert.throws(()=>buildRendererSpec(rows,{kind:'dashboard',charts:[child,child,child]},'vega'),resourceError);
});
