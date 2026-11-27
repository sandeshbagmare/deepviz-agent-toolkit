import assert from 'node:assert/strict';
import {test} from 'node:test';
import {render} from '../dist/index.js';

const measured = [6249996250000, 6249997500000, 6249998750000, 6250000000000,
  6250001250000, 6250002500000, 6250003750000, 6250005000000];
const cases = [
  ['small-positive', [1, 2, 3, 4, 5, 6, 7, 8]],
  ['measured-aggregate', measured],
  ['signed-scientific', [-9.999e120, -6e120, -3e120, -1e120, 1e120, 3e120, 6e120, 9.999e120]],
  ['negative', [-1, -2, -3, -4, -5, -6, -7, -8]],
  ['fixed-small-negative', [-0.000001, 1, 2, 3, 4, 5, 6, 7]],
];
const attrs = text => Object.fromEntries([...text.matchAll(/([\w-]+)="([^"]*)"/g)].map(match => [match[1], match[2]]));

for (const [name, values] of cases) for (const [width, height] of [[960, 540], [240, 200]]) {
  test(`R11 SVG ${name} at ${width}x${height}: deterministic readable numeric tick space`, () => {
    const rows = values.map((value, i) => ({group: `g${i}`, value}));
    const artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none',
      width, height, max_points: 10}, 'svg');
    const svg = artifact.renderer_spec.spec.svg;
    assert.equal(artifact.input_count, 8);
    assert.equal(artifact.output_count, 8);
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    assert.match(svg, new RegExp(`viewBox="0 0 ${width} ${height}"`));
    const axis = attrs(svg.match(/<g\b[^>]*>/)[0]);
    assert.equal(axis['font-family'], 'monospace', 'numeric ticks need explicit matching SVG/HTML font metrics');
    assert.equal(axis['font-size'], '12', 'readable fixed font size, not shrink-to-fit');
    const ticks = [...svg.matchAll(/<text\b([^>]*)>([^<]*)<\/text>/g)]
      .map(match => ({...attrs(match[1]), text: match[2]})).filter(text => text['text-anchor'] === 'end');
    assert.deepEqual(ticks.map(tick => tick.text), [Math.max(1, ...values).toPrecision(4), Math.min(0, ...values).toPrecision(4)]);
    for (const tick of ticks) {
      // A 12px monospace advance is ~7.2px; reserve room for the y-axis title too.
      assert.ok(+tick.x - tick.text.length * 7.2 >= 24, `left numeric label space too small for ${tick.text}`);
    }
    const bars = [...svg.matchAll(/<rect\b([^>]*)><title>([^<]*)<\/title><\/rect>/g)]
      .map(match => ({...attrs(match[1]), title: match[2]}));
    assert.equal(bars.length, 8);
    const unit = +bars[0].height / Math.abs(values[0]);
    const zero = +bars[0].y + (values[0] >= 0 ? +bars[0].height : 0);
    bars.forEach((bar, i) => {
      assert.equal(bar.title, `g${i}: ${values[i]}`);
      assert.ok(+bar.width > 0 && +bar.height > 0 && +bar.x >= 0 && +bar.x + +bar.width <= width);
      assert.ok(Math.abs(+bar.height - Math.abs(values[i]) * unit) < 1e-6);
      assert.ok(Math.abs(+bar.y + (values[i] >= 0 ? +bar.height : 0) - zero) < 1e-6);
    });
    assert.doesNotMatch(svg, /NaN|Infinity/);
  });
}

test('R11 native SVG margin change preserves escaped title, field/category labels and series legend', () => {
  const artifact = render([{category: '<unsafe>', value: measured[0], series: '<cohort>'},
    {category: 'safe', value: measured[1], series: 'safe'}],
  {kind: 'bar', title: '</title><script>bad</script>', x: 'category', y: 'value', color: 'series', aggregation: 'none'}, 'svg');
  const svg = artifact.renderer_spec.spec.svg;
  assert.ok(svg.includes('&lt;unsafe&gt;') && svg.includes('&lt;cohort&gt;'));
  assert.ok(svg.includes('&lt;/title&gt;&lt;script&gt;bad&lt;/script&gt;'));
  assert.ok(svg.includes('aria-label="Series key"'));
  assert.ok(!svg.includes('<script>'));
});
