/** Finite caller-authored fixtures shared semantically with the Python probes. */
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';

export const corpus = JSON.parse(readFileSync(new URL('./corpus.json', import.meta.url), 'utf8'));
export const raw = {kind:'table', aggregation:'none', max_points:100};
export const clone = value => structuredClone(value);

export function connection(rows, key, finished=false) {
  return {[key]:key==='edges'?rows.map((node,index)=>({node,cursor:`opaque-${index}`})):rows,
    totalCount:987654321, pageInfo:{hasNextPage:!finished,endCursor:'same-cursor'}};
}
export const page = (rows,key,finished=false) => ({data:{feed:connection(rows,key,finished)}});

export function success(name) {
  const first = [clone(corpus.repeat),clone(corpus.repeat)];
  const tail = ['repeat','distinct','repeat'].map(key=>clone(corpus[key]));
  const modes = name==='mixed-auto'?['edges','nodes','edges']:name==='edges-auto'?['edges','edges','edges']:['nodes','nodes','nodes'];
  let pages = [page(first,modes[0],true),page([],modes[1]),page(tail,modes[2],true)];
  const spec = {...raw};
  let expected = clone(corpus.expected_five), notices = [];
  if(name==='nested-select') {
    pages = [first,[],tail].map(rows=>({data:{buckets:[{feed:connection(rows,'edges')}],
      shadow:{edges:[{cursor:'invalid-unselected'}]}}}));
    spec.data_path = 'data.buckets.feed.edges.node';
  } else if(name==='siblings-select') {
    for(const item of pages)item.data.shadow = {edges:[{cursor:'invalid-unselected'}]};
    spec.data_path = 'data.feed.nodes';
  } else if(name==='pages-envelope-select') {
    spec.data_path = 'pages.data.feed.nodes';
    return {data:{pages},spec,expected,notices};
  } else if(name==='warnings-late') {
    pages.at(-1).data.feed.nodes.push(null,null);
    pages.at(-1).errors = [{message:'unselected resolver unavailable'}];
    notices = ['null','graphql'];
  } else if(name==='missing-branch-select') {
    pages[1] = {data:{}};
    spec.data_path = 'data.feed.nodes';
    notices = ['missing'];
  } else if(name==='all-empty') {
    pages = ['edges','nodes','edges'].map(key=>page([],key));
    expected = [];
  }
  return {data:pages,spec,expected,notices};
}

export function lateFault(name, selected) {
  const pages = [page(Array.from({length:40},(_,index)=>({id:index,measure:index/4})),'nodes'),page([],'nodes')];
  const bad = name==='edge-without-node'?{data:{feed:{edges:[{cursor:'missing-node'}]}}}:
    name==='node-field-collision'?page([{'a.b':1,a:{b:2}}],'nodes'):
      {data:null,errors:[{message:'late page unavailable'}]};
  if(name==='error-only-no-data')delete bad.data;
  if(name==='error-only-empty-data')bad.data={};
  pages.push(bad);
  return {data:pages,spec:{...raw,...(selected?{data_path:'data.feed'}:{})}};
}

export function siblingPages(name) {
  const [key,variant] = name.split('-');
  const {data} = lateFault('node-field-collision',false);
  const bad = connection([{id:'selected-only'}],key);
  bad.audit = variant==='scalar'?7:{source:'must-not-disappear'};
  data[2] = {data:{feed:bad}};
  return data;
}

export class PullPages {
  constructor(values, poisonAfter=null) {
    this.values=values;this.poisonAfter=poisonAfter;this.pulled=[];this.finished=false;
  }
  async *[Symbol.asyncIterator]() {
    let index=0;
    while(true) {
      assert.ok(this.poisonAfter===null || index<this.poisonAfter,'overread a page after the invalid late node');
      if(index===this.values.length) {this.finished=true;return;}
      this.pulled.push(index);
      yield this.values[index++];
    }
  }
}
