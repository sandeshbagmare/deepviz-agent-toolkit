import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {existsSync,readFileSync,writeFileSync,readdirSync,mkdirSync,copyFileSync,realpathSync,lstatSync,statSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import path from 'node:path';

const {values}=parseArgs({options:{source:{type:'string'},output:{type:'string'},'expected-source':{type:'string'},'npm-cli':{type:'string'},install:{type:'boolean',default:false}}});
assert.ok(values.source&&values.output,'Usage: verify-packed-consumer.mjs --source SOURCE --output NEW_EXTERNAL_DIRECTORY [--expected-source SHA] [--npm-cli FILE] [--install]');
const source=realpathSync(path.resolve(values.source));
const output=path.resolve(values.output);
const probes=fileURLToPath(new URL('./',import.meta.url));
assert.ok(!existsSync(output),'Refuse to overwrite an existing evidence/consumer directory');
assert.ok(path.relative(source,output).startsWith(`..${path.sep}`),'Output must be outside the source workspace');
mkdirSync(output);
const env={...process.env,npm_config_cache:path.join(output,'npm-cache'),npm_config_audit:'false',npm_config_fund:'false',npm_config_update_notifier:'false'};
delete env.NODE_PATH;
const commands=[];
const summary={started:new Date().toISOString(),sourceDirectory:source,outputDirectory:output,node:process.version,commands,checks:{},limitations:['Not a final source freeze, release, CI or independent multi-reviewer signoff','Browser dependencies are installed development bundles served locally, not vendor assets bundled inside the tarball','Only the installed Node/Chromium versions and bounded two-row light-theme charts are exercised']};
const save=()=>writeFileSync(path.join(output,'summary.json'),JSON.stringify(summary,null,2));
const hash=filename=>createHash('sha256').update(readFileSync(filename)).digest('hex');
function run(label,executable,args,cwd=source) {
  const started=new Date().toISOString();
  const result=spawnSync(executable,args,{cwd,env,encoding:'utf8',timeout:240000,maxBuffer:16*1024*1024});
  writeFileSync(path.join(output,`${label}.stdout.log`),result.stdout??'');
  writeFileSync(path.join(output,`${label}.stderr.log`),result.stderr??'');
  commands.push({label,executable,args,cwd,started,exit:result.status,signal:result.signal,error:result.error?.message??null});
  save();
  console.log(`${label}: exit=${result.status}${result.error?' process error':''}`);
  return result;
}
function required(label,executable,args,cwd) {
  const result=run(label,executable,args,cwd);
  assert.equal(result.status,0,`${label} failed; inspect retained logs`);
  return result.stdout;
}
function snapshot(root,files) {return files.map(name=>({name,bytes:statSync(path.join(root,name)).size,sha256:hash(path.join(root,name))}));}

try {
  summary.checkout=required('source-head','git',['rev-parse','HEAD']).trim();
  const pin=values['expected-source']??summary.checkout;
  summary.productSource=required('product-source','git',['rev-parse',`${pin}^{commit}`]).trim();
  required('source-ancestor','git',['merge-base','--is-ancestor',summary.productSource,'HEAD']);
  const sourcePaths=['package.json','package-lock.json','packages/deepviz','schemas','prompts'];
  required('product-diff-before','git',['diff','--exit-code',summary.productSource,'--',...sourcePaths]);
  const packageMetadata=JSON.parse(readFileSync(path.join(source,'packages/deepviz/package.json'),'utf8'));
  const workspaceMetadata=JSON.parse(readFileSync(path.join(source,'package.json'),'utf8'));
  const sourceFiles=['package.json','package-lock.json','packages/deepviz/package.json','packages/deepviz/tsconfig.json','schemas/chart-spec.schema.json','prompts/v1/system.md','prompts/v1/request.md',...readdirSync(path.join(source,'packages/deepviz/src')).map(name=>`packages/deepviz/src/${name}`)];
  summary.sourceFiles=snapshot(source,sourceFiles);
  const candidates=[values['npm-cli'],process.env.npm_execpath,path.join(path.dirname(process.execPath),'node_modules/npm/bin/npm-cli.js'),path.resolve(path.dirname(process.execPath),'../lib/node_modules/npm/bin/npm-cli.js')];
  const npm=candidates.find(filename=>filename&&existsSync(filename)&&filename.endsWith('.js'));
  assert.ok(npm,'npm CLI not located; pass --npm-cli /path/to/npm-cli.js');
  summary.npm={path:npm,sha256:hash(npm),version:required('npm-version',process.execPath,[npm,'--version']).trim()};
  if(values.install) {
    assert.ok(!existsSync(path.join(source,'node_modules')),'--install requires a fresh own source dependency tree');
    required('npm-ci',process.execPath,[npm,'ci','--ignore-scripts','--no-audit','--no-fund']);
  } else assert.ok(existsSync(path.join(source,'node_modules/typescript/bin/tsc')),'Own source dependencies absent; rerun with --install in a fresh own worktree');
  summary.installScriptsDisabled=values.install;
  for(const [label,args] of [['build',['run','build']],['typecheck',['run','typecheck']],['tests',['test']],['schema',['run','schema:check']],['package-check',['run','package:check']],['dry-run',['pack','--dry-run','--workspace','@deepviz/agent-toolkit']]]) {
    const result=run(label,process.execPath,[npm,...args]);
    summary.checks[label]=result.status===0?'PASS':'FAIL';
    if(['build','typecheck','schema'].includes(label)) assert.equal(result.status,0,`${label} prerequisite failed`);
  }
  const packDirectory=path.join(output,'pack');
  mkdirSync(packDirectory);
  required('actual-pack',process.execPath,[npm,'pack','--workspace','@deepviz/agent-toolkit','--pack-destination',packDirectory]);
  const tarballs=readdirSync(packDirectory).filter(name=>name.endsWith('.tgz'));
  assert.equal(tarballs.length,1);
  const tarball=path.join(packDirectory,tarballs[0]);
  const members=required('tarball-list','tar',['-tzf',tarball]).trim().split(/\r?\n/).sort();
  for(const file of ['package/LICENSE','package/README.md','package/dist/index.js','package/dist/index.d.ts','package/dist/chart-spec.schema.json']) assert.ok(members.includes(file),file);
  assert.equal(members.some(name=>name.startsWith('package/src/')||name.startsWith('package/test/')||name.includes('/node_modules/')),false);
  summary.tarball={path:tarball,bytes:statSync(tarball).size,sha256:hash(tarball),members,prompts:members.filter(name=>name.includes('/prompts/'))};
  const consumer=path.join(output,'consumer');
  mkdirSync(consumer);
  const enclosingGit=run('consumer-git-isolation','git',['rev-parse','--show-toplevel'],consumer);
  assert.notEqual(enclosingGit.status,0,'Consumer must not be inside any Git workspace');
  for(let parent=path.dirname(consumer);;parent=path.dirname(parent)) {
    const metadata=path.join(parent,'package.json');
    if(existsSync(metadata)) assert.equal(Boolean(JSON.parse(readFileSync(metadata,'utf8')).workspaces),false,'Consumer has an enclosing npm workspace');
    if(parent===path.dirname(parent)) break;
  }
  writeFileSync(path.join(consumer,'package.json'),JSON.stringify({name:'r10-08-packed-consumer',private:true,type:'module'}));
  required('consumer-install',process.execPath,[npm,'install','--offline','--ignore-scripts','--no-audit','--no-fund','--workspaces=false','--package-lock=false',tarball],consumer);
  const installed=path.join(consumer,'node_modules/@deepviz/agent-toolkit');
  assert.equal(lstatSync(installed).isSymbolicLink(),false);
  summary.consumer={path:consumer,installedPackage:realpathSync(installed),distFiles:[]};
  for(const name of readdirSync(path.join(source,'packages/deepviz/dist'))) {
    assert.equal(hash(path.join(installed,'dist',name)),hash(path.join(source,'packages/deepviz/dist',name)),`Installed byte identity: ${name}`);
    summary.consumer.distFiles.push(...snapshot(installed,[`dist/${name}`]));
  }
  const names={vega:['vega','build/vega.min.js'],vegaLite:['vega-lite','build/vega-lite.min.js'],vegaEmbed:['vega-embed','build/vega-embed.min.js'],echarts:['echarts','dist/echarts.min.js'],antv:['@antv/g2','dist/g2.min.js'],plotly:['plotly.js-dist-min','plotly.min.js']};
  const assets={};
  summary.assets=[];
  for(const [key,[name,file]] of Object.entries(names)) {
    const version=JSON.parse(readFileSync(path.join(source,'node_modules',name,'package.json'),'utf8')).version;
    assert.equal(version,workspaceMetadata.devDependencies[name],`Declared dependency version ${name}`);
    assets[key]=`https://cdn.jsdelivr.net/npm/${name}@${version}/${file}`;
    const asset=path.join(source,'node_modules',name,file);
    summary.assets.push({key,package:name,version,bytes:statSync(asset).size,sha256:hash(asset),url:assets[key]});
  }
  const expected={version:packageMetadata.version,schema:JSON.parse(readFileSync(path.join(source,'schemas/chart-spec.schema.json'),'utf8')),assets,prompts:Object.fromEntries(['system','request'].map(name=>[name,hash(path.join(source,`prompts/v1/${name}.md`))]))};
  writeFileSync(path.join(consumer,'expected.json'),JSON.stringify(expected,null,2));
  for(const filename of ['consumer.test.mjs','types.mts']) copyFileSync(path.join(probes,filename),path.join(consumer,filename));
  writeFileSync(path.join(consumer,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,noEmit:true,skipLibCheck:false,module:'NodeNext',moduleResolution:'NodeNext',target:'ES2022',types:[]},include:['types.mts']}));
  const consumerTests=run('consumer-tests',process.execPath,['--test','consumer.test.mjs'],consumer);
  summary.checks.consumer=consumerTests.status===0?'PASS':'FAIL';
  const types=run('consumer-types',process.execPath,[path.join(source,'node_modules/typescript/bin/tsc'),'--project','tsconfig.json'],consumer);
  summary.checks.types=types.status===0?'PASS':'FAIL';
  const browser=run('consumer-browser',process.execPath,[path.join(probes,'browser.mjs'),source,consumer,output],consumer);
  summary.checks.browser=browser.status===0?'PASS':'FAIL';
  required('product-diff-after','git',['diff','--exit-code',summary.productSource,'--',...sourcePaths]);
  assert.deepEqual(snapshot(source,sourceFiles),summary.sourceFiles,'Product source changed during verification');
  summary.probes=snapshot(probes,readdirSync(probes).filter(name=>statSync(path.join(probes,name)).isFile()));
  summary.finished=new Date().toISOString();
  summary.status=Object.values(summary.checks).every(value=>value==='PASS')?'PASS':'FAIL';
} catch(error) {
  summary.status='BLOCKED';
  summary.blocker=error.message;
} finally {
  save();
  console.log(JSON.stringify({status:summary.status,source:summary.productSource,tarballSha256:summary.tarball?.sha256,checks:summary.checks,blocker:summary.blocker??null,summary:path.join(output,'summary.json')}));
  process.exitCode=summary.status==='PASS'?0:1;
}
