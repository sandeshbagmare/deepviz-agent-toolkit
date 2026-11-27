import assert from 'node:assert/strict';
import {test} from 'node:test';
import {render} from '../dist/index.js';

// Narrow abbreviations must not merge 250 and 750 into the same visible label.
test('R34 narrow legacy thinning keeps selected numeric-suffix categories distinguishable', () => {
  const rows = Array.from({length: 1000}, (_, i) => ({group: `Common long category name ${i}`, value: i}));
  const artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none', width: 240, height: 200}, 'svg');
  const svg = artifact.renderer_spec.spec.svg;
  const ticks = [...svg.matchAll(/<text class="category-tick"[^>]*><title>([^<]*)<\/title>([^<]*)<\/text>/g)];
  assert.ok(ticks.length >= 5 && ticks.length <= 15);
  assert.equal(new Set(ticks.map(tick => tick[2])).size, ticks.length);
  assert.ok(ticks.every(tick => tick[2].includes('…')));
  assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
  assert.equal(artifact.input_count, 1000);
  assert.equal(artifact.output_count, 1000);
  assert.match(svg, /<title>Common long category name 999: 999<\/title>/);
});
