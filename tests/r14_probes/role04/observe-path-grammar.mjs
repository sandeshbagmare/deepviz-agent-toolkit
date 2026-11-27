import {readFileSync} from 'node:fs';
import {normalize,ValidationError} from '../../../packages/deepviz/dist/index.js';
const corpus=JSON.parse(readFileSync(new URL('./collision-cases.json',import.meta.url),'utf8'));
const observations=corpus.observations.map(item=>{
  let outcome;
  try{outcome=normalize(item.data,{kind:'table',aggregation:'none',data_path:item.path});}
  catch(error){if(!(error instanceof ValidationError))throw error;outcome={error_type:error.name,message:error.message};}
  return {id:item.id,classification:item.classification,path:item.path,outcome};
});
console.log(JSON.stringify({language:'typescript',normative:false,observations},null,2));
