import {
  render, normalizeStream, validateSpec,
  type ChartKind, type Engine, type BrowserEngine, type DataFormat, type Aggregation,
  type ChartSpec, type ChartSpecInput, type Scalar, type DataRecord, type NormalizedData,
  type Artifact, type AssetName, type RenderOptions, type RendererResult,
  type HtmlArtifact, type RenderTool,
} from '@deepviz/agent-toolkit';

// All sixteen public type names must remain exported; no source-tree paths aliases.
export type UnchangedTypeSurface = [
  ChartKind, Engine, BrowserEngine, DataFormat, Aggregation, ChartSpec, ChartSpecInput,
  Scalar, DataRecord, NormalizedData, Artifact, AssetName, RenderOptions,
  RendererResult, HtmlArtifact, RenderTool,
];
const spec: ChartSpecInput = {kind: 'bar', x: 'region', y: 'value', aggregation: 'sum'};
const validated: ChartSpec = validateSpec(spec);
const record: DataRecord = {region: '東京', value: 7};
const chart: HtmlArtifact = render([record], validated, 'svg');
const baseArtifact: Artifact = chart;
const result: NormalizedData = await normalizeStream((async function* () { yield record; })(), spec);
console.log(baseArtifact.output_count, result.input_count, chart.html.length);
