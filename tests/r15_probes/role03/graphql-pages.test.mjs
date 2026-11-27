/** Public TS normalization only: exact values/counts/multiplicity and late-page errors. */
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {normalize, normalizeStream, ValidationError} from '../../../packages/deepviz/dist/index.js';
import {clone, corpus, lateFault, PullPages, raw, siblingPages, success} from './graphql-fixtures.mjs';

function assertResult(result, expected, notices) {
  assert.equal(result.input_count,expected.length,'count actual non-null rows, not page/server totals');
  assert.deepEqual(result.records,expected,'all supplied pages preserve order/scalar values/nested fields');
  const counter = rows => [...rows.reduce((map,row)=>{
    const key=JSON.stringify(Object.entries(row).sort(([a],[b])=>a.localeCompare(b)));
    map.set(key,(map.get(key)??0)+1);return map;
  },new Map())].sort(([a],[b])=>a.localeCompare(b));
  assert.deepEqual(counter(result.records),counter(expected),'do not deduplicate/invent repeated legitimate nodes');
  assert.equal(result.strategy,'none');
  const warnings=result.warnings.map(value=>value.toLowerCase());
  assert.equal(warnings.length,notices.length,'no silent loss or spurious warning');
  for(const notice of notices)assert.equal(warnings.filter(value=>value.includes(notice) && (notice!=='graphql' || value.includes('error'))).length,1);
  // TS warning strings are deduplicated categories, NOT exact null/page counts.
}

async function invoke(data,spec,carrier) {
  if(carrier==='json')return normalize(JSON.stringify(data),{...spec,format:'json'});
  if(carrier==='async') {
    const values=Array.isArray(data)?data:[data], source=new PullPages(values);
    const result=await normalizeStream(source,spec);
    assert.deepEqual(source.pulled,values.map((_,index)=>index));
    assert.equal(source.finished,true,'valid supplied source must be exhausted');
    return result;
  }
  return normalize(data,spec);
}

for(const name of corpus.successes)for(const carrier of ['list','json','async']) {
  test(`cross-page-empty-repeat:${name}:${carrier}`,async()=>{
    const {data,spec,expected,notices}=success(name), original=clone(data);
    assertResult(await invoke(data,spec,carrier),expected,notices);
    assert.deepEqual(data,original,'caller pages/cursors/errors/node records must remain unchanged');
  });
}

for(const fault of corpus.late_faults)for(const selected of [false,true])for(const carrier of ['list','json','async']) {
  test(`late-invalid-after-prefix-and-empty:${fault}:${selected?'explicit':'auto'}:${carrier}`,async()=>{
    const {data,spec}=lateFault(fault,selected),original=clone(data);
    const source=carrier==='async'?new PullPages(data,3):null;
    await assert.rejects(async()=>{
      if(source)return await normalizeStream(source,spec);
      return await invoke(data,spec,carrier);
    },error=>error instanceof ValidationError && /graphql|edge|node|colli/i.test(error.message) && error.message.length<=512);
    if(source)assert.deepEqual(source.pulled,[0,1,2],'stop before requesting any page after the invalid node');
    assert.deepEqual(data,original);
  });
}

for(const reverse of [false,true])for(const carrier of ['list','json','async']) {
  test(`late-multiple-connections-no-implicit-merge:${reverse?'shadow-first':'feed-first'}:${carrier}`,async()=>{
    const {data,spec}=lateFault('node-field-collision',false);
    const candidates=[['feed',{nodes:[{id:'left'}]}],['shadow',{nodes:[{id:'right'}]}]];
    data[2]={data:Object.fromEntries(reverse?candidates.reverse():candidates)};
    await assert.rejects(()=>invoke(data,spec,carrier),error=>error instanceof ValidationError && /ambiguous|data_path|multiple/i.test(error.message));
  });
}

for(const name of corpus.known_sibling_variants) {
  test(`DEDUP-R10-01-F1-late-sibling-loss-must-reject:${name}`,()=>{
    assert.throws(()=>normalize(siblingPages(name),raw),error=>error instanceof ValidationError && /ambiguous|data_path/i.test(error.message));
  });
}

for(const singlePage of [false,true])test(`minimal-valid-control:${singlePage?'single-page':'direct-records'}`,()=>{
  const rows=[{id:'repeat',measure:-3.25},{id:'repeat',measure:-3.25}];
  assertResult(normalize(singlePage?{data:{feed:{nodes:rows}}}:rows,raw),rows,[]);
});

for(const fault of ['error-only-response','error-only-no-data','error-only-empty-data']) {
  test(`direct-error-only-envelope-control:${fault}`,()=>{
    const {data}=lateFault(fault,false);
    assert.throws(()=>normalize(data.at(-1),raw),error=>error instanceof ValidationError && /graphql.*errors.*data/i.test(error.message));
  });
}

test('ordinary-business-errors-field-is-not-a-transport-envelope',async()=>{
  const source=[{id:'business-record',errors:[{message:'ordinary field value'}]}];
  const expected=[{id:'business-record','errors.0.message':'ordinary field value'}];
  assertResult(normalize(source,raw),expected,[]);
  assertResult(await normalizeStream((async function*(){yield* source;})(),raw),expected,[]);
});
