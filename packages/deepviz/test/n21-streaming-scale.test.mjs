import assert from 'node:assert/strict';
import {mkdtemp,readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import test from 'node:test';
import {exactSum,oneShotRecords,runScaleCase} from '../scripts/verify-streaming-scale.mjs';

const {normalizeStream,renderStream,ValidationError}=await import(process.env.N21_PACKAGE_ENTRY
  ?pathToFileURL(resolve(process.env.N21_PACKAGE_ENTRY)).href:new URL('../dist/index.js',import.meta.url).href);

test('N21 independent integer oracle and single-use source reject replay',async()=>{
  assert.equal(exactSum(10),55n);
  assert.equal(exactSum(10_000_000),50_000_005_000_000n);
  const {source,stats}=oneShotRecords(10);
  const actual=[];
  for await(const row of source)actual.push(row.value);
  assert.deepEqual(actual,[1,2,3,4,5,6,7,8,9,10]);
  assert.deepEqual(stats,{iterations:1,consumed:10,completed:true});
  assert.throws(()=>source[Symbol.iterator](),/replay/);
});

test('N21 measured public streaming sum and sample cases assert real consumption',async()=>{
  const outputDir=await mkdtemp(join(tmpdir(),'deepviz-n21-unit-'));
  for(const mode of ['sum','sample']){
    const result=await runScaleCase({size:1000,mode,outputDir});
    assert.equal(result.input_count,1000);
    assert.equal(result.consumed,1000);
    assert.equal(result.iterations,1);
    assert.equal(result.completed,true);
    assert.equal(result.output_count,mode==='sum'?8:64);
    assert.ok(result.sampled_peak_heap_bytes>=result.baseline_heap_bytes);
    assert.ok(result.sampled_peak_rss_bytes>=result.baseline_rss_bytes);
    if(mode==='sum')assert.match(await readFile(result.html_path,'utf8'),/<svg/);
  }
});

test('N21 high cardinality conserves integer sum in a disclosed bounded other bucket',async()=>{
  const {source,stats}=oneShotRecords(10_000,{unique:true});
  const result=await normalizeStream(source,{kind:'bar',x:'group',y:'value',aggregation:'sum',max_points:10});
  assert.equal(stats.consumed,10_000);
  assert.equal(result.input_count,10_000);
  assert.equal(result.records.length,10);
  assert.equal(result.records.reduce((sum,row)=>sum+BigInt(row.value),0n),exactSum(10_000));
  for(let i=0;i<9;i++)assert.deepEqual(result.records[i],{group:`g${i}`,value:i+1});
  assert.match(result.records[9].group,/^__deepviz_other__/);
  assert.match(result.warnings.join(' '),/cardinality.*other bucket/);
});

test('N21 numeric controls exclude booleans/text/null and warn for nonfinite values',async()=>{
  const values=[1,2,NaN,Infinity,-Infinity,null,'7',true];
  const result=await normalizeStream(values.map(value=>({group:'a',value})),{x:'group',y:'value',aggregation:'sum'});
  assert.equal(result.input_count,8);
  assert.deepEqual(result.records,[{group:'a',value:3}]);
  assert.match(result.warnings.join(' '),/Non-finite/);
  assert.match(result.warnings.join(' '),/Non-numeric/);
});

test('N21 projection and reduction happen before renderer serialization',async()=>{
  let consumed=0;
  const forbidden='N21_DO_NOT_SERIALIZE_SOURCE_PAYLOAD';
  function* source(){for(let i=0;i<10_000;i++){consumed++;yield {group:`g${i%8}`,value:i+1,unused:forbidden.repeat(32)};}}
  const result=await renderStream(source(),{x:'group',y:'value',aggregation:'sum',max_points:10},'svg');
  assert.equal(consumed,10_000);
  assert.equal(result.input_count,10_000);
  assert.equal(result.output_count,8);
  assert.equal(result.renderer_spec.normalized.records.reduce((sum,row)=>sum+BigInt(row.value),0n),exactSum(10_000));
  assert.ok(!result.html.includes(forbidden));
  assert.ok(Buffer.byteLength(result.html)<100_000);
});

test('N21 invalid spec rejects without consuming a single source row',async()=>{
  const {source,stats}=oneShotRecords(10);
  await assert.rejects(normalizeStream(source,{max_points:0}),ValidationError);
  assert.equal(stats.iterations,0);
  assert.equal(stats.consumed,0);
});

test('N21 input failures reject instead of reporting a silently truncated success',async()=>{
  async function* source(){yield {group:'a',value:1};throw new Error('N21 sentinel source failure');}
  await assert.rejects(normalizeStream(source(),{x:'group',y:'value',aggregation:'sum'}),/N21 sentinel source failure/);
});

test('N21 genuine asynchronous one-shot input is consumed once through completion',async()=>{
  let consumed=0;
  async function* source(){for(let i=1;i<=1000;i++){consumed++;yield {group:'a',value:i};}}
  const result=await normalizeStream(source(),{x:'group',y:'value',aggregation:'sum'});
  assert.equal(consumed,1000);
  assert.equal(result.input_count,1000);
  assert.deepEqual(result.records,[{group:'a',value:500_500}]);
});

test('N21 finite sum overflow stays warned null instead of a nonfinite payload',async()=>{
  const result=await normalizeStream([{group:'a',value:1e308},{group:'a',value:1e308}],{x:'group',y:'value',aggregation:'sum'});
  assert.deepEqual(result.records,[{group:'a',value:null}]);
  assert.match(result.warnings.join(' '),/Non-finite/);
  assert.ok(!JSON.stringify(result.records).includes('Infinity'));
});

test('N21 resource ruling preserves a valid sub-64KiB string without truncation',async()=>{
  const text='x'.repeat(20_000);
  const result=await normalizeStream([{text}],{kind:'table',aggregation:'none'});
  assert.equal(result.records[0].text.length,20_000);
  assert.ok(result.records[0].text===text,'the entire caller string must be preserved');
  assert.deepEqual(result.warnings,[]);
});

test('N21 resource ruling rejects over-64KiB UTF8 cells and over-256KiB records',async()=>{
  await assert.rejects(normalizeStream([{text:'€'.repeat(22_000)}],{kind:'table'}),error=>error instanceof ValidationError&&/byte|KiB|UTF-8/i.test(error.message));
  const wide=Object.fromEntries(Array.from({length:5},(_,i)=>[`field${i}`,'x'.repeat(60_000)]));
  await assert.rejects(normalizeStream([wide],{kind:'table'}),error=>error instanceof ValidationError&&/byte|KiB/i.test(error.message));
});

test('N21 retained UTF8 budget aborts a safe wide stream incrementally before 1500 rows',async()=>{
  let consumed=0;
  function* source(){for(let i=0;i<10_000;i++){consumed++;yield {seq:i,text:'€'.repeat(4000)};}}
  await assert.rejects(normalizeStream(source(),{kind:'table',aggregation:'none',max_points:10_000}),error=>error instanceof ValidationError&&/retained|budget|MiB/i.test(error.message));
  assert.ok(consumed<1500,`byte ceiling must reject before consuming the whole input, consumed ${consumed}`);
});
