import test from 'node:test';
import assert from 'node:assert/strict';
import {normalize, normalizeStream, buildRendererSpec} from '../dist/index.js';

test('N17: UTF-16 text truncation is disclosed, not assumed byte safety',()=>{
  const result=normalize([{label:'\u{1f642}'.repeat(10000),value:1}],{kind:'table',aggregation:'none'});
  assert.equal(result.records[0].label.length,10000);
  assert.equal(Buffer.byteLength(result.records[0].label),20000);
  assert.ok(result.warnings.some(warning=>warning.includes('truncated')));
  console.log(JSON.stringify({probe:'N17 UTF-8 bytes after text truncation',bytes:Buffer.byteLength(JSON.stringify(result.records)),warnings:result.warnings}));
});

test('N17: wide/deep records and schema drift are rejected',()=>{
  assert.throws(()=>normalize([Object.fromEntries(Array.from({length:1025},(_,i)=>['k'+i,i]))],{kind:'table'}),/1024 fields/);
  assert.throws(()=>normalize([{a:'x'.repeat(10000),b:'x'.repeat(10000),c:'x'.repeat(10000),d:'x'.repeat(10000),e:'x'.repeat(10000),f:'x'.repeat(10000),g:'x'.repeat(10000),h:'x'.repeat(10000),i:'x'.repeat(10000),j:'x'.repeat(10000)}],{kind:'table'}),/100,000/);
  let deep={v:1};for(let i=0;i<66;i++)deep={next:deep};
  assert.throws(()=>normalize([deep],{kind:'table'}),/depth/);
  const cycle={};cycle.next=cycle;
  assert.throws(()=>normalize([cycle],{kind:'table'}),/Cyclic/);
  assert.throws(()=>normalize([Object.fromEntries(Array.from({length:600},(_,i)=>['k'+i,i])),Object.fromEntries(Array.from({length:600},(_,i)=>['k'+(600+i),i]))],{kind:'table'}),/schema exceeds 1024/);
});

test('N17: high-cardinality async source keeps exact total including repeats',async()=>{
  async function* rows(){for(let i=0;i<1000;i++)yield {g:String(i%100),v:i+1};}
  const result=await normalizeStream(rows(),{x:'g',y:'v',aggregation:'sum',max_points:10});
  assert.equal(result.input_count,1000);
  assert.equal(result.records.reduce((total,row)=>total+row.v,0),500500);
  assert.deepEqual(result.records[0],{g:'0',v:4510});
  assert.equal(result.records.length,10);
  assert.ok(result.warnings.some(warning=>warning.includes('cardinality')));
});

test('N17: dashboard serializes retained data repeatedly; observation not acceptance',()=>{
  const source=Array.from({length:10},(_,i)=>({label:'x'.repeat(4000)+i,v:i+1}));
  const result=buildRendererSpec(source,{kind:'dashboard',charts:Array.from({length:24},()=>({kind:'bar',x:'label',y:'v',aggregation:'none',max_points:10}))},'echarts');
  const sourceBytes=Buffer.byteLength(JSON.stringify(source));
  const retainedBytes=result.children.reduce((sum,child)=>sum+Buffer.byteLength(JSON.stringify(child.normalized.records)),0);
  assert.equal(result.children.length,24);
  assert.equal(result.children.reduce((sum,child)=>sum+child.normalized.records.length,0),240);
  assert.equal(retainedBytes,24*sourceBytes);
  console.log(JSON.stringify({probe:'N17 dashboard fanout',sourceBytes,retainedBytes,children:24,totalRows:240}));
});
