import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {cases,sourceSha} from './fixtures.mjs';
import {assess,negativeControls} from './oracle.mjs';
const packet=JSON.parse(await readFile(new URL('../../../docs/coordination/evidence/R18-06/observations.json',import.meta.url),'utf8'));

test('saved real-DOM matrix has every public fixture once per actual SVG and HTML',()=>{
  assert.equal(packet.source_sha,sourceSha);assert.equal(packet.cases.length,66);assert.equal(cases.length,33);
  const identities=new Set(packet.cases.map(row=>`${row.id}/${row.format}`));assert.equal(identities.size,66);
  for(const fixture of cases)for(const format of ['svg','html'])assert(identities.has(`${fixture.id}/${format}`));
});
test('independent literal values/zero/spacing/ticks/geometry oracle accepts saved genuine measurements',()=>{
  let total=0;
  for(const row of packet.cases){
    const checks=assess(cases.find(fixture=>fixture.id===row.id),row.state,row.format);total+=checks.length;
    assert.deepEqual(checks.filter(check=>!check.pass),[],`${row.id}/${row.format}`);
    assert(row.screenshot_sha256.match(/^[0-9a-f]{64}$/));
  }
  assert.equal(total,1337); // 1403 includes the separately recorded public literal-title check on66artifacts.
});
test('blank/value/order/zero/tick/clipping/browser-error mutations are all rejected without oracle crashes',()=>{
  const row=packet.cases.find(item=>item.id==='area-scientific-240'&&item.format==='svg');
  const controls=negativeControls(cases.find(fixture=>fixture.id===row.id),row.state,'svg');
  assert.equal(controls.length,7);assert.deepEqual(controls.filter(control=>!control.rejected),[]);
});
