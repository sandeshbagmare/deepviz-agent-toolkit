"""No implicit product imports: consume only explicitly supplied live browser evidence."""
import json
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption('--host-evidence', help='Actual role14 host-observations.json from unchanged HTML')


@pytest.fixture(scope='session')
def cases(request):
    name = request.config.getoption('--host-evidence')
    if not name:
        pytest.fail('Explicit actual --host-evidence required; never skip or infer browser success')
    evidence = json.loads(Path(name).read_text(encoding='utf-8'))
    assert evidence['source_commit'] == '7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6'
    assert len(evidence['cases']) == 5
    return {case['id']: case for case in evidence['cases']}
