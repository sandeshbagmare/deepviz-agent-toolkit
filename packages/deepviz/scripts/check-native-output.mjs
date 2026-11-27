/** Bounded native-only paint/geometry check; never loads browser-engine CDNs. */
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile,writeFile,access} from 'node:fs/promises';
import {createRequire} from 'node:module';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [outputArg,existingToolRoot]=process.argv.slice(2);
assert.ok(outputArg,'Usage: node check-native-output.mjs CONSUMER_DIR [existing-tool-root]');
const output=path.resolve(outputArg);
for(const name of ['native-svg.png','native-table.png','native-browser.json']){
  await assert.rejects(access(path.join(output,name)),{code:'ENOENT'},`Refuse to overwrite ${name}`);
}
const {chromium}=existingToolRoot?createRequire(pathToFileURL(path.resolve(existingToolRoot,'package.json')))('playwright'):await import('playwright');
const pages=new Map(await Promise.all(['native-svg.html','native-table.html'].map(async name=>['/'+name,await readFile(path.join(output,name))])));
const server=createServer((request,response)=>{
  const bytes=pages.get(request.url);response.writeHead(bytes?200:404,{'Content-Type':'text/html; charset=utf-8'});response.end(bytes??'Not found');
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
let browser;const record={started:new Date().toISOString(),scope:'native SVG and escaped table only; no CDN acceptance',cases:[]};
try{
  browser=await chromium.launch({headless:true});record.browser=browser.version();
  for(const name of ['native-svg','native-table']){
    const page=await browser.newPage({viewport:{width:1100,height:900}});const errors=[],requests=[];
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});page.on('pageerror',error=>errors.push(String(error)));
    await page.route('**/*',async route=>{if(route.request().url().startsWith(origin+'/'))await route.continue();else{requests.push(route.request().url());await route.abort();}});
    await page.goto(origin+'/'+name+'.html');await page.waitForFunction(()=>globalThis.deepvizReady===true);
    assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[]);assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
    const actual=await page.evaluate(()=>({title:document.title,marks:[...document.querySelectorAll('rect.mark')].map(el=>({title:el.querySelector('title')?.textContent,y:Number(el.getAttribute('y')),height:Number(el.getAttribute('height'))})),cells:[...document.querySelectorAll('tbody td')].map(el=>el.textContent),images:document.querySelectorAll('img').length}));
    if(name==='native-svg'){
      assert.equal(actual.title,'Packed native');assert.deepEqual(actual.marks.map(mark=>mark.title),['Alpha: 2','Beta: 5','Gamma: -3']);
      const heights=[97.5,243.75,146.25],ys=[211.25,65,308.75];
      actual.marks.forEach((mark,index)=>{assert.ok(Math.abs(mark.height-heights[index])<1e-9);assert.ok(Math.abs(mark.y-ys[index])<1e-9);});
    }else{assert.equal(actual.images,0);assert.ok(actual.cells.includes('<img src=x onerror=alert(1)>'));}
    const screenshot=path.join(output,name+'.png');await page.screenshot({path:screenshot,fullPage:true});record.cases.push({name,actual,errors,unexpectedRequests:requests,screenshot});await page.close();
  }
  record.passed=true;console.log('PASS: two native pages; literal values/geometry/table text, zero console/page errors or external requests.');
}catch(error){record.passed=false;record.failure=String(error);throw error;}
finally{record.finished=new Date().toISOString();await writeFile(path.join(output,'native-browser.json'),JSON.stringify(record,null,2));if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
