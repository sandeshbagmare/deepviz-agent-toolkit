import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import path from 'node:path';
import {sourceSha} from './fixtures.mjs';
const evidence=path.resolve(process.argv[2]);
const identity=JSON.parse(await readFile(path.join(evidence,'identity.json'),'utf8'));
const source=identity.source_directory;
const git=(...args)=>execFileSync('git',['-C',source,...args]).toString().trim();
assert.equal(git('rev-parse','HEAD'),sourceSha);
assert.equal(git('status','--porcelain'),'');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
for(const file of identity.sourceProof){
  const bytes=await readFile(path.join(source,file.file));
  assert.equal(hash(bytes),file.working_sha256);assert.equal(git('rev-parse',`${sourceSha}:${file.file}`),file.git_blob);
}
for(const file of identity.buildProof)assert.equal(hash(await readFile(path.join(source,'packages/deepviz/dist',file.file))),file.sha256);
const tools=[];const require=createRequire(import.meta.url);
for(const dependency of ['typescript','playwright']){
  const packagePath=require.resolve(`${dependency}/package.json`),bytes=await readFile(packagePath),pkg=JSON.parse(bytes.toString());
  tools.push({dependency,version:pkg.version,installed_package_path:packagePath,package_sha256:hash(bytes)});
}
const captures=JSON.parse(await readFile(path.join(evidence,'captures.json'),'utf8'));
for(const capture of captures)assert.equal(hash(await readFile(path.join(evidence,'captures',capture.file))),capture.sha256);
const result={observed_at:new Date().toISOString(),source_sha:sourceSha,source_clean:true,
  source_working_hashes_rechecked:identity.sourceProof.length,compiled_dist_hashes_rechecked:identity.buildProof.length,
  actual_published_capture_hashes_rechecked:captures.length,all_original66_capture_hashes_checked_by_collector:true,
  installed_tools_read_only:true,dependencies_installed:false,tools,
  original_oracles_and_source_edited:false,no_shared_git_or_GitHub_write:true};
await writeFile(path.join(evidence,'final-source-verification.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
