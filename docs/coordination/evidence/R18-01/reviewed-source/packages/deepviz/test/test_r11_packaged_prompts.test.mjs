import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, mkdtemp, rmdir} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const canonical=new URL('../../../prompts/v1/',import.meta.url);
const packaged=new URL('../dist/prompts/v1/',import.meta.url);
const filenames=['README.md','system.md','request.md'];

for(const filename of filenames) {
  test(`R11 packaged v1/${filename} preserves canonical bytes`,async()=>{
    const bytes=await readFile(new URL(filename,canonical));
    assert.deepEqual(await readFile(new URL(filename,packaged)),bytes);
  });
}

test('R11 raw versioned exports resolve to the three generated Markdown resources',async()=>{
  const metadata=JSON.parse(await readFile(new URL('../package.json',import.meta.url),'utf8'));
  for(const filename of filenames) {
    assert.equal(metadata.exports[`./prompts/v1/${filename}`],`./dist/prompts/v1/${filename}`);
  }
  assert.deepEqual(metadata.exports['.'],{types:'./dist/index.d.ts',import:'./dist/index.js'});
  assert.equal(metadata.exports['./chart-spec.schema.json'],'./dist/chart-spec.schema.json');
});

test('R11 prompt copy is repeatable outside the checkout cwd and preserves emitted code',async()=>{
  const cwd=await mkdtemp(path.join(tmpdir(),'deepviz-r11-copy-'));
  const entry=new URL('../dist/index.js',import.meta.url);
  const before=await readFile(entry);
  try {
    for(let repeat=0;repeat<2;repeat++) {
      const result=spawnSync(process.execPath,[fileURLToPath(new URL('../scripts/copy-prompts.mjs',import.meta.url))],{cwd,encoding:'utf8',timeout:10000});
      assert.equal(result.status,0,result.stderr);
      for(const filename of filenames) assert.deepEqual(await readFile(new URL(filename,packaged)),await readFile(new URL(filename,canonical)));
      assert.deepEqual(await readFile(entry),before);
    }
  } finally {await rmdir(cwd);}
});
