import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';

const current=await import(pathToFileURL(process.env.R13_TS_MODULE).href);
const baseline=await import(pathToFileURL(process.env.R13_BASE_TS_MODULE).href);
const spec={kind:'bar',x:'g',y:'v',aggregation:'sum'};
const cases=JSON.parse(readFileSync(new URL('./exact-cases.json',import.meta.url),'utf8'));

for(const item of cases)test(`exact independent oracle ${item.name}`,async()=>{
  async function* source(){for(const v of item.values)yield {g:'a',v};}
  const result=await current.normalizeStream(source(),spec);
  assert.deepEqual(result.records,[{g:'a',v:item.expected}]);
  assert.equal(result.input_count,item.values.length);assert.deepEqual(result.warnings,[]);
});

test('one async group consumes the whole stream with one aggregate output',async()=>{
  let consumed=0;
  async function* source(){
    for(let index=0;index<8192;index++){consumed++;yield {g:'a',v:1e308};}
    for(let index=0;index<8192;index++){consumed++;yield {g:'a',v:-1e308};}
    consumed++;yield {g:'a',v:17};
  }
  const result=await current.normalizeStream(source(),spec);
  assert.equal(consumed,16385);assert.equal(result.input_count,consumed);
  assert.deepEqual(result.records,[{g:'a',v:17}]);assert.deepEqual(result.warnings,[]);
});

test('mean and deterministic sampling match untouched base output exactly',async()=>{
  const rows=[1e308,1e308,-1e308].map(v=>({g:'a',v}));
  assert.deepEqual(current.normalize(rows,{...spec,aggregation:'mean'}),baseline.normalize(rows,{...spec,aggregation:'mean'}));
  const samples=Array.from({length:1001},(_,v)=>({g:`group${v%7}`,v}));
  const sample={...spec,aggregation:'sample',max_points:17};
  assert.deepEqual(await current.normalizeStream(samples,sample),await baseline.normalizeStream(samples,sample));
});
for(const sign of [-1,1])test(`true ${sign} overflow remains warned JSON-safe null`,()=>{
  const result=current.normalize([{g:'a',v:sign*1e308},{g:'a',v:sign*1e308}],spec);
  assert.deepEqual(result.records,[{g:'a',v:null}]);
  assert.ok(result.warnings.some(warning=>warning.includes('finite')));
  assert.doesNotThrow(()=>JSON.stringify(result));
});
