// Actual pinned native payload -> existing G2 dependency. Not a browser/CI claim.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createRequire}=require('node:module');
const home=__dirname,main=String.raw`C:\Users\bagma\deepviz-agent-toolkit`;
const g2Package=path.join(main,'node_modules/@antv/g2/package.json');
const req=createRequire(g2Package),makeScale=req('@antv/g2/lib/scale/linear').Linear;
const scalePackage=req.resolve('@antv/scale/package.json');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const dependencies=[g2Package,scalePackage,req.resolve('@antv/g2/lib/scale/linear'),...['scales/linear.js','scales/continuous.js','utils/normalize.js'].map(n=>path.join(path.dirname(scalePackage),'lib',n))];
const before=Object.fromEntries(dependencies.map(p=>[p,hash(p)]));
const inputPath=path.join(home,'native-extent-inputs.json'),input=JSON.parse(fs.readFileSync(inputPath,'utf8'));
const cases=input.cases.map(c=>{
  const config=c.native.scale.color;
  const numeric=makeScale({...config,range:[0,1]});
  const color=makeScale(config);
  const mapped=c.literal_values.map(x=>numeric.map(x)),colors=c.literal_values.map(x=>color.map(x));
  const passed=mapped[0]===0 && mapped[1]===1 && mapped.every(Number.isFinite) && colors[0]!==colors[1];
  return {name:c.name,literal_values:c.literal_values,domain:config.domain,
    mapped:mapped.map(x=>Number.isFinite(x)?x:String(x)),colors,passed};
});
const after=Object.fromEntries(dependencies.map(p=>[p,hash(p)]));
if(JSON.stringify(before)!==JSON.stringify(after)) throw Error('Installed dependency bytes changed');
const result={source_commit:input.source_commit,node:process.version,executable:process.execPath,
  g2_version:JSON.parse(fs.readFileSync(g2Package)).version,scale_version:JSON.parse(fs.readFileSync(scalePackage)).version,
  native_input_sha256:hash(inputPath),dependency_before:before,dependency_after:after,cases,
  counts:{cases:cases.length,passed:cases.filter(c=>c.passed).length,failed:cases.filter(c=>!c.passed).length,skipped:0},
  limits:'Actual existing G2 scale dependency with actual frozen adapter payload; NOT full G2 browser/paint/254 tests'};
fs.writeFileSync(path.join(home,'extent-scale-counterexample.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));process.exitCode=result.counts.failed?1:0;
