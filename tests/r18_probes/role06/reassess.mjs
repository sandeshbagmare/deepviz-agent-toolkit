// Re-score saved native DOM observations after observer-only corrections; never rerender or overwrite originals.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {cases,sourceSha} from './fixtures.mjs';
import {assess,negativeControls} from './oracle.mjs';
const directory=path.resolve(process.argv[2]);
const original=await readFile(path.join(directory,'browser-report-viewport.json'));
const report=JSON.parse(original.toString());
assert.equal(report.source_sha,sourceSha);assert.equal(report.cases.length,50);
const identities=new Set();
for(const row of report.cases){
  const fixture=cases.find(item=>item.id===row.id);assert(fixture);
  assert(row.state,`Missing original measurement: ${row.id}`);
  assert(!identities.has(`${row.id}/${row.format}`));identities.add(`${row.id}/${row.format}`);
  const image=await readFile(path.join(directory,'browser-viewport',row.screenshot));
  assert.equal(createHash('sha256').update(image).digest('hex'),row.sha256,'Actual capture changed');
  row.checks=assess(fixture,row.state,row.format);
  row.checks.push({name:'public-literal-title',pass:row.format==='svg'||row.state.htmlTitle===`R18 ${row.id}`,observed:row.state.htmlTitle});
}
const control=report.cases.find(row=>row.id==='area-scientific-240'&&row.format==='svg');
report.negativeControls=negativeControls(cases.find(item=>item.id===control.id),control.state,'svg');
report.reassessment={original_file:'browser-report-viewport.json',original_sha256:createHash('sha256').update(original).digest('hex'),
  no_browser_rerun:true, original_checks:1047,original_failures:10,original_negative_control_failures:1,
  observer_errata:[
    '1e-6 dimensionless x-gap tolerance falsely rejected SVGPointList float32 ratio3.9999984956; 1e-4 tolerance and original 0.02pixel independent literal geometry check both retained.',
    'Exact semicircle large-arc flag can be0 or1 because finite scientific total division is slightly above0.5; actual radius/center/endpoints/fractions remain independently checked.',
    'Blank mutation exposed own optional-mark access TypeError; explicit failures now preserved instead of throwing.',
  ]};
report.counts={artifacts:50,checks:report.cases.reduce((n,row)=>n+row.checks.length,0),
  failures:report.cases.reduce((n,row)=>n+row.checks.filter(check=>!check.pass).length,0),
  negative_controls:report.negativeControls.length,negative_controls_failed:report.negativeControls.filter(row=>!row.rejected).length,
  unsupported:0,skipped:0};
report.failures=report.cases.flatMap(row=>row.checks.filter(check=>!check.pass).map(check=>({id:row.id,format:row.format,...check})));
await writeFile(path.join(directory,'browser-report-reassessed.json'),JSON.stringify(report,null,2),{flag:'wx'});
console.log(JSON.stringify({source_sha:sourceSha,counts:report.counts,failures:report.failures,negativeControls:report.negativeControls},null,2));
assert.equal(report.counts.negative_controls_failed,0);
process.exitCode=report.counts.failures?1:0;
