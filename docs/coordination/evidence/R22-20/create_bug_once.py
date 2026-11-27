"""One R22-authorized F20 issue creation; refuse repeats and uncertain outcomes."""
from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import UTC, datetime

from github_discovery import BASE, OUTPUT, ApiFailure, Client, discover, issue_view


def save(name: str, value: dict) -> None:
    (OUTPUT / name).write_text(json.dumps(value, indent=2), encoding='utf-8')


def specific_plotly_bug(text: str) -> bool:
    lowered = text.lower()
    return ('f20-plotly-literal-text' in lowered
            or ('plotly' in lowered and bool(re.search(r'\banchors?\b|literal.text|r13-hover|r13-legend', lowered))))


def main() -> None:
    client = None
    attempted = False
    try:
        if (OUTPUT / 'post-attempt.json').exists():
            raise ApiFailure('prior-attempt-stop-no-repeat')
        decision = json.loads((OUTPUT / 'dedup-decision.json').read_text(encoding='utf-8'))
        if decision['decision'] != 'create-one' or decision['specific_existing_bug_matches']:
            raise ApiFailure('create-not-authorized-by-decision')
        body = (OUTPUT / 'issue-body.md').read_text(encoding='utf-8')
        audit = json.loads((OUTPUT / 'evidence-audit.json').read_text(encoding='utf-8'))
        body_sha = hashlib.sha256(body.encode('utf-8')).hexdigest()
        if audit['issue_body_utf8_sha256'] != body_sha or audit['invalid_permalinks']:
            raise ApiFailure('body-or-evidence-audit-mismatch')
        if '<!-- deepviz-bug-key: F20-PLOTLY-LITERAL-TEXT -->' not in body:
            raise ApiFailure('wrong-bug-scope')
        if not decision['title'].startswith('Bug: Plotly data labels, legend and hover'):
            raise ApiFailure('wrong-title-scope')

        # Fresh expected identity, repository and complete dedup snapshot just before POST.
        client = Client()
        refreshed = discover(client)
        save('prewrite-discovery.json', refreshed)
        candidates = [item for item in refreshed['open_issues']
                      if specific_plotly_bug(item['title'] + '\n' + (item['body'] or ''))]
        # Comments on broad parent stories could contain a newer specific bug report.
        for item in refreshed['open_issues']:
            if item['comments']:
                for page in range(1, 101):
                    comments = client.get(BASE + f'/issues/{item["number"]}/comments?per_page=100&page={page}')
                    if not isinstance(comments, list):
                        raise ApiFailure('bad-comments-page')
                    for comment in comments:
                        if specific_plotly_bug(comment.get('body') or ''):
                            # Only exact, manually read broad-triage comments may be classified
                            # nonduplicates. New/edited matching text still stops before POST.
                            body_hash = hashlib.sha256((comment.get('body') or '').encode('utf-8')).hexdigest()
                            reviewed = any(
                                rule['issue'] == item['number'] and rule['comment_id'] == comment.get('id')
                                and rule['body_utf8_sha256'] == body_hash
                                for rule in decision.get('reviewed_nonduplicate_comments', [])
                            )
                            if reviewed:
                                continue
                            candidates.append({'number': item['number'], 'title': item['title'],
                                               'html_url': comment['html_url'], 'matched_in': 'comment'})
                    if len(comments) < 100:
                        break
                else:
                    raise ApiFailure('incomplete-comments-pagination-stop')
        if candidates:
            save('new-specific-match-blocker.json', {'matches': candidates, 'mutations': 0,
                                                    'disposition': 'STOP for dedup decision; no automatic POST'})
            raise ApiFailure('new-specific-duplicate-stop')
        post_path = BASE + '/issues'
        payload = {'title': decision['title'], 'body': body}
        # Persist BEFORE the sole attempt. Even an ambiguous network outcome must not be retried.
        save('post-attempt.json', {'attempted_utc': datetime.now(UTC).isoformat(),
                                   'method': 'POST', 'path': post_path, 'maximum_attempts': 1,
                                   'body_utf8_sha256': body_sha, 'title': decision['title'],
                                   'retry_policy': 'NEVER retry this attempt; inspect receipt or handoff R04'})
        attempted = True
        request = urllib.request.Request('https://api.github.com' + post_path, method='POST',
                                         data=json.dumps(payload).encode('utf-8'), headers={
                                             'Authorization': 'Bearer ' + client._token,
                                             'Accept': 'application/vnd.github+json',
                                             'Content-Type': 'application/json',
                                             'User-Agent': 'deepviz-r22-role20-one-authorized-bug',
                                         })
        try:
            with client._opener.open(request, timeout=60) as response:
                status = response.status
                created = json.load(response)
        except urllib.error.HTTPError as error:
            client.calls.append({'method': 'POST', 'path': post_path, 'status': error.code})
            raise ApiFailure('post-http-stop-no-retry', error.code) from None
        except Exception:
            raise ApiFailure('post-transport-ambiguous-stop-no-retry') from None
        client.calls.append({'method': 'POST', 'path': post_path, 'status': status})
        save('post-response.json', {'http_status': status, 'issue': issue_view(created),
                                   'body_utf8_sha256': body_sha, 'mutations_attempted': 1})
        if status != 201:
            raise ApiFailure('unexpected-post-status-stop', status)
        number = created.get('number')
        if type(number) is not int or number <= 0:
            raise ApiFailure('missing-returned-issue-number-stop')
        actual = client.get(BASE + f'/issues/{number}')
        expected_url = f'https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/{number}'
        if (actual.get('html_url') != expected_url or actual.get('title') != decision['title']
                or actual.get('body') != body or actual.get('state') != 'open'
                or 'pull_request' in actual):
            raise ApiFailure('issue-get-readback-mismatch-stop')
        receipt = {'observed_utc': datetime.now(UTC).isoformat(), 'http_post_status': status,
                   'http_get_status': client.calls[-1]['status'], 'number': number,
                   'html_url': expected_url, 'title': actual['title'], 'state': actual['state'],
                   'body_utf8_sha256': body_sha, 'body_exact_match': True, 'mutations_attempted': 1,
                   'create_count': 1, 'comment_count': 0, 'closures_or_pr_or_source_writes': 0,
                   'calls': client.calls, 'source_fix_owner': 'R04 _plotly',
                   'test_replays': 0, 'final_signoff': False}
        save('issue-receipt.json', receipt)
        print(json.dumps(receipt, indent=2))
    except ApiFailure as error:
        failure = {'kind': error.kind, 'http_status': error.status,
                   'mutation_attempted_this_run': attempted,
                   'calls': client.calls if client is not None else [],
                   'disposition': 'STOP, no retries/alternate identity/interface; handoff R04'}
        save('publication-blocker.json', failure)
        print(json.dumps(failure, indent=2))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
