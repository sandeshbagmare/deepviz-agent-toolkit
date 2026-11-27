// Bounded screenshot-path diagnostic; never rerenders helper outputs or builds.
import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {createServer} from 'node:http';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';

const input=resolve(process.argv[2]),out=resolve(process.argv[3]);mkdirSync(out);
const summary={status:'IN_PROGRESS',capture:'viewport only; same2000x800, no helper rerender',controls:[]};
const save=()=>writeFileSync(resolve(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');
const {chromium}=createRequire(resolve(process.env.R22_READONLY_DEPS,'package.json'))('playwright');
const server=createServer((req,res)=>{
  const name=req.url?.slice(1);
  if(['omitted-default','dashboard'].includes(name)){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(readFileSync(resolve(input,name+'.html')));}
  else{res.writeHead(req.url==='/favicon.ico'?204:404);res.end();}
});
let browser;
try{
  browser=await chromium.launch({headless:true});summary.chromium=browser.version();
  await new Promise(done=>server.listen(0,'127.0.0.1',done));const base=`http://127.0.0.1:${server.address().port}`;
  for(const name of ['omitted-default','dashboard']){
    const page=await browser.newPage({viewport:{width:2000,height:800}}),errors=[],external=[];
    const control={name,errors,external_requests:external};summary.controls.push(control);
    try{
      page.on('pageerror',error=>errors.push(String(error)));
      page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
      await page.route('**/*',route=>route.request().url().startsWith(base)?route.continue():(external.push(route.request().url()),route.abort()));
      await page.goto(base+'/'+name);await page.waitForFunction(()=>globalThis.deepvizReady===true);
      control.dom=await page.evaluate(()=>({title:document.title,h1:document.querySelector('h1').textContent,
        headings:[...document.querySelectorAll('h2')].map(e=>e.textContent),ready:globalThis.deepvizReady,bootstrap_errors:globalThis.deepvizErrors,
        viewport:[innerWidth,innerHeight,devicePixelRatio],document:[document.documentElement.scrollWidth,document.documentElement.scrollHeight],
        charts:[...document.querySelectorAll('.chart svg')].map(svg=>({title:svg.querySelector('title').textContent,
          mark_titles:[...svg.querySelectorAll('.mark title')].map(e=>e.textContent),zero:[...svg.querySelectorAll('text')].some(e=>e.textContent==='0.000'),
          marks:[...svg.querySelectorAll('rect.mark')].map(e=>({y:Number(e.getAttribute('y')),height:Number(e.getAttribute('height'))}))}))}));
      const cdp=await page.context().newCDPSession(page);control.layout=await cdp.send('Page.getLayoutMetrics');await cdp.detach();save();
      assert.equal(control.dom.title,name==='dashboard'?'R22 helper dashboard':'Visualization');
      assert.equal(control.dom.h1,control.dom.title);assert.deepEqual(control.dom.bootstrap_errors,[]);
      assert.equal(control.dom.charts.length,name==='dashboard'?2:1);
      assert.deepEqual(control.dom.headings,name==='dashboard'?['R22 first','R22 second']:['Visualization']);
      for(const chart of control.dom.charts){
        assert.deepEqual(chart.mark_titles,['A: 2','B: 3']);assert.equal(chart.zero,true);
        assert.equal(chart.marks.length,2);assert.ok(Math.abs(chart.marks[0].height/chart.marks[1].height-2/3)<1e-9);
        assert.ok(chart.marks.every(mark=>Math.abs(mark.y+mark.height-455)<1e-9));
      }
      assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
      await page.screenshot({path:resolve(out,name+'.png'),fullPage:false});control.viewport_png_captured=true;save();
    }finally{await page.close();}
  }
  summary.status='PASS';
}catch(error){summary.status='BLOCKED_OR_FAILED_NOT_PASS';summary.error=String(error);process.exitCode=1;}
finally{save();if(browser)await browser.close();if(server.listening)await new Promise(done=>server.close(done));}
console.log(JSON.stringify(summary,null,2));
