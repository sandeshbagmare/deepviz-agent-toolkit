import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {render} from '../dist/index.js';

const assets={vega:'/assets/vega',vegaLite:'/assets/vegaLite',vegaEmbed:'/assets/vegaEmbed',echarts:'/assets/echarts',antv:'/assets/antv',plotly:'/assets/plotly'};
const paths={vega:'vega/build/vega.min.js',vegaLite:'vega-lite/build/vega-lite.min.js',vegaEmbed:'vega-embed/build/vega-embed.min.js',echarts:'echarts/dist/echarts.min.js',antv:'@antv/g2/dist/g2.min.js',plotly:'plotly.js-dist-min/plotly.min.js'};
const browser=await chromium.launch({headless:true});
let html='';
const server=createServer(async(req,res)=>{
  try {
    const key=req.url?.replace('/assets/','');
    if(paths[key]) {res.writeHead(200,{'Content-Type':'text/javascript'});res.end(await readFile(fileURLToPath(new URL(`../../../node_modules/${paths[key]}`,import.meta.url))));}
    else if(req.url==='/') {res.writeHead(200,{'Content-Type':'text/html'});res.end(html);}
    else if(req.url==='/favicon.ico') {res.writeHead(204);res.end();}
    else {res.writeHead(404);res.end();}
  } catch(error){res.writeHead(500);res.end(String(error));}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
test.after(async()=>{await browser.close();await new Promise(resolve=>server.close(resolve));});

for(const engine of ['svg','vega','echarts','antv','plotly']) {
  test(`${engine}: offline HTML renders charts and neutralizes malicious content`,async()=>{
    const page=await browser.newPage();
    try {
      const errors=[],external=[];
      page.on('pageerror',error=>errors.push(String(error)));
      page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
      await page.route('**/*',route=>route.request().url().startsWith(base)?route.continue():(external.push(route.request().url()),route.abort()));
      for(const kind of ['bar','line','area','pie','scatter','histogram','bubble','table']) {
        const attack='</script><img src=x onerror="globalThis.pwned=1"><script>';
        const data=Array.from({length:8},(_,i)=>({x:i+1,y:(i+1)*2,size:i+2,label:attack}));
        html=render(data,{kind,x:'x',y:'y',size:kind==='bubble' && engine!=='echarts'?'size':null,title:attack},engine,{assets}).html;
        await page.goto(base);
        await page.waitForFunction(()=>globalThis.deepvizReady===true);
        assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[],`${kind}: bootstrap errors`);
        assert.equal(await page.evaluate(()=>globalThis.pwned),undefined);
        assert.equal(await page.locator('img').count(),0);
        assert.ok(await page.locator(kind==='table'?'table':'#chart-0 svg, #chart-0 canvas').count()>0,`${kind}: no actual renderer output`);
      }
      assert.deepEqual(errors,[]);
      assert.deepEqual(external,[]);
    } finally {await page.close();}
  });
}

test('all browser engines render a two-chart dashboard offline',async()=>{
  for(const engine of ['svg','vega','echarts','antv','plotly']) {
    const page=await browser.newPage();
    try {
      html=render([{x:'a',y:2},{x:'b',y:3}],{kind:'dashboard',charts:[{kind:'bar',x:'x',y:'y'},{kind:'line',x:'x',y:'y'}]},engine,{assets}).html;
      await page.goto(base);
      await page.waitForFunction(()=>globalThis.deepvizReady===true);
      assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[]);
      for(let i=0;i<2;i++)assert.ok(await page.locator(`#chart-${i} svg, #chart-${i} canvas`).count()>0);
    } finally {await page.close();}
  }
});

for(const [engine,kinds] of Object.entries({vega:['box','violin','heatmap'],echarts:['heatmap','radar','treemap','sunburst','funnel','gauge'],antv:['heatmap','box','radar','treemap'],plotly:['heatmap','box','violin','radar','treemap','sunburst','funnel','gauge','geo']})) {
  test(`${engine}: specialized supported charts render offline`,async()=>{
    const page=await browser.newPage();
    try {
      const errors=[];
      page.on('pageerror',error=>errors.push(String(error)));
      page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
      for(const kind of kinds) {
        const data=[{x:1,y:2,z:3},{x:2,y:3,z:4},{x:3,y:4,z:5}];
        html=render(kind==='gauge'?data.slice(0,1):data,{kind,x:'x',y:'y',color:kind==='heatmap'?'z':null},engine,{assets}).html;
        await page.goto(base);
        await page.waitForFunction(()=>globalThis.deepvizReady===true);
        assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[],`${kind}: bootstrap errors`);
        assert.ok(await page.locator('#chart-0 svg, #chart-0 canvas').count()>0,`${kind}: no renderer output`);
      }
      assert.deepEqual(errors,[]);
    } finally {await page.close();}
  });
}
