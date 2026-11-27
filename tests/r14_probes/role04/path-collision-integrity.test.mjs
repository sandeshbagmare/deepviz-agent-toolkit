import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {normalize,normalizeStream,ValidationError} from '../../../packages/deepviz/dist/index.js';

const corpus=JSON.parse(readFileSync(new URL('./collision-cases.json',import.meta.url),'utf8'));
const base={kind:'table',aggregation:'none',max_points:100};
const clone=value=>structuredClone(value);
function reverseObjects(value){
  if(Array.isArray(value))return value.map(reverseObjects);
  if(value!==null && typeof value==='object')return Object.fromEntries(Object.entries(value).reverse().map(([key,item])=>[key,reverseObjects(item)]));
  return value;
}
function preserved(records,count,expected){assert.deepEqual(records,expected);assert.equal(count,expected.length);}
test('literal fixture really contains byte-distinct Unicode confusables',()=>{
  const row=corpus.preservations.find(item=>item.id==='byte-distinct-unicode-no-normalization').expected[0];
  assert.equal('cafe\u0301'.normalize('NFC'),'caf\u00e9');
  assert.notDeepEqual(Buffer.from('cafe\u0301','utf8'),Buffer.from('caf\u00e9','utf8'));
  assert.deepEqual(['caf\u00e9','cafe\u0301','a.b','a\uff0eb','\u0430.b'].map(key=>row[key]),[11,29,31,37,43]);
});
function ambiguity(error){
  assert.ok(error instanceof ValidationError);assert.match(error.message,/collid|collision|ambig/i);
  assert.ok(Buffer.byteLength(error.message,'utf8')<=240);return true;
}
for(const item of corpus.collisions)for(const reverse of [false,true])for(const carrier of ['records','json','selected']){
  test(`collision ${item.id}, reverse=${reverse}, ${carrier}`,()=>{
    const row=reverse?reverseObjects(item.row):clone(item.row),before=clone(row);
    let data=[row],spec={...base,x:'id',y:item.field};
    if(carrier==='json'){data=JSON.stringify(data);spec={...spec,format:'json'};}
    else if(carrier==='selected'){data={payload:{rows:data}};spec={...spec,data_path:'payload.rows'};}
    assert.throws(()=>normalize(data,spec),ambiguity);assert.deepEqual(row,before);
  });
}
for(const item of corpus.preservations)for(const carrier of ['records','jsonl']){
  test(`preserve ${item.id}, ${carrier}`,()=>{
    const data=clone(item.rows),before=clone(data);
    const spec={...base,...item.spec,...carrier==='jsonl'?{format:'jsonl'}:{}};
    const result=normalize(carrier==='jsonl'?data.map(row=>JSON.stringify(row)).join('\n'):data,spec);
    preserved(result.records,result.input_count,item.expected);
    assert.deepEqual(result.warnings,[]);assert.equal(result.strategy,'none');assert.deepEqual(data,before);
  });
}
for(const item of corpus.columns){
  test(`column integrity ${item.id}`,()=>{
    const data=clone(item.data),before=clone(data),spec={...base,...item.spec};
    if(item.reject)assert.throws(()=>normalize(data,spec),ambiguity);
    else{
      let result;
      try{result=normalize(data,spec);}catch(error){
        assert.equal(item.ambiguity_allowed,true);ambiguity(error);assert.match(error.message,/ambig/i);
      }
      if(result){
        preserved(result.records,result.input_count,item.expected);
        assert.deepEqual(result.warnings,[]);assert.equal(result.strategy,'none');
      }
    }
    assert.deepEqual(data,before);
  });
}
for(const item of corpus.selected){
  test(`explicit data_path ${item.id}`,()=>{
    const result=normalize(clone(item.data),{...base,...item.spec});
    preserved(result.records,result.input_count,item.expected);
    assert.deepEqual(result.warnings,[]);assert.equal(result.strategy,'none');
  });
}
function guarded(item,invalidIndex){
  const state={yielded:0,exhausted:false};
  const source={async *[Symbol.asyncIterator](){
    for(let index=0;index<60;index++){
      assert.ok(invalidIndex===null || index<=invalidIndex,'Consumed collision tail');
      state.yielded++;yield index===invalidIndex?clone(item.row):{id:index,[item.field]:index+11};
    }
    state.exhausted=true;
  }};
  return {source,state};
}
for(const item of corpus.collisions)for(const invalidIndex of [0,40]){
  test(`early collision ${item.id}, bad row ${invalidIndex+1}`,async()=>{
    const {source,state}=guarded(item,invalidIndex);
    await assert.rejects(normalizeStream(source,{...base,x:'id',y:item.field}),ambiguity);
    assert.deepEqual(state,{yielded:invalidIndex+1,exhausted:false});
  });
}
test('ordinary stream consumes past inference prefix with exact fields/counts',async()=>{
  const item=corpus.collisions[0],{source,state}=guarded(item,null);
  const result=await normalizeStream(source,{...base,x:'id',y:item.field});
  preserved(result.records,result.input_count,Array.from({length:60},(_,id)=>({id,'part.leaf':id+11})));
  assert.deepEqual(state,{yielded:60,exhausted:true});assert.deepEqual(result.warnings,[]);assert.equal(result.strategy,'none');
});
for(const corruption of ['last-write-only','dropped-field','wrong-count']){
  test(`strict oracle rejects corrupt success: ${corruption}`,()=>{
    const expected=[{literal:11,nested:29}];
    const rows=corruption==='last-write-only'?[{literal:29}]:corruption==='dropped-field'?[{literal:11}]:clone(expected);
    assert.throws(()=>preserved(rows,corruption==='wrong-count'?2:1,expected),assert.AssertionError);
  });
}
