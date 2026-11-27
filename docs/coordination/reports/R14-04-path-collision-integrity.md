# R14-04 — flattened path / field collision integrity

**Status:** NEW finite integrity suite verified: **69 Python + 69 TypeScript passed, zero failures/skips**. No silent overwrite found in this corpus; no product defect/fix or new issue claimed. Scoped publication pending actual execution. 2026-11-27.

## Owner, exact source and allowed writes

- SAME-ID `ses_de5678314ffeuDXtC7RfGsbD6V`. FULL MAIN R14 common+04, own actual-ID note/R13 report/current canonical read before work; prework note/report saved. No spawning, new children, installs or service/auth/provider changes.
- Reused own branch `agents/r10-04-utf8-field-envelope`, initially clean at `ee5cf1971bc22acaf046dd25d92b5164497f4837`; old trees/evidence remain preserved. Exact published product target **`5340bc69b7203ad7a9166543062482d819f9b705`**. Before/after `git diff --exit-code <5340> -- python packages schemas` exit0; six relevant source files also matched immutable `git show <5340>:<path>` bytes and blob IDs. This establishes source equivalence, not a claim that own HEAD is5340.
- Loaded Python normalizer inside this own worktree, SHA-256 `0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83`; TS source `d1b45d2a55dfd05361184a57da952a0da735e9b6d72c2491f908ef27bda22371`. Reused own source-verified compiled normalizer `adb0493123fd478567212e76e2c6e52c828aeaa9eb5425c219b5b1a576689612`; compiled models/index hashes also recorded. No fresh build is claimed.
- Writes ONLY NEW `tests/r14_probes/role04/` (six portable files), this report, `evidence/R14-04/` and own actual-ID note. Production normalizers remain16-exclusive. No production/model/schema/policy/original-oracle changes, shared branch, issue/PR writes or other agent notes. R04 alone integrates and manages issues/PRs.
- Compact public-source/results/raw-log hash manifest: [`../evidence/R14-04/integrity-results.json`](../evidence/R14-04/integrity-results.json). Ignored raw artifacts are under own `artifacts/local/R14-04/`; no generated data or logs need publication.

## Contract and independent oracle

Architecture `docs/architecture.md:52–53` requires equal-length columns, explicit mapping and a flatten escaping/collision rule; capability docs require stable ambiguity/collision behavior. Actual public normalizers already enforce terminal duplicate checks: Python `normalize.py:467`, TS `normalize.ts:313`. Path selectors split on dots (Python265–295, TS58–75/274–283); no universal bracket/Unicode-index grammar is promised.

The NEW invariant never chooses a silent winner: preserve every explicitly mapped distinct key/value/logical row, or raise concise public collision/ambiguity error. Same-row collisions in the current unescaped dotted namespace require rejection, rather than silently merging11and29or dropping null. Across-row paths may share a field if each original row/value/count survives; that is a strict positive, not invented ambiguity.

| Per-language cases | Count | Actual observation |
|---|---:|---|
| Six genuine same-row collisions × two recursive key orders × records/JSON/explicit path |36| All reject via public ValueError/ValidationError with collision/ambiguity message≤240UTF-8bytes; inputs unchanged. Literal-dot, literal-index, deep array index, dotted child, numeric dictionary, null contribution covered. |
| Five noncolliding fixtures × records/JSONL |10| Exact keys/values/counts, strategy none, no warning or mutation. Brackets, zero-prefix strings, fullwidth dots, composed/combining Unicode, Latin/Cyrillic lookalikes and across-row origins preserved. |
| Scalar/mixed scalar+nested column integrity |3| Ordinary scalar columns exact in both. Python preserves both nested columns; TS clearly rejects ambiguous nested arrays. Collision columns reject safely in both. No silent column loss. |
| Explicit data_path positives |3| Correct nested branch selected rather than dotted literal sibling; ASCII list index and numeric-looking object key select the requested rows. Intentional explicit selection is not undisclosed loss. |
| Guarded collision row1or41of60 |12| Exactly1or41rows pulled/yielded, no tail consumed, no exhausted flag. Bounded invalid input is not hidden by32-row inference. Closure intentionally outside this lane. |
| Ordinary stream |1| Consumes all60and retains exact60records/count, no warning, including beyond inference prefix. |
| Corrupt-success oracle controls |3| Own exact assertion detects overwritten11→29, missing field and wrong count. No production mocking or fabricated red→green. |
| Literal Unicode fixture self-check |1| NFC-equivalent composed/combining keys are byte-distinct and carry independent values; fullwidth-dot/Cyrillic keys explicitly checked by escapes. |
| **Total** |**69**| **0 integrity failures observed per language**. This is finite evidence, not universal acceptance. |

## Separate naming-policy observations — not counted as passing tests or bugs

Four small observation fixtures per language were collected through public APIs (both collectors exit0):

- `data_path='groups.١'`: Python interprets Arabic-Indic digit1as index1and selects29; TS returns a concise unmatched-path error. Source cause: Python `str.isdecimal()/int` versus TSASCII`/^\d+$/`. The accepted index alphabet is unspecified; this difference is **not** labeled a data-loss defect or ticket.
- `groups.01`: both select index1/value29. Leading-zero policy remains unspecified.
- Literal key `groups[0]`: both select the literal key/value11; no-literal `groups[1]` rejects. No bracket-index capability inferred.
- Mixed noncolliding scalar/nested column inference differs as above, but both satisfy preserve-or-clear-reject. R04 may document these language-specific acceptance choices without treating rejection as silent loss.

**Minimal R04 proposal:** retain current collision guards and byte-distinct names; include these strict positives/negatives when reviewing later16handback. If exact cross-language index grammar is required, explicitly decide ASCII-only versus Unicode-decimal and bracket/escaping syntax, then release a separate owner-scoped change/test. No such policy/source edit is made here. No repeat of old4096/65536matrices, numerical SUM review or iterator cleanup.

## Exact commands, results and chronology

Run from own worktree with existing read-only `$PY=C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`, `$env:PYTHONPATH=<own>/python/deepviz/src`, `$env:PYTHONUTF8='1'`; Node uses the own checkout's source-verified `dist`.

| Command | Actual exit/result |
|---|---|
| `& $PY -m pytest tests/r14_probes/role04/test_path_collision_integrity.py -q --tb=short --junitxml=artifacts/local/R14-04/python-collision-final.xml` |0; **69passed/0failed/0skipped0.52s**, final log/XML retained |
| `& $PY -m ruff check tests/r14_probes/role04` |0; all checks passed |
| `& $PY -m mypy tests/r14_probes/role04` |0; two source files/no issues |
| `node --check tests/r14_probes/role04/path-collision-integrity.test.mjs` |0 |
| `node --test tests/r14_probes/role04/path-collision-integrity.test.mjs` |0; **69passed/0failed/0skipped332.5602ms** |
| `& $PY tests/r14_probes/role04/observe_path_grammar.py`; `node tests/r14_probes/role04/observe-path-grammar.mjs` |0each; four nonnormative observations each, not test-pass counts |
| Before/after target source diff and immutable-source hash collector |0; six target sources exact; own module identity verified |
| Final compact-manifest readback |0; six fixture/source files and11raw artifacts matched; compiled normalize/models/index hashed; source unchanged |
| Captured-memory GCM GET/user/repo/ownref/targetcommit/issue6 |0collector; fiveHTTP200responses at2026-11-27T14:28:23.787587UTC; account`sandeshbagmare`, pushpermissiontrue, ownrefee5cf19, actual published5340exists, issue6open. No APIwrite. |

Initial NEW suites had68pass/0fail/0skip each (Python0.56s/TS525.2136ms), Ruff/mypy0. Added independent Unicode fixture validity guard and reran final69each above; no producer/source fix happened.

One evidence collector attempt failed **before execution** with Python parse error at embedded trusted-JS triple quotes through PowerShell native`-c $script` conversion (exit1). Minimal quote-only reproduction confirmed nativeargumentexit1versus stdinexit0; corrected collector used `$script | & $PY -`, exit0. It did not rerun suites or alter product. Original failure/quote test retained honestly, no harness error counted as productRED.

## Publication, limitations and next action

- Pending small meaningful ownbranch commit: six NEWprobe/docs files, this report, sanitized evidenceJSON, own note; explicit staging/scope/whitespace/credential scans, non-force own push and exact remote-SHA receipt. Publication will not duplicateR10testcommit or stage another worker's paths.
- No full suites/global lint-types, fresh TSbuild/npmci, distributions, renderer/browser/visual, originalN11four-policy rerun/fix, role16changed source,10M/RSS/finalCI or independent final approval. Prior fourN11REDs remain historical/unresolved by this work. Issue6is a real existing formats backlog context, not closed here;900criterion not advanced by test-case counting.
- **Current action:** finish scoped test/evidence publication and return exact receipt for root/R04rollingtriage; no running job/local blocker.
- **One executable next action (R04 after receipt):** inspect `tests/r14_probes/role04/README.md` and this69/69evidence; preserve collision guards during16integration, decide naming grammar only if product parity requires it, and assign genuine independent candidate retests. No source/policy/oracle edit is authorized to this worker.
