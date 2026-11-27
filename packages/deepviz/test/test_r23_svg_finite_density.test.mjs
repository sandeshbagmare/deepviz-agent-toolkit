import assert from 'node:assert/strict';
import {test} from 'node:test';
import {render} from '../dist/index.js';

const attrs = text => Object.fromEntries([...text.matchAll(/([\w-]+)="([^"]*)"/g)].map(m => [m[1], m[2]]));
const marks = (svg, tag) => [...svg.matchAll(new RegExp(`<${tag} class="mark"([^>]+)>`, 'g'))].map(m => attrs(m[1]));
const near = (got, want) => assert.ok(Math.abs(got - want) < 1e-9, `${got} != ${want}`);
function chart(rows, kind = 'bar', extra = {}) {
  const artifact = render(rows, {kind, x: 'group', y: 'value', aggregation: 'none', width: 240, height: 200, ...extra}, 'svg');
  assert.deepEqual(artifact.renderer_spec.normalized.records, rows, 'geometry must not change literal input values');
  assert.equal(artifact.input_count, rows.length);
  assert.equal(artifact.output_count, rows.length);
  assert.doesNotMatch(artifact.renderer_spec.spec.svg, /(?:NaN|Infinity)/);
  return artifact.renderer_spec.spec.svg;
}

// An overflowing range, dropped sign/zero, or normalization of raw values breaks these literals.
for (const magnitude of [1e308, Number.MAX_VALUE]) test(`R23 finite bar ±${magnitude} keeps two 35px bars and zero`, () => {
  const svg = chart([{group: 'n', value: -magnitude}, {group: 'p', value: magnitude}]);
  const bars = marks(svg, 'rect');
  assert.equal(bars.length, 2);
  assert.deepEqual(bars.map(b => +b.height), [35, 35]);
  assert.deepEqual(bars.map(b => +b.y), [100, 65]);
  assert.ok(svg.includes(`n: ${-magnitude}`) && svg.includes(`p: ${magnitude}`));
});

test('R23 asymmetric finite MAX magnitudes preserve 1:2 signed heights', () => {
  const bars = marks(chart([{group: 'n', value: -Number.MAX_VALUE / 2}, {group: 'p', value: Number.MAX_VALUE}]), 'rect');
  near(+bars[0].height, 70 / 3);
  near(+bars[1].height, 140 / 3);
  near(+bars[0].y, +bars[1].y + +bars[1].height);
});

for (const kind of ['line', 'area', 'scatter', 'bubble']) test(`R23 ${kind} shares stable signed finite Y coordinates`, () => {
  const svg = chart([{group: 0, value: -1e308, size: 1}, {group: 1, value: 1e308, size: 4}], kind,
    kind === 'bubble' ? {size: 'size'} : {});
  if (kind === 'line' || kind === 'area') {
    const points = marks(svg, 'polyline')[0].points.split(' ').map(pair => pair.split(',').map(Number));
    assert.deepEqual(points, kind === 'area' ? [[120, 100], [120, 135], [175, 65], [175, 100]] : [[120, 135], [175, 65]]);
  } else {
    const circles = marks(svg, 'circle');
    assert.deepEqual(circles.map(c => [+c.cx, +c.cy]), [[120, 135], [175, 65]]);
    assert.deepEqual(circles.map(c => +c.r), kind === 'bubble' ? [15, 30] : [4, 4]);
  }
});

test('R23 numeric X marks and ticks share a finite extreme-range transform', () => {
  const svg = chart([{group: -Number.MAX_VALUE, value: 1}, {group: Number.MAX_VALUE, value: 2}], 'scatter', {width: 960, height: 540});
  assert.deepEqual(marks(svg, 'circle').map(c => +c.cx), [72, 895]);
  const ticks = [...svg.matchAll(/<text class="category-tick"([^>]+)>/g)].map(m => attrs(m[1]));
  assert.deepEqual(ticks.map(t => +t.x), [72, 895]);
});

test('R23 adjacent same-sign MAX X values retain equal spacing', () => {
  const maximum = Number.MAX_VALUE, ulp = 2 ** 971;
  const rows = [maximum - 2 * ulp, maximum - ulp, maximum].map((group, i) => ({group, value: i + 1}));
  assert.deepEqual(marks(chart(rows, 'scatter', {width: 960, height: 540}), 'circle').map(c => +c.cx), [72, 483.5, 895]);
});

test('R23 subnormal X intervals retain the 1:3 ratio', () => {
  const rows = [0, Number.MIN_VALUE, 4 * Number.MIN_VALUE].map((group, i) => ({group, value: i + 1}));
  assert.deepEqual(marks(chart(rows, 'line', {width: 960, height: 540}), 'polyline')[0].points.split(' ').map(pair => +pair.split(',')[0]), [72, 277.75, 895]);
});

test('R23 all-negative finite magnitudes retain sign, 2:1 heights and common zero', () => {
  const bars = marks(chart([{group: 'a', value: -1e308}, {group: 'b', value: -5e307}]), 'rect');
  assert.deepEqual(bars.map(b => +b.height), [70, 35]);
  assert.deepEqual(bars.map(b => +b.y), [65, 65]);
});

test('R23 empty, zero and constant domains remain valid without invented marks', () => {
  assert.equal(marks(chart([]), 'rect').length, 0);
  assert.deepEqual(marks(chart([{group: 'z', value: 0}]), 'rect').map(b => +b.height), [0]);
  assert.deepEqual(marks(chart([{group: 'p', value: 4}]), 'rect').map(b => +b.height), [70]);
  assert.deepEqual(marks(chart([{group: 7, value: 2}], 'scatter'), 'circle').map(c => +c.cx), [72]);
});

test('R23 a nonzero Y that collapses onto emitted zero fails before successful artifact return', () => {
  const rows = [{group: 'tiny', value: Number.MIN_VALUE}];
  for (const kind of ['bar', 'line', 'area', 'scatter', 'bubble']) {
    assert.throws(() => render(kind === 'bar' ? rows : [{group: 0, value: Number.MIN_VALUE}],
      {kind, x: 'group', y: 'value', aggregation: 'none', width: 240, height: 200}, 'svg'),
    /SVG numeric range cannot be represented at requested dimensions/);
  }
  assert.deepEqual(rows, [{group: 'tiny', value: Number.MIN_VALUE}]);
});

const categoryTicks = svg => [...svg.matchAll(/<text class="category-tick"([^>]*)><title>([^<]*)<\/title>([^<]*)<\/text>/g)]
  .map(m => ({...attrs(m[1]), title: m[2], text: m[3]}));
test('R23 ordinary eight 240px labels use readable separate rows without losing bars or text', () => {
  const rows = Array.from({length: 8}, (_, i) => ({group: `g${i}`, value: i + 1}));
  const svg = chart(rows), ticks = categoryTicks(svg);
  assert.deepEqual(ticks.map(t => t.text), rows.map(row => row.group));
  assert.deepEqual([...new Set(ticks.map(t => +t.y))].sort(), [153, 169]);
  assert.equal(marks(svg, 'rect').length, 8);
  assert.ok(ticks.every(t => +t['font-size'] === 12));
});

test('R23 infeasible eight full Unicode labels reject before returning an artifact at 240px', () => {
  const rows = Array.from({length: 8}, (_, i) => ({group: `東京都東部支店${i + 1}`, value: i + 1}));
  let artifact;
  assert.throws(() => {artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none', width: 240, height: 200}, 'svg');},
    /category density cannot fit at requested dimensions.*larger dimensions/);
  assert.equal(artifact, undefined, 'rejection is not a successful chart');
  assert.equal(rows[7].group, '東京都東部支店8');
});

test('R23 full Unicode labels and all fourteen categories are retained when wider space fits', () => {
  for (const rows of [Array.from({length: 8}, (_, i) => ({group: `東京都東部支店${i + 1}`, value: i + 1})),
    Array.from({length: 14}, (_, i) => ({group: `g${i}`, value: i + 1}))]) {
    const svg = chart(rows, 'bar', {width: 960, height: 540}), ticks = categoryTicks(svg);
    assert.deepEqual(ticks.map(t => t.text), rows.map(row => row.group));
    assert.deepEqual(ticks.map(t => t.title), rows.map(row => row.group));
    assert.equal(marks(svg, 'rect').length, rows.length);
  }
});

test('R23 complete labels longer than eighteen characters are never abbreviated', () => {
  const rows = [{group: 'complete-branch-name-01', value: 1}, {group: 'complete-branch-name-02', value: 2}];
  assert.deepEqual(categoryTicks(chart(rows, 'bar', {width: 960, height: 540})).map(t => t.text), rows.map(row => row.group));
});
