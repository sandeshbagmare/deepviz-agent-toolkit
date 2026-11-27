import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync, realpathSync} from 'node:fs';
import {resolve, join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import test from 'node:test';

const sourceSha = process.env.R15_EXPECT_SOURCE_SHA ?? '5340bc69b7203ad7a9166543062482d819f9b705';
const root = realpathSync(resolve(process.env.R15_CANDIDATE_DIR ?? process.cwd()));
const worker = fileURLToPath(new URL('./reserved-keys-worker.mjs', import.meta.url));
const packageDir = join(root, 'packages/deepviz');
const hash = path => createHash('sha256').update(readFileSync(join(root, path))).digest('hex');
const git = args => {
  const result = spawnSync('git', ['-C', root, ...args], {encoding: 'utf8', timeout: 15_000});
  assert.equal(result.status, 0, result.stderr || result.stdout || String(result.error));
  return result.stdout.trim();
};

test('R15-09 provenance: public TS sources/configs equal the frozen target', t => {
  assert.match(sourceSha, /^[0-9a-f]{40}$/);
  git(['diff', '--exit-code', sourceSha, '--', 'packages/deepviz/src', 'packages/deepviz/package.json', 'packages/deepviz/tsconfig.json', 'package.json', 'package-lock.json']);
  const loaded = Object.fromEntries(['index', 'models', 'normalize', 'render', 'renderers'].map(name => [name, hash(`packages/deepviz/dist/${name}.js`)]));
  if (sourceSha === '5340bc69b7203ad7a9166543062482d819f9b705') {
    assert.equal(loaded.normalize, 'adb0493123fd478567212e76e2c6e52c828aeaa9eb5425c219b5b1a576689612', 'existing known-source normalize build changed');
    assert.equal(loaded.render, '39bcd415d119e39ef3107dee4b455778541776f3901c4ae5facbb1447fcc5388', 'existing known-source render build changed');
  }
  t.diagnostic(JSON.stringify({candidate: root, own_head: git(['rev-parse', 'HEAD']), source_sha: sourceSha, source_tree: git(['rev-parse', `${sourceSha}:packages/deepviz/src`]), built_sha256: loaded, build_repeated: false}));
});

const loader = `
import {realpathSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
assert.equal(realpathSync(fileURLToPath(import.meta.resolve('@deepviz/agent-toolkit'))),realpathSync(process.argv[3]));
const api=await import('@deepviz/agent-toolkit');
const {run}=await import(pathToFileURL(process.argv[1]).href);
await run(api,JSON.parse(process.argv[2]));
`;

function check(candidate, t) {
  const child = spawnSync(process.execPath, ['--input-type=module', '--eval', loader, worker, JSON.stringify(candidate), join(packageDir, 'dist/index.js')], {cwd: packageDir, encoding: 'utf8', timeout: 15_000});
  assert.equal(child.signal, null, `child signal: ${child.signal}`);
  assert.ok(child.stdout, child.stderr || String(child.error));
  const result = JSON.parse(child.stdout);
  t.diagnostic(JSON.stringify(result));
  assert.notEqual(result.pid, process.pid, 'fixture did not run in a fresh child');
  assert.equal(child.status, 0, result.assertion_failure || child.stderr);
  assert.equal(result.assertions_passed, true);
  assert.equal(result.input_and_global_prototype_unchanged, true);
}

for (const route of ['normalize', 'stream', 'tool']) {
  for (const key of ['__proto__', 'constructor', 'prototype', 'toString']) {
    for (const scenario of ['own-record', 'own-null-prototype', 'mapped-own-field', 'own-data-path', 'inherited-data-path', 'missing-mapped-field']) {
      test(`R15-09 ${route} / ${key} / ${scenario}`, t => check({route, key, scenario}, t));
    }
  }
  for (const scenario of ['ordinary', 'ordinary-null-prototype', 'omitted-spec']) {
    test(`R15-09 ${route} / positive / ${scenario}`, t => check({route, key: 'ordinary', scenario}, t));
  }
}
for (const route of ['normalize', 'stream']) {
  test(`R15-09 ${route} / explicit null ChartSpec rejects (not the known tool-default defect)`, t => check({route, key: 'ordinary', scenario: 'null-spec'}, t));
}
