/** Bounded read-only carrier diagnostic; exit0 saves observations, not test approval. */
import {createHash} from 'node:crypto';
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {normalize, normalizeStream} from '../../../packages/deepviz/dist/index.js';
import {clone, lateFault, page, raw} from './graphql-fixtures.mjs';

const expectedSource = '5340bc69b7203ad7a9166543062482d819f9b705';
const root = fileURLToPath(new URL('../../../',import.meta.url));
const destination = resolve(process.argv[2]??'artifacts/r15-03/carrier-diagnostic.json');
const observations=[];
for(const variant of ['null-data','no-data','empty-data'])for(const carrier of ['direct','list','json','async','explicit']) {
  const failed = variant==='null-data'?{data:null,errors:[{message:'late page unavailable'}]}:
    variant==='empty-data'?{data:{},errors:[{message:'late page unavailable'}]}:
      {errors:[{message:'late page unavailable'}]};
  const {data:pages}=lateFault('error-only-response',false);
  pages[2]=clone(failed);
  try {
    const result=carrier==='direct'?normalize(failed,raw):
      carrier==='json'?normalize(JSON.stringify(pages),{...raw,format:'json'}):
        carrier==='async'?await normalizeStream((async function*(){yield* pages;})(),raw):
          normalize(pages,{...raw,...(carrier==='explicit'?{data_path:'data.feed'}:{})});
    observations.push({variant,carrier,outcome:'returned',input_count:result.input_count,
      output_count:result.records.length,strategy:result.strategy,last_record:result.records.at(-1),warnings:result.warnings});
  } catch(error) {
    observations.push({variant,carrier,outcome:'rejected',error_type:error.constructor.name,message:error.message});
  }
}
// Do not prescribe a policy from the current behavior: show N12 pages-wrapper ambiguity only.
const ordinaryPages={pages:[page([{id:'one'}],'nodes'),page([],'nodes'),page([{id:'two'}],'nodes')]};
for(const selected of [false,true]) {
  try {
    const result=normalize(ordinaryPages,{...raw,...(selected?{data_path:'pages.data.feed.nodes'}:{})});
    observations.push({variant:'N12-known-pages-wrapper-policy',carrier:selected?'explicit':'auto',outcome:'returned',...result});
  } catch(error) {
    observations.push({variant:'N12-known-pages-wrapper-policy',carrier:selected?'explicit':'auto',outcome:'rejected',message:error.message});
  }
}
const paths=['packages/deepviz/src/normalize.ts','packages/deepviz/dist/normalize.js','packages/deepviz/dist/index.js'];
// Independent smallest two-page literal, no shared fixture builder/prefix required.
const minimalLiteral=[{data:{feed:{nodes:[{id:'kept',measure:2}]}}},
  {data:null,errors:[{message:'late page unavailable'}]}];
const minimalResult=normalize(minimalLiteral,raw);
observations.push({variant:'minimal-two-page-literal-no-builders',carrier:'list',
  outcome:'returned',source:minimalLiteral,...minimalResult});
const identity=Object.fromEntries(paths.map(path=>[path,{path:resolve(root,path),sha256:createHash('sha256').update(readFileSync(resolve(root,path))).digest('hex')}]));
const result={recorded_at:new Date().toISOString(),node:process.version,expected_source:expectedSource,
  own_public_import:import.meta.resolve('../../../packages/deepviz/dist/index.js'),identity,observations,
  claim:'observed public behavior only; diagnostic exit0 is not acceptance or final-source verification'};
mkdirSync(dirname(destination),{recursive:true});
writeFileSync(destination,JSON.stringify(result,null,2)+'\n');
console.log(`OBSERVATIONS=${observations.length}; DIAGNOSTIC=${destination}; ACCEPTANCE_NOT_CLAIMED=True`);
