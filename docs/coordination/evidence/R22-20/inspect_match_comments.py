"""Read only the two dedup-blocking GitHub comments; no mutation or retry."""
from __future__ import annotations

import json
from datetime import UTC, datetime

from github_discovery import BASE, OUTPUT, ApiFailure, Client


def main() -> None:
    client = Client()
    records: list[dict] = []
    for issue, comment_id in ((27, 7221698876), (20, 7221697848)):
        comments = client.get(BASE + f'/issues/{issue}/comments?per_page=100&page=1')
        matches = [item for item in comments if item.get('id') == comment_id]
        if len(matches) != 1:
            raise ApiFailure('expected-comment-not-found-or-duplicate')
        comment = matches[0]
        records.append({'issue': issue, 'comment_id': comment_id, 'html_url': comment.get('html_url'),
                        'created_at': comment.get('created_at'), 'updated_at': comment.get('updated_at'),
                        'user_login': (comment.get('user') or {}).get('login'),
                        'body': comment.get('body')})
    result = {'observed_utc': datetime.now(UTC).isoformat(), 'records': records,
              'calls': client.calls, 'mutations': 0,
              'disposition': 'Read-only classification; no automatic write'}
    (OUTPUT / 'match-comment-readback.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'readback_exit': 0, 'comments': [
        {'issue': record['issue'], 'comment_id': record['comment_id'], 'html_url': record['html_url'],
         'body_preview': (record['body'] or '')[:220].replace('\n', ' ')} for record in records],
                      'mutations': 0}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except ApiFailure as error:
        print(json.dumps({'readback_exit': 1, 'kind': error.kind, 'mutations': 0,
                          'disposition': 'STOP; no retry/alternate identity'}, indent=2))
        raise SystemExit(1) from None
