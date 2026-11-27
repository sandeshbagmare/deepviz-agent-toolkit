import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile, mkdir, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {render} from '../dist/index.js';

const attack='</ScRiPt><img src=x onerror="globalThis.n17Executed=1"><script>&\u2028\u2029';
const field='<svg/onload=alert(1)>';
const evidence=new URL('../../../artifacts/local/N17/browser/',import.meta.url);
const assets={vega:'/assets/vega',vegaLite:'/assets/vegaLite',vegaEmbed:'/assets/vegaEmbed',echarts:'/assets/echarts',antv:'/assets/antv',plotly:'/assets/plotly'};
const dependencyPaths={vega:'vega/build/vega.min.js',vegaLite:'vega-lite/build/vega-lite.min.js',vegaEmbed:'vega-embed/build/vega-embed.min.js',echarts:'echarts/dist/echarts.min.js',antv:'@antv/g2/dist/g2.min.js',plotly:'plotly.js-dist-min/plotly.min.js'};

test('N17: actual browser title/field/category/series injection including hover', {timeout:90000},async()=>{
  await mkdir(evidence,{recursive:true});
  let html='';
  const server=createServer(async(req,res)=>{
    try {
      const key=req.url?.replace('/assets/','');
      if(dependencyPaths[key]) {res.writeHead(200,{'Content-Type':'text/javascript'});res.end(await readFile(new URL('../../../node_modules/'+dependencyPaths[key],import.meta.url)));}
      else if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end(html);}
      else if(req.url==='/favicon.ico'){res.writeHead(204);res.end();}
      else {res.writeHead(404);res.end();}
    }catch(error){res.writeHead(500);res.end(String(error));}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base='http://127.0.0.1:'+server.address().port;
  let browser;
  const observations=[];
  try {
    browser=await chromium.launch({headless:true});
    for(const engine of ['svg','vega','echarts','antv','plotly']) {
      const page=await browser.newPage({viewport:{width:1280,height:1050}});
      try {
        const errors=[],external=[];
        page.on('pageerror',error=>errors.push(String(error)));
        page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
        await page.route('**/*',route=>route.request().url().startsWith(base)?route.continue():(external.push(route.request().url()),route.abort()));
        const rows=[{[field]:attack,v:2,series:attack},{[field]:'Safe B',v:5,series:attack}];
        const artifact=render(rows,{kind:'bar',x:field,y:'v',color:'series',aggregation:'none',title:attack,description:attack,width:900,height:520},engine,{assets});
        html=artifact.html;
        await writeFile(new URL(engine+'.html',evidence),html);
        await page.goto(base);
        await page.waitForFunction(()=>globalThis.deepvizReady===true,{},{timeout:15000});
        assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[],engine+': bootstrap errors');
        const shapeCount=await page.locator('#chart-0 svg path, #chart-0 svg rect, #chart-0 canvas').count();
        assert.ok(shapeCount>=1,engine+': no actual renderer marks');
        if(engine==='echarts')await page.evaluate(()=>echarts.getInstanceByDom(document.getElementById('chart-0')).dispatchAction({type:'showTip',seriesIndex:0,dataIndex:0}));
        const graph=await page.locator('#chart-0').boundingBox();
        for(const [x,y] of [[0.3,0.4],[0.7,0.4],[0.3,0.75]])await page.mouse.move(graph.x+graph.width*x,graph.y+graph.height*y);
        await page.screenshot({path:fileURLToPath(new URL(engine+'.png',evidence)),fullPage:true});
        assert.equal(await page.evaluate(()=>globalThis.n17Executed),undefined,engine+': script executed');
        assert.equal(await page.locator('img, [onerror], [onload]').count(),0,engine+': injected active DOM');
        assert.deepEqual(errors,[],engine+': browser errors');
        assert.deepEqual(external,[],engine+': outbound dependency/request');
        observations.push({engine,shapeCount,inputCount:artifact.input_count,outputCount:artifact.output_count,errors,external});
      }finally{await page.close();}
    }
  }finally{
    await writeFile(new URL('observations.json',evidence),JSON.stringify(observations,null,2));
    if(browser)await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
});
