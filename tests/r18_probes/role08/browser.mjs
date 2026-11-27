// Real pinned-CDN G2 execution. No request routing, payload edits, or HTML rewrites.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [outputArgument,installedToolRoot]=process.argv.slice(2);
assert.ok(outputArgument&&installedToolRoot,'Usage: browser.mjs GENERATED_OUTPUT EXISTING_TOOL_ROOT');
const output=path.resolve(outputArgument);
const require=createRequire(path.join(path.resolve(installedToolRoot),'package.json'));
const {chromium}=require('playwright');
const input=JSON.parse(await readFile(path.join(output,'cases.json'),'utf8'));
const screenshots=path.join(output,'screenshots');await mkdir(screenshots);
const browser=await chromium.launch({headless:true});
const report={identity:input.identity,node:process.version,chromium:browser.version(),checks:[],cases:[],
  method:'All HTML is unmodified. Each case first opens without any G2 observer. A separate observation-only navigation captures the real constructor return; args/options/library/DOM unchanged.',
  scope:'11 bounded R18 cases, real CDN, not final candidate / all kinds / accessibility / large scale'};
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
function check(id,name,pass,observed){report.checks.push({id,name,pass:Boolean(pass),observed});}
const equal=(actual,expected)=>JSON.stringify(actual)===JSON.stringify(expected);
function categoryLegend(tree){
  return tree.flatMap((node,index)=>{
    if(!String(node.className).split(' ').includes('g2-legend-item'))return [];
    const next=tree.findIndex((candidate,j)=>j>index&&String(candidate.className).split(' ').includes('g2-legend-item'));
    const item=tree.slice(index,next<0?undefined:next);
    return [{label:String(item.find(child=>child.node==='text')?.text),
      fill:item.find(child=>String(child.className).split(' ').includes('g2-legend-marker'))?.fill??null}];
  });
}

async function open(fixture,observe){
  const page=await browser.newPage({viewport:{width:1100,height:850},deviceScaleFactor:1});
  const row={observer:observe?'constructor-return-only':'none',errors:[],requests:[],failedRequests:[]};
  page.on('console',message=>{if(message.type()==='error')row.errors.push({kind:'console',text:message.text()});});
  page.on('pageerror',error=>row.errors.push({kind:'page',text:String(error)}));
  page.on('response',response=>{if(response.url().startsWith('https:'))row.requests.push({url:response.url(),status:response.status()});});
  page.on('requestfailed',request=>row.failedRequests.push({url:request.url(),failure:request.failure()?.errorText}));
  if(observe)await page.addInitScript(()=>{
    window.__r18Charts=[];
    let library;
    Object.defineProperty(window,'G2',{configurable:true,get:()=>library,set:value=>{
      library=value;
      let constructor;
      Object.defineProperty(value,'Chart',{configurable:true,enumerable:true,get:()=>constructor,set:original=>{
        constructor=new Proxy(original,{construct(target,args,newTarget){
          const chart=Reflect.construct(target,args,newTarget);window.__r18Charts.push(chart);return chart;
        }});
      }});
    }});
  });
  try {
    await page.goto(pathToFileURL(path.join(output,fixture.html)).href,{waitUntil:'load',timeout:60000});
    row.readiness=await page.evaluate(async()=>{
      if(!window.deepvizReady?.then)return {status:'missing'};
      const settled=window.deepvizReady.then(()=>({status:'resolved'}),error=>({status:'rejected',error:String(error)}));
      return Promise.race([settled,new Promise(resolve=>setTimeout(()=>resolve({status:'timeout'}),20000))]);
    });
    row.state=await page.evaluate(observe=>{
      const payloads=JSON.parse(document.getElementById('deepviz-data').textContent);
      const element=document.getElementById('chart-0'),canvas=element.querySelector('canvas');
      const context=canvas?.getContext('2d');
      const pixels=context?.getImageData(0,0,canvas.width,canvas.height).data;
      let painted=0;
      if(pixels)for(let i=0;i<pixels.length;i+=4)if(pixels[i+3]>0&&pixels[i]+pixels[i+1]+pixels[i+2]<650)painted++;
      const result={payloads,painted,title:document.querySelector('h1').textContent,tableRows:[...document.querySelectorAll('tbody tr')].map(row=>row.textContent),native:null};
      if(!observe)return result;
      const chart=window.__r18Charts[0];
      if(!chart)return result;
      const root=chart.getContext().canvas.document.documentElement;
      function describe(mark){
        let box;try{const b=mark.getBBox();box={x:b.x,y:b.y,width:b.width,height:b.height};}catch{box=null;}
        return {node:mark.nodeName,className:mark.className,fill:mark.getAttribute('fill'),stroke:mark.getAttribute('stroke'),
          text:mark.getAttribute('text'),box,attributes:mark.attributes?Object.fromEntries(Object.entries(mark.attributes).filter(([key,value])=>['string','number','boolean'].includes(typeof value)&&key!=='path')):{},
        };
      }
      const marks=[...root.querySelectorAll('.element')].map(describe);
      const texts=[...root.querySelectorAll('text')].map(describe);
      const nodes=[];
      function walk(node,ancestors=[]){
        const label=String(node.className??node.getAttribute?.('class')??'');
        if(/legend|legend/i.test(label)||ancestors.some(name=>/legend/i.test(name)))nodes.push({...describe(node),ancestors});
        for(const child of node.children??[])walk(child,[...ancestors,label]);
      }
      walk(root);
      const samples=marks.map(mark=>{
        if(!mark.box||!context)return null;
        const x=Math.round(mark.box.x+mark.box.width/2),y=Math.round(mark.box.y+mark.box.height/2);
        return {x,y,rgba:[...context.getImageData(x,y,1,1).data]};
      });
      result.native={marks,texts,legendTree:nodes,samples};return result;
    },observe);
  }catch(error){row.harnessError=String(error);}
  row.screenshot=fixture.id+(observe?'-observed':'-production')+'.png';
  await page.screenshot({path:path.join(screenshots,row.screenshot),fullPage:true});
  row.screenshotSha256=hash(await readFile(path.join(screenshots,row.screenshot)));
  await page.close();return row;
}

try{
  for(const fixture of input.cases){
    assert.equal(hash(await readFile(path.join(output,fixture.html))),fixture.html_sha256,'Original HTML changed before browser run');
    const manifest=JSON.parse(await readFile(path.join(output,fixture.manifest),'utf8'));
    const production=await open(fixture,false);
    check(fixture.id,'unmodified-production-ready',production.readiness?.status==='resolved',production.readiness??production.harnessError);
    check(fixture.id,'unmodified-production-zero-errors',production.errors.length===0,production.errors);
    check(fixture.id,'real-pinned-CDN-loads',production.failedRequests.length===0&&production.requests.length>0&&production.requests.every(r=>r.url==='https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js'&&r.status===200),{failed:production.failedRequests,responses:production.requests});
    check(fixture.id,'literal-input-records-preserved',equal(manifest.charts[0].records,fixture.rows),manifest.charts[0].records);
    check(fixture.id,'unmodified-production-paints',production.state?.painted>100,production.state?.painted);
    const observed=await open(fixture,true);
    check(fixture.id,'observation-does-not-change-readiness',observed.readiness?.status===production.readiness?.status&&observed.errors.length===production.errors.length,{production:production.readiness,observed:observed.readiness,observerErrors:observed.errors});
    check(fixture.id,'embedded-native-equals-public-manifest',equal(observed.state?.payloads,manifest.native_specs)&&equal(production.state?.payloads,manifest.native_specs),observed.state?.payloads);
    const native=observed.state?.native,marks=native?.marks??[];
    if(fixture.mode==='category'){
      check(fixture.id,'literal-categorical-labels-values',equal(manifest.native_specs[0].data.map(r=>[r._x,r._y]),fixture.expected),manifest.native_specs[0].data);
      check(fixture.id,'one-native-mark-per-literal-category',marks.length===fixture.expected.length,marks);
      check(fixture.id,'categorical-data-colors-distinct',new Set(marks.map(m=>String(m.fill))).size===fixture.expected.length,marks.map(m=>m.fill));
      // A G2 categorical legend item contains one label and one colored marker.
      const tree=native?.legendTree??[];
      const legend=categoryLegend(tree);
      check(fixture.id,'visible-legend-labels-and-distinct-keys',equal(legend.map(item=>item.label),fixture.expected.map(([label])=>label))&&legend.every(item=>item.fill)&&new Set(legend.map(item=>String(item.fill))).size===fixture.expected.length,legend);
      const color=value=>String(value).toLowerCase();
      check(fixture.id,'actual-native-colors-agree-with-visible-legend',marks.length===legend.length&&legend.every((item,index)=>item.fill&&color(item.fill)===color(marks[index]?.fill)),{legend,markFills:marks.map(m=>m.fill)});
    }else if(fixture.mode==='heatmap'){
      check(fixture.id,'literal-negative-or-control-values',equal(manifest.native_specs[0].data.map(r=>r._heat),fixture.expected),manifest.native_specs[0].data);
      check(fixture.id,'two-cell-marks',marks.length===2&&marks.every(m=>m.box?.width>10&&m.box?.height>10),marks);
      const unequal=fixture.expected[0]!==fixture.expected[1];
      check(fixture.id,'quantitative-cell-colors-distinct-iff-values-differ',marks.length===2&&((String(marks[0]?.fill)!==String(marks[1]?.fill))===unequal),marks.map(m=>m.fill));
      const legendTexts=(native?.legendTree??[]).filter(n=>n.node==='text').map(n=>String(n.text));
      const numericTicks=legendTexts.map(Number).filter(Number.isFinite);
      check(fixture.id,'visible-finite-quantitative-legend',numericTicks.length>0&&fixture.expected.every(value=>Math.min(...numericTicks)<=value&&Math.max(...numericTicks)>=value),{legendTexts,numericTicks});
      check(fixture.id,'literal-grid-cell-order',marks.length===2&&marks[0].box?.x<marks[1].box?.x&&marks[0].box?.y<marks[1].box?.y,marks.map(m=>m.box));
    }else{
      const payload=manifest.native_specs[0];
      const points=fixture.id==='line'?payload.children[1].data:payload.data;
      check(fixture.id,'literal-fixed-control-values',equal(points.map(r=>[r._x,r._y]),fixture.expected),points);
      const pointMarks=fixture.id==='line'?marks.filter(m=>m.box?.width===6&&m.box?.height===6):marks;
      check(fixture.id,'fixed-control-three-points',pointMarks.length===3,pointMarks);
      check(fixture.id,'fixed-control-original-fill',pointMarks.length===3&&pointMarks.every(m=>String(m.fill).toLowerCase()==='#386cb0'),pointMarks.map(m=>m.fill));
      const xs=pointMarks.map(m=>m.box.x+m.box.width/2);
      const ratio=(xs[2]-xs[1])/(xs[1]-xs[0]);
      check(fixture.id,'fixed-control-unequal-x-spacing',Math.abs(ratio-2)<1e-6,{xs,ratio});
    }
    assert.equal(hash(await readFile(path.join(output,fixture.html))),fixture.html_sha256,'Original HTML changed during browser run');
    report.cases.push({id:fixture.id,production,observed});
    await writeFile(path.join(output,'browser-results.json'),JSON.stringify(report,null,2));
    console.log(fixture.id+': production '+production.readiness?.status+', strict failures '+report.checks.filter(c=>c.id===fixture.id&&!c.pass).length);
  }
}finally{await browser.close();}
report.totals={cases:report.cases.length,checks:report.checks.length,passed:report.checks.filter(c=>c.pass).length,failed:report.checks.filter(c=>!c.pass).length,skipped:0};
await writeFile(path.join(output,'browser-results.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({commit:input.identity.commit,...report.totals,failures:report.checks.filter(c=>!c.pass).map(({id,name})=>({id,name}))}));
process.exitCode=report.totals.failed?1:0;
