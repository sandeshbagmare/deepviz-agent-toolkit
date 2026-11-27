import test from 'node:test';
import assert from 'node:assert/strict';
import {buildRendererSpec,renderStream} from '../dist/index.js';

const wideRows=()=>Array.from({length:110},(_,x)=>({x,y:x+1,...Object.fromEntries(
  Array.from({length:6},(_,i)=>[`text${i}`,'界'.repeat(3000)]))}));
const child={kind:'scatter',x:'x',y:'y',aggregation:'none'};

test('dashboard accepts bounded combined UTF-8 child payloads below 32 MiB',()=>{
  const result=buildRendererSpec(wideRows(),{kind:'dashboard',charts:[child,child]},'plotly');
  assert.equal(result.children.length,2);
  assert.deepEqual(result.children.map(chart=>chart.normalized.records.length),[110,110]);
  assert.deepEqual(result.children.map(chart=>chart.spec.data[0].y[109]),[110,110]);
});

test('combined UTF-8 payload above 32 MiB fails before any native renderer is built',()=>{
  // Each child is below the 16 MiB retained-state ceiling; six copies exceed 32 MiB.
  // SVG does not support geo: that error must not precede the combined payload guard.
  assert.throws(()=>buildRendererSpec(wideRows(),{kind:'dashboard',charts:[
    {...child,kind:'geo'},...Array.from({length:5},()=>child),
  ]},'svg'),/combined.*32\s*MiB.*(?:payload|limit|budget)|combined.*payload.*32\s*MiB/i);
});

test('stream byte checks inspect reduced rows, never serialize the raw input iterator',async()=>{
  let reads=0;
  const source=(function*(){for(let x=0;x<100_000;x++){reads++;yield {x,y:x};}})();
  Object.defineProperty(source,'toJSON',{value(){throw new Error('Raw source must not be serialized');}});
  const result=await renderStream(source,{kind:'scatter',x:'x',y:'y',max_points:10},'svg');
  assert.equal(reads,100_000);
  assert.equal(result.input_count,100_000);
  assert.equal(result.output_count,10);
  assert.equal(result.strategy,'sample');
});

test('Plotly rejects sparse heatmap Cartesian expansion above 100000 cells before allocating it',()=>{
  const rows=Array.from({length:330},(_,i)=>({day:`day${i}`,slot:`slot${i}`,z:i}));
  assert.throws(()=>buildRendererSpec(rows,{kind:'heatmap',x:'day',y:'slot',color:'z',aggregation:'none'},'plotly'),
    /heatmap.*100000.*cell|heatmap.*cell.*100000/i);
});
