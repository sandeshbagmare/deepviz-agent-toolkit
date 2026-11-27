import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdirSync, readFileSync, realpathSync, writeFileSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import test from 'node:test';

const expected = '7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6';
assert.ok(process.env.R20_CANDIDATE_DIR, 'Supply an exact clean isolated 7bc source with its own fresh build');
assert.ok(process.env.R20_EVIDENCE_DIR, 'Supply a NEW unique evidence directory');
const root = realpathSync(resolve(process.env.R20_CANDIDATE_DIR));
const output = resolve(process.env.R20_EVIDENCE_DIR);
const tooling = process.env.R20_TOOLING_NODE_MODULES && realpathSync(process.env.R20_TOOLING_NODE_MODULES);
const git = args => {
  const child = spawnSync('git', ['-C', root, ...args], {encoding: 'utf8', timeout: 15_000});
  assert.equal(child.status, 0, child.stderr || child.stdout || String(child.error));
  return child.stdout.trim();
};
assert.equal(git(['rev-parse', 'HEAD']), expected);
assert.equal(git(['status', '--porcelain', '--untracked-files=no']), '', 'Source is not tracked-clean');
const hashes = {};
for (const name of ['index', 'models', 'normalize', 'render', 'renderers', 'schema']) {
  for (const [kind, path] of [['source', `src/${name}.ts`], ['built', `dist/${name}.js`]]) {
    hashes[`${kind}/${name}`] = createHash('sha256').update(readFileSync(join(root, 'packages/deepviz', path))).digest('hex');
  }
}
assert.equal(hashes['built/normalize'], '52d718460e6501ca84a3ef8c9a5b9da92eb4c2b71109bd73a3b9351db85501e5', 'Fresh frozen-source normalize build mismatch');
assert.equal(hashes['built/render'], '39bcd415d119e39ef3107dee4b455778541776f3901c4ae5facbb1447fcc5388');
mkdirSync(output, {recursive: false});
writeFileSync(join(output, 'source-build.json'), JSON.stringify({source_sha: expected, candidate: root, tracked_clean: true, node: process.version, hashes, method: 'Fresh own absolute-installed-tsc build; exact clean detached source; self-import realpath asserted inside each task child'}, null, 2));

const worker = fileURLToPath(new URL('./task-success-worker.mjs', import.meta.url));
const loader = `
import assert from 'node:assert/strict';
import {realpathSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
assert.equal(realpathSync(fileURLToPath(import.meta.resolve('@deepviz/agent-toolkit'))),realpathSync(process.argv[3]));
const api=await import('@deepviz/agent-toolkit');
const {runTask}=await import(pathToFileURL(process.argv[1]).href);
await runTask(api,JSON.parse(process.argv[2]));
`;

for (const [task, title] of [
  ['bounded-sum', 'literal ordinary SUM reduces groups before serialization, explains loss, repeats deterministically'],
  ['dashboard', 'two child datasets, mappings, titles and themes remain distinct with honest counts'],
  ['discovery-errors', 'public discovery/schema and ordinary field errors support actionable agent calls'],
  ['browser', 'actual public SVG tool HTML has literal marks/order/ratios and zero browser errors'],
]) {
  test(`R20-09 ${title}`, t => {
    const config = {task, output, tooling, python: process.env.R20_VALIDATOR_PYTHON};
    const child = spawnSync(process.execPath, ['--input-type=module', '--eval', loader, worker, JSON.stringify(config), join(root, 'packages/deepviz/dist/index.js')], {cwd: join(root, 'packages/deepviz'), encoding: 'utf8', timeout: 45_000});
    assert.equal(child.signal, null, `task child signal ${child.signal}`);
    assert.ok(child.stdout, child.stderr || String(child.error));
    const result = JSON.parse(child.stdout);
    t.diagnostic(JSON.stringify(result));
    assert.equal(child.status, 0, result.failure || child.stderr);
    if (result.skipped) return t.skip(result.reason);
    assert.equal(result.passed, true);
  });
}
