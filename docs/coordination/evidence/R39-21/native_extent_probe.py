"""Two-record independent native/SDK boundary probe, not browser/full-suite approval."""
import hashlib,importlib,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[3]
source=here/'inputs/python/deepviz/src'
sys.dont_write_bytecode=True
sys.path[:0]=[str(source),r'C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages']
manifest=json.loads((here/'runtime-source-manifest.json').read_text())
def check():
    for row in manifest:
        assert hashlib.sha256((root/row['saved']).read_bytes()).hexdigest()==row['sha256']
check()
from deepviz.models import ChartSpec
from deepviz.normalize import normalize
from deepviz.engines import native_spec
modules={}
for name in ['deepviz','deepviz.models','deepviz.normalize','deepviz.render','deepviz.engines']:
    module=importlib.import_module(name);p=Path(module.__file__).resolve()
    assert p.is_relative_to(source.resolve())
    modules[name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
results=[]
for name,values in [('negative_control',[-7.0,-2.0]),('opposite_finite_MAX',[-1e308,1e308])]:
    rows=[{'x':'A','y':'AM','heat':values[0]},{'x':'B','y':'PM','heat':values[1]}]
    spec=ChartSpec(kind='heatmap',x='x',y='y',color='heat',aggregation='none')
    normalized=normalize(rows,spec)
    native,warnings,kind=native_spec('antv',normalized.records,spec)
    assert normalized.records==rows and rows[0]['heat']==values[0] and rows[1]['heat']==values[1]
    assert [row['_heat'] for row in native['data']]==values
    results.append({'name':name,'literal_values':values,'native':native,'warnings':warnings,'input_count':normalized.input_count})
check()
(here/'native-extent-inputs.json').write_text(json.dumps({'source_commit':'3185e0d9936c7d6f1a9d30b94089b804d75fe991','executable':sys.executable,'modules':modules,'cases':results},indent=2,allow_nan=False)+'\n',encoding='utf-8')
print('2actualfrozen-source native heatmap payloads; Git/module/raw identities preserved; notauthor21/browser254')
