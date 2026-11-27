"""Static identities from a FROZEN existing map. Never enumerate/fetch refs or run product tests."""
import hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
INPUT=Path(r'C:\Users\bagma\deepviz-agent-toolkit\docs\coordination\evidence\R29-release\branch-inventory.json')
raw=INPUT.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='540d45be07d62c30db87b8dfb6eb50dfccaf6d86dd85847b2df55a9dbc83a764'
data=json.loads(raw); assert len(data['branches'])==103 and len(data['tip_analyses'])==98
paths=sorted({p for x in data['tip_analyses'].values() for p in x['changed_product_paths']})
commands=[];units={};delta={}
def git(args):
    r=subprocess.run(['git',*args],capture_output=True,check=True)
    commands.append({'argv':['git',*args],'exit':r.returncode,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest()})
    return r.stdout

def add(path,blob,tip=None,history=None):
    if set(blob)=={'0'}: return None
    key=path+'@'+blob
    if key not in units:
        kind='code' if Path(path).suffix in {'.py','.ts','.mjs','.cjs','.js'} else 'contract/config/asset'
        units[key]={'id':key,'path':path,'git_blob':blob,'kind':kind,'frozen_tips':[],'history_commits':[],'full_file_reviews':[],'scoped_reviews':[],'coverage':'UNREVIEWED'}
    row=units[key]
    if tip and tip not in row['frozen_tips']:row['frozen_tips'].append(tip)
    if history and history not in row['history_commits']:row['history_commits'].append(history)
    return key

named=['31cff73ab057c3fed69bd400ac005f2f11609027','bff9384d1ebe5c8f6f8f0f994300264b32bb98d8','3185e0d9936c7d6f1a9d30b94089b804d75fe991','3eab699b61850a20e91132e16caf8c589085f9ee']
tips=sorted(set(data['tip_analyses'])|set(named));tip_units={}
for sha in tips:
    assert re.fullmatch('[0-9a-f]{40}',sha)
    rows=git(['ls-tree','-r',sha,'--',*paths]).decode().splitlines();keys=[]
    for line in rows:
        left,path=line.split('\t',1);mode,kind,blob=left.split()
        if kind=='blob':keys.append(add(path,blob,tip=sha))
    tip_units[sha]=keys

commits=sorted(set(data['product_commit_subjects'])|set(named))
for sha in commits:
    assert re.fullmatch('[0-9a-f]{40}',sha)
    parents=git(['show','-s','--format=%P',sha]).decode().strip().split()
    if not parents:continue
    rows=git(['diff','--raw','--no-abbrev',parents[0],sha,'--',*paths]).decode().splitlines()
    for line in rows:
        meta,*names=line.split('\t');oldmode,newmode,old,new,status=meta.split()
        path=names[-1];oldpath=names[0]
        oldkey=add(oldpath,old,history=sha);newkey=add(path,new,history=sha)
        key='|'.join([oldpath,path,old,new,status])
        if key not in delta:delta[key]={'id':key,'old_unit':oldkey,'new_unit':newkey,'status':status,'commits':[],'review_refs':[]}
        delta[key]['commits'].append(sha)

branches=[{'name':b['name'],'frozen_tip':b['tip_for_analysis'],'stored_disposition':b['disposition'],'units':tip_units[b['tip_for_analysis']]} for b in data['branches']]
result={'scope':'Existing103map ONLY; named exact supplied source/default pins are NOT new branches or a fresh inventory','input_sha256':hashlib.sha256(raw).hexdigest(),'input_observed_utc':data['observed_utc'],'original_default_sha':data['default_sha'],'named_pins':named,'paths':paths,'branches':branches,'tip_units':tip_units,'file_units':list(units.values()),'commit_diff_units':list(delta.values()),'commands':commands,'not_checked':'Live changed refs/dirty uncommitted producer files/missing later publications/complete all-branch review; no fetch/API/test/assignment'}
(HERE/'source-unit-identities.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen_branch_rows':len(branches),'frozen_tip_count':98,'named_total_pins':len(tips),'stored_product_paths':len(paths),'file_blob_units':len(units),'tip_file_blob_units':sum(bool(v['frozen_tips']) for v in units.values()),'dedup_commit_diff_units':len(delta),'product_commit_pins':len(commits),'local_Git_metadata_commands':len(commands),'exits_nonzero':0,'product_executions':0},indent=2))
