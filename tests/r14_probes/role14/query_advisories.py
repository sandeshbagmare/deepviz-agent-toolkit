"""Read bounded official GitHub advisory pages for already inventoried runtime versions.

No install, downloaded-code execution, vulnerability inference or automatic ticket writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

TARGETS = (
    ('vega', '6.4.0', 'npm emitted script'),
    ('vega-lite', '6.5.0', 'npm emitted script'),
    ('vega-embed', '7.4.0', 'npm emitted script'),
    ('@antv/g2', '5.4.8', 'npm/Python emitted script'),
    ('plotly.js-dist-min', '4.3.0', 'npm emitted package'),
    ('plotly.js', '4.3.0', 'canonical project alias for npm emitted bundle'),
    ('plotly.js', '3.7.0', 'canonical JS project for Python embedded bundle'),
    ('plotly.js-dist-min', '3.7.0', 'dist alias coverage for Python embedded bundle'),
)
API_VERSION = '2026-03-10'
MAX_BYTES = 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def initial_path(package: str, version: str | None, kind: str) -> str:
    return '/advisories?' + urlencode({'ecosystem': 'npm', 'affects': package + ('@' + version if version else ''),
                                      'type': kind, 'per_page': '100', 'sort': 'published', 'direction': 'desc'})


def next_path(link: str, current: str) -> str | None:
    links = re.findall(r'<([^>]+)>;\s*rel="([^"]+)"', link)
    found = [url for url, relation in links if relation == 'next']
    assert len(found) <= 1, 'Ambiguous pagination'
    if not found:
        return None
    target = urlsplit(found[0])
    assert target.scheme == 'https' and target.netloc == 'api.github.com' and target.path == '/advisories'
    assert not target.fragment and not target.username and not target.password
    expected = parse_qs(urlsplit(current).query)
    actual = parse_qs(target.query)
    for key in ['ecosystem', 'affects', 'type', 'per_page', 'sort', 'direction']:
        assert expected[key] == actual.get(key), 'Pagination changed query coverage'
    assert set(actual) <= set(expected) | {'after', 'before'}, 'Unexpected pagination parameter'
    return target.path + '?' + target.query


class Client:
    def __init__(self, authenticate: bool):
        self.token: str | None = None
        self.requests: list[dict[str, Any]] = []
        self.opener = build_opener(NoRedirect())
        if authenticate:
            result = subprocess.run(['git', '-c', 'credential.interactive=false', 'credential', 'fill'],
                                    input='protocol=https\nhost=github.com\n\n', capture_output=True,
                                    text=True, timeout=20, check=False)
            assert result.returncode == 0, 'Sanitized GCM lookup failed'
            values = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
            self.token = values.get('password')
            assert self.token, 'Credential absent; no authenticated query'
            identity, evidence = self.get('/user')
            assert evidence['status'] == 200 and isinstance(identity, dict) and identity.get('login') == 'sandeshbagmare', 'Unexpected account or authentication failure'

    def get(self, api_path: str) -> tuple[Any, dict[str, Any]]:
        assert api_path.startswith(('/advisories?', '/user')) and not api_path.startswith('//')
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'DeepViz-R14-14-bounded-advisories',
                   'X-GitHub-Api-Version': API_VERSION}
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        record: dict[str, Any] = {'url': 'https://api.github.com' + api_path,
            'retrieved_at_utc': datetime.now(UTC).isoformat(), 'requested_api_version': API_VERSION}
        self.requests.append(record)
        try:
            with self.opener.open(Request(record['url'], headers=headers), timeout=40) as response:
                body = response.read(MAX_BYTES + 1)
                record.update(status=response.status, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                    headers={key: response.headers.get(key) for key in ['Link', 'X-RateLimit-Limit', 'X-RateLimit-Remaining',
                        'X-RateLimit-Reset', 'X-RateLimit-Resource', 'X-GitHub-Api-Version-Selected'] if response.headers.get(key) is not None})
                if len(body) > MAX_BYTES:
                    record['error'] = 'response-size-bound'
                    return None, record
                try:
                    return json.loads(body), record
                except json.JSONDecodeError:
                    record['error'] = 'invalid-JSON'
                    return None, record
        except HTTPError as error:
            record.update(status=error.code, error='HTTP-error', headers={key: error.headers.get(key) for key in
                ['Retry-After', 'X-RateLimit-Remaining', 'X-RateLimit-Reset', 'X-RateLimit-Resource'] if error.headers.get(key) is not None})
        except (URLError, TimeoutError):
            record.update(status=None, error='network-or-timeout')
        return None, record


def query(client: Client, package: str, version: str | None, kind: str, pages: int) -> dict[str, Any]:
    result: dict[str, Any] = {'ecosystem': 'npm', 'package': package, 'version': version,
        'type': kind, 'pages': [], 'advisories': [], 'complete_for_requested_filter': False}
    current = initial_path(package, version, kind)
    for _ in range(pages):
        data, evidence = client.get(current)
        result['pages'].append(evidence)
        if evidence['status'] != 200 or not isinstance(data, list) or 'error' in evidence:
            result['gap'] = 'HTTP/shape/size error; do not interpret as zero matches'
            break
        evidence['advisory_count'] = len(data)
        for item in data:
            assert isinstance(item, dict) and item.get('type') == kind
            assert any(v.get('package', {}).get('name') == package and v.get('package', {}).get('ecosystem') == 'npm' for v in item.get('vulnerabilities', [])), 'Advisory does not match requested package/ecosystem'
            result['advisories'].append({key: item.get(key) for key in ['ghsa_id', 'cve_id', 'html_url', 'summary', 'description',
                'type', 'severity', 'published_at', 'updated_at', 'github_reviewed_at', 'withdrawn_at', 'vulnerabilities', 'references']})
        current_next = next_path(evidence.get('headers', {}).get('Link', ''), current)
        if current_next is None:
            result['complete_for_requested_filter'] = True
            break
        current = current_next
    if not result['complete_for_requested_filter'] and 'gap' not in result:
        result['gap'] = 'page cap reached with next cursor remaining'
    result['count'] = len(result['advisories'])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--authenticate', action='store_true', help='GCM in-memory only; verify expected GET/user')
    parser.add_argument('--max-pages', type=int, default=2, choices=[1, 2])
    args = parser.parse_args()
    args.out.mkdir(parents=False, exist_ok=False)
    client = Client(args.authenticate)
    queries = []
    for package, version, role in TARGETS:
        for kind in ['reviewed', 'unreviewed', 'malware']:
            result = query(client, package, version, kind, args.max_pages)
            result['inventory_relationship'] = role
            queries.append(result)
            (args.out / 'query-progress.json').write_text(json.dumps({'queries': queries, 'requests': client.requests}, indent=2), encoding='utf-8')
    for package in dict.fromkeys(package for package, _, _ in TARGETS):
        queries.append(query(client, package, None, 'reviewed', args.max_pages))
        (args.out / 'query-progress.json').write_text(json.dumps({'queries': queries, 'requests': client.requests}, indent=2), encoding='utf-8')
    result = {'retrieved_at_utc': datetime.now(UTC).isoformat(), 'target_source': '5340bc69b7203ad7a9166543062482d819f9b705',
        'runtime_inventory_source': '3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab', 'requested_api_version': API_VERSION,
        'authenticated_expected_user_verified': args.authenticate, 'max_pages_per_query': args.max_pages,
        'queries': queries, 'requests': client.requests,
        'limits': ['Exact-version results use GitHub server affected-version filtering; no local range/exploitability inference.',
            'All-version reviewed queries provide historical range context, not execution-path evidence.',
            'Complete bounded query pages do not prove database completeness or package safety.',
            'No transitive packages, future versions, undisclosed vulnerabilities or automatic issue/dependency writes.']}
    (args.out / 'advisory-queries.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    gaps = [q for q in queries if not q['complete_for_requested_filter']]
    print(json.dumps({'queries': len(queries), 'requests': len(client.requests), 'incomplete_queries': len(gaps),
        'exact_version_advisory_occurrences': sum(q['count'] for q in queries if q['version'] is not None),
        'range_context_occurrences': sum(q['count'] for q in queries if q['version'] is None),
        'meaning': 'Recorded query coverage only, NOT a safe/unsafe verdict.'}, indent=2))
    raise SystemExit(1 if gaps else 0)


if __name__ == '__main__':
    main()
