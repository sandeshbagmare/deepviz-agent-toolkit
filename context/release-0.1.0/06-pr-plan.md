# PR creation and consolidation plan

- Default branch: `main`
- Main SHA reconciled: `54dd12e2d8d5d69e25426e92c313f0f79e00de81`
- Date: 2026-11-28
- Plan version: 1.1 (local renderer-split amendment pending)

Append-only correction of published PLAN-CHANGE-02@0f6 on baseline main54dd; unpublished until RM scope check, fresh4reports required on the new exact head; no product promotion before merge. User forbids main-to-feature merges, force-push/history rewrite and branch deletion. fix_norm alone owns the UNPUBLISHED normalization-rebased replacement; old #40 is unaccepted/nonpromotable. Published #41-46 remain preserved preparation/source records; after dependency main QA, use fresh unpublished true-rebase/scoped-selection branches, publish once, and map full keeper paths/SHAs before superseding old PRs. All tests/exact2+2/CI/main-QA gates remain.

## Existing PR actions

| PR | Disposition | Planned action |
|---:|---|---|
| #33 | V1-MERGE | Already merged; leave unchanged. |
| #38 | V1-MERGE | Already merged; leave unchanged. |
| #39 | MERGED baseline | Merged at `54dd12e2d8d5d69e25426e92c313f0f79e00de81`; leave its branch/checkout unchanged. QA-01 result-main baseline verification passed; full release remains unverified. |
| #31 | CLOSE-SUPERSEDED (conditional) | Live state: open draft, stale base `0ae2cf26426822135fc10d337fcacf580b7ed833`, head `62344d85f5f471767b7aa3a2005a9e000ca06440`, 324 paths and +36,025/-3; Python 3.11-3.13 jobs fail. Preserve useful focused work before any superseding disposition; do not rebase/merge its broad diff. |

RM-01 approves focused size exceptions for this coherent plan amendment (approximately 1,100 metadata/documentation changed lines) and NEW-01 (at most 2,750 changed lines across exactly the 10 claimed paths). PR #40 at `a94f85c47e9a18f01009484a6813738eb8259a03` against `main@f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` measures 2,687 additions + 2 deletions = 2,689 changed lines. The 61-line tolerance is only for necessary review/rebase fixes and regenerated normalization evidence within this existing coherent task; additional paths or unrelated scope require a new plan-change ruling. Do not split arbitrarily or omit tests to reach a line count. Two independent exact-head reviewer reports, two tester reports, current-main rebase/checks, dependency order and sequential merge gates remain unchanged. NEW-02 has a separate RM-approved 1,300-line ceiling across its five audited regression/harness/test paths plus scale-output JSON/PNG only; the remaining 96 lines are solely for compact actual evidence and necessary fixes within those seven paths. All required tests remain mandatory.

## Preparation and promotion

User policy is binding: no main-to-feature merge commits, no force-push/history rewrite, and no branch deletion. Preserve published #40-46 branches as preparation/source records. After each prerequisite is merged and verified on main, build a fresh UNPUBLISHED current-main branch by true rebase of a private copy or scoped product selection, with zero feature merge commits; publish it once, open only the necessary replacement PR, and map every retained/excluded path and source/keeper SHA before RM may supersede the old PR. No quota/duplicate tickets or PRs, no old-draft promotion, no dropped tests; all fresh exact-head 2+2/CI/dependency and non-author main-QA gates remain.

## New PRs

Every PR requires two independent reviewer reports and two independent tester reports on the exact head. Each report records identity, scope, exact commit, findings, commands, results and limitations. Commit screenshot/SVG/PNG evidence and embed its repository path in the PR body, including for plan-only or non-rendering work; use an artifact derived from the actual tested input/output or release-plan state. New commits/rebases invalidate prior reports and evidence.

### PLAN-CHANGE-01 - merged baseline (#39)

Merged at `54dd12e2d8d5d69e25426e92c313f0f79e00de81`. The following original PR template is historical; the current renderer-split amendment is separate and local only. QA-01 result-main baseline verification passed; full release remains unverified.

Create a plan-only PR from `plan/release-0.1.0-owner-decisions` against current `main`; keep the diff inside `context/release-0.1.0/`. It synchronizes canonical YAML with Markdown, adds Arrow/Parquet test ownership, records the caller's #28 revision, maps all 11 live P0s to their wave or deferral, and embeds the committed release-wave SVG. Require two exact-head reviewer reports, two exact-head tester reports, and successful `git diff --check`, YAML/JSON parse, cross-file scope checks and SVG XML validation. Merge before opening NEW-01.

The PR body must include the exact head SHA, test output, all four report summaries/links, and:

```markdown
## Visual evidence
![DeepViz 0.1.0 release plan](context/release-0.1.0/evidence/plan-change-wave-map.svg)
```

### NEW-01 - [v1][W1][feature] add bounded Python input normalization

- Action: prepare `release/v1/w1-python-normalization` in an isolated branch; promote to a PR only in Wave 1 after the approved dependencies. Select the latest96 normalizer provenance with the focused PR #40 fixes, necessary input/GraphQL/Arrow tests, minimal public package exports, selector model/schema contract, existing normalization smoke harness and measured JSON/SVG evidence in the 10 claimed paths. Earlier refs are provenance/test sources, not a replay list.
- Source branches: `feat/ingestion`, `feat/r34-python-data-foundation`, `test/graphql-contract`, `agents/r10-04-utf8-field-envelope`, `test/n19-formats`, `agents/r45-04-private-numeric-accounting`.
- Source selection: RM ruling: use latest96 normalizer provenance (R17/exact finite sum/mean/owned-input and R45 fixes), necessary input/GraphQL/Arrow tests, minimal __init__.py exports, and the focused reviewed PR #40 follow-ups. NEW-01 also owns selector-boundary changes in `python/deepviz/src/deepviz/models.py` and `schemas/chart-spec.schema.json`, its existing `scripts/benchmark_scale.py` smoke harness, and measured `docs/verification/normalization/normalization-output.json` plus `docs/verification/normalization/normalization-output.svg`. These five paths are part of the same bounded-normalization task, not permission for broad schema/package/docs work. Do not replay old patches or whole 9ce04fc/355637c commits; exclude TypeScript, coordination and unrelated evidence dumps.
- Source commit references: `a711ea5c9f4b97d53a80e1cac86c42e25c9d4dbc`, `9531dab2b4d629c6fffdff9b7dc7dfcebb3def03`, `6c412e0f6be7e96a24a7f6c5cbcfdba9a48ef2c5`, `429890b45bb1e85087507e07b95dcd382aa53ab4`, `0ea34db2217037c309ab5ce77361b9e2c3dadd50`, `96b819aee5b01ba88b5a609b587331a528aaa070`.
- Files: `python/deepviz/src/deepviz/normalize.py`, `python/deepviz/tests/test_normalize.py`, `python/deepviz/tests/test_graphql_contract.py`, `python/deepviz/tests/test_n19_formats.py`, `python/deepviz/src/deepviz/__init__.py`, `python/deepviz/src/deepviz/models.py`, `schemas/chart-spec.schema.json`, `scripts/benchmark_scale.py`, `docs/verification/normalization/normalization-output.json`, `docs/verification/normalization/normalization-output.svg`.
- Size: RM-approved coherent size exception: at most 2,750 changed lines across the 10 claimed paths; PR #40 at `a94f85c47e9a18f01009484a6813738eb8259a03` measures 2,687 additions + 2 deletions = 2,689 changed lines. The 61-line tolerance covers only necessary review/rebase fixes and regenerated normalization evidence within this existing task; additional paths or unrelated scope require a new ruling. Retain exact-head 2 reviewer + 2 tester gates.
- Labels: `v1`, `wave-1`, `type:feature`, `P1`, `planned`; update lifecycle label. Rebase and rerun checks before review.
- Merge: squash; Revert squash, rerun main suite, stop wave.

```markdown
## What
[v1][W1][feature] add bounded Python input normalization.
## Why (links: issue #, plan item)
Owner-confirmed Python-only 0.1.0; issues #5, #6, #7, #8; plan NEW-01.
## Source branches consolidated
feat/ingestion, feat/r34-python-data-foundation, test/graphql-contract, agents/r10-04-utf8-field-envelope, test/n19-formats, agents/r45-04-private-numeric-accounting
## Depends on (PRs that must merge first)
PLAN-CHANGE-02 merged FIRST, then true rebase of this unpublished branch onto resulting main before one publication; fresh exact-head checks/2+2/CI and exact-main QA mandatory.
## Files touched
python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_graphql_contract.py, python/deepviz/tests/test_n19_formats.py, python/deepviz/src/deepviz/__init__.py, python/deepviz/src/deepviz/models.py, schemas/chart-spec.schema.json, scripts/benchmark_scale.py, docs/verification/normalization/normalization-output.json, docs/verification/normalization/normalization-output.svg
## How tested (commands + results)
Normalization, GraphQL, Arrow Table/RecordBatch/Reader, IPC file/stream, Parquet path/buffer, malformed/duplicate/oversized nested input, optional-extra error; install [columnar], verify zero skips, full pytest/Ruff/mypy. Verify selector model/runtime/checked-in-schema parity and no-read/no-open controls; run the existing benchmark smoke and validate the measured JSON/SVG evidence. Correct both existing JSON/SVG artifact provenance records to the actual final tested source, and add/retest the newly found shared-_connection-DAG scan, empty-DAG _flatten scan, and ArrowUnion preconversion-amplification regressions in existing normalize.py/test_normalize.py paths. No main-to-feature merge, force-push, omitted test or extra path is authorized; recount against the existing NEW-01 ceiling. The fifth Arrow-schema-DAG work-budget regression must remain covered in the final-main rerun within existing claimed paths; preserve all29 new regressions and every prior case. Old40/7296 gates invalid; plan2 FIRST, then true-rebase/rerun/recount on resulting main before one publication.

## Risk & rollback
RM ruling: use latest96 normalizer provenance (R17/exact finite sum/mean/owned-input and R45 fixes), necessary input/GraphQL/Arrow tests, minimal __init__.py exports, and the focused reviewed PR #40 follow-ups. NEW-01 also owns selector-boundary changes in `python/deepviz/src/deepviz/models.py` and `schemas/chart-spec.schema.json`, its existing `scripts/benchmark_scale.py` smoke harness, and measured `docs/verification/normalization/normalization-output.json` plus `docs/verification/normalization/normalization-output.svg`. These five paths are part of the same bounded-normalization task, not permission for broad schema/package/docs work. Do not replay old patches or whole 9ce04fc/355637c commits; exclude TypeScript, coordination and unrelated evidence dumps. Rollback: Revert squash, rerun main suite, stop wave.
## Visual evidence (committed repository paths; embed every image)
![Measured normalization output](docs/verification/normalization/normalization-output.svg)
Machine-readable companion: `docs/verification/normalization/normalization-output.json`.
## Checklist
- [ ] Rebased on latest main
- [ ] Two independent reviewer and two tester reports on exact head
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```


### NEW-02 - [v1][W1][test] verify bounded reducer regressions and streaming scale

- Action: preserve published preparation/source `release/v1/w1-python-scale` unchanged. Only after dependency main QA, prepare a fresh UNPUBLISHED true-rebased/scoped-selection current-main replacement (branch/PR TBD), publish once, and map all keeper paths/SHAs before superseding old; never force-push or merge main into the feature.
- Source branches: `feat/r34-python-data-foundation`, `fix/r17-normalizer-boundaries`, `agents/r10-16-finite-overflow-fix`, `agents/r45-04-private-numeric-accounting`.
- Source selection: RM ruling: NEW-01 selects latest96 normalizer with reviewed reducer correctness fixes. NEW-02 does not replay those hunks; add reducer regression/scale acceptance and only newly demonstrated necessary fixes. Historical ec9f669 -> 5ba8603 order is provenance, not replay sequence.
- Source commit references: `ec9f669eff28cd5351da142765b7755e3b2f484f`, `5ba860305dcc86ac2f95f01705b984d2b40f2799`, `c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19`, `a7363be273d7b3bbcb1b52ef79a58bb4e6d0e3be`, `7ab546251029df169604358448ecd462d8db5e6f`, `546c25ea75ee9d8a41b3832aa639664bc9a683b5`, `96b819aee5b01ba88b5a609b587331a528aaa070`.
- Files: `python/deepviz/tests/test_r07_finite_overflow.py`, `python/deepviz/tests/test_r17_normalizer_boundaries.py`, `python/deepviz/tests/test_r45_numeric_state_accounting.py`, `scripts/verify_python_scale.py`, `tests/test_release_scale.py`, `docs/verification/scale/scale-output.json`, `docs/verification/scale/scale-output.png`.
- Size: <=1,300 changed lines across these seven paths only; audited+1,204/-0 leaves96 for compact actual evidence/necessary fixes in those paths. No omitted tests; fresh exact-head2+2/CI/dependencies/main-QA unchanged.
- Labels: `v1`, `wave-1`, `type:test`, `P1`, `planned`; update lifecycle label. Rebase and rerun checks before review.
- Merge: squash; Revert this squash only; keep NEW-01.

```markdown
## What
[v1][W1][test] verify bounded reducer regressions and streaming scale.
## Why (links: issue #, plan item)
Owner-confirmed Python-only 0.1.0; issues #8, #22; plan NEW-02.
## Source branches consolidated
feat/r34-python-data-foundation, fix/r17-normalizer-boundaries, agents/r10-16-finite-overflow-fix, agents/r45-04-private-numeric-accounting
## Depends on (PRs that must merge first)
NEW-01 merged; isolated preparation may run in parallel, with rebase and exact-head checks afterward.
## Files touched
python/deepviz/tests/test_r07_finite_overflow.py, python/deepviz/tests/test_r17_normalizer_boundaries.py, python/deepviz/tests/test_r45_numeric_state_accounting.py, scripts/verify_python_scale.py, tests/test_release_scale.py, docs/verification/scale/scale-output.json, docs/verification/scale/scale-output.png
## How tested (commands + results)
Exact finite SUM/MEAN and transient-overflow controls; R07/R17/R45 numeric-state/owned-input tests; bounded Arrow streams; scripts/verify_python_scale.py and tests/test_release_scale.py at 10/1K/100K/1M/10M. Machine-readable normalizer evidence now; renderer-linked scale and independent replication before #22 closure. Do not reapply fixes already in NEW-01. Record final exact base/head, full numstat and actual evidence; no template or old-head check is a pass.

## Risk & rollback
RM ruling: NEW-01 selects latest96 normalizer with reviewed reducer correctness fixes. NEW-02 does not replay those hunks; add reducer regression/scale acceptance and only newly demonstrated necessary fixes. Historical ec9f669 -> 5ba8603 order is provenance, not replay sequence. Rollback: Revert this squash only; keep NEW-01.
## Visual evidence (committed repository paths; embed every image)
![Actual tested output](path/to/committed-artifact.svg)
## Checklist
- [ ] Rebased on latest main
- [ ] Two independent reviewer and two tester reports on exact head
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```


RM exception: Audited PR #41@49431aced25f21f4543d00853623c7d2b5b23fc8: +1,204/-0 across five existing regression/harness/test paths. RM-01 authorizes a NEW-02-only ceiling of 1,300 changed lines across those five paths plus docs/verification/scale/scale-output.json and scale-output.png only. The remaining 96 lines cover compact measured evidence and necessary fixes within those seven paths only; do not drop tests. Actual final-head recount remains required.

### NEW-03 roll-up / existing PR #42 preservation

Split proposal only: `NEW-02 -> NEW-03A -> NEW-03B -> NEW-04`; NEW-03 is not a standalone replacement PR and closes only after both child merges are independently verified on main. Preserve PR #42 at its captured baseline source head `79bbb12a396d6d138c1ac54ea93b827aba5bb923` until all retained/excluded hunks and evidence are mapped to keeper PRs. No GitHub action is requested or claimed.

### NEW-03A - [v1][W2][feature] add shared render boundary, Matplotlib and Vega-Lite

- Local draft only: no replacement GitHub PR opened. Planned branch `release/v1/w2-python-renderers-static` must be prepared on a fresh UNPUBLISHED true-rebased/scoped-selection current-main branch after dependency main QA; the published preparation branch is preserved.
- Source branches: feat/renderers, test/backend-vega. Ordered source references: `31acb2f6e58bc83f71c1736af9d4be37c56ad59c`, `420a956788c9b78529d3348650a32913090f5671`. Apply mixed commits with `--no-commit` and stage only scoped hunks; do not replay broad renderer ancestry.
- Size: Earlier <=982 projection is historical. Prepared fdb7718050b9065ffcc6c770662268f392603980 measures 975 changed text lines plus three PNGs against its f692014 merge-base. Prepared only, not on main or final dependency base; retain all tests and actual <=1,000 final-head cap/recount after true rebase.
- Evidence gates: each child requires its own exact-head two independent reviewer and two independent tester reports, observed green CI and non-author QA after merge. Every required test remains mandatory; an estimate does not pass the actual <=1,000-line gate.
- Merge: squash. Preserve PR #42 until replacement coverage is fully accounted for; do not close or rewrite it through this draft.

```markdown
## What
[v1][W2][feature] add shared render boundary, Matplotlib and Vega-Lite; logical parent NEW-03 is complete only after NEW-03A and NEW-03B are both verified-on-main.
## Why (links: issue #, plan item)
Python-only 0.1.0; issues #9 and #11; plan item NEW-03A. Renderer source scope remains unchanged.
## Source branches consolidated
feat/renderers, test/backend-vega
## Depends on (PRs that must merge first)
NEW-02 merged and verified on exact main (NEW-01 is transitive); this renderer-split plan-change approved and merged.
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py, python/deepviz/tests/test_static_browser.py, evidence/new03a/**
## How tested (commands + results)
Run complete relevant tests in test_render.py and test_static_browser.py with real Matplotlib PNG/SVG and Vega-Lite SVG/HTML/fallback artifacts; inspect bar/table/dashboard semantics, titles/labels, MIME/manifest, safe text/paths and browser console/runtime/network behavior. Keep all required tests; no skipped required case. Run full Python regression, Ruff, mypy and applicable package/build checks; observed green CI and two independent reviewer plus two independent tester reports must target exact final head. Rebase onto exact post-NEW-02 main before final reports; non-author QA verifies the merge on exact main. Record actual commands/results, exact base/head and the complete numstat; no execution pass is claimed by this template.
## Risk & rollback
Shared engines.py/render.py/test_render.py paths are serialized: NEW-02 -> NEW-03A -> NEW-03B -> NEW-04. Stage only the shared render/artifact boundary plus Matplotlib and Vega-Lite hunks; exclude Plotly/ECharts/AntV implementation. Rollback: Revert NEW-03A squash if required, rerun main checks and stop the dependent renderer queue; preserve normalized main.
## Visual evidence (committed repository paths; embed every image)
Commit compact actual gallery output under `evidence/new03a/**` and embed each final image path here. This template is not visual evidence.
## Checklist
- [ ] Actual full diff <=1,000 changed lines; no required tests omitted
- [ ] Rebased on exact dependency main and CI green
- [ ] Two independent reviewer and two independent tester reports target exact final head
- [ ] Actual output gallery committed and embedded
- [ ] Non-author exact-main QA recorded after merge
```

### NEW-03B - [v1][W2][feature] add Python Plotly renderer

- Local draft only: no replacement GitHub PR opened. Planned branch `release/v1/w2-python-renderers-plotly` must be prepared on a fresh UNPUBLISHED true-rebased/scoped-selection current-main branch after dependency main QA; the published preparation branch is preserved.
- Source branches: feat/renderers, test/backend-plotly. Ordered source references: `31acb2f6e58bc83f71c1736af9d4be37c56ad59c`, `420a956788c9b78529d3348650a32913090f5671`. Apply mixed commits with `--no-commit` and stage only scoped hunks; do not replay broad renderer ancestry.
- Size: Planning estimate only: approximately 239 changed lines; not a measured diff. Actual full proposed diff must be <=1,000 changed lines including every required test and text evidence file.
- Evidence gates: each child requires its own exact-head two independent reviewer and two independent tester reports, observed green CI and non-author QA after merge. Every required test remains mandatory; an estimate does not pass the actual <=1,000-line gate.
- Merge: squash. Preserve PR #42 until replacement coverage is fully accounted for; do not close or rewrite it through this draft.

```markdown
## What
[v1][W2][feature] add Python Plotly renderer; logical parent NEW-03 is complete only after NEW-03A and NEW-03B are both verified-on-main.
## Why (links: issue #, plan item)
Python-only 0.1.0; issue #10; plan item NEW-03B. Renderer source scope remains unchanged.
## Source branches consolidated
feat/renderers, test/backend-plotly
## Depends on (PRs that must merge first)
NEW-03A merged and verified on exact main; this renderer-split plan-change approved and merged.
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py, python/deepviz/tests/test_plotly_browser.py, evidence/new03b/**
## How tested (commands + results)
Run Plotly-scoped test_render.py and test_plotly_browser.py cases with actual HTML and browser output, including hostile titles/labels, literal text, trace/axis semantics, artifact/MIME/manifest and browser console/runtime/network behavior. Rerun Matplotlib/Vega-Lite regression controls from NEW-03A. Keep all required tests; no skipped required case. Run full Python regression, Ruff, mypy and applicable package/build checks; observed green CI and two independent reviewer plus two independent tester reports must target exact final head. Non-author QA verifies the merge on exact main. Record actual commands/results, exact base/head and the complete numstat; no execution pass is claimed by this template.
## Risk & rollback
Rebase onto the actual NEW-03A main merge, preserve the shared render boundary and static backends, and stage Plotly-only implementation/test hunks. No broad source commit or TypeScript replay. Rollback: Revert only NEW-03B squash; preserve NEW-03A shared boundary, Matplotlib and Vega-Lite, rerun static regression/main checks and stop NEW-04 promotion. After revert, mark NEW-03B and the NEW-03 roll-up unverified until the affected exact-main QA passes again.
## Visual evidence (committed repository paths; embed every image)
Commit compact actual gallery output under `evidence/new03b/**` and embed each final image path here. This template is not visual evidence.
## Checklist
- [ ] Actual full diff <=1,000 changed lines; no required tests omitted
- [ ] Rebased on exact dependency main and CI green
- [ ] Two independent reviewer and two independent tester reports target exact final head
- [ ] Actual output gallery committed and embedded
- [ ] Non-author exact-main QA recorded after merge
```

### NEW-04 - [v1][W2][feature] add Python ECharts and AntV G2 renderers

- Preserve published preparation/source `release/v1/w2-python-renderers-b` unchanged. After dependency main QA, prepare a fresh UNPUBLISHED true-rebased/scoped-selection current-main replacement branch/PR TBD, then one publication and full keeper mapping; no old-draft promotion.
- Source branches: feat/renderers, fix/r20-antv-color-scale, fix/r23-count-channel, fix/r45-17-antv-subnormal, agents/r10-03-echarts-numeric-x, agents/r38-18-antv-source-review, review/r35-12-count-source. Ordered source references: `31acb2f6e58bc83f71c1736af9d4be37c56ad59c`, `420a956788c9b78529d3348650a32913090f5671`, `3185e0d9936c7d6f1a9d30b94089b804d75fe991`, `4429f0521612b97eee3790f0d8d0fbc3cad3f8be`, `85796dbe3360fb88686f2e7188122e2da80d54c2`. Apply mixed commits with `--no-commit` and stage only scoped hunks; do not replay broad renderer ancestry.
- Size: Prepared overlay4f59c12ad2fb5a976ca6759477d1483eea597431 versus dependency14539a280ab1cb91f93b2c06f9105cd646f7c2a3 measures+964/-14=978 changed text lines across15 paths, with8 PNGs. Neither overlay nor dependency is main acceptance; fresh unpublished replacement/current-main rebase and final<=1000 recount remain mandatory. Independent23-browser/34-unit receipt is for real product commit9cc5c9e802064d18f253e39795c832128c84afbe; author receipt stored at4f59 separately reports462 pytest/23 browser. Neither is final replacement-head or main acceptance.
- Evidence gates: each proposed slice requires its own exact-head two independent reviewer and two independent tester reports, observed green CI and non-author QA after merge. Every required test remains mandatory; an estimate does not pass the actual <=1,000-line gate.
- Merge: squash. Preserve PR #42 until replacement coverage is fully accounted for; do not close or rewrite it through this draft.

```markdown
## What
[v1][W2][feature] add Python ECharts and AntV G2 renderers; NEW-04 follows verified NEW-03B and retains the existing ECharts/AntV source scope.
## Why (links: issue #, plan item)
Python-only 0.1.0; issues #12 and #13; plan item NEW-04. Renderer source scope remains unchanged.
## Source branches consolidated
feat/renderers, fix/r20-antv-color-scale, fix/r23-count-channel, fix/r45-17-antv-subnormal, agents/r10-03-echarts-numeric-x, agents/r38-18-antv-source-review, review/r35-12-count-source
## Depends on (PRs that must merge first)
NEW-03B merged and verified on exact main; NEW-03A remains verified as its prerequisite.
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/tests/test_browser_acceptance.py, python/deepviz/tests/test_r23_count_channel.py, python/deepviz/tests/test_renderers_b.py, evidence/new04/**
## How tested (commands + results)
Use actual python/deepviz/tests/test_renderers_b.py, test_browser_acceptance.py and test_r23_count_channel.py; preserve targeted R20 color/domain and R23 count/extreme native-source acceptance, plus shared static/Plotly regression checks. Historical root tests/ anticipated paths and absent R20 test filenames are not delivered-file claims. Inspect the real8-PNG/native/browser evidence, console/runtime/network behavior; retain all full checks, fresh exact-head2 reviewer+2 tester reports, green CI, final size recount and non-author exact-main QA after prerequisite main acceptance. Prepared4f59 versus14539 measures978 text/15paths/8PNG only; not main acceptance.

## Risk & rollback
Shared renderer paths are serialized after NEW-03B; select existing ECharts/AntV and independent R20/R23/count/color/extreme-value source hunks only. Anticipated named test/evidence paths do not broaden source scope. Rollback: Revert squash; rerun renderer tests.
## Visual evidence (committed repository paths; embed every image)
Commit compact actual gallery output under `evidence/new04/**` and embed each final image path here. This template is not visual evidence.
## Checklist
- [ ] Actual full diff <=1,000 changed lines; no required tests omitted
- [ ] Rebased on exact dependency main and CI green
- [ ] Two independent reviewer and two independent tester reports target exact final head
- [ ] Actual output gallery committed and embedded
- [ ] Non-author exact-main QA recorded after merge
```

### NEW-05 - [v1][W3][feature] add recommendations and Deep Agents tools

- Action: preserve published preparation/source `release/v1/w3-python-tools` unchanged. Only after dependency main QA, prepare a fresh UNPUBLISHED true-rebased/scoped-selection current-main replacement (branch/PR TBD), publish once, and map all keeper paths/SHAs before superseding old; never force-push or merge main into the feature.
- Ordered cherry-pick source SHAs: `6731720cfc4c7b0a729c4958a7d2e2f4fe614107`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-3`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-05 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by owner-confirmed Python-only 0.1.0 scope; issue #16; plan item NEW-05.
## Source branches consolidated
feat/integrations
## Depends on (PRs that must merge first)
NEW-03A, NEW-03B, NEW-04
## Files touched
python/deepviz/src/deepviz/recommend.py, python/deepviz/src/deepviz/tools.py, python/deepviz/src/deepviz/__init__.py, python/deepviz/tests/test_tools_api.py, evidence/new05/tools-output.png, evidence/new05/report.json
## How tested (commands + results)
In a fresh `.[agents]` environment, construct, inspect and invoke the actual LangChain `StructuredTool` API, then run normalize -> recommend -> render through the real tool flow. These required tests must execute with zero skips. Separately, in a fresh base-only install without LangChain/Deep Agents, import core and prove optional integrations remain lazy without loading `langchain_core`; test_tools_api.py must construct/inspect/invoke actual StructuredTool and exercise the real API flow with installed [agents] and zero skips; full checks. Record final exact base/head, full numstat and actual evidence; no template or old-head check is a pass.

## Risk & rollback
1,341-line integration source; stage recommendation/tool API before MCP. Rollback: Revert squash; preserve renderer APIs.
## Visual evidence (committed repository paths; embed every image)
<!-- Replace with the exact-head test output artifact and committed repository path. -->
![Actual tested output](path/to/committed-artifact.svg)
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-06 - [v1][W3][feature] add safe stdio MCP server and CLI

- Action: preserve published preparation/source `release/v1/w3-python-mcp-cli` unchanged. Only after dependency main QA, prepare a fresh UNPUBLISHED true-rebased/scoped-selection current-main replacement (branch/PR TBD), publish once, and map all keeper paths/SHAs before superseding old; never force-push or merge main into the feature.
- Ordered cherry-pick source SHAs: `6731720cfc4c7b0a729c4958a7d2e2f4fe614107`, `d65dfc0fd807d0335b858476de8cdf7c6b958711`, `cd75c459ddba9f3d6bc0a5185b570af369fb4980`, `f48c72e26000560b48f3dfd137696fa9acf17637`, `91d62f4218302b3f3659a01611e76234398cdc98`, `6cba2d49eb4de82d5df64f790803e23c08f07b9d`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-3`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-06 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by owner-confirmed Python-only 0.1.0 scope; issues #17, #21; plan item NEW-06.
## Source branches consolidated
feat/integrations, fix/r14-mcp-json-budget, fix/r41-callback-admission, agents/r10-10-stdio-artifact-lifecycle, agents/r11-10-strict-mcp-boundaries
## Depends on (PRs that must merge first)
NEW-05
## Files touched
python/deepviz/src/deepviz/mcp_server.py, python/deepviz/src/deepviz/cli.py, python/deepviz/src/deepviz/tools.py, examples/, prompts/v1/, tests/test_mcp_cli.py, evidence/new06/mcp-output.png, evidence/new06/report.json
## How tested (commands + results)
In a fresh `.[mcp]` environment, test stdio initialize/list/call, safe artifact retrieval, malformed JSON and callback admission. Exercise the real integration tool call in the fresh `[agents]` lane; required integration tests must not skip. Separately run the base-only lazy-import control without LangChain/Deep Agents; report any unrelated optional-test skips explicitly. Use actual tests/test_mcp_cli.py for delivered tests; port required JSON-budget, callback-admission and portability cases there as needed. Historical test_integrations/R14/R41 file names are source/acceptance provenance, not a claim those files are delivered by PR #44. Record final exact base/head, full numstat and actual evidence; no template or old-head check is a pass.

## Risk & rollback
Shares package API/entrypoints; select Python MCP-only paths and fix callback order/capacity. Rollback: Revert squash; retain tools; stop MCP wave.
## Visual evidence (committed repository paths; embed every image)
<!-- Replace with the exact-head test output artifact and committed repository path. -->
![Actual tested output](path/to/committed-artifact.svg)
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-07 - [v1][W4][fix] harden Python render bounds and security

- Action: create fresh branch `release/v1/w4-python-hardening` from latest main; apply only listed files/hunks. Source branches: feat/hardening, fix/r12-dense-table-budget, agents/r10-01-correctness-regressions, agents/r10-02-security-boundaries.
- Ordered cherry-pick source SHAs: `d5b68c470416f93127c8187e8111d0d27d20b108`, `2b2709ec6846ad8e136641257e04b4ae48eded08`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-4`, `type:fix`, `P0`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-07 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by owner-confirmed Python-only 0.1.0 scope; issues #21, #23; plan item NEW-07.
## Source branches consolidated
feat/hardening, fix/r12-dense-table-budget, agents/r10-01-correctness-regressions, agents/r10-02-security-boundaries
## Depends on (PRs that must merge first)
NEW-03A, NEW-03B, NEW-04
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_r12_table_budget.py, tests/
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Renderer paths were changed in earlier waves; rebase on their merged SHAs. Import only Python hardening/test hunks. Rollback: Revert squash; stop release if safety gate fails.
## Visual evidence (committed repository paths; embed every image)
<!-- Replace with the exact-head test output artifact and committed repository path. -->
![Actual tested output](path/to/committed-artifact.svg)
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-08 - [v1][W5][test] complete Python release acceptance and docs

- Action: NEW-08 is a logical roll-up, not a broad omnibus PR. Preserve mapped published package/CI preparations; after prerequisites/main QA, use fresh UNPUBLISHED replacements with one publication and full keeper mapping. Remaining acceptance/docs needs focused claims before publication.
- Ordered cherry-pick source SHAs: `12e7b6109e7fa6eebabf9a20912fcaf06f56f5a7`, `e6a8a8c2126dc90f10de8a3b0b16a9eaad829478`, `5f7ab4cf0e3e43075e781a20344c40c57d6fc7f7`, `c799dc5e3a9ffbdd522cab96419c466f86e04401`, `f1e71035b1818bd280037efaa1394adf500139fb`, `146f0276323918307b642bc86d1414dbb3b686d9`, `06c04900466f66d7919b68a5c3626d94df248ea6`, `2b4f0a8a2de7540a53d8399c2b87bbdd19b137e6`, `ccb0bf0856cde5c6a866b9418a7b6fca66f2c7cf`, `dedb41fa8df3fdb90b845eef7a10b5fa4032872c`, `9bcf27dd0888778a6826fbd1f3203bc4652cec40`, and `8a10108752567f6d0faac700240c4acf77b32556` (only `tests/r13_probes/role15/test_reducer_source_ownership.py`; exclude agent-state/evidence/report files). Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-5`, `type:test`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-08 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by owner-confirmed Python-only 0.1.0 scope; issues #19, #20, #22, #23, #24, #26, #27, #29 and #4; plan item NEW-08.
## Source branches consolidated
test/acceptance, test/aggregation-semantics, test/backend-antv, test/mcp-transport, test/portability, perf/verification, agents/r10-07-python-clean-distribution, agents/r10-11-python-scale-envelope, agents/r10-13-ci-negative-controls, agents/r10-14-assets-offline-provenance, agents/r10-15-owned-input-cleanup
## Depends on (PRs that must merge first)
NEW-01..NEW-07
## Files touched
tests/, python/deepviz/tests/, .github/workflows/, README.md, docs/capabilities.md, docs/architecture.md, docs/research/, docs/process/, SECURITY.md, pyproject.toml, python/deepviz/src/deepviz/py.typed, python/deepviz/src/deepviz/schemas/, python/deepviz/src/deepviz/prompts/, schemas/, prompts/v1/, scripts/performance_suite.py, docs/verification/performance.md, tests/test_performance_contract.py
## How tested (commands + results)
Full Python tests/Ruff/mypy/build; clean base/[columnar]/[mcp]/[agents] wheel and sdist installs; in the fresh installed [agents] lane, construct, inspect and invoke the real LangChain StructuredTool API and complete normalize -> recommend -> render with zero skips; in a separate fresh base-only install without LangChain/Deep Agents, import core and verify integrations remain unloaded; package resource/type-marker and entrypoint checks; five-engine and renderer-linked scale evidence with independent replication (#22); dated primary-source research including licensing/runtime/scale/output trade-offs (#19); exact-main CI (#20); package acceptance (#24); every-PR report/visual audit (#26); labeled/milestoned/dependency-aware process issue map and primary GitHub constraints (#27); publicly retargeted genuine focused-PR report provenance and gallery (#29); public #4 amendment deferring npm #25 and TS #14/#15 from 0.1.0 and explicitly waiving the unmet historical 900-issue criterion for this release with real counts only and no fabricated tickets/closures. Record final exact base/head, full numstat and actual evidence; no template or old-head check is a pass.

## Risk & rollback
Consolidate acceptance after code; omit duplicate/RED tests until fixed; exclude agent-state/evidence dumps. Rollback: Revert acceptance/doc commit only; stop release and repair CI.
## Visual evidence (committed repository paths; embed every image)
<!-- Replace with the exact-head test output artifact and committed repository path. -->
![Actual tested output](path/to/committed-artifact.svg)
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```


## Reusable PR body template (verbatim)

```markdown
## What
## Why (links: issue #, plan item)
## Source branches consolidated
## Depends on (PRs that must merge first)
## Files touched
tests/, python/deepviz/tests/, .github/workflows/, README.md, docs/capabilities.md, docs/architecture.md, docs/research/, docs/process/, SECURITY.md, pyproject.toml, python/deepviz/src/deepviz/py.typed, python/deepviz/src/deepviz/schemas/, python/deepviz/src/deepviz/prompts/, schemas/, prompts/v1/, scripts/performance_suite.py, docs/verification/performance.md, tests/test_performance_contract.py
## Risk & rollback
## Visual evidence (committed repository paths; embed every image)
<!-- Replace with the exact-head test output artifact and committed repository path. -->
![Actual tested output](path/to/committed-artifact.svg)
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

Do not close source branches during this planning run. Close only after the replacement PRs are merged and their source content is preserved.

## NEW-08 mapped package and CI sub-PRs (local amendment)

| Child / draft | Branch / owner | Dependencies | Reviewers / testers | Exact claimed paths / mandatory output |
|---|---|---|---|---|
| NEW-08-PACKAGE / #45 | `release/v1/w5-python-package` / IMP-08 | NEW-01..NEW-07, including both NEW-03A and NEW-03B, merged and verified on exact main. | REV-03 + REV-04; QA-02 + QA-03 independent non-author reports on this sub-PR exact head | `pyproject.toml`, `python/deepviz/src/deepviz/py.typed`, `tests/test_release_package.py`, `evidence/new08-package/installed-output.png`, `evidence/new08-package/report.json` |
| NEW-08-CI / #46 | `release/v1/w5-python-ci` / CI-01 | NEW-08-PACKAGE plus NEW-01..NEW-07 (both renderer children) merged and verified on exact main. | REV-03 + REV-04; QA-02 + QA-03 independent non-author reports on this sub-PR exact head | `.github/CI.md`, `.github/workflows/python-release.yml`, `evidence/new08-ci/browser-output.png`, `evidence/new08-ci/report.json` |

These are non-ready drafts: required actual PNG/JSON is absent at the audited heads. Use tested installed-package output for #45 and actual CI/browser output for #46; status diagrams do not satisfy the image requirement. Recount the complete fixed/evidence head under 1,000 lines and restart exact-head 2+2/CI after every change. Final NEW-08 acceptance/research/process/docs remains separately incomplete.

PLAN-CHANGE-02-only budget: <=1,200 changed lines across the prior11 context paths plus only the existing SVG; ad540340 measured+737/-262=999 is historical, leaving201 lines solely for coherent consistency/policy/status and actual tested visual corrections. Recount the final full diff; no product scope or gate waiver.

NEW-01 replacement PR is TBD: plan2 FIRST, correct the two artifact provenance records and every discovered boundedness/work-budget regression, true-rebase the unpublished branch onto resulting main, verify zero feature merges and all fresh gates, then one publication. Rebase checklists refer only to unpublished replacements; never force-update old published drafts.
