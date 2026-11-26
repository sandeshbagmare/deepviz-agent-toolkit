import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {render} from '../dist/index.js';

const output=new URL('../../../artifacts/local/N18/',import.meta.url);
await mkdir(output,{recursive:true});
const assets={vega:'/assets/vega',vegaLite:'/assets/vegaLite',vegaEmbed:'/assets/vegaEmbed',echarts:'/assets/echarts',antv:'/assets/antv',plotly:'/assets/plotly'};
const paths={vega:'vega/build/vega.min.js',vegaLite:'vega-lite/build/vega-lite.min.js',vegaEmbed:'vega-embed/build/vega-embed.min.js',echarts:'echarts/dist/echarts.min.js',antv:'@antv/g2/dist/g2.min.js',plotly:'plotly.js-dist-min/plotly.min.js'};
const browser=await chromium.launch({headless:true});
const identity={node:process.version,chromium:browser.version(),files:{}};
for(const path of ['package-lock.json','schemas/chart-spec.schema.json','packages/deepviz/src/render.ts','packages/deepviz/src/renderers.ts',
  'packages/deepviz/dist/render.js','packages/deepviz/dist/renderers.js',...Object.values(paths).map(path=>`node_modules/${path}`)]) {
  const bytes=await readFile(new URL(`../../../${path}`,import.meta.url));
  identity.files[path]={bytes:bytes.byteLength,sha256:createHash('sha256').update(bytes).digest('hex')};
}
await writeFile(new URL('source-assets.identity.json',output),JSON.stringify(identity,null,2));
let html='';
const server=createServer(async(req,res)=>{
  try {
    const key=req.url?.replace('/assets/','');
    if(paths[key]) {res.writeHead(200,{'Content-Type':'text/javascript'});res.end(await readFile(new URL(`../../../node_modules/${paths[key]}`,import.meta.url)));}
    else if(req.url==='/') {res.writeHead(200,{'Content-Type':'text/html'});res.end(html);}
    else if(req.url==='/favicon.ico') {res.writeHead(204);res.end();}
    else {res.writeHead(404);res.end();}
  } catch(error) {res.writeHead(500);res.end(String(error));}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
test.after(async()=>{await browser.close();await new Promise(resolve=>server.close(resolve));});

async function open(data,spec,engine,label) {
  const result=render(data,spec,engine,{assets});
  html=result.html;
  // Capture the real chart instance without changing native options or rendering.
  if(engine==='antv') {
    const nonce=html.match(/<script nonce="([^"]+)"/)[1];
    html=html.replace('</head>',`<script nonce="${nonce}">const originalRender=G2.Chart.prototype.render;G2.Chart.prototype.render=function(...args){globalThis.actualG2=this;return originalRender.apply(this,args);};</script></head>`);
  }
  const page=await browser.newPage({viewport:{width:1250,height:900},deviceScaleFactor:1});
  const errors=[],external=[];
  page.on('pageerror',error=>errors.push(String(error)));
  page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.route('**/*',route=>route.request().url().startsWith(base)?route.continue():(external.push(route.request().url()),route.abort()));
  await page.goto(base);
  await page.waitForFunction(()=>globalThis.deepvizReady===true);
  await page.screenshot({path:fileURLToPath(new URL(`${label}.png`,output)),fullPage:true});
  await writeFile(new URL(`${label}.native.json`,output),JSON.stringify(result.renderer_spec,null,2));
  assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[]);
  assert.deepEqual(errors,[],'browser console/page errors');
  assert.deepEqual(external,[],'unexpected network dependency');
  return page;
}

test('AntV color-grouped bars occupy separate rectangles rather than hiding each other',async()=>{
  const page=await open([{x:'Q1',y:10,group:'East'},{x:'Q2',y:20,group:'East'},{x:'Q1',y:25,group:'West'},{x:'Q2',y:5,group:'West'}],
    {kind:'bar',x:'x',y:'y',color:'group',aggregation:'none',title:'Grouped bars: East 10/20; West 25/5'},'antv','antv-grouped-bars');
  try {
    const bounds=await page.evaluate(()=>[...actualG2.getContext().canvas.document.documentElement.querySelectorAll('.element')].map(mark=>{
      const box=mark.getBBox();return {x:box.x,y:box.y,width:box.width,height:box.height};
    }));
    await writeFile(new URL('antv-grouped-bars.bounds.json',output),JSON.stringify(bounds,null,2));
    assert.equal(bounds.length,4);
    for(let i=0;i<bounds.length;i++) for(let j=i+1;j<bounds.length;j++) {
      const a=bounds[i],b=bounds[j];
      const overlapWidth=Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x);
      const overlapHeight=Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y);
      assert.ok(overlapWidth<=1 || overlapHeight<=1,`bars ${i}/${j} overlap: ${JSON.stringify([a,b])}`);
    }
  } finally {await page.close();}
});

test('ECharts signed heatmap has two category axes and distinct actual negative-value fills',async()=>{
  const page=await open([{day:'Mon',slot:'AM',z:-7},{day:'Tue',slot:'PM',z:-2}],
    {kind:'heatmap',x:'day',y:'slot',color:'z',aggregation:'none',title:'Signed heatmap: Mon/AM -7; Tue/PM -2'},'echarts','echarts-signed-heatmap');
  try {
    const state=await page.evaluate(()=>{
      const chart=echarts.getInstanceByDom(document.getElementById('chart-0'));
      const data=chart.getModel().getSeriesByIndex(0).getData();
      return {xs:chart.getOption().xAxis[0].data,ys:chart.getOption().yAxis[0].data,
        values:Array.from({length:data.count()},(_,i)=>data.getValues(['x','y','value'],i)),
        fills:Array.from({length:data.count()},(_,i)=>data.getItemVisual(i,'style').fill),
        text:chart.getZr().storage.getDisplayList().map(mark=>mark.style?.text).filter(text=>text!==undefined)};
    });
    await writeFile(new URL('echarts-signed-heatmap.runtime.json',output),JSON.stringify(state,null,2));
    assert.deepEqual(state.xs,['Mon','Tue']);assert.deepEqual(state.ys,['AM','PM']);
    assert.notEqual(state.fills[0],state.fills[1]);
    assert.ok(state.text.includes('-7'));assert.ok(state.text.includes('-2'));
  } finally {await page.close();}
});

test('Plotly renders exactly one bar per real color-group row including a null group',async()=>{
  const page=await open([{x:'Q1',y:2,group:null},{x:'Q1',y:7,group:'West'}],
    {kind:'bar',x:'x',y:'y',color:'group',aggregation:'none',title:'Null group 2; West 7'},'plotly','plotly-null-group');
  try {
    assert.deepEqual(await page.locator('#chart-0').evaluate(el=>el.data.map(trace=>trace.y)),[[2],[7]]);
    assert.equal(await page.locator('.barlayer .point').count(),2);
    assert.match(await page.locator('.legend').textContent(),/\(missing\)/);
  } finally {await page.close();}
});

test('Plotly and SVG pies expose category identities visually while preserving 2:6 values',async()=>{
  for(const engine of ['plotly','svg']) {
    const page=await open([{x:'Alpha',y:2},{x:'Beta',y:6}],
      {kind:'pie',x:'x',y:'y',title:'Pie: Alpha 25%; Beta 75%'},engine,`${engine}-pie-key`);
    try {
      const key=engine==='plotly'?page.locator('.legend'):page.locator('[aria-label="Category key"]');
      assert.match(await key.textContent(),/Alpha/);assert.match(await key.textContent(),/Beta/);
      assert.ok(await key.isVisible());
    } finally {await page.close();}
  }
});

test('ECharts signed bubble coordinates and unequal per-datum sizes reach actual native marks',async()=>{
  const page=await open([{x:-2,y:-4,s:4},{x:3,y:5,s:16}],
    {kind:'bubble',x:'x',y:'y',size:'s',aggregation:'none',title:'Bubbles: (-2,-4,size4), (3,5,size16)'},'echarts','echarts-signed-bubble');
  try {
    const state=await page.evaluate(()=>{
      const chart=echarts.getInstanceByDom(document.getElementById('chart-0'));
      const data=chart.getModel().getSeriesByIndex(0).getData();
      return {values:[data.getValues(['x','y'],0),data.getValues(['x','y'],1)],sizes:[data.getItemVisual(0,'symbolSize'),data.getItemVisual(1,'symbolSize')]};
    });
    assert.deepEqual(state.values,[[-2,-4],[3,5]]);assert.ok(state.sizes[1]>state.sizes[0]);
  } finally {await page.close();}
});

test('numeric line x=1,2,4 keeps 1:2 horizontal gaps in ECharts and SVG',async()=>{
  for(const engine of ['echarts','svg']) {
    const page=await open([{x:1,y:2},{x:2,y:8},{x:4,y:5}],
      {kind:'line',x:'x',y:'y',aggregation:'none',title:'Numeric line: x1/2/4; y2/8/5'},engine,`${engine}-numeric-line`);
    try {
      const xs=engine==='echarts'?await page.evaluate(()=>{
        const chart=echarts.getInstanceByDom(document.getElementById('chart-0'));
        return [1,2,4].map(x=>chart.convertToPixel({xAxisIndex:0},x));
      }):await page.locator('#chart-0 polyline.mark').evaluate(mark=>mark.getAttribute('points').split(' ').map(point=>Number(point.split(',')[0])));
      assert.ok(Math.abs((xs[2]-xs[1])/(xs[1]-xs[0])-2)<1e-8);
    } finally {await page.close();}
  }
});

for(const engine of ['svg','vega','echarts','antv','plotly']) {
  test(`${engine}: signed bubble areas preserve the 4:16 size ratio`,async()=>{
    const page=await open([{x:-2,y:-4,s:4},{x:3,y:5,s:16}],
      {kind:'bubble',x:'x',y:'y',size:'s',aggregation:'none',title:'Signed bubble areas: s4 then s16'},engine,`${engine}-bubble-areas`);
    try {
      const bounds=engine==='antv'?await page.evaluate(()=>[...actualG2.getContext().canvas.document.documentElement.querySelectorAll('.element')].map(mark=>{
        const box=mark.getBBox();return {x:box.x,y:box.y,width:box.width,height:box.height};
      })):engine==='echarts'?await page.evaluate(()=>{
        const data=echarts.getInstanceByDom(document.getElementById('chart-0')).getModel().getSeriesByIndex(0).getData();
        return [0,1].map(i=>{const [x,y]=data.getItemLayout(i),size=data.getItemVisual(i,'symbolSize');return {x,y,width:size,height:size};});
      }):await page.locator(engine==='svg'?'#chart-0 circle.mark':engine==='vega'?'#chart-0 .mark-symbol.role-mark path':'#chart-0 .scatterlayer .point').evaluateAll(marks=>marks.map(mark=>{
        const box=mark.getBoundingClientRect();return {x:box.x,y:box.y,width:box.width,height:box.height};
      }));
      await writeFile(new URL(`${engine}-bubble-areas.bounds.json`,output),JSON.stringify(bounds,null,2));
      assert.equal(bounds.length,2,engine);
      assert.ok(bounds[1].width>bounds[0].width,`${engine}: size measure must affect real mark width`);
      assert.ok(Math.abs((bounds[1].width/bounds[0].width)**2-4)<0.05,`${engine}: actual bubble areas must preserve 1:4 ratio`);
      assert.ok(bounds[1].x>bounds[0].x,`${engine}: signed x positions must preserve order`);
      assert.ok(bounds[1].y<bounds[0].y,`${engine}: signed y positions must preserve order`);
      if(engine==='antv') assert.ok(Math.max(...bounds.map(mark=>mark.x+mark.width))<=
        await page.evaluate(()=>actualG2.getContext().canvas.getConfig().width),'AntV entire bubble must fit its actual canvas');
    } finally {await page.close();}
  });
}
