import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {test,before,after} from 'node:test';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
import {fixtures} from './fixtures.mjs';
import {baselineSha,proveSource,sha256} from './identity.mjs';
import {assess} from './oracle.mjs';

assert(process.env.R24_SOURCE&&process.env.R24_OUTPUT,'Explicit immutable source and NEW unique output are required');
const source=path.resolve(process.env.R24_SOURCE),output=path.resolve(process.env.R24_OUTPUT);
const expected=process.env.R24_EXPECTED_SHA??baselineSha;
const reference=path.resolve(process.env.R24_BUILD_PROOF??'docs/coordination/evidence/R18-06/identity.json');
const identity=await proveSource(source,expected,reference);
const {render,normalize}=await import(identity.public_module);
assert.equal(typeof render,'function');assert.equal(typeof normalize,'function');
assert.equal(fixtures.length,8);assert(fixtures.every(fixture=>fixture.records.every(record=>Object.values(record).every(Number.isFinite))));
await mkdir(output,{recursive:false});await mkdir(path.join(output,'captures'));
await writeFile(path.join(output,'identity.json'),JSON.stringify(identity,null,2));
await writeFile(path.join(output,'fixtures.json'),JSON.stringify(fixtures,null,2));
let browser;
const result={source_sha:expected,argv:process.argv,cwd:process.cwd(),cases:[],counts:{}};
before(async()=>{browser=await chromium.launch({headless:true});result.chromium=browser.version();});
after(async()=>{
  await browser?.close();
  const finalProof=await proveSource(source,expected,reference);
  assert.deepEqual(finalProof.sourceProof,identity.sourceProof);assert.deepEqual(finalProof.buildProof,identity.buildProof);
  result.source_and_build_hashes_unchanged_after_browser=true;
  result.counts={cases:result.cases.length,correct_rendered:result.cases.filter(row=>row.outcome==='correct-rendered').length,
    honest_rejections:result.cases.filter(row=>row.outcome==='honest-explicit-rejection').length,
    failed_success_artifacts:result.cases.filter(row=>row.outcome==='failed-success-artifact').length,
    checks:result.cases.reduce((n,row)=>n+row.checks.length,0),failures:result.cases.reduce((n,row)=>n+row.checks.filter(check=>!check.pass).length,0),
    observed_browser_errors:result.cases.reduce((n,row)=>n+(row.state?.errors?.length??0),0),external_requests:result.cases.reduce((n,row)=>n+(row.state?.requests?.length??0),0),
    captures:result.cases.filter(row=>row.capture).length,harness_errors:result.cases.filter(row=>row.harness_error).length,skipped:0};
  await writeFile(path.join(output,'report.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result.counts));
});

for(const fixture of fixtures)test(`R24 ${fixture.id}: finite literal quantitative layout or clear honest rejection`,{timeout:15000},async()=>{
  const input=structuredClone(fixture.records),row={id:fixture.id,kind:fixture.kind,extreme:fixture.extreme};
  let page;
  try{
    row.normalized=normalize(input,fixture.spec);
    let artifact;
    try{artifact=render(input,fixture.spec,'svg');row.artifactReturned=true;}
    catch(error){row.error={name:error.name,message:error.message};row.artifactReturned=false;}
    row.inputAfter=input;
    if(artifact){
      const svg=String(artifact.renderer_spec.spec.svg);
      row.artifact={input_count:artifact.input_count,output_count:artifact.output_count,strategy:artifact.strategy,warnings:artifact.warnings,
        records:artifact.renderer_spec.normalized.records};
      await writeFile(path.join(output,`${fixture.id}.svg`),svg);
      const htmlFile=path.join(output,`${fixture.id}.html`);await writeFile(htmlFile,artifact.html);
      const marks=[...svg.matchAll(/<(polyline|circle) class="mark"([^>]+)>/g)].map(match=>({tag:match[1],attributes:Object.fromEntries([...match[2].matchAll(/([\w-]+)="([^"]*)"/g)].map(item=>[item[1],item[2]]))}));
      const points=marks.flatMap(mark=>mark.tag==='circle'?[[Number(mark.attributes.cx),Number(mark.attributes.cy)]]:
        mark.attributes.points.trim().split(/\s+/).map(pair=>pair.split(',').map(Number)));
      row.native={svg,svg_sha256:sha256(svg),html_sha256:sha256(artifact.html),marks,attributes:marks.map(mark=>mark.attributes),points};
      page=await browser.newPage({viewport:{width:1200,height:900},deviceScaleFactor:1});
      page.setDefaultTimeout(5000);page.setDefaultNavigationTimeout(5000);
      const errors=[],requests=[];
      page.on('console',message=>{if(message.type()==='error')errors.push({kind:'console',message:message.text()});});
      page.on('pageerror',error=>errors.push({kind:'pageerror',message:error.message}));
      page.on('request',request=>{if(!request.url().startsWith('file:'))requests.push(request.url());});
      await page.goto(pathToFileURL(htmlFile).href,{waitUntil:'load'});
      await page.waitForFunction(()=>globalThis.deepvizReady===true);
      row.state=await page.evaluate(()=>{
        const root=document.querySelector('svg[role="img"]'),axisPath=root.querySelector('g > path');
        const axisValues=axisPath.getAttribute('d').match(/[-+]?(?:\d*\.)?\d+(?:e[-+]?\d+)?/gi).map(Number);
        const box=element=>{const b=element.getBBox(),m=element.getCTM();const corners=[[b.x,b.y],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
          return {x:Math.min(...corners.map(p=>p.x)),y:Math.min(...corners.map(p=>p.y)),width:Math.abs(corners[1].x-corners[0].x),height:Math.abs(corners[1].y-corners[0].y)};};
        const marks=[...root.querySelectorAll('.mark')].map(mark=>({tag:mark.tagName,points:mark.tagName==='polyline'?[...mark.points].map(p=>[p.x,p.y]):[[mark.cx.baseVal.value,mark.cy.baseVal.value]],
          r:mark.tagName==='circle'?mark.r.baseVal.value:null,box:box(mark),fill:getComputedStyle(mark).fill,stroke:getComputedStyle(mark).stroke}));
        const texts=[...root.querySelectorAll('text')],textBoxes=texts.map(text=>({literal:text.textContent,box:box(text)}));
        const ticks=[...root.querySelectorAll('.category-tick')].map(tick=>({literal:tick.querySelector('title').textContent,x:Number(tick.getAttribute('x')),box:box(tick)}));
        const overlaps=(a,b)=>a.x<b.x+b.width-0.1&&b.x<a.x+a.width-0.1&&a.y<b.y+b.height-0.1&&b.y<a.y+a.height-0.1;
        const viewport=root.getBoundingClientRect();
        return {ready:globalThis.deepvizReady,deepvizErrors:globalThis.deepvizErrors,title:document.title,width:Number(root.getAttribute('width')),height:Number(root.getAttribute('height')),
          axis:{left:axisValues[0],top:axisValues[1],bottom:axisValues[2],right:axisValues[3]},marks,points:marks.flatMap(mark=>mark.points),ticks,textBoxes,
          painted:marks.length>0&&marks.every(mark=>(mark.box.width>0||mark.box.height>0)&&(mark.fill!=='none'||mark.stroke!=='none')),
          textInside:textBoxes.every(({box:b})=>b.x>=-0.2&&b.y>=-0.2&&b.x+b.width<=viewport.width+0.2&&b.y+b.height<=viewport.height+0.2),
          tickOverlap:ticks.some((tick,i)=>ticks.slice(i+1).some(other=>overlaps(tick.box,other.box))),
          table:[...document.querySelectorAll('tbody tr')].map(tr=>[...tr.querySelectorAll('td')].map(td=>td.textContent)),
          viewport:{x:viewport.x,y:viewport.y,width:viewport.width,height:viewport.height}};
      });
      row.state.errors=errors;row.state.requests=requests;
      if(fixture.kind==='area'){
        const capture=path.join(output,'captures',`${fixture.id}.png`);
        await page.screenshot({path:capture,clip:row.state.viewport,timeout:5000});
        row.capture={file:path.relative(output,capture),sha256:sha256(await readFile(capture))};
      }
    }
    row.checks=assess(fixture,row);
    const failures=row.checks.filter(check=>!check.pass);
    row.outcome=failures.length?'failed-success-artifact':row.error?'honest-explicit-rejection':'correct-rendered';
    result.cases.push(row);await writeFile(path.join(output,'progress.json'),JSON.stringify(result,null,2));
    assert.deepEqual(failures.map(check=>check.name),[],JSON.stringify(failures));
  }catch(error){
    if(!row.checks){
      row.harness_error={name:error.name,message:error.message};row.outcome='unexpected-harness-error';
      row.checks=[{name:'all-new-fixture-observations-completed',pass:false,observed:row.harness_error}];
      result.cases.push(row);await writeFile(path.join(output,'progress.json'),JSON.stringify(result,null,2));
    }
    throw error;
  }finally{await page?.close();}
});
