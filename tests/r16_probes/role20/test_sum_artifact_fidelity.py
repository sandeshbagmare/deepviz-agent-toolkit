"""Non-author ec9 end-to-end artifact checks using small literal final SUMs."""
from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import math
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from deepviz.models import ChartSpec
from deepviz.normalize import normalize
from deepviz.render import render

SOURCE_SHA = 'ec9f669eff28cd5351da142765b7755e3b2f484f'
ENGINES = ['matplotlib', 'plotly', 'vega', 'echarts', 'antv']
EXPECTED = [{'group': 'A', 'total': 1.0}, {'group': 'B', 'total': 0.5},
            {'group': 'C', 'total': 3.0}]
NETWORK = 'HTML requires network access to load its exact-version pinned browser library from jsDelivr.'


def source_identity() -> dict:
    source = Path(os.environ['R16_20_SOURCE']).resolve()

    def git(*args: str) -> str:
        return subprocess.run(['git', *args], cwd=source, capture_output=True,
                              text=True, check=True).stdout.strip()

    assert git('rev-parse', 'HEAD') == SOURCE_SHA
    assert git('status', '--porcelain') == '', 'Consumer source must stay clean'
    loaded = {}
    for name in ('deepviz.normalize', 'deepviz.render', 'deepviz.engines', 'deepviz.models'):
        filename = importlib.import_module(name).__file__
        assert filename is not None
        file = Path(filename).resolve()
        relative = file.relative_to(source).as_posix()
        blob = git('hash-object', str(file))
        assert blob == git('rev-parse', f'HEAD:{relative}')
        loaded[name] = {'relative': relative, 'git_blob': blob,
                        'sha256': hashlib.sha256(file.read_bytes()).hexdigest()}
    return {'source': SOURCE_SHA, 'source_path': str(source), 'source_status': '', 'modules': loaded}


def fixture_rows(promoted: bool) -> list[dict]:
    groups = {
        'A': [1.7e308, 1.7e308, -1.7e308, -1.7e308, 1.0],
        'B': [1.7e308, 1.7e308, -1.7e308, -1.7e308, 0.25, 0.25],
        'C': [-1.7e308, -1.7e308, 1.7e308, 1.7e308, 1.0, 1.0, 1.0],
    } if promoted else {
        'A': [0.25, 0.25, 0.25, 0.125, 0.125],
        'B': [0.125, 0.125, 0.125, 0.0625, 0.03125, 0.03125],
        'C': [0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25],
    }
    # Independent literal expected totals, not an implementation of the fallback.
    assert [len(values) for values in groups.values()] == [5, 6, 7]
    if promoted:
        assert all(math.isinf(values[0] + values[1]) for values in groups.values())
    return [{'group': group, 'total': values[index]}
            for index in range(7) for group, values in groups.items() if index < len(values)]


def chart_spec() -> ChartSpec:
    return ChartSpec(kind='bar', title='R16 finite SUM fidelity', x='group', y='total',
                     aggregation='sum', max_points=10, width=900, height=420,
                     description='18 source rows: A=5, B=6, C=7; exact grouped totals shown.')


def reject_nonfinite(value: str) -> None:
    raise AssertionError(f'Nonfinite JSON constant: {value}')


def strict_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding='utf-8'), parse_constant=reject_nonfinite)
    json.dumps(result, allow_nan=False)
    return result


@pytest.fixture(scope='session')
def outputs(tmp_path_factory):
    root = tmp_path_factory.getbasetemp() / 'actual'
    root.mkdir()
    identity = source_identity()
    identity['dependencies'] = {name: importlib.metadata.version(name) for name in
                                ['matplotlib', 'plotly', 'vl-convert-python', 'numpy', 'pydantic']}
    (root / 'identity-before.json').write_text(json.dumps(identity, indent=2), encoding='utf-8')
    yield root
    after = source_identity()
    assert after['modules'] == identity['modules']
    (root / 'identity-after.json').write_text(json.dumps(after, indent=2), encoding='utf-8')


@pytest.mark.parametrize('promoted', [True, False], ids=['promoted', 'ordinary'])
def test_public_normalize_has_only_finite_final_group_totals(promoted, outputs) -> None:
    rows = fixture_rows(promoted)
    result = normalize(iter(rows), chart_spec())
    assert result.records == EXPECTED
    assert result.input_count == 18 and result.strategy == 'sum' and result.warnings == []
    assert all(set(row) == {'group', 'total'} and type(row['total']) in (int, float)
               and math.isfinite(row['total']) for row in result.records)
    json.dumps(result.records, allow_nan=False)
    (outputs / f'normalize-{promoted}.json').write_text(json.dumps({
        'records': result.records, 'input_count': result.input_count,
        'strategy': result.strategy, 'warnings': result.warnings,
        'literal_expected_group_input_counts': [5, 6, 7],
    }, indent=2), encoding='utf-8')


@pytest.fixture(scope='session')
def generated(outputs):
    cache = {}

    def generate(promoted: bool, engine: str) -> dict:
        key = (promoted, engine)
        if key not in cache:
            case = outputs / ('promoted' if promoted else 'ordinary') / engine
            case.mkdir(parents=True)
            # Raw one-shot public input: render itself must normalize and reduce.
            artifact = render(iter(fixture_rows(promoted)), chart_spec(), engine=engine,
                              output_dir=case / 'artifacts')
            manifest_path = next(Path(p) for p in artifact.paths if p.endswith('manifest.json'))
            manifest = strict_json(manifest_path)
            html = next(Path(p) for p in artifact.paths if p.endswith('chart.html'))
            result = {'engine': engine, 'promoted': promoted, 'case_path': str(case),
                      'artifact': artifact.to_dict(), 'manifest': manifest,
                      'manifest_path': str(manifest_path), 'html': str(html)}
            (case / 'generated.json').write_text(json.dumps(result, indent=2, allow_nan=False),
                                                 encoding='utf-8')
            cache[key] = result
        return cache[key]

    return generate


def bar_ratios(heights: list[float]) -> None:
    assert len(heights) == 3 and all(math.isfinite(height) and height > 0 for height in heights)
    assert heights[1] / heights[0] == pytest.approx(0.5, abs=0.04)
    assert heights[2] / heights[0] == pytest.approx(3.0, abs=0.06)


@pytest.mark.parametrize('promoted', [True, False], ids=['promoted', 'ordinary'])
@pytest.mark.parametrize('engine', ENGINES)
def test_public_render_keeps_reduction_counts_values_and_native_payloads(promoted, engine, generated):
    result = generated(promoted, engine)
    artifact, manifest = result['artifact'], result['manifest']
    assert artifact['input_count'] == 18 and artifact['output_count'] == 3
    assert artifact['strategy'] == manifest['strategy'] == 'sum'
    expected_warnings = [NETWORK] if engine in {'echarts', 'antv'} else []
    assert artifact['warnings'] == manifest['warnings'] == expected_warnings
    assert len(manifest['charts']) == 1
    chart = manifest['charts'][0]
    assert chart['records'] == EXPECTED
    assert all(set(row) == {'group', 'total'} for row in chart['records'])
    assert (chart['input_count'], chart['output_count'], chart['strategy']) == (18, 3, 'sum')
    assert chart['warnings'] == expected_warnings
    assert chart['requested_kind'] == chart['rendered_kind'] == 'bar'
    html = Path(result['html']).read_text(encoding='utf-8')
    assert '3 displayed records from 18 input records. Reduction strategy: sum.' in html
    assert html.count('<tbody>') == 1 and html.count('<tr>') == 4
    assert set(manifest) == {'engine', 'charts', 'warnings', 'native_specs', 'strategy', 'accessible_path'}
    assert all(token not in json.dumps(manifest).lower() for token in
               ['bigint', '_sum_units', 'sumunits', 'accumulator', 'non-finite', '__deepviz_other__'])
    native = manifest['native_specs']
    metrics = {'warnings': expected_warnings, 'native_final_values': [1.0, 0.5, 3.0]}
    if engine == 'matplotlib':
        assert native == []
        svg = ET.parse(next(p for p in artifact['paths'] if p.endswith('.svg'))).getroot()
        paths = [node for node in svg.iter() if node.tag.endswith('path')
                 and 'fill: #386cb0' in node.attrib.get('style', '')]
        heights = []
        for node in paths:
            coordinates = [float(value) for value in re.findall(r'-?\d+(?:\.\d+)?', node.attrib['d'])]
            heights.append(max(coordinates[1::2]) - min(coordinates[1::2]))
        bar_ratios(heights)
        metrics['static_svg_heights'] = heights
    else:
        assert len(native) == 1
        payload = native[0]
        if engine == 'plotly':
            assert payload['data'][0]['x'] == ['A', 'B', 'C']
            values = payload['data'][0]['y']
        elif engine == 'vega':
            assert [row['_x'] for row in payload['data']['values']] == ['A', 'B', 'C']
            values = [row['_y'] for row in payload['data']['values']]
            svg = ET.parse(next(p for p in artifact['paths'] if p.endswith('.svg'))).getroot()
            native_marks = [node.attrib for node in svg.iter()
                            if node.attrib.get('aria-roledescription') == 'bar']
            assert len(native_marks) == 3
            metrics['static_svg_marks'] = native_marks
        elif engine == 'echarts':
            assert payload['series'][0]['data'] == [['A', 1.0], ['B', 0.5], ['C', 3.0]]
            values = [row[1] for row in payload['series'][0]['data']]
        else:
            assert [row['_x'] for row in payload['data']] == ['A', 'B', 'C']
            assert all(set(row) == {'_x', '_y', '_color', '_size', '_heat', '_row'}
                       for row in payload['data']), 'Only declarative channels, no reducer slots'
            values = [row['_y'] for row in payload['data']]
        assert values == [1.0, 0.5, 3.0]
        assert all(type(value) in (int, float) and math.isfinite(value) for value in values)
    (Path(result['case_path']) / 'assertions.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')


@pytest.mark.parametrize('promoted', [True, False], ids=['promoted', 'ordinary'])
@pytest.mark.parametrize('engine', ['plotly', 'echarts', 'antv'])
def test_real_native_browser_values_and_bar_heights(promoted, engine, generated):
    node = shutil.which('node')
    modules = Path(os.environ.get('R16_20_NODE_MODULES', 'node_modules')).resolve()
    if node is None or not (modules / 'playwright/package.json').is_file():
        pytest.skip('Needs already-installed Node/Playwright; no install')
    result = generated(promoted, engine)
    folder = Path(result['case_path'])
    request = {'engine': engine, 'html': result['html'], 'result': str(folder / 'browser.json'),
               'image': str(folder / 'browser.png')}
    (folder / 'request.json').write_text(json.dumps(request), encoding='utf-8')
    proc = subprocess.run([node, str(Path(__file__).with_name('sum_browser.cjs')),
                           str(folder / 'request.json'), str(modules)], capture_output=True,
                          text=True, timeout=90, check=False)
    assert proc.returncode == 0, proc.stderr[-2000:]
    observed = strict_json(folder / 'browser.json')
    assert observed['errors'] == observed['blocked'] == []
    assert observed['native_ready'] is True and observed['render_error'] is None
    assert observed['native_values'] == [1.0, 0.5, 3.0]
    assert observed['table_cells'] == ['A', '1.0', 'B', '0.5', 'C', '3.0']
    assert observed['svg_count'] > 0 if engine != 'antv' else observed['canvas_count'] > 0
    bar_ratios(observed['bar_heights'])
