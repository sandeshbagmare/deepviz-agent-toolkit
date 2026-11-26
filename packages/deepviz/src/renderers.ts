import {ValidationError} from './models.js';
import type {BrowserEngine, ChartSpec, DataRecord, NormalizedData, Scalar} from './models.js';

export type RendererSpec = Record<string, unknown>;
export interface ChartMapping {x:string;y:string;color:string|null;size:string|null}
export const browserEngines: readonly BrowserEngine[]=['vega','echarts','antv','plotly','svg'];
const supported: Record<BrowserEngine,readonly string[]> = {
  vega:['bar','line','scatter','area','pie','heatmap','histogram','box','violin','bubble','table'],
  echarts:['bar','line','scatter','area','pie','heatmap','histogram','bubble','radar','treemap','sunburst','funnel','gauge','table'],
  antv:['bar','line','scatter','area','pie','heatmap','histogram','box','bubble','radar','treemap','table'],
  plotly:['bar','line','scatter','area','pie','heatmap','histogram','box','violin','bubble','radar','treemap','sunburst','funnel','gauge','geo','table'],
  svg:['bar','line','scatter','area','pie','bubble','histogram','table'],
};
const unsupportedColor: Record<BrowserEngine,readonly string[]> = {
  vega:['violin'],
  echarts:['pie','treemap','sunburst','funnel','gauge','radar','histogram'],
  antv:['histogram'],
  plotly:['pie','treemap','sunburst','geo','gauge'],
  svg:['pie','histogram'],
};
export function escapeHtml(value: unknown): string {
  return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]!));
}
function requireNumeric(records:DataRecord[],field:string):void {
  if(records.some(row=>typeof row[field]!=='number')) throw new ValidationError(`Field ${field} requires finite numeric values without null or missing measurements`);
}
export function mapping(data:NormalizedData,spec:ChartSpec,engine:BrowserEngine):ChartMapping {
  if(!browserEngines.includes(engine)) throw new ValidationError(`Unsupported browser engine: ${engine}`);
  if(!supported[engine].includes(spec.kind)) throw new ValidationError(`Unsupported kind ${spec.kind} for ${engine}`);
  if(spec.size && !['scatter','bubble','table'].includes(spec.kind)) throw new ValidationError('Size fields require scatter or bubble charts');
  if(spec.kind==='gauge' && data.records.length!==1) throw new ValidationError('A gauge requires exactly one measurement; aggregate first');
  const fields=[...new Set(data.records.flatMap(row=>Object.keys(row)))];
  const color=spec.color??(spec.kind==='heatmap'?'count':null);
  const x=spec.x??fields[0]??'x';
  const y=spec.y??(spec.kind==='heatmap'?fields.find(field=>field!==x && field!==color):spec.aggregation==='count'?'count':fields.find(field=>field!==x && data.records.some(row=>typeof row[field]==='number')))??x;
  const intrinsicCategoryColor=engine==='vega' && spec.kind==='pie' || engine==='antv' && ['pie','treemap'].includes(spec.kind);
  if(spec.color && (unsupportedColor[engine].includes(spec.kind) || intrinsicCategoryColor && color!==x)) {
    throw new ValidationError(`Color mapping is unsupported for ${engine} ${spec.kind}; omit color or select a grouping-capable chart`);
  }
  if(spec.kind!=='table') {
    for(const field of [x,y,color,spec.size].filter((field):field is string=>field!==null)) {
      if(data.records.length && !fields.includes(field)) throw new ValidationError(`Missing mapped field: ${field}`);
    }
    if(!['histogram','geo','heatmap'].includes(spec.kind)) requireNumeric(data.records,y);
    if(spec.kind==='histogram') requireNumeric(data.records,x);
    if(spec.size) {
      requireNumeric(data.records,spec.size);
      if(data.records.some(row=>Number(row[spec.size!])<0)) throw new ValidationError('Size fields require non-negative values');
    }
    if(spec.kind==='heatmap') {
      requireNumeric(data.records,color!);
      const coordinates=new Set<string>();
      for(const row of data.records) {
        const coordinate=JSON.stringify([row[x],row[y]]);
        if(coordinates.has(coordinate)) throw new ValidationError('Duplicate heatmap coordinates; select an aggregation');
        coordinates.add(coordinate);
      }
    }
    if(['pie','treemap','sunburst','funnel','gauge'].includes(spec.kind) && data.records.some(row=>typeof row[y]==='number' && row[y]<0)) throw new ValidationError(`${spec.kind} requires non-negative values`);
  }
  return {x,y,color,size:spec.size};
}

const literalField=(field:string)=>field.replace(/[.\[\]\\]/g,'\\$&');
function sizeMaximum(data:NormalizedData,field:string):number {
  let max=0;
  for(const row of data.records) max=Math.max(max,Number(row[field]));
  return max||1;
}
export function vegaSpec(data:NormalizedData,spec:ChartSpec,m:ChartMapping):RendererSpec {
  const {x,y,color,size}=m;
  const quantitative=(field:string)=>data.records.some(row=>typeof row[field]==='number');
  const encoding:RendererSpec={
    x:{field:literalField(x),type:quantitative(x)?'quantitative':'nominal'},
    y:{field:literalField(y),type:'quantitative'},
  };
  if(color) encoding.color={field:literalField(color),type:spec.kind==='heatmap'?'quantitative':'nominal'};
  if(size) encoding.size={field:literalField(size),type:'quantitative',scale:{domain:[0,sizeMaximum(data,size)],range:[0,3600],zero:true,nice:false}};
  if(spec.kind==='heatmap') encoding.y={field:literalField(y),type:quantitative(y)?'quantitative':'nominal'};
  const mark:RendererSpec={type:({scatter:'point',bubble:'circle',heatmap:'rect',histogram:'bar',box:'boxplot',pie:'arc',violin:'area'} as Record<string,string>)[spec.kind]??spec.kind,tooltip:false};
  const result:RendererSpec={$schema:'https://vega.github.io/schema/vega-lite/v6.json',data:{values:data.records},mark,encoding,width:spec.width-120,height:spec.height-100,
    config:{background:spec.theme==='dark'?'#111827':'white',axis:{labelColor:spec.theme==='dark'?'#e5e7eb':'#374151',titleColor:spec.theme==='dark'?'#e5e7eb':'#374151'},legend:{labelColor:spec.theme==='dark'?'#e5e7eb':'#374151',titleColor:spec.theme==='dark'?'#e5e7eb':'#374151'}}};
  if(spec.kind==='pie') { delete encoding.x;delete encoding.y;encoding.theta={field:literalField(y),type:'quantitative'};encoding.color={field:literalField(x),type:'nominal'}; }
  if(spec.kind==='histogram') { encoding.x={field:literalField(x),type:'quantitative',bin:true};encoding.y={aggregate:'count',type:'quantitative'}; }
  if(spec.kind==='violin') {
    result.transform=[{density:literalField(y),as:['value','density']}];
    encoding.x={field:'density',type:'quantitative',stack:'center',axis:null};
    encoding.y={field:'value',type:'quantitative'};
    delete encoding.color;delete encoding.size;
    mark.orient='horizontal';
  }
  return result;
}

function bins(rows:DataRecord[],field:string):{x:number,y:number}[] {
  const values=rows.map(row=>row[field]).filter((value):value is number=>typeof value==='number');
  if(!values.length) return [];
  let min=Infinity,max=-Infinity;
  for(const value of values) { min=Math.min(min,value);max=Math.max(max,value); }
  const count=Math.min(30,Math.max(1,Math.ceil(Math.sqrt(values.length))));
  const step=(max-min||1)/count;
  const output=Array.from({length:count},(_,i)=>({x:min+step*(i+0.5),y:0}));
  for(const value of values) output[Math.min(count-1,Math.floor((value-min)/step))]!.y++;
  return output;
}

export function echartsSpec(data:NormalizedData,spec:ChartSpec,m:ChartMapping):RendererSpec {
  const {x,y,color,size}=m;
  if(size && !['scatter','bubble'].includes(spec.kind)) throw new ValidationError('ECharts size fields require scatter or bubble charts');
  const seriesType=({area:'line',bubble:'scatter',histogram:'bar'} as Record<string,string>)[spec.kind]??spec.kind;
  const result:RendererSpec={animation:false,backgroundColor:spec.theme==='dark'?'#111827':'white',textStyle:{color:spec.theme==='dark'?'#e5e7eb':'#374151'},tooltip:{show:false},series:[]};
  if(['pie','treemap','sunburst','funnel'].includes(spec.kind)) {
    result.series=[{type:seriesType,data:data.records.map(row=>({name:String(row[x]??''),value:row[y]}))}];return result;
  }
  if(spec.kind==='gauge') { result.series=[{type:'gauge',min:0,max:Math.max(100,...data.records.map(row=>Number(row[y]))),data:data.records.slice(0,1).map(row=>({name:String(row[x]??''),value:row[y]}))}];return result; }
  if(spec.kind==='radar') {
    result.radar={indicator:data.records.map(row=>({name:String(row[x]??''),max:Math.max(1,Number(row[y]))*1.1}))};
    result.series=[{type:'radar',data:[{value:data.records.map(row=>row[y])}]}];return result;
  }
  if(spec.kind==='heatmap') {
    if(!color) throw new ValidationError('ECharts heatmap requires color as its numeric value field');
    const xs=[...new Set(data.records.map(row=>row[x]))],ys=[...new Set(data.records.map(row=>row[y]))];
    result.xAxis={type:'category',data:xs};result.yAxis={type:'category',data:ys};
    let min=Infinity,max=-Infinity;
    for(const row of data.records) { min=Math.min(min,Number(row[color]));max=Math.max(max,Number(row[color])); }
    result.visualMap={min:data.records.length?min:0,max:data.records.length?max:1,text:data.records.length?[String(max),String(min)]:[],calculable:false};
    result.series=[{type:'heatmap',data:data.records.map(row=>[xs.indexOf(row[x]),ys.indexOf(row[y]),row[color]])}];return result;
  }
  if(spec.kind==='histogram') {
    const values=bins(data.records,x);
    result.xAxis={type:'category',data:values.map(row=>row.x)};result.yAxis={type:'value'};
    result.series=[{type:'bar',data:values.map(row=>row.y),barCategoryGap:'0%'}];return result;
  }
  const scatter=['scatter','bubble'].includes(spec.kind);
  const numericX=scatter || ['line','area'].includes(spec.kind) && data.records.every(row=>typeof row[x]==='number');
  const categories=color?[...new Set(data.records.map(row=>row[x]))]:data.records.map(row=>row[x]);
  result.xAxis=numericX?{type:'value'}:{type:'category',data:categories};result.yAxis={type:'value'};
  if(scatter) requireNumeric(data.records,x);
  const groups=color?[...new Set(data.records.map(row=>row[color]))]:[null];
  const maxSize=size?sizeMaximum(data,size):1;
  result.series=groups.map(group=> {
    const rows=color?data.records.filter(row=>row[color]===group):data.records;
    if(color && !numericX && new Set(rows.map(row=>row[x])).size!==rows.length) throw new ValidationError('Duplicate category within a color group; select an aggregation');
    const series:RendererSpec={name:group===null?'':String(group),type:seriesType,
      data:numericX?rows.map(row=>size?{value:[row[x],row[y]],symbolSize:Math.sqrt(Number(row[size])/maxSize)*60}:[row[x],row[y]]):color?categories.map(category=>rows.find(row=>row[x]===category)?.[y]??null):rows.map(row=>row[y])};
    if(scatter) series.clip=false;
    if(spec.kind==='area') series.areaStyle={};
    return series;
  });
  if(color) result.legend={};
  return result;
}

export function antvSpec(data:NormalizedData,spec:ChartSpec,m:ChartMapping):RendererSpec {
  const {x,y,color,size}=m;
  const result:RendererSpec={type:({bar:'interval',scatter:'point',bubble:'point',pie:'interval',heatmap:'cell',histogram:'rect',box:'boxplot',treemap:'treemap'} as Record<string,string>)[spec.kind]??spec.kind,
    data:data.records,encode:{x,y,...color?{color}: {},...size?{size}:{}},animate:false,interaction:{tooltip:false},theme:spec.theme,width:spec.width,height:spec.height};
  if(size) {
    result.scale={size:{type:'sqrt',domain:[0,sizeMaximum(data,size)],range:[0,30],nice:false}};
    result.paddingRight=45;
  }
  if(spec.kind==='bar' && color) result.transform=[{type:'dodgeX'}];
  if(spec.kind==='pie') { result.coordinate={type:'theta'};result.transform=[{type:'stackY'}];result.encode={y,color:x};result.legend={color:{position:'bottom'}}; }
  if(spec.kind==='histogram') { result.encode={x,y:'count'};result.transform=[{type:'binX',y:'count'}]; }
  if(spec.kind==='radar') { result.type='line';result.coordinate={type:'polar'};result.scale={x:{padding:0.5}}; }
  if(spec.kind==='treemap') {
    result.data={value:{name:'root',children:data.records.map(row=>({name:String(row[x]??''),value:row[y]}))}};
    result.layout={value:'value'};result.encode={color:'name'};
  }
  return result;
}

export function plotlySpec(data:NormalizedData,spec:ChartSpec,m:ChartMapping):RendererSpec {
  const {x,y,color,size}=m;
  const text=(value:Scalar|undefined)=>typeof value==='string'?escapeHtml(value):value;
  const grouped=color!==null && !['heatmap','pie','treemap','sunburst','geo'].includes(spec.kind);
  const groups=grouped?[...new Set(data.records.map(row=>row[color!]))]:[null];
  const sizeRef=size?sizeMaximum(data,size)/1800:1;
  const traces=groups.map(group=> {
    const rows=grouped?data.records.filter(row=>row[color!]===group):data.records;
    const trace:RendererSpec={type:({line:'scatter',area:'scatter',bubble:'scatter',radar:'scatterpolar',gauge:'indicator'} as Record<string,string>)[spec.kind]??spec.kind,
      x:rows.map(row=>text(row[x])),y:rows.map(row=>row[y]),hoverinfo:'skip',...color?{name:group===null?'(missing)':text(group)}:{}};
    if(['line','area'].includes(spec.kind)) trace.mode='lines';
    if(['scatter','bubble'].includes(spec.kind)) trace.mode='markers';
    if(spec.kind==='area') trace.fill='tozeroy';
    if(size) trace.marker={size:rows.map(row=>Number(row[size])),sizemode:'area',sizeref:sizeRef};
    if(['pie','treemap','sunburst'].includes(spec.kind)) {
      delete trace.x;delete trace.y;trace.labels=rows.map(row=>text(row[x]));trace.values=rows.map(row=>row[y]);
      if(spec.kind!=='pie') trace.parents=rows.map(()=> '');
    }
    if(spec.kind==='histogram') { delete trace.y;trace.nbinsx=30; }
    if(spec.kind==='heatmap') {
      if(!color) throw new ValidationError('Plotly heatmap requires color as its numeric value field');
      const xs=[...new Set(rows.map(row=>row[x]))],ys=[...new Set(rows.map(row=>row[y]))];
      if(xs.length*ys.length>100000) throw new ValidationError('Plotly heatmap grid exceeds 100000 cells; aggregate or reduce coordinate cardinality');
      const cells=new Map(rows.map(row=>[JSON.stringify([row[x],row[y]]),row[color]]));
      trace.x=xs.map(text);trace.y=ys.map(text);trace.z=ys.map(yValue=>xs.map(xValue=>cells.get(JSON.stringify([xValue,yValue]))??null));
    }
    if(spec.kind==='radar') { delete trace.x;delete trace.y;trace.theta=rows.map(row=>text(row[x]));trace.r=rows.map(row=>row[y]);trace.fill='toself'; }
    if(spec.kind==='gauge') { delete trace.x;delete trace.y;trace.mode='gauge+number';trace.value=rows[0]?.[y]??0; }
    if(spec.kind==='geo') {
      requireNumeric(rows,x);requireNumeric(rows,y);trace.type='scattergeo';trace.lon=rows.map(row=>row[x]);trace.lat=rows.map(row=>row[y]);trace.mode='markers';delete trace.x;delete trace.y;
    }
    return trace;
  });
  return {data:traces,layout:{width:spec.width,height:spec.height,paper_bgcolor:spec.theme==='dark'?'#111827':'white',plot_bgcolor:spec.theme==='dark'?'#111827':'white',font:{color:spec.theme==='dark'?'#e5e7eb':'#374151'},margin:{l:65,r:25,t:25,b:65},showlegend:!!color || spec.kind==='pie',
    ...(spec.kind==='geo'?{geo:{visible:false,projection:{type:'equirectangular'},lonaxis:{showgrid:true},lataxis:{showgrid:true}}}:{})},config:{responsive:true,displayModeBar:false,staticPlot:true}};
}

export function tableHtml(data:NormalizedData):string {
  const columns=[...new Set(data.records.flatMap(row=>Object.keys(row)))];
  return `<div class="table-scroll"><table><thead><tr>${columns.map(column=>`<th scope="col">${escapeHtml(column)}</th>`).join('')}</tr></thead><tbody>${data.records.map(row=>`<tr>${columns.map(column=>`<td>${escapeHtml(row[column])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}

export function svgHtml(data:NormalizedData,spec:ChartSpec,m:ChartMapping):string {
  let rows=data.records,x=m.x,y=m.y;
  if(spec.kind==='histogram') { rows=bins(rows,x);x='x';y='y'; }
  const width=spec.width,height=spec.height,pad=65,w=width-pad*2,h=height-pad*2;
  const values=rows.map(row=>Number(row[y]??0));
  let min=0,max=1;
  for(const value of values) { min=Math.min(min,value);max=Math.max(max,value); }
  const py=(value:number)=>pad+h-(value-min)/(max-min)*h;
  const numericX=['scatter','bubble'].includes(spec.kind) || ['line','area'].includes(spec.kind) && rows.every(row=>typeof row[x]==='number');
  if(numericX) requireNumeric(rows,x);
  const xv=rows.map(row=>Number(row[x]??0));
  let xmin=Infinity,xmax=-Infinity;
  for(const value of xv) { xmin=Math.min(xmin,value);xmax=Math.max(xmax,value); }
  const categories=m.color || numericX?[...new Set(rows.map(row=>row[x]))]:rows.map(row=>row[x]);
  const px=(i:number)=>numericX?pad+(xv[i]!-xmin)/(xmax-xmin||1)*w:pad+((m.color?categories.indexOf(rows[i]?.[x]):i)+0.5)*w/Math.max(1,categories.length);
  const palette=spec.theme==='dark'?['#60a5fa','#fbbf24','#34d399','#f472b6','#c4b5fd','#fb923c']:['#2563eb','#b45309','#047857','#be185d','#7c3aed','#c2410c'];
  const groups=m.color?[...new Set(rows.map(row=>row[m.color!]))]:[null];
  const groupIndex=(row:DataRecord)=>m.color?groups.indexOf(row[m.color]):0;
  const maxSize=m.size?sizeMaximum(data,m.size):1;
  const colorFor=(i:number)=>palette[i%palette.length]!;
  const dashFor=(i:number)=>['','7 4','2 3','9 3 2 3'][i%4]!;
  const textColor=spec.theme==='dark'?'#e5e7eb':'#374151';
  let marks='';
  if(spec.kind==='pie') {
    const total=values.reduce((a,b)=>a+b,0),radius=Math.min(w,h)/2;
    let angle=-Math.PI/2;
    marks=values.map((value,i)=> {
      const delta=total?value/total*Math.PI*2:0,end=angle+delta;
      const cx=width/2,cy=height/2;
      const path=delta>=Math.PI*2-1e-10?`<circle class="mark" cx="${cx}" cy="${cy}" r="${radius}" fill="${colorFor(i)}"><title>${escapeHtml(rows[i]?.[x])}: ${value}</title></circle>`:
        `<path class="mark" d="M${cx},${cy} L${cx+Math.cos(angle)*radius},${cy+Math.sin(angle)*radius} A${radius},${radius} 0 ${delta>Math.PI?1:0},1 ${cx+Math.cos(end)*radius},${cy+Math.sin(end)*radius} Z" fill="${colorFor(i)}"><title>${escapeHtml(rows[i]?.[x])}: ${value}</title></path>`;
      angle=end;return delta?path:'';
    }).join('');
  } else if(['bar','histogram'].includes(spec.kind)) {
    const barWidth=w/Math.max(categories.length,1)*0.8/Math.max(groups.length,1);
    marks=rows.map((row,i)=>`<rect class="mark" x="${px(i)-w/Math.max(categories.length,1)*0.4+barWidth*groupIndex(row)}" y="${Math.min(py(0),py(values[i]!))}" width="${barWidth}" height="${Math.abs(py(0)-py(values[i]!))}" fill="${colorFor(groupIndex(row))}"><title>${escapeHtml(row[x])}: ${values[i]}</title></rect>`).join('');
  } else if(['line','area'].includes(spec.kind)) {
    marks=groups.map((_,g)=>{
      const indices=rows.map((row,i)=>({row,i})).filter(({row})=>groupIndex(row)===g).map(({i})=>i);
      if(!indices.length)return '';
      const points=indices.map(i=>`${px(i)},${py(values[i]!)}`).join(' ');
      return `<polyline class="mark" points="${spec.kind==='area'?`${px(indices[0]!)},${py(0)} `:''}${points}${spec.kind==='area'?` ${px(indices.at(-1)!)},${py(0)}`:''}" fill="${spec.kind==='area'?colorFor(g):'none'}" fill-opacity="0.25" stroke="${colorFor(g)}" stroke-dasharray="${dashFor(g)}" stroke-width="2"/>`;
    }).join('');
  } else marks=rows.map((row,i)=>`<circle class="mark" cx="${px(i)}" cy="${py(values[i]!)}" r="${m.size?Math.sqrt(Number(row[m.size])/maxSize)*30:4}" fill="${colorFor(groupIndex(row))}"><title>${escapeHtml(row[x])}: ${values[i]}</title></circle>`).join('');
  const stride=Math.max(1,Math.ceil(categories.length/12));
  const shortLabel=(value:unknown)=>{const text=String(value??'');return text.length>18?`${text.slice(0,9)}…${text.slice(-8)}`:text;};
  const ticks=categories.map((value,i)=>({value,i})).filter(({i})=>i%stride===0 || i===categories.length-1).map(({value,i})=>{
    const position=numericX?pad+(Number(value)-xmin)/(xmax-xmin||1)*w:m.color?pad+(i+0.5)*w/Math.max(1,categories.length):px(i);
    return `<text class="category-tick" x="${position}" y="${pad+h+18}" text-anchor="middle" font-size="12"><title>${escapeHtml(value)}</title>${escapeHtml(shortLabel(value))}</text>`;
  }).join('');
  const axis=spec.kind==='pie'?'':`<g fill="${textColor}"><path d="M${pad},${pad} V${pad+h} H${pad+w}" fill="none" stroke="${textColor}"/><text x="${pad-8}" y="${pad+8}" text-anchor="end">${escapeHtml(max.toPrecision(4))}</text><text x="${pad-8}" y="${pad+h}" text-anchor="end">${escapeHtml(min.toPrecision(4))}</text><text x="${width/2}" y="${height-12}" text-anchor="middle">${escapeHtml(x)}</text><text transform="translate(15 ${height/2}) rotate(-90)" text-anchor="middle">${escapeHtml(y)}</text>${ticks}</g>`;
  const legend=spec.kind==='pie'?`<ul aria-label="Category key">${rows.map((row,i)=>`<li><svg aria-hidden="true" width="20" height="12"><circle cx="6" cy="6" r="5" fill="${colorFor(i)}"/></svg> ${escapeHtml(row[x])}</li>`).join('')}</ul>`:
    m.color?`<ul aria-label="Series key">${groups.map((group,g)=>`<li><svg aria-hidden="true" width="36" height="12"><line x1="0" y1="6" x2="32" y2="6" stroke="${colorFor(g)}" stroke-dasharray="${dashFor(g)}" stroke-width="3"/></svg> ${escapeHtml(group)}</li>`).join('')}</ul>`:'';
  return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${escapeHtml(spec.title)}" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" fill="${textColor}"><title>${escapeHtml(spec.title)}</title>${axis}${marks}</svg>${legend}`;
}
