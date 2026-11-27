"""Read completed role20 artifacts; this command never reruns render/browser tests."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from test_sum_artifact_fidelity import source_identity


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    def digest(path: Path) -> dict:
        return {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    before = json.loads((args.raw_root / 'actual/identity-before.json').read_text(encoding='utf-8'))
    after = json.loads((args.raw_root / 'actual/identity-after.json').read_text(encoding='utf-8'))
    current = source_identity()
    assert before['modules'] == after['modules'] == current['modules']
    cases = []
    for generated in sorted((args.raw_root / 'actual').glob('*/*/generated.json')):
        folder = generated.parent
        result = json.loads(generated.read_text(encoding='utf-8'))
        assertions = json.loads((folder / 'assertions.json').read_text(encoding='utf-8'))
        row = {'fixture': folder.parent.name, 'engine': folder.name,
               'artifact': result['artifact'], 'manifest': result['manifest'],
               'assertions': assertions,
               'files': {Path(path).name: digest(Path(path)) for path in result['artifact']['paths']}}
        if (folder / 'browser.json').exists():
            row['browser'] = json.loads((folder / 'browser.json').read_text(encoding='utf-8'))
            assert row['browser']['errors'] == row['browser']['blocked'] == []
        if result['promoted']:
            image = (folder / 'browser.png') if (folder / 'browser.png').exists() else next(
                (Path(path) for path in result['artifact']['paths'] if path.endswith('.png')), None)
            if image is not None:
                shutil.copyfile(image, args.output / f'{folder.name}.png')
                row['inspected_image'] = digest(image)
            if folder.name == 'vega':
                svg = next(Path(path) for path in result['artifact']['paths'] if path.endswith('.svg'))
                shutil.copyfile(svg, args.output / 'vega.svg')
        cases.append(row)
    assert len(cases) == 10
    assert len([row for row in cases if 'browser' in row]) == 6
    tree = ET.parse(Path(str(args.raw_root) + '.xml'))
    suite = tree.getroot().find('testsuite')
    assert suite is not None
    assert (suite.attrib['tests'], suite.attrib['failures'], suite.attrib['errors'],
            suite.attrib['skipped']) == ('18', '0', '0', '0')
    for element in tree.iter():
        element.attrib.pop('hostname', None)
    tree.write(args.output / 'results.xml', encoding='utf-8', xml_declaration=True)
    probes = {path.name: digest(path) for path in Path(__file__).parent.iterdir() if path.is_file()}
    summary = {'source': current, 'test_exit': 0, 'passed': 18, 'failed': 0, 'skipped': 0,
               'suite_elapsed_s': float(suite.attrib['time']), 'pretest_dependencies': before['dependencies'],
               'cases': cases, 'published_probes': probes,
               'execution_caveat': '18 tests executed before nullable module.__file__ guard only. '
                                   'Executed hashes stored separately; postguard source identity/lint/mypy '
                                   'checked, no browser replay. Source and numerical/browser assertions unchanged.'}
    (args.output / 'results.json').write_text(json.dumps(summary, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps({'collector_exit': 0, 'passed': 18, 'cases': 10, 'browser_cases': 6,
                      'source_modules_stable': 4,
                      'published_evidence_bytes': sum(path.stat().st_size for path in args.output.iterdir()
                                                      if path.is_file())}, indent=2))


if __name__ == '__main__':
    main()
