import assert from 'node:assert/strict';
import {execFileSync,spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=fileURLToPath(new URL('../../../',import.meta.url));
const defaultEntry=fileURLToPath(new URL('../dist/index.js',import.meta.url));
const tiers=[10,1_000,100_000,1_000_000,10_000_000];
const caps={heap_bytes:256*1024**2,rss_bytes:768*1024**2,elapsed_ms:180_000};

export function exactSum(size){const n=BigInt(size);return n*(n+1n)/2n;}

/** The iterator throws on replay and never owns a collection of input rows. */
export function oneShotRecords(size,{unique=false,observe=()=>{}}={}){
  const stats={iterations:0,consumed:0,completed:false};
  const source={
    [Symbol.iterator](){
      if(stats.iterations++)throw new Error('N21 source replay is forbidden');
      return (function*(){
        for(let i=0;i<size;i++){
          if(i%8192===0)observe();
          stats.consumed++;
          yield {group:`g${unique?i:i%8}`,value:i+1,seq:i};
        }
        stats.completed=true;
      })();
    },
  };
  return {source,stats};
}

export async function runScaleCase({size,mode,entry=process.env.N21_PACKAGE_ENTRY??defaultEntry,outputDir}){
  assert.ok(Number.isSafeInteger(size)&&size>0&&size<=10_000_000,'safe tier required');
  assert.ok(['sum','sample'].includes(mode),'supported case required');
  await mkdir(outputDir,{recursive:true});
  const api=await import(pathToFileURL(resolve(entry)).href);
  globalThis.gc?.();
  const baseline=process.memoryUsage();
  let peakHeap=baseline.heapUsed,peakRss=baseline.rss,samples=0;
  const started=performance.now();
  function observe(){
    const current=process.memoryUsage();samples++;
    peakHeap=Math.max(peakHeap,current.heapUsed);peakRss=Math.max(peakRss,current.rss);
    assert.ok(current.heapUsed<caps.heap_bytes,'N21 sampled heap cap exceeded');
    assert.ok(current.rss<caps.rss_bytes,'N21 sampled RSS cap exceeded');
    assert.ok(performance.now()-started<caps.elapsed_ms,'N21 elapsed cap exceeded');
  }
  const {source,stats}=oneShotRecords(size,{observe});
  const spec=mode==='sum'
    ?{kind:'bar',title:`N21 ${size.toLocaleString('en-US')} streamed rows: exact grouped sums`,x:'group',y:'value',aggregation:'sum',max_points:10,width:960,height:540}
    :{kind:'line',x:'seq',y:'value',aggregation:'sample',max_points:64};
  let normalized,artifact;
  try{
    if(mode==='sum'){
      artifact=await api.renderStream(source,spec,'svg');
      normalized=artifact.renderer_spec.normalized;
    }else normalized=await api.normalizeStream(source,spec);
    observe();
    assert.equal(stats.iterations,1);assert.equal(stats.completed,true);assert.equal(stats.consumed,size);
    assert.equal(normalized.input_count,size);
    assert.equal(normalized.strategy,mode);
    assert.equal(normalized.records.length,Math.min(size,mode==='sum'?8:64));
    if(mode==='sum'){
      assert.equal(normalized.records.reduce((sum,row)=>sum+BigInt(row.value),0n),exactSum(size));
      for(let bucket=0;bucket<Math.min(8,size);bucket++){
        const count=BigInt(Math.floor((size-1-bucket)/8)+1);
        const expected=count*BigInt(bucket+1)+4n*count*(count-1n);
        assert.deepEqual(normalized.records[bucket],{group:`g${bucket}`,value:Number(expected)});
      }
      assert.equal(artifact.output_count,normalized.records.length);
      assert.equal(artifact.input_count,size);
      assert.ok(Buffer.byteLength(artifact.html)<100_000,'only bounded grouped records may reach HTML');
      assert.match(artifact.html,/<svg/);
      await writeFile(join(outputDir,`${mode}-${size}.html`),artifact.html,{flag:'wx'});
      await writeFile(join(outputDir,`${mode}-${size}.svg`),artifact.renderer_spec.spec.svg,{flag:'wx'});
    }else{
      const rows=normalized.records;
      assert.equal(new Set(rows.map(row=>row.seq)).size,rows.length);
      for(let i=0;i<rows.length;i++){
        const row=rows[i];
        assert.ok(Number.isInteger(row.seq)&&row.seq>=0&&row.seq<size);
        assert.equal(row.value,row.seq+1);assert.equal(row.group,`g${row.seq%8}`);
        if(i)assert.ok(row.seq>rows[i-1].seq,'sample preserves source ordering');
      }
      if(size>64){
        assert.match(normalized.warnings.join(' '),/sample.*64.*records/i);
        assert.ok(rows.some(row=>row.seq>=64),'a reservoir is not silent prefix truncation');
      }
    }
    const result={status:'PASS',size,mode,input_count:normalized.input_count,output_count:normalized.records.length,
      ...stats,strategy:normalized.strategy,warnings:normalized.warnings,
      exact_source_integer_sum:exactSum(size).toString(),
      loss:mode==='sum'?'Exact integer sums per eight groups; individual rows and within-group distributions not retained.':'Deterministic reservoir sample; discarded source rows and their distributions are not reconstructed.',
      elapsed_ms:Math.round((performance.now()-started)*100)/100,samples,
      baseline_heap_bytes:baseline.heapUsed,sampled_peak_heap_bytes:peakHeap,sampled_heap_delta_bytes:peakHeap-baseline.heapUsed,
      baseline_rss_bytes:baseline.rss,sampled_peak_rss_bytes:peakRss,sampled_rss_delta_bytes:peakRss-baseline.rss,
      explicit_gc:typeof globalThis.gc==='function',
      ...(artifact?{html_path:join(outputDir,`${mode}-${size}.html`),html_bytes:Buffer.byteLength(artifact.html),svg_path:join(outputDir,`${mode}-${size}.svg`)}:{}),
      reduced_records:normalized.records};
    await writeFile(join(outputDir,`${mode}-${size}.json`),JSON.stringify(result,null,2),{flag:'wx'});
    return result;
  }catch(error){
    const failure={status:'FAIL',size,mode,...stats,elapsed_ms:performance.now()-started,
      samples,baseline_heap_bytes:baseline.heapUsed,sampled_peak_heap_bytes:peakHeap,baseline_rss_bytes:baseline.rss,sampled_peak_rss_bytes:peakRss,
      error:String(error),stack:error.stack};
    await writeFile(join(outputDir,`${mode}-${size}-failure.json`),JSON.stringify(failure,null,2),{flag:'wx'});
    throw error;
  }
}

async function hash(path){return createHash('sha256').update(await readFile(path)).digest('hex');}
async function identity(entry){
  const git=(...args)=>execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
  const files=['index','models','normalize','render','renderers','schema'];
  const fingerprints=[];
  for(const name of files){
    const built=join(root,'packages/deepviz/dist',`${name}.js`),imported=join(dirname(entry),`${name}.js`);
    const builtHash=await hash(built),importedHash=await hash(imported);
    assert.equal(importedHash,builtHash,`${name}: imported package differs from this worktree build`);
    fingerprints.push({name,source_sha256:await hash(join(root,'packages/deepviz/src',`${name}.ts`)),built_sha256:builtHash,imported_sha256:importedHash});
  }
  return {source_commit:git('rev-parse','HEAD'),branch:git('branch','--show-current'),dirty:git('status','--short'),
    source_root:root,import_entry:entry,package:JSON.parse(await readFile(join(dirname(entry),'../package.json'),'utf8')),
    fingerprints,schema_sha256:await hash(join(root,'schemas/chart-spec.schema.json')),
    harness_sha256:await hash(fileURLToPath(import.meta.url)),node:process.version,platform:process.platform,arch:process.arch};
}

async function verifyRenderedCase(scaleDir,outputDir){
  const {chromium}=await import('playwright');
  await mkdir(dirname(outputDir),{recursive:true});
  await mkdir(outputDir);
  const measured=JSON.parse(await readFile(join(scaleDir,'sum-10000000.json'),'utf8'));
  const html=await readFile(measured.html_path,'utf8');
  const browser=await chromium.launch({headless:true});
  const errors=[],network=[];
  try{
    const page=await browser.newPage({viewport:{width:1100,height:850},deviceScaleFactor:1});
    page.on('pageerror',error=>errors.push(String(error)));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.route('**/*',route=>{network.push(route.request().url());return route.abort();});
    await page.setContent(html);
    await page.waitForFunction(()=>globalThis.deepvizReady===true);
    const geometry=await page.locator('#chart-0 svg').evaluate(svg=>({
      width:svg.viewBox.baseVal.width,height:svg.viewBox.baseVal.height,
      texts:[...svg.querySelectorAll('text')].map(text=>{
        const box=text.getBBox(),matrix=text.getCTM();
        const corners=[[box.x,box.y],[box.x+box.width,box.y],[box.x,box.y+box.height],[box.x+box.width,box.y+box.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(matrix));
        const left=Math.min(...corners.map(point=>point.x)),top=Math.min(...corners.map(point=>point.y));
        return {text:[...text.childNodes].filter(node=>node.nodeType===3).map(node=>node.textContent).join(''),x:left,y:top,width:Math.max(...corners.map(point=>point.x))-left,height:Math.max(...corners.map(point=>point.y))-top};
      }),
      bars:[...svg.querySelectorAll('rect.mark')].map(mark=>({title:mark.querySelector('title')?.textContent,x:Number(mark.getAttribute('x')),y:Number(mark.getAttribute('y')),width:Number(mark.getAttribute('width')),height:Number(mark.getAttribute('height'))})),
    }));
    await page.screenshot({path:join(outputDir,'sum-10000000-browser.png'),fullPage:true});
    await writeFile(join(outputDir,'visual-observation.json'),JSON.stringify({errors,network,geometry},null,2),{flag:'wx'});
    assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
    assert.deepEqual(await page.evaluate(()=>globalThis.deepvizErrors),[]);
    assert.equal(geometry.bars.length,8);
    const max=Math.max(...measured.reduced_records.map(row=>row.value));
    const baseline=Math.max(...geometry.bars.map(bar=>bar.y+bar.height));
    const fullHeight=Math.max(...geometry.bars.map(bar=>bar.height));
    assert.ok(fullHeight>0&&baseline>0&&baseline<=geometry.height);
    geometry.bars.forEach((bar,i)=>{
      const expected=measured.reduced_records[i];
      assert.equal(bar.title,`${expected.group}: ${expected.value}`);
      assert.ok(Math.abs(bar.y+bar.height-baseline)<1e-6,'shared zero baseline');
      assert.ok(Math.abs(bar.height-expected.value/max*fullHeight)<1e-6,'actual bar height encodes exact sum');
      assert.ok(bar.width>0&&bar.x>=0&&bar.x+bar.width<=geometry.width);
    });
    for(const row of measured.reduced_records)assert.ok(geometry.texts.some(text=>text.text===row.group));
    assert.ok(geometry.texts.some(text=>/^0(?:\.0+)?$/.test(text.text)),'zero tick visible');
    const clipped_text=geometry.texts.filter(text=>text.x<0||text.x+text.width>geometry.width);
    const result={status:clipped_text.length?'FAIL':'PASS',errors,network,geometry,clipped_text,
      screenshot:join(outputDir,'sum-10000000-browser.png'),
      rationale:'All eight real SVG mark titles and pixel heights checked against exact streamed grouped sums, common zero baseline, category tick labels; offline browser, no console/page/network errors.'};
    await writeFile(join(outputDir,'visual.json'),JSON.stringify(result,null,2),{flag:'wx'});
    assert.deepEqual(clipped_text,[],'axis/category text must not be clipped by the SVG viewport');
    console.log(JSON.stringify(result));
  }finally{await browser.close();}
}

async function main(){
  const args=Object.fromEntries(process.argv.slice(2).map(arg=>{const at=arg.indexOf('=');return [arg.slice(2,at),arg.slice(at+1)];}));
  const entry=resolve(args.entry??defaultEntry);
  const outputDir=resolve(args.output??join(root,'artifacts/local/N21',new Date().toISOString().replace(/[:.]/g,'-')));
  if(args.visual){await verifyRenderedCase(resolve(args.visual),args.output?outputDir:join(resolve(args.visual),`visual-${Date.now()}`));return;}
  if(args.child){
    const result=await runScaleCase({size:Number(args.size),mode:args.mode,entry,outputDir});
    console.log(JSON.stringify({size:result.size,mode:result.mode,status:result.status,elapsed_ms:result.elapsed_ms}));
    return;
  }
  await mkdir(outputDir,{recursive:true});
  const provenance=await identity(entry);
  await writeFile(join(outputDir,'identity.json'),JSON.stringify(provenance,null,2),{flag:'wx'});
  const results=[];
  for(const size of tiers)for(const mode of ['sum','sample']){
    const argv=['--expose-gc','--max-old-space-size=384',fileURLToPath(import.meta.url),'--child=1',`--size=${size}`,`--mode=${mode}`,`--entry=${entry}`,`--output=${outputDir}`];
    const child=spawnSync(process.execPath,argv,{cwd:root,encoding:'utf8',timeout:200_000,maxBuffer:1024*1024});
    await writeFile(join(outputDir,`${mode}-${size}.log`),JSON.stringify({command:[process.execPath,...argv],exit_code:child.status,signal:child.signal,error:child.error?.message,stdout:child.stdout,stderr:child.stderr},null,2),{flag:'wx'});
    let measured;
    try{measured=JSON.parse(await readFile(join(outputDir,`${mode}-${size}.json`),'utf8'));}catch{/* A crash is a failed case, not a missing tier silently skipped. */}
    if(measured&&child.status!==0)measured={...measured,status:'FAIL',exit_code:child.status,error:child.error?.message??child.stderr};
    results.push(measured??{status:'FAIL',size,mode,exit_code:child.status,error:child.error?.message??child.stderr});
    console.log(`${mode} ${size}: ${child.status===0&&measured?'PASS':'FAIL'}`);
    await writeFile(join(outputDir,'summary.json'),JSON.stringify({provenance,caps,
      methodology:'Each tier/mode is a fresh Node child process, --expose-gc and --max-old-space-size=384. Import before GC/baseline. process.memoryUsage() samples synchronously before every 8,192 source records and after reduction/render/serialization. These are sampled peaks, not continuous maxima; short-lived peaks and native/browser memory between samples may be missed. RSS includes Node/runtime/allocator, not just retained rows. No timing extrapolation, no pre-materialized input array; one-shot iterator counts every yielded record. Sum cases use public renderStream to offline SVG HTML; sample cases use public normalizeStream. Resource caps fail deliberately small supported runs rather than attempting exhaustion. Child timeout is 200s; measured elapsed cap 180s.',results},null,2));
  }
  if(results.some(result=>result.status!=='PASS'))process.exitCode=1;
  console.log(outputDir);
}

if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await main();
