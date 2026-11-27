import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
import {assess,negativeControls} from './oracle.mjs';

const directory=path.resolve(process.argv[2]||'');
const manifest=JSON.parse(await readFile(path.join(directory,'manifest.json'),'utf8'));
const capture=path.join(directory,'browser-viewport');await mkdir(capture,{recursive:false});
const browser=await chromium.launch({headless:true});
const report={source_sha:manifest.source_sha,chromium:browser.version(),cases:[],negativeControls:[],limits:[
  'Only the exact SVG adapter checkpoint and literal tiny fixtures; not other engines, density, scaling, packages or latest MAIN.',
  'Standalone SVG contains its first public native SVG; optional HTML legend tested on real HTML artifact only.',
  'All-negative domain includes inherited maximum1; tests require correct zero mapping, not a new axis-domain policy.',
]};
try{
  for(const fixture of manifest.cases){
    for(const format of ['svg','html']){
      const page=await browser.newPage({viewport:{width:1250,height:1600},deviceScaleFactor:1});
      page.setDefaultTimeout(10000);page.setDefaultNavigationTimeout(10000);
      const errors=[],networkFailures=[],externalRequests=[];
      page.on('console',message=>{if(message.type()==='error')errors.push(`console: ${message.text()}`);});
      page.on('pageerror',error=>errors.push(`pageerror: ${error.message}`));
      page.on('requestfailed',request=>networkFailures.push({url:request.url(),error:request.failure()?.errorText}));
      page.on('request',request=>{if(/^https?:/.test(request.url()))externalRequests.push(request.url());});
      let row;
      try{
        await page.goto(pathToFileURL(path.join(directory,fixture[format])).href,{waitUntil:'load'});
        if(format==='html')await page.waitForFunction(()=>globalThis.deepvizReady===true);
        const measured=await page.evaluate(()=>{
          const root=document.querySelector('svg[role="img"]');if(!root)throw new Error('Missing native root SVG');
          const box=element=>{const b=element.getBBox(),matrix=root.getCTM().inverse().multiply(element.getCTM());
            const corners=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]]
              .map(([x,y])=>new DOMPoint(x,y).matrixTransform(matrix));
            const xs=corners.map(point=>point.x),ys=corners.map(point=>point.y);
            return{x:Math.min(...xs),y:Math.min(...ys),width:Math.max(...xs)-Math.min(...xs),height:Math.max(...ys)-Math.min(...ys)};};
          const rect=element=>{const b=element.getBoundingClientRect();return{x:b.x,y:b.y,width:b.width,height:b.height,right:b.right,bottom:b.bottom};};
          const label=element=>[...element.childNodes].filter(node=>node.nodeType===Node.TEXT_NODE).map(node=>node.textContent).join('');
          const text=element=>({text:label(element),title:element.querySelector('title')?.textContent||null,box:box(element),
            x:element.x.baseVal[0]?.value??null,y:element.y.baseVal[0]?.value??null,rect:rect(element)});
          const axis=root.querySelector('g>path');
          return {root:{width:root.viewBox.baseVal.width,height:root.viewBox.baseVal.height},rootViewport:rect(root),
            axis:axis?box(axis):null,texts:[...root.querySelectorAll('text')].map(text),
            yTicks:[...root.querySelectorAll('g>text:not(.category-tick):not([transform])')].slice(0,2).map(text),
            categoryTicks:[...root.querySelectorAll('.category-tick')].map(text),
            marks:[...root.querySelectorAll('.mark')].map(mark=>{const style=getComputedStyle(mark);return{
              tag:mark.localName,box:box(mark),rect:rect(mark),title:mark.querySelector('title')?.textContent||null,
              fill:style.fill,stroke:style.stroke,strokeWidth:Number.parseFloat(style.strokeWidth),opacity:style.opacity,
              fillOpacity:Number(style.fillOpacity),display:style.display,visibility:style.visibility,
              cx:mark.cx?.baseVal.value??null,cy:mark.cy?.baseVal.value??null,r:mark.r?.baseVal.value??null,
              points:mark.points?[...mark.points].map(point=>[point.x,point.y]):null,d:mark.getAttribute('d')};}),
            tableRows:[...document.querySelectorAll('details tbody tr')].map(tr=>[...tr.querySelectorAll('td')].map(td=>td.textContent)),
            legend:[...document.querySelectorAll('ul[aria-label="Category key"] li')].map(li=>({label:li.textContent.trim(),
              fill:getComputedStyle(li.querySelector('circle')).fill,rect:rect(li)})),
            ready:globalThis.deepvizReady??null,deepvizErrors:globalThis.deepvizErrors??[],
            viewport:{width:innerWidth,height:innerHeight},htmlTitle:document.querySelector('h2')?.textContent??null};
        });
        const state={...measured,errors,networkFailures,externalRequests};
        const checks=assess(fixture,state,format);
        checks.push({name:'public-literal-title',pass:format==='svg'||state.htmlTitle===`R18 ${fixture.id}`,observed:state.htmlTitle});
        const screenshot=`${fixture.id}-${format}.png`;
        // Chromium/Playwright fullPage XML screenshot times out; real SVG viewport clipping does not alter XML bytes.
        const svgClip={x:state.rootViewport.x,y:state.rootViewport.y,width:state.rootViewport.width,height:state.rootViewport.height};
        await page.screenshot({path:path.join(capture,screenshot),...(format==='svg'?{clip:svgClip}:{fullPage:true}),timeout:10000});
        const bytes=await readFile(path.join(capture,screenshot));
        row={id:fixture.id,format,checks,state,screenshot,sha256:createHash('sha256').update(bytes).digest('hex')};
        if(fixture.id==='area-scientific-240' && format==='svg'){
          // Only measured copies are corrupted: production HTML/native payload is never mutated to manufacture a pass.
          report.negativeControls.push(...negativeControls(fixture,state,format));
        }
      }catch(error){row={id:fixture.id,format,checks:[{name:'actual-browser-execution',pass:false,observed:String(error)}],errors,networkFailures};}
      report.cases.push(row);
      await writeFile(path.join(directory,'browser-progress-viewport.json'),JSON.stringify(report,null,2));
      console.log(`${fixture.id} ${format}: ${row.checks.filter(check=>!check.pass).length}/${row.checks.length} failed`);
      await page.close();
    }
  }
}finally{await browser.close();}
report.counts={artifacts:report.cases.length,checks:report.cases.reduce((n,row)=>n+row.checks.length,0),
  failures:report.cases.reduce((n,row)=>n+row.checks.filter(check=>!check.pass).length,0),
  negative_controls:report.negativeControls.length,negative_controls_failed:report.negativeControls.filter(row=>!row.rejected).length,
  unsupported:manifest.unsupported.length,skipped:0};
report.failures=report.cases.flatMap(row=>row.checks.filter(check=>!check.pass).map(check=>({id:row.id,format:row.format,...check})));
await writeFile(path.join(directory,'browser-report-viewport.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({source_sha:report.source_sha,counts:report.counts,failures:report.failures,negativeControls:report.negativeControls},null,2));
assert.equal(report.counts.negative_controls_failed,0,'Oracle corruption control failed');
process.exitCode=report.counts.failures?1:0;
