from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path.cwd()
PARENT = '3185e0d9936c7d6f1a9d30b94089b804d75fe991'
HEAD = '4429f0521612b97eee3790f0d8d0fbc3cad3f8be'
paths = [
 'python/deepviz/src/deepviz/engines.py',
 'python/deepviz/src/deepviz/render.py',
 'python/deepviz/src/deepviz/models.py',
 'python/deepviz/src/deepviz/normalize.py',
 'python/deepviz/tests/test_backend_antv.py',
 'python/deepviz/tests/test_r45_antv_subnormal_heatmap.py',
 'tests/r45_probes/role17/native.cjs',
]
def run(*args: str) -> bytes:
 return subprocess.run(['git', *args], check=True, capture_output=True).stdout
def blob(rev: str, path: str) -> bytes:
 return run('cat-file','blob',f'{rev}:{path}')
def hash_entry(rev: str, path: str) -> dict:
 data=blob(rev,path)
 return {'git_blob':run('rev-parse',f'{rev}:{path}').decode().strip(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
manifest={}
for path in paths:
 manifest[path]={}
 for rev in (PARENT,HEAD):
  ok=subprocess.run(['git','cat-file','-e',f'{rev}:{path}'],capture_output=True).returncode==0
  if ok: manifest[path][rev]=hash_entry(rev,path)

base=Path('docs/coordination/evidence/R52-21')
proof=json.loads((base/'source-proof.json').read_text(encoding='utf-8'))
proof['exact_path_hashes']=manifest
proof['tree']={'parent':run('rev-parse',f'{PARENT}^{{tree}}').decode().strip() if False else run('rev-parse',f'{PARENT}^{{tree}}').decode().strip(),'head':run('rev-parse',f'{HEAD}^{{tree}}').decode().strip()}
proof['production_change_lines']={'engines.py':'694-712 target; 19 additions, no deletions; only _antv heatmap branch'}
proof['line_level_static_points']=[
 {'lines':'694-700','claim':'If high-low is non-finite, midpoint low/2 + high/2 and two adjacent segments replace one overflowing span; arithmetic proof for opposite finite extrema is finite.'},
 {'lines':'701-709','claim':'Unsafe native legend coordinate uses [0,1] while preserving original numeric labels and domainValue; this is native payload construction, not paint proof.'},
 {'lines':'710-712','claim':'Label length is capped by spec.width - 32; this source rule is not sufficient to guarantee two endpoint labels fit, and exact-head painted output independently found overlap at width 240.'},
]
(base/'source-proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')

dedup={
 'product_head':HEAD,'product_parent':PARENT,
 'source2_decision':'CLEAR_NARROWLY',
 'main_target':'AntV/renderer PR lane (planned PR4; PR number UNKNOWN)',
 'blocker_removed':'second non-author SOURCE2 gate for exact 4429 producer',
 'source_hashes':{
  'head_engines_sha256':manifest['python/deepviz/src/deepviz/engines.py'][HEAD]['sha256'],
  'parent_engines_sha256':manifest['python/deepviz/src/deepviz/engines.py'][PARENT]['sha256'],
  'head_engines_git_blob':manifest['python/deepviz/src/deepviz/engines.py'][HEAD]['git_blob'],
  'parent_engines_git_blob':manifest['python/deepviz/src/deepviz/engines.py'][PARENT]['git_blob'],
 },
 'deduplicated_native_scale_findings':[
  {'id':'R38-18-F1','source':'3185e0d9936c7d6f1a9d30b94089b804d75fe991','input':'[-MAX,0,+MAX]','observed':'G2 native Linear span Infinity; upper mapped color NaN; browser_runs=0','classification':'same finite-span arithmetic mechanism'},
  {'id':'R39-21-F1','source':'3185e0d9936c7d6f1a9d30b94089b804d75fe991','input':'[-1e308,+1e308]','observed':'G2 factory normalized endpoint NaN; one negative control passed; no full paint claim','classification':'same finite-span arithmetic mechanism; corroborating evidence, not a second issue'},
 ],
 'head_static_effect':{'source':'4429','input':'opposite-sign finite extrema','native_domain':'[low, low/2 + high/2, high]','native_range':'3 finite colors','proof':'for +/-MAX and +/-1e308 midpoint=0 and both segment spans finite; raw _heat values remain in data'},
 'separate_painted_finding':{
  'id':'R51-05-F1','source':HEAD,'input':'[-sys.float_info.max,+sys.float_info.max], width=240, height=520','observed':'real G2/Chromium output resolved with 2 marks and zero errors; endpoint labels overlap 98.98046875 px and right edge is 299.74609375 > canvas 240','classification':'distinct legend layout/paint defect; not native scale arithmetic and not waived by native static clearance'},
 'preserved_subnormal_finding':{'id':'R38-17-F1','source':'3185e0d9936c7d6f1a9d30b94089b804d75fe991','observed':'four finite subnormal heat values rendered zero G2 cells in published real output; internal cause remains unconfirmed','classification':'retained strict affected behavior; author 4429 results do not independently waive it'},
 'author_evidence_not_counted':{'producer':'4429','reported':'10/10 plus original4/4 and role21 254 checks','use':'context only; no author acceptance borrowed'},
 'limits':['No product import/test/native G2/browser/output execution in this SOURCE2 review.','No source, test oracle, issue, PR, merge, CI or default-branch action.','R51-05 independent browser evidence is read, not replayed.'],
}
(base/'dedup-disposition.json').write_text(json.dumps(dedup,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_proof':str(base/'source-proof.json'),'dedup':str(base/'dedup-disposition.json'),'engine_head':manifest['python/deepviz/src/deepviz/engines.py'][HEAD]},indent=2))
