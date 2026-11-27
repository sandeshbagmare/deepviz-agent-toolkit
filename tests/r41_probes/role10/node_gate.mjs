// Source binding/provenance BEFORE any original test consumer; no product patch.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync, realpathSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const binding = JSON.parse(readFileSync(process.env.R41_BINDINGS, 'utf8'));
assert.equal(binding.source_sha, '546c25ea75ee9d8a41b3832aa639664bc9a683b5');
for (const key of ['current', 'base', 'oracles', 'built', 'compiler']) {
  for (const item of binding[key]) {
    assert.equal(createHash('sha256').update(readFileSync(item.path)).digest('hex'), item.sha256, item.path);
  }
}
const modules = [];
for (const [label, root, sha] of [['candidate', binding.candidate, binding.source_sha], ['baseline', binding.baseline, binding.baseline_sha]]) {
  const file = path.join(root, 'packages/deepviz/dist/index.js');
  assert.equal(realpathSync(file), file);
  const url = pathToFileURL(file).href;
  const actual = await import(url);
  assert.equal(typeof actual.normalize, 'function');
  assert.equal(typeof actual.normalizeStream, 'function');
  modules.push({label, product_sha: sha, module_url: url, resolved_url: import.meta.resolve(url),
    index_sha256: createHash('sha256').update(readFileSync(file)).digest('hex'), exports: Object.keys(actual)});
}
writeFileSync(path.join(process.env.R41_PROOF_DIR, `${process.pid}.json`), JSON.stringify({pid: process.pid,
  all_input_oracle_emit_tool_hashes_verified_BEFORE_consumer: true, modules, node: process.version}, null, 2));
