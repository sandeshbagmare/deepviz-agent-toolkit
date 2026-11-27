import test from 'node:test';
import assert from 'node:assert/strict';
import {buildRendererSpec,render,renderStream,ValidationError} from '../dist/index.js';

const rows=[{x:1,y:2,cohort:'East'},{x:2,y:4,cohort:'East'},{x:3,y:8,cohort:'West'},{x:4,y:10,cohort:'West'}];
const unsupported={
  vega:['violin','pie'],
  echarts:['pie','treemap','sunburst','funnel','gauge','radar','histogram'],
  antv:['histogram','pie','treemap'],
  plotly:['pie','treemap','sunburst','geo','gauge'],
  svg:['pie','histogram'],
};

for(const [engine,kinds] of Object.entries(unsupported)) for(const kind of kinds) {
  test(`${engine} ${kind}: refuses a color mapping that the native adapter discards`,()=>{
    assert.throws(()=>buildRendererSpec(kind==='gauge'?rows.slice(0,1):rows,
      {kind,x:'x',y:'y',color:'cohort',aggregation:'none'},engine),error=>
      error instanceof ValidationError && /color/i.test(error.message) && /unsupported|not support/i.test(error.message));
  });
}

test('unsupported grouped Vega violin fails through public HTML, stream and dashboard paths',async()=>{
  const spec={kind:'violin',x:'x',y:'y',color:'cohort',aggregation:'none'};
  assert.throws(()=>render(rows,spec,'vega'),/color.*(?:unsupported|not support)/i);
  await assert.rejects(renderStream(rows,spec,'vega'),/color.*(?:unsupported|not support)/i);
  assert.throws(()=>render(rows,{kind:'dashboard',charts:[spec]},'vega'),/color.*(?:unsupported|not support)/i);
});

test('uncolored global Vega density and actually grouped Plotly violins remain available',()=>{
  const spec={kind:'violin',x:'x',y:'y',aggregation:'none'};
  const single=buildRendererSpec(rows,spec,'vega');
  assert.equal(single.spec.transform[0].density,'y');
  assert.equal(single.normalized.records.length,4);
  const grouped=buildRendererSpec(rows,{...spec,color:'cohort'},'plotly');
  assert.deepEqual(grouped.spec.data.map(trace=>({name:trace.name,y:trace.y})),[
    {name:'East',y:[2,4]},{name:'West',y:[8,10]},
  ]);
});

test('intrinsic Vega/AntV category colors preserve an explicit matching x field',()=>{
  const spec={kind:'pie',x:'x',y:'y',color:'x',aggregation:'none'};
  assert.equal(buildRendererSpec(rows,spec,'vega').spec.encoding.color.field,'x');
  assert.equal(buildRendererSpec(rows,spec,'antv').spec.encode.color,'x');
  const tree=buildRendererSpec(rows,{...spec,kind:'treemap'},'antv');
  assert.equal(tree.spec.encode.color,'name');
  assert.deepEqual(tree.spec.data.value.children.map(row=>row.name),['1','2','3','4']);
});

test('supported grouped bars still preserve the requested cohort in all five targets',()=>{
  for(const engine of ['svg','vega','echarts','antv','plotly']) {
    const result=buildRendererSpec(rows,{kind:'bar',x:'x',y:'y',color:'cohort',aggregation:'none'},engine);
    assert.deepEqual(result.normalized.records.map(row=>row.cohort),['East','East','West','West']);
    if(engine==='svg') assert.match(result.spec.svg,/Series key[\s\S]*East[\s\S]*West/);
    else if(engine==='vega') assert.equal(result.spec.encoding.color.field,'cohort');
    else if(engine==='echarts') assert.deepEqual(result.spec.series.map(series=>series.name),['East','West']);
    else if(engine==='antv') assert.equal(result.spec.encode.color,'cohort');
    else assert.deepEqual(result.spec.data.map(trace=>trace.name),['East','West']);
  }
});
