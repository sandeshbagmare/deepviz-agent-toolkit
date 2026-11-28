import hashlib, json
from pathlib import Path
paths=[
 'docs/coordination/reports/R38-18-antv-source-review.md',
 'docs/coordination/evidence/R38-18/extreme-native-numeric-result.json',
 'docs/coordination/reports/R39-21-antv-source-and-coverage.md',
 'docs/coordination/evidence/R39-21/extent-scale-counterexample.json',
 'docs/coordination/evidence/R39-21/independent-R38-17-F1.json',
 'docs/coordination/reports/R51-05-antv-source-review.md',
 'docs/coordination/evidence/R51-05/source-review.json',
 'docs/coordination/evidence/R51-05/minimum-width-max-label/label-bounds.json',
 'docs/coordination/reports/R45-17-antv-subnormal-implementation.md',
]
entries=[]
for raw in paths:
 p=Path(raw)
 if not p.is_file():
  entries.append({'path':raw,'available':False})
  continue
 b=p.read_bytes(); entries.append({'path':raw,'available':True,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
out={'captured_from_MAIN_checkout':'C:/Users/bagma/deepviz-agent-toolkit','purpose':'read-only exact prior report/evidence identity; not independent reproduction or test execution','files':entries}
Path('docs/coordination/evidence/R52-21/prior-evidence-manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
