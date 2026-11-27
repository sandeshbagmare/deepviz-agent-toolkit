// Two actual SVG helper outputs, using the guarded fresh public entry only.
import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {createServer} from 'node:http';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const root=resolve(process.env.R22_SOURCE),out=resolve(process.argv[2]);
mkdirSync(out); // Preserve earlier observations; no exist_ok/overwrite.
const {createTools}=await import(pathToFileURL(resolve(root,'packages/deepviz/dist/index.js')).href);
const tool=createTools().find(value=>value.name==='render_svg');assert.ok(tool);
const rows=[{category:'A',value:2},{category:'B',value:3}];
const fixtures=[
  {name:'omitted-default',input:{data:rows},title:'Visualization',panels:1,output:2},
  {name:'dashboard',input:{data:rows,spec:{kind:'dashboard',title:'R22 helper dashboard',columns:2,
    charts:[{kind:'bar',title:'R22 first',x:'category',y:'value',aggregation:'none'},
      {kind:'bar',title:'R22 second',x:'category',y:'value',aggregation:'none'}]}},
    title:'R22 helper dashboard',panels:2,output:4},
];
const summaries=[];
for(const fixture of fixtures){
  const artifact=await tool.invoke(fixture.input);
  assert.equal(artifact.input_count,2);assert.equal(artifact.output_count,fixture.output);
  assert.equal(artifact.renderer_spec.chart_spec.title,fixture.title);assert.deepEqual(artifact.warnings,[]);
  const charts=artifact.renderer_spec.children.length?artifact.renderer_spec.children:[artifact.renderer_spec];
  assert.equal(charts.length,fixture.panels);
  for(const [index,chart] of charts.entries()){
    assert.deepEqual(chart.normalized.records,rows);assert.equal(chart.normalized.input_count,2);
    assert.match(chart.spec.svg,/<title>A: 2<\/title>/);assert.match(chart.spec.svg,/<title>B: 3<\/title>/);
    assert.match(chart.spec.svg,/>0\.000<\/text>/);
    writeFileSync(resolve(out,`${fixture.name}-${index}.svg`),chart.spec.svg);
  }
  writeFileSync(resolve(out,fixture.name+'.html'),artifact.html);
  summaries.push({name:fixture.name,title:fixture.title,input_count:artifact.input_count,
    output_count:artifact.output_count,strategy:artifact.strategy,warnings:artifact.warnings,
    child_titles:charts.map(chart=>chart.chart_spec.title),native_records:charts.map(chart=>chart.normalized.records)});
}
const summary={source_commit:'7d8ccdce22430a9ddf3a14a9e64bf15b2373ae57',actual_svg_fixtures:summaries,
  browser:{status:'NOT_RUN'}};
writeFileSync(resolve(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');
const require=createRequire(resolve(process.env.R22_READONLY_DEPS,'package.json'));
let chromium;
try{({chromium}=require('playwright'));}catch(error){
  summary.browser={status:'BLOCKED_OPTIONAL_NOT_INSTALLED',error:String(error)};
  writeFileSync(resolve(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');
  process.exitCode=2;
}
if(chromium){
  const server=createServer((req,res)=>{
    const fixture=fixtures.find(value=>req.url==='/'+value.name);
    if(fixture){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(readFileSync(resolve(out,fixture.name+'.html')));}
    else if(req.url==='/favicon.ico'){res.writeHead(204);res.end();}
    else{res.writeHead(404);res.end();}
  });
  let browser;
  try{
    browser=await chromium.launch({headless:true});
    await new Promise(ready=>server.listen(0,'127.0.0.1',ready));
    const base=`http://127.0.0.1:${server.address().port}`,controls=[];
    for(const fixture of fixtures){
      const page=await browser.newPage({viewport:{width:2000,height:800}}),errors=[],external=[];
      try{
        page.on('pageerror',error=>errors.push(String(error)));
        page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
        await page.route('**/*',route=>route.request().url().startsWith(base)?route.continue():(external.push(route.request().url()),route.abort()));
        await page.goto(base+'/'+fixture.name);await page.waitForFunction(()=>globalThis.deepvizReady===true);
        assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[]);
        assert.equal(await page.title(),fixture.title);
        assert.equal(await page.locator('h1').innerText(),fixture.title);
        assert.equal(await page.locator('.chart svg').count(),fixture.panels);
        const geometries=await page.locator('.chart svg').evaluateAll(elements=>elements.map(svg=>({
          titles:[...svg.querySelectorAll('.mark title')].map(node=>node.textContent),
          marks:[...svg.querySelectorAll('rect.mark')].map(node=>({y:Number(node.getAttribute('y')),height:Number(node.getAttribute('height'))})),
          zero:[...svg.querySelectorAll('text')].some(node=>node.textContent==='0.000'),
          box:{width:svg.getBoundingClientRect().width,right:svg.getBoundingClientRect().right},
        })));
        for(const geometry of geometries){
          assert.deepEqual(geometry.titles,['A: 2','B: 3']);assert.equal(geometry.marks.length,2);
          assert.ok(Math.abs(geometry.marks[0].height/geometry.marks[1].height-2/3)<1e-9);
          assert.ok(geometry.marks.every(mark=>Math.abs(mark.y+mark.height-455)<1e-9));
          assert.equal(geometry.zero,true);assert.ok(geometry.box.width>=900&&geometry.box.right<=2000);
        }
        await page.screenshot({path:resolve(out,fixture.name+'.png'),fullPage:true});
        assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
        controls.push({name:fixture.name,errors,external_requests:external,geometries});
      }finally{await page.close();}
    }
    summary.browser={status:'PASS',chromium:browser.version(),controls};
  }catch(error){
    summary.browser={status:'FAILED_OR_BLOCKED_NOT_PASS',error:String(error)};process.exitCode=1;
  }finally{
    writeFileSync(resolve(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');
    if(browser)await browser.close();if(server.listening)await new Promise(done=>server.close(done));
  }
}
console.log(JSON.stringify(summary,null,2));
