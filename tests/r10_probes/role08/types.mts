import {
  createTools, normalizeStream, render,
  type ChartSpec, type ChartSpecInput, type NormalizedData, type DataRecord,
  type Scalar, type Artifact, type HtmlArtifact, type BrowserEngine, type Engine,
  type RenderOptions, type RendererResult, type RenderTool, type ChartKind,
  type DataFormat, type Aggregation, type AssetName,
} from '@deepviz/agent-toolkit';

export type PublicTypes = [
  ChartSpec, ChartSpecInput, NormalizedData, DataRecord, Scalar, Artifact,
  HtmlArtifact, BrowserEngine, Engine, RenderOptions, RendererResult, RenderTool,
  ChartKind, DataFormat, Aggregation, AssetName,
];
const spec: ChartSpecInput = {kind:'bar', x:'x', y:'y'};
const artifact: HtmlArtifact = render([{x:'Alpha', y:2}], spec, 'svg');
const normalized = await normalizeStream((async function*(){yield {x:'Alpha', y:2};})(), spec);
console.log(artifact.mime_type, normalized.input_count, createTools().length);
