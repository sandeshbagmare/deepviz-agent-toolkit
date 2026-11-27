"""Offline negative controls for query coverage; never contact a network."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('r14_advisory_query', Path(__file__).with_name('query_advisories.py'))
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def test_scoped_package_version_is_encoded_and_ecosystem_explicit():
    path = probe.initial_path('@antv/g2', '5.4.8', 'reviewed')
    assert path == '/advisories?ecosystem=npm&affects=%40antv%2Fg2%405.4.8&type=reviewed&per_page=100&sort=published&direction=desc'


@pytest.mark.parametrize('url', ['http://api.github.com/advisories', 'https://evil.invalid/advisories',
                               'https://api.github.com/user', 'https://token@api.github.com/advisories'])
def test_pagination_rejects_other_origins_or_resources(url):
    with pytest.raises(AssertionError):
        probe.next_path(f'<{url}>; rel="next"', probe.initial_path('vega', '6.4.0', 'reviewed'))


def test_pagination_must_preserve_exact_package_version_filter():
    with pytest.raises(AssertionError):
        probe.next_path('<https://api.github.com/advisories?ecosystem=npm&affects=vega&type=reviewed&per_page=100&sort=published&direction=desc&after=A>; rel="next"',
                        probe.initial_path('vega', '6.4.0', 'reviewed'))


def test_next_cursor_accepted_without_losing_filter():
    first = probe.initial_path('vega', '6.4.0', 'reviewed')
    assert probe.next_path(f'<https://api.github.com{first}&after=A>; rel="next"', first) == first + '&after=A'
    assert probe.next_path('', first) is None


class FakeClient:
    def __init__(self, body, status=200, link=''):
        self.body, self.status, self.link = body, status, link

    def get(self, _):
        return self.body, {'status': self.status, 'headers': {'Link': self.link}}


def test_zero_page_is_coverage_only_not_a_safety_verdict():
    result = probe.query(FakeClient([]), 'vega', '6.4.0', 'reviewed', 2)
    assert result['complete_for_requested_filter'] is True and result['count'] == 0
    assert 'safe' not in result and 'vulnerable' not in result


def test_http_or_pagecap_error_is_not_zero_match_success():
    failed = probe.query(FakeClient(None, 429), 'vega', '6.4.0', 'reviewed', 2)
    assert failed['count'] == 0 and failed['complete_for_requested_filter'] is False
    first = probe.initial_path('vega', '6.4.0', 'reviewed')
    capped = probe.query(FakeClient([], link=f'<https://api.github.com{first}&after=A>; rel="next"'), 'vega', '6.4.0', 'reviewed', 1)
    assert capped['count'] == 0 and capped['complete_for_requested_filter'] is False
    assert 'page cap' in capped['gap']


def test_wrong_package_in_response_is_not_silently_accepted():
    with pytest.raises(AssertionError, match='requested package'):
        probe.query(FakeClient([{'type': 'reviewed', 'vulnerabilities': [{'package': {'ecosystem': 'pip', 'name': 'vega'}}]}]),
                    'vega', '6.4.0', 'reviewed', 2)
