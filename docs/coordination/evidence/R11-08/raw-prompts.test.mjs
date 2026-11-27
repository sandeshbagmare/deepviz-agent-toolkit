import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import * as api from '@deepviz/agent-toolkit';
const fixture=JSON.parse(await readFile(new URL('./expected.json',import.meta.url),'utf8'));
const root=fileURLToPath(new URL('./node_modules/@deepviz/agent-toolkit/',import.meta.url));
for(const name of ['README','system','request'])test('Raw v1 '+name+' export reads exact canonical bytes without executable imports',async()=>{
  const url=import.meta.resolve('@deepviz/agent-toolkit/prompts/v1/'+name+'.md');
  assert.equal(fileURLToPath(url),path.join(root,'dist','prompts','v1',name+'.md'));
  const bytes=await readFile(new URL(url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'),fixture.prompts[name]);
  await assert.rejects(import(url),error=>error.code==='ERR_UNKNOWN_FILE_EXTENSION');
});
test('All thirteen runtime exports remain unchanged with no invented prompt reader',()=>assert.deepEqual(Object.keys(api).sort(),['ValidationError','buildRendererSpec','chartKinds','chartSpecSchema','createTools','defaultAssets','isObject','normalize','normalizeStream','render','renderStream','safeKey','validateSpec'].sort()));
