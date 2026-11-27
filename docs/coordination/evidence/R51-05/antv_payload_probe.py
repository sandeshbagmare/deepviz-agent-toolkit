from pathlib import Path
import hashlib, json, math, os, sys
source = Path(r'C:\Users\bagma\AppData\Local\Temp\opencode\r51-05-antv-4429-ses_de567830effe0E5yIwQgDACLMD')
site = Path(r'C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages')
sys.path.insert(0, str(site)); sys.path.insert(0, str(source / 'python' / 'deepviz' / 'src'))
from deepviz.engines import native_spec
from deepviz.models import ChartSpec

MAX = 1.7976931348623157e308
cases = {
    'ordinary-signed': [-12.0, -3.0, 3.0, 12.0],
    'negative-subnormal': [-8e-310, -6e-310, -4e-310, -2e-310],
    'minimum-subnormal': [5e-324, 1e-323, 1.5e-323, 2e-323],
    'signed-MAX': [-MAX, 0.0, MAX],
    'constant-MAX': [MAX, MAX, MAX, MAX],
    'negative-constant-MAX': [-MAX, -MAX, -MAX, -MAX],
    'zero': [0.0, 0.0, 0.0, 0.0],
}
results = {}
for name, values in cases.items():
    rows = [{'column': c, 'row': r, 'heat': value} for (c, r), value in zip(
        [('West','North'), ('East','North'), ('West','South'), ('East','South')], values, strict=False)]
    original = json.loads(json.dumps(rows))
    native, warnings, actual = native_spec('antv', rows, ChartSpec(kind='heatmap', x='column', y='row', color='heat', aggregation='none', width=240, height=520, title=name))
    assert actual == 'heatmap' and rows == original
    json.dumps(native, allow_nan=False)
    color_scale = native['scale']['color']
    legend = native['legend']['color']
    result = {
        'values': values,
        'native_data_values': [row['_heat'] for row in native['data']],
        'native_coordinates': [[row['_x'], row['_y']] for row in native['data']],
        'scale_domain': color_scale['domain'],
        'scale_range': color_scale['range'],
        'legend': legend,
        'warnings': warnings,
        'json_finite': True,
    }
    if name == 'signed-MAX':
        assert color_scale['domain'] == [-MAX, 0.0, MAX]
        assert len(color_scale['range']) == 3
        assert legend['domain'] == [0, 1] and legend['data'][0]['domainValue'] == -MAX and legend['data'][1]['domainValue'] == MAX
    if name in {'negative-subnormal', 'minimum-subnormal'}:
        assert legend['domain'] == [0, 1]
        assert legend['data'][0]['domainValue'] == values[0] and legend['data'][1]['domainValue'] == values[-1]
    if name in {'constant-MAX', 'negative-constant-MAX'}:
        assert all(math.isfinite(float(v)) for v in color_scale['domain'])
        assert 'length' in legend and legend['length'] == 208, legend
    results[name] = result
bar, _, _ = native_spec('antv', [{'label':'A','value':1}], ChartSpec(kind='bar', x='label', y='value', width=240))
assert bar.get('style', {}).get('fill') == '#386cb0' and 'scale' not in bar
results['non_heatmap_bar_unchanged'] = {'style': bar['style'], 'has_scale': 'scale' in bar}
out = Path(os.environ['R51_OUT']); out.mkdir(parents=True, exist_ok=True)
(out / 'payload-probe.json').write_text(json.dumps({'source_commit':'4429f0521612b97eee3790f0d8d0fbc3cad3f8be','cases':results}, indent=2, allow_nan=False)+'\n', encoding='utf-8')
print(json.dumps({'exit':0,'cases':len(cases),'output':str(out/'payload-probe.json'),'source':str(source)}, indent=2))
