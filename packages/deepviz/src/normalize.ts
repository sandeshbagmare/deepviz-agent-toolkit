import {isObject, safeKey, validateSpec, ValidationError} from './models.js';
import type {Aggregation, ChartSpec, DataRecord, NormalizedData, Scalar} from './models.js';

const MAX_FIELDS = 1024;
const MAX_DEPTH = 64;
const MAX_CELL_BYTES = 64 * 1024;
const MAX_RECORD_BYTES = 256 * 1024;
const MAX_RETAINED_BYTES = 16 * 1024 * 1024;
const wrappers = ['edges','nodes','records','rows','results','items','pages','data'];
const metadata = ['pageInfo','totalCount','count','extensions','errors','meta','pagination'];
const numericText = /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$/;
// Python str.strip whitespace: FEFF is cell content, while NEL and the record separators are whitespace.
function pythonStrip(text:string):string {
  return text.replace(/^[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+|[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+$/g,'');
}

function stringBytes(text:string):number {
  if(text.length>MAX_CELL_BYTES)throw new ValidationError('String cell or field name exceeds 64 KiB UTF-8 limit');
  let utf8=0,json=2;
  for(let i=0;i<text.length;i++) {
    const code=text.charCodeAt(i),next=text.charCodeAt(i+1);
    let bytes=code<0x80?1:code<0x800?2:3;
    if(code>=0xd800 && code<=0xdbff && next>=0xdc00 && next<=0xdfff) {bytes=4;i++;json+=4;}
    else if(code===34 || code===92 || code===8 || code===9 || code===10 || code===12 || code===13)json+=2;
    else if(code<32 || (code>=0xd800 && code<=0xdfff))json+=6;
    else json+=bytes;
    utf8+=bytes;
    if(utf8>MAX_CELL_BYTES)throw new ValidationError('String cell or field name exceeds 64 KiB UTF-8 limit');
  }
  return json;
}

function scalarBytes(value:Scalar):number {return typeof value==='string'?stringBytes(value):String(value).length;}
function fieldBytes(key:string,value:Scalar):number {return stringBytes(key)+1+scalarBytes(value);}
function recordBytes(row:DataRecord):number {
  let bytes=2,fields=0;
  for(const [key,value] of Object.entries(row)) {
    bytes+=fieldBytes(key,value)+(fields++?1:0);
    checkRecordBytes(bytes);
  }
  return bytes;
}
function checkRecordBytes(bytes:number):void {
  if(bytes>MAX_RECORD_BYTES)throw new ValidationError('Flattened record exceeds 256 KiB UTF-8 JSON byte budget');
}

type Notice=(message:string)=>void;
function checkGraphql(value:Record<string,unknown>,warn:Notice):void {
  const errors=value.errors;
  if(!errors || ((Array.isArray(errors) || isObject(errors)) && !Object.keys(errors).length))return;
  if(!Object.hasOwn(value,'data') && !Object.keys(value).every(key=>metadata.includes(key)))return;
  const data=value.data;
  if(!data || ((Array.isArray(data) || isObject(data)) && !Object.keys(data).length))throw new ValidationError('GraphQL response contains errors and no data');
  warn('GraphQL responses contained errors alongside usable data');
}

interface PathState {matches:number;missing:number;empty:number}
function* pathValues(value: unknown, parts: string[], state:PathState,warn:Notice, depth = 0): Generator<unknown> {
  if (depth > MAX_DEPTH) throw new ValidationError('Data path exceeds maximum depth');
  if (!parts.length) { state.matches++;yield value; return; }
  if(isObject(value))checkGraphql(value,warn);
  if (Array.isArray(value)) {
    if(/^\d+$/.test(parts[0]!)) {
      const index=Number(parts[0]);
      if(index>=value.length)state.missing++;
      else yield* pathValues(value[index],parts.slice(1),state,warn,depth+1);
    } else {
      if(!value.length)state.empty++;
      for (const item of value) yield* pathValues(item, parts, state,warn, depth + 1);
    }
    return;
  }
  const [head, ...tail] = parts;
  if (!isObject(value) || !head || !Object.hasOwn(value, head)) {state.missing++;return;}
  yield* pathValues(value[head], tail, state,warn, depth + 1);
}

function hasCollection(value: unknown, depth = 0): boolean {
  if (depth > MAX_DEPTH) throw new ValidationError('Cyclic input or maximum nesting depth exceeded');
  if (Array.isArray(value)) return true;
  return isObject(value) && Object.values(value).some(item => hasCollection(item, depth + 1));
}

function graphqlConnection(value:Record<string,unknown>,depth=0):boolean {
  if(depth>MAX_DEPTH)throw new ValidationError('GraphQL response exceeds maximum depth');
  if(Object.hasOwn(value,'edges') || Object.hasOwn(value,'nodes'))return true;
  const children=Object.entries(value).filter(([key])=>!metadata.includes(key)).map(([,child])=>child);
  if(children.length===1 && isObject(children[0]))return graphqlConnection(children[0],depth+1);
  if(children.length>1 && children.some(child=>isObject(child) && graphqlConnection(child,depth+1)))throw new ValidationError('Ambiguous GraphQL fields require an explicit data_path');
  return false;
}

function sequenceEnvelope(value:Record<string,unknown>):boolean {
  return (Object.hasOwn(value,'node') && Object.keys(value).every(key=>['node','cursor'].includes(key)))
    || ['data','edges','nodes','pages'].some(key=>Object.hasOwn(value,key) && hasCollection(value[key]));
}

function* unpack(value: unknown, warn:Notice, depth = 0): Generator<unknown> {
  if (depth > MAX_DEPTH) throw new ValidationError('Cyclic input or maximum nesting depth exceeded');
  if (Array.isArray(value)) {
    for (const row of value) {
      if (isObject(row) && Object.hasOwn(row,'node') && Object.keys(row).every(key=>['node','cursor'].includes(key))) {
        if(row.node===null)warn('Null GraphQL/path nodes skipped');else yield* unpack(row.node,warn,depth+1);
      }
      else if (isObject(row) && sequenceEnvelope(row)) yield* unpack(row,warn,depth+1);
      else yield row;
    }
    return;
  }
  if (isObject(value)) {
    for (const key of Object.keys(value)) {stringBytes(key);safeKey(key);}
    const entries=Object.entries(value);
    if(!entries.length && !depth)return;
    if(Object.hasOwn(value,'node') && entries.every(([key])=>['node','cursor'].includes(key))) {
      if(value.node===null)warn('Null GraphQL/path nodes skipped');else yield* unpack(value.node,warn,depth+1);
      return;
    }
    checkGraphql(value,warn);
    const arrays=entries.filter(([,item])=>Array.isArray(item));
    const scalarColumns=arrays.every(([,items])=>(items as unknown[]).every(item=>!isObject(item) && !Array.isArray(item)));
    const nullConnection=entries.length===1 && ['nodes','edges'].includes(entries[0]![0])
      && Array.isArray(entries[0]![1]) && entries[0]![1].every(item=>item===null);
    if(entries.length && arrays.length===entries.length && !nullConnection && (entries.length>1 || !wrappers.includes(entries[0]![0]) || scalarColumns)) {
      const length=(arrays[0]![1] as unknown[]).length;
      if(arrays.some(([,item])=>(item as unknown[]).length!==length))throw new ValidationError('Column arrays must have equal length');
      if(entries.length>1 && !scalarColumns)throw new ValidationError('Ambiguous nested column arrays; set an explicit data_path');
      for(let i=0;i<length;i++)yield Object.fromEntries(arrays.map(([key,items])=>[key,(items as unknown[])[i]]));
      return;
    }
    const connection=graphqlConnection(value);
    if(Object.hasOwn(value,'edges') || Object.hasOwn(value,'nodes')) {
      if(Object.hasOwn(value,'edges') && Object.hasOwn(value,'nodes'))throw new ValidationError('GraphQL connection has both edges and nodes; choose data_path');
      const edges=Object.hasOwn(value,'edges');
      const nodes=edges?value.edges:value.nodes;
      if(!Array.isArray(nodes))throw new ValidationError('GraphQL edges/nodes must be arrays');
      for(const item of nodes) {
        if(edges && (!isObject(item) || !Object.hasOwn(item,'node')))throw new ValidationError('Each GraphQL edge must contain a node');
        const node=edges?(item as Record<string,unknown>).node:item;
        if(node===null)warn('Null GraphQL/path nodes skipped');else yield* unpack(node,warn,depth+1);
      }
      return;
    }
    const preferred=entries.filter(([key,item])=>wrappers.includes(key) && hasCollection(item)
      && entries.every(([sibling])=>sibling===key || metadata.includes(sibling)));
    const candidates=preferred.length ? preferred : entries.filter(([,item])=>hasCollection(item));
    if (candidates.length>1) throw new ValidationError('Ambiguous collections; set data_path');
    if (!preferred.length && candidates.length && entries.some(([,item])=>!isObject(item) && !Array.isArray(item))) {yield value;return;}
    if (candidates.length===1) {
      if(!preferred.length && !connection)throw new ValidationError('Ambiguous custom collection; set an explicit data_path');
      yield* unpack(candidates[0]![1],warn,depth+1);return;
    }
    yield value;
    return;
  }
  if (value===null || ['string','number','boolean'].includes(typeof value)) { yield value; return; }
  throw new ValidationError('Expected JSON records, columns, or a supported text format');
}

function* csvRows(text: string, delimiter: string): Generator<string[]> {
  let row: string[]=[], field='', quoted=false, closed=false;
  let cellBytes=0,rowBytes=2;
  const append=(text:string):void=> {
    const code=text.codePointAt(0)!;
    const bytes=code<0x80?1:code<0x800?2:code<0x10000?3:4;
    if(cellBytes+bytes>MAX_CELL_BYTES)throw new ValidationError('String cell or field name exceeds 64 KiB UTF-8 limit');
    cellBytes+=bytes;field+=text;
  };
  const push=():void=> {
    if(row.length>=MAX_FIELDS)throw new ValidationError(`CSV row exceeds ${MAX_FIELDS} fields`);
    const cost=rowBytes+stringBytes(field)+(row.length?1:0);checkRecordBytes(cost);
    rowBytes=cost;row.push(field);field='';cellBytes=0;
  };
  for(let i=0;i<text.length;i++) {
    let ch=text[i]!;
    const code=ch.charCodeAt(0),next=text.charCodeAt(i+1);
    if(code>=0xd800 && code<=0xdbff && next>=0xdc00 && next<=0xdfff) {ch=text.slice(i,i+2);i++;}
    if(quoted) {
      if(ch==='"' && text[i+1]==='"') { append('"'); i++; }
      else if(ch==='"') { quoted=false; closed=true; }
      else append(ch);
    } else if(ch==='"' && !field && !closed) quoted=true;
    else if(ch===delimiter) { push();closed=false; }
    else if(ch==='\n' || ch==='\r') {
      if(ch==='\r' && text[i+1]==='\n') i++;
      if(field || closed || row.length) { push();yield row; }
      row=[];rowBytes=2;field='';cellBytes=0;closed=false;
    } else {
      if(closed || ch==='"') throw new ValidationError('Malformed CSV quote');
      append(ch);
    }
  }
  if(quoted) throw new ValidationError('Unclosed CSV quote');
  if(field || closed || row.length) { push();yield row; }
}

function checkJsonKeys(text:string):void {
  const frames:{keys:Set<string>|null,expectKey:boolean,cost:number}[]=[];
  let retained=0;
  for(let i=0;i<text.length;i++) {
    const ch=text[i]!;
    if(ch==='"') {
      const start=i++;
      while(i<text.length && text[i]!=='"') {
        if(i-start>MAX_CELL_BYTES*6+2)throw new ValidationError('String cell or field name exceeds 64 KiB UTF-8 limit');
        if(text[i]==='\\')i++;
        i++;
      }
      const decoded=JSON.parse(text.slice(start,i+1)) as string;
      const cost=stringBytes(decoded),frame=frames.at(-1);
      if(frame?.keys && frame.expectKey) {
        if(frame.keys.has(decoded))throw new ValidationError(`Duplicate JSON object key: ${decoded}`);
        if(frame.keys.size>=MAX_FIELDS)throw new ValidationError(`JSON object exceeds ${MAX_FIELDS} fields`);
        if(retained+cost+16>MAX_RETAINED_BYTES)throw new ValidationError('Retained JSON key state exceeds 16 MiB UTF-8 JSON byte budget');
        retained+=cost+16;frame.cost+=cost+16;frame.keys.add(decoded);frame.expectKey=false;
      }
    } else if(ch==='{' || ch==='[') {
      if(frames.length>MAX_DEPTH)throw new ValidationError('JSON input exceeds maximum depth');
      frames.push({keys:ch==='{'?new Set<string>():null,expectKey:ch==='{',cost:0});
    } else if(ch==='}' || ch===']')retained-=frames.pop()?.cost??0;
    else if(ch===',' && frames.at(-1)?.keys)frames.at(-1)!.expectKey=true;
  }
}

function parseJson(text:string,auto=false):unknown {
  try {checkJsonKeys(text);return JSON.parse(text);}
  catch(error) {
    if(error instanceof ValidationError || auto)throw error;
    throw new ValidationError('Content is not valid JSON or JSONL');
  }
}

function* parseText(text: string, spec: ChartSpec,warn:Notice,state:PathState): Generator<unknown> {
  text=text.replace(/^\uFEFF+/,'');
  let format=spec.format;
  if(format==='auto') {
    if(!pythonStrip(text))return;
    let parsed:unknown;
    try {parsed=parseJson(text,true);}
    catch(error) {
      if(!(error instanceof SyntaxError))throw error;
      if(/^\s*[\[{]/.test(text))format='jsonl';
      else {
        const first=text.split('\n',1)[0]!;
        if(!/[\t,]/.test(first))throw new ValidationError('Content is not valid JSON, JSONL or delimited content; specify format');
        format=first.includes('\t')?'tsv':'csv';
      }
    }
    if(format==='auto') {yield* selected(parsed,spec,warn,state);return;}
  }
  if(format==='json') { yield* selected(parseJson(text),spec,warn,state); return; }
  if(format==='jsonl') {
    // Match one line at a time rather than allocating an array of every line.
    for(const match of text.matchAll(/[^\r\n]+/g)) if(pythonStrip(match[0])) yield* selected(parseJson(match[0]),spec,warn,state,true);
    return;
  }
  if(format!=='csv' && format!=='tsv') throw new ValidationError(`Unsupported ${format}; use an Arrow/Parquet adapter to supply records`);
  let header: string[]|undefined;
  for(const row of csvRows(text.replace(/^\uFEFF/,''),format==='tsv'?'\t':',')) {
    if(!header) {
      header=row;
      if(header.length>MAX_FIELDS || header.some(key=>!pythonStrip(key)) || new Set(header).size!==header.length) throw new ValidationError('CSV header must have unique non-empty names');
      header.forEach(safeKey);
    } else {
      if(row.length!==header.length) throw new ValidationError('CSV column count does not match header');
      yield* selected(Object.fromEntries(header.map((key,i)=> {
        const value=row[i]!;
        const stripped=pythonStrip(value);
        return [key, !stripped?null:numericText.test(stripped)?stripped==='-0'?0:Number(stripped):/^(?:nan|[+-]?inf(?:inity)?)$/i.test(stripped)?NaN:value];
      })),spec,warn,state,true);
    }
  }
}

function* selected(data: unknown, spec: ChartSpec,warn:Notice,state:PathState,sequence=false): Generator<unknown> {
  if(spec.data_path!==null) {
    safeKey(spec.data_path);
    const parts=spec.data_path.split('.');
    if(parts.some(part=>!part))throw new ValidationError('data_path must contain non-empty dot-separated components');
    for(const value of pathValues(data,parts,state,warn)) {
      if(value===null)warn('Null GraphQL/path nodes skipped');else yield* unpack(value,warn);
    }
  } else if(sequence && isObject(data) && !sequenceEnvelope(data)) {checkGraphql(data,warn);yield data;}
  else yield* unpack(data,warn);
}

function finishSelection(spec:ChartSpec,warn:Notice,state:PathState):void {
  if(spec.data_path===null)return;
  if(!state.matches && state.missing)throw new ValidationError(`data_path ${spec.data_path} did not match any input`);
  if(state.missing)warn('Data path branches with missing components skipped');
}

function flatten(value: unknown, warn: Notice,index:number): {row:DataRecord,cost:number} {
  if(!isObject(value)) value={index,value};
  const result: DataRecord={};
  let cost=2,fields=0;
  const seen=new Set<object>();
  const visit=(node: unknown, prefix: string, depth: number): void=> {
    if(depth>MAX_DEPTH) throw new ValidationError('Cyclic input or maximum nesting depth exceeded');
    if(prefix)stringBytes(prefix);
    if(Array.isArray(node)) {
      if(seen.has(node))throw new ValidationError('Cyclic input is not supported');
      seen.add(node);node.forEach((item,i)=>visit(item,`${prefix}.${i}`,depth+1));seen.delete(node);return;
    }
    if(isObject(node)) {
      if(seen.has(node)) throw new ValidationError('Cyclic input is not supported');
      if(Object.getPrototypeOf(node)!==Object.prototype && Object.getPrototypeOf(node)!==null) throw new ValidationError('Only plain JSON objects are supported');
      seen.add(node);
      for(const [key,item] of Object.entries(node)) { if(!key)throw new ValidationError('Record field names must be non-empty');stringBytes(key);safeKey(key); visit(item,prefix?`${prefix}.${key}`:key,depth+1); }
      seen.delete(node);
      return;
    }
    if(fields>=MAX_FIELDS) throw new ValidationError(`Record exceeds ${MAX_FIELDS} fields`);
    if(Object.hasOwn(result,prefix)) throw new ValidationError(`Colliding flattened field: ${prefix}`);
    let scalar: Scalar;
    if(typeof node==='number') {
      scalar=Number.isFinite(node)?node:null;
      if(scalar===null) warn('Non-finite numeric values replaced with null');
    } else if(typeof node==='string') {
      scalar=node;
    } else if(node===null || typeof node==='boolean') scalar=node;
    else throw new ValidationError(`Non-JSON value in field ${prefix}`);
    cost+=fieldBytes(prefix,scalar)+(fields++?1:0);
    checkRecordBytes(cost);
    result[prefix]=scalar;
  };
  visit(value,'',0);
  return {row:result,cost};
}

class Reducer {
  private records: {row:DataRecord,index:number,cost:number}[]=[];
  private groups=new Map<string,{row:DataRecord,count:number,value:number|null,correction:number,exponent:number,cost:number}>();
  private other:{row:DataRecord,count:number,value:number|null,correction:number,exponent:number,cost:number}|null=null;
  private warnings=new Set<string>();
  private count=0;
  private random=0x12345678;
  private retainedBytes=128;
  private prefix:{row:DataRecord,index:number,cost:number}[]=[];
  private strategy:Aggregation|null=null;
  private fields:string[]=[];
  private measure='count';
  private schema=new Map<string,number>();
  private missing=0;
  notice=(message:string):void=>{
    if(!this.warnings.has(message)) {this.reserve(stringBytes(message)+16);this.warnings.add(message);}
  };
  constructor(private spec: ChartSpec) {
    for(const key of [spec.x,spec.y,spec.color,spec.size,spec.data_path]) if(key) {stringBytes(key);safeKey(key);}
    if(spec.data_path!==null && spec.data_path.split('.').some(part=>!part)) throw new ValidationError('data_path must contain non-empty dot-separated components');
    if([spec.x,spec.y,spec.color,spec.size].some(key=>key!==null && !pythonStrip(key))) throw new ValidationError('Mapped field names must not be empty');
  }
  add(value: unknown): void {
    const flattened=flatten(value,this.notice,this.count),row=flattened.row;
    let cost=flattened.cost;
    const index=this.count++;
    if(!Number.isSafeInteger(this.count)) throw new ValidationError('Input count exceeds safe integer range');
    for(const [key,value] of Object.entries(row)) {
      const type=typeof value==='number'?1:typeof value==='string'?2:value===null?0:4;
      if(!this.schema.has(key)) {
        if(this.schema.size>=MAX_FIELDS)throw new ValidationError(`Input schema exceeds ${MAX_FIELDS} fields`);
        this.reserve(stringBytes(key)+16);
      }
      this.schema.set(key,(this.schema.get(key)??0)|type);
    }
    for(const field of [this.spec.x,this.spec.y,this.spec.color,this.spec.size]) {
      if(field!==null && !Object.hasOwn(row,field)) {
        cost+=fieldBytes(field,null)+(Object.keys(row).length?1:0);checkRecordBytes(cost);
        row[field]=null;this.missing++;
      }
    }
    cost+=64;
    if(this.strategy===null) {
      this.reserve(cost);
      this.prefix.push({row,index,cost});
      if(this.prefix.length===32) this.initialize();
    } else this.reduce(row,index,cost);
  }
  private initialize():void {
    const numeric:string[]=[],categorical:string[]=[];
    for(const {row} of this.prefix) for(const [key,value] of Object.entries(row)) {
      if(typeof value==='number') numeric.push(key);
      else if(typeof value==='string' || typeof value==='boolean') categorical.push(key);
    }
    this.strategy=this.spec.aggregation;
    if(this.spec.kind==='heatmap') {
      const coordinates=[...new Set(this.prefix.flatMap(({row})=>Object.keys(row).filter(key=>key!==this.spec.color)))];
      const x=this.spec.x??coordinates.find(key=>key!==this.spec.y)??null;
      const y=this.spec.y??coordinates.find(key=>key!==x)??null;
      this.fields=[...new Set([x,y].filter((field):field is string=>field!==null))];
      this.measure=this.spec.color??'count';
      if(this.strategy==='auto')this.strategy=this.spec.color!==null?'sum':'count';
      if(this.grouped()) {
        if(this.prefix.length && this.fields.length!==2)throw new ValidationError('Heatmaps require distinct x and y coordinate fields');
        if(this.strategy!=='count' && this.spec.color===null)throw new ValidationError('Numeric heatmap reductions require a color measure field');
      }
    } else {
      const scalar=this.prefix.length>0 && this.prefix.every(({row})=>Object.keys(row).length===2 && Object.hasOwn(row,'index') && Object.hasOwn(row,'value'));
      const x=this.spec.x??(scalar?(categorical.includes('value')&&!numeric.includes('value')?'value':null):categorical[0]??null);
      const y=this.spec.y??numeric.find(key=>key!==x && !(scalar && key==='index'))??null;
      if(this.strategy==='auto') this.strategy=['bar','pie','radar','treemap','sunburst','funnel'].includes(this.spec.kind) && x!==null && categorical.includes(x)?y!==null?'sum':'count':'none';
      this.fields=[...new Set([x,this.spec.color].filter((key):key is string=>key!==null))];
      this.measure=this.strategy==='count' && this.spec.y===null?'count':y??'count';
      if(['sum','mean','min','max'].includes(this.strategy) && y===null) throw new ValidationError(`${this.strategy} requires a numeric y field`);
    }
    if(this.grouped()) {
      if(this.fields.includes(this.measure)) throw new ValidationError('Reduction measure must differ from grouping fields');
      if(this.spec.size!==null && ![...this.fields,this.measure].includes(this.spec.size)) throw new ValidationError('Reduction would remove the size field; use aggregation sample or none');
    }
    while(this.prefix.length) {
      const {row,index,cost}=this.prefix.shift()!;
      this.retainedBytes-=cost;
      this.reduce(row,index,cost);
    }
  }
  private grouped():boolean {return this.strategy!==null && ['sum','mean','count','min','max'].includes(this.strategy);}
  private reduce(row:DataRecord,index:number,cost:number):void {
    const max_points=this.spec.max_points;
    if(this.grouped()) {
      const key=JSON.stringify(this.fields.map(field=>row[field]??null));
      let group=this.groups.get(key);
      if(!group) {
        if(this.other) group=this.other;
        else if(this.groups.size<max_points) {
          const record=Object.fromEntries(this.fields.map(field=>[field,row[field]??null])) as DataRecord;
          const keyCost=2+this.fields.reduce((bytes,field,i)=>bytes+scalarBytes(row[field]??null)+(i?1:0),0);
          const groupCost=recordBytes(record)+keyCost+stringBytes(this.measure)+26+128;
          this.reserve(groupCost);
          group={row:record,count:0,value:null,correction:0,exponent:0,cost:groupCost};this.groups.set(key,group);
        } else {
          const last=[...this.groups.keys()].at(-1)!;
          this.other=this.groups.get(last)!;this.groups.delete(last);group=this.other;
          this.notice(`Group cardinality exceeded max_points=${max_points}; first ${max_points-1} groups are exact and all remaining contributions form the final other bucket`);
        }
      }
      if(this.strategy==='count') {group.count++;group.value=group.count;return;}
      let value=row[this.measure];
      if(typeof value!=='number') {if(value!==null && value!==undefined)this.notice('Non-numeric measure values excluded from reduction');return;}
      group.count++;
      if(this.strategy==='mean' && group.exponent)value*=2**-group.exponent;
      if(group.value===null) group.value=value;
      else if(this.strategy==='sum' || this.strategy==='mean') {
        let previous=group.value,total=previous+value;
        if(this.strategy==='mean' && !Number.isFinite(total)) {
          // A finite mean can have an overflowing numerator: scale every term together.
          previous*=0.5;value*=0.5;group.correction*=0.5;group.exponent++;
          total=previous+value;
        }
        // Carry a bounded Neumaier correction with the group, including when it overflows into other.
        group.correction=Number.isFinite(total)?group.correction+(Math.abs(previous)>=Math.abs(value)?(previous-total)+value:(value-total)+previous):0;
        group.value=total;
      }
      else group.value=this.strategy==='min'?Math.min(group.value,value):this.strategy==='max'?Math.max(group.value,value):group.value+value;
      if(!Number.isFinite(group.value)) this.notice('Non-finite numeric values replaced with null');
      return;
    }
    if(this.records.length<max_points) { this.reserve(cost);this.records.push({row,index,cost}); }
    else {
      this.random^=this.random<<13; this.random^=this.random>>>17; this.random^=this.random<<5;
      const target=Math.floor((this.random>>>0)/4294967296*(index+1));
      if(target<max_points) { this.reserve(cost-this.records[target]!.cost);this.records[target]={row,index,cost}; }
    }
  }
  private reserve(bytes:number):void {
    if(this.retainedBytes+bytes>MAX_RETAINED_BYTES) throw new ValidationError('Retained normalized state exceeds 16 MiB UTF-8 JSON byte budget; lower max_points or reduce fields');
    this.retainedBytes+=bytes;
  }
  finish(): NormalizedData {
    if(this.strategy===null) this.initialize();
    for(const field of [this.spec.x,this.spec.y,this.spec.color,this.spec.size]) if(field!==null && this.count && !this.schema.has(field)) throw new ValidationError(`Requested field missing from input: ${field}`);
    if(this.missing) this.notice(`${this.missing} missing mapped field values filled with null`);
    const mixed=[...this.schema].filter(([,mask])=>(mask&1) && (mask&6)).map(([key])=>key);
    if(mixed.length)this.notice(mixed.reduce((bytes,key)=>bytes+key.length,0)>4096?
      `Fields contain mixed numeric/non-numeric values: ${mixed.length} fields (names omitted from byte-bounded metadata).`:
      `Fields contain mixed numeric/non-numeric values: ${mixed.join(', ')}.`);
    const {max_points}=this.spec;
    const grouped=this.grouped();
    if(!grouped && this.count>max_points) this.notice(`Deterministic reservoir sample: ${max_points} of ${this.count} records; max_points overrides aggregation=${this.spec.aggregation}`);
    const states=[...this.groups.values()];
    if(this.other) {
      let label='__deepviz_other__';
      const labels=new Set(states.flatMap(group=>Object.values(group.row)));
      while(labels.has(label)) label+='_';
      states.push({...this.other,row:Object.fromEntries(this.fields.map(field=>[field,label]))});
    }
    const records:DataRecord[]=[];
    if(grouped) {
      this.groups.clear();this.other=null;
      for(const group of states) {
        const value=group.value===null?null:this.strategy==='mean'?
          (group.value/group.count+group.correction/group.count)*2**group.exponent:
          group.value+(this.strategy==='sum'?group.correction:0);
        if(value!==null && !Number.isFinite(value))this.notice('Non-finite numeric values replaced with null');
        const row={...group.row,[this.measure]:value===null || !Number.isFinite(value)?null:value};
        this.reserve(recordBytes(row)+1-group.cost);records.push(row);
      }
    }
    return {
      records:grouped?records:this.records.sort((a,b)=>a.index-b.index).map(item=>item.row),
      input_count:this.count, warnings:[...this.warnings],
      strategy:grouped?this.strategy!:this.count>max_points?'sample':this.strategy==='sample'?'sample':'none',
    };
  }
}

/** Normalizes JSON-compatible values or text; max_points bounds retained rows. */
export function normalize(data: unknown, input: unknown = {}): NormalizedData {
  const spec=validateSpec(input);
  const reducer=new Reducer(spec);
  const state={matches:0,missing:0,empty:0};
  for(const row of typeof data==='string'?parseText(data,spec,reducer.notice,state):selected(data,spec,reducer.notice,state)) reducer.add(row);
  finishSelection(spec,reducer.notice,state);
  return reducer.finish();
}

/** Consume async records/pages incrementally. Text chunks are not a supported stream format. */
export async function normalizeStream(data: AsyncIterable<unknown> | Iterable<unknown>, input: unknown = {}): Promise<NormalizedData> {
  const spec=validateSpec(input);
  const reducer=new Reducer(spec);
  const state={matches:0,missing:0,empty:0};
  for await(const page of data) for(const row of selected(page,spec,reducer.notice,state,true)) reducer.add(row);
  finishSelection(spec,reducer.notice,state);
  return reducer.finish();
}
