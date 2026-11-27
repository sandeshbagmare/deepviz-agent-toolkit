// Evidence integrity only: reads the one completed eight-case run; never renders or launches a browser.
import assert from 'node:assert/strict';
import {copyFile,mkdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {sha256,proveSource} from './identity.mjs';
const [runArgument,setupArgument,targetArgument]=process.argv.slice(2);
const run=path.resolve(runArgument),setup=path.resolve(setupArgument),target=path.resolve(targetArgument);
const report=JSON.parse(await readFile(path.join(run,'report.json'),'utf8'));
const identity=JSON.parse(await readFile(path.join(run,'identity.json'),'utf8'));
const command=JSON.parse(await readFile(path.join(setup,'test-command.json'),'utf8'));
assert.equal(report.cases.length,8);assert.equal(report.counts.harness_errors,0);
assert.equal(report.counts.captures,2);assert.equal(command.exit,1);
assert.deepEqual(report.counts,{cases:8,correct_rendered:4,honest_rejections:0,failed_success_artifacts:4,checks:144,
  failures:32,observed_browser_errors:8,external_requests:0,captures:2,harness_errors:0,skipped:0});
const proof=await proveSource(identity.source_directory,identity.source_sha,identity.genuine_prior_build_reference);
assert.deepEqual(proof.sourceProof,identity.sourceProof);assert.deepEqual(proof.buildProof,identity.buildProof);
for(const test of identity.tests)assert.equal(sha256(await readFile(new URL(test.file,import.meta.url))),test.sha256,'Do not rewrite the executed strict fixture');
await mkdir(target,{recursive:false});await mkdir(path.join(target,'artifacts'));
const artifacts=[];
for(const row of report.cases){
  for(const extension of ['svg','html']){
    const file=`${row.id}.${extension}`,original=path.join(run,file),bytes=await readFile(original);
    assert.equal(sha256(bytes),row.native[`${extension}_sha256`]);
    const publish=extension==='svg'||row.kind==='area';
    if(publish)await copyFile(original,path.join(target,'artifacts',file));
    artifacts.push({file,bytes:bytes.length,sha256:sha256(bytes),published:publish});
  }
  if(row.capture){
    const bytes=await readFile(path.join(run,row.capture.file));assert.equal(sha256(bytes),row.capture.sha256);
    const file=path.basename(row.capture.file);await copyFile(path.join(run,row.capture.file),path.join(target,'artifacts',file));
    artifacts.push({file,bytes:bytes.length,sha256:sha256(bytes),published:true});
  }
}
for(const [from,to] of [['report.json','observations.json'],['identity.json','identity.json'],['fixtures.json','fixtures.json']])await copyFile(path.join(run,from),path.join(target,to));
for(const file of ['preflight.json','test-command.json','test.stdout.log','test.stderr.log'])await copyFile(path.join(setup,file),path.join(target,file));
await writeFile(path.join(target,'artifact-manifest.json'),JSON.stringify(artifacts,null,2));
const readback={observed_at:new Date().toISOString(),source_sha:identity.source_sha,strict_command_exit:command.exit,
  counts:report.counts,source_working_git_hashes_rechecked:proof.sourceProof.length,compiled_dist_hashes_rechecked:proof.buildProof.length,
  executed_test_hashes_unchanged:identity.tests,original_artifact_hashes_rechecked:artifacts.length,
  actual_published_artifacts:artifacts.filter(row=>row.published).length,no_product_or_browser_rerun:true,no_rebuild_or_installs:true,
  mandatory_zero_browser_error_gate:'FAIL: eight native SVG console parse errors retained; zero page errors is not zero browser errors',
  known_cause:'Role13 already demonstrated inherited finite-range overflow. No new issue filed; producer12 owns future repair.',
  future_committed_repair_received_or_tested:false,prior_R18_suite_replayed:false,final_candidate_approval:false};
await writeFile(path.join(target,'readback.json'),JSON.stringify(readback,null,2));
console.log(JSON.stringify(readback,null,2));
