# R10-15 owned-input cleanup: strict RED regression handoff

Owner: `ses_de56780c8ffe7LgwvwdfR5qFQD`, SAME-ID continuation,2026-11-27.
Own branch: `agents/r10-15-owned-input-cleanup`; base checkpoint:
`3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab` (**not final freeze**).

## Scope and Agile acceptance

R03-15-F1 is one genuine input-ownership cleanup work item, not six/thirteen fake
tickets. R04 owns issue/PR writes and integration; R04/16 owns `normalize.py`.
This worker publishes only NEW tests, own notes/report and compact evidence.
No production/existing-oracle edit, install, shared environment mutation or spawn.
Latest R10 own-branch publication authority supersedes older blanket worker bans
only for these explicitly owned paths. Root is point of contact.

Acceptance: library-owned Path resources close before downstream error returns,
even while caller retains traceback; caller-owned streams remain open/usable.
Dependency: R04/16 normalizer handback/fix, then independent rerun/review and remote
CI. No issue created/closed by worker; R04 must map or create at most a genuine
ownership work item. Full production/900 legitimate completed issues remains unmet.

## Executed evidence

Existing MAIN venv used read-only; own checkpoint `PYTHONPATH`, bytecode off,
pytest plugin autoload disabled. Python3.12.16/Windows11, pytest9.2.0,
pyarrow26.0.1. Actual own-source `normalize.py` SHA256:
`0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83`.

Portable commands are in `tests/r10_probes/role15/README.md`. Exact final local
pytest suffix also used `--basetemp=artifacts/r10-15/pytest-published
--junitxml=artifacts/r10-15/cleanup-published.xml` and `-o junit_family=legacy`.
The local artifact directories are unique/owned and are **not** committed.

| Check | Exit | Actual result |
|---|---:|---|
| Initial owned41cases |1|29pass/12fail/0skip,7.97s|
| Six existing format suites + final43owned cases (before annotation-only type correction) |1|277pass/13fail/0skip,11.11s; existing247allpass|
| **Exact publish-version owned43cases** |**1**|**30pass/13fail/0skip,1.91s**|
| `python -m ruff check tests/r10_probes/role15` |0|All checks passed|
| `python -m mypy tests/r10_probes/role15 --cache-dir artifacts/r10-15/mypy-cache` |0|1sourcefile; initial two own rows-inference errors corrected with annotation only|

Eleven owned-input failures: JSONL flatten before/after inference prefix and plan,
CSV/TSV plan, Arrow IPC file/stream flatten and plan, Parquet flatten and plan.
Every case observes actual `.closed=False` and retained-traceback rename failure
`PermissionError/errno13/WinError32`. Parser-originated/ordinary-success controls
and eager JSON Path downstream errors close owned files correctly.

Two additional strict caller-ownership failures occur on second-line invalid
JSONL (StringIO and actual caller-opened file). Malformed first line leaves the
borrowed stream open. Standalone with/without-BOM and direct read-only generator
discrimination confirms `_without_bom` delegates `yield from iterator`, forwarding
`close()` to the borrowed stream when the parser unwinds after entering delegation.
This is a separately traced ownership edge within cleanup acceptance, not a false
claim that every manifestation originates at an identical line.

## Minimal ownership-safe proposal (NOT implemented)

Unwind library-owned source-generator chains in guaranteed finally paths across
prefix inference, plan and consumption (`normalize.py:202-234,479-504,689-709`).
Avoid forwarding wrapper close to borrowed text inputs (`_without_bom:89-94`),
e.g. non-owning iteration rather than close-forwarding delegation. Do not blindly
close every iterable; preserve borrowed streams/Arrow readers. No source diff or
GREEN claim is included in this test/evidence branch.

## Provenance, publication and limits

Baseline0c5fa82 remains preserved:269pass/1strictclosefailure/0skip and eight real
diagnostic observations (six downstream WinError32 locks,two close/renamecontrols).
`baseline-provenance.json` names original hashes; baseline was not relabeled as a
new checkpoint run. `summary.json` contains current counts/failure index/hash data.
Raw local logs/XML retain every RED and initial own-type-check failure; only compact
sanitized evidence is staged. No credentials/helper output or private datasets.

Authenticated in-memory GCM GET/user verified `sandeshbagmare` (HTTP200); intended
public repo GET200/pushpermissiontrue/clean HTTPSorigin verified. Own remote branch
was absent (ls-remote exit2) before creation; checkpoint object and ownbranch verified.
Commit/push/readback receipt is written to owner's MAIN note/report only after actual
commands; this payload does not preclaim an unexecuted push.

No final signoff, complete SDLC/900 claim, default-branch integration, issue closure,
independent review, browser semantics, full build/scale/MCP/DeepAgent or remote CI
pass. Actual file-lock effect is Windows-specific; portable handle state is checked
elsewhere but not yet executed on another OS. Optional unavailable pyarrow would
be a precise skip, not a pass. Production fixes remain blocked by source ownership.

**Next action:** R04 takes the NEW strict tests without weakening them, fixes owned
unwind and borrowed-stream boundary after16handback, then runs the portable command
and relevant existing suites on frozen source and requests independent verification.
