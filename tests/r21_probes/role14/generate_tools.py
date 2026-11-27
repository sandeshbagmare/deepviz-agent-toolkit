"""Materialize exact source objects and invoke three real Deep Agent StructuredTools.

Existing dependencies only. Source snapshot and artifacts live in a new owned output.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

SOURCE = '7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6'
ROWS = [{'label': 'A & B', 'value': 3}, {'label': 'C < D', 'value': 9}]
SPEC = {'kind': 'bar', 'x': 'label', 'y': 'value', 'aggregation': 'none',
        'title': 'Offline <literal> & host', 'width': 700, 'height': 340}


class Scripts(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.urls: list[str] = []
        self.images: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'script' and 'src' in values:
            self.urls.append(values['src'])
        if tag == 'img' and 'src' in values:
            self.images.append(values['src'])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=False, exist_ok=False)
    repo = args.repository.resolve()
    source = args.out / 'snapshot'
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', SOURCE,
                                    '--', 'python/deepviz/src/deepviz'], cwd=repo, text=True).splitlines()
    provenance = []
    for relative in paths:
        destination = source / relative
        assert destination.resolve().is_relative_to(source.resolve())
        content = subprocess.check_output(['git', 'show', SOURCE + ':' + relative], cwd=repo)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        provenance.append({'file': relative, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    sys.path.insert(0, str((source / 'python/deepviz/src').resolve()))
    deepviz = importlib.import_module('deepviz')
    assert deepviz.__file__ and Path(deepviz.__file__).resolve().is_relative_to(source.resolve())
    tools_module = importlib.import_module('deepviz.tools')
    tools = {tool.name: tool for tool in tools_module.create_tools(args.out / 'tool-artifacts')}
    artifacts = []
    for engine in ['echarts', 'antv', 'matplotlib']:
        tool = tools['render_' + engine]
        response = tool.invoke({'data': ROWS, 'spec': SPEC})
        assert response['engine'] == engine and response['input_count'] == response['output_count'] == 2
        files = [Path(file).resolve() for file in response['paths']]
        html = next(file for file in files if file.suffix == '.html')
        parsed = Scripts(html.read_text(encoding='utf-8'))
        artifacts.append({'engine': engine, 'tool_name': tool.name, 'tool_adapter': type(tool).__name__,
            'tool_response': {**response, 'paths': [p.relative_to(args.out.resolve()).as_posix() for p in files]},
            'html': html.relative_to(args.out.resolve()).as_posix(), 'external_scripts': parsed.urls, 'images': parsed.images,
            'files': [{'file': file.relative_to(args.out.resolve()).as_posix(), 'bytes': file.stat().st_size,
                       'sha256': hashlib.sha256(file.read_bytes()).hexdigest()} for file in files]})
    imported = []
    for name, module in list(sys.modules.items()):
        if name == 'deepviz' or name.startswith('deepviz.'):
            assert module.__file__ and Path(module.__file__).resolve().is_relative_to(source.resolve()), name
            imported.append(name)
    for item in provenance:
        assert hashlib.sha256((source / item['file']).read_bytes()).hexdigest() == item['sha256']
    manifest = {'source_commit': SOURCE, 'source_files': provenance, 'imported_own_modules': sorted(imported),
        'python_version': sys.version.split()[0], 'langchain_core_version': importlib.metadata.version('langchain-core'),
        'rows': ROWS, 'spec': SPEC, 'artifacts': artifacts,
        'limits': ['Direct invocation of real create_tools StructuredTools intended for Deep Agent attachment; no LLM/provider/DeepAgent-model run.',
                   'Rendered bytes are unchanged; source materialized from exact immutable Git objects, no package build or install.',
                   'Tool artifact creation success is not a browser-runtime readiness claim.']}
    (args.out / 'tool-artifacts.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'source_commit': SOURCE, 'source_files': len(provenance), 'actual_tools_invoked': len(artifacts),
                      'counts_each': 2, 'generation': 'pass, not browser readiness'}, indent=2))


if __name__ == '__main__':
    main()
