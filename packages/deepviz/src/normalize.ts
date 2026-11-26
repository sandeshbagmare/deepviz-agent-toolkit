import {isObject, safeKey, validateSpec, ValidationError} from './models.js';
import type {Aggregation, ChartSpec, DataRecord, NormalizedData, Scalar} from './models.js';

const MAX_FIELDS = 1000;
const MAX_TEXT = 10000;
const MAX_DEPTH = 32;
const MAX_RECORD_CHARS = 100_000;
const MAX_RETAINED_CHARS = 16_000_000;
const wrappers = ['edges','nodes','records','results','items','pages','data'];
const numericText = /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$/;

function* pathValues(value: unknown, parts: string[], depth = 0): Generator<unknown> {
  if (depth > MAX_DEPTH) throw new ValidationError('Data path exceeds maximum depth');
  if (!parts.length) { yield value; return; }
  if (Array.isArray(value)) {
    for (const item of value) yield* pathValues(item, parts, depth + 1);
    return;
  }
  const [head, ...tail] = parts;
  if (!isObject(value) || !head || !Object.hasOwn(value, head)) throw new ValidationError(`Missing data_path component: ${head}`);
  yield* pathValues(value[head], tail, depth + 1);
}

function hasCollection(value: unknown, depth = 0): boolean {
  if (depth > MAX_DEPTH) throw new ValidationError('Cyclic input or maximum nesting depth exceeded');
  if (Array.isArray(value)) return true;
  return isObject(value) && Object.values(value).some(item => hasCollection(item, depth + 1));
}

function* unpack(value: unknown, depth = 0): Generator<unknown> {
  if (depth > MAX_DEPTH) throw new ValidationError('Cyclic input or maximum nesting depth exceeded');
  if (Array.isArray(value)) {
    for (const row of value) {
      if (isObject(row) && Object.hasOwn(row,'node')) yield* unpack(row.node,depth+1);
      else if (isObject(row) && wrappers.some(key=>Object.hasOwn(row,key) && hasCollection(row[key]))) yield* unpack(row,depth+1);
      else yield row;
    }
    return;
  }
  if (isObject(value)) {
    for (const key of Object.keys(value)) safeKey(key);
    const entries=Object.entries(value);
    const arrays=entries.filter(([,item])=>Array.isArray(item));
    // A single array named "nodes" is a collection; other all-array objects are columns.
    if (entries.length && arrays.length===entries.length && !(entries.length===1 && wrappers.includes(entries[0]![0]))) {
      const length=(arrays[0]![1] as unknown[]).length;
      if (arrays.some(([,item])=>(item as unknown[]).length!==length)) throw new ValidationError('Column arrays must have equal length');
      if (arrays.every(([,items])=>(items as unknown[]).every(item=>!isObject(item) && !Array.isArray(item)))) {
        for(let i=0;i<length;i++) yield Object.fromEntries(arrays.map(([key,items])=>[key,(items as unknown[])[i]]));
        return;
      }
    }
    const preferred=entries.filter(([key,item])=>wrappers.includes(key) && hasCollection(item));
    const candidates=preferred.length ? preferred : entries.filter(([,item])=>hasCollection(item));
    if (candidates.length>1) throw new ValidationError('Ambiguous collections; set data_path');
    if (!preferred.length && candidates.length && entries.some(([,item])=>!isObject(item) && !Array.isArray(item))) throw new ValidationError('Record contains a nested array; select a collection with data_path');
    if (candidates.length===1) { yield* unpack(candidates[0]![1],depth+1); return; }
    yield value;
    return;
  }
  if (value===null || ['string','number','boolean'].includes(typeof value)) { yield {value}; return; }
  throw new ValidationError('Expected JSON records, columns, or a supported text format');
}

function* csvRows(text: string, delimiter: string): Generator<string[]> {
  let row: string[]=[], field='', quoted=false, closed=false;
  for(let i=0;i<text.length;i++) {
    const ch=text[i]!;
    if(quoted) {
      if(ch==='"' && text[i+1]==='"') { field+='"'; i++; }
      else if(ch==='"') { quoted=false; closed=true; }
      else field+=ch;
    } else if(ch==='"' && !field && !closed) quoted=true;
    else if(ch===delimiter) { row.push(field); field=''; closed=false; }
    else if(ch==='\n' || ch==='\r') {
      if(ch==='\r' && text[i+1]==='\n') i++;
      row.push(field);
      if(row.some(value=>value!=='')) yield row;
      row=[];field='';closed=false;
    } else {
      if(closed || ch==='"') throw new ValidationError('Malformed CSV quote');
      field+=ch;
    }
  }
  if(quoted) throw new ValidationError('Unclosed CSV quote');
  if(field || closed || row.length) { row.push(field); yield row; }
}

function* parseText(text: string, spec: ChartSpec): Generator<unknown> {
  let format=spec.format;
  if(format==='auto') format=/^\s*[\[{]/.test(text) ? 'json' : text.split(/\r?\n/,1)[0]?.includes('\t') ? 'tsv' : 'csv';
  if(format==='json') { yield* selected(JSON.parse(text),spec); return; }
  if(format==='jsonl') {
    // Match one line at a time rather than allocating an array of every line.
    for(const match of text.matchAll(/[^\r\n]+/g)) if(match[0].trim()) yield* selected(JSON.parse(match[0]),spec);
    return;
  }
  if(format!=='csv' && format!=='tsv') throw new ValidationError(`Unsupported ${format}; use an Arrow/Parquet adapter to supply records`);
  let header: string[]|undefined;
  for(const row of csvRows(text.replace(/^\uFEFF/,''),format==='tsv'?'\t':',')) {
    if(!header) {
      header=row;
      if(header.length>MAX_FIELDS || header.some(key=>!key) || new Set(header).size!==header.length) throw new ValidationError('CSV header must have unique non-empty names');
      header.forEach(safeKey);
    } else {
      if(row.length!==header.length) throw new ValidationError('CSV column count does not match header');
      yield Object.fromEntries(header.map((key,i)=> {
        const value=row[i]!;
        return [key, value===''?null:numericText.test(value) && Number.isFinite(Number(value))?Number(value):value];
      }));
    }
  }
}

function* selected(data: unknown, spec: ChartSpec): Generator<unknown> {
  if(spec.data_path) {
    safeKey(spec.data_path);
    for(const value of pathValues(data,spec.data_path.split('.'))) yield* unpack(value);
  } else yield* unpack(data);
}

function flatten(value: unknown, warn: (message: string)=>void): DataRecord {
  if(!isObject(value)) value={value};
  const result: DataRecord={};
  const seen=new Set<object>();
  const visit=(node: unknown, prefix: string, depth: number): void=> {
    if(depth>MAX_DEPTH) throw new ValidationError('Cyclic input or maximum nesting depth exceeded');
    if(isObject(node)) {
      if(seen.has(node)) throw new ValidationError('Cyclic input is not supported');
      if(Object.getPrototypeOf(node)!==Object.prototype && Object.getPrototypeOf(node)!==null) throw new ValidationError('Only plain JSON objects are supported');
      seen.add(node);
      for(const [key,item] of Object.entries(node)) { safeKey(key); visit(item,prefix?`${prefix}.${key}`:key,depth+1); }
      seen.delete(node);
      return;
    }
    if(Object.keys(result).length>=MAX_FIELDS) throw new ValidationError(`Record exceeds ${MAX_FIELDS} fields`);
    if(Object.hasOwn(result,prefix)) throw new ValidationError(`Colliding flattened field: ${prefix}`);
    let scalar: Scalar;
    if(Array.isArray(node)) throw new ValidationError(`Nested array at ${prefix}; select a collection using data_path`);
    if(typeof node==='number') {
      scalar=Number.isFinite(node)?node:null;
      if(scalar===null) warn('Non-finite numeric values replaced with null');
    } else if(typeof node==='string') {
      scalar=node.slice(0,MAX_TEXT);
      if(node.length>MAX_TEXT) warn(`Text fields truncated to ${MAX_TEXT} characters`);
    } else if(node===null || typeof node==='boolean') scalar=node;
    else throw new ValidationError(`Non-JSON value in field ${prefix}`);
    result[prefix]=scalar;
  };
  visit(value,'',0);
  return result;
}

class Reducer {
  private records: {row:DataRecord,index:number,cost:number}[]=[];
  private groups=new Map<string,{row:DataRecord,count:number,value:number|null,cost:number}>();
  private other:{row:DataRecord,count:number,value:number|null,cost:number}|null=null;
  private warnings=new Set<string>();
  private count=0;
  private random=0x12345678;
  private retainedChars=0;
  private prefix:{row:DataRecord,index:number,cost:number}[]=[];
  private strategy:Aggregation|null=null;
  private fields:string[]=[];
  private measure='count';
  private schema=new Set<string>();
  private missing=0;
  constructor(private spec: ChartSpec) {
    for(const key of [spec.x,spec.y,spec.color,spec.size,spec.data_path]) if(key) safeKey(key);
    if([spec.x,spec.y,spec.color,spec.size].some(key=>key!==null && !key.trim())) throw new ValidationError('Mapped field names must not be empty');
  }
  add(value: unknown): void {
    const row=flatten(value,message=>this.warnings.add(message));
    const cost=Object.entries(row).reduce((sum,[key,value])=>sum+key.length+String(value).length+8,0);
    if(cost>MAX_RECORD_CHARS) throw new ValidationError('Record exceeds 100,000-character budget; reduce fields or text');
    const index=this.count++;
    if(!Number.isSafeInteger(this.count)) throw new ValidationError('Input count exceeds safe integer range');
    for(const key of Object.keys(row)) this.schema.add(key);
    if(this.schema.size>MAX_FIELDS) throw new ValidationError(`Input schema exceeds ${MAX_FIELDS} fields`);
    for(const field of [this.spec.x,this.spec.y,this.spec.color,this.spec.size]) {
      if(field!==null && !Object.hasOwn(row,field)) {row[field]=null;this.missing++;}
    }
    if(this.strategy===null) {
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
    const scalar=this.prefix.length>0 && this.prefix.every(({row})=>Object.keys(row).length===2 && Object.hasOwn(row,'index') && Object.hasOwn(row,'value'));
    const x=this.spec.x??(scalar?(categorical.includes('value')&&!numeric.includes('value')?'value':null):categorical[0]??null);
    const y=this.spec.y??numeric.find(key=>key!==x && !(scalar && key==='index'))??null;
    this.strategy=this.spec.aggregation;
    if(this.strategy==='auto') this.strategy=['bar','pie','radar','treemap','sunburst','funnel','heatmap'].includes(this.spec.kind) && x!==null && categorical.includes(x)?y!==null?'sum':'count':'none';
    this.fields=[...new Set([x,this.spec.color].filter((key):key is string=>key!==null))];
    this.measure=this.strategy==='count' && this.spec.y===null?'count':y??'count';
    if(['sum','mean','min','max'].includes(this.strategy) && y===null) throw new ValidationError(`${this.strategy} requires a numeric y field`);
    if(this.grouped()) {
      if(this.fields.includes(this.measure)) throw new ValidationError('Reduction measure must differ from grouping fields');
      if(this.spec.size!==null && ![...this.fields,this.measure].includes(this.spec.size)) throw new ValidationError('Reduction would remove the size field; use aggregation sample or none');
    }
    for(const {row,index,cost} of this.prefix) this.reduce(row,index,cost);
    this.prefix=[];
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
          const groupCost=JSON.stringify(record).length+40;
          group={row:record,count:0,value:null,cost:groupCost};this.groups.set(key,group);
          this.retainedChars+=groupCost;this.checkBudget();
        } else {
          const last=[...this.groups.keys()].at(-1)!;
          this.other=this.groups.get(last)!;this.groups.delete(last);group=this.other;
          this.warnings.add(`Group cardinality exceeded max_points=${max_points}; first ${max_points-1} groups are exact and all remaining contributions form the final other bucket`);
        }
      }
      if(this.strategy==='count') {group.count++;group.value=group.count;return;}
      const value=row[this.measure];
      if(typeof value!=='number') {if(value!==null && value!==undefined)this.warnings.add('Non-numeric measure values excluded from reduction');return;}
      group.count++;
      if(group.value===null) group.value=value;
      else if(this.strategy==='mean') group.value=group.value*((group.count-1)/group.count)+value/group.count;
      else group.value=this.strategy==='min'?Math.min(group.value,value):this.strategy==='max'?Math.max(group.value,value):group.value+value;
      if(!Number.isFinite(group.value)) {group.value=null;this.warnings.add('Non-finite numeric values replaced with null');}
      return;
    }
    if(this.records.length<max_points) { this.records.push({row,index,cost});this.retainedChars+=cost; }
    else {
      this.random^=this.random<<13; this.random^=this.random>>>17; this.random^=this.random<<5;
      const target=Math.floor((this.random>>>0)/4294967296*(index+1));
      if(target<max_points) { this.retainedChars+=cost-this.records[target]!.cost;this.records[target]={row,index,cost}; }
    }
    this.checkBudget();
  }
  private checkBudget():void {
    if(this.retainedChars>MAX_RETAINED_CHARS) throw new ValidationError('Retained data exceeds 16 MB character budget; lower max_points or reduce fields');
  }
  finish(): NormalizedData {
    if(this.strategy===null) this.initialize();
    for(const field of [this.spec.x,this.spec.y,this.spec.color,this.spec.size]) if(field!==null && this.count && !this.schema.has(field)) throw new ValidationError(`Requested field missing from input: ${field}`);
    if(this.missing) this.warnings.add(`${this.missing} missing mapped field values filled with null`);
    const {max_points}=this.spec;
    const grouped=this.grouped();
    if(!grouped && this.count>max_points) this.warnings.add(`Deterministic reservoir sample: ${max_points} of ${this.count} records; max_points overrides aggregation=${this.spec.aggregation}`);
    const states=[...this.groups.values()];
    if(this.other) {
      let label='__deepviz_other__';
      const labels=new Set(states.flatMap(group=>Object.values(group.row)));
      while(labels.has(label)) label+='_';
      states.push({...this.other,row:Object.fromEntries(this.fields.map(field=>[field,label]))});
    }
    return {
      records:grouped?states.map(group=>({...group.row,[this.measure]:group.value})):
        this.records.sort((a,b)=>a.index-b.index).map(item=>item.row),
      input_count:this.count, warnings:[...this.warnings],
      strategy:grouped?this.strategy!:this.count>max_points?'sample':this.strategy==='sample'?'sample':'none',
    };
  }
}

/** Normalizes JSON-compatible values or text; max_points bounds retained rows. */
export function normalize(data: unknown, input: unknown = {}): NormalizedData {
  const spec=validateSpec(input);
  const reducer=new Reducer(spec);
  for(const row of typeof data==='string'?parseText(data,spec):selected(data,spec)) reducer.add(row);
  return reducer.finish();
}

/** Consume async records/pages incrementally. Text chunks are not a supported stream format. */
export async function normalizeStream(data: AsyncIterable<unknown> | Iterable<unknown>, input: unknown = {}): Promise<NormalizedData> {
  const spec=validateSpec(input);
  const reducer=new Reducer(spec);
  for await(const page of data) for(const row of selected(page,spec)) reducer.add(row);
  return reducer.finish();
}
