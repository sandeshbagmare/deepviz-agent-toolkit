import assert from 'node:assert/strict';
import test from 'node:test';
import {normalize,normalizeStream} from '../dist/index.js';

const sum={kind:'table',x:'g',y:'v',aggregation:'sum'};
const tiny=Number.MIN_VALUE;
const permutations=[ [1e308,1e308,-1e308], [1e308,-1e308,1e308], [-1e308,1e308,1e308] ];

for(const values of permutations) for(const sign of [1,-1]) {
  test(`finite final SUM survives transient overflow permutation ${sign}:${values}`,async()=>{
    const rows=values.map(v=>({g:'all',v:sign*v}));
    for(const result of [normalize(rows,sum),await normalizeStream(rows,sum)]) {
      assert.deepEqual(result.records,[{g:'all',v:sign*1e308}]);
      assert.equal(result.input_count,3);
      assert.deepEqual(result.warnings,[]);
    }
  });
}

for(const residual of [0,1,-1,tiny,-tiny]) {
  test(`overflow cancellation keeps residual ${residual} including subnormal precision`,()=>{
    const values=[1e308,1e308,residual,-1e308,-1e308];
    const result=normalize(values.map(v=>({g:'all',v})),sum);
    assert.deepEqual(result.records,[{g:'all',v:residual}]);
    assert.equal(result.input_count,5);
    assert.deepEqual(result.warnings,[]);
  });
}

test('fallback retains pre-overflow compensation and independent groups',()=>{
  const rows=[...([1e308,1,1e308,-1e308,-1e308].map(v=>({g:'a',v}))),
    ...([-1e308,-1e308,1e308].map(v=>({g:'b',v}))),{g:'empty',v:null}];
  const result=normalize(rows,sum);
  assert.deepEqual(result.records,[{g:'a',v:1},{g:'b',v:-1e308},{g:'empty',v:null}]);
  assert.equal(result.input_count,rows.length);
  assert.deepEqual(result.warnings,[]);
});

for(const [tail,expected] of [
  [[1,2**-53],1],
  [[1,2**-53,tiny],1+Number.EPSILON],
  [[1,3*2**-53],1+2*Number.EPSILON],
  [[Number.MAX_VALUE],Number.MAX_VALUE],
  [[2**-1022,-tiny],2**-1022-tiny],
]) test(`fallback rounds ties to even and retains boundary values: ${tail}`,()=>{
  const values=[1e308,1e308,-1e308,-1e308,...tail];
  assert.equal(normalize(values.map(v=>({g:'all',v})),sum).records[0].v,expected);
});

test('fallback state transfers to the other bucket on eviction',async()=>{
  const rows=Array.from({length:9},(_,i)=>({g:`keep${i}`,v:i}));
  rows.push(...[1e308,1e308,tiny].map(v=>({g:'evicted',v})),
    ...[-1e308,-1e308].map(v=>({g:'new',v})),{g:'keep0',v:7});
  const result=await normalizeStream(rows,{...sum,max_points:10});
  assert.equal(result.records.length,10);
  assert.deepEqual(result.records[0],{g:'keep0',v:7});
  assert.deepEqual(result.records.at(-1),{g:'__deepviz_other__',v:tiny});
  assert.equal(result.input_count,rows.length);
  assert.ok(result.warnings.some(w=>/other bucket/i.test(w)));
  assert.ok(!result.warnings.some(w=>/non-finite/i.test(w)));
});

for(const sign of [1,-1]) test(`truly unrepresentable ${sign} final sum stays JSON-safe warned null`,()=>{
  const result=normalize([{g:'all',v:sign*Number.MAX_VALUE},{g:'all',v:sign*Number.MAX_VALUE}],sum);
  assert.deepEqual(result.records,[{g:'all',v:null}]);
  assert.ok(result.warnings.some(w=>/non-finite/i.test(w)));
  assert.ok(!/Infinity|NaN/.test(JSON.stringify(result)));
});

test('SUM fix leaves compensated small values, means, counts, integer policy and nonfinite input unchanged',()=>{
  assert.equal(normalize([1e16,1,-1e16].map(v=>({g:'all',v})),sum).records[0].v,1);
  assert.equal(normalize([Number.MAX_SAFE_INTEGER,1,1].map(v=>({g:'all',v})),sum).records[0].v,9007199254740992);
  const rows=[1e308,1e308,-1e308,null,'bad',NaN].map(v=>({g:'all',v}));
  const mean=normalize(rows,{...sum,aggregation:'mean'});
  assert.ok(Math.abs(mean.records[0].v-1e308/3)<=(1e308/3)*1e-15);
  assert.ok(mean.warnings.some(w=>/non-finite/i.test(w)));
  assert.equal(normalize(rows,{...sum,aggregation:'count'}).records[0].v,6);
  assert.equal(normalize([{g:'all',v:tiny},{g:'all',v:tiny}],{...sum,aggregation:'mean'}).records[0].v,tiny);
});

test('a one-pass fallback stream retains subnormal mass without a growing partial list',async()=>{
  let consumed=0;
  async function* rows(){for(let i=0;i<2000;i++)for(const v of [1e308,1e308,tiny,-1e308,-1e308]){consumed++;yield {g:'all',v};}}
  const result=await normalizeStream(rows(),sum);
  assert.equal(result.input_count,10000);
  assert.equal(consumed,10000);
  assert.deepEqual(result.records,[{g:'all',v:2000*tiny}]);
});

test('fallback group state is charged to the incremental retained byte budget',async()=>{
  let consumed=0;
  async function* rows(){for(let i=0;i<100000;i++)for(const v of [1e308,1e308,-1e308]){consumed++;yield {g:String(i),v};}}
  await assert.rejects(normalizeStream(rows(),{...sum,max_points:100000}),/16.*MiB/);
  assert.ok(consumed<150000,`fallback state was not budgeted early: consumed ${consumed}`);
});
