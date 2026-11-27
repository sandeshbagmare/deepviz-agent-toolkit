# R10-01 portable correctness regressions

What this change does: Publishes NEW independent Python/TypeScript regression tests for connection-sibling loss, count-measure mapping and scalar-column naming. Strict failures and positive controls are retained; no production file or existing oracle changes.

## Ownership, source and lifecycle

- Owner/session: R03/R10 role01, ses_de5678335ffeI7xJrod5l25Q0Q (native identity reconfirmed), 2026-11-27. R10 common contract and role01 accepted before work; no spawning.
- Source checkpoint: **3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab**, not a final freeze. Own isolated branch **agents/r10-01-correctness-regressions** at C:/Users/bagma/AppData/Local/Temp/opencode/r10-01-correctness-ses_de5678335ffeI7xJrod5l25Q0Q.
- Immutable R03 baseline0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43 and its report/probes remain preserved. R10 results are newly executed, not borrowed baseline passes.
- Allowed writes: own tests/r10_probes/role01/, own actual-ID note, this report and evidence/R10-01 only. Normalizers remain16/R04 and enginesR04; no source/existing-test edits, installs, shared-branch commits/pushes or issue/PR mutations.
- Agile mapping: authenticated GET verified existing open [issue23: Inspect real renderer outputs and commit reproducible visual evidence](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/23). F2 is an actual semantic-output dependency, not satisfaction of that issue's browser/image acceptance. F1/F3 are genuine previously reported contract candidates for R04/backlog disposition, not newly fabricated or closed tickets.
- Acceptance: portable strict RED and successful controls; exact source/module identity; safe scoped commit/push and actual remote-SHA receipt. Source fixes, independent non-author retesting, full gates/real charts and evidence-linked issue disposition remain downstream dependencies. This is not full SDLC completion, final approval, a green CI claim or900issue completion.

## Confirmed findings and permanent oracles

1. **P1 F1: TS drops ambiguous GraphQL siblings.** packages/deepviz/src/normalize.ts:84-90,130-150. Input {nodes:[{id:1}],version:7} succeeds with only [{id:1}], without a loss warning; audit:{source:'left'} and edges equivalents also disappear. Ten NEW strict failures cover direct, genuine async-generator and encoded JSON inputs; one additional failure covers custom-wrapper path policy. Explicit paths/known metadata pass, and Python rejects the ambiguous input. Small fix proposal: enforce the existing sibling metadata allowlist after valid column discrimination and require explicit custom-wrapper selection. Owner16/R04 only after producer handback.

2. **P1 F2: Python native charts use numeric color as y instead of count.** python/deepviz/src/deepviz/normalize.py:547-548 creates count2 correctly, but engines.py:59-73 (especially64) re-infers y=s. Two {g:'a',s:100} rows with {x:'g',color:'s',aggregation:'count'} encode100 instead of2. NEW failures cover shared channels for series0/100/-4 and four native payloads. Positive controls protect explicit count-measure names, categorical series and heatmap coordinates; TS native equivalents encode2. Small fix proposal: count-aware shared y selection without changing heatmap coordinate semantics. OwnerR04.

3. **P2 F3: Python drops wrapper-named scalar columns.** python/deepviz/src/deepviz/normalize.py:364-376 versus TS normalize.ts:119-128. Input {rows:[1,2]} with explicit y='rows' raises missing-field instead of preserving the column; records/items/results/data likewise fail. Five NEW explicit-mapping failures contrast with passing TS cases. Nested record-array and custom scalar-column controls pass. R04 must settle/apply the existing shared scalar-column preservation/explicit-ambiguity policy, not waive the tests silently; normalizer source is not released to this reviewer.

The23 failed cases belong to these three families; they are not23new issues. No source defect is claimed solely from a missing tool, skipped test or unmeasured memory assumption.

## Executed commands and exact result

Execution used shared Python3.12.16 and installed Node v26.13.1/TypeScript tooling read-only. PYTHONPATH pointed only at the isolated checkpoint's python/deepviz/src; PYTHONDONTWRITEBYTECODE=1. TS built output remained only in the isolated ignored dist. No npmci/dependency installation was run.

| Check | Observed result |
| --- | --- |
| Existing compiler: node C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript/bin/tsc -p packages/deepviz/tsconfig.json | exit0 |
| NEW pytest test_correctness_regressions.py | **exit1;12failed/21passed/0errors/0skips**,33tests;0.96s |
| NEW Node correctness-regressions.test.mjs | **exit1;11failed/19passed/0skips/0cancelled**,30tests;246.6305ms |
| Existing Python normalize/statistics/models | exit0;145passed/0skips |
| Complete existing Node package test directory | exit0;246passed/0failed/0skips |
| Scoped Ruff on NEW Python test | exit0 |
| Production/schema diff versus checkpoint | exit0/empty |

Exact argv, failed test IDs, raw-log hashes and source/test hashes are in docs/coordination/evidence/R10-01/verification.json. The compact evidence includes both NEW RED logs; full existing-suite logs/JUnit remain under isolated artifacts/local/R10-01/run-v1. Local capture driver deliberately exited1 because the source is RED; no collector-exit0 is used to claim success.

Reproduction from a checkout containing these NEW files, with that checkout's own source/dependencies:

    node node_modules/typescript/bin/tsc -p packages/deepviz/tsconfig.json
    # Set PYTHONPATH to this checkout's python/deepviz/src.
    python -m pytest tests/r10_probes/role01/test_correctness_regressions.py -q --tb=short -p no:cacheprovider
    node --test --test-reporter=tap tests/r10_probes/role01/correctness-regressions.test.mjs

An existing compiler outside the checkout may be passed by absolute path. Both test commands correctly return1 on the source checkpoint. README describes the literal invariants and execution without Windows-only hardcoded imports. No xfail/skip or original-oracle weakening hides RED.

## Source and import identity

Python's test guard checks actual imports against this checkout; captured Node resolution is this checkout's packages/deepviz/dist/index.js. Selected SHA256s:

- Python normalize.py:0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83
- Python engines.py:a8a27279e2c9f1601eacd4047da601159202ab65a5faea5efeca98294d4f85de
- TS normalize.ts:d1b45d2a55dfd05361184a57da952a0da735e9b6d72c2491f908ef27bda22371
- Built normalize.js:adb0493123fd478567212e76e2c6e52c828aeaa9eb5425c219b5b1a576689612
- NEW Python test:aadd94225decbcc3997264ae88508c08633e929595f9eefd817faf598cb0cf2b
- NEW Node test:1c864fa8677fd924cfb71d7c795d87e45942005f012183934c529f82d7a8ff25

## Authentication and publication checkpoint

Before publication, authenticated GET/user returned200/login sandeshbagmare; intended public repository and credential-free HTTPS origin were verified. Own branch lookup returned404 before writes; configured Git author was nonempty. GCM output/token stayed in captured process memory only, never terminal output, command arguments, files or Git config. Compact sanitized discovery evidence is authentication.json; no auth/config mutation or issue/PR write occurred.

Publication is not yet attempted at this checkpoint. Next: explicit owned-path staging, staged-diff/whitespace/credential-pattern review, honest small commit, non-force push of OWN branch, actual remote-SHA readback, then durable MAIN receipt. Do not mistake this pre-publication checkpoint for a push receipt.

## Limits and next action

Not run: full Python/whole-release lint/types, package builds/clean consumers,10M/continuous memory, real browser/PNG/SVG inspection, paid providers, security/MCP acceptance or final-head remote CI. Source3aa is a checkpoint and later R04/16 fixes are unverified. No false final signoff, human approval, release, issue closure or benchmark claim.

Next executable action in the OWN branch: git diff --cached --check after staging only owned paths. After publication, R04 should inspect the real commit/evidence, queue source fixes after16handback and rerun these unchanged strict oracles on an explicitly pinned corrected candidate.