"""Check a locally built/installed toolkit without downloading or installing dependencies."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata as metadata
import json
import subprocess
import sys
import tarfile
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile

PINS = {
    'echarts': ['https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js'],
    'antv': ['https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js'],
}
NOTICE_SHA256 = '8c45d9eaf50c2f72dd9c7ab9ef440788ba58a3538484b5c51c1f17d5128752e7'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Document(HTMLParser):
    def __init__(self, html: str):
        super().__init__()
        self.scripts: list[str] = []
        self.images: list[str] = []
        self.comments: list[str] = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'script' and 'src' in values:
            self.scripts.append(values['src'])
        if tag == 'img' and 'src' in values:
            self.images.append(values['src'])

    def handle_comment(self, text):
        self.comments.append(text)


def validate_html(html: str, engine: str, notice: str = '') -> Document:
    document = Document(html)
    assert document.scripts == PINS.get(engine, []), (engine, document.scripts)
    if engine == 'plotly':
        assert notice, 'No audited notice supplied'
        expected = ' '.join(notice.split())
        assert any(expected in ' '.join(comment.split()) for comment in document.comments), 'Incomplete notice'
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--installed', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--sdist', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source, installed = args.source.resolve(), args.installed.resolve()
    args.out.mkdir(parents=False, exist_ok=False)
    sys.path.insert(0, str(installed))
    package = importlib.import_module('deepviz')
    assert package.__file__ is not None, 'Namespace package is not an installed toolkit'
    assert Path(package.__file__).resolve().is_relative_to(installed), 'Source fallback, not installed package'

    def source_bytes(relative: str) -> bytes:
        pinned = subprocess.check_output(['git', 'show', f'{args.source_commit}:{relative}'], cwd=source)
        assert (source / relative).read_bytes() == pinned, f'Source differs from requested commit: {relative}'
        return pinned

    checked = []
    with ZipFile(args.wheel) as wheel, tarfile.open(args.sdist, 'r:gz') as sdist:
        for file in sorted((source / 'python/deepviz/src/deepviz').glob('*.py')):
            relative = file.relative_to(source).as_posix()
            member = 'deepviz/' + file.name
            expected = source_bytes(relative)
            assert wheel.read(member) == expected
            candidates = [item for item in sdist.getmembers() if item.name.endswith('/' + relative)]
            assert len(candidates) == 1
            stream = sdist.extractfile(candidates[0])
            assert stream is not None
            assert stream.read() == expected
            stream.close()
            assert (installed / member).read_bytes() == expected
            module = importlib.import_module('deepviz' if file.stem == '__init__' else 'deepviz.' + file.stem)
            assert module.__file__ is not None
            assert Path(module.__file__).resolve() == installed / member
            checked.append({'file': member, 'sha256': sha(expected), 'wheel_sdist_installed_match': True})
        assets = {
            'deepviz/resources/plotly-js-LICENSE.txt': 'python/deepviz/src/deepviz/resources/plotly-js-LICENSE.txt',
            'deepviz/resources/chart-spec.schema.json': 'schemas/chart-spec.schema.json',
            'deepviz/py.typed': 'python/deepviz/src/deepviz/py.typed',
            **{f'deepviz/resources/prompts/v1/{name}.md': f'prompts/v1/{name}.md' for name in ['README', 'request', 'system']},
        }
        for member, relative in assets.items():
            expected = source_bytes(relative)
            assert wheel.read(member) == expected
            assert (installed / member).read_bytes() == expected
            checked.append({'file': member, 'sha256': sha(expected), 'wheel_installed_match': True})

    notice = (installed / 'deepviz/resources/plotly-js-LICENSE.txt').read_text(encoding='utf-8')
    assert sha(notice.encode()) == NOTICE_SHA256
    from plotly.offline import get_plotlyjs, get_plotlyjs_version
    runtime = get_plotlyjs()
    summary = {
        'source_commit': args.source_commit,
        'mode': 'Fresh local wheel target; preinstalled runtime dependencies reused read-only; no dependency resolution.',
        'python': sys.version.split()[0],
        'distributions': [{'name': file.name, 'bytes': file.stat().st_size, 'sha256': sha(file.read_bytes())} for file in [args.wheel, args.sdist]],
        'installed_files': checked,
        'plotly': {'python_version': metadata.version('plotly'), 'js_version': get_plotlyjs_version(),
                   'js_bytes': len(runtime.encode()), 'js_sha256': sha(runtime.encode()),
                   'notice_sha256': NOTICE_SHA256, 'audited_notice_tag': '3.7.0',
                   'runtime_matches_audited_notice_tag': get_plotlyjs_version() == '3.7.0'},
        'outputs': [],
        'limits': ['Not a fresh dependency-resolved environment.', 'No comprehensive advisory or transitive license certification.',
                   'External URLs are inventory only; this script never fetches them.'],
    }
    rows = [{'label': 'Alpha', 'value': 3}, {'label': 'Beta', 'value': 9}]
    spec: dict[str, object] = {'kind': 'bar', 'x': 'label', 'y': 'value', 'aggregation': 'none', 'title': 'Installed asset control'}
    cases = [(engine, spec, engine) for engine in ['matplotlib', 'plotly', 'vega', 'echarts', 'antv']]
    cases.append(('plotly', {'kind': 'dashboard', 'title': 'Installed dashboard', 'charts': [spec, {**spec, 'title': 'Second panel'}]}, 'plotly-dashboard'))
    for engine, chart, name in cases:
        artifact = package.render(rows, chart, engine=engine, output_dir=args.out / 'renders' / name)
        assert artifact.input_count == 2
        assert artifact.output_count == (4 if name.endswith('dashboard') else 2)
        html = next(Path(file) for file in artifact.paths if file.endswith('.html'))
        text = html.read_text(encoding='utf-8')
        document = validate_html(text, engine, notice)
        if engine == 'plotly':
            assert runtime in text
        for image in document.images:
            assert image == 'chart.svg' and (html.parent / image).is_file()
        summary['outputs'].append({'id': 'python-' + name, 'engine': engine,
            'html': html.relative_to(args.out).as_posix(), 'html_sha256': sha(html.read_bytes()),
            'scripts': document.scripts, 'offline_expected': not document.scripts,
            'input_count': artifact.input_count, 'output_count': artifact.output_count, 'warnings': artifact.warnings})
    assert summary['plotly']['runtime_matches_audited_notice_tag'], 'Runtime license tag not independently audited'
    (args.out / 'python-manifest.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({'source_commit': args.source_commit, 'installed_files': len(checked), 'renders': len(cases), 'result': 'pass'}, indent=2))


if __name__ == '__main__':
    main()
