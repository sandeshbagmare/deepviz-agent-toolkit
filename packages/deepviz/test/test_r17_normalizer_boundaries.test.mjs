import assert from 'node:assert/strict';
import test from 'node:test';
import {normalize,normalizeStream} from '../dist/index.js';

const tiny=Number.MIN_VALUE;
// Literal means of exact binary64 values; Python independently checks Fraction rounding.
const cases=[
  ['split-positive',[1,tiny,-1,tiny,tiny],tiny],
  ['split-negative',[-1,-tiny,1,-tiny,-tiny],-tiny],
  ['overflow-tiny-tail',[1e308,1e308,-1e308,-1e308,4*tiny],tiny],
  ['late-overflow',[...Array(32).fill(8*tiny),1e308,1e308,-1e308,-1e308],7*tiny],
  ['constant-tiny',Array(5).fill(tiny),tiny],
  ['tie-even',[tiny,2*tiny],2*tiny],
  ['positive-half-zero',[0,tiny],0],
  ['negative-half-zero',[0,-tiny],-0],
  ['wide-numerator',[...Array(32).fill(0),1e308,1e308],5.882352941176471e306],
  ['prefix-residual',[1e30,1,-1e30,tiny,1e308,1e308,-1e308,-1e308],0.125],
];
for(const [name,values,expected] of cases)for(const stream of [false,true]) {
  test(`mean rounds once ${name} ${stream?'async-one-pass':'records'}`,async()=>{
    let consumed=0;
    const rows=values.map(v=>({g:'only',v}));
    async function* records(){for(const row of rows){consumed++;yield row;}}
    const spec={kind:'bar',x:'g',y:'v',aggregation:'mean',max_points:10};
    const result=stream?await normalizeStream(records(),spec):normalize(rows,spec);
    assert.equal(result.input_count,values.length);
    assert.equal(result.strategy,'mean');assert.deepEqual(result.warnings,[]);
    assert.deepEqual(result.records,[{g:'only',v:expected}]);
    assert.equal(consumed,stream?values.length:0);
    assert.ok(Number.isFinite(result.records[0].v));
  });
}
test('other mean preserves tiny values and excludes booleans/null/numeric strings',()=>{
  const rows=Array.from({length:9},(_,i)=>({g:`g${i}`,v:i}));
  const values=[1e308,1e308,-1e308,-1e308,6*tiny,true,null,'2'];
  const result=normalize([...rows,...values.map((v,i)=>({g:`overflow${i}`,v}))],{x:'g',y:'v',aggregation:'mean',max_points:10});
  assert.equal(result.input_count,17);assert.equal(result.records.length,10);
  assert.deepEqual(result.records.slice(0,9),rows);
  assert.deepEqual(result.records[9],{g:'__deepviz_other__',v:tiny});
  assert.ok(result.warnings.some(message=>/non-numeric/i.test(message)));
  assert.ok(result.warnings.some(message=>/other/i.test(message)));
});
