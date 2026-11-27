import assert from 'node:assert/strict';
import test from 'node:test';
import {normalize,normalizeStream} from '@deepviz/agent-toolkit';

const mean={kind:'table',aggregation:'mean',y:'v'};
const near=(actual,expected)=>assert.ok(typeof actual==='number' && Number.isFinite(actual)
  && Math.abs(actual-expected)<=Math.abs(expected)*1e-15,`expected ${expected}, received ${actual}`);

test('compensated means retain the small cancellation residual',async()=>{
  const rows=[{v:1e16},{v:1},{v:-1e16}];
  assert.equal(normalize(rows,mean).records[0].v,1/3);
  assert.equal((await normalizeStream(rows,mean)).records[0].v,1/3);
});

test('subnormal identical observations do not underflow during mean updates',()=>{
  assert.equal(normalize([{v:Number.MIN_VALUE},{v:Number.MIN_VALUE}],mean).records[0].v,Number.MIN_VALUE);
});

test('rescaled mean numerators remain finite after same-sign overflow',()=>{
  for(const values of [[1e308,1e308],[1e308,1e308,-1e308]]) {
    const result=normalize(values.map(v=>({v})),mean);
    near(result.records[0].v,values.length===2?1e308:1e308/3);
    assert.deepEqual(result.warnings,[]);
  }
  for(const count of [2,3,32,1000]) {
    const result=normalize(Array.from({length:count},()=>({v:Number.MAX_VALUE})),mean);
    assert.equal(result.records[0].v,Number.MAX_VALUE);
    assert.deepEqual(result.warnings,[]);
  }
});

test('rescaled means preserve a residual after cancellation of overflowing finite inputs',()=>{
  const result=normalize([1e308,1e308,1,-1e308,-1e308].map(v=>({v})),mean);
  assert.equal(result.records[0].v,0.2);
  assert.deepEqual(result.warnings,[]);
});

test('other-bucket means transfer compensation and weight valid raw observations',async()=>{
  const rows=[...Array.from({length:9},(_,i)=>({g:`keep${i}`,v:0})),
    {g:'evicted',v:1e16},{g:'evicted',v:1},{g:'overflow',v:-1e16},
    {g:'overflow',v:null},{g:'overflow',v:'not numeric'}];
  const spec={...mean,x:'g',max_points:10};
  for(const result of [normalize(rows,spec),await normalizeStream(rows,spec)]) {
    assert.equal(result.input_count,14);
    assert.equal(result.records.length,10);
    assert.equal(result.records.find(row=>row.g==='__deepviz_other__').v,1/3);
    assert.ok(result.warnings.some(warning=>/group cardinality/i.test(warning)));
    assert.ok(result.warnings.some(warning=>/non-numeric measure/i.test(warning)));
  }
});

test('other-bucket means preserve the rescaling exponent through eviction',()=>{
  const rows=[...Array.from({length:9},(_,i)=>({g:`keep${i}`,v:0})),
    {g:'evicted',v:1e308},{g:'evicted',v:1e308},
    {g:'overflow',v:-1e308},{g:'overflow',v:-1e308},{g:'third',v:3}];
  const result=normalize(rows,{...mean,x:'g',max_points:10});
  assert.equal(result.records.find(row=>row.g==='__deepviz_other__').v,0.6);
});

test('all-null means and overflowing sums keep their existing explicit null semantics',()=>{
  assert.equal(normalize([{g:'a',v:null},{g:'a',v:'bad'}],{...mean,x:'g'}).records[0].v,null);
  const sum=normalize([{v:1e308},{v:1e308}],{...mean,aggregation:'sum'});
  assert.equal(sum.records[0].v,null);
  assert.ok(sum.warnings.some(warning=>/non-finite/i.test(warning)));
});

test('many retained mean groups still enforce the 16 MiB incremental state budget',async()=>{
  let consumed=0;
  async function* rows(){for(let i=0;i<100000;i++){consumed++;yield {g:`${i}:`+'x'.repeat(10000),v:i};}}
  await assert.rejects(()=>normalizeStream(rows(),{...mean,x:'g',max_points:100000}),/16.*MiB/i);
  assert.ok(consumed<1000,`state overflow must reject early, consumed ${consumed}`);
});
