"""Strict real-browser F20-1 regression; current checkpoint is intentionally RED.

Run with installed DeepViz render extras, Node/Playwright/Chromium and
R10_20_NODE_MODULES pointing to an existing node_modules directory. No installs,
network, payload code execution or clicks are used by this test.
"""
from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from deepviz.models import ChartSpec
from deepviz.render import render

LINK = '<a href="https://example.invalid/r10-20">R10 safe link</a>'
HANDLER = '<img src="R10-inert:" onerror="">'
LITERAL = '<b>R10 literal label</b>'
SERIES = '<b>R10 literal series</b>'
VALUES = [3, 7, 11]


@pytest.mark.parametrize('dashboard', [False, True], ids=['chart', 'dashboard'])
@pytest.mark.parametrize('family', ['categorical', 'numeric', 'time'])
def test_plotly_literal_labels_and_coordinate_controls(
    family: str, dashboard: bool, tmp_path: Path,
) -> None:
    node = shutil.which('node')
    modules = Path(os.environ.get('R10_20_NODE_MODULES', 'node_modules')).resolve()
    if node is None or not (modules / 'playwright/package.json').is_file():
        pytest.skip('Requires already-installed Node/Playwright; no automatic install')
    x_values = {
        'categorical': [LINK, HANDLER, LITERAL],
        'numeric': [1, 2, 4],
        'time': ['2026-01-01', '2026-01-02', '2026-01-04'],
    }[family]
    records = [{'x': x, 'value': value, **({'series': SERIES} if family == 'categorical' else {})}
               for x, value in zip(x_values, VALUES, strict=True)]
    child = ChartSpec(kind='bar' if family == 'categorical' else 'line',
                      title=f'R10 {family} literal-label control', x='x', y='value',
                      color='series' if family == 'categorical' else None,
                      aggregation='none', height=420, max_points=10)
    spec = (ChartSpec(kind='dashboard', title='R10 two-child literal labels',
                      charts=[child, child], columns=2, width=1000, height=520)
            if dashboard else child)
    artifact = render(records, spec, engine='plotly', output_dir=tmp_path / 'artifacts')
    html = next(Path(p) for p in artifact.paths if p.endswith('chart.html'))
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith('manifest.json'))
                          .read_text(encoding='utf-8'))
    child_count = 2 if dashboard else 1
    assert artifact.input_count == 3 and artifact.output_count == 3 * child_count
    assert all(chart['records'] == records for chart in manifest['charts'])
    assert html.stat().st_size < 6_000_000, 'Small fixture HTML unexpectedly grew'
    request = {
        'html': str(html), 'family': family, 'child_count': child_count,
        'x_values': x_values, 'values': VALUES,
        'literal_strings': [LINK, HANDLER, LITERAL, SERIES] if family == 'categorical' else [],
        'result': str(tmp_path / 'browser.json'), 'screenshot': str(tmp_path / 'browser.png'),
    }
    request_file = tmp_path / 'request.json'
    request_file.write_text(json.dumps(request), encoding='utf-8')
    proc = subprocess.run(
        [node, str(Path(__file__).with_name('browser_assertions.cjs')), str(request_file), str(modules)],
        capture_output=True, text=True, timeout=90, check=False,
    )
    assert proc.returncode == 0, f'Browser harness failed: {proc.stderr[-2000:]}'
    observed = json.loads((tmp_path / 'browser.json').read_text(encoding='utf-8'))
    observed['html_bytes'] = html.stat().st_size
    observed['source_modules'] = {
        name: str(Path(importlib.import_module(name).__file__).resolve())
        for name in ('deepviz.engines', 'deepviz.render', 'deepviz.normalize')
    }
    (tmp_path / 'browser.json').write_text(json.dumps(observed, indent=2), encoding='utf-8')
    assert observed['errors'] == [] and observed['blocked'] == [], observed
    assert len(observed['charts']) == child_count
    for chart in observed['charts']:
        assert chart['y'] == VALUES
        assert chart['mark_count'] == 3
        assert chart['anchors'] == [], f'F20-1 data created active anchors: {chart["anchors"]}'
        assert chart['handlers'] == [], f'Data created event attributes: {chart["handlers"]}'
        assert chart['missing_literal_strings'] == [], chart['missing_literal_strings']
        if family != 'categorical':
            assert chart['x'] == x_values, 'Literal-label hardening must not mutate numeric/time values'
            positions = chart['mark_centers']
            first = positions[1]['x'] - positions[0]['x']
            second = positions[2]['x'] - positions[1]['x']
            assert first > 0 and second > 0
            assert first / second == pytest.approx(0.5, abs=0.015)
            assert positions[0]['y'] > positions[1]['y'] > positions[2]['y']
    assert observed['table_cells'] == [str(value) for row in records for value in row.values()] * child_count
