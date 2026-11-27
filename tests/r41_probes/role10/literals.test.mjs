import assert from 'node:assert/strict';
import test from 'node:test';
import {pathToFileURL} from 'node:url';
const {normalize, normalizeStream} = await import(pathToFileURL(process.env.R13_TS_MODULE).href);
const raw = {kind:'table', aggregation:'none', max_points:10};

for (const encoded of [false,true]) for (const selected of [false,true]) test(`new protocol columns ${encoded} ${selected}`,()=>{
  const columns={records:[0,false,null],items:['z','y','x']}, data=selected?{outer:columns}:columns, original=structuredClone(data);
  const result=normalize(encoded?JSON.stringify(data):data,{...raw,...(selected?{data_path:'outer'}:{})});
  assert.deepEqual(result.records,[{records:0,items:'z'},{records:false,items:'y'},{records:null,items:'x'}]);
  assert.equal(result.input_count,3); assert.equal(result.strategy,'none'); assert.deepEqual(result.warnings,[]); assert.deepEqual(data,original);
});
for (const encoded of [false,true]) test(`new selected record protocol cells ${encoded}`,()=>{
  const data={outer:[{nodes:[0,false],items:[null]},{nodes:[-2],items:[true]}]}, original=structuredClone(data);
  const result=normalize(encoded?JSON.stringify(data):data,{...raw,data_path:'outer'});
  assert.deepEqual(result.records,[{'nodes.0':0,'nodes.1':false,'items.0':null},{'nodes.0':-2,'items.0':true}]);
  assert.equal(result.input_count,2); assert.equal(result.strategy,'none'); assert.deepEqual(result.warnings,[]); assert.deepEqual(data,original);
});
for (const carrier of ['list','json','async']) test(`new business reason/boolean errors ${carrier}`,async()=>{
  const data=Array(2).fill({ref:'audit',errors:[{reason:'local',ok:false}],value:0}), original=structuredClone(data);
  const result=carrier==='async'?await normalizeStream((async function*(){yield* data;})(),raw):normalize(carrier==='json'?JSON.stringify(data):data,raw);
  assert.deepEqual(result.records,Array(2).fill({ref:'audit','errors.0.reason':'local','errors.0.ok':false,value:0}));
  assert.equal(result.input_count,2); assert.equal(result.strategy,'none'); assert.deepEqual(result.warnings,[]); assert.deepEqual(data,original);
});
for (const carrier of ['object','json','async']) test(`new null GraphQL metadata and late warning ${carrier}`,async()=>{
  const pages=[{data:{feed:{nodes:[{id:'r',value:0},null,{id:'r',value:0}],pageInfo:null,totalCount:null}},extensions:null},
    {data:{feed:{nodes:[]}}}, {data:{feed:{edges:[{node:{id:'z',value:-0.5}},{node:null}],pageInfo:null,totalCount:null}},errors:[{message:'partial flag'}]}];
  const original=structuredClone(pages);
  const result=carrier==='async'?await normalizeStream((async function*(){yield* pages;})(),raw):normalize(carrier==='json'?JSON.stringify({pages}):{pages},raw);
  assert.deepEqual(result.records,[{id:'r',value:0},{id:'r',value:0},{id:'z',value:-0.5}]);
  assert.equal(result.input_count,3); assert.equal(result.strategy,'none'); assert.equal(result.warnings.length,2);
  assert.equal(result.warnings.filter(message=>/null/i.test(message)).length,1); assert.equal(result.warnings.filter(message=>/errors/i.test(message)).length,1); assert.deepEqual(pages,original);
});
test('new late error-only/null-metadata async page stops before host tail',async()=>{
  const pages=[{data:{feed:{nodes:Array.from({length:35},(_,id)=>({id}))}}},{data:{feed:{nodes:[]}}},{data:null,errors:[{message:'unavailable'}],extensions:null}];
  const original=structuredClone(pages),pulled=[];
  async function* source(){for(let i=0;i<pages.length;i++){pulled.push(i);yield pages[i];}throw new Error('overread after bad page');}
  await assert.rejects(normalizeStream(source(),raw),error=>/graphql.*errors.*data/i.test(error.message)&&error.message.length<=512);
  assert.deepEqual(pulled,[0,1,2]); assert.deepEqual(pages,original);
});
for(const stream of [false,true])for(const sign of [-1,1])for(const tiny of [false,true])test(`new exact prefix ${stream} ${sign} ${tiny}`,async()=>{
  const values=tiny?[2**52,3*Number.MIN_VALUE,-(2**52),4*Number.MIN_VALUE,-Number.MIN_VALUE]:[2**54,0.375,-(2**54),2**54,-(2**54)];
  const rows=values.map(value=>({g:'r',v:sign*value})),original=structuredClone(rows),spec={x:'g',y:'v',aggregation:'sum'};
  const result=stream?await normalizeStream((async function*(){yield* rows;})(),spec):normalize(rows,spec);
  assert.deepEqual(result.records,[{g:'r',v:sign*(tiny?6*Number.MIN_VALUE:0.375)}]); assert.equal(result.input_count,5); assert.equal(result.strategy,'sum'); assert.deepEqual(result.warnings,[]); assert.deepEqual(rows,original);
});
for(const aggregation of ['sum','count'])test(`new raw count versus numeric contribution ${aggregation}`,()=>{
  const rows=[0,false,null,'0',-2].map(v=>({g:'r',v})),original=structuredClone(rows),result=normalize(rows,{x:'g',y:'v',aggregation});
  assert.deepEqual(result.records,[{g:'r',v:aggregation==='sum'?-2:5}]); assert.equal(result.input_count,5); assert.equal(result.strategy,aggregation);
  assert.equal(result.warnings.length,aggregation==='sum'?1:0); if(aggregation==='sum')assert.match(result.warnings[0],/non-numeric/i); assert.deepEqual(rows,original);
});
