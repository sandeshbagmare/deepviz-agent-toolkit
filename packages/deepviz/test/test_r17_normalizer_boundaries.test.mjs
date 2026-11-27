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

for(const name of ['rows','records','items','results','data','nodes','edges','pages'])for(const mapped of [false,true])for(const encoded of [false,true]) {
  test(`scalar column ${name} ${mapped?'explicit-y':'inferred'} ${encoded?'encoded-json':'object'}`,()=>{
    const data={[name]:[true,null,false]};
    const result=normalize(encoded?JSON.stringify(data):data,{kind:'table',aggregation:'none',...(mapped?{y:name}:{})});
    assert.equal(result.input_count,3);assert.equal(result.strategy,'none');assert.deepEqual(result.warnings,[]);
    assert.deepEqual(result.records,[{[name]:true},{[name]:null},{[name]:false}]);
  });
}
for(const stream of [false,true])test(`scalar sequence and nested flags survive ${stream?'async-one-pass':'records'}`,async()=>{
  const rows=[true,null,false,{flags:[true,null,false]}];
  async function* records(){yield* rows;}
  const result=stream?await normalizeStream(records(),{kind:'table',aggregation:'none'}):normalize(rows,{kind:'table',aggregation:'none'});
  assert.equal(result.input_count,4);assert.deepEqual(result.warnings,[]);
  assert.deepEqual(result.records,[{index:0,value:true},{index:1,value:null},{index:2,value:false},{'flags.0':true,'flags.1':null,'flags.2':false}]);
});
for(const key of ['nodes','edges'])for(const [label,sibling] of [['scalar',{version:7}],['object',{audit:{source:'left'}}]])for(const mode of ['object','encoded-json','async-one-pass']) {
  test(`connection ${key} rejects disappearing ${label} sibling ${mode}`,async()=>{
    const source={[key]:key==='nodes'?[{id:1}]:[{node:{id:1}}],...sibling},spec={kind:'table',aggregation:'none'};
    if(mode==='async-one-pass') {
      async function* pages(){yield source;}
      await assert.rejects(normalizeStream(pages(),spec),/ambiguous.*data_path/i);
    } else assert.throws(()=>normalize(mode==='encoded-json'?JSON.stringify(source):source,spec),/ambiguous.*data_path/i);
    assert.deepEqual(normalize(source,{...spec,data_path:key}).records,[{id:1}]);
  });
}
test('custom connection wrapper requires explicit selection',()=>{
  const source={payload:{nodes:[{id:1}]}};
  assert.throws(()=>normalize(source,{kind:'table',aggregation:'none'}),/custom.*data_path/i);
  assert.deepEqual(normalize(source,{kind:'table',aggregation:'none',data_path:'payload.nodes'}).records,[{id:1}]);
});
for(const key of ['nodes','edges'])test(`known nested ${key} connection preserves flags/nulls/metadata`,async()=>{
  const node={id:1,flag:false,flags:[true,null,false]},nodes=key==='nodes'?[node,null]:[{node},{node:null}];
  const source={data:{users:{[key]:nodes,totalCount:2}},errors:[{message:'partial'}]},spec={kind:'table',aggregation:'none'};
  async function* pages(){yield source;}
  for(const result of [normalize(source,spec),await normalizeStream(pages(),spec)]) {
    assert.equal(result.input_count,1);
    assert.deepEqual(result.records,[{id:1,flag:false,'flags.0':true,'flags.1':null,'flags.2':false}]);
    assert.ok(result.warnings.some(message=>/errors/.test(message)));
    assert.ok(result.warnings.some(message=>/null/i.test(message)));
  }
});
