// Trusted local probe, never JavaScript supplied through ChartSpec.
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

const { normalize } = await import(pathToFileURL(process.argv[2]));
const text = 'x'.repeat(10_001);
const kept = normalize([{ text }], { kind: 'table' });
assert.equal(kept.records[0].text, text);
const observations = { retained_length: kept.records[0].text.length, warnings: kept.warnings };
for (const [name, data, spec] of [
  ['oversize_cell', [{ text: 'x'.repeat(65_537) }], { kind: 'table' }],
  ['duplicate_json', '{"x":1,"x":2}', { kind: 'table', format: 'json' }],
]) {
  let rejection;
  try { normalize(data, spec); } catch (error) { rejection = { name: error.name, message: error.message }; }
  assert.ok(rejection, name);
  observations[name] = rejection;
}
console.log(JSON.stringify(observations));
