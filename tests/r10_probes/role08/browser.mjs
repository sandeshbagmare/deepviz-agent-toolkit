import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile,writeFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const [source,consumer,output]=process.argv.slice(2);
assert.ok(source&&consumer&&output,'Usage: browser.mjs SOURCE CONSUMER OUTPUT');
const require=createRequire(path.join(source,'package.json'));
const {chromium}=require('playwright');
const packageRoot=path.join(consumer,'node_modules','@deepviz','agent-toolkit');
const {render}=await import(pathToFileURL(path.join(packageRoot,'dist/index.js')).href);
const files={vega:'vega/build/vega.min.js',vegaLite:'vega-lite/build/vega-lite.min.js',vegaEmbed:'vega-embed/build/vega-embed.min.js',echarts:'echarts/dist/echarts.min.js',antv:'@antv/g2/dist/g2.min.js',plotly:'plotly.js-dist-min/plotly.min.js'};
const assets=Object.fromEntries(Object.keys(files).map(key=>[key,`/asset/${key}`]));
let html='';
const server=createServer(async(req,res)=>{
  try {
    const asset=req.url?.match(/^\/asset\/([A-Za-z]+)$/)?.[1];
    if(asset&&files[asset]) {res.writeHead(200,{'Content-Type':'text/javascript'});res.end(await readFile(path.join(source,'node_modules',files[asset])));}
    else if(/^\/pkg\/[a-z.-]+$/.test(req.url??'')) {res.writeHead(200,{'Content-Type':req.url.endsWith('.json')?'application/json':'text/javascript'});res.end(await readFile(path.join(packageRoot,'dist',req.url.slice(5))));}
    else if(req.url==='/') {res.writeHead(200,{'Content-Type':'text/html'});res.end(html);}
    else if(req.url==='/favicon.ico') {res.writeHead(204);res.end();}
    else {res.writeHead(404);res.end();}
  } catch {res.writeHead(500);res.end('Local fixture resource unavailable');}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
let browser;
const results=[];
try {
  browser=await chromium.launch({headless:true});
  for(const engine of ['module','svg','vega','echarts','antv','plotly']) {
    const page=await browser.newPage({viewport:{width:1000,height:700},deviceScaleFactor:1});
    const errors=[],external=[];
    page.on('pageerror',error=>errors.push(String(error)));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.route('**/*',route=>route.request().url().startsWith(base)?route.continue():(external.push(route.request().url()),route.abort()));
    try {
      if(engine==='module') {
        html=`<!doctype html><meta charset="utf-8"><h1>Packed native browser entry</h1><div id="chart-0"></div><script type="module">import * as api from '/pkg/index.js';const rows=api.normalize({x:['Alpha','Beta'],y:[2,5]}).records;const result=api.render(rows,{x:'x',y:'y'},'svg');document.querySelector('#chart-0').innerHTML=result.renderer_spec.spec.svg;globalThis.deepvizErrors=[];globalThis.moduleResult={exports:Object.keys(api).sort(),records:rows,input_count:result.input_count,output_count:result.output_count};globalThis.deepvizReady=true;</script>`;
      } else {
        const artifact=render([{x:'Alpha',y:2},{x:'Beta',y:5}],{x:'x',y:'y',title:`Packed ${engine}`},engine,{assets});
        assert.equal(artifact.input_count,2);
        assert.equal(artifact.output_count,2);
        assert.deepEqual(artifact.renderer_spec.normalized.records,[{x:'Alpha',y:2},{x:'Beta',y:5}]);
        html=artifact.html;
      }
      await writeFile(path.join(output,`browser-${engine}.html`),html,{flag:'wx'});
      await page.goto(base);
      await page.waitForFunction(()=>globalThis.deepvizReady===true);
      assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[]);
      const geometry=await page.locator('#chart-0').evaluate(element=>({svg:element.querySelectorAll('svg').length,canvas:element.querySelectorAll('canvas').length}));
      assert.ok(geometry.svg+geometry.canvas>0,`${engine}: no rendered geometry`);
      let native=null;
      if(engine==='module'||engine==='svg') {
        native=await page.locator('#chart-0 svg').evaluate(svg=>[...svg.querySelectorAll('rect')].map(mark=>({height:Number(mark.getAttribute('height')),bottom:Number(mark.getAttribute('y'))+Number(mark.getAttribute('height'))})));
        assert.equal(native.length,2);
        assert.ok(Math.abs(native[0].height/native[1].height-2/5)<1e-9);
        assert.equal(native[0].bottom,native[1].bottom);
      }
      const moduleResult=engine==='module'?await page.evaluate(()=>globalThis.moduleResult):null;
      if(moduleResult) assert.deepEqual(moduleResult.records,[{x:'Alpha',y:2},{x:'Beta',y:5}]);
      assert.deepEqual(errors,[],`${engine}: console/page errors`);
      assert.deepEqual(external,[],`${engine}: external requests`);
      const screenshot=`browser-${engine}.png`;
      await page.screenshot({path:path.join(output,screenshot),fullPage:true});
      results.push({engine,...geometry,native,moduleResult,consoleErrors:0,externalRequests:0,screenshot});
    } finally {await page.close();}
  }
  console.log(JSON.stringify({chromium:browser.version(),results}));
} finally {
  await writeFile(path.join(output,'browser-results.json'),JSON.stringify({chromium:browser?.version()??null,results},null,2),{flag:'wx'});
  if(browser) await browser.close();
  await new Promise(resolve=>server.close(resolve));
}
