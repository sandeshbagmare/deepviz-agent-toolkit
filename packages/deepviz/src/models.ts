/** JSON-compatible contract shared with Python deepviz.models.ChartSpec. */
export const chartKinds = ['bar','line','scatter','area','pie','heatmap','histogram','box','violin','bubble','radar','treemap','sunburst','funnel','gauge','geo','table','dashboard'] as const;
export type ChartKind = typeof chartKinds[number];
export type Engine = 'matplotlib' | 'plotly' | 'vega' | 'echarts' | 'antv';
export type BrowserEngine = Exclude<Engine, 'matplotlib'> | 'svg';
export type DataFormat = 'auto' | 'json' | 'jsonl' | 'csv' | 'tsv' | 'parquet' | 'arrow';
export type Aggregation = 'auto' | 'none' | 'sample' | 'sum' | 'mean' | 'count' | 'min' | 'max';
export interface ChartSpec {
  version: 1;
  kind: ChartKind;
  title: string;
  description: string;
  x: string | null;
  y: string | null;
  color: string | null;
  size: string | null;
  data_path: string | null;
  format: DataFormat;
  aggregation: Aggregation;
  max_points: number;
  width: number;
  height: number;
  theme: 'light' | 'dark';
  charts: ChartSpec[];
  columns: number;
}
export type ChartSpecInput = Partial<Omit<ChartSpec, 'charts'>> & {charts?: ChartSpecInput[]};
export type Scalar = string | number | boolean | null;
export type DataRecord = Record<string, Scalar>;
export interface NormalizedData {
  records: DataRecord[];
  input_count: number;
  warnings: string[];
  strategy: string;
}
export interface Artifact {
  paths: string[];
  mime_type: string;
  engine: string;
  input_count: number;
  output_count: number;
  strategy: string;
  warnings: string[];
}

export class ValidationError extends Error {
  constructor(message: string) { super(message); this.name = 'ValidationError'; }
}
export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
export function safeKey(key: string): void {
  if (key.split('.').some(part => ['__proto__','prototype','constructor'].includes(part))) {
    throw new ValidationError(`Unsafe field or path: ${key}`);
  }
}
const defaults: Omit<ChartSpec, 'charts'> = {
  version: 1, kind: 'bar', title: 'Visualization', description: '',
  x: null, y: null, color: null, size: null, data_path: null,
  format: 'auto', aggregation: 'auto', max_points: 2000,
  width: 900, height: 520, theme: 'light', columns: 2,
};
/** Strict JSON-schema validation: no coercion, expressions, URLs, or extra keys. */
export function validateSpec(input: unknown = {}): ChartSpec {
  return parseSpec(input, 0);
}
function parseSpec(input: unknown, depth: number): ChartSpec {
  if (!isObject(input)) throw new ValidationError('ChartSpec must be an object');
  if (depth > 1) throw new ValidationError('Nested dashboards are not supported');
  for (const key of Object.keys(input)) {
    if (!Object.hasOwn(defaults,key) && key !== 'charts') throw new ValidationError(`Unknown ChartSpec property: ${key}`);
  }
  const spec = {...defaults, ...input, charts: []} as ChartSpec;
  if (spec.version !== 1) throw new ValidationError('version must be 1');
  for (const [key, values] of [
    ['kind', chartKinds], ['format',['auto','json','jsonl','csv','tsv','parquet','arrow']],
    ['aggregation',['auto','none','sample','sum','mean','count','min','max']], ['theme',['light','dark']],
  ] as const) {
    if (!(values as readonly unknown[]).includes(spec[key])) throw new ValidationError(`Invalid ${key}`);
  }
  for (const [key, max] of [['title',500],['description',2000]] as const) {
    if (typeof spec[key] !== 'string' || [...spec[key]].length > max) throw new ValidationError(`${key} must be a string of at most ${max} characters`);
  }
  for (const key of ['x','y','color','size','data_path'] as const) {
    if (spec[key] !== null && typeof spec[key] !== 'string') throw new ValidationError(`${key} must be a string or null`);
  }
  for (const [key, min, max] of [['max_points',10,100000],['width',240,4096],['height',200,4096],['columns',1,6]] as const) {
    if (!Number.isInteger(spec[key]) || spec[key] < min || spec[key] > max) throw new ValidationError(`${key} must be an integer in ${min}..${max}`);
  }
  const charts = Object.hasOwn(input,'charts') ? input.charts : [];
  if (!Array.isArray(charts) || charts.length > 24) throw new ValidationError('charts must be an array of at most 24 charts');
  if (spec.kind === 'dashboard' && !charts.length) throw new ValidationError('A dashboard requires at least one chart');
  if (spec.kind !== 'dashboard' && charts.length) throw new ValidationError('Only dashboards can contain charts');
  if (depth && spec.kind === 'dashboard') throw new ValidationError('Nested dashboards are not supported');
  spec.charts = charts.map(chart => parseSpec(chart, depth + 1));
  return spec;
}
