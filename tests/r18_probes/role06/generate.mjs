import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir,readFile,readdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {cases,sourceSha} from './fixtures.mjs';

const [sourceArgument,outputArgument] = process.argv.slice(2);
assert(sourceArgument && outputArgument,'Usage: node generate.mjs <clean-exact-source> <NEW-output>');
const source = path.resolve(sourceArgument), output = path.resolve(outputArgument);
const selected=process.argv[4]?cases.filter(fixture=>fixture.profile===process.argv[4]):cases;
assert(selected.length>0,'No selected literal fixtures');
await mkdir(output,{recursive:false});
const git = (...args)=>execFileSync('git',['-C',source,...args]);
assert.equal(git('rev-parse','HEAD').toString().trim(),sourceSha);
assert.equal(git('status','--porcelain').toString(),'','Frozen source must be clean');
const sha256 = bytes=>createHash('sha256').update(bytes).digest('hex');
const sourceFiles = git('ls-tree','-r','--name-only',sourceSha,'packages/deepviz/src').toString().trim().split('\n');
sourceFiles.push('packages/deepviz/package.json','packages/deepviz/tsconfig.json','package.json','package-lock.json');
const sourceProof=[];
for(const file of sourceFiles){
  const blob=git('show',`${sourceSha}:${file}`), working=await readFile(path.join(source,file));
  assert.equal(working.toString('utf8').replace(/\r\n/g,'\n'),blob.toString('utf8'),`Dirty/non-Git bytes: ${file}`);
  sourceProof.push({file,git_blob:git('rev-parse',`${sourceSha}:${file}`).toString().trim(),
    git_sha256:sha256(blob),working_sha256:sha256(working),working_CRLF:(working.toString().match(/\r\n/g)||[]).length,
    git_equals_working_after_only_CRLF_to_LF:true});
}
const dist=path.join(source,'packages/deepviz/dist'),buildProof=[];
for(const file of (await readdir(dist)).sort()){
  const body=await readFile(path.join(dist,file));buildProof.push({file,bytes:body.length,sha256:sha256(body)});
}
const publicUrl=pathToFileURL(path.join(dist,'index.js')).href;
const {render,ValidationError}=await import(publicUrl);
const manifest={source_sha:sourceSha,source_directory:source,public_module:publicUrl,node:process.version,
  sourceProof,buildProof,cases:[],unsupported:[]};
for(const fixture of selected){
  const spec={kind:fixture.kind,x:'x',y:'y',aggregation:'none',width:fixture.width,height:fixture.height,
    title:`R18 ${fixture.id}`,...fixture.kind==='bubble'?{size:'size'}:{}};
  try{
    const artifact=render(fixture.rows,spec,'svg');
    assert.equal(artifact.renderer_spec.chart_spec.kind,fixture.kind,'Unexpected public fallback');
    assert.deepEqual(artifact.renderer_spec.normalized.records,fixture.rows);
    assert.equal(artifact.input_count,fixture.rows.length);assert.equal(artifact.output_count,fixture.rows.length);
    assert.equal(artifact.strategy,'none');assert.deepEqual(artifact.warnings,[]);
    const native=artifact.renderer_spec.spec.svg;
    assert.equal(typeof native,'string');
    const end=native.indexOf('</svg>');assert(end>0);
    // Public spec.svg is an SVG+optional HTML legend fragment. Standalone file is its first real SVG only.
    const svg=native.slice(0,end+6);
    await writeFile(path.join(output,`${fixture.id}.svg`),svg);
    await writeFile(path.join(output,`${fixture.id}.html`),artifact.html);
    manifest.cases.push({...fixture,svg:`${fixture.id}.svg`,html:`${fixture.id}.html`,spec,
      public_metadata:{input_count:artifact.input_count,output_count:artifact.output_count,
        strategy:artifact.strategy,warnings:artifact.warnings},svg_sha256:sha256(svg),html_sha256:sha256(artifact.html)});
  }catch(error){
    if(error instanceof ValidationError && error.message.startsWith('Unsupported kind ')){
      manifest.unsupported.push({id:fixture.id,message:error.message});
    }else throw error;
  }
}
assert.equal(manifest.cases.length+manifest.unsupported.length,selected.length);
await writeFile(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2));
console.log(JSON.stringify({source_sha:sourceSha,source_files:sourceProof.length,dist_files:buildProof.length,
  cases:manifest.cases.length,unsupported:manifest.unsupported,output},null,2));
