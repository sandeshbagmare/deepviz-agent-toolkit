// Real Python StructuredTool HTML host. Controlled denial/local exact bytes; never change HTML/bootstrap.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {parseArgs} from 'node:util';
const {values}=parseArgs({options:{manifest:{type:'string'},'deps-root':{type:'string'},'prior-inventory':{type:'string'},out:{type:'string'}}});
for(const key of ['manifest','deps-root','prior-inventory','out'])assert.ok(values[key],`Missing --${key}`);
const json=async file=>JSON.parse((await readFile(file,'utf8')).replace(/^\uFEFF/,''));
const sha=body=>createHash('sha256').update(body).digest('hex');
const manifest=await json(values.manifest), prior=await json(values['prior-inventory']), base=path.dirname(path.resolve(values.manifest)), output=path.resolve(values.out), deps=path.resolve(values['deps-root']);
assert.equal(manifest.source_commit,'7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6');
await mkdir(output,{recursive:false});
const {chromium}=await import(pathToFileURL(path.join(deps,'node_modules/playwright/index.mjs')).href);
const assets=new Map(), inventory=[];
for(const engine of ['echarts','antv']){
  const old=prior.installed_runtime_assets.find(a=>a.name===engine);assert.ok(old);
  const directory=path.join(deps,'node_modules',old.package), meta=await json(path.join(directory,'package.json')), body=await readFile(path.join(directory,old.asset));
  assert.equal(meta.version,old.version);assert.equal(sha(body),old.sha256);
  const item=manifest.artifacts.find(a=>a.engine===engine);assert.equal(item.external_scripts.length,1);
  assets.set(item.external_scripts[0],body);inventory.push({engine,package:meta.name,version:meta.version,sha256:sha(body),bytes:body.length,mode:'EXISTING exact local runtime bytes supplied at emitted URL; not live CDN health'});
}
const browser=await chromium.launch({headless:true});
const result={source_commit:manifest.source_commit,tool_adapter:'Actual create_tools StructuredTool.invoke, no LLM/provider',browser:{version:browser.version(),playwright:(await json(path.join(deps,'node_modules/playwright/package.json'))).version,serviceWorkers:'block',offline_context:true},runtime_inventory:inventory,cases:[],limits:['The denial fixture aborts exact external URLs intentionally; ERR_FAILED is expected resource evidence, not live outage.','No payload/HTML/bootstrap/fake library replacement. Local positive supplies only preexisting hash-verified real runtime bytes.','Bounded host1500ms ready-promise discovery is an observer deadline, not a public product timeout contract.','No end-to-end DeepAgent model/provider run, all-engine/kind/CDN-health claim.']};
try{
  for(const fixture of [{engine:'echarts',mode:'denied'},{engine:'antv',mode:'denied'},{engine:'matplotlib',mode:'static-offline'},{engine:'echarts',mode:'existing-local-runtime'},{engine:'antv',mode:'existing-local-runtime'}]){
    const artifact=manifest.artifacts.find(a=>a.engine===fixture.engine), htmlPath=path.resolve(base,artifact.html), html=await readFile(htmlPath);
    assert.equal(sha(html),artifact.files.find(f=>f.file===artifact.html).sha256,'HTML bytes changed');
    const context=await browser.newContext({offline:true,serviceWorkers:'block',viewport:{width:1000,height:800}}),page=await context.newPage();
    const denied=[],supplied=[],resourceFailures=[],consoleErrors=[],pageErrors=[],unexpectedRequests=[];
    const origin='http://r21-role14.invalid', local=new Map([[origin+'/chart.html',{body:html,contentType:'text/html'}]]);
    for(const image of artifact.images){assert.equal(image,'chart.svg');local.set(origin+'/'+image,{body:await readFile(path.join(path.dirname(htmlPath),image)),contentType:'image/svg+xml'});}
    page.on('console',msg=>{if(msg.type()==='error')consoleErrors.push(msg.text());});page.on('pageerror',error=>pageErrors.push(String(error)));
    page.on('requestfailed',request=>resourceFailures.push({url:request.url(),error:request.failure()?.errorText}));
    await context.route('**/*',route=>{const url=route.request().url();if(local.has(url))return route.fulfill({status:200,...local.get(url)});if(url===origin+'/favicon.ico')return route.fulfill({status:204,body:''});if(fixture.mode==='existing-local-runtime'&&assets.has(url)){supplied.push({url,sha256:sha(assets.get(url))});return route.fulfill({status:200,contentType:'text/javascript',body:assets.get(url)});}if(artifact.external_scripts.includes(url))denied.push(url);else unexpectedRequests.push(url);return route.abort('failed');});
    await page.goto(origin+'/chart.html',{waitUntil:'load',timeout:15000});
    let hostWait='not-applicable-static',readyOutcome='not-applicable-static';const start=performance.now();
    if(fixture.engine!=='matplotlib'){
      try{await page.waitForFunction(()=>globalThis.deepvizReady&&typeof globalThis.deepvizReady.then==='function',null,{timeout:1500});hostWait='promise-present';}
      catch(error){if(error.name!=='TimeoutError')throw error;hostWait='observer-timeout-no-promise';}
      readyOutcome=await page.evaluate(async()=>{try{const value=await Promise.race([globalThis.deepvizReady,new Promise(resolve=>setTimeout(()=>resolve('__HOST_TIMEOUT__'),1500))]);return value==='__HOST_TIMEOUT__'?'host-timeout':'fulfilled';}catch(error){return 'rejected:'+String(error);}});
    }
    const hostElapsedMs=performance.now()-start;
    await page.evaluate(()=>document.fonts.ready);
    const state=await page.evaluate(()=>({readyType:typeof globalThis.deepvizReady,readyThenType:typeof globalThis.deepvizReady?.then,renderError:document.body.dataset.renderError??null,visibleErrorText:[...document.querySelectorAll('[role="alert"],[role="status"]')].map(e=>e.textContent),chartText:document.querySelector('#chart-0')?.textContent??null,chartChildren:document.querySelector('#chart-0')?.childElementCount??null,chartGraphics:document.querySelectorAll('#chart-0 svg,#chart-0 canvas').length,loadingIndicators:document.querySelectorAll('[aria-busy="true"],[role="progressbar"]').length,bodyText:document.body.innerText,title:document.querySelector('h1')?.textContent,literalElements:document.querySelectorAll('literal').length,tableCells:[...document.querySelectorAll('td')].map(e=>e.textContent),tableHeaders:[...document.querySelectorAll('th')].map(e=>({text:e.textContent,scope:e.scope})),tableCaption:document.querySelector('caption')?.textContent,summaryText:document.querySelector('summary')?.textContent,detailsOpen:document.querySelector('details')?.open,embeddedSpec:document.querySelector('#deepviz-data')?JSON.parse(document.querySelector('#deepviz-data').textContent):null,images:[...document.images].map(i=>({complete:i.complete,width:i.naturalWidth,height:i.naturalHeight,alt:i.alt})),echartsValues:globalThis.echarts?echarts.getInstanceByDom(document.querySelector('#chart-0'))?.getOption()?.series?.[0]?.data:null}));
    assert.equal(state.title,manifest.spec.title);assert.equal(state.literalElements,0);assert.deepEqual(state.tableCells,['A & B','3','C < D','9']);assert.deepEqual(unexpectedRequests,[]);
    if(fixture.mode==='denied'){
      assert.deepEqual(denied,artifact.external_scripts);assert.equal(state.chartGraphics,0);assert.equal(supplied.length,0);
    }else{
      assert.deepEqual(denied,[]);assert.deepEqual(resourceFailures,[]);assert.deepEqual(consoleErrors,[]);assert.deepEqual(pageErrors,[]);
      if(fixture.engine==='matplotlib'){assert.deepEqual(supplied,[]);assert.equal(state.images[0]?.complete,true);assert.ok(state.images[0]?.width>0);}
      else{assert.equal(hostWait,'promise-present');assert.equal(readyOutcome,'fulfilled');assert.ok(state.chartGraphics>0);assert.equal(supplied.length,1);}
      if(fixture.engine==='echarts')assert.deepEqual(state.echartsValues,[['A & B',3],['C < D',9]]);
    }
    const id=fixture.engine+'-'+fixture.mode,screenshot=id+'.png';await page.screenshot({path:path.join(output,screenshot),fullPage:true});
    const initialAccessible=await page.locator('body').ariaSnapshot();
    await page.locator('summary').focus();await page.keyboard.press('Enter');
    assert.equal(await page.locator('details').evaluate(e=>e.open),true);assert.equal(await page.getByRole('table').count(),1);
    const openedAccessible=await page.locator('body').ariaSnapshot();assert.ok(openedAccessible.includes('A & B')&&openedAccessible.includes('C < D'));
    await page.screenshot({path:path.join(output,id+'-fallback-open.png'),fullPage:true});
    result.cases.push({id,...fixture,html_sha256:sha(html),host_promise_discovery:hostWait,naive_await_ready_outcome:readyOutcome,host_observation_ms:hostElapsedMs,state,blocked:denied,local_runtime_supplied:supplied,resource_failures:resourceFailures,expected_fixture_ERR_FAILED:consoleErrors.filter(error=>error.includes('net::ERR_FAILED')),unexpected_console_errors:consoleErrors.filter(error=>!error.includes('net::ERR_FAILED')),page_errors:pageErrors,unexpected_requests:unexpectedRequests,initial_accessible_snapshot:initialAccessible,keyboard_opened_accessible_snapshot:openedAccessible,screenshot,fallback_screenshot:id+'-fallback-open.png',classification:fixture.mode==='denied'?'EXPECTED-INTERACTIVE-FAILURE; failure/readiness UX evaluated separately':'REAL-POSITIVE-CONTROL'});
    await context.close();
  }
}finally{await browser.close();await writeFile(path.join(output,'host-observations.json'),JSON.stringify(result,null,2));}
console.log(JSON.stringify({source_commit:result.source_commit,cases:result.cases.length,real_positive_controls:result.cases.filter(c=>c.mode!=='denied').length,controlled_denial_fixtures:result.cases.filter(c=>c.mode==='denied').length,downloaded_code_executed:false,meaning:'Host observation completed, NOT product UX/safety/final signoff.'},null,2));
