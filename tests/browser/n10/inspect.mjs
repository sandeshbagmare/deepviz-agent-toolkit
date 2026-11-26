// Read-only native-artifact inspection. No request routing or dependency stubs.
import {createServer} from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {chromium} from 'playwright';
import {analyzeRaster} from '../qa.mjs';

const root=fileURLToPath(new URL('../../../',import.meta.url));
const out=path.join(root,'artifacts/local/N10');
const run=process.argv[2]??'default';
const filters=process.argv.slice(3);
const manifests=[];
for(const name of ['python','typescript']) {
  try {manifests.push(JSON.parse(await readFile(path.join(out,`${name}-manifest.json`),'utf8')));}catch(error){if(error.code!=='ENOENT')throw error;}
}
const assetPaths={vega:'vega/build/vega.min.js',vegaLite:'vega-lite/build/vega-lite.min.js',vegaEmbed:'vega-embed/build/vega-embed.min.js',echarts:'echarts/dist/echarts.min.js',antv:'@antv/g2/dist/g2.min.js',plotly:'plotly.js-dist-min/plotly.min.js'};
const server=createServer(async(req,res)=>{
  try {
    if(req.url==='/favicon.ico'){res.writeHead(204);res.end();return;}
    let file;
    if(req.url?.startsWith('/assets/')) {
      const key=req.url.slice('/assets/'.length).replace(/\.js$/,'');
      if(!assetPaths[key])throw new Error('unknown asset');
      file=path.join(root,'node_modules',assetPaths[key]);
    } else {
      const requestPath=decodeURIComponent(new URL(req.url,'http://localhost').pathname).slice(1);
      file=path.resolve(out,requestPath);
      if(!file.startsWith(out+path.sep))throw new Error('outside artifact root');
    }
    const type={'.html':'text/html; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.js':'text/javascript'}[path.extname(file)]??'application/octet-stream';
    res.writeHead(200,{'Content-Type':type});res.end(await readFile(file));
  }catch(error){res.writeHead(404,{'Content-Type':'text/plain'});res.end(String(error));}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const runDir=path.join(out,`browser-${run}`);
await mkdir(runDir); // Fresh run only: never replace earlier evidence.
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:1240,height:1000},deviceScaleFactor:1,locale:'en-US',colorScheme:'light',reducedMotion:'reduce'});
await context.addInitScript(()=>{
  // Observation only: retain actual Canvas API behavior and return values.
  globalThis.__n10drawnText=[];
  const original=CanvasRenderingContext2D.prototype.fillText;
  CanvasRenderingContext2D.prototype.fillText=function(...args){
    if(globalThis.__n10drawnText.length<10000){const t=this.getTransform();globalThis.__n10drawnText.push({text:String(args[0]),x:t.a*args[1]+t.c*args[2]+t.e,y:t.b*args[1]+t.d*args[2]+t.f,fill:this.fillStyle,font:this.font});}
    return Reflect.apply(original,this,args);
  };
});
const report={run,started_at:new Date().toISOString(),source_sha:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),
  browser:browser.version(),node:process.version,viewport:{width:1240,height:1000},manifests:manifests.map(m=>m.identity),
  mode:run.includes('local')?'Explicit local official npm assets through supported TS render options; not a default-CDN acceptance pass':'Unmodified default artifact URLs and live external resources; no routing or stubs',cases:[]};
const allCases=manifests.flatMap(m=>m.cases).filter(c=>c.path && (!run.includes('local') || c.language==='typescript')).filter(c=>!filters.length || filters.some(f=>c.id.startsWith(f)));
function nativeState(){
  const graphs=[...document.querySelectorAll('[id^="chart-"]')].filter(e=>/^chart-\d+$/.test(e.id));
  const text=[...document.querySelectorAll('svg text')].map(e=>({text:e.textContent,fill:getComputedStyle(e).fill,box:(()=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,width:b.width,height:b.height};})()}));
  const state={title:document.title,background:getComputedStyle(document.body).backgroundColor,bodyText:document.body.innerText,
    renderError:document.body.dataset.renderError??null,bootstrapErrors:globalThis.deepvizErrors??[],
    globals:{plotly:globalThis.Plotly?.version??null,echarts:globalThis.echarts?.version??null,g2:globalThis.G2?.version??(globalThis.G2?'loaded-version-not-exposed':null),vega:globalThis.vega?.version??null,vegaLite:globalThis.vegaLite?.version??null,vegaEmbed:globalThis.vegaEmbed?.version??null},
    image:[...document.images].map(i=>({src:i.getAttribute('src'),complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight})),
    svgText:text,canvasText:globalThis.__n10drawnText??[],graphs:[]};
  for(const el of graphs){
    const box=el.getBoundingClientRect();
    const graph={id:el.id,box:{x:box.x,y:box.y,width:box.width,height:box.height},svg:el.querySelectorAll('svg').length,canvas:el.querySelectorAll('canvas').length,
      marks:[...el.querySelectorAll('path,rect,circle,ellipse,polyline')].slice(0,400).map(p=>{
        const b=p.getBoundingClientRect();return{tag:p.tagName,cls:p.getAttribute('class'),aria:p.getAttribute('aria-label'),d:p.getAttribute('d'),points:p.getAttribute('points'),title:p.querySelector('title')?.textContent,
          fill:getComputedStyle(p).fill,stroke:getComputedStyle(p).stroke,box:{x:b.x,y:b.y,width:b.width,height:b.height}};}),
      canvasObjects:[...el.querySelectorAll('canvas')].map(c=>({width:c.width,height:c.height,keys:Object.keys(c)}))};
    if(el.data){
      graph.plotly={data:el.data,fullData:el._fullData?.map(t=>({type:t.type,name:t.name,x:t.x,y:t.y,values:t.values,labels:t.labels,z:t.z,mode:t.mode,visible:t.visible})),
        calcdata:el.calcdata?.map(items=>items.slice(0,20).map(d=>({x:d.x,y:d.y,p:d.p,s:d.s,label:d.label,v:d.v,pts:d.pts}))),
        axes:{x:{type:el._fullLayout?.xaxis?.type,range:el._fullLayout?.xaxis?.range},y:{type:el._fullLayout?.yaxis?.type,range:el._fullLayout?.yaxis?.range}}};
    }
    const ec=globalThis.echarts?.getInstanceByDom(el);
    if(ec){graph.echarts={option:ec.getOption(),series:ec.getModel().getSeries().map(s=>{
      const d=s.getData();return{name:s.name,type:s.subType,dimensions:d.dimensions,items:Array.from({length:d.count()},(_,i)=>({name:d.getName(i),values:d.dimensions.map(k=>d.get(k,i)),layout:d.getItemLayout(i),style:d.getItemVisual(i,'style')}))};})};}
    state.graphs.push(graph);
  }
  return state;
}
try{
  for(const c of allCases){
    const r={id:c.id,language:c.language,engine:c.engine,case:c.case,oracle:c.oracle,path:run.includes('local')?c.local_path:c.path,
      consoleErrors:[],consoleWarnings:[],pageErrors:[],failedRequests:[],resources:[],checks:[],errors:[]};
    const page=await context.newPage();
    const bodies=[];
    page.on('console',m=>{if(m.type()==='error')r.consoleErrors.push(m.text());if(m.type()==='warning')r.consoleWarnings.push(m.text());});
    page.on('pageerror',e=>r.pageErrors.push(String(e)));
    page.on('requestfailed',q=>r.failedRequests.push({url:q.url(),error:q.failure()?.errorText}));
    page.on('response',response=>{
      const entry={url:response.url(),status:response.status(),type:response.request().resourceType()};r.resources.push(entry);
      if(entry.type==='script')bodies.push(response.body().then(body=>{entry.bytes=body.length;entry.sha256=createHash('sha256').update(body).digest('hex');}).catch(e=>{entry.bodyError=String(e);}));
    });
    try{
      await page.goto(`${base}/${r.path}`,{waitUntil:'load',timeout:35000});
      if(c.language==='python' && ['matplotlib','vega'].includes(c.engine)){
        await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0),{},{timeout:10000});
      } else if(c.language==='python'){
        await page.evaluate(async()=>{if(globalThis.deepvizReady)await globalThis.deepvizReady;});
      } else {
        await page.waitForFunction(()=>globalThis.deepvizReady===true,{},{timeout:15000});
      }
      await page.waitForTimeout(500);
      r.state=await page.evaluate(nativeState);
      if(c.language==='python' && ['matplotlib','vega'].includes(c.engine)){
        const img=page.locator('figure img');const src=await img.getAttribute('src');
        const svg=await page.request.get(new URL(src,page.url()).href);
        r.staticSvg={url:svg.url(),status:svg.status(),sha256:createHash('sha256').update(await svg.body()).digest('hex'),
          description:'Actual native static engine SVG, rendered as companion HTML image; human screenshot inspection required.'};
      }
      await page.screenshot({path:path.join(runDir,`${c.id}.png`),fullPage:true,animations:'disabled'});
      const regions=c.language==='python'&&['matplotlib','vega'].includes(c.engine)?page.locator('figure img'):page.locator('[id^="chart-"]').filter({has:page.locator('svg,canvas')});
      r.regionCount=await regions.count();
      r.rasters=[];
      const analyzer=await context.newPage();
      for(let i=0;i<r.regionCount;i++){
        const image=await regions.nth(i).screenshot({animations:'disabled'});
        await writeFile(path.join(runDir,`${c.id}-region-${i}.png`),image);
        r.rasters.push(await analyzer.evaluate(analyzeRaster,{png:image.toString('base64')}));
      }
      await analyzer.close();
      const check=(name,pass,detail)=>{r.checks.push({name,pass,detail});if(!pass)r.errors.push(`${name}: ${detail}`);};
      check('console clean',r.consoleErrors.length===0,JSON.stringify(r.consoleErrors));
      check('uncaught exceptions clean',r.pageErrors.length===0,JSON.stringify(r.pageErrors));
      check('bootstrap clean',!r.state.renderError&&r.state.bootstrapErrors.length===0,JSON.stringify([r.state.renderError,r.state.bootstrapErrors]));
      check('no failed resource loads',r.failedRequests.length===0,JSON.stringify(r.failedRequests));
      const expectedPanels=c.case==='dashboard'?2:1;
      if(c.language==='python'&&['matplotlib','vega'].includes(c.engine))check('native static image loads',r.state.image.length===1&&r.state.image[0].naturalWidth>0,JSON.stringify(r.state.image));
      else check('native renderer panel count',r.regionCount===expectedPanels,`${r.regionCount} actual SVG/canvas regions, expected ${expectedPanels}`);
      // Three small native scatter glyphs can legitimately occupy <150 pixels;
      // preserve nonblank/ink checks, and review exact count/coordinates separately.
      const minimumColored=c.case==='scatter'?60:150;
      for(const [index,raster]of r.rasters.entries())check(`panel ${index} nonempty`,raster.inkPixels>500&&raster.coloredPixels>minimumColored,JSON.stringify(raster));
      if(c.case==='darkbar')check('dark body background',r.state.background!=='rgb(255, 255, 255)',r.state.background);
      const versions=r.state.globals;
      if(c.engine==='plotly')check('real Plotly loaded',Boolean(versions.plotly),JSON.stringify(versions));
      if(c.engine==='echarts')check('real ECharts loaded',Boolean(versions.echarts),JSON.stringify(versions));
      if(c.engine==='antv')check('real G2 loaded',Boolean(versions.g2),JSON.stringify(versions));
      if(c.engine==='vega'&&c.language==='typescript')check('real Vega stack loaded',Boolean(versions.vega&&versions.vegaLite&&versions.vegaEmbed),JSON.stringify(versions));
      r.status=r.errors.length?'failed':'native-runtime-checks-passed-human-semantics-required';
    }catch(error){r.status='failed';r.errors.push(String(error));try{await page.screenshot({path:path.join(runDir,`${c.id}-failure.png`),fullPage:true});}catch{}}
    await Promise.allSettled(bodies);
    await page.close();
    if(r.consoleErrors.length||r.pageErrors.length||r.failedRequests.length)r.status='failed';
    report.cases.push(r);
    console.log(r.id,r.status,r.errors.join(' | '));
    await writeFile(path.join(runDir,'report.json'),JSON.stringify(report,null,2));
  }
}finally{
  report.finished_at=new Date().toISOString();
  report.total=report.cases.length;report.failed=report.cases.filter(c=>c.status==='failed').length;report.runtime_pass=report.total-report.failed;
  await writeFile(path.join(runDir,'report.json'),JSON.stringify(report,null,2));
  await browser.close();await new Promise(resolve=>server.close(resolve));
}
console.log(JSON.stringify({run,total:report.total,failed:report.failed,runtime_pass:report.runtime_pass,report:path.join(runDir,'report.json')},null,2));
process.exitCode=Number(report.failed>0);
