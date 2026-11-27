import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {chartSpecSchema,chartKinds,validateSpec} from '../dist/index.js';

const canonical=process.argv[2]??fileURLToPath(new URL('../../../schemas/chart-spec.schema.json',import.meta.url));
assert.deepEqual(chartSpecSchema,JSON.parse(await readFile(canonical,'utf8')),'npm schema must exactly match the Python-generated canonical JSON schema');
const properties=chartSpecSchema.$defs.ChartSpec.properties;
assert.deepEqual([...properties.kind.enum],[...chartKinds]);
const defaults=validateSpec({});
assert.deepEqual(Object.keys(properties).sort(),Object.keys(defaults).sort());
for(const [field,property] of Object.entries(properties)) {
  if(Object.hasOwn(property,'default')) assert.deepEqual(defaults[field],property.default,`Runtime/schema default mismatch for ${field}`);
}
console.log('Canonical Python JSON Schema, kinds, fields, and runtime defaults: PASS');
