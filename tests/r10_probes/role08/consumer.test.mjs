import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,readdir,realpath} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import * as api from '@deepviz/agent-toolkit';
import schema from '@deepviz/agent-toolkit/chart-spec.schema.json' with {type:'json'};

const fixture=JSON.parse(await readFile(new URL('./expected.json',import.meta.url),'utf8'));
const entry=fileURLToPath(import.meta.resolve('@deepviz/agent-toolkit'));
const root=path.resolve(path.dirname(entry),'..');
const rows=[{x:'Alpha',y:2},{x:'Beta',y:5}];
const source=()=> (async function*(){yield* rows;})();
const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');

test('the installed entry is local, materialized, and not a workspace fallback',async()=>{
  assert.equal(entry,path.join(fileURLToPath(new URL('./',import.meta.url)),'node_modules','@deepviz','agent-toolkit','dist','index.js'));
  assert.equal((await lstat(root)).isSymbolicLink(),false);
  assert.equal(await realpath(root),root);
  const metadata=JSON.parse(await readFile(path.join(root,'package.json'),'utf8'));
  assert.equal(metadata.name,'@deepviz/agent-toolkit');
  assert.equal(metadata.version,fixture.version);
  assert.deepEqual(metadata.dependencies??{},{});
});

test('documented runtime exports are callable from the packed public entry',()=>{
  for(const name of ['validateSpec','normalize','normalizeStream','buildRendererSpec','render','renderStream','createTools','ValidationError']) assert.equal(typeof api[name],'function',name);
  assert.equal(api.chartKinds.length,18);
  assert.deepEqual(api.defaultAssets,fixture.assets);
});

test('the public JSON subpath and schema export equal the canonical source schema',()=>{
  assert.deepEqual(schema,api.chartSpecSchema);
  assert.deepEqual(schema,fixture.schema);
  assert.equal(api.validateSpec({}).version,1);
  assert.throws(()=>api.validateSpec({kind:'not-a-chart'}),api.ValidationError);
});

test('records, columns, delimited text and streaming preserve exact consumer values',async()=>{
  const spec={x:'x',y:'y'};
  for(const data of [rows,{x:['Alpha','Beta'],y:[2,5]},'x,y\nAlpha,2\nBeta,5\n']) {
    const normalized=api.normalize(data,spec);
    assert.equal(normalized.input_count,2);
    assert.deepEqual(normalized.records,rows);
  }
  assert.deepEqual((await api.normalizeStream(source(),spec)).records,rows);
});

test('packed streaming render emits two exact native SVG marks',async()=>{
  const artifact=await api.renderStream(source(),{x:'x',y:'y'},'svg');
  assert.equal(artifact.input_count,2);
  assert.equal(artifact.output_count,2);
  assert.deepEqual(artifact.renderer_spec.normalized.records,rows);
  assert.match(artifact.html,/<svg\b/);
  assert.match(artifact.renderer_spec.spec.svg,/Alpha/);
  assert.match(artifact.renderer_spec.spec.svg,/Beta/);
});

test('all five packed agent helper APIs execute without workspace runtime dependencies',async()=>{
  const tools=api.createTools();
  assert.deepEqual(tools.map(tool=>tool.name),['render_vega','render_echarts','render_antv','render_plotly','render_svg']);
  for(const tool of tools) {
    const artifact=await tool.invoke({data:rows,spec:{x:'x',y:'y'}});
    assert.equal(artifact.input_count,2);
    assert.equal(artifact.output_count,2);
    assert.deepEqual(artifact.renderer_spec.normalized.records,rows);
    assert.equal(artifact.mime_type,'text/html');
  }
});

test('unexported internal paths are not mistaken for a supported package entry',async()=>{
  await assert.rejects(import('@deepviz/agent-toolkit/dist/index.js'),error=>error.code==='ERR_PACKAGE_PATH_NOT_EXPORTED');
});

async function packedFiles(directory,prefix='') {
  const result=[];
  for(const entry of await readdir(directory,{withFileTypes:true})) {
    const name=path.posix.join(prefix,entry.name);
    assert.equal(entry.isSymbolicLink(),false,`Unexpected packed symlink: ${name}`);
    if(entry.isDirectory()) result.push(...await packedFiles(path.join(directory,entry.name),name));
    else result.push(name);
  }
  return result;
}
const files=await packedFiles(root);
for(const name of ['system','request']) {
  test(`canonical versioned ${name} prompt is present in the installed tarball`,async()=>{
    const matches=files.filter(file=>file.endsWith(`prompts/v1/${name}.md`));
    assert.ok(matches.length>0,`Missing canonical prompts/v1/${name}.md from actual installed tarball`);
    for(const file of matches) assert.equal(sha256(await readFile(path.join(root,file))),fixture.prompts[name],`Stale or modified canonical prompt: ${file}`);
  });
}
