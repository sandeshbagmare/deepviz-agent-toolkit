from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import traceback
from collections import Counter
from pathlib import Path

TARGET='96b819aee5b01ba88b5a609b587331a528aaa070'
PARENT='546c25ea75ee9d8a41b3832aa639664bc9a683b5'
root=Path(__file__).parent
source_root=root/'source-96b819'
shutil.rmtree(source_root, ignore_errors=True)
source_root.mkdir()
archive=subprocess.run(['git','archive','--format=tar',TARGET,'python/deepviz/src/deepviz'],check=True,capture_output=True).stdout
with tarfile.open(fileobj=__import__('io').BytesIO(archive), mode='r:') as tf:
    tf.extractall(source_root)
package_root=source_root/'python/deepviz/src'
sys.path.insert(0,str(package_root))
import deepviz
from deepviz import normalize
normalizer=__import__('importlib').import_module('deepviz.normalize')
orig_limit=sys.get_int_max_str_digits()
results=[]
def case(name, fn):
    try:
        value=fn(); results.append({'name':name,'status':'PASS','detail':value})
    except Exception as exc:
        results.append({'name':name,'status':'FAIL','error_type':type(exc).__name__,'error':str(exc),'traceback_tail':traceback.format_exc().splitlines()[-5:]})

def wide_cancel():
    n=10**3900
    out=normalize([{'g':'one','v':n},{'g':'one','v':-n}], {'x':'g','y':'v','aggregation':'mean','max_points':10})
    assert out.records == [{'g':'one','v':0.0}]
    assert out.input_count == 2 and out.warnings == []
    assert sys.get_int_max_str_digits()==orig_limit
    return {'records':out.records,'input_count':out.input_count}
case('wide_integer_mean_cancellation',wide_cancel)

def wide_sum_float_mix():
    n=10**3900
    out=normalize([{'g':'one','v':n},{'g':'one','v':0.0},{'g':'one','v':-n}], {'x':'g','y':'v','aggregation':'sum'})
    assert out.records == [{'g':'one','v':0.0}]
    return {'records':out.records}
case('wide_integer_sum_float_cancellation',wide_sum_float_mix)

def large_float_sum():
    out=normalize(iter([{'g':'one','v':1e308},{'g':'one','v':1e308},{'g':'one','v':-1e308}]), {'x':'g','y':'v','aggregation':'sum'})
    assert out.records == [{'g':'one','v':1e308}]
    assert out.warnings == []
    return {'records':out.records}
case('finite_large_float_sum',large_float_sum)

def one_pass():
    class Once:
        def __init__(self): self.calls=0; self.rows=[{'g':'one','v':2},{'g':'one','v':4}]
        def __iter__(self):
            if self.calls: raise AssertionError('replayed')
            self.calls += 1
            yield from self.rows
    rows=Once(); out=normalize(rows, {'x':'g','y':'v','aggregation':'mean'})
    assert rows.calls==1 and out.records==[{'g':'one','v':3.0}]
    return {'calls':rows.calls,'records':out.records}
case('one_pass_input',one_pass)

def bool_count():
    out=normalize([{'g':'one','v':True},{'g':'one','v':False}], {'x':'g','y':'v','aggregation':'count'})
    assert out.records == [{'g':'one','v':2}] and out.warnings==[]
    return {'records':out.records}
case('bool_count_path',bool_count)

def float_fallback():
    out=normalize([{'g':'one','v':0.5},{'g':'one','v':1.5}], {'x':'g','y':'v','aggregation':'mean'})
    assert out.records == [{'g':'one','v':1.0}]
    return {'records':out.records}
case('ordinary_float_state',float_fallback)

def unsupported_value():
    try:
        normalize([{'g':'one','v':object()}], {'x':'g','y':'v','aggregation':'mean'})
    except TypeError as exc:
        assert 'Unsupported record value' in str(exc)
        return {'error':str(exc)}
    raise AssertionError('unsupported object unexpectedly accepted')
case('unsupported_private_input_rejection',unsupported_value)

def bound_small():
    vals=[0,1,7,8,9,10,99,100,10**100,-1,-10,-(10**100)]
    checks=[]
    for n in vals:
        expected=len(str(abs(n)))+(1 if n<0 else 0)
        got=normalizer._state_number_bytes(n)
        assert got>=expected,(n,got,expected)
        checks.append([n if abs(n)<1000 else ('negative' if n<0 else 'positive'),got,expected])
    return {'checks':checks}
case('independent_small_decimal_upper_bound',bound_small)

def charge_release():
    r=normalizer._Reducer('mean',['g'],'v',10,Counter())
    r.add({'g':'one','v':0})
    state=next(iter(r.groups.values())); before=state.copy(); base=r.retained_bytes
    n=10**3900
    units=normalizer._sum_units(n)
    r._store(state,units,exponent=-1074)
    charged=r.retained_bytes
    assert charged>base and state[1] is units
    r._store(state,0,exponent=-1074)
    assert r.retained_bytes==base and state==before
    assert r.finish()==[{'g':'one','v':0.0}]
    return {'base':base,'charged':charged,'released':r.retained_bytes}
case('wide_private_charge_release',charge_release)

# exact Git object identities and connected source structure
paths=['python/deepviz/src/deepviz/normalize.py','python/deepviz/tests/test_r45_numeric_state_accounting.py']
ident=[]
for path in paths:
    blob=subprocess.run(['git','rev-parse',f'{TARGET}:{path}'],check=True,capture_output=True,text=True).stdout.strip()
    raw=subprocess.run(['git','cat-file','blob',f'{TARGET}:{path}'],check=True,capture_output=True).stdout
    ident.append({'path':path,'blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
source_text=(source_root/'python/deepviz/src/deepviz/normalize.py').read_text(encoding='utf-8')
assert 'def _state_number_bytes' in source_text and 'value.bit_length() // 3 + 1' in source_text
assert 'sys.set_int_max_str_digits' not in source_text
summary={'target':TARGET,'parent':PARENT,'module_origins':{'deepviz':deepviz.__file__,'normalize':normalizer.__file__},'source_identity':ident,'cases':results,'counts':{'cases':len(results),'passed':sum(r['status']=='PASS' for r in results),'failed':sum(r['status']=='FAIL' for r in results),'skipped':0},'digit_limit_before_after':{'before':orig_limit,'after':sys.get_int_max_str_digits()},'notes':['Independent bounded probe; no author test imported or executed.','No production source or original oracle changed.']}
(root/'source-probe-result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
raise SystemExit(1 if summary['counts']['failed'] else 0)
