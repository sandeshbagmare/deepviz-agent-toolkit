"""Novel sink discriminators; no original R10 test or production code is changed."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from deepviz.models import ChartSpec
from deepviz.render import render

LEGEND = '<a href="https://example.invalid/r13-legend">R13 legend</a>'
HOVER = [
    '<a href="https://example.invalid/r13-hover">R13 hover</a>',
    '<b>R13 "hover" & text</b>',
    '<img src="R13-inert:" onerror="">',
]
TITLE = '<a href="https://example.invalid/r13-title">R13 "title" & \'quote\'</a>'


@pytest.mark.parametrize('sink', ['legend', 'hover', 'title'])
def test_plotly_isolated_sink_literal_text(sink: str, tmp_path: Path) -> None:
    node = shutil.which('node')
    modules = Path(os.environ.get('R13_20_NODE_MODULES', 'node_modules')).resolve()
    if node is None or not (modules / 'playwright/package.json').is_file():
        pytest.skip('Requires existing Node/Playwright; never installs dependencies')

    # Payloads occur only in the specified sink, never in x/y coordinates.
    xs = {'legend': [1, 2, 4], 'hover': [-120, -60, 120],
          'title': ['2026-02-01', '2026-02-02', '2026-02-04']}[sink]
    ys = [10, 20, 35] if sink == 'hover' else [3, 7, 11]
    records = [{'x': x, 'value': y, **({'label': HOVER[index] if sink == 'hover' else LEGEND}
                                     if sink != 'title' else {})}
               for index, (x, y) in enumerate(zip(xs, ys, strict=True))]
    spec = ChartSpec(kind='geo' if sink == 'hover' else 'line', x='x', y='value',
                     color='label' if sink != 'title' else None,
                     title=TITLE if sink == 'title' else f'R13 isolated {sink}',
                     aggregation='none', width=1000, height=480, max_points=10)
    artifact = render(records, spec, engine='plotly', output_dir=tmp_path / 'artifacts')
    html = next(Path(p) for p in artifact.paths if p.endswith('chart.html'))
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith('manifest.json'))
                          .read_text(encoding='utf-8'))
    assert artifact.input_count == artifact.output_count == 3
    assert manifest['charts'][0]['records'] == records
    assert html.stat().st_size < 6_000_000

    request = {'sink': sink, 'html': str(html), 'result': str(tmp_path / 'browser.json'),
               'image': str(tmp_path / 'browser.png')}
    request_path = tmp_path / 'request.json'
    request_path.write_text(json.dumps(request), encoding='utf-8')
    proc = subprocess.run(
        [node, str(Path(__file__).with_name('sink_browser.cjs')), str(request_path), str(modules)],
        capture_output=True, text=True, timeout=90, check=False,
    )
    assert proc.returncode == 0, f'Native browser collection failed: {proc.stderr[-2000:]}'
    observed = json.loads((tmp_path / 'browser.json').read_text(encoding='utf-8'))
    assert observed['errors'] == [] and observed['blocked'] == [], observed
    assert observed['native_json_bytes'] < 50_000
    snapshots = [observed['before'], *observed['hover_states']]
    for snapshot in snapshots:
        assert snapshot['x'] == xs and snapshot['y'] == ys
        assert len(snapshot['mark_centers']) == 3
        centers = snapshot['mark_centers']
        ratio = (centers[1]['x'] - centers[0]['x']) / (centers[2]['x'] - centers[1]['x'])
        assert ratio == pytest.approx(1 / 3 if sink == 'hover' else 0.5, abs=0.015)
        assert centers[0]['y'] > centers[1]['y'] > centers[2]['y']

    violations = []
    for index, snapshot in enumerate(snapshots):
        if snapshot['anchors']:
            violations.append(f'state {index}: active anchors {snapshot["anchors"]}')
        if snapshot['handlers']:
            violations.append(f'state {index}: event handlers {snapshot["handlers"]}')
    if sink == 'legend' and observed['before']['legend_text'] != [LEGEND]:
        violations.append(f'legend not literal: {observed["before"]["legend_text"]}')
    if sink == 'hover':
        assert len(observed['hover_states']) == 3, 'All three actual pointer hovers required'
        assert observed['before']['hover_text'] == []
        for state, original in zip(observed['hover_states'], HOVER, strict=True):
            if not any(original in text for text in state['hover_text']):
                violations.append(f'hover not literal: {state["hover_text"]}')
    if sink == 'title' and observed['before']['native_title'] != [TITLE]:
        violations.append(f'native title not literal: {observed["before"]["native_title"]}')
    assert violations == [], '\n'.join(violations)
