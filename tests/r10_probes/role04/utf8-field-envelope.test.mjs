import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {normalize,normalizeStream,ValidationError} from '../../../packages/deepviz/dist/index.js';

const cases=JSON.parse(readFileSync(new URL('./utf8-envelope-cases.json',import.meta.url),'utf8'));
const none={kind:'table',aggregation:'none',max_points:10};
const bytes=value=>Buffer.byteLength(value,'utf8');
function sizedText(size,unit){
  assert.equal(bytes(unit.text),unit.utf8_width);
  const text=unit.text.repeat(Math.floor(size/unit.utf8_width))+'x'.repeat(size%unit.utf8_width);
  assert.equal(bytes(text),size);
  return text;
}
function observed(rows){
  const state={yielded:0,iterations:0,exhausted:false,closed:false};
  const source={async *[Symbol.asyncIterator](){
    state.iterations++;
    try{
      for(const row of rows){state.yielded++;yield row;}
      state.exhausted=true;
    } finally {state.closed=true;}
  }};
  return {source,state};
}
function limitError(pattern){
  return error=>{
    assert.ok(error instanceof ValidationError);
    assert.match(error.message,pattern);
    return true;
  };
}

for(const unit of cases.units)for(const location of ['raw','composite','array-index'])for(const item of cases.names){
  test(`name ${location} ${unit.id} ${item.bytes} bytes`,()=>{
    const size=item.bytes;
    let field,row;
    if(location==='raw'){
      field=sizedText(size,unit);row={[field]:7};
    }else if(location==='composite'){
      const left=Math.floor((size-1)/2),outer=sizedText(left,unit),inner=sizedText(size-left-1,unit);
      field=`${outer}.${inner}`;row={[outer]:{[inner]:7}};
      assert.ok(bytes(outer)<65_536 && bytes(inner)<65_536);
    }else{
      const outer=sizedText(size-2,unit);field=`${outer}.0`;row={[outer]:[7]};
      assert.ok(bytes(outer)<=65_535);
    }
    assert.equal(bytes(field),size);
    if(item.typescript_accepts){
      const result=normalize([row],none);
      assert.deepEqual(result.records,[{[field]:7}]);assert.equal(result.input_count,1);
      assert.equal(result.strategy,'none');assert.deepEqual(result.warnings,[]);
    }else assert.throws(()=>normalize([row],none),limitError(/64 KiB UTF-8 limit/));
  });
}
for(const unit of cases.units)for(const item of cases.cells){
  test(`cell ${unit.id} ${item.bytes} bytes, no truncation`,()=>{
    const text=sizedText(item.bytes,unit);
    if(item.accepts){
      const result=normalize([{payload:text}],none);
      assert.deepEqual(result.records,[{payload:text}]);assert.equal(result.input_count,1);
      assert.equal(result.strategy,'none');assert.deepEqual(result.warnings,[]);
    }else assert.throws(()=>normalize([{payload:text}],none),limitError(/64 KiB UTF-8 limit/));
  });
}
test('fixture declares the exact language-specific name acceptance difference',()=>{
  assert.deepEqual(cases.names.filter(item=>item.python_accepts!==item.typescript_accepts).map(item=>item.bytes),[4097,65535,65536]);
  assert.deepEqual(cases.names.filter(item=>item.python_accepts).map(item=>item.bytes),[4095,4096]);
});

for(const unit of cases.units)for(const location of ['name','cell'])for(const invalidIndex of [0,40]){
  test(`early consumption ${location} ${unit.id} invalid row ${invalidIndex+1}`,async()=>{
    const bad=sizedText(65_537,unit);
    const rows=(function*(){
      for(let index=0;index<80;index++)yield index===invalidIndex?
        location==='name'?{[bad]:index}:{payload:bad}:{safe:index};
    })();
    const {source,state}=observed(rows);
    await assert.rejects(normalizeStream(source,none),limitError(/64 KiB UTF-8 limit/));
    assert.deepEqual(state,{yielded:invalidIndex+1,iterations:1,exhausted:false,closed:true});
  });
}

function* wideRows(grouped){
  for(let index=0;index<512;index++){
    const text=String(index).padStart(4,'0')+'é'.repeat(30_718);
    assert.equal(bytes(text),61_440);
    yield grouped?{g:text,v:1}:{seq:index,payload:text};
  }
}
for(const grouped of [false,true]){
  test(`16MiB ${grouped?'group':'reservoir'} state rejects incrementally`,async t=>{
    const {source,state}=observed(wideRows(grouped));
    const spec=grouped?{x:'g',y:'v',aggregation:'sum',max_points:1000}:{...none,max_points:1000};
    await assert.rejects(normalizeStream(source,spec),limitError(/Retained normalized state exceeds 16 MiB/));
    assert.ok(state.yielded>1 && state.yielded<=274);
    assert.equal(state.exhausted,false);assert.equal(state.iterations,1);assert.equal(state.closed,true);
    t.diagnostic(JSON.stringify({grouped,...state}));
  });
  test(`30MiB input, small ${grouped?'group':'reservoir'} state keeps counts and discloses loss`,async()=>{
    assert.equal(512*61_440,31_457_280);assert.ok(31_457_280>16_777_216);
    const {source,state}=observed(wideRows(grouped));
    const spec=grouped?{x:'g',y:'v',aggregation:'sum',max_points:10}:none;
    const result=await normalizeStream(source,spec);
    assert.deepEqual(state,{yielded:512,iterations:1,exhausted:true,closed:true});
    assert.equal(result.input_count,512);assert.equal(result.records.length,10);
    if(grouped){
      assert.equal(result.strategy,'sum');
      assert.deepEqual(result.records.map(row=>row.v),[...Array(9).fill(1),503]);
      assert.equal(result.records.at(-1).g,'__deepviz_other__');
      assert.match(result.warnings.join(' '),/cardinality/i);
    }else{
      assert.equal(result.strategy,'sample');
      const indices=result.records.map(row=>row.seq);
      assert.deepEqual(indices,[...new Set(indices)].sort((a,b)=>a-b));
      assert.ok(result.records.every(row=>row.payload===String(row.seq).padStart(4,'0')+'é'.repeat(30_718)));
      assert.match(result.warnings.join(' '),/sample/i);
    }
    assert.doesNotMatch(result.warnings.join(' '),/truncat/i);
  });
}
