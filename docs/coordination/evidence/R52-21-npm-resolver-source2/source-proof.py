from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

ROOT=Path.cwd()
BASE='656f4f35e5e72d16cdb5ebf557b7d64607eaaa43'
DIRECT_PARENT='c1e1f20e92d69f44fedd9c7d9d272234d8e7d697'
RESOLVER='aa421822ea016b59cca674bdb547598c0c64d6d0'
TIP='ddd6ad527a7347cf0c601e88b71dec288206347c'
PATHS=['packages/deepviz/scripts/check-materialized-package.mjs','packages/deepviz/test/test_r40_foundation.test.mjs']
AUX_DOCS=['docs/agent-state/ses_de56782e6ffeVWDIuY3v01kkBt.md','docs/coordination/reports/R40-08-npm-foundation-implementation.md','docs/coordination/status/role08.md']
REQUESTED_PLURAL='packages/deepviz/tests/test_r40_foundation.test.mjs'

def git(*args:str,check=True):
    return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,text=True,check=check)
def blob(rev,path):
    b=subprocess.run(['git','cat-file','blob',f'{rev}:{path}'],cwd=ROOT,capture_output=True,check=True).stdout
    return b
def sha(b): return hashlib.sha256(b).hexdigest()
def path_id(rev,path):
    b=blob(rev,path)
    return {'blob':git('rev-parse',f'{rev}:{path}').stdout.strip(),'sha256':sha(b),'bytes':len(b)}

aa_parent=git('show','-s','--format=%P',RESOLVER).stdout.strip()
assert aa_parent==DIRECT_PARENT, f'expected exact resolver parent {DIRECT_PARENT}, got {aa_parent}'
assert git('merge-base','--is-ancestor',BASE,DIRECT_PARENT,check=False).returncode==0
assert git('merge-base','--is-ancestor',RESOLVER,TIP,check=False).returncode==0
changed=git('diff','--name-status',f'{RESOLVER}^',RESOLVER).stdout.splitlines()
expected={f'M\t{p}' for p in PATHS+AUX_DOCS}
assert set(changed)==expected, changed
product_changed=[line for line in changed if line.split('\t',1)[1] in PATHS]
assert set(product_changed)=={f'M\t{p}' for p in PATHS}
later=git('diff','--name-status',RESOLVER,TIP,'--',*PATHS).stdout.splitlines()
assert later==[], later
assert git('rev-list','--count',f'{RESOLVER}..{TIP}').stdout.strip()=='1'
assert subprocess.run(['git','cat-file','-e',f'{RESOLVER}:{REQUESTED_PLURAL}'],cwd=ROOT,capture_output=True).returncode!=0

source={p:{rev:path_id(rev,p) for rev in (BASE,DIRECT_PARENT,RESOLVER,TIP)} for p in PATHS}
CONNECTED=['package.json','package-lock.json','.github/workflows/npm-foundation.yml','packages/deepviz/scripts/check-package.mjs']
connected={p:path_id(TIP,p) for p in CONNECTED}
assert all(source[p][BASE]['blob']==source[p][DIRECT_PARENT]['blob'] for p in PATHS)
base_to_tip_paths=git('diff','--name-status',BASE,TIP,'--',*PATHS).stdout.splitlines()
assert set(base_to_tip_paths)=={f'M\t{p}' for p in PATHS}, base_to_tip_paths
checker_parent=blob(BASE,PATHS[0]).decode('utf-8')
checker_head=blob(RESOLVER,PATHS[0]).decode('utf-8')
test_parent=blob(BASE,PATHS[1]).decode('utf-8')
test_head=blob(RESOLVER,PATHS[1]).decode('utf-8')
old="fileURLToPath(import.meta.resolve('typescript/bin/tsc'))"
new="path.join(path.dirname(fileURLToPath(import.meta.resolve('typescript/package.json'))),'bin','tsc')"
assert old in checker_parent and old not in checker_head
assert new in checker_head and new in blob(TIP,PATHS[0]).decode('utf-8')
assert "import.meta.resolve('typescript/package.json')" not in test_parent
assert "import.meta.resolve('typescript/package.json')" in test_head and "import.meta.resolve('typescript/package.json')" in blob(TIP,PATHS[1]).decode('utf-8')

package=json.loads(blob(TIP,'package.json'))
lock=json.loads(blob(TIP,'package-lock.json'))
workflow=blob(TIP,'.github/workflows/npm-foundation.yml').decode('utf-8')
checker_tip=blob(TIP,PATHS[0]).decode('utf-8')
test_tip=blob(TIP,PATHS[1]).decode('utf-8')
check_package=blob(TIP,'packages/deepviz/scripts/check-package.mjs').decode('utf-8')
assert package['scripts']['package:materialized']=='node packages/deepviz/scripts/check-materialized-package.mjs'
assert package['devDependencies']['typescript']=='7.0.2'
lock_ts=lock['packages']['node_modules/typescript']
assert lock_ts['version']=='7.0.2' and lock_ts['bin']['tsc']=='bin/tsc'
assert "npm run package:materialized -- \"$RUNNER_TEMP/packed/deepviz-agent-toolkit-0.1.0.tgz\" \"$RUNNER_TEMP/consumer\"" in workflow
assert "node: ['22', '24']" in workflow
assert "assert.ok(checker.includes(\"import.meta.resolve('typescript/package.json')\")" in test_tip
tsc_direct= "node_modules/typescript/bin/tsc" in check_package
assert tsc_direct

# Read-only inspection of the already existing MAIN checkout's installed TypeScript package metadata.
installed_path=Path(r'C:\Users\bagma\deepviz-agent-toolkit\node_modules\typescript\package.json')
installed_info={'path':str(installed_path),'available':installed_path.is_file()}
if installed_path.is_file():
    installed_bytes=installed_path.read_bytes(); installed=json.loads(installed_bytes)
    installed_info.update({'sha256':sha(installed_bytes),'bytes':len(installed_bytes),'version':installed.get('version'),'exports_package_json':installed.get('exports',{}).get('./package.json'),'exports_keys':list(installed.get('exports',{}).keys()),'bin_tsc':installed.get('bin',{}).get('tsc')})
    installed_bin=installed_path.parent/'bin'/'tsc'
    installed_info['bin_file_exists']=installed_bin.is_file()
    if installed_bin.is_file(): installed_info.update({'bin_file_sha256':sha(installed_bin.read_bytes()),'bin_file_bytes':installed_bin.stat().st_size})
    assert installed['version']=='7.0.2'
    assert installed.get('exports',{}).get('./package.json')=='./package.json'
    assert installed.get('bin',{}).get('tsc')=='./bin/tsc'

result={
 'reviewer_actual_id':'ses_de5678018ffezK8JGDUaSzvcWn',
 'source_base':BASE,'resolver_commit':RESOLVER,'resolver_direct_parent':aa_parent,'published_tip':TIP,
 'published_tip_parent':git('show','-s','--format=%P',TIP).stdout.strip(),
 'resolver_is_ancestor_of_tip':True,'commits_after_resolver_to_tip':1,
 'resolver_commit_all_changed_paths':changed,'resolver_commit_product_paths':product_changed,'resolver_commit_auxiliary_documentation_paths':AUX_DOCS,'base_to_tip_reviewed_path_changes':base_to_tip_paths,'later_changes_to_reviewed_paths':later,
 'requested_plural_test_path':'not present at resolver commit; actual changed regression path is packages/deepviz/test/test_r40_foundation.test.mjs (singular test)',
 'paths':source,
 'connected_source_blobs_at_tip':connected,
 'line_references':{'checker':'packages/deepviz/scripts/check-materialized-package.mjs:9-10,15-21,101-107','regression':'packages/deepviz/test/test_r40_foundation.test.mjs:19-26','package_script':'package.json:12','typescript_dev_dependency':'package.json:24','typescript_lock_entry':'package-lock.json:'+str(next(i for i,line in enumerate(blob(TIP,'package-lock.json').decode('utf-8').splitlines(),1) if '"node_modules/typescript"' in line)),'workflow':'.github/workflows/npm-foundation.yml:18,25,35-36','sibling_package_check':'packages/deepviz/scripts/check-package.mjs:44'},
 'source_facts':{
   'parent_resolves_hidden_cli_subpath':old in checker_parent,
   'target_resolves_exported_package_json_then_bin_tsc':new in checker_head,
   'target_regression_assertion':"import.meta.resolve('typescript/package.json')" in test_head,
   'package_materialized_script':package['scripts']['package:materialized'],
   'workflow_node_matrix':['22','24'],'workflow_invokes_materialized_gate':True,
   'typescript_dev_dependency':package['devDependencies']['typescript'],
   'lock_typescript_version':lock_ts['version'],'lock_integrity':lock_ts['integrity'],'lock_bin':lock_ts['bin'],
   'sibling_package_check_uses_direct_filesystem_path':tsc_direct,
   'cached_MAIN_installed_package_metadata':installed_info,
 },
 'reviewed_behavior':{
   'resolution_base':'ESM checker module URL; import.meta.resolve applies Node package exports from that module location, not process.cwd()',
   'exact_locked_export':'TypeScript 7.0.2 package metadata explicitly maps ./package.json to ./package.json; bin metadata maps tsc to ./bin/tsc',
   'compiler_override':'optional third CLI argument remains path.resolve(compilerArg); workflow supplies only archive/output, so default metadata branch is used there',
   'failure':'resolution/file read failure enters existing catch, records passed=false/failure and rethrows; finally writes receipt; nonzero child status is asserted',
   'bounds':'existing spawnSync timeout=120000 ms and maxBuffer=8 MiB unchanged',
   'test_assertion':'strict source-string assertion guards the new resolver expression; actual materialized gate is invoked by Node 22/24 workflow, not exercised by this review',
 },
 'execution_limits':{'product_imports':0,'test_suites_run':0,'tests_passed':0,'tests_failed':0,'tests_skipped':0,'builds':0,'Node_runtime_probes':0,'network_or_install':False},
 'static_proof_assert_statement_count':sum(isinstance(n,__import__('ast').Assert) for n in __import__('ast').walk(__import__('ast').parse(Path(__file__).read_text(encoding='utf-8-sig')))),
 'scope':'static Git-blob/source review only; density implementation/tests intentionally excluded',
}
out=ROOT/'docs/coordination/evidence/R52-21-npm-resolver-source2/source-proof.json'
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
