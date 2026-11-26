# C00 recovery-document verification

Date: 2026-11-27. Producer: C00, session `ses_de6e9da62ffe4nQ5DMuAaht0xL`.
Scope: recovery documentation only, not product correctness or independent release acceptance.
Working directory: DeepViz repository root. Interpreter: project `.venv/Scripts/python.exe`.

## Executed command

The following inline Python was passed through PowerShell's literal here-string to the project interpreter (`@' ... '@ | .\.venv\Scripts\python.exe -`):

```python
from pathlib import Path
import re
import subprocess

root = Path.cwd()
owned = [root / 'AGENTS.md', root / 'RESUME.md']
owned += [path for path in (root / 'docs/coordination').rglob('*.md')
          if path.name not in {'C17-integration.md', 'C18-recovery-audit.md'} or path.parent.name == 'tasks']
for path in owned:
    text = path.read_text(encoding='utf-8')
    assert text.strip(), f'Empty file: {path.relative_to(root)}'
    assert all(line == line.rstrip() for line in text.splitlines()), f'Trailing whitespace: {path}'
    assert text.count('```') % 2 == 0, f'Unclosed fence: {path}'
resume = (root / 'RESUME.md').read_text(encoding='utf-8')
for link in re.findall(r'`([^`]+\.md)`', resume):
    assert (root / link).is_file(), f'Broken resume reference: {link}'
roster = (root / 'docs/coordination/ROSTER.md').read_text(encoding='utf-8')
assert '22 running agents total' in roster
assert 'ses_de6ddc25affeMo5NjdAuqfub72' in roster
assert 'ses_de6dc95eeffej0nH3Io6H3qwqU' in roster
assert 'C17 may fill21' in roster and 'C18' in roster
assert 'Recovery documentation only' in roster
old = (root / 'docs/coordination/tasks/C16-integration-lead.md').read_text(encoding='utf-8')
assert 'SUPERSEDED' in old
brief = (root / 'docs/coordination/BRIEF.md').read_text(encoding='utf-8')
for required in ('actual session ID', 'dirty paths', 'exit codes', 'limitations', 'Next executable action:'):
    assert required in brief, f'Missing report field: {required}'
request = (root / 'docs/coordination/REQUEST.md').read_text(encoding='utf-8')
assert request.count('- [ ]') == 11, 'Acceptance checklist changed unexpectedly'
print(f'PASS: read-back, whitespace, fences and restart links for {len(owned)} coordination files')
print('PASS: actual child IDs, exclusive product/recovery ownership, superseded old assignment, 22-total cap')
print('PASS: report provenance/next-action fields and 11 explicitly unchecked acceptance criteria')
check = subprocess.run(['git', 'diff', '--check', '--', 'AGENTS.md', 'RESUME.md', 'docs/coordination'], text=True)
assert check.returncode == 0, 'Git whitespace verification failed'
print('PASS: git diff --check for recovery scope')
```

## Observed result

Exit code: **0**. No tests skipped or product suites run. Output:

```text
PASS: read-back, whitespace, fences and restart links for 15 coordination files
PASS: actual child IDs, exclusive product/recovery ownership, superseded old assignment, 22-total cap
PASS: report provenance/next-action fields and 11 explicitly unchecked acceptance criteria
PASS: git diff --check for recovery scope
```

The15-file count is the observed snapshot, not a fixed future expectation; other workers were adding their own coordination files concurrently. The command does not establish actual live-agent concurrency over time, agent completion, remote backup, code correctness or final acceptance. Those require C17's runtime/slot evidence and candidate-specific verification. Fresh checks are required after substantive edits.

## Refined final scoped verification

A second executed here-string/project-interpreter check (exit0) used the explicit13 C00 paths instead of walking concurrent worker files: `AGENTS.md`, `RESUME.md`, the five coordination root documents above, `reports/C00-recovery.md`, four saved task briefs, and this evidence file. Fence detection was refined to `len(re.findall(r'^```', text, flags=re.MULTILINE)) % 2 == 0`, because the initial saved checker itself contains literal backticks inside its code. The same restart links, IDs, superseded assignment, ownership,22-total reservation,11 unchecked criteria and scoped Git whitespace check were re-executed.

```text
PASS: 13 explicitly C00-owned recovery files, valid fences/references/whitespace
PASS: actual child identities, exclusive ownership, superseded C16, 21+1=22 reservation, honest acceptance gaps
PASS: scoped git diff --check; product tests not run by C00
```

This is the latest C00 author-check result. C18's independent audit and C17's product verification remain distinct evidence.

## Complete reproducible post-audit checker

The full current13-path checker below supersedes the summarized refinement above. Invoke its exact body using `@' ... '@ | .\.venv\Scripts\python.exe -` from the project root. It incorporates C18 F2/F3/F4 recovery fixes and the release of C18's former1 slot, so the current budget is22 inclusive rather than the historical21+1 split. It does **not** certify C17's F1 live-register repair or product gates.

```python
from pathlib import Path
import re
import subprocess

root = Path.cwd()
paths = ['AGENTS.md', 'RESUME.md', 'docs/coordination/STATE.md',
         'docs/coordination/ROSTER.md', 'docs/coordination/BRIEF.md',
         'docs/coordination/REQUEST.md', 'docs/coordination/WORKLOG.md',
         'docs/coordination/reports/C00-recovery.md',
         'docs/coordination/tasks/C16-integration-lead.md',
         'docs/coordination/tasks/C17-integration.md',
         'docs/coordination/tasks/C17-capacity-steering.md',
         'docs/coordination/tasks/C18-recovery-audit.md',
         'docs/coordination/evidence/C00-document-check.md']
texts = {name: (root / name).read_text(encoding='utf-8') for name in paths}
for name, text in texts.items():
    assert text.strip(), name
    assert all(line == line.rstrip() for line in text.splitlines()), name
    assert len(re.findall(r'^```', text, flags=re.MULTILINE)) % 2 == 0, name
for name in re.findall(r'`([^`]+\.md)`', texts['RESUME.md']):
    assert (root / name).is_file(), name
live = 'docs/coordination/C17-live-slots.md'
assert (root / live).is_file()
for name in ['AGENTS.md', 'RESUME.md', 'docs/coordination/STATE.md', 'docs/coordination/ROSTER.md']:
    assert live in texts[name], name
rules = texts['AGENTS.md']
assert 'C00 alone updates' in rules and 'C17 alone owns' in rules
assert 'The coordinator alone' not in rules
assert 'reserve its slot in the roster' not in rules
roster = texts['docs/coordination/ROSTER.md']
assert '22 running agents total' in roster and 'C17 owns the full22-slot inclusive budget' in roster
assert all(identity in roster for identity in ['ses_de6ddc25affeMo5NjdAuqfub72', 'ses_de6dc95eeffej0nH3Io6H3qwqU'])
assert 'completed; evidence received; slot released to C17' in roster
assert 'SUPERSEDED' in texts['docs/coordination/tasks/C16-integration-lead.md']
assert texts['docs/coordination/REQUEST.md'].count('- [ ]') == 11
assert 'Other worker reports, task files' in texts['docs/coordination/reports/C00-recovery.md']
assert subprocess.run(['git', 'diff', '--check', '--', 'AGENTS.md', 'RESUME.md', 'docs/coordination']).returncode == 0
print(f'PASS: {len(paths)} explicit recovery files; readable, whitespace/fences/restart references valid')
print('PASS: named recovery/product owners, direct live-register links, real child IDs, superseded C16, C18 completion')
print('PASS: 22-inclusive global budget and 11 honest acceptance gaps; scoped Git whitespace clean')
print('NOT CERTIFIED: live-register F1 repair, actual ongoing concurrency, product or release acceptance')
```

Observed execution of that exact command: **exit0**. Output:

```text
PASS: 13 explicit recovery files; readable, whitespace/fences/restart references valid
PASS: named recovery/product owners, direct live-register links, real child IDs, superseded C16, C18 completion
PASS: 22-inclusive global budget and 11 honest acceptance gaps; scoped Git whitespace clean
NOT CERTIFIED: live-register F1 repair, actual ongoing concurrency, product or release acceptance
```

Earlier author-check results remain historical. This fresh result verifies only the explicitly named post-audit recovery checks; it is not independent product signoff.
