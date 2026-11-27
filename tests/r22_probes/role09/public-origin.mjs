import assert from 'node:assert/strict';
import {realpathSync} from 'node:fs';
import {createRequire} from 'node:module';
import {join} from 'node:path';

// The fixed host command sets --conditions=import for the import-only export.
const requireFromCandidate = createRequire(join(process.argv[2], 'package.json'));
assert.equal(realpathSync(requireFromCandidate.resolve('@deepviz/agent-toolkit')), realpathSync(join(process.argv[2], 'dist/index.js')));
console.log('Requested candidate public package entry verified');
