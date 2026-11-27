"""Collect this lane's synthetic evidence without rerunning any browser tests."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_root', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--source', default='3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    def git(*items: str) -> str:
        return subprocess.run(['git', *items], cwd=root, capture_output=True,
                              text=True, check=True).stdout.strip()

    def digest(path: Path) -> dict:
        return {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    modules = {}
    for name in ('deepviz.engines', 'deepviz.render', 'deepviz.normalize', 'deepviz.models'):
        file = Path(importlib.import_module(name).__file__).resolve()
        relative = file.relative_to(root).as_posix()
        actual = git('hash-object', str(file))
        assert actual == git('rev-parse', f'{args.source}:{relative}')
        modules[name] = {'file': relative, 'git_blob': actual, **digest(file)}
    inherited = {}
    for relative in ('tests/r10_probes/role20/test_plotly_literal_labels.py',
                     'tests/r10_probes/role20/browser_assertions.cjs'):
        blob = git('hash-object', str(root / relative))
        assert blob == git('rev-parse', f'c1bf91c5439d585e2ff157752f380cfa4fe85c6d:{relative}')
        inherited[relative] = blob

    cases = []
    for folder in sorted(args.raw_root.glob('test_plotly_isolated_sink_lite*')):
        if not folder.is_dir():
            continue
        request = json.loads((folder / 'request.json').read_text(encoding='utf-8'))
        observed = json.loads((folder / 'browser.json').read_text(encoding='utf-8'))
        assert observed['errors'] == observed['blocked'] == []
        image = folder / 'browser.png'
        shutil.copyfile(image, output / f'{request["sink"]}.png')
        cases.append({'sink': request['sink'], 'observed': observed,
                      'html_local_path': request['html'], 'html': digest(Path(request['html'])),
                      'image_local_path': str(image), 'image': digest(image)})
    assert {case['sink'] for case in cases} == {'legend', 'hover', 'title'}
    tree = ET.parse(Path(str(args.raw_root) + '.xml'))
    suite = tree.getroot().find('testsuite')
    assert suite is not None and suite.attrib['tests'] == suite.attrib['failures'] == '3'
    assert suite.attrib['errors'] == suite.attrib['skipped'] == '0'
    for element in tree.iter():
        element.attrib.pop('hostname', None)
    tree.write(output / 'strict-red.xml', encoding='utf-8', xml_declaration=True)
    summary = {'source': args.source, 'collector_head': git('rev-parse', 'HEAD'),
               'strict_test_exit': 1, 'tests': 3, 'failed': 3, 'passed': 0, 'skipped': 0,
               'suite_elapsed_s': float(suite.attrib['time']), 'cases': cases,
               'production_modules': modules, 'inherited_r10_test_blobs_unchanged': inherited,
               'new_probes': {p.name: digest(p) for p in sorted(Path(__file__).parent.iterdir())
                              if p.is_file()}}
    (output / 'strict-red.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({'collector_exit': 0, 'strict_test_exit': 1, 'cases': len(cases),
                      'source_blob_matches': len(modules), 'inherited_r10_blobs_unchanged': len(inherited),
                      'html_bytes': [case['html']['bytes'] for case in cases],
                      'images': {case['sink']: case['image'] for case in cases}}, indent=2))


if __name__ == '__main__':
    main()
