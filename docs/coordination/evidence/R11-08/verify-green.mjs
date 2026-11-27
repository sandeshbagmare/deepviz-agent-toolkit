import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync,mkdirSync,existsSync,readdirSync,statSync,lstatSync,realpathSync,copyFileSync} from 'node:fs';
import path from 'node:path';

const [sourceArgument,outputArgument,probesArgument,baselineArgument]=process.argv.slice(2);
assert.ok(sourceArgument&&outputArgument&&probesArgument&&baselineArgument,'Usage: verify-green.mjs SOURCE NEW_EXTERNAL_OUTPUT R10_PROBES R10_INSTALLED_PACKAGE');
const source=realpathSync(sourceArgument),output=path.resolve(outputArgument),probes=realpathSync(probesArgument),baseline=realpathSync(baselineArgument);
assert.ok(!existsSync(output),'Refuse to overwrite prior output');
assert.ok(path.relative(source,output).startsWith(`..${path.sep}`),'External output required');
mkdirSync(output);
const env={...process.env,npm_config_cache:path.join(output,'npm-cache'),npm_config_audit:'false',npm_config_fund:'false',npm_config_update_notifier:'false'};
delete env.NODE_PATH;
const npm=path.join(path.dirname(process.execPath),'node_modules/npm/bin/npm-cli.js');
const commands=[];
const summary={started:new Date().toISOString(),source,output,base:'ca25af486bf443949125df789f5b5fd1fda8bba8',node:process.version,npmCli:npm,commands,status:'RUNNING',installState:'Own isolated npm ci --ignore-scripts --no-audit --no-fund completed before RED; no shared dependency install or lockfile change',limits:['Producer-authored evidence, not an independent final review','Node26/Chromium159 only; no registry publication/default CDN/whole-dashboard/10M acceptance','Vendor dependencies served from own isolated dev dependencies; not bundled runtime assets']};
const hash=file=>createHash('sha256').update(readFileSync(file)).digest('hex');
const save=()=>writeFileSync(path.join(output,'summary.json'),JSON.stringify(summary,null,2));
function run(label,args,cwd=source,executable=process.execPath){
  const start=new Date().toISOString();
  const result=spawnSync(executable,args,{cwd,env,encoding:'utf8',timeout:240000,maxBuffer:16*1024*1024});
  writeFileSync(path.join(output,label+'.stdout.log'),result.stdout??'');
  writeFileSync(path.join(output,label+'.stderr.log'),result.stderr??'');
  commands.push({label,executable,args,cwd,start,exit:result.status,signal:result.signal,error:result.error?.message??null});
  save();console.log(label+':exit'+result.status);
  assert.equal(result.status,0,`${label} failed; retained logs are authoritative`);
  return result.stdout;
}
function walk(root,prefix=''){
  const result=[];
  for(const name of readdirSync(root).sort()){
    const relative=path.posix.join(prefix,name),file=path.join(root,name);
    assert.equal(lstatSync(file).isSymbolicLink(),false,`Unexpected symlink ${file}`);
    if(statSync(file).isDirectory())result.push(...walk(file,relative));
    else result.push(relative);
  }
  return result;
}
const manifest=(root,files)=>files.map(name=>({name,bytes:statSync(path.join(root,name)).size,sha256:hash(path.join(root,name))}));
try {
  summary.commit=run('head',['rev-parse','HEAD'],source,'git').trim();
  run('source-clean',['diff','--exit-code','HEAD','--','package.json','package-lock.json','packages/deepviz','prompts','schemas'],source,'git');
  run('protected-source-unchanged',['diff','--exit-code',summary.base,'--','package.json','package-lock.json','packages/deepviz/src','prompts','schemas'],source,'git');
  const productFiles=['package.json','package-lock.json','packages/deepviz/package.json','packages/deepviz/README.md','packages/deepviz/scripts/copy-prompts.mjs','packages/deepviz/test/test_r11_packaged_prompts.test.mjs','schemas/chart-spec.schema.json',...['README.md','system.md','request.md'].map(name=>'prompts/v1/'+name),...walk(path.join(source,'packages/deepviz/src')).map(name=>'packages/deepviz/src/'+name)];
  summary.productFiles=manifest(source,productFiles);
  summary.tools={node:{path:process.execPath,sha256:hash(process.execPath)},npm:{path:npm,sha256:hash(npm),version:run('npm-version',[npm,'--version']).trim()},typescript:{version:JSON.parse(readFileSync(path.join(source,'node_modules/typescript/package.json'),'utf8')).version},playwright:{version:JSON.parse(readFileSync(path.join(source,'node_modules/playwright/package.json'),'utf8')).version}};
  for(const [label,args] of [['build',['run','build']],['typecheck',['run','typecheck']],['lint',['run','lint']],['tests',['test']],['schema',['run','schema:check']],['package-check',['run','package:check']],['dry-run',['pack','--dry-run','--workspace','@deepviz/agent-toolkit']]])run(label,[npm,...args]);
  const packs=[];
  for(let repeat=1;repeat<=2;repeat++){
    const destination=path.join(output,'pack'+repeat);mkdirSync(destination);
    run('actual-pack'+repeat,[npm,'pack','--workspace','@deepviz/agent-toolkit','--pack-destination',destination]);
    const names=readdirSync(destination).filter(name=>name.endsWith('.tgz'));assert.equal(names.length,1);
    const tarball=path.join(destination,names[0]);
    const members=run('tar-list'+repeat,['-tzf',tarball],source,'tar').trim().split(/\r?\n/).sort();
    for(const filename of ['README.md','system.md','request.md'])assert.ok(members.includes('package/dist/prompts/v1/'+filename));
    assert.equal(members.some(name=>name.startsWith('package/src/')||name.startsWith('package/test/')||name.includes('/node_modules/')),false);
    packs.push({tarball,bytes:statSync(tarball).size,sha256:hash(tarball),members});
  }
  assert.equal(packs[0].sha256,packs[1].sha256,'Repeated build/prepack must preserve actual tarball bytes');summary.packs=packs;
  const consumer=path.join(output,'consumer');mkdirSync(consumer);
  for(let parent=consumer;;parent=path.dirname(parent)){
    assert.equal(existsSync(path.join(parent,'.git')),false,'External consumer must be outside every Git workspace');
    if(existsSync(path.join(parent,'package.json')))assert.equal(Boolean(JSON.parse(readFileSync(path.join(parent,'package.json'),'utf8')).workspaces),false);
    if(parent===path.dirname(parent))break;
  }
  writeFileSync(path.join(consumer,'package.json'),JSON.stringify({name:'deepviz-r11-prompt-consumer',private:true,type:'module'}));
  run('clean-consumer-install',[npm,'install','--offline','--ignore-scripts','--no-audit','--no-fund','--workspaces=false','--package-lock=false',packs[0].tarball],consumer);
  const installed=path.join(consumer,'node_modules/@deepviz/agent-toolkit');
  assert.equal(lstatSync(installed).isSymbolicLink(),false);
  const distFiles=walk(path.join(source,'packages/deepviz/dist'));
  assert.deepEqual(walk(path.join(installed,'dist')),distFiles);
  for(const name of distFiles)assert.equal(hash(path.join(installed,'dist',name)),hash(path.join(source,'packages/deepviz/dist',name)),name);
  summary.installed={path:realpathSync(installed),dist:manifest(installed,distFiles.map(name=>'dist/'+name))};
  const previousRuntime=walk(path.join(baseline,'dist'));
  for(const name of previousRuntime)assert.equal(hash(path.join(installed,'dist',name)),hash(path.join(baseline,'dist',name)),`R10 emitted runtime/type/schema changed: ${name}`);
  summary.unchangedR10RuntimeFiles=previousRuntime.length;
  const schema=JSON.parse(readFileSync(path.join(source,'schemas/chart-spec.schema.json'),'utf8'));
  const fixture=JSON.parse(readFileSync(path.resolve(baseline,'../../../expected.json'),'utf8'));
  assert.deepEqual(fixture.schema,schema,'R10 canonical schema unchanged');
  for(const name of ['system','request'])assert.equal(fixture.prompts[name],hash(path.join(source,`prompts/v1/${name}.md`)));
  fixture.prompts.README=hash(path.join(source,'prompts/v1/README.md'));
  writeFileSync(path.join(consumer,'expected.json'),JSON.stringify(fixture,null,2));
  const copiedProbes=path.join(output,'probes');mkdirSync(copiedProbes);
  for(const name of ['consumer.test.mjs','types.mts','browser.mjs'])copyFileSync(path.join(probes,name),path.join(copiedProbes,name));
  for(const name of ['consumer.test.mjs','types.mts'])copyFileSync(path.join(copiedProbes,name),path.join(consumer,name));
  writeFileSync(path.join(consumer,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,noEmit:true,skipLibCheck:false,module:'NodeNext',moduleResolution:'NodeNext',target:'ES2022',types:[]},include:['types.mts']}));
  writeFileSync(path.join(consumer,'raw-prompts.test.mjs'),`import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import * as api from '@deepviz/agent-toolkit';
const fixture=JSON.parse(await readFile(new URL('./expected.json',import.meta.url),'utf8'));
const root=fileURLToPath(new URL('./node_modules/@deepviz/agent-toolkit/',import.meta.url));
for(const name of ['README','system','request'])test('Raw v1 '+name+' export reads exact canonical bytes without executable imports',async()=>{
  const url=import.meta.resolve('@deepviz/agent-toolkit/prompts/v1/'+name+'.md');
  assert.equal(fileURLToPath(url),path.join(root,'dist','prompts','v1',name+'.md'));
  const bytes=await readFile(new URL(url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'),fixture.prompts[name]);
  await assert.rejects(import(url),error=>error.code==='ERR_UNKNOWN_FILE_EXTENSION');
});
test('All thirteen runtime exports remain unchanged with no invented prompt reader',()=>assert.deepEqual(Object.keys(api).sort(),['ValidationError','buildRendererSpec','chartKinds','chartSpecSchema','createTools','defaultAssets','isObject','normalize','normalizeStream','render','renderStream','safeKey','validateSpec'].sort()));
`);
  run('clean-consumer-tests',['--test','consumer.test.mjs','raw-prompts.test.mjs'],consumer);
  run('clean-consumer-types',[path.join(source,'node_modules/typescript/bin/tsc'),'--project','tsconfig.json'],consumer);
  run('clean-consumer-browser',[path.join(copiedProbes,'browser.mjs'),source,consumer,output],consumer);
  summary.browser=JSON.parse(readFileSync(path.join(output,'browser-results.json'),'utf8'));
  assert.equal(summary.browser.results.length,6);
  summary.images=manifest(output,summary.browser.results.map(result=>result.screenshot));
  summary.canonicalPrompts=manifest(source,['README.md','system.md','request.md'].map(name=>'prompts/v1/'+name));
  summary.probes=manifest(copiedProbes,walk(copiedProbes));
  summary.rawConsumer=manifest(consumer,['raw-prompts.test.mjs','expected.json','types.mts','tsconfig.json']);
  summary.ownAssetBundles=manifest(path.join(source,'node_modules'),['vega/build/vega.min.js','vega-lite/build/vega-lite.min.js','vega-embed/build/vega-embed.min.js','echarts/dist/echarts.min.js','@antv/g2/dist/g2.min.js','plotly.js-dist-min/plotly.min.js']);
  assert.deepEqual(manifest(source,productFiles),summary.productFiles,'Source bytes changed during acceptance');
  run('source-clean-after',['diff','--exit-code','HEAD','--','package.json','package-lock.json','packages/deepviz','prompts','schemas'],source,'git');
  summary.status='PASS';summary.finished=new Date().toISOString();save();
  console.log(JSON.stringify({status:summary.status,commit:summary.commit,tarSha256:packs[0].sha256,tarFiles:packs[0].members.length,unchangedRuntimeFiles:previousRuntime.length,summary:path.join(output,'summary.json')}));
} catch(error){summary.status='FAIL';summary.error=error.message;save();console.error(summary.error);process.exitCode=1;}
