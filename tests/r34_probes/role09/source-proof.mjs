import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const source = resolve(process.env.R34_SOURCE);
const evidence = resolve(process.env.R34_EVIDENCE);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const receipt = JSON.parse(readFileSync(join(evidence, 'source-build.json'), 'utf8'));
assert.equal(receipt.source_sha, 'c3ee1edbfc65406cef7fd809f5a6887471d576a5');
assert.equal(receipt.source_root, source);
assert.equal(receipt.build.exit, 0);
assert.equal(execFileSync('git', ['rev-parse', 'HEAD'], {cwd: source, encoding: 'utf8'}).trim(), receipt.source_sha);
assert.equal(execFileSync('git', ['status', '--porcelain', '--untracked-files=no'], {cwd: source, encoding: 'utf8'}).trim(), '');
for (const [name, expected] of Object.entries(receipt.files)) assert.equal(hash(readFileSync(join(source, name))), expected.raw_sha256, name);
for (const [name, expected] of Object.entries(receipt.dist)) assert.equal(hash(readFileSync(join(source, name))), expected, name);
const pkg = JSON.parse(readFileSync(join(source, 'packages/deepviz/package.json'), 'utf8'));
assert.equal(pkg.exports['.'].import, './dist/index.js');
const publicURL = pathToFileURL(join(source, 'packages/deepviz/dist/index.js')).href;
const api = await import(publicURL);
assert.equal(typeof api.render, 'function');
writeFileSync(join(evidence, `process-origin-${process.pid}.json`), JSON.stringify({pid: process.pid,
  source_sha: receipt.source_sha, public_entry: publicURL, argv: process.argv, node: process.version,
  source_and_all_fresh_dist_hashes_verified_before_public_import: true}, null, 2), {flag: 'wx'});
export {api, evidence, hash, source};
