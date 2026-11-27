/** Public tarball gate without dependency installation. This is NOT a clean install. */
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const [archiveArg,outputArg,compilerArg]=process.argv.slice(2);
assert.ok(archiveArg&&outputArg,'Usage: node check-materialized-package.mjs archive.tgz NEW_OUTPUT [existing-typescript-bin]');
const archive=path.resolve(archiveArg),output=path.resolve(outputArg);
await mkdir(output); // Fail closed rather than overwrite a prior consumer's evidence.
const record={started:new Date().toISOString(),cleanInstalled: false,commands:[],files:[]};
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
function run(name,exe,args,cwd=output){
  const started=new Date().toISOString();
  const result=spawnSync(exe,args,{cwd,encoding:'utf8',timeout:120000,maxBuffer:8*1024*1024});
  record.commands.push({name,exe,args,cwd,started,finished:new Date().toISOString(),exit:result.status,error:result.error?.message??null});
  return Promise.all([writeFile(path.join(output,name+'.stdout.log'),result.stdout??''),writeFile(path.join(output,name+'.stderr.log'),result.stderr??'')]).then(()=>{
    assert.equal(result.status,0,`${name}: ${result.stdout}\n${result.stderr}`);return result.stdout;
  });
}
try{
  record.archive={path:archive,sha256:hash(await readFile(archive))};
  const modules=['index','models','normalize','render','renderers','schema'];
  const expected=['package.json','README.md','LICENSE','dist/chart-spec.schema.json',...modules.flatMap(name=>['js','js.map','d.ts'].map(ext=>`dist/${name}.${ext}`)),...['README','system','request'].map(name=>`dist/prompts/v1/${name}.md`)].map(name=>'package/'+name).sort();
  const members=(await run('archive-list','tar',['-tzf',archive])).trim().split(/\r?\n/).sort();
  assert.deepEqual(members,expected,'Exact published allowlist: no missing runtime/resources or source/dependency leaks');
  const listing=await run('archive-types','tar',['-tvzf',archive]);
  assert.ok(listing.trim().split(/\r?\n/).every(line=>line.startsWith('-')),'Only ordinary files may be materialized');
  const packageDir=path.join(output,'node_modules','@deepviz','agent-toolkit');
  await mkdir(packageDir,{recursive:true});
  await run('extract','tar',['-xzf',archive,'-C',packageDir,'--strip-components=1']);
  for(const name of expected){const relative=name.slice('package/'.length);const bytes=await readFile(path.join(packageDir,relative));record.files.push({path:relative,bytes:bytes.length,sha256:hash(bytes)});}
  const metadata=JSON.parse(await readFile(path.join(packageDir,'package.json'),'utf8'));
  assert.equal(metadata.name,'@deepviz/agent-toolkit');assert.equal(metadata.type,'module');assert.equal(metadata.engines.node,'>=22');
  assert.deepEqual(metadata.dependencies??{},{});assert.deepEqual(metadata.optionalDependencies??{},{});
  await writeFile(path.join(output,'package.json'),JSON.stringify({name:'deepviz-manual-public-consumer',private:true,type:'module'}));
  const root=new URL('../../../',import.meta.url);
  const expectations={entry:pathToFileURL(path.join(packageDir,'dist/index.js')).href,schema:JSON.parse(await readFile(new URL('schemas/chart-spec.schema.json',root),'utf8')),prompts:{}};
  for(const name of ['README','system','request'])expectations.prompts[name]=hash(await readFile(new URL(`prompts/v1/${name}.md`,root)));
  await writeFile(path.join(output,'expected.json'),JSON.stringify(expectations));
  await writeFile(path.join(output,'consumer.test.mjs'),`import assert from 'node:assert/strict';
import test from 'node:test';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import * as api from '@deepviz/agent-toolkit';
import schema from '@deepviz/agent-toolkit/chart-spec.schema.json' with {type:'json'};
const expected=JSON.parse(await readFile(new URL('./expected.json',import.meta.url),'utf8'));
test('packed public ESM resolves ONLY materialized dist and has all13 exports',()=>{
 assert.equal(import.meta.resolve('@deepviz/agent-toolkit'),expected.entry);
 assert.deepEqual(Object.keys(api).sort(),['chartKinds','ValidationError','isObject','safeKey','validateSpec','normalize','normalizeStream','defaultAssets','buildRendererSpec','render','renderStream','createTools','chartSpecSchema'].sort());
});
test('packed schema is the current canonical source, not stale installed JSON',()=>{assert.deepEqual(schema,expected.schema);assert.deepEqual(schema,api.chartSpecSchema);});
test('packed runtime retains raw dashboard/default-kind semantics of the staged paired schema',()=>{
 const cases=[[{charts:[{}]},false],[{kind:'dashboard'},false],[{kind:'dashboard',charts:[]},false],[{kind:'bar',charts:[]},true],[{kind:'dashboard',charts:[{}]},true],[{kind:'dashboard',charts:[{kind:'dashboard',charts:[{}]}]},false]];
 for(const [input,valid] of cases){if(valid)assert.doesNotThrow(()=>api.validateSpec(input));else assert.throws(()=>api.validateSpec(input),api.ValidationError);}
});
for(const name of ['README','system','request'])test('packed raw prompt '+name+' has canonical bytes',async()=>{
 const url=import.meta.resolve('@deepviz/agent-toolkit/prompts/v1/'+name+'.md');assert.ok(url.startsWith(new URL('./node_modules/',import.meta.url).href));
 assert.equal(createHash('sha256').update(await readFile(new URL(url))).digest('hex'),expected.prompts[name]);
});
test('packed defaults and strict public helper boundary retain actual semantics',async()=>{
 assert.equal(api.validateSpec({}).width,900);assert.throws(()=>api.validateSpec({width:'900'}),api.ValidationError);
 assert.deepEqual(api.createTools().map(t=>t.name),['render_vega','render_echarts','render_antv','render_plotly','render_svg']);
 await assert.rejects(api.createTools().find(t=>t.name==='render_svg').invoke({data:[{x:'A',y:2}],spec:null}),api.ValidationError);
});
test('packed literal normalization and one-pass stream do not change caller input',async()=>{
 const input=[{x:'A',y:2},{x:'B',y:5},{x:'A',y:3}];const before=structuredClone(input);
 assert.deepEqual(api.normalize(input,{x:'x',y:'y',aggregation:'sum'}).records,[{x:'A',y:5},{x:'B',y:5}]);
 let yields=0,closed=0;async function* rows(){try{for(const row of input){yields++;yield row;}}finally{closed++;}}
 const result=await api.normalizeStream(rows(),{x:'x',y:'y',aggregation:'count'});
 assert.equal(yields,3);assert.equal(closed,1);assert.equal(result.input_count,3);assert.deepEqual(result.records,[{x:'A',y:2},{x:'B',y:1}]);assert.deepEqual(input,before);
});
test('packed public mean handles literal subnormal/MAX and excludes null from denominator',()=>{
 const reduce=ys=>api.normalize(ys.map(y=>({x:'A',y})),{x:'x',y:'y',aggregation:'mean'}).records[0].y;
 assert.equal(reduce([Number.MIN_VALUE,Number.MIN_VALUE,Number.MIN_VALUE]),Number.MIN_VALUE);
 assert.equal(reduce([Number.MAX_VALUE,Number.MAX_VALUE]),Number.MAX_VALUE);assert.equal(reduce([-7,2,null]),-2.5);
});
test('packed native SVG and browser HTML retain literal data and explicit asset scope',async()=>{
 const rows=[{x:'Alpha',y:2},{x:'Beta',y:5},{x:'Gamma',y:-3}];
 const native=api.render(rows,{title:'Packed native',x:'x',y:'y',aggregation:'none'},'svg');
 assert.equal(native.input_count,3);assert.equal(native.output_count,3);assert.deepEqual(native.paths,[]);assert.deepEqual(native.renderer_spec.normalized.records,rows);assert.ok(native.html.includes('<svg'));assert.ok(!/<script[^>]+src=/.test(native.html));
 await writeFile(new URL('./native-svg.html',import.meta.url),native.html);
 const table=api.render([{x:'<img src=x onerror=alert(1)>',y:2}],{kind:'table',x:'x',y:'y'},'svg');assert.ok(!table.html.includes('<img src=x'));assert.ok(table.html.includes('&lt;img'));await writeFile(new URL('./native-table.html',import.meta.url),table.html);
 const browser=api.render(rows,{x:'x',y:'y',aggregation:'none'},'vega');assert.deepEqual(browser.renderer_spec.normalized.records,rows);assert.ok(browser.html.includes(api.defaultAssets.vega));await writeFile(new URL('./vega.html',import.meta.url),browser.html);
});
`);
  await run('public-consumer',process.execPath,['--test','consumer.test.mjs']);
  await writeFile(path.join(output,'types.mts'),`import {validateSpec,normalize,buildRendererSpec,render,createTools,type ChartKind,type Engine,type BrowserEngine,type DataFormat,type Aggregation,type ChartSpec,type ChartSpecInput,type Scalar,type DataRecord,type NormalizedData,type Artifact,type AssetName,type RenderOptions,type RendererResult,type HtmlArtifact,type RenderTool} from '@deepviz/agent-toolkit';
const enums:[ChartKind,Engine,BrowserEngine,DataFormat,Aggregation,AssetName]=['bar','plotly','svg','json','sum','vega'];
const scalar:Scalar=2;const row:DataRecord={x:'A',y:scalar};const input:ChartSpecInput={kind:enums[0],x:'x',y:'y'};
const spec:ChartSpec=validateSpec(input);const normalized:NormalizedData=normalize([row],spec);const result:RendererResult=buildRendererSpec([row],spec,'svg');const options:RenderOptions={};const artifact:HtmlArtifact=render([row],spec,'svg',options);const common:Artifact=artifact;const tools:RenderTool[]=createTools(options);void[normalized,result,common,tools];
// @ts-expect-error Numeric fields must not accept coerced strings.
const invalid:ChartSpecInput={width:'900'};void invalid;
// @ts-expect-error Model-authored specs do not gain renderer asset authority.
const unsafe:ChartSpecInput={assets:{vega:'https://invalid.example'}};void unsafe;
// @ts-expect-error Unknown engines are not a supported browser API.
render([row],spec,'matplotlib');
`);
  // Node's package exports can hide an installed compiler CLI; resolve its package root first.
  const compiler=compilerArg?path.resolve(compilerArg):path.join(path.dirname(fileURLToPath(import.meta.resolve('typescript/package.json'))),'bin','tsc');
  record.compiler={path:compiler,sha256:hash(await readFile(compiler))};
  await run('public-types',process.execPath,[compiler,'--noEmit','--strict','--skipLibCheck','false','--module','NodeNext','--moduleResolution','NodeNext','--target','ES2022','--lib','ES2022,DOM','types.mts']);
  record.passed=true;console.log('PASS: manually materialized tarball; 25-file allowlist, public ESM/schema/prompts/runtime/types. NOT a clean install.');
}catch(error){record.passed=false;record.failure=String(error);throw error;}
finally{record.finished=new Date().toISOString();await writeFile(path.join(output,'receipt.json'),JSON.stringify(record,null,2));}
