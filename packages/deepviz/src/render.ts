import {isObject, validateSpec, ValidationError} from './models.js';
import type {Artifact, BrowserEngine, ChartSpec, NormalizedData} from './models.js';
import {normalize, normalizeStream} from './normalize.js';
import {antvSpec,browserEngines,echartsSpec,escapeHtml,mapping,plotlySpec,svgHtml,tableHtml,vegaSpec} from './renderers.js';
import type {RendererSpec} from './renderers.js';
import {chartSpecSchema} from './schema.js';

export type AssetName='vega'|'vegaLite'|'vegaEmbed'|'echarts'|'antv'|'plotly';
export interface RenderOptions {assets?:Partial<Record<AssetName,string>>}
export interface RendererResult {
  engine:BrowserEngine;
  chart_spec:ChartSpec;
  normalized:NormalizedData;
  spec:RendererSpec;
  children:RendererResult[];
}
export interface HtmlArtifact extends Artifact {html:string;renderer_spec:RendererResult}
export const defaultAssets:Readonly<Record<AssetName,string>>=Object.freeze({
  vega:'https://cdn.jsdelivr.net/npm/vega@6.4.0/build/vega.min.js',
  vegaLite:'https://cdn.jsdelivr.net/npm/vega-lite@6.5.0/build/vega-lite.min.js',
  vegaEmbed:'https://cdn.jsdelivr.net/npm/vega-embed@7.4.0/build/vega-embed.min.js',
  echarts:'https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js',
  antv:'https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js',
  plotly:'https://cdn.jsdelivr.net/npm/plotly.js-dist-min@4.3.0/plotly.min.js',
});
const engineAssets:Record<BrowserEngine,AssetName[]>={vega:['vega','vegaLite','vegaEmbed'],echarts:['echarts'],antv:['antv'],plotly:['plotly'],svg:[]};

function buildNormalized(normalized:NormalizedData,spec:ChartSpec,engine:BrowserEngine):RendererResult {
  const mapped=mapping(normalized,spec,engine);
  const generated=spec.kind==='table'?{html:tableHtml(normalized)}:
    engine==='vega'?vegaSpec(normalized,spec,mapped):engine==='echarts'?echartsSpec(normalized,spec,mapped):
      engine==='antv'?antvSpec(normalized,spec,mapped):engine==='plotly'?plotlySpec(normalized,spec,mapped):{svg:svgHtml(normalized,spec,mapped)};
  return {engine,chart_spec:spec,normalized,spec:generated,children:[]};
}

/** Generate an engine-native spec after validation and bounded normalization. */
export function buildRendererSpec(data:unknown,input:unknown={},engine:BrowserEngine='vega'):RendererResult {
  if(!browserEngines.includes(engine)) throw new ValidationError(`Unsupported browser engine: ${engine}`);
  const spec=validateSpec(input);
  if(spec.kind!=='dashboard') return buildNormalized(normalize(data,spec),spec,engine);
  const children=spec.charts.map(child=>buildNormalized(normalize(data,{
    ...child,
    data_path:child.data_path??spec.data_path,
    format:child.format==='auto'?spec.format:child.format,
  }),child,engine));
  const counts=children.map(child=>child.normalized.input_count);
  const warnings=[...new Set(children.flatMap(child=>child.normalized.warnings))];
  if(new Set(counts).size>1) warnings.push('Dashboard children select different input counts; input_count is the maximum child count');
  return {engine,chart_spec:spec,normalized:{records:[],input_count:Math.max(...counts),warnings,strategy:'dashboard'},spec:{},children};
}

function scriptJson(value:unknown):string {
  return JSON.stringify(value).replace(/[<>&\u2028\u2029]/g,ch=>`\\u${ch.charCodeAt(0).toString(16).padStart(4,'0')}`);
}
function validateAsset(value:unknown):string {
  if(typeof value!=='string' || /[\s<>"'`\\]/.test(value)) throw new ValidationError('Unsafe asset URL');
  const relative=/^(?:\.\.?\/|\/(?!\/))/.test(value);
  const url=new URL(value,'https://deepviz.invalid/');
  if((!relative && !/^https?:\/\//.test(value)) || !['https:','http:'].includes(url.protocol) || url.username || url.password) throw new ValidationError('Unsafe asset URL');
  return value;
}

function artifact(result:RendererResult,options:RenderOptions):HtmlArtifact {
  if(!isObject(options)) throw new ValidationError('Render options must be an object');
  if(options.assets!==undefined && !isObject(options.assets)) throw new ValidationError('assets must be an object');
  const assets={...defaultAssets,...(options.assets as Partial<Record<AssetName,string>>|undefined)};
  for(const key of Object.keys(assets)) {
    if(!Object.hasOwn(defaultAssets,key)) throw new ValidationError(`Unknown asset name: ${key}`);
    validateAsset(assets[key as AssetName]);
  }
  const {engine,chart_spec:spec}=result;
  const charts=result.children.length?result.children:[result];
  const external=charts.some(chart=>chart.chart_spec.kind!=='table')?engineAssets[engine].map(key=>assets[key]):[];
  const nonce=Array.from(globalThis.crypto.getRandomValues(new Uint8Array(16)),value=>value.toString(16).padStart(2,'0')).join('');
  const origins=[...new Set(external.filter(value=>/^https?:/.test(value)).map(value=>new URL(value).origin))];
  const csp=`default-src 'none'; script-src 'nonce-${nonce}' 'self' ${origins.join(' ')}${engine==='vega'?" 'unsafe-eval'":''}; style-src 'unsafe-inline'; img-src data:; font-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'`;
  const payload=charts.map((chart,index)=>({id:`chart-${index}`,engine,spec:chart.spec,kind:chart.chart_spec.kind}));
  const body=charts.map((chart,index)=> {
    const child=chart.chart_spec;
    const content=child.kind==='table'?String(chart.spec.html):engine==='svg'?String(chart.spec.svg):'';
    return `<section aria-labelledby="heading-${index}"><h2 id="heading-${index}">${escapeHtml(child.title)}</h2>${child.description?`<p>${escapeHtml(child.description)}</p>`:''}<div class="chart" id="chart-${index}" style="min-height:${child.height}px">${content}</div>${child.kind!=='table'?`<details><summary>Chart data (${chart.normalized.records.length} rows)</summary>${tableHtml(chart.normalized)}</details>`:''}</section>`;
  }).join('');
  const bootstrap=`(async()=>{const charts=${scriptJson(payload)};globalThis.deepvizReady=false;globalThis.deepvizErrors=[];for(const chart of charts){if(chart.kind==='table'||chart.engine==='svg')continue;try{const el=document.getElementById(chart.id);if(chart.engine==='vega'){await vegaEmbed(el,chart.spec,{actions:false,renderer:'svg',tooltip:false});}else if(chart.engine==='echarts'){echarts.init(el).setOption(chart.spec);}else if(chart.engine==='antv'){const view=new G2.Chart({container:el});view.options(chart.spec);await view.render();}else if(chart.engine==='plotly'){await Plotly.newPlot(el,chart.spec.data,chart.spec.layout,chart.spec.config);}}catch(error){const message=String(error);globalThis.deepvizErrors.push(message);document.getElementById(chart.id).textContent='Chart failed: '+message;}}globalThis.deepvizReady=true;})();`;
  const warnings=result.normalized.warnings;
  const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="${escapeHtml(csp)}"><title>${escapeHtml(spec.title)}</title><style>body{font:14px system-ui,sans-serif;margin:24px;background:${spec.theme==='dark'?'#111827':'#fff'};color:${spec.theme==='dark'?'#e5e7eb':'#1f2937'}}h1{font-size:24px}h2{font-size:18px}.dashboard{display:grid;grid-template-columns:repeat(${spec.kind==='dashboard'?spec.columns:1},minmax(0,1fr));gap:24px}section{min-width:0}.chart{overflow:auto}svg{max-width:100%;height:auto}.table-scroll{overflow:auto;max-height:600px}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #9ca3af;padding:6px 10px;text-align:left}summary{cursor:pointer}@media(max-width:800px){.dashboard{grid-template-columns:1fr}}</style>${external.map(url=>`<script nonce="${nonce}" src="${escapeHtml(url)}"></script>`).join('')}</head><body><h1>${escapeHtml(spec.title)}</h1>${spec.kind==='dashboard' && spec.description?`<p>${escapeHtml(spec.description)}</p>`:''}${warnings.length?`<aside aria-label="Data warnings"><ul>${warnings.map(warning=>`<li>${escapeHtml(warning)}</li>`).join('')}</ul></aside>`:''}<main class="dashboard">${body}</main><script nonce="${nonce}">${bootstrap}</script></body></html>`;
  if(html.length>20_000_000) throw new ValidationError('HTML output exceeds 20 MB character budget; lower max_points or reduce fields');
  return {paths:[],mime_type:'text/html',engine,input_count:result.normalized.input_count,output_count:charts.reduce((sum,chart)=>sum+chart.normalized.records.length,0),strategy:result.normalized.strategy,warnings:[...warnings],html,renderer_spec:result};
}

/** Returns HTML, not a file. Browser assets are network-loaded unless replaced with local URLs. */
export function render(data:unknown,input:unknown={},engine:BrowserEngine='vega',options:RenderOptions={}):HtmlArtifact {
  return artifact(buildRendererSpec(data,input,engine),options);
}

/** Stream a single chart without materializing source rows. */
export async function renderStream(data:AsyncIterable<unknown>|Iterable<unknown>,input:unknown={},engine:BrowserEngine='vega',options:RenderOptions={}):Promise<HtmlArtifact> {
  const spec=validateSpec(input);
  if(spec.kind==='dashboard') throw new ValidationError('Streaming dashboards are unsupported; normalize each chart stream separately');
  return artifact(buildNormalized(await normalizeStream(data,spec),spec,engine),options);
}

export interface RenderTool {
  name:string;
  description:string;
  inputSchema:Record<string,unknown>;
  invoke(input:unknown):Promise<HtmlArtifact>;
}
/** Framework-neutral tool helpers; adapt invoke/inputSchema to your agent SDK. */
export function createTools(options:RenderOptions={}):RenderTool[] {
  return browserEngines.map(engine=>({
    name:`render_${engine}`,
    description:`Validate and render a bounded ${engine} chart or dashboard as HTML. No filesystem or arbitrary code execution.`,
    inputSchema:{type:'object',additionalProperties:false,required:['data'],properties:{data:{},spec:{$ref:'#/$defs/ChartSpec'}},$defs:chartSpecSchema.$defs},
    async invoke(input:unknown):Promise<HtmlArtifact> {
      if(!isObject(input) || !Object.hasOwn(input,'data') || Object.keys(input).some(key=>!['data','spec'].includes(key))) throw new ValidationError('Tool input requires data and optional spec only');
      return render(input.data,input.spec??{},engine,options);
    },
  }));
}
