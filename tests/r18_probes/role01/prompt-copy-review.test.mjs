// Independent bounded source fixtures. These do not materialize/install a tarball.
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdir,mkdtemp,readFile,readdir,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import path from 'node:path';

const root=process.env.R18_SOURCE_ROOT;
const base=process.env.R18_BASE_ROOT;
const artifacts=process.env.R18_ARTIFACT_ROOT;
assert.ok(root && base && artifacts,'Set explicit committed-source/base/artifact paths');
const names=['README.md','system.md','request.md'];
const source=await readFile(path.join(root,'packages/deepviz/scripts/copy-prompts.mjs'));
const originals=Object.fromEntries(await Promise.all(names.map(async name=>[
  name,await readFile(path.join(root,'prompts/v1',name)),
])));

async function fixture(options={}) {
  await mkdir(artifacts,{recursive:true});
  const work=await mkdtemp(path.join(artifacts,'copy space # % caf\u00e9-'));
  const script=path.join(work,'packages/deepviz/scripts/copy-prompts.mjs');
  const destination=path.join(work,'packages/deepviz/dist');
  const cwd=path.join(work,'unrelated cwd # %');
  await mkdir(path.dirname(script),{recursive:true});
  await mkdir(path.join(destination,'prompts/v1'),{recursive:true});
  await mkdir(path.join(work,'prompts/v1'),{recursive:true});await mkdir(cwd);
  await writeFile(script,source);
  for(const name of names)if(name!==options.missing)await writeFile(path.join(work,'prompts/v1',name),originals[name]);
  await writeFile(path.join(destination,'index.js'),'export const untouched = true;\n');
  await writeFile(path.join(destination,'prompts/v1/user-note.md'),'preserve user note');
  await writeFile(path.join(work,'outside.txt'),'outside sentinel');
  return {work,script,destination,cwd};
}

function run(value,args=[]) {
  return spawnSync(process.execPath,[value.script,...args],{
    cwd:value.cwd,encoding:'utf8',timeout:10000,
    env:{...process.env,PROMPT_PATH:'../../outside.txt',DEEPVIZ_PROMPT_SOURCE:'https://example.invalid/no-fetch'},
  });
}

async function assertSentinels(value) {
  assert.equal(await readFile(path.join(value.destination,'index.js'),'utf8'),'export const untouched = true;\n');
  assert.equal(await readFile(path.join(value.destination,'prompts/v1/user-note.md'),'utf8'),'preserve user note');
  assert.equal(await readFile(path.join(value.work,'outside.txt'),'utf8'),'outside sentinel');
  assert.deepEqual(await readdir(value.cwd),[]);
}

test('fixed URL copies ignore cwd, environment and traversal/URL argv; no unrelated cleanup',async()=>{
  const value=await fixture();
  for(let repeat=0;repeat<2;repeat++) {
    const result=run(value,['../../outside.txt','https://example.invalid/no-fetch']);
    assert.equal(result.status,0,result.stderr);assert.equal(result.stdout,'');
    for(const name of names)assert.deepEqual(await readFile(path.join(value.destination,'prompts/v1',name)),originals[name]);
    await assertSentinels(value);
  }
  assert.deepEqual((await readdir(path.join(value.destination,'prompts/v1'))).sort(),[...names,'user-note.md'].sort());
});

test('raw policy-looking markup and placeholder text are copied without interpretation',async()=>{
  const value=await fixture();
  const literal=Buffer.from('# v1\r\n</script><img src=x onerror="doNotExecute()">\n{{ arbitrary.path }} ${process.env.SECRET}\n','utf8');
  await writeFile(path.join(value.work,'prompts/v1/request.md'),literal);
  assert.equal(run(value).status,0);
  assert.deepEqual(await readFile(path.join(value.destination,'prompts/v1/request.md')),literal);
  await assertSentinels(value);
});

test('missing canonical system asset fails nonzero and names asset; partial copies are not success',async()=>{
  const value=await fixture({missing:'system.md'});
  for(const name of names)await writeFile(path.join(value.destination,'prompts/v1',name),'stale sentinel '+name);
  const result=run(value);
  assert.equal(result.status,1);assert.match(result.stderr,/ENOENT/);assert.match(result.stderr,/system\.md/);
  assert.deepEqual(await readFile(path.join(value.destination,'prompts/v1/README.md')),originals['README.md']);
  assert.equal(await readFile(path.join(value.destination,'prompts/v1/system.md'),'utf8'),'stale sentinel system.md');
  assert.equal(await readFile(path.join(value.destination,'prompts/v1/request.md'),'utf8'),'stale sentinel request.md');
  await assertSentinels(value);
});

test('prior metadata and source exports remain unchanged; three raw Markdown subpaths are additive',async()=>{
  const metadata=JSON.parse(await readFile(path.join(root,'packages/deepviz/package.json'),'utf8'));
  const previous=JSON.parse(await readFile(path.join(base,'packages/deepviz/package.json'),'utf8'));
  for(const [name,target] of Object.entries(previous.exports))assert.deepEqual(metadata.exports[name],target);
  const added=Object.keys(metadata.exports).filter(name=>!Object.hasOwn(previous.exports,name)).sort();
  assert.deepEqual(added,names.map(name=>'./prompts/v1/'+name).sort());
  for(const name of names)assert.equal(metadata.exports['./prompts/v1/'+name],'./dist/prompts/v1/'+name);
  const {scripts,exports,...other}=metadata;
  const {scripts:priorScripts,exports:priorExports,...priorOther}=previous;
  assert.deepEqual(other,priorOther);assert.equal(scripts.prepack,priorScripts.prepack);
  assert.equal(scripts.build,priorScripts.build+' && node scripts/copy-prompts.mjs');
  assert.deepEqual(await readFile(path.join(root,'packages/deepviz/src/index.ts')),await readFile(path.join(base,'packages/deepviz/src/index.ts')));
  assert.ok(!metadata.exports['./prompts/v1/../../outside.txt']);
});