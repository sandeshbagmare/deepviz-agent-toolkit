import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

export const artifacts = path.resolve('artifacts/r39-15');
const packageRoot = path.join(artifacts, 'input/packages/deepviz');
const proof = JSON.parse(fs.readFileSync(path.join(artifacts, 'source-compiler-prebuild.json'), 'utf8'));
const build = JSON.parse(fs.readFileSync(path.join(artifacts, 'build-proof-before.json'), 'utf8'));
const sha = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
assert.equal(proof.source_commit, 'c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19');
assert.equal(build.source_commit, proof.source_commit);
assert.ok(!process.env.NODE_OPTIONS, 'Do not run this consumer with an external Node loader/hook');
for (const [relative, hash] of Object.entries(proof.raw_Git_equal_inputs_sha256)) {
  assert.equal(sha(path.join(artifacts, 'input', relative)), hash);
}
for (const [relative, hash] of Object.entries(build.dist_sha256)) assert.equal(sha(path.join(packageRoot, 'dist', relative)), hash);
const consumer = process.env.R39_CONSUMER;
assert.ok(['producer', 'independent'].includes(consumer));
const publicURL = pathToFileURL(fs.realpathSync(path.join(packageRoot, 'dist/index.js')));
const directURL = pathToFileURL(fs.realpathSync(path.join(packageRoot, 'dist/normalize.js')));
const modelsURL = pathToFileURL(fs.realpathSync(path.join(packageRoot, 'dist/models.js')));
export const api = await import(publicURL.href);
const direct = await import(directURL.href);
const models = await import(modelsURL.href);
assert.equal(api.normalize, direct.normalize);
assert.equal(api.normalizeStream, direct.normalizeStream);
assert.equal(api.ValidationError, models.ValidationError);
for (const [relative, hash] of Object.entries(build.dist_sha256)) assert.equal(sha(path.join(packageRoot, 'dist', relative)), hash);
const receipt = {source_commit: proof.source_commit, consumer, pid: process.pid, Node: process.version,
  own_public_index_URL: publicURL.href, own_normalizer_URL: directURL.href,
  source_inputs11_and_dist_raw_hashes_verified_before_import: true,
  public_exports_same_exact_own_normalizer_and_models_objects: true, no_external_NODE_OPTIONS: true,
  source_commit_not546_final_approval: true};
fs.writeFileSync(path.join(artifacts, `import-proof-${consumer}-${process.pid}.json`), JSON.stringify(receipt, null, 2), {flag: 'wx'});
export function bits(number) {
  const buffer = new ArrayBuffer(8); const view = new DataView(buffer);
  view.setFloat64(0, number); return view.getBigUint64(0).toString(16).padStart(16, '0');
}
export function record(value) {
  fs.appendFileSync(path.join(artifacts, 'independent-actual.jsonl'), JSON.stringify(value) + '\n');
}