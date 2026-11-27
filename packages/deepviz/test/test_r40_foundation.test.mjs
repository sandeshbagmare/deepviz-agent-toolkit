import assert from 'node:assert/strict';
import {readFile,mkdtemp,writeFile,rm} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import test from 'node:test';

const root=new URL('../../../',import.meta.url);
test('R40: native output gate refuses an existing image before loading optional browser tooling',async()=>{
  const output=await mkdtemp(path.join(tmpdir(),'deepviz-r40-native-'));
  try{
    const image=path.join(output,'native-svg.png');await writeFile(image,'caller-owned sentinel');
    const result=spawnSync(process.execPath,[fileURLToPath(new URL('../scripts/check-native-output.mjs',import.meta.url)),output],{encoding:'utf8',timeout:10000});
    assert.equal(result.status,1);assert.match(result.stderr,/Refuse to overwrite native-svg\.png/);
    assert.equal(await readFile(image,'utf8'),'caller-owned sentinel');
  }finally{await rm(output,{recursive:true,force:true});}
});
test('R40: a no-install materialized packed-consumer gate is publicly runnable',async()=>{
  const metadata=JSON.parse(await readFile(new URL('package.json',root),'utf8'));
  assert.equal(metadata.scripts['package:materialized'],'node packages/deepviz/scripts/check-materialized-package.mjs');
  const checker=await readFile(new URL('packages/deepviz/scripts/check-materialized-package.mjs',root),'utf8');
  assert.ok(checker.includes('cleanInstalled: false'));
  assert.ok(!checker.includes("'install'"),'The materialized gate must not install dependencies');
});
test('R40: npm-only CI retains full tests, schema and actual public tarball gate',async()=>{
  const workflow=await readFile(new URL('.github/workflows/npm-foundation.yml',root),'utf8');
  for(const command of ['npm ci','npm run build','npm run typecheck','npm test','npm run schema:check','npm pack','npm run package:materialized'])assert.ok(workflow.includes(command),command);
  assert.ok(!workflow.includes('continue-on-error'));
});
test('R40: installed README does not present obsolete budgets or unmerged schema as shipped',async()=>{
  const text=await readFile(new URL('packages/deepviz/README.md',root),'utf8');
  assert.ok(text.includes('Draft foundation'));
  assert.ok(text.includes('manually materialized'));
  assert.ok(text.includes('64 KiB'));
  assert.ok(!text.includes('truncate at 10000'));
  assert.ok(!text.includes('../../docs/'));
});
test('R40: extracted root and workspace keep the original dependency lock agreement',async()=>{
  const metadata=JSON.parse(await readFile(new URL('package.json',root),'utf8'));
  const lock=JSON.parse(await readFile(new URL('package-lock.json',root),'utf8'));
  assert.deepEqual(lock.packages[''].devDependencies,metadata.devDependencies);
  assert.deepEqual(metadata.workspaces,['packages/deepviz']);
  assert.equal(lock.packages['packages/deepviz'].version,'0.1.0');
});
