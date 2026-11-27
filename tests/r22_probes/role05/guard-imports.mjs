// Verification-only: reject mixed public/connected module origins before loading.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {appendFileSync,readFileSync,realpathSync} from 'node:fs';
import {registerHooks} from 'node:module';
import {resolve,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=realpathSync(process.env.R22_SOURCE);
const dist=realpathSync(resolve(root,'packages/deepviz/dist'));
const expected=realpathSync(resolve(dist,'index.js'));
const manifest=JSON.parse(readFileSync(process.env.R22_DIST_MANIFEST,'utf8'));
const log=process.env.R22_IMPORT_LOG;
function record(value){appendFileSync(log,JSON.stringify({pid:process.pid,...value})+'\n');}
function verify(url){
  const path=fileURLToPath(url),actual=realpathSync(path);
  assert.equal(actual,path,'R22 symlink/reparse module origin');
  assert.ok(actual.startsWith(dist+sep),'R22 connected module escaped own fresh dist');
  const relative=actual.slice(dist.length+1).split(sep).join('/');
  assert.equal(createHash('sha256').update(readFileSync(path)).digest('hex'),manifest.files[relative],
    'R22 fresh build module bytes differ from manifest');
  record({kind:'verified-own-dist',relative,url});
}
registerHooks({
  resolve(specifier,context,nextResolve){
    const result=nextResolve(specifier,context);
    if(specifier==='@deepviz/agent-toolkit'){
      if(result.url!==pathToFileURL(expected).href){
        record({kind:'wrong-public-origin-rejected',url:result.url});
        throw new Error('R22 public package resolved outside own fresh build');
      }
      record({kind:'public-own-dist',url:result.url});
    }
    const ownPrefix=pathToFileURL(dist+sep).href;
    if(context.parentURL?.startsWith(ownPrefix) && result.url.startsWith('file:')){
      assert.ok(result.url.startsWith(ownPrefix),'R22 connected import escaped own dist');
    }
    if(result.url.startsWith(ownPrefix))verify(result.url);
    return result;
  },
  load(url,context,nextLoad){
    if(url.startsWith(pathToFileURL(dist+sep).href))verify(url);
    return nextLoad(url,context);
  },
});
record({kind:'guard-ready',root,entry:expected});
