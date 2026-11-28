from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT=Path.cwd(); PY=r'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe'
BASE='656f4f35e5e72d16cdb5ebf557b7d64607eaaa43'; DIRECT='c1e1f20e92d69f44fedd9c7d9d272234d8e7d697'; HEAD='aa421822ea016b59cca674bdb547598c0c64d6d0'; TIP='ddd6ad527a7347cf0c601e88b71dec288206347c'
paths=['packages/deepviz/scripts/check-materialized-package.mjs','packages/deepviz/test/test_r40_foundation.test.mjs']
checks=[]
def run(label,args,expected=0):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 checks.append({'label':label,'command':' '.join(args),'exit':p.returncode,'expected_exit':expected,'expectation_met':p.returncode==expected,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()})
 if p.returncode!=expected: raise RuntimeError(f'{label}: expected exit {expected}, observed {p.returncode}: {p.stderr}')
 return p
run('own working tree snapshot',['git','status','--short','--branch'])
run('own HEAD',['git','rev-parse','HEAD'])
run('resolver exact commit metadata',['git','show','-s','--format=%H%n%P%n%s',HEAD])
run('published package tip metadata',['git','show','-s','--format=%H%n%P%n%s',TIP])
run('resolver is ancestor of ddd tip',['git','merge-base','--is-ancestor',HEAD,TIP])
run('resolver parent to commit name-status',['git','diff','--name-status',f'{HEAD}^',HEAD])
run('package-base to published-tip target-path diff',['git','diff','--name-status',BASE,TIP,'--',*paths])
run('resolver to published-tip target-path diff',['git','diff','--name-status',HEAD,TIP,'--',*paths])
run('target-path diff whitespace check',['git','diff','--check',BASE,TIP,'--',*paths])
run('requested plural path absence',['git','cat-file','-e',f'{HEAD}:packages/deepviz/tests/test_r40_foundation.test.mjs'],expected=128)
run('static source hash ancestry/export proof',[PY,'-B','docs/coordination/evidence/R52-21-npm-resolver-source2/source-proof.py'])
result={'source_base':BASE,'resolver_commit':HEAD,'resolver_direct_parent':DIRECT,'published_package_tip':TIP,'checks':checks,'source_assert_statements_passed':24,'product_tests_run':0,'product_tests_passed':0,'product_tests_failed':0,'product_tests_skipped':0,'product_imports':0,'Node_runtime_probes':0,'builds':0,'CI_runs':0,'installs_or_network':0,'density_review_or_tests':0,'failed_preliminary_review_harness_attempts':[{'command':'python -B docs/coordination/evidence/R52-21-npm-resolver-source2/source-proof.py','exit':1,'cause':'initial expectation incorrectly assumed aa421 direct parent was package base 656f; actual direct parent is c1e1f20 docs checkpoint. Corrected to compare base, direct parent, resolver and tip.'},{'command':'python -B docs/coordination/evidence/R52-21-npm-resolver-source2/source-proof.py','exit':1,'cause':'initial source-proof expectation assumed entire resolver commit had exactly two changed paths; Git showed three documentation receipt paths in addition to the two reviewed package paths. Corrected proof records all five and isolates product paths.'},{'command':'python -B docs/coordination/evidence/R52-21-npm-resolver-source2/source-proof.py','exit':1,'cause':'initial base-to-tip filtered-path assertion reused the all-commit path set; corrected expectation to the two package paths.'},{'command':'Copy-Item scope.json to MAIN evidence directory','exit':'PowerShell path error','cause':'MAIN evidence subdirectory did not yet exist; created owned directory and copied successfully.'},{'command':'verification-results.py (plural path absence expected exit1)','exit':1,'cause':'Git cat-file -e reports missing path with exit128, not1; inventory corrected to assert observed missing-path exit128.'}]}
assert all(c['expectation_met'] for c in checks)
Path('docs/coordination/evidence/R52-21-npm-resolver-source2/verification-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
