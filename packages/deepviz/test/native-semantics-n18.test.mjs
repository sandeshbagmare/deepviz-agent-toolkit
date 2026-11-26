import test from 'node:test';
import assert from 'node:assert/strict';
import {buildRendererSpec,render} from '../dist/index.js';

test('Plotly keeps a real null color group separate instead of replaying every group in it',()=>{
  const result=buildRendererSpec([{x:'Q1',y:2,series:null},{x:'Q1',y:7,series:'West'}],
    {kind:'bar',x:'x',y:'y',color:'series',aggregation:'none'},'plotly');
  assert.deepEqual(result.spec.data.map(trace=>trace.y),[[2],[7]]);
  assert.equal(result.spec.data[0].name,'(missing)');
});

for(const engine of ['svg','vega','echarts','antv','plotly']) {
  test(`${engine}: bubble coordinates may be signed`,()=>{
    const result=buildRendererSpec([{x:-2,y:-4,s:4},{x:3,y:5,s:16}],
      {kind:'bubble',x:'x',y:'y',size:'s',aggregation:'none'},engine);
    assert.equal(result.normalized.records[0].y,-4,engine);
  });
  test(`${engine}: negative size values are refused rather than silently clamped`,()=>{
    assert.throws(()=>buildRendererSpec([{x:1,y:2,s:-3}],
      {kind:'bubble',x:'x',y:'y',size:'s'},engine),/size.*non-negative|non-negative.*size/i,engine);
  });
}

test('heatmaps explicitly refuse duplicate coordinates instead of selecting the first cell silently',()=>{
  for(const engine of ['vega','echarts','antv','plotly']) {
    assert.throws(()=>buildRendererSpec([{day:'Mon',slot:'AM',z:2},{day:'Mon',slot:'AM',z:7}],
      {kind:'heatmap',x:'day',y:'slot',color:'z',aggregation:'none'},engine),/duplicat.*(?:coordinate|cell)|aggregat/i,engine);
  }
});

test('ECharts heatmap color domain covers signed measurements rather than clamping them to zero',()=>{
  const result=buildRendererSpec([{day:'Mon',slot:'AM',z:-7},{day:'Tue',slot:'PM',z:-2}],
    {kind:'heatmap',x:'day',y:'slot',color:'z',aggregation:'none'},'echarts');
  assert.equal(result.spec.visualMap.min,-7);
  assert.equal(result.spec.visualMap.max,-2);
  assert.deepEqual(result.spec.visualMap.text,['-2','-7']);
  assert.deepEqual(result.spec.xAxis.data,['Mon','Tue']);
  assert.deepEqual(result.spec.yAxis.data,['AM','PM']);
  assert.deepEqual(result.spec.series[0].data,[[0,0,-7],[1,1,-2]]);
});

test('Plotly pies retain a visible category legend without a separate color mapping',()=>{
  const result=buildRendererSpec([{x:'Alpha',y:2},{x:'Beta',y:6}],{kind:'pie',x:'x',y:'y'},'plotly');
  assert.equal(result.spec.layout.showlegend,true);
  assert.deepEqual(result.spec.data[0].labels,['Alpha','Beta']);
  assert.deepEqual(result.spec.data[0].values,[2,6]);
});

test('SVG pies expose visible category names, including the single full-circle case',()=>{
  const html=render([{x:'Only category',y:8}],{kind:'pie',x:'x',y:'y'},'svg').renderer_spec.spec.svg;
  assert.match(html,/<circle class="mark"[^>]*><title>Only category: 8<\/title><\/circle>/);
  assert.match(html,/aria-label="Category key"/);
  assert.match(html,/> Only category</);
});

test('ECharts numeric line coordinates preserve unequal x intervals in every color group',()=>{
  const result=buildRendererSpec([{x:1,y:2,group:'East'},{x:2,y:8,group:'East'},{x:4,y:5,group:'East'},
    {x:1,y:3,group:'West'},{x:4,y:7,group:'West'}],
    {kind:'line',x:'x',y:'y',color:'group',aggregation:'none'},'echarts');
  assert.equal(result.spec.xAxis.type,'value');
  assert.deepEqual(result.spec.series.map(series=>series.data),[[[1,2],[2,8],[4,5]],[[1,3],[4,7]]]);
});

test('SVG numeric line coordinates and tick positions preserve 1:2 horizontal gaps',()=>{
  const svg=render([{x:1,y:2},{x:2,y:8},{x:4,y:5}],
    {kind:'line',x:'x',y:'y',aggregation:'none'},'svg').renderer_spec.spec.svg;
  const xs=svg.match(/<polyline class="mark" points="([^"]+)"/)[1].split(' ').map(point=>Number(point.split(',')[0]));
  assert.ok(Math.abs((xs[2]-xs[1])/(xs[1]-xs[0])-2)<1e-9);
  const ticks=[...svg.matchAll(/class="category-tick" x="([^"]+)"/g)].map(match=>Number(match[1]));
  assert.deepEqual(ticks,xs);
});

test('size mappings never silently disappear on non-marker chart kinds',()=>{
  for(const engine of ['svg','vega','echarts','antv','plotly']) {
    assert.throws(()=>buildRendererSpec([{x:'A',y:2,s:4},{x:'B',y:8,s:9}],
      {kind:'pie',x:'x',y:'y',size:'s',aggregation:'none'},engine),/size.*(?:scatter|bubble|marker)/i,engine);
  }
});

test('tiny size measures preserve marker area ratios rather than sharing a minimum clamp',()=>{
  const rows=[{x:-2,y:-4,s:0.01},{x:3,y:5,s:0.04}];
  const spec={kind:'bubble',x:'x',y:'y',size:'s',aggregation:'none'};
  const sizes=buildRendererSpec(rows,spec,'echarts').spec.series[0].data.map(mark=>mark.symbolSize);
  assert.equal(sizes[1]/sizes[0],2);
  const svg=render(rows,spec,'svg').renderer_spec.spec.svg;
  const radii=[...svg.matchAll(/<circle class="mark"[^>]* r="([^"]+)"/g)].map(match=>Number(match[1]));
  assert.equal(radii[1]/radii[0],2);
});
