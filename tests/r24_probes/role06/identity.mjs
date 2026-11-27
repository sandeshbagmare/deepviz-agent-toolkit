import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFile,realpath,readdir} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
export const baselineSha='5e595a8f893955ce34a0e26553bb7bf257ea93ae';
export const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const git=(directory,...args)=>execFileSync('git',['-C',directory,...args],{encoding:'utf8'}).trim();

export async function proveSource(source,expected,referencePath){
  assert.match(expected,/^[0-9a-f]{40}$/);
  const referenceBytes=await readFile(referencePath),reference=JSON.parse(referenceBytes.toString());
  assert.equal(reference.source_sha,expected,'A build manifest for this exact committed source is mandatory');
  assert.equal(git(source,'rev-parse','HEAD'),expected);
  assert.equal(git(source,'status','--porcelain'),'','Never import dirty producer source');
  assert.equal(git(source,'config','--get','remote.origin.url'),'https://github.com/sandeshbagmare/deepviz-agent-toolkit.git');
  const sourceProof=[];
  for(const file of reference.sourceProof){
    const working=await readFile(path.join(source,file.file));
    const committed=execFileSync('git',['-C',source,'show',`${expected}:${file.file}`]);
    assert.equal(git(source,'rev-parse',`${expected}:${file.file}`),file.git_blob);
    assert.equal(sha256(working),file.working_sha256,'Existing source changed since genuine build');
    assert.equal(working.toString().replace(/\r\n/g,'\n'),committed.toString().replace(/\r\n/g,'\n'));
    sourceProof.push({file:file.file,git_blob:file.git_blob,git_sha256:sha256(committed),working_sha256:sha256(working)});
  }
  const buildProof=[];
  for(const file of reference.buildProof){
    const bytes=await readFile(path.join(source,'packages/deepviz/dist',file.file));
    assert.equal(sha256(bytes),file.sha256,'Existing compiled output changed; do not silently rebuild');
    buildProof.push({file:file.file,bytes:bytes.length,sha256:sha256(bytes)});
  }
  assert.equal(sourceProof.length,11);assert.equal(buildProof.length,19);
  const publicEntry=await realpath(path.join(source,'packages/deepviz/dist/index.js'));
  assert.equal(path.relative(await realpath(source),publicEntry),path.join('packages','deepviz','dist','index.js'));
  const tests=[];
  for(const entry of (await readdir(new URL('.',import.meta.url))).filter(file=>file.endsWith('.mjs')).sort()){
    const bytes=await readFile(new URL(entry,import.meta.url));tests.push({file:entry,bytes:bytes.length,sha256:sha256(bytes)});
  }
  return {observed_at:new Date().toISOString(),source_sha:expected,source_directory:source,source_clean:true,
    expected_origin:git(source,'config','--get','remote.origin.url'),public_module:pathToFileURL(publicEntry).href,
    genuine_prior_build_reference:path.resolve(referencePath),reference_sha256:sha256(referenceBytes),
    reused_existing_build:true,new_build:false,sourceProof,buildProof,tests,node:process.version};
}
