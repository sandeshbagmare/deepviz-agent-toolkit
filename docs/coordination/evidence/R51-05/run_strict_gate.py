from __future__ import annotations
import hashlib, io, json, os, subprocess, sys, time
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from pathlib import Path

source=Path(r'C:\Users\bagma\AppData\Local\Temp\opencode\r51-05-antv-4429-ses_de567830effe0E5yIwQgDACLMD')
site=Path(r'C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages')
main=Path(r'C:\Users\bagma\deepviz-agent-toolkit')
commit='4429f0521612b97eee3790f0d8d0fbc3cad3f8be'
base=Path(r'C:\Users\bagma\AppData\Local\Temp\opencode\r51-05-antv-command-01-ses_de567830effe0E5yIwQgDACLMD')
assert not base.exists(), base
out=base/'pytest-temp'; base.mkdir(parents=True); out.mkdir()
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==commit
assert subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)==''
paths=['python/deepviz/src/deepviz/__init__.py','python/deepviz/src/deepviz/models.py','python/deepviz/src/deepviz/normalize.py','python/deepviz/src/deepviz/engines.py','python/deepviz/src/deepviz/render.py','python/deepviz/tests/test_r45_antv_subnormal_heatmap.py','tests/r45_probes/role17/native.cjs','python/deepviz/tests/test_r20_antv_color_scale.py']
def blob(p):return subprocess.check_output(['git','-C',str(source),'show',f'{commit}:{p}'])
def sha(b):return hashlib.sha256(b).hexdigest()
before={p:{'git_sha256':sha(blob(p)),'working_sha256':sha((source/p).read_bytes())} for p in paths}
asset=main/'node_modules/@antv/g2/dist/g2.min.js'; assert asset.is_file()
assetsha=sha(asset.read_bytes()); assert assetsha=='7e7d346cab68c002a889dc6145bfc1f9ae1391be82ce8d514fb106ef3a6e6412'
start=datetime.now(timezone.utc);clock=time.perf_counter(); stdout=io.StringIO();stderr=io.StringIO()
sys.path.insert(0,str(site));sys.path.insert(0,str(source/'python/deepviz/src'))
import pytest
args=['-q','-p','no:cacheprovider','--basetemp',str(out),str(source/'python/deepviz/tests/test_r45_antv_subnormal_heatmap.py')]
with redirect_stdout(stdout),redirect_stderr(stderr):
 result=pytest.main(args)
elapsed=time.perf_counter()-clock
(base/'stdout.txt').write_text(stdout.getvalue(),encoding='utf-8',newline='\n');(base/'stderr.txt').write_text(stderr.getvalue(),encoding='utf-8',newline='\n')
after={p:{'git_sha256':sha(blob(p)),'working_sha256':sha((source/p).read_bytes())} for p in paths}
assert before==after
assert assetsha==sha(asset.read_bytes())
status=subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
mods={name:{'path':__import__(name,fromlist=['']).__file__,'sha256':sha(Path(__import__(name,fromlist=['']).__file__).read_bytes())} for name in ['deepviz','deepviz.models','deepviz.engines','deepviz.render','deepviz.normalize']}
assert status==''
receipt={'utc_start':start.isoformat(),'utc_end':datetime.now(timezone.utc).isoformat(),'cwd':str(source),'argv':['python','-B','-S',str(Path(__file__).resolve()),'--pytest','-q -p no:cacheprovider --basetemp <owned> test_r45_antv_subnormal_heatmap.py'],'pytest_argv':args,'pytest_exit':int(result),'elapsed_seconds_including_runner':elapsed,'source_commit':commit,'pytest_root':str(source/'python/deepviz/tests/test_r45_antv_subnormal_heatmap.py'),'case_contract':'10 real-G2 tests; first four are original strict subnormal inputs and four original strict cell/color/grid/pixel conditions are asserted unchanged at test lines58-71; appended MAX/signed/zero controls are preserved.', 'before_after_tracked_bytes_equal':before==after,'source_status_after':status,'module_origins':mods,'G2_SHA256_before_after':assetsha,'stdout_file':str(base/'stdout.txt'),'stderr_file':str(base/'stderr.txt'),'artifact_root':str(out),'limitations':['Only this strict R45 10-case browser suite executed. Old role21 21-case/254-check suite not replayed; those remain separate producer evidence and tests were unmodified.','This is non-author tester evidence on the exact AntV source commit but not CI, merged main, all-engine or full-suite approval.']}
(base/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exit':int(result),'elapsed_seconds':elapsed,'source_clean':not status,'G2':assetsha,'modules':mods,'pytest_stdout':stdout.getvalue(),'pytest_stderr':stderr.getvalue(),'artifact_root':str(out)},indent=2))
raise SystemExit(int(result))
