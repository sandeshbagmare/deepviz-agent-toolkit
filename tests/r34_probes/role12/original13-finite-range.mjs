import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {join, resolve} from 'node:path';
import {test} from 'node:test';
import {pathToFileURL} from 'node:url';

const source = resolve(process.env.R17_13_SOURCE);
assert.equal(execFileSync('git', ['rev-parse', 'HEAD'], {cwd: source, encoding: 'utf8'}).trim(),
  process.env.DEEPVIZ_R34_EXPECT_HEAD);
const {render} = await import(pathToFileURL(join(source, 'packages/deepviz/dist/index.js')).href);

for (const magnitude of [1e200, 1e308]) {
  test(`R17 finite signed ${magnitude}: two visible bars with finite common-baseline geometry`, () => {
    const rows = [{group: 'negative', value: -magnitude}, {group: 'positive', value: magnitude}];
    const artifact = render(rows, {kind: 'bar', x: 'group', y: 'value', aggregation: 'none',
      width: 240, height: 200}, 'svg');
    assert.deepEqual(artifact.renderer_spec.normalized.records, rows);
    const svg = artifact.renderer_spec.spec.svg;
    assert.doesNotMatch(svg, /(?:x|y|width|height)="(?:NaN|-?Infinity)/,
      'two finite accepted measurements must not produce invalid SVG coordinates');
    const bars = [...svg.matchAll(/<rect class="mark"([^>]+)>/g)].map(match =>
      Object.fromEntries([...match[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(m => [m[1], m[2]])));
    assert.equal(bars.length, 2);
    for (const bar of bars) assert.equal(+bar.height, 35, 'opposite equal values need equal visible magnitude');
    assert.equal(+bars[0].y, +bars[1].y + +bars[1].height, 'positive and negative bars share zero');
  });
}
