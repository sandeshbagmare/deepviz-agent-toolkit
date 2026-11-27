import hashlib, json, sys, traceback
from pathlib import Path
from importlib import import_module
root=Path(__file__).parent; src=(root/'source-96b819/python/deepviz/src').resolve(); sys.path.insert(0,str(src))
import deepviz
norm=import_module('deepviz.normalize'); before=sys.get_int_max_str_digits()
assert Path(norm.__file__).resolve()==src/'deepviz/normalize.py'
assert hashlib.sha256(Path(norm.__file__).read_bytes()).hexdigest()=='b64814a6406857d9c9a1078fb759725a65a4a91d0db033c765d015df018dc6fd'
class Once:
 def __init__(self,rows):self.rows=rows;self.calls=0;self.yielded=0
 def __iter__(self):
  if self.calls:raise AssertionError('input replayed')
  self.calls+=1
  for row in self.rows:self.yielded+=1;yield row
n=10**4000; rows=Once([{'g':'only','v':n},{'g':'only','v':-n}]); source_repr_digits=len(str(n))
try:
 result=norm.normalize(rows,{'x':'g','y':'v','aggregation':'mean','max_points':10})
 outcome={'status':'PASS','records':result.records,'input_count':result.input_count,'strategy':result.strategy,'warnings':result.warnings,'source_iterations':rows.calls,'source_yielded':rows.yielded,'input_digit_count':source_repr_digits,'digit_limit_before_after':[before,sys.get_int_max_str_digits()]}
 assert result.records==[{'g':'only','v':0.0}] and result.input_count==2 and rows.calls==1 and rows.yielded==2 and sys.get_int_max_str_digits()==before
except Exception as exc:
 outcome={'status':'FAIL','error_type':type(exc).__name__,'error':str(exc),'traceback_tail':traceback.format_exc().splitlines()[-6:]}
report={'source':'96b819aee5b01ba88b5a609b587331a528aaa070','source_parent':'546c25ea75ee9d8a41b3832aa639664bc9a683b5','module_origin':norm.__file__,'module_sha256':hashlib.sha256(Path(norm.__file__).read_bytes()).hexdigest(),'exact_unmodified_F1_probe':outcome,'counts':{'cases':1,'passed':int(outcome['status']=='PASS'),'failed':int(outcome['status']=='FAIL'),'skipped':0},'notes':['New independent caller-authored probe only; original published 11 and author tests were not executed or changed.','No global digit-limit change.']}
(root/'strict-f1-result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,indent=2)); raise SystemExit(0 if outcome['status']=='PASS' else 1)
