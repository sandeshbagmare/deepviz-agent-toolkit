from __future__ import annotations
import ast, hashlib, json, subprocess
from pathlib import Path
source=Path(r'C:\Users\bagma\AppData\Local\Temp\opencode\r51-05-antv-4429-ses_de567830effe0E5yIwQgDACLMD'); out=Path.cwd()/r'docs/coordination/evidence/R51-05'; commit='4429f0521612b97eee3790f0d8d0fbc3cad3f8be'; parent=commit+'^'
def run(*args):return subprocess.check_output(['git','-C',str(source),*args],text=True)
def blob(path,rev):return subprocess.check_output(['git','-C',str(source),'show',f'{rev}:{path}'])
def sha(b):return hashlib.sha256(b).hexdigest()
changed=run('diff','--name-status',parent,commit).splitlines();assert set(changed)=={'M\tpython/deepviz/src/deepviz/engines.py','A\tpython/deepviz/tests/test_r45_antv_subnormal_heatmap.py','A\ttests/r45_probes/role17/native.cjs'},changed
eng='python/deepviz/src/deepviz/engines.py'; old=blob(eng,parent); new=blob(eng,commit)
def fmap(b):
 lines=b.decode().splitlines(keepends=True);tree=ast.parse(''.join(lines)); d={}
 for n in tree.body:
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
   a=n.lineno-1;z=n.end_lineno;d[n.name]=''.join(lines[a:z])
 return d
om,nm=fmap(old),fmap(new);assert set(om)==set(nm)
protected={k:{'same':om[k]==nm[k],'old_sha256':sha(om[k].encode()),'new_sha256':sha(nm[k].encode())} for k in sorted(nm) if k!='_antv'}; assert all(v['same'] for v in protected.values())
connected=['python/deepviz/src/deepviz/render.py','python/deepviz/src/deepviz/models.py','python/deepviz/src/deepviz/normalize.py'];assert all(blob(p,commit)==blob(p,parent) for p in connected)
diff=run('diff','--no-ext-diff','--unified=0',parent,commit).splitlines(); prod_added=[x[1:] for x in diff if x.startswith('+') and not x.startswith('+++') and 'python/deepviz/src/deepviz/engines.py' in x]
# Restrict token checks to the new production hunk only; probes legitimately invoke subprocesses.
for token in ('eval(', 'exec(', 'subprocess', 'os.system', 'open(', '<script', 'http://', 'https://'):
 assert not any(token in line for line in prod_added),token
out.mkdir(parents=True,exist_ok=True);proof={'source_commit':commit,'parent_commit':run('rev-parse',parent).strip(),'tree_clean':not bool(run('status','--short')),'changed_paths':changed,'engines_blob_sha256':{'parent':sha(old),'product':sha(new)},'protected_top_level_functions':protected,'unchanged_connected_blobs':{p:sha(blob(p,commit)) for p in connected},'added_production_lines':prod_added,'forbidden_added_production_token_scan':{'tokens':['eval(','exec(','subprocess','os.system','open(','<script','http://','https://'],'matches':[]},'review_scope':'_antv delta and its stable call path only','static_disposition':'No material source finding in reviewed delta; relies on fresh non-author strict G2 output acceptance for behavior.'}
(out/'source-review.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');(out/'source-diff.patch').write_text(run('diff','--no-ext-diff','--unified=80',parent,commit),encoding='utf-8');(out/'source-review-command.json').write_text(json.dumps({'cwd':str(source),'argv':['python','-B','-S','R51-05/evidence/source_review.py'],'exit':0,'checked':commit,'protected_functions_compared':len(protected)},indent=2)+'\n')
print(json.dumps({'exit':0,'commit':commit,'changed_paths':changed,'protected_functions_compared':len(protected),'unchanged_connected_blobs':len(connected),'production_token_matches':0},indent=2))
