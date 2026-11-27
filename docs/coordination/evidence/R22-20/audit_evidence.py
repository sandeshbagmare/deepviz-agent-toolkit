"""Verify immutable local Git permalinks/baseline evidence; never rerun browsers."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent


def git(*args: str) -> bytes:
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout


def main() -> None:
    body = (BASE / 'issue-body.md').read_text(encoding='utf-8')
    matches = re.findall(
        r'https://(?:github\.com/sandeshbagmare/deepviz-agent-toolkit/blob/'
        r'|raw\.githubusercontent\.com/sandeshbagmare/deepviz-agent-toolkit/)'
        r'([a-f0-9]{40})/([^\s)#]+)', body,
    )
    allowed = {'3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab',
               'c1bf91c5439d585e2ff157752f380cfa4fe85c6d',
               'f9087d0518e74378e810b9efe6d6630a12044399'}
    checked = []
    for sha, path in matches:
        assert sha in allowed
        file_bytes = git('show', f'{sha}:{path}')
        checked.append({'commit': sha, 'path': path, 'bytes': len(file_bytes),
                        'sha256': hashlib.sha256(file_bytes).hexdigest()})
    assert len(checked) >= 12
    r10_sha = 'c1bf91c5439d585e2ff157752f380cfa4fe85c6d'
    r13_sha = 'f9087d0518e74378e810b9efe6d6630a12044399'
    r10 = json.loads(git('show', f'{r10_sha}:docs/coordination/evidence/R10-20/strict-red.json'))
    r13 = json.loads(git('show', f'{r13_sha}:docs/coordination/evidence/R13-20/strict-red.json'))
    assert (r10['failed'], r10['passed'], r10['skipped']) == (2, 4, 0)
    assert (r13['failed'], r13['passed'], r13['skipped']) == (3, 0, 0)
    assert r10['source'] == r13['source'] == '3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab'
    for summary in (r10, r13):
        for case in summary['cases']:
            assert case['observed']['errors'] == case['observed']['blocked'] == []
    images = []
    for name, case in zip(('categorical-chart', 'categorical-dashboard'), r10['cases'][:2], strict=True):
        path = f'docs/coordination/evidence/R10-20/{name}.png'
        actual = hashlib.sha256(git('show', f'{r10_sha}:{path}')).hexdigest()
        assert actual == case['image']['sha256']
        images.append({'path': path, 'commit': r10_sha, 'sha256': actual})
    for case in r13['cases']:
        path = f'docs/coordination/evidence/R13-20/{case["sink"]}.png'
        actual = hashlib.sha256(git('show', f'{r13_sha}:{path}')).hexdigest()
        assert actual == case['image']['sha256']
        images.append({'path': path, 'commit': r13_sha, 'sha256': actual})
    suites = []
    for sha, wave in ((r10_sha, 'R10'), (r13_sha, 'R13')):
        tree = ET.fromstring(git('show', f'{sha}:docs/coordination/evidence/{wave}-20/strict-red.xml'))
        suite = tree.find('testsuite')
        assert suite is not None
        suites.append({key: suite.attrib[key] for key in ('tests', 'failures', 'errors', 'skipped')})
    assert suites == [{'tests': '6', 'failures': '2', 'errors': '0', 'skipped': '0'},
                      {'tests': '3', 'failures': '3', 'errors': '0', 'skipped': '0'}]
    assert git('diff', 'ffea4d74ece9a02864eae404eb0596d660172ba9', '--', 'python/deepviz/src',
               'packages/deepviz/src', 'schemas', 'tests/r10_probes/role20',
               'tests/r13_probes/role20', 'tests/r16_probes/role20') == b''
    summary = {'issue_body_utf8_sha256': hashlib.sha256(body.encode('utf-8')).hexdigest(),
               'invalid_permalinks': [], 'checked_permalinks': checked,
               'five_png_hashes_match_actual_recorded_images': images,
               'recorded_junit_suites': suites, 'browser_errors_in_recorded_nine_cases': 0,
               'test_browser_or_build_replays': 0, 'production_and_existing_oracles_unchanged': True,
               'limitations': 'Local immutable Git evidence verification, not a fresh product test or URL fetch.'}
    (BASE / 'evidence-audit.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({'audit_exit': 0, 'immutable_git_links': len(checked), 'image_hash_matches': len(images),
                      'recorded_r10': '2 failed / 4 passed / 0 skipped',
                      'recorded_r13': '3 failed / 0 passed / 0 skipped',
                      'no_replays_or_production_edits': True}, indent=2))


if __name__ == '__main__':
    main()
