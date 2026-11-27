import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,copyFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {cases,sourceSha} from './fixtures.mjs';
const [firstArgument,zeroArgument,targetArgument]=process.argv.slice(2);
const first=path.resolve(firstArgument),zero=path.resolve(zeroArgument),target=path.resolve(targetArgument);
await mkdir(target,{recursive:false});await mkdir(path.join(target,'captures'));
const hash=body=>createHash('sha256').update(body).digest('hex');
const load=async(directory,file)=>JSON.parse(await readFile(path.join(directory,file),'utf8'));
const initial=await load(first,'browser-report-viewport.json');
const corrected=await load(first,'browser-report-reassessed.json');
const added=await load(zero,'browser-report-viewport.json');
const manifests=[await load(first,'manifest.json'),await load(zero,'manifest.json')];
assert.equal(corrected.counts.failures,0);assert.equal(added.counts.failures,0);
assert.deepEqual(manifests[0].sourceProof,manifests[1].sourceProof);
assert.deepEqual(manifests[0].buildProof,manifests[1].buildProof);
const rows=[],seen=new Set();
for(const [directory,report] of [[first,corrected],[zero,added]]){
  assert.equal(report.source_sha,sourceSha);
  for(const row of report.cases){
    const identity=`${row.id}/${row.format}`;assert(!seen.has(identity));seen.add(identity);
    assert(cases.some(fixture=>fixture.id===row.id));
    const screenshot=await readFile(path.join(directory,'browser-viewport',row.screenshot));
    assert.equal(hash(screenshot),row.sha256,'Capture altered after original measurement');
    rows.push({id:row.id,format:row.format,checks:row.checks.map(({name,pass})=>({name,pass})),
      state:row.state,screenshot:row.screenshot,screenshot_sha256:row.sha256});
  }
}
assert.equal(rows.length,66);assert.equal(seen.size,cases.length*2);
const selection=['line-scientific-240-svg.png','scatter-negative-240-svg.png','area-scientific-240-svg.png',
  'bubble-negative-240-svg.png','line-negative-960-svg.png','pie-scientific-240-html.png',
  'area-scientific-240-html.png','bubble-positive-960-svg.png','area-zero-240-svg.png','scatter-zero-960-html.png'];
const captures=[];
for(const file of selection){
  const original=path.join(file.includes('-zero-')?zero:first,'browser-viewport',file);
  await copyFile(original,path.join(target,'captures',file));
  const body=await readFile(path.join(target,'captures',file));
  const row=rows.find(item=>item.screenshot===file);assert.equal(hash(body),row.screenshot_sha256);
  captures.push({file,sha256:hash(body),bytes:body.length});
}
const counts={fixtures:cases.length,artifacts:rows.length,checks:rows.reduce((n,row)=>n+row.checks.length,0),
  failures:rows.reduce((n,row)=>n+row.checks.filter(check=>!check.pass).length,0),
  console_or_page_errors:rows.reduce((n,row)=>n+row.state.errors.length,0),
  external_requests:rows.reduce((n,row)=>n+row.state.externalRequests.length,0),
  unsupported:0,skipped:0,negative_controls:corrected.negativeControls.length,
  negative_controls_failed:corrected.negativeControls.filter(row=>!row.rejected).length};
const identity={source_sha:sourceSha,chromium:corrected.chromium,node:manifests[0].node,
  source_directory:manifests[0].source_directory,public_module:manifests[0].public_module,
  sourceProof:manifests[0].sourceProof,buildProof:manifests[0].buildProof};
const observations={source_sha:sourceSha,counts,cases:rows};
const controls={source_sha:sourceSha,controls:corrected.negativeControls,
  original_browser_report_sha256:corrected.reassessment.original_sha256,
  original_browser_counts:initial.counts,original_observer_failures:initial.failures,
  original_negative_controls:initial.negativeControls,reassessment:corrected.reassessment};
for(const [file,data] of Object.entries({'identity.json':identity,'observations.json':observations,
  'observer-errata-controls.json':controls,'captures.json':captures})){
  await writeFile(path.join(target,file),JSON.stringify(data,null,2));
}
console.log(JSON.stringify({source_sha:sourceSha,counts,hash_verified_original_captures:66,published_original_captures:captures.length,target},null,2));
