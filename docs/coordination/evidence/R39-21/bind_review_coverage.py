"""Bind scoped, actually read reports to exact source bytes; never promote metadata to approval."""
import ast,collections,hashlib,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
MAIN=Path(r'C:\Users\bagma\deepviz-agent-toolkit')
D=json.loads((H/'source-unit-identities.json').read_text());S=json.loads((H/'review-scope-specifications.json').read_text())
commands=[];cache={};evidence=[]
def git(args):
    r=subprocess.run(['git',*args],capture_output=True,check=True)
    commands.append({'argv':['git',*args],'exit':r.returncode,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest()})
    return r.stdout

def source(pin,path):
    key=(pin,path)
    if key not in cache:cache[key]=git(['show',pin+':'+path])
    return cache[key]
def functions(raw):
    lines=raw.splitlines(keepends=True);result={};tree=ast.parse(raw.decode())
    for f in tree.body:
        if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)):
            result[f.name]=(f.lineno,f.end_lineno,hashlib.sha256(b''.join(lines[f.lineno-1:f.end_lineno])).hexdigest())
        elif isinstance(f,ast.ClassDef):
            for m in f.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    result[f.name+'.'+m.name]=(m.lineno,m.end_lineno,hashlib.sha256(b''.join(lines[m.lineno-1:m.end_lineno])).hexdigest())
    return result

def feature(path):
    if path.endswith('tools.py') or path.endswith('mcp_server.py'):
        return ['tools/MCP feature after usable Python normalize/render/package','R22-02-F1 callback repair + resource/transport final-head gates']
    if path.endswith('recommend.py'):
        return ['recommend/profile + connected CLI/tool feature','usable Python foundation/contract/render imports and source-specific tools boundaries']
    if path.startswith('packages/') or path in {'package.json','package-lock.json'}:
        return ['existing R40 complete usable npm foundation','schema composition prerequisite; sole normalizer/SVG producer pins; helper/prompts and real packed-consumer/CI gates']
    if path.endswith('models.py') or path.startswith('schemas/') or path.endswith('chart-contract.yml') or path.endswith('export_schema.py'):
        return ['contract PR33 only exactbff/main31cff shipped; other contract units NOT approved','preserve repaired Mapping guard; R04 composition/schema728 successor needs own exact-head gates']
    if path.endswith('normalize.py'):
        return ['existing Python bounded-ingestion/package foundation','chosen frozen numerical/ownership/GraphQL/scalar/prefix fixes; independent final-head/package/CI gates']
    if path.endswith(('engines.py','render.py','cli.py')) or 'LICENSE' in path:
        return ['dependency-complete Python static/native/HTML rendering + CLI feature slices','normalization/package closure; COUNT/dense/literal/security + AntV F1s; no whole-file historical merge']
    return ['existing R29 release validation/package/docs dependency','R04 dispositions exact useful source scope; metadata/assets are not code-reviewed by inheritance']

for spec in S:
    mainraw=(MAIN/spec['report']).read_bytes();rec={**spec,'FULL_MAIN_report_read_by_role21':True,'MAIN_report_sha256':hashlib.sha256(mainraw).hexdigest(),'MAIN_report_lines':len(mainraw.splitlines()),'bindings':[]}
    if spec['published_report_commit']:
        published=git(['show',spec['published_report_commit']+':'+spec['report']]);rec['published_report_sha256']=hashlib.sha256(published).hexdigest();rec['published_report_blob']=git(['rev-parse',spec['published_report_commit']+':'+spec['report']]).decode().strip();rec['MAIN_equals_published_report']=mainraw==published;rec['publication_basis']='Historical actual nonforce/exact-readback receipt in FULL report, not a fresh remote check; MAIN may append receipt'
    else:rec['publication_basis']='THIS task actual source review; own meaningful publication pending, no invented SHA'
    paths=set(spec['full_files'])|set(spec['scoped_paths'])|set(spec['functions'])
    for path in paths:
        raw=source(spec['target_source'],path);blob=git(['rev-parse',spec['target_source']+':'+path]).decode().strip()
        binding={'path':path,'blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'scope':'FULL_FILE' if path in spec['full_files'] else spec['scoped_paths'].get(path,'FUNCTION_UNITS'),'function_units':{}}
        wanted=spec['functions'].get(path,[])
        if wanted:
            fs=functions(raw)
            for name in wanted:
                assert name in fs,(spec['id'],name)
                start,end,sha=fs[name];binding['function_units'][name]={'start':start,'end':end,'sha256':sha}
        rec['bindings'].append(binding)
        for unit in D['file_units']:
            if unit['path']!=path:continue
            if unit['git_blob']==blob:
                ref={'id':spec['id'],'target_source':spec['target_source'],'exact_file_blob':True,'scope':binding['scope'],'function_units':binding['function_units'],'findings':spec['findings'],'context':'ONLY described scope; no final-head/whole-branch acceptance'}
                unit['full_file_reviews' if path in spec['full_files'] else 'scoped_reviews'].append(ref)
            elif wanted:
                other=git(['cat-file','blob',unit['git_blob']]);fs=functions(other);matches={}
                for name,target in binding['function_units'].items():
                    if name in fs and fs[name][2]==target['sha256']:matches[name]={'start':fs[name][0],'end':fs[name][1],'sha256':fs[name][2]}
                if matches:
                    findings=spec['findings'] if spec['id']!='R39-own-AntV' or '_antv' in matches else []
                    unit['scoped_reviews'].append({'id':spec['id'],'target_source':spec['target_source'],'exact_file_blob':False,'exact_function_bytes':matches,'findings':findings,'context':'RAW function bytes equal ONLY; changed file/callers/dependencies need affected gates; NOT whole-file approval'})
    evidence.append(rec)

for unit in D['file_units']:
    unit['coverage']='FULL_FILE_SOURCE_REVIEW_EXISTS_NOT_RELEASE_APPROVAL' if unit['full_file_reviews'] else 'SCOPED_SOURCE_REVIEW_EXISTS_NOT_FULL_FILE' if unit['scoped_reviews'] else 'UNREVIEWED'
    unit['required_feature_PR_and_dependencies']=feature(unit['path']);unit['decision_owner']='R04 sole manager; ledger is NOT an assignment'
    unit['historical_only']=not bool(unit['frozen_tips'])
byid={u['id']:u for u in D['file_units']}
for row in D['commit_diff_units']:
    unit=byid.get(row['new_unit']);row['review_refs']=sorted({r['id'] for r in (unit['full_file_reviews']+unit['scoped_reviews']) if r['target_source'] in row['commits']}) if unit else []
    row['scope_limit']='A named source review of this commit/change ONLY; not whole file/history or final assembly approval'
D['review_evidence']=evidence;D['coverage_binding_commands']=commands
D['coverage_counts']=dict(collections.Counter(u['coverage'] for u in D['file_units']))
D['limitations']=['103 is the existing frozen branch map, NOT live branch count','43 stored product/config/asset paths; test-only/original oracles are not this source universe','116fileblobs include historical-only endpoints; those are preserved, not silently shipped or approved','FULLread of a report is NOT re-review of every source file; scoped context remains partial','Source/byte equality transfers ONLY described scope, never tests/CI/approval to a changed context','Unread/unmapped reviews remain UNREVIEWED here; no claim that no external report exists','Root has separate live status inventory; it is metadata, NOT this source-coverage gate','R04 alone selects needed feature PRs/dependency order/source grants/merges']
(H/'source-review-coverage.json').write_text(json.dumps(D,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file_units':len(D['file_units']),'coverage_counts':D['coverage_counts'],'actual_FULL_source_reports_read':len(evidence),'local_binding_Git_reads':len(commands),'runtime_or_baseline_replays':0},indent=2))
