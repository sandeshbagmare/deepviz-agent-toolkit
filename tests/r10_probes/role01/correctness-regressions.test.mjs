import test from 'node:test';
import assert from 'node:assert/strict';

import {normalize,normalizeStream,buildRendererSpec} from '../../../packages/deepviz/dist/index.js';

const identity={kind:'table',aggregation:'none'};
const names=['rows','records','items','results','data'];
const connection=key=>({[key]:key==='nodes'?[{id:1}]:[{node:{id:1}}]});



for(const key of ['nodes','edges']) {
  for(const [label,sibling] of [['scalar',{version:7}],['object',{audit:{source:'left'}}]]) {
    const source={...connection(key),...sibling};
    test(`F1 sync ${key} rejects unexpected ${label} sibling`,()=>{
      assert.throws(()=>normalize(source,identity),/ambiguous.*data_path/i);
    });
    test(`F1 async ${key} rejects unexpected ${label} sibling`,async()=>{
      async function* pages(){yield source;}
      await assert.rejects(normalizeStream(pages(),identity),/ambiguous.*data_path/i);
    });
  }
  test(`F1 encoded ${key} also rejects an ambiguous sibling`,()=>{
    assert.throws(()=>normalize(JSON.stringify({...connection(key),version:7}),{...identity,format:'json'}),/ambiguous.*data_path/i);
  });
  test(`F1 ${key} explicit path is valid in sync and async inputs`,async()=>{
    const source={...connection(key),version:7};
    for(const result of [normalize(source,{...identity,data_path:key}),await normalizeStream([source],{...identity,data_path:key})]) {
      assert.deepEqual(result.records,[{id:1}]);assert.equal(result.input_count,1);assert.deepEqual(result.warnings,[]);
    }
  });
  test(`F1 ${key} known metadata is not an ambiguity`,async()=>{
    const source={...connection(key),totalCount:7};
    assert.deepEqual(normalize(source,identity).records,[{id:1}]);
    assert.deepEqual((await normalizeStream([source],identity)).records,[{id:1}]);
  });
}

test('F1 custom GraphQL wrapper requires explicit selection',()=>{
  assert.throws(()=>normalize({payload:{nodes:[{id:1}]}},identity),/(ambiguous|custom).*data_path/i);
});
test('F1 custom GraphQL explicit selection is valid',()=>{
  assert.deepEqual(normalize({payload:{nodes:[{id:1}]}},{...identity,data_path:'payload.nodes'}).records,[{id:1}]);
});

for(const key of names) {
  test(`F3 ${key} scalar column preserves explicit mapping`,()=>{
    const result=normalize({[key]:[1,2]},{...identity,y:key});
    assert.deepEqual(result.records,[{[key]:1},{[key]:2}]);assert.equal(result.input_count,2);
  });
  test(`F3 ${key} nested record array retains parent identity`,()=>{
    const result=normalize([{id:7,[key]:[1,2]}],identity);
    assert.deepEqual(result.records,[{id:7,[`${key}.0`]:1,[`${key}.1`]:2}]);assert.equal(result.input_count,1);
  });
}

for(const engine of ['echarts','plotly','antv','vega'])test(`F2 ${engine} uses count rather than numeric color`,()=>{
  const result=buildRendererSpec([{g:'a',s:100},{g:'a',s:100}],{kind:'bar',x:'g',color:'s',aggregation:'count'},engine);
  assert.deepEqual(result.normalized.records,[{g:'a',s:100,count:2}]);
  const native=result.spec;
  const actual=engine==='echarts'?native.series.flatMap(series=>series.data):engine==='plotly'?native.data.flatMap(trace=>trace.y):
    engine==='antv'?native.data.map(row=>row[native.encode.y]):native.data.values.map(row=>row[native.encoding.y.field]);
  assert.deepEqual(actual,[2]);
});