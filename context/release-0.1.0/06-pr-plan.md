# PR creation and consolidation plan

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

## Existing PR actions

| PR | Disposition | Planned action |
|---:|---|---|
| #33 | V1-MERGE | Already merged; leave unchanged. |
| #38 | V1-MERGE | Already merged; leave unchanged. |
| #31 | CLOSE-SUPERSEDED (conditional) | Live state: open draft, stale base `0ae2cf26426822135fc10d337fcacf580b7ed833`, head `62344d85f5f471767b7aa3a2005a9e000ca06440`, 324 paths and +36,025/-3; Python 3.11-3.13 jobs fail. Preserve useful focused work before any superseding disposition; do not rebase/merge its broad diff. |

RM-01 approves focused size exceptions for this coherent plan amendment (approximately 1,100 metadata/documentation changed lines) and NEW-01 (approximately 2,000 lines of existing normalizer plus necessary tests/public imports). Do not split arbitrarily or omit tests to reach a line count. Two independent exact-head reviewer reports, two tester reports, current-main rebase/checks and merge gates remain unchanged; larger or unrelated expansion needs a new plan-change ruling.

## Preparation and promotion

Parallel preparation is authorized at the owner request: agents may prepare independent source selections, tests and code in isolated branches for upcoming tasks. Claim exact paths and never write overlapping files in a shared checkout. Shared-file tasks use isolated branches and serialized integration. Owner-approved draft PRs for planned waves may be opened for preparation; future-wave drafts stay non-ready until dependencies complete. Promote only after rebase onto current main, required checks, and fresh exact-head independent reports. Sequential INT-01/02 main merges and dependency order remain binding; preparation does not pass a wave or mark work complete.

## New PRs

Every PR requires two independent reviewer reports and two independent tester reports on the exact head. Each report records identity, scope, exact commit, findings, commands, results and limitations. Commit screenshot/SVG/PNG evidence and embed its repository path in the PR body, including for plan-only or non-rendering work; use an artifact derived from the actual tested input/output or release-plan state. New commits/rebases invalidate prior reports and evidence.

### PLAN-CHANGE-01 - align confirmed scope and live gates

Create a plan-only PR from `plan/release-0.1.0-owner-decisions` against current `main`; keep the diff inside `context/release-0.1.0/`. It synchronizes canonical YAML with Markdown, adds Arrow/Parquet test ownership, records the caller's #28 revision, maps all 11 live P0s to their wave or deferral, and embeds the committed release-wave SVG. Require two exact-head reviewer reports, two exact-head tester reports, and successful `git diff --check`, YAML/JSON parse, cross-file scope checks and SVG XML validation. Merge before opening NEW-01.

The PR body must include the exact head SHA, test output, all four report summaries/links, and:

```markdown
## Visual evidence
![DeepViz 0.1.0 release plan](context/release-0.1.0/evidence/plan-change-wave-map.svg)
```

### NEW-01 - [v1][W1][feature] add bounded Python input normalization

- Action: prepare `release/v1/w1-python-normalization` in an isolated branch; promote to a PR only in Wave 1 after the approved dependencies. Select the final reviewed normalizer from `96b819aee5b01ba88b5a609b587331a528aaa070`, necessary input/GraphQL/Arrow tests and minimal public package exports. Earlier refs are provenance/test sources, not a replay list.
- Source branches: `feat/ingestion`, `feat/r34-python-data-foundation`, `test/graphql-contract`, `agents/r10-04-utf8-field-envelope`, `test/n19-formats`, `agents/r45-04-private-numeric-accounting`.
- Source selection: RM ruling: select latest reviewed Python normalizer from 96b819a (already includes R17/exact finite sum/mean/owned-input and R45 fixes), necessary input/GraphQL/Arrow tests, and minimal __init__.py exports for public models/normalize API. Do not replay old patches. Exclude 9ce04fc package-only, 355637c schema/docs, TS/coordination/evidence.
- Source commit references: `a711ea5c9f4b97d53a80e1cac86c42e25c9d4dbc`, `9531dab2b4d629c6fffdff9b7dc7dfcebb3def03`, `6c412e0f6be7e96a24a7f6c5cbcfdba9a48ef2c5`, `429890b45bb1e85087507e07b95dcd382aa53ab4`, `0ea34db2217037c309ab5ce77361b9e2c3dadd50`, `96b819aee5b01ba88b5a609b587331a528aaa070`.
- Files: `python/deepviz/src/deepviz/normalize.py`, `python/deepviz/tests/test_normalize.py`, `python/deepviz/tests/test_graphql_contract.py`, `python/deepviz/tests/test_n19_formats.py`, `python/deepviz/src/deepviz/__init__.py`.
- Size: RM-approved coherent size exception: approximately 2,000 changed lines for existing normalizer and necessary tests; retain exact-head 2 reviewer + 2 tester gates.
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
Wave 0 G0 and approved PLAN-CHANGE-01; isolated preparation is allowed before merge.
## Files touched
python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_graphql_contract.py, python/deepviz/tests/test_n19_formats.py, python/deepviz/src/deepviz/__init__.py
## How tested (commands + results)
Normalization, GraphQL, Arrow Table/RecordBatch/Reader, IPC file/stream, Parquet path/buffer, malformed/duplicate/oversized nested input, optional-extra error; install [columnar], verify zero skips, full pytest/Ruff/mypy. Record actual exact-head commands/results; no unrun check is a pass.
## Risk & rollback
RM ruling: select latest reviewed Python normalizer from 96b819a (already includes R17/exact finite sum/mean/owned-input and R45 fixes), necessary input/GraphQL/Arrow tests, and minimal __init__.py exports for public models/normalize API. Do not replay old patches. Exclude 9ce04fc package-only, 355637c schema/docs, TS/coordination/evidence. Rollback: Revert squash, rerun main suite, stop wave.
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


### NEW-02 - [v1][W1][test] verify bounded reducer regressions and streaming scale

- Action: prepare `release/v1/w1-python-reductions` in an isolated branch; promote to a PR only in Wave 1 after the approved dependencies. NEW-01 already includes the latest96 reducer fixes. Add reducer regression and scale acceptance; do not replay source hunks already present. Historical `ec9f669` precedes child `5ba8603`; use those refs for regression provenance only.
- Source branches: `feat/r34-python-data-foundation`, `fix/r17-normalizer-boundaries`, `agents/r10-16-finite-overflow-fix`, `agents/r45-04-private-numeric-accounting`.
- Source selection: RM ruling: NEW-01 selects latest96 normalizer with reviewed reducer correctness fixes. NEW-02 does not replay those hunks; add reducer regression/scale acceptance and only newly demonstrated necessary fixes. Historical ec9f669 -> 5ba8603 order is provenance, not replay sequence.
- Source commit references: `ec9f669eff28cd5351da142765b7755e3b2f484f`, `5ba860305dcc86ac2f95f01705b984d2b40f2799`, `c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19`, `a7363be273d7b3bbcb1b52ef79a58bb4e6d0e3be`, `7ab546251029df169604358448ecd462d8db5e6f`, `546c25ea75ee9d8a41b3832aa639664bc9a683b5`, `96b819aee5b01ba88b5a609b587331a528aaa070`.
- Files: `python/deepviz/src/deepviz/normalize.py`, `python/deepviz/tests/test_normalize.py`, `python/deepviz/tests/test_r07_finite_overflow.py`, `python/deepviz/tests/test_r17_normalizer_boundaries.py`, `python/deepviz/tests/test_r45_numeric_state_accounting.py`, `scripts/verify_python_scale.py`, `tests/test_release_scale.py`.
- Size: 300-900 lines; after NEW-01
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
python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_r07_finite_overflow.py, python/deepviz/tests/test_r17_normalizer_boundaries.py, python/deepviz/tests/test_r45_numeric_state_accounting.py, scripts/verify_python_scale.py, tests/test_release_scale.py
## How tested (commands + results)
Exact finite SUM/MEAN and transient-overflow controls; R07/R17/R45 numeric-state/owned-input tests; bounded Arrow streams; scripts/verify_python_scale.py and tests/test_release_scale.py at 10/1K/100K/1M/10M. Machine-readable normalizer evidence now; renderer-linked scale and independent replication before #22 closure. Do not reapply fixes already in NEW-01. Record actual exact-head commands/results; no unrun check is a pass.
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


### NEW-03 - [v1][W2][feature] add Python Matplotlib, Plotly, and Vega renderers

- Action: create fresh branch `release/v1/w2-python-renderers-a` from latest main; apply only listed files/hunks. Source branches: feat/renderers, test/backend-plotly, test/backend-vega.
- Ordered cherry-pick source SHAs: `31acb2f6e58bc83f71c1736af9d4be37c56ad59c`, `420a956788c9b78529d3348650a32913090f5671`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-2`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-03 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by owner-confirmed Python-only 0.1.0 scope; issues #9, #10, #11; plan item NEW-03.
## Source branches consolidated
feat/renderers, test/backend-plotly, test/backend-vega
## Depends on (PRs that must merge first)
NEW-01, NEW-02
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Source commit 31acb2f6 adds five backends in 1,184 lines; stage only these three and their tests; NEW-04 follows. Rollback: Revert squash; normalized main remains.
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

### NEW-04 - [v1][W2][feature] add Python ECharts and AntV G2 renderers

- Action: create fresh branch `release/v1/w2-python-renderers-b` from latest main; apply only listed files/hunks. Source branches: feat/renderers, fix/r20-antv-color-scale, fix/r23-count-channel, fix/r45-17-antv-subnormal, agents/r10-03-echarts-numeric-x, agents/r38-18-antv-source-review, review/r35-12-count-source.
- Ordered cherry-pick source SHAs: `31acb2f6e58bc83f71c1736af9d4be37c56ad59c`, `420a956788c9b78529d3348650a32913090f5671`, `3185e0d9936c7d6f1a9d30b94089b804d75fe991`, `4429f0521612b97eee3790f0d8d0fbc3cad3f8be`, `85796dbe3360fb88686f2e7188122e2da80d54c2`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-2`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-04 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by owner-confirmed Python-only 0.1.0 scope; issues #12, #13; plan item NEW-04.
## Source branches consolidated
feat/renderers, fix/r20-antv-color-scale, fix/r23-count-channel, fix/r45-17-antv-subnormal, agents/r10-03-echarts-numeric-x, agents/r38-18-antv-source-review, review/r35-12-count-source
## Depends on (PRs that must merge first)
NEW-03
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py, python/deepviz/tests/test_r20_antv_color_scale.py, python/deepviz/tests/test_r23_count_channel.py
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Shares renderer paths; rebase after NEW-03; select independent count/AntV hunks once. Rollback: Revert squash; rerun renderer tests.
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

### NEW-05 - [v1][W3][feature] add recommendations and Deep Agents tools

- Action: create fresh branch `release/v1/w3-python-tools` from latest main; apply only listed files/hunks. Source branches: feat/integrations.
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
NEW-03, NEW-04
## Files touched
python/deepviz/src/deepviz/recommend.py, python/deepviz/src/deepviz/tools.py, python/deepviz/src/deepviz/__init__.py, python/deepviz/tests/test_integrations.py
## How tested (commands + results)
Fresh `.[agents]` environment: construct, inspect and invoke real LangChain `StructuredTool`, run normalize -> recommend -> render; zero skips. Separate base-only install without LangChain/Deep Agents verifies core imports and integrations stay lazy. Record exact commands and actual output; no pass may be claimed before execution.
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

- Action: create fresh branch `release/v1/w3-python-mcp-cli` from latest main; apply only listed files/hunks. Source branches: feat/integrations, fix/r14-mcp-json-budget, fix/r41-callback-admission, agents/r10-10-stdio-artifact-lifecycle, agents/r11-10-strict-mcp-boundaries.
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
python/deepviz/src/deepviz/mcp_server.py, python/deepviz/src/deepviz/cli.py, python/deepviz/src/deepviz/tools.py, python/deepviz/tests/test_integrations.py, python/deepviz/tests/test_r14_tool_json_boundary.py, python/deepviz/tests/test_r41_callback_admission.py, examples/, prompts/v1/
## How tested (commands + results)
In a fresh `.[mcp]` environment, test stdio initialize/list/call, safe artifact, malformed JSON and callback admission. Exercise the real tool call in the fresh `[agents]` lane with zero skips for required integration tests. Separately run a base-only lazy-import control; report unrelated skips. Record exact commands/results; no pass may be claimed before execution.
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
NEW-03, NEW-04
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

- Action: create fresh branch `release/v1/w5-python-acceptance` from latest main; apply only listed files/hunks. Source branches: test/acceptance, test/aggregation-semantics, test/backend-antv, test/mcp-transport, test/portability, perf/verification, agents/r10-07-python-clean-distribution, agents/r10-11-python-scale-envelope, agents/r10-13-ci-negative-controls, agents/r10-14-assets-offline-provenance, agents/r10-15-owned-input-cleanup.
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
Full Python tests/Ruff/mypy/build; clean base/[columnar]/[mcp]/[agents] wheel and sdist installs; installed `[agents]` lane must construct/inspect/invoke real LangChain `StructuredTool` and run normalize -> recommend -> render with zero skips, with a separate base-only lazy-import control; package resource/type-marker and entrypoint checks; five-engine and renderer-linked scale evidence with independent replication (#22); dated primary-source research including licensing/runtime/scale/output trade-offs (#19); exact-main CI (#20); package acceptance (#24); every-PR report/visual audit (#26); labeled/milestoned/dependency-aware process issue map and primary GitHub constraints (#27); publicly retargeted genuine focused-PR report provenance and gallery (#29); public amendment to original #4 acceptance: defer npm #25 and TS #14/#15 from 0.1.0; explicitly waive the unmet historical 900-issue criterion for this release while reporting real counts only, with no fabricated tickets or closures; then release roll-up. Record actual commands/results.
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
## How tested (commands + results)
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
