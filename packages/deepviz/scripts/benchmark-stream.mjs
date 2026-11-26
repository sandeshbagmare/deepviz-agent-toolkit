import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {normalizeStream} from '../dist/index.js';

const source_commit=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
const results=[];
for(const size of [10,1000,100000,1000000,10000000]) {
  globalThis.gc?.();
  const baseline=process.memoryUsage();
  let peakHeap=baseline.heapUsed,peakRss=baseline.rss;
  function observe(){const current=process.memoryUsage();peakHeap=Math.max(peakHeap,current.heapUsed);peakRss=Math.max(peakRss,current.rss);}
  async function* source(){for(let x=0;x<size;x++){if(x%10000===0)observe();yield {x,y:x%1000};}}
  const started=performance.now();
  const result=await normalizeStream(source(),{kind:'line',x:'x',y:'y',aggregation:'sample',max_points:2000});
  const elapsed_ms=performance.now()-started;
  observe();
  assert.equal(result.input_count,size);
  assert.equal(result.records.length,Math.min(size,2000));
  assert.equal(result.strategy,'sample');
  results.push({input_count:size,output_count:result.records.length,strategy:result.strategy,elapsed_ms:Math.round(elapsed_ms*100)/100,baseline_heap_bytes:baseline.heapUsed,sampled_peak_heap_bytes:peakHeap,baseline_rss_bytes:baseline.rss,sampled_peak_rss_bytes:peakRss});
}
console.log(JSON.stringify({source_commit,node:process.version,platform:process.platform,arch:process.arch,memory_methodology:'One Node process, explicit GC before each scale; process.memoryUsage sampled every 10,000 yielded records and after reduction. RSS includes runtime and prior-scale allocation; peaks are sampled, not continuous or isolated-process maxima. No rendering included; source is an async generator, never an input array.',results},null,2));
