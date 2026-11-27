// Bounded installed-package asset checks. Never fetch or substitute a CDN runtime.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, writeFile, mkdir, realpath} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {parseArgs} from 'node:util';
const {values}=parseArgs({options:{manifest:{type:'string'},'npm-package':{type:'string'},'built-dir':{type:'string'},tarball:{type:'string'},'deps-root':{type:'string'},out:{type:'string'}}});
for(const key of ['manifest','npm-package','built-dir','tarball','deps-root','out'])assert.ok(values[key],`Missing --${key}`);
const readJson=async file=>JSON.parse((await readFile(file,'utf8')).replace(/^\uFEFF/,''));
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const npmRoot=path.resolve(values['npm-package']), deps=path.resolve(values['deps-root']), output=path.resolve(values.out);
await mkdir(output,{recursive:false});
const manifest=await readJson(values.manifest), installed=await readJson(path.join(npmRoot,'package.json'));
assert.equal(await realpath(npmRoot),npmRoot,'Installed package must not be a workspace symlink');
const {render,defaultAssets}=await import(pathToFileURL(path.join(npmRoot,'dist/index.js')).href);
const {chromium}=await import(pathToFileURL(path.join(deps,'node_modules/playwright/index.mjs')).href);
const files=[];
for(const file of ['index.js','models.js','normalize.js','render.js','renderers.js','schema.js','chart-spec.schema.json']){
  const bytes=await readFile(path.join(npmRoot,'dist',file));
  assert.deepEqual(bytes,await readFile(path.join(values['built-dir'],file)),file+' differs from pinned build');
  files.push({file:'dist/'+file,bytes:bytes.length,sha256:sha(bytes)});
}
const tar=await readFile(values.tarball);
const result={source_commit:manifest.source_commit,npm_distribution:{name:installed.name,version:installed.version,tarball_bytes:tar.length,tarball_sha256:sha(tar),installed_files:files,dependencies:installed.dependencies??{},bundled:installed.bundleDependencies??[]},defaultAssets,installed_runtime_assets:[],cases:[],limits:['Local toolkit tarball installed alone, not third-party dependency resolution.','No downloaded script executes; all non-artifact requests denied.','No full engine, geography, transitive-license or security certification.']};
for(const [name,packageName,asset] of [['vega','vega','build/vega.min.js'],['vegaLite','vega-lite','build/vega-lite.min.js'],['vegaEmbed','vega-embed','build/vega-embed.min.js'],['echarts','echarts','dist/echarts.min.js'],['antv','@antv/g2','dist/g2.min.js'],['plotly','plotly.js-dist-min','plotly.min.js']]){
  const directory=path.join(deps,'node_modules',packageName), meta=await readJson(path.join(directory,'package.json'));
  assert.ok(defaultAssets[name].includes(packageName+'@'+meta.version+'/'),'Pin/installed version mismatch');
  const bytes=await readFile(path.join(directory,asset)), notices=[];
  for(const file of ['LICENSE','LICENSE.txt','NOTICE']){
    try{const text=await readFile(path.join(directory,file));notices.push({file,bytes:text.length,sha256:sha(text)});}catch(error){if(error.code!=='ENOENT')throw error;}
  }
  result.installed_runtime_assets.push({name,package:meta.name,version:meta.version,declared_license:meta.license,asset,bytes:bytes.length,sha256:sha(bytes),notices,executed:false});
}
const cases=manifest.outputs.map(c=>({...c,language:'python',file:path.resolve(path.dirname(values.manifest),c.html)}));
for(const engine of ['vega','echarts','antv','plotly','svg'])for(const kind of ['bar','table']){
  const artifact=render([{label:'Alpha',value:3},{label:'Beta',value:9}],{kind,x:'label',y:'value',aggregation:'none',title:'Installed asset control'},engine);
  const file=path.join(output,engine+'-'+kind+'.html');await writeFile(file,artifact.html,{flag:'wx'});
  const scripts=[...artifact.html.matchAll(/<script[^>]+src="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(scripts.length,kind==='table'||engine==='svg'?0:engine==='vega'?3:1);
  cases.push({id:'npm-'+engine+'-'+kind,language:'npm',engine,kind,file,scripts,offline_expected:!scripts.length,html_sha256:sha(artifact.html)});
}
const browser=await chromium.launch({headless:true});
result.browser={version:browser.version(),playwright:(await readJson(path.join(deps,'node_modules/playwright/package.json'))).version,offline:true,serviceWorkers:'block',CDN_substitution:false};
try{
  for(const c of cases){
    const context=await browser.newContext({offline:true,serviceWorkers:'block',viewport:{width:1100,height:800}}), page=await context.newPage();
    const errors=[],exceptions=[],blocked=[],html=await readFile(c.file),origin='http://role14.invalid';
    const local=new Map([[origin+'/chart.html',{body:html,contentType:'text/html'}]]);
    if(c.language==='python'&&['matplotlib','vega'].includes(c.engine))local.set(origin+'/chart.svg',{body:await readFile(path.join(path.dirname(c.file),'chart.svg')),contentType:'image/svg+xml'});
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    page.on('pageerror',error=>exceptions.push(String(error)));
    await context.route('**/*',route=>{const url=route.request().url();if(local.has(url))return route.fulfill({status:200,...local.get(url)});if(url===origin+'/favicon.ico')return route.fulfill({status:204,body:''});blocked.push(url);return route.abort('internetdisconnected');});
    await page.goto(origin+'/chart.html',{waitUntil:'load'});
    if(c.language==='python'&&c.engine==='plotly')await page.waitForFunction(()=>[...document.querySelectorAll('[id^="chart-"][role="img"]')].every(el=>el._fullLayout));
    if(c.language==='npm')await page.waitForFunction(()=>globalThis.deepvizReady===true);
    await page.evaluate(()=>document.fonts.ready);
    const state=await page.evaluate(()=>({plotlyBars:document.querySelectorAll('.barlayer .point path').length,svgMarks:document.querySelectorAll('.chart svg rect').length,images:[...document.images].map(i=>i.complete&&i.naturalWidth>0),tableCells:document.querySelectorAll('td').length,deepvizErrors:globalThis.deepvizErrors??[],deepvizReady:typeof globalThis.deepvizReady==='boolean'?globalThis.deepvizReady:null,chartText:document.querySelector('#chart-0')?.textContent?.slice(0,160)}));
    if(c.offline_expected){
      assert.deepEqual(errors,[],c.id);assert.deepEqual(exceptions,[],c.id);assert.deepEqual(blocked,[],c.id);assert.deepEqual(state.deepvizErrors,[],c.id);
      if(c.language==='python'&&c.engine==='plotly')assert.equal(state.plotlyBars,c.id.endsWith('dashboard')?4:2,c.id);
      if(c.language==='python'&&['matplotlib','vega'].includes(c.engine))assert.deepEqual(state.images,[true],c.id);
      if(c.kind==='table')assert.equal(state.tableCells,4,c.id);
      if(c.id==='npm-svg-bar')assert.equal(state.svgMarks,2,c.id);
    }else{
      assert.deepEqual([...blocked].sort(),[...c.scripts].sort(),c.id+' unexpected network');
      assert.ok(exceptions.length||state.deepvizErrors.length,c.id+' failed to expose missing runtime');
    }
    let screenshot;
    if(['python-plotly-dashboard','npm-svg-bar','npm-echarts-bar'].includes(c.id)){screenshot=c.id+'.png';await page.screenshot({path:path.join(output,screenshot),fullPage:true});}
    result.cases.push({id:c.id,offline_expected:c.offline_expected,classification:c.offline_expected?'rendered-control':'EXPECTED-CHART-FAILURE-CDN-BLOCKED',html_sha256:sha(html),state,console_errors:errors,page_errors:exceptions,blocked,...(screenshot?{screenshot}:{})});
    await context.close();
  }
}finally{await browser.close();await writeFile(path.join(output,'offline-manifest.json'),JSON.stringify(result,null,2));}
console.log(JSON.stringify({source_commit:result.source_commit,installed_js_files:files.length,cases:result.cases.length,offline_positive:result.cases.filter(c=>c.offline_expected).length,expected_CDN_failures:result.cases.filter(c=>!c.offline_expected).length},null,2));
