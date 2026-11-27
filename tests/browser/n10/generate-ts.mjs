import {readFile, mkdir, writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {render} from '../../../packages/deepviz/dist/index.js';

const root=fileURLToPath(new URL('../../../',import.meta.url));
const out=path.join(root,'artifacts/local/N10');
const cases=JSON.parse(await readFile(new URL('./cases.json',import.meta.url),'utf8'));
const identity={source_sha:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),node:process.version,
  git_status:execFileSync('git',['status','--short'],{cwd:root,encoding:'utf8'}),
  schema_sha256:createHash('sha256').update(await readFile(path.join(root,'schemas/chart-spec.schema.json'))).digest('hex')};
const assets={vega:'/assets/vega.js',vegaLite:'/assets/vegaLite.js',vegaEmbed:'/assets/vegaEmbed.js',echarts:'/assets/echarts.js',antv:'/assets/antv.js',plotly:'/assets/plotly.js'};
const results=[];
await mkdir(out,{recursive:true});
for(const engine of ['svg','vega','echarts','antv','plotly']) for(const c of cases) {
  const spec={title:`N10 TypeScript ${engine} ${c.id}`,width:800,height:460,aggregation:'none',...c.spec};
  const item={id:`ts-${engine}-${c.id}`,language:'typescript',engine,case:c.id,spec,input:c.data,oracle:c.oracle};
  if(engine==='svg' && c.id==='heatmap') {item.status='unsupported-explicit';item.reason='Native SVG heatmap is not an advertised supported chart.';results.push(item);continue;}
  try {
    const online=render(c.data,spec,engine);
    const local=render(c.data,spec,engine,{assets});
    const relative=`typescript/${engine}/${c.id}`;
    await mkdir(path.join(out,relative),{recursive:true});
    await writeFile(path.join(out,relative,'default.html'),online.html);
    await writeFile(path.join(out,relative,'local-assets.html'),local.html);
    item.path=`${relative}/default.html`;
    item.local_path=`${relative}/local-assets.html`;
    item.renderer_spec=online.renderer_spec;
    item.status='generated-not-accepted';
  } catch(error) {item.status='generation-failed';item.error=String(error);}
  results.push(item);
  console.log(item.id,item.status,item.error??'');
}
await writeFile(path.join(out,'typescript-manifest.json'),JSON.stringify({identity,cases:results},null,2));
process.exitCode=Number(results.some(item=>item.status==='generation-failed'));
