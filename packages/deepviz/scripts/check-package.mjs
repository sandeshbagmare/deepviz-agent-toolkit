import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root=fileURLToPath(new URL('../../../',import.meta.url));
const packageDir=fileURLToPath(new URL('../',import.meta.url));
const scratch=path.join(packageDir,'.verify');
await mkdir(scratch,{recursive:true});
const work=await mkdtemp(path.join(scratch,'consumer-'));
function run(args,cwd=root) {
  const result=spawnSync(process.execPath,args,{cwd,encoding:'utf8',env:process.env});
  if(result.status!==0) throw new Error(`${args.join(' ')}\n${result.stdout}\n${result.stderr}`);
  return result.stdout;
}
try {
  assert.ok(process.env.npm_execpath,'Run this check through npm run package:check');
  const metadata=JSON.parse(run([process.env.npm_execpath,'pack','--json','--ignore-scripts','--workspace','@deepviz/agent-toolkit','--pack-destination',work]));
  const pack=metadata[0];
  for(const resource of ['README.md','LICENSE','dist/index.js','dist/index.d.ts','dist/chart-spec.schema.json']) assert.ok(pack.files.some(file=>file.path===resource),`Missing packed resource: ${resource}`);
  assert.ok(!pack.files.some(file=>file.path.startsWith('test/')||file.path.startsWith('src/')),'Do not publish test/source fixtures');
  const consumer=path.join(work,'consumer');
  await mkdir(consumer);
  await writeFile(path.join(consumer,'package.json'),JSON.stringify({name:'deepviz-packed-consumer',private:true,type:'module'}));
  run([process.env.npm_execpath,'install','--offline','--ignore-scripts','--no-audit','--no-fund','--workspaces=false','--package-lock=false',path.join(work,pack.filename)],consumer);
  await writeFile(path.join(consumer,'main.mjs'),`import assert from 'node:assert/strict';
import {render,normalize,validateSpec,chartSpecSchema} from '@deepviz/agent-toolkit';
import schema from '@deepviz/agent-toolkit/chart-spec.schema.json' with {type:'json'};
assert.deepEqual(schema,chartSpecSchema);
assert.equal(validateSpec({}).version,1);
assert.deepEqual(normalize({x:['A'],y:[2]}).records,[{x:'A',y:2}]);
const chart=render([{x:'A',y:2}],{x:'x',y:'y'},'svg');
assert.equal(chart.output_count,1);assert.ok(chart.html.includes('<svg'));
`);
  run([path.join(consumer,'main.mjs')],consumer);
  await writeFile(path.join(consumer,'types.mts'),`import {render,normalizeStream,type ChartSpecInput,type HtmlArtifact} from '@deepviz/agent-toolkit';
const spec:ChartSpecInput={kind:'bar',x:'x',y:'y'};
const artifact:HtmlArtifact=render([{x:'A',y:2}],spec,'svg');
const records=await normalizeStream((async function*(){yield {x:1};})());
console.log(artifact.html,records.input_count);
`);
  await writeFile(path.join(consumer,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,noEmit:true,module:'NodeNext',target:'ES2022',skipLibCheck:true},include:['types.mts']}));
  run([path.join(root,'node_modules/typescript/bin/tsc'),'--project',path.join(consumer,'tsconfig.json')],consumer);
  console.log(`Packed consumer passed: ESM, JSON schema, runtime, and TypeScript declarations (${pack.files.length} packed files, ${pack.size} bytes).`);
} finally {await rm(work,{recursive:true,force:true});}
