# Live release tracker

- Default branch: `main`
- Main SHA verified: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1 (plan-change pending)

Current wave: Wave 1 is queued. G0 is verified on exact `main@f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` for the existing ChartSpec baseline. PRs #40/#41 are open drafts for NEW-01/02 preparation only; they are not ready implementation PRs and remain blocked from promotion until PLAN-CHANGE-01 merges. Authorized future-wave drafts #42-46 likewise remain non-ready until dependencies complete. Decisions: Python-only 0.1.0; TypeScript issues #14/#15 and npm issue #25 deferred to v1.1; Arrow/Parquet required via optional `[columnar]`; version `0.1.0`; the historical 900-issue criterion is waived for 0.1.0 but remains unmet, with public #4/#28 updates pending plan merge. Use real counts only; do not fabricate tickets or closures. Eleven live P0 issues are mapped below; #28 is waived only after the public update/closure. Full evidence is in `18-current-state-audit.md`.

| ID | Wave | Owner | State | Blocked by | Claimed files | Scope / claim / implementation / review / CI / merge / QA | Last update |
|---|---:|---|---|---|---|---|---|
| NEW-01 | 1 | IMP-01 | planned; PR #40 draft prep only | PLAN-CHANGE-01 merged before promotion | python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_graphql_contract.py, python/deepviz/tests/test_n19_formats.py, python/deepviz/src/deepviz/__init__.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-02 | 1 | IMP-02 | planned; PR #41 draft prep only | NEW-01; serialized shared-file handoff | python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_r07_finite_overflow.py, python/deepviz/tests/test_r17_normalizer_boundaries.py, python/deepviz/tests/test_r45_numeric_state_accounting.py, scripts/verify_python_scale.py, tests/test_release_scale.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-03 | 2 | IMP-03 | planned | NEW-01, NEW-02 | python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-04 | 2 | IMP-04 | planned | NEW-03 | python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py, python/deepviz/tests/test_r20_antv_color_scale.py, python/deepviz/tests/test_r23_count_channel.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-05 | 3 | IMP-05 | planned | NEW-03, NEW-04; installed [agents] real StructuredTool/API and flow tests, zero skips; separate base-only lazy-import control | python/deepviz/src/deepviz/recommend.py, python/deepviz/src/deepviz/tools.py, python/deepviz/src/deepviz/__init__.py, python/deepviz/tests/test_integrations.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-06 | 3 | IMP-06 | planned | NEW-05; installed [mcp]/[agents] real integration lanes with no skipped required tests; separate base-only lazy-import control | python/deepviz/src/deepviz/mcp_server.py, python/deepviz/src/deepviz/cli.py, python/deepviz/src/deepviz/tools.py, python/deepviz/tests/test_integrations.py, python/deepviz/tests/test_r14_tool_json_boundary.py, python/deepviz/tests/test_r41_callback_admission.py, examples/, prompts/v1/ | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-07 | 4 | IMP-07 | planned | NEW-03, NEW-04 | python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_r12_table_budget.py, tests/ | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-08 | 5 | IMP-08 | planned | NEW-01..NEW-07 | tests/, python/deepviz/tests/, .github/workflows/, README.md, docs/capabilities.md, docs/architecture.md, docs/research/, docs/process/, SECURITY.md, pyproject.toml, python/deepviz/src/deepviz/py.typed, python/deepviz/src/deepviz/schemas/, python/deepviz/src/deepviz/prompts/, schemas/, prompts/v1/, scripts/performance_suite.py, docs/verification/performance.md, tests/test_performance_contract.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-31 | before wave 1 | RM-01 | open draft; stale base and 3 Python CI failures | Preserve focused useful work through reviewed PRs; do not merge/close yet | release/candidate | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-40 | Wave 1 prep | IMP-01 | open draft; non-ready | Dependencies, rebase, CI and exact-head 2+2 before promotion | release/v1/w1-python-normalization | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-41 | Wave 1 prep | IMP-02 | open draft; non-ready | Dependencies, rebase, CI and exact-head 2+2 before promotion | release/v1/w1-python-scale | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-42 | Wave 2 prep | IMP-03 | open draft; non-ready | Dependencies, rebase, CI and exact-head 2+2 before promotion | release/v1/w2-python-renderers-a | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-43 | Wave 3 prep | IMP-05 | open draft; non-ready | Dependencies, rebase, CI and exact-head 2+2 before promotion | release/v1/w3-python-tools | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-44 | Wave 3 prep | IMP-06 | open draft; non-ready | Dependencies, rebase, CI and exact-head 2+2 before promotion | release/v1/w3-python-mcp-cli | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-45 | Wave 5 prep | IMP-08 | open draft; non-ready | Dependencies, rebase, CI and exact-head 2+2 before promotion | release/v1/w5-python-package | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-46 | Wave 5 prep | CI-01 | open draft; non-ready | NEW-01..NEW-07, plan approval, rebase, CI and exact-head 2+2 before promotion | release/v1/w5-python-ci | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-28 | before G3 | TRI-01 + RM-01 | caller explicitly removed the 900-issue criterion for 0.1.0; issue still open P0 | Merge plan change; publish #4 scope/900-criterion amendment and exact live counts, then close as superseded | - | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PLAN-CHANGE-01 | Wave 0 / before NEW-01 | RM-01 | in progress; local branch `plan/release-0.1.0-owner-decisions` from `main@f692014...` | Final exact-head 2 reviewer reports, 2 tester reports, committed SVG path in PR body, checks and merge | `context/release-0.1.0/**` | [x] / [x] / [x] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-1 | Wave 1/2 roll-up | TRI-01 | open P0 foundation epic | Record W1 normalization/#8 proof; close only after #5 Artifact acceptance in W2 and applicable child evidence pass on exact main. | NEW-01/02 | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-4 | G3 roll-up | TRI-01 + RM-01 | open P0 delivery epic; public scope addendum pending | After plan merge, publicly amend #4 to defer npm #25 and TypeScript #14/#15 from 0.1.0 and record the unmet historical 900-issue criterion as waived for this release using real counts only; retain Python #19/#20/#21/#22/#23/#24/#26/#27/#29 acceptance. Keep #28 open until publication; close it only after that update, and close #4 only after applicable children and G3 evidence. | NEW-08, public issue #4 scope addendum | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-5 | Wave 1 contract + Wave 2 artifact acceptance | IMP-01 + QA + renderer owners | open P0 contract issue; ChartSpec verified, NormalizedData and Artifact pending | Wave 1 verifies NormalizedData counts/strategy/warnings; keep issue open until Wave 2 verifies real Artifact metadata, safe paths, MIME/output and schema/API parity on main. | NEW-01/02, NEW-03/04 | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-8 | Wave 1 | IMP-02 + QA | open P0 streaming story | Close after reducer-before-materialization, metadata, edge, and scale evidence on main | NEW-02 | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-14 | deferred v1.1 | DOC-01 | open P0 TypeScript issue, outside Python-only scope | Keep open and unchanged; revisit in v1.1 | - | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-20 | Wave 5 | CI-01 | open P0; Python CI in scope, TS CI deferred | Full Python test/lint/type/build/package workflow and exact-main green run | NEW-08 | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-21 | Wave 4/5 | REV-04 + QA-01 | open P0 security acceptance | Named negative tests: script/title/cell injection, script-closing and dangerous config; traversal/absolute path escape; arbitrary remote-URL/code execution; unrelated overwrite; document optional network runtimes; inspect dependencies/diagnostics/packaging for credential disclosure. Independent exact-commit security review and main QA. | NEW-07/08 | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-23 | Wave 2 | QA-02 + QA-03 | open P0 visual acceptance | Inspected five-engine and dashboard outputs plus browser/runtime/network evidence | NEW-03/04/08 | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-26 | every PR through Wave 5 | RM-01 + REV/QA | open P0 evidence process | Two independent reports per class on exact head plus committed visual paths; close after final audit | all PRs | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-30 | before Wave 2 | QA-02 + IMP-07 | open P0; strict numeric fix merged | Record exact-main focused QA and green 3.11-3.13 checks; then update and close only when all criteria pass | tests/test_models.py, tests/test_numeric_schema.py, tests/test_dashboard_schema.py | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-19 | Wave 5 | DOC-01 | open P1 research evidence | Dated primary sources for five renderers, Deep Agents and MCP; distinguish facts/inference/unknowns; match claims to tested scope | docs/research/, docs/architecture.md | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-22 | Wave 1 proof; Wave 2/5 closure | IMP-02 + QA + renderer owners | open P1 scale evidence; renderer-linked acceptance pending | Wave 1 records normalizer scale at 10/1K/100K/1M/10M. Keep issue open until bounded renderer payloads at every scale and independent replication on exact main in Wave 2/5. Any unrun required size keeps #22 open and blocks G3; record the unrun limits explicitly. | NEW-02, NEW-03/04, NEW-08 | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-24 | Wave 5 | IMP-08 + QA | open P1 package acceptance | Build wheel/sdist; clean-install and smoke public API, render, CLI/MCP; no public publishing | NEW-08 | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-25 | deferred v1.1 | DOC-01 | open P1 npm package; explicitly outside Python-only 0.1.0 scope | Keep open unchanged; revisit with TypeScript/npm in v1.1 | - | [x] / [x] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-27 | Wave 5 | DOC-01 + TRI-01 | open P1 process evidence | Publish issue map under docs/process with real issue/milestone/label snapshot, dependencies, acceptance, status and evidence; primary GitHub secondary-limit and author self-approval docs with access dates; retain unmet historical 900 count plus explicit release waiver, no padding. | docs/process/ | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-29 | Every PR; Wave 5 closure | RM-01 + REV/QA | open P1 report provenance; public focused-PR retarget pending | After plan merge, publicly retarget original #31 criteria to focused replacement PRs with source/keeper mapping. Require two genuine reviews and two tests with session identity/exact SHA/scope/findings/commands/results, actual committed gallery per rendering PR, and explicit separation from GitHub APPROVED states; no self-approval/rule bypass. | all PRs, public issue #29 retarget | [x] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |

## Agent roster and current assignment

All 22 release roles remain assigned (RM-01 plus 21 child roles), with a task cap of 22 against 101 platform slots. Current work includes consolidation, source/integration preparation, independent review and QA; other roles retain completed audits and stand by for the next scoped task. The latest platform snapshot observed 9 running sessions; refresh concurrency before dispatch rather than claiming all roles are simultaneously running.

| Role | Assignment | State |
|---|---|---|
| RM-01 | Orchestration/status, plan-change review/publication, owner decisions and gates | Active |
| INT-01 | Integration feasibility and later approved sequential merges | Active |
| INT-02 | Plan consistency/integration preflight and rebase queue | Active |
| IMP-01 | Isolated NEW-01 source selection and bounded input preparation | Active |
| IMP-02 | Isolated NEW-02 reducer preparation; integrate after NEW-01 | Active |
| IMP-03 | Renderer readiness/source preparation | Active |
| IMP-04 | Reducer source audit complete; renderer-B preparation queued | Audit complete; standby or independent verification queue |
| IMP-05 | #28 evidence audited; public owner-revision preparation | Audit complete; standby or independent verification queue |
| IMP-06 | Package metadata audited; MCP preparation queued | Audit complete; standby or independent verification queue |
| IMP-07 | #30 reproduced; security regression preparation queued | Audit complete; standby or independent verification queue |
| IMP-08 | Package/NEW-08 acceptance preparation queued | Audit complete; standby or independent verification queue |
| REV-01 | Independent contract review; exact-head plan review standby | Audit complete; standby or independent verification queue |
| REV-02 | Independent source-selection review; final-head re-review standby | Audit complete; standby or independent verification queue |
| REV-03 | Scale-acceptance audit and final-head plan review | Active |
| REV-04 | Security/source review and visual provenance audit | Audit complete; standby or independent verification queue |
| QA-01 | G0 verification complete; final-head plan test standby | Audit complete; standby or independent verification queue |
| QA-02 | Contract E2E complete; final-head plan test/visual evidence | Audit complete; standby or independent verification queue |
| QA-03 | Plan consistency audit and QA-owned SVG corrections | Audit complete; standby or independent verification queue |
| TRI-01 | Live P0/issue acceptance and public scope-action preparation | Audit complete; standby or independent verification queue |
| CI-01 | CI/G0 audit complete; final-head CI checks standby | Audit complete; standby or independent verification queue |
| DOC-01 | Sole release-plan writer/consolidation except QA-owned SVG | Active |
| RES-01 | P0/wave-entry audit complete; surge standby | Audit complete; standby or independent verification queue |

At each transition, update the matching checkbox and YAML status together. Enter the PR/issue link, exact SHA and evidence link in the associated PR comment or status note. Check a gate only when its acceptance evidence exists. RM-01 reconciles both boards at every handoff and session resume.
