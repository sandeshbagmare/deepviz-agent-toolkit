import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import test from 'node:test';

if (!process.env.DEEPVIZ_R15_TS_ENTRY) throw new Error('Set DEEPVIZ_R15_TS_ENTRY to the built pinned public index.js');
const { buildRendererSpec } = await import(pathToFileURL(process.env.DEEPVIZ_R15_TS_ENTRY));
const rows = [
  { group: 'A', position: 0, series: 90, weight: 900, measure: 10 },
  { group: 'A', position: 0, series: 90, weight: 900, measure: 10 },
  { group: 'B', position: 1, series: 80, weight: 800, measure: 20 },
  { group: 'B', position: 1, series: 80, weight: 800, measure: 20 },
  { group: 'B', position: 1, series: 80, weight: 800, measure: 20 },
  { group: 'C', position: 10, series: 70, weight: 700, measure: 30 },
];
const countRecords = [{ group: 'A', series: 90, count: 2 }, { group: 'B', series: 80, count: 3 }, { group: 'C', series: 70, count: 1 }];
const bubbleRecords = [{ position: 0, series: 90, count: 2 }, { position: 1, series: 80, count: 3 }, { position: 10, series: 70, count: 1 }];
const noneRows = [{ group: 'A', series: 90, weight: 900, measure: 4 }, { group: 'B', series: 80, weight: 800, measure: 7 }, { group: 'C', series: 70, weight: 700, measure: 2 }];

function measures(engine, native) {
  if (engine === 'vega') {
    assert.equal(native.encoding.y.type, 'quantitative');
    return native.data.values.map(row => row[native.encoding.y.field]);
  }
  if (engine === 'antv') return native.data.map(row => row[native.encode.y]);
  if (engine === 'plotly') return native.data.flatMap(trace => trace.y);
  assert.equal(native.yAxis.type, 'value');
  return native.series.flatMap(series => series.data.filter(value => value !== null)
    .map(value => Array.isArray(value) ? value[1] : typeof value === 'object' ? value.value[1] : value));
}

for (const engine of ['vega', 'antv', 'plotly', 'echarts']) {
  for (const kind of ['bar', 'line', 'bubble']) test(`${engine} ${kind} COUNT ignores numeric color/retained size as measure`, () => {
    const result = buildRendererSpec(rows, { kind, x: kind === 'bubble' ? 'position' : 'group', color: 'series',
      ...(kind === 'bubble' ? { size: 'series' } : {}), aggregation: 'count', max_points: 10 }, engine);
    assert.deepEqual(result.normalized.records, kind === 'bubble' ? bubbleRecords : countRecords);
    assert.equal(result.normalized.input_count, 6);
    assert.equal(result.normalized.strategy, 'count');
    assert.deepEqual(result.normalized.warnings, []);
    assert.deepEqual(measures(engine, result.spec), [2, 3, 1]);
  });
  for (const kind of ['bar', 'line']) for (const aggregation of ['sum', 'none']) {
    test(`${engine} ${kind} explicit ${aggregation} remains its own measure`, () => {
      const result = buildRendererSpec(aggregation === 'sum' ? rows : noneRows,
        { kind, x: 'group', color: 'series', y: 'measure', aggregation, max_points: 10 }, engine);
      assert.equal(result.normalized.strategy, aggregation);
      assert.deepEqual(measures(engine, result.spec), aggregation === 'sum' ? [20, 60, 30] : [4, 7, 2]);
    });
  }
}
