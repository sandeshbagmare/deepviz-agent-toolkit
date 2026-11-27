import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
import {pathToFileURL} from 'node:url';

const source=process.env.R16_02_SOURCE, build=process.env.R16_02_TS_BUILD;
assert.ok(source && build,'An explicit pinned source and fresh independently built TS directory are required');
const module=await import(pathToFileURL(path.join(build,'normalize.js')).href);
const {normalize,normalizeStream}=module;
const spec={kind:'table',x:'g',y:'v',aggregation:'sum',max_points:1000};
const label=(index,width)=>String(index).padStart(4,'0')+'x'.repeat(width-4);
const save=async(name,value)=>{if(process.env.R16_02_RESULTS)await writeFile(path.join(process.env.R16_02_RESULTS,name+'.json'),JSON.stringify(value,null,2)+'\n',{flag:'wx'});};

for(const adapter of ['sync','stream'])test(`incremental promotion admission near 16MiB: ${adapter}`,async()=>{
  let consumed=0;
  function* rows(tail){for(const value of [1e308,tail])for(let i=0;i<255;i++){consumed++;yield {g:label(i,32640),v:value};}}
  const run=async tail=>adapter==='sync'?normalize(Array.from(rows(tail)),spec):normalizeStream(rows(tail),spec);
  let ordinary=await run(0);
  assert.equal(ordinary.input_count,510);assert.equal(consumed,510);
  assert.equal(ordinary.records.length,255);assert.deepEqual(ordinary.warnings,[]);
  ordinary=null;consumed=0;
  await assert.rejects(run(1e308),/Retained normalized state exceeds 16 MiB/);
  if(adapter === "stream")assert.ok(consumed>255 && consumed<510,`Unexpected consumed count ${consumed}`); else assert.equal(consumed,510);
  await save('typescript-promotion-admission-'+adapter,{groups:255,key_ascii_bytes:32640,ordinary_rows:510,overflow_consumed_rows:consumed,
    method:'Finite public input/early rejection only. No heap/RSS bound inferred from byte accounting.'});
  const fresh=normalize([{g:'fresh',v:1}],spec);
  assert.equal(fresh.input_count,1);assert.equal(fresh.records.length,1);assert.deepEqual(fresh.warnings,[]);
});

test('one other bucket does not promote once per unknown category or leak exact state',async()=>{
  async function* rows(){for(let i=0;i<1000;i++)for(const v of [1e308,1e308,-1e308,-1e308])yield {g:label(i,4096),v};}
  const result=await normalizeStream(rows(),{...spec,max_points:10});
  assert.equal(result.input_count,4000);assert.equal(result.records.length,10);
  assert.ok(result.records.at(-1).g.startsWith('__deepviz_other__'));
  assert.equal(result.warnings.length,1);assert.match(result.warnings[0],/other bucket/);
  for(const record of result.records){assert.deepEqual(Object.keys(record).sort(),['g','v']);assert.ok(Number.isFinite(record.v));}
  const encoded=JSON.stringify(result);assert.doesNotMatch(encoded,/"exact"|"correction"|"exponent"|NaN|Infinity/);
  const fresh=normalize([{g:'fresh',v:0}],spec);assert.deepEqual(fresh.warnings,[]);assert.equal(fresh.records.length,1);
  await save('typescript-other-lifetime',{input_groups:1000,rows:4000,output_records:10,output_json_bytes:Buffer.byteLength(encoded),warnings:result.warnings});
});

test('non-JSON BigInt after established promotion rejects instead of entering internal integer state',async()=>{
  let consumed=0;
  async function* rows(){for(let i=0;i<32;i++){consumed++;yield {g:'one',v:i<2?1e308:0};}consumed++;yield {g:'one',v:1n};consumed++;yield {g:'one',v:0};}
  await assert.rejects(normalizeStream(rows(),spec),/Non-JSON value/);
  assert.equal(consumed,33);
  await save('typescript-bigint-input-admission',{consumed_rows:consumed,scope:'Public non-JSON input guard, no internal reducer mutation'});
});

test('compiled normalizer has its own immutable source map, not shared producer build',async()=>{
  const map=JSON.parse(await readFile(path.join(build,'normalize.js.map'),'utf8'));
  const expected=path.resolve(source,'packages/deepviz/src/normalize.ts');
  const mapped=path.resolve(build,map.sources[0]);
  assert.equal(mapped,expected);
  const digest=createHash('sha256').update(await readFile(path.join(build,'normalize.js'))).digest('hex');
  await save('typescript-build-consumer',{source_map_target:path.relative(source,mapped).replaceAll('\\','/'),compiled_normalize_sha256:digest,node:process.version});
});
