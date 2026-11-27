import test from 'node:test';
import assert from 'node:assert/strict';
import * as toolkit from '../dist/index.js';

const rows=[{category:'A',value:2,group:'one'},{category:'B',value:4,group:'one'}];
const spec={kind:'bar',x:'category',y:'value',title:'Example',aggregation:'none'};

test('five engines create real specs or SVG using identical mapped values', () => {
  assert.equal(typeof toolkit.buildRendererSpec,'function');
  const vega=toolkit.buildRendererSpec(rows,spec,'vega');
  assert.equal(vega.spec.mark.type,'bar');
  assert.equal(vega.spec.encoding.x.field,'category');
  assert.deepEqual(vega.spec.data.values,rows);
  const echarts=toolkit.buildRendererSpec(rows,spec,'echarts');
  assert.equal(echarts.spec.series[0].type,'bar');
  assert.deepEqual(echarts.spec.series[0].data,[2,4]);
  const plotly=toolkit.buildRendererSpec(rows,spec,'plotly');
  assert.equal(plotly.spec.data[0].type,'bar');
  assert.deepEqual(plotly.spec.data[0].x,['A','B']);
  const antv=toolkit.buildRendererSpec(rows,spec,'antv');
  assert.equal(antv.spec.type,'interval');
  assert.equal(antv.spec.encode.y,'value');
  const svg=toolkit.render(rows,spec,'svg');
  assert.equal(svg.mime_type,'text/html');
  assert.match(svg.html,/<svg/);
  assert.equal((svg.html.match(/class="mark"/g)||[]).length,2);
  assert.equal(svg.input_count,2);
  assert.equal(svg.output_count,2);
});

test('rendering reports bounds, aggregation and metadata without double-normalization', () => {
  assert.equal(typeof toolkit.render,'function');
  const result=toolkit.render(Array.from({length:100},(_,x)=>({x,y:x})),{x:'x',y:'y',max_points:10},'plotly');
  assert.equal(result.input_count,100);
  assert.equal(result.output_count,10);
  assert.equal(result.strategy,'sample');
  assert.ok(result.warnings.length);
  const count=toolkit.buildRendererSpec(rows,{x:'group',aggregation:'count'},'vega');
  assert.equal(count.spec.encoding.y.field,'count');
  assert.deepEqual(count.spec.data.values,[{group:'one',count:2}]);
});

test('HTML escapes title, cells, script-breaking strings, SVG text and unsafe asset URLs', () => {
  assert.equal(typeof toolkit.render,'function');
  const attack='</script><img src=x onerror="globalThis.pwned=1"><script>';
  for(const engine of ['svg','vega','echarts','antv','plotly']) {
    const result=toolkit.render([{category:attack,value:2}],{...spec,title:attack,description:attack},engine);
    assert.ok(!result.html.includes(attack));
    assert.ok(!result.html.includes('<img'));
    assert.ok(!result.html.includes('onerror="globalThis'));
    assert.match(result.html,/Content-Security-Policy/);
  }
  assert.throws(()=>toolkit.render(rows,spec,'vega',{assets:{vega:'javascript:alert(1)'}}),/asset|unsafe/i);
  assert.throws(()=>toolkit.render(rows,spec,'vega',{assets:{vega:'https://x/" onload="x'}}),/asset|unsafe/i);
});

test('dashboards create separate engine specs and metadata for every child', () => {
  assert.equal(typeof toolkit.render,'function');
  const result=toolkit.render(rows,{kind:'dashboard',title:'Dashboard',columns:2,charts:[spec,{...spec,kind:'line',title:'Trend'}]},'vega');
  assert.equal(result.input_count,2);
  assert.equal(result.output_count,4);
  assert.equal(result.strategy,'dashboard');
  assert.equal(result.renderer_spec.children.length,2);
  assert.match(result.html,/id="chart-0"/);
  assert.match(result.html,/id="chart-1"/);
});

test('missing fields, invalid numeric mappings and unsupported kinds fail explicitly', () => {
  assert.equal(typeof toolkit.render,'function');
  assert.throws(()=>toolkit.render(rows,{x:'not_here',y:'value'},'vega'),/field/i);
  assert.throws(()=>toolkit.render([{category:'a',value:'bad'}],spec,'svg'),/numeric/i);
  assert.throws(()=>toolkit.render(rows,{...spec,kind:'sunburst'},'svg'),/unsupported/i);
  assert.throws(()=>toolkit.render(rows,spec,'matplotlib'),/engine/i);
  assert.throws(()=>toolkit.render(rows,spec,'bogus'),/engine/i);
});

test('five tool helpers expose validation schemas and invoke the selected engine', async () => {
  assert.equal(typeof toolkit.createTools,'function');
  const tools=toolkit.createTools();
  assert.equal(tools.length,5);
  assert.equal(new Set(tools.map(tool=>tool.name)).size,5);
  for(const tool of tools) {
    assert.equal(tool.inputSchema.type,'object');
    const result=await tool.invoke({data:rows,spec});
    assert.equal(tool.name,`render_${result.engine}`);
    assert.equal(result.output_count,2);
    await assert.rejects(()=>tool.invoke({data:rows,spec:{width:0}}));
  }
});

test('async rendering preserves original stream count in its artifact', async () => {
  assert.equal(typeof toolkit.renderStream,'function');
  async function* source(){for(let x=0;x<100;x++)yield {x,y:x};}
  const result=await toolkit.renderStream(source(),{x:'x',y:'y',max_points:10},'svg');
  assert.equal(result.input_count,100);
  assert.equal(result.output_count,10);
  assert.equal(result.strategy,'sample');
});

test('ECharts never drops duplicate category rows and refuses ambiguous grouped duplicates',()=>{
  const input=[{x:'a',y:1},{x:'a',y:2}];
  const result=toolkit.buildRendererSpec(input,{x:'x',y:'y',aggregation:'none'},'echarts');
  assert.deepEqual(result.spec.series[0].data,[1,2]);
  assert.throws(()=>toolkit.buildRendererSpec(input.map(row=>({...row,c:'one'})),{x:'x',y:'y',color:'c',aggregation:'none'},'echarts'),/duplicat|aggregat/i);
});

test('ECharts bubble sizes are encoded per datum without executable callbacks',()=>{
  const result=toolkit.buildRendererSpec([{x:1,y:2,s:3},{x:2,y:4,s:30}],{kind:'bubble',x:'x',y:'y',size:'s'},'echarts');
  assert.ok(result.spec.series[0].data[1].symbolSize>result.spec.series[0].data[0].symbolSize);
  assert.deepEqual(result.spec.series[0].data[0].value,[1,2]);
  assert.equal(typeof result.spec.series[0].data[0].symbolSize,'number');
});

test('untrusted numeric mappings reject null and missing measurements instead of inventing zeros',()=>{
  for(const engine of ['svg','vega','echarts','antv','plotly']) {
    assert.throws(()=>toolkit.render([{x:'a',y:2},{x:'b'}],{x:'x',y:'y'},engine),/numeric|missing/i);
    assert.throws(()=>toolkit.render([{x:'a',y:null}],{x:'x',y:'y'},engine),/numeric|missing/i);
  }
});

test('a gauge refuses multiple rows instead of silently dropping measurements',()=>{
  for(const engine of ['echarts','plotly']) assert.throws(()=>toolkit.render(rows,{...spec,kind:'gauge'},engine),/single|one/i);
});

test('native SVG splits line series on a shared category domain and includes dash-cued legend',()=>{
  const result=toolkit.render([{x:'Q1',y:10,region:'East'},{x:'Q2',y:20,region:'East'},{x:'Q1',y:25,region:'West'},{x:'Q2',y:5,region:'West'}],
    {kind:'line',x:'x',y:'y',color:'region'},'svg');
  assert.equal((result.html.match(/<polyline class="mark"/g)||[]).length,2);
  assert.match(result.html,/stroke-dasharray="7 4"/);
  assert.match(result.html,/East/);
  assert.match(result.html,/West/);
  const lines=[...result.html.matchAll(/<polyline class="mark"[^>]*points="([^"]+)"/g)].map(match=>match[1].split(' ').map(point=>Number(point.split(',')[0])));
  assert.deepEqual(lines[0],lines[1]);
});

test('dark themes explicitly color SVG text and Vega legends for contrast',()=>{
  const svg=toolkit.render(rows,{...spec,theme:'dark'},'svg').renderer_spec.spec.svg;
  assert.match(svg,/fill="#e5e7eb"/);
  const vega=toolkit.buildRendererSpec(rows,{...spec,color:'group',theme:'dark'},'vega');
  assert.equal(vega.spec.config.legend.labelColor,'#e5e7eb');
  assert.equal(vega.spec.config.legend.titleColor,'#e5e7eb');
});

test('native SVG thins long category axes and preserves full distinguishable labels',()=>{
  const data=Array.from({length:40},(_,i)=>({x:`Common long category name ${i}`,y:i}));
  const svg=toolkit.render(data,{kind:'bar',x:'x',y:'y'},'svg').renderer_spec.spec.svg;
  const ticks=[...svg.matchAll(/class="category-tick"/g)];
  assert.ok(ticks.length>=5 && ticks.length<=15);
  assert.match(svg,/<title>Common long category name 0<\/title>/);
  assert.match(svg,/<title>Common long category name 39<\/title>/);
  assert.match(svg,/…/);
});

test('AntV pie has a visible category key when tooltips are disabled',()=>{
  const result=toolkit.buildRendererSpec(rows,{...spec,kind:'pie'},'antv');
  assert.notEqual(result.spec.legend?.color,false);
  assert.equal(result.spec.encode.color,'category');
});

test('categorical heatmaps map y as a coordinate and infer count as the default color measure',()=>{
  const data=[{x:'Mon',y:'AM'},{x:'Mon',y:'AM'},{x:'Tue',y:'PM'}];
  const result=toolkit.buildRendererSpec(data,{kind:'heatmap',x:'x',y:'y'},'vega');
  assert.equal(result.spec.encoding.y.type,'nominal');
  assert.equal(result.spec.encoding.color.field,'count');
  assert.deepEqual(result.spec.data.values,[{x:'Mon',y:'AM',count:2},{x:'Tue',y:'PM',count:1}]);
});
