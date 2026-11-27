# R10-04 — portable UTF-8 field-envelope regressions

**Status:** NEW regression validation complete on checkpoint; own-branch publication receipt pending actual execution. No production/policy/existing-oracle fix, final acceptance or whole-suite green claimed. Date2026-11-27.

## Owner, source and scope

- SAME-ID `ses_de5678314ffeuDXtC7RfGsbD6V`, native session_move verified. FULL MAIN R10common+04 and own R03 note/report read first, then current canonical/AGENTS/RESUME. No spawning; root handles rolling18–22 admission. POC=point of contact.
- Branch `agents/r10-04-utf8-field-envelope`, NEW clean worktree `C:/Users/bagma/AppData/Local/Temp/opencode/r10-04-utf8-field-envelope-ses_de5678314ffeuDXtC7RfGsbD6V`, base/checkpoint `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`. R03detached0c5/probes remain untouched. MAIN independently advances and is not the test source.
- Allowed publication paths ONLY: `tests/r10_probes/role04/`, this NEW report, `docs/coordination/evidence/R10-04/`, own actual-ID note. Normalizers belong16/R04; no production/global-policy/existing-test edits, installs/shared-env changes, other notes, shared-branch/issue/PR writes.
- Source/module/fixture/log hashes and compact exact results: [`../evidence/R10-04/utf8-envelope-checkpoint.json`](../evidence/R10-04/utf8-envelope-checkpoint.json). Raw logs/XML remain ignored under own `artifacts/local/R10-04/`, not staged. Python normalize module0473bce…, TSsource d1b45d2…/own compiled module adb0493… match recorded source identities; actual loaded paths are this worktree.

## Backlog / acceptance / dependencies

- Authenticated GET2026-11-27T02:27:42.777199UTC: `/user`200=`sandeshbagmare`, repo200public/pushpermission=true, issues22/30each200open. Issue22is real bounded-stream/scale acceptance context; issue30is specifically schema numeric coercion, not a field-budget ticket claimed solved here. No ticket created/closed;900criterion not advanced by counting test cases.
- Acceptance: reusable NEW shared literal4095/4096/4097names and65535/65536/65537cells, full composite/array-index boundaries, exact Python4KiB/TS64KiB name difference, no truncation, first/late invalid consumption, bounded-state rejection and truthful512input→10output sampling/group-loss controls.
- This is a test/evidence lane, not a released product fix: original strict N11RED remains. Source-owner16/R04 changes invalidate affected evidence; independent non-author review/testing and final remote CI/integration/issue disposition remain R04 dependencies. No self-review called independent approval.

## Published test design and observations

- Four NEW portable files in `tests/r10_probes/role04/`: literal JSON fixtures, Python pytest, TS node:test and README with PowerShell/POSIX recipes. No private production byte counters imported.
- Both languages test72name cases (six explicit byte sizes ×four Unicode widths ×raw/composite/array-index) and12cell cases. The4097/65535/65536name cases are intentionally **rejected by Python, accepted by TS**, describing the checkpoint rather than changing shared policy. Both preserve cells through65536and reject65537. Accepted records/counts/strategy/no-warning and exact unchanged values are asserted.
- Near4096composite names use individually safe segments; separators and`.0` count. This avoids the historical64KiB nested fixture's earlier oversized-outer-key failure masking a final-composite check.
- Sixteen early-consumption controls/language reject exactly row1or41of80without consuming the tail, including beyond32-row prefix/10-row reservoir. TSiteratorclosure is asserted; Python caller closure is deliberately outside this lane.
- Each language has four lazy-state controls.512×61440=31457280logical payload bytes can safely consume all512and retain10with sampling/cardinality warnings, exact values/source-order (sample), and grouped counts`[1,1,1,1,1,1,1,1,1,503]`. Over16MiB retained-state controls reject specifically on the state budget: Python273reservoir/273group pulls; TS273reservoir/137group yields, before exhaustion (TSclosed=true). No prebuilt30MiB array.

## Exact checks at checkpoint

Commands run from own worktree; `$PY=C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`, `$env:PYTHONPATH=<own-worktree>/python/deepviz/src`, `$env:PYTHONUTF8='1'`; `$TSC=C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript/bin/tsc`. These installed tools were read-only. Python3.12.16/Nodev26.13.1/TypeScript7.0.2.

| Command | Actual result |
|---|---|
| `git worktree add -b agents/r10-04-utf8-field-envelope <NEW-own-directory> 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`; status/HEAD |0; initially clean exact-source own branch, configured author already present |
| `& $PY -m pytest tests/r10_probes/role04/test_utf8_field_envelope.py -q -s --junitxml=artifacts/local/R10-04/python-boundaries-final.xml` |0;104passed/0failed/0skipped1.42s; `python-boundaries-final.log/xml` |
| `& $PY -m ruff check tests/r10_probes/role04/test_utf8_field_envelope.py` |0; all checks passed, `ruff-final.log` |
| `& $PY -m mypy tests/r10_probes/role04/test_utf8_field_envelope.py` |0;1sourcefile/noissues, `mypy-final.log` |
| `node $TSC -p packages/deepviz/tsconfig.json`; `node $TSC --noEmit -p packages/deepviz/tsconfig.json` |0each; own source compiled/typechecked, `ts-build.log`,`ts-typecheck.log` |
| `node --test tests/r10_probes/role04/utf8-field-envelope.test.mjs` |0;105passed/0failed/0skipped1868.5154ms, `ts-boundaries-final.log` |
| `& $PY -m pytest tests/test_n11_resource_policy.py -q --tb=short --junitxml=artifacts/local/R10-04/n11-checkpoint.xml` |**1;22passed/4failed/0skipped1.45s**; same three raw64KiB-name positives plus nested64KiB-name positive, explicit4096-byte error. Existing tests untouched; `n11-checkpoint.log/xml` |
| `node --test packages/deepviz/test/test_n21_resource_policy.test.mjs` |0;23passed/0failed/0skipped2132.6926ms, `n21-checkpoint.log` |
| `git diff --exit-code 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab -- python packages schemas tests/test_n11_resource_policy.py` |0; production/schema/existing oracle unchanged |
| Captured in-memory GCM GET/user/repo/issues |0; fourHTTP200responses above; no APIwrite/token output/redirect following |
| `git -c credential.interactive=false ls-remote --exit-code --heads origin refs/heads/agents/r10-04-utf8-field-envelope` before publication |2, own remote branch absent; no existing ref overwritten |

First Python run104pass0skip0.84s/Ruff0; initial mypy1from two NEW probe-local dict inference errors. Local `row: dict[str, Any]` annotation corrected only test typing; final rerun above passed. Initial TS105pass0skip685.6573ms; no failing product behavior was fixed or hidden.

## Publication, limits and next action

- Publication plan (NOT an executed claim yet): stage only explicit owned files, inspect staged diff/whitespace/scope and credential scan, small meaningful commit, non-force push only own branch, verify remote SHA and save actual MAIN receipt. R04aloneintegrates/issues/PRs.
- Not run: full product suites/global lint/types, npmci/install, distributions/browser/visual gates,10Mscale/processRSS/continuous memory, non-author review/test or final CI. Finite state controls are not a memory/scale benchmark. Original fourREDpolicy positives remain uncorrected.
- **Current action:** commit/publish this scoped tested checkpoint; authentication is verified, no local blocker.
- **Next executable action:** explicit-path `git add -- <own seven files>` followed by staged scope/whitespace/credential checks; commit/non-force own push and actual remote SHA readback before returning. Then R04 reviews tests/policy distinction and reruns after16normalizer changes, without marking issue22or the full project complete.
