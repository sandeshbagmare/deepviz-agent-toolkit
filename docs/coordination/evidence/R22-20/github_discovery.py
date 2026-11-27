"""Role20 read-only GitHub dedup discovery; credentials never leave memory."""
from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

REPOSITORY = 'sandeshbagmare/deepviz-agent-toolkit'
BASE = f'/repos/{REPOSITORY}'
OUTPUT = Path(__file__).resolve().parent


class ApiFailure(Exception):
    """Contain only a sanitized error category and HTTP status."""

    def __init__(self, kind: str, status: int | None = None):
        self.kind = kind
        self.status = status


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self) -> None:
        try:
            credential = subprocess.run(
                ['git', '-c', 'credential.interactive=false', 'credential', 'fill'],
                input='protocol=https\nhost=github.com\n\n', capture_output=True,
                text=True, timeout=20, check=True,
            )
            fields = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
            self._token = fields['password']
            origin = subprocess.run(['git', 'remote', 'get-url', 'origin'], check=True,
                                    capture_output=True, text=True, timeout=20).stdout.strip()
            if origin != f'https://github.com/{REPOSITORY}.git':
                raise ApiFailure('unauthorized-origin')
        except ApiFailure:
            raise
        except Exception:
            raise ApiFailure('credential-unavailable') from None
        self._opener = urllib.request.build_opener(NoRedirect())
        self.calls: list[dict] = []

    def get(self, path: str):
        if path != '/user' and not path.startswith(BASE + '/') and path != BASE:
            raise ApiFailure('unauthorized-api-path')
        request = urllib.request.Request('https://api.github.com' + path, headers={
            'Authorization': 'Bearer ' + self._token,
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'deepviz-r22-role20-qa-dedup',
        })
        try:
            with self._opener.open(request, timeout=60) as response:
                status = response.status
                result = json.load(response)
        except urllib.error.HTTPError as error:
            self.calls.append({'method': 'GET', 'path': path, 'status': error.code})
            raise ApiFailure('http-stop-no-retry', error.code) from None
        except Exception:
            raise ApiFailure('transport-or-json-stop-no-retry') from None
        self.calls.append({'method': 'GET', 'path': path, 'status': status})
        return result


def issue_view(issue: dict) -> dict:
    return {key: issue.get(key) for key in
            ('number', 'title', 'body', 'state', 'html_url', 'comments', 'created_at', 'updated_at')}


def discover(client: Client) -> dict:
    user = client.get('/user')
    if user.get('login') != 'sandeshbagmare':
        raise ApiFailure('wrong-identity')
    repository = client.get(BASE)
    if (repository.get('full_name') != REPOSITORY or not repository.get('has_issues')
            or repository.get('archived') or repository.get('default_branch') != 'main'):
        raise ApiFailure('repository-scope-or-default-mismatch')
    issues: list[dict] = []
    prs: list[dict] = []
    pages: list[dict] = []
    for page in range(1, 101):
        batch = client.get(BASE + f'/issues?state=open&per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ApiFailure('bad-issue-page')
        pages.append({'page': page, 'returned': len(batch)})
        for item in batch:
            (prs if 'pull_request' in item else issues).append(issue_view(item))
        if len(batch) < 100:
            break
    else:
        raise ApiFailure('incomplete-pagination-stop')
    required = {str(number): issue_view(client.get(BASE + f'/issues/{number}'))
                for number in (10, 21, 23)}
    return {'observed_utc': datetime.now(UTC).isoformat(), 'actual_user': user['login'],
            'repository': repository['full_name'], 'default_branch': repository['default_branch'],
            'public': not repository['private'], 'pagination_complete': True, 'pages': pages,
            'open_issues': issues, 'open_prs_excluded': prs, 'required_issue_reads': required,
            'calls': client.calls, 'mutations': 0}


def main() -> None:
    client = None
    try:
        client = Client()
        result = discover(client)
        (OUTPUT / 'discovery.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps({'actual_user': result['actual_user'], 'repository': result['repository'],
                          'default_branch': result['default_branch'],
                          'complete_open_issues': len(result['open_issues']),
                          'open_prs_excluded': len(result['open_prs_excluded']),
                          'pages': result['pages'], 'mutations': 0,
                          'titles': [{'number': item['number'], 'title': item['title']}
                                     for item in result['open_issues']]}, indent=2))
    except ApiFailure as error:
        failure = {'kind': error.kind, 'http_status': error.status,
                   'calls': client.calls if client is not None else [], 'mutations': 0,
                   'disposition': 'STOP, no retries or alternate identity; handoff R04'}
        (OUTPUT / 'discovery-blocker.json').write_text(json.dumps(failure, indent=2), encoding='utf-8')
        print(json.dumps(failure, indent=2))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
