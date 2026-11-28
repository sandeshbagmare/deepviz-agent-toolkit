# Merge plan and release waves

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

Six waves (0-5), eight logical changes, split into focused PRs through plan-change if required. Wave 0 is the verified baseline. Owner-approved draft PRs for planned waves may be opened for preparation; only the current wave may be promoted to ready or merged, after dependencies, rebase, CI and exact-head review gates pass. Target <=400 changed lines and split before the usual 1,000-line cap, subject to the explicit RM exceptions below.

Parallel preparation is authorized at the owner request: agents may prepare independent source selections, tests and code in isolated branches for upcoming tasks. Claim exact paths and never write overlapping files in a shared checkout. Shared-file tasks use isolated branches and serialized integration. Owner-approved draft PRs for any planned wave may be open as preparation, but drafts for future waves stay non-ready and cannot merge until dependencies complete and the branch is rebased onto current main. Dependency order, sequential INT-01/02 main merges, exact-head two-review/two-test evidence, and CI/rebase gates remain binding. Preparation does not pass a wave or mark work complete; independent drafts may be prepared and reviewed in parallel, while promotion and merges remain sequential.

RM-01 approves focused size exceptions for this coherent plan amendment (approximately 1,100 metadata/documentation changed lines) and NEW-01 (approximately 2,000 lines of existing normalizer plus necessary tests/public imports). Do not split arbitrarily or omit tests to reach a line count. Two independent exact-head reviewer reports, two tester reports, current-main rebase/checks and merge gates remain unchanged; larger or unrelated expansion needs a new plan-change ruling.

## Wave 0 - Foundation (verified on current main)

Entry and verified SHA: main `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`. At this exact SHA, local Python 3.14.8 checks passed with source path configured: `PYTHONPATH=python/deepviz/src python -m pytest -q --strict-markers` (118 passed), `python -m ruff check .` (pass), `python -m mypy` (pass), and `python -m build --outdir %TEMP%\deepviz-wave0-build-f692014b` (wheel and sdist built at version 0.1.0). GitHub run [46089153606](https://github.com/sandeshbagmare/deepviz-agent-toolkit/actions/runs/46089153606) passed the current focused Python 3.11-3.13 test/Ruff/mypy matrix. The standard pytest command without source installation/PYTHONPATH fails collection (`ModuleNotFoundError: deepviz`); this is recorded and matches the workflow's configured `PYTHONPATH`. #33/#38 are merged and verified as ancestors. G0 is checked for the existing ChartSpec baseline; full package/entrypoint/optional-extra clean-install smoke remains a later release acceptance task. Do not merge product PRs if the current-main checks regress. Rollback: revert any later regression.

## Wave 1 - Python input core

Entry: G0 checked on exact main; plan-change amendment merged; #26 evidence process active; no known current-main S1/S2 or security/data-loss regression. Do not require scheduled in-scope P0 work to be closed before the wave that owns it. Exit: NEW-01/02 merge and pass exact-main tests, including #8 and the NormalizedData portion of #5; record normalizer scale proof for #22 without closing its renderer-linked criteria; #1 roll-up evidence recorded; #30 exact-main acceptance recorded; #28 owner revision published after this amendment merges. Keep #14 deferred to v1.1. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-1`.

### NEW-01 - [v1][W1][feature] add bounded Python input normalization

- Source branches: `feat/ingestion`, `feat/r34-python-data-foundation`, `test/graphql-contract`, `agents/r10-04-utf8-field-envelope`, `test/n19-formats`, `agents/r45-04-private-numeric-accounting`. Target: `main`; new branch `release/v1/w1-python-normalization`.
- Files: `python/deepviz/src/deepviz/normalize.py`, `python/deepviz/tests/test_normalize.py`, `python/deepviz/tests/test_graphql_contract.py`, `python/deepviz/tests/test_n19_formats.py`, `python/deepviz/src/deepviz/__init__.py`. Estimated size: RM-approved coherent exception of approximately 2,000 lines including necessary tests; retain complete 2+2 gates.
- Dependencies: Wave 0 and the approved plan-change amendment. NEW-01 owns the initial normalizer/input adapters and optional Arrow/Parquet readers/tests; NEW-02 is serialized after NEW-01 and owns reducer regression/scale acceptance in the shared `normalize.py` and `test_normalize.py` paths. Parallel preparation is allowed in isolated branches; shared-file integration and final review remain serialized after NEW-01 merges. Expected conflicts/resolution: Ingestion and R34 share normalize.py; use fresh-main integration and only reviewed Python input-format/GraphQL/Arrow hunks.
- Reviewers: REV-01 + REV-02; QA-01 + QA-02 non-authors. Required tests: normalization, GraphQL, Arrow Table/Batch/Reader, IPC file/stream, Parquet path/buffer and optional-dependency tests; full pytest/Ruff/mypy and `[columnar]` install checks.
- Merge: squash. Rollback: Revert squash, rerun main suite, stop wave.

RM source ruling: select latest reviewed Python normalizer from 96b819a (already includes R17/exact finite sum/mean/owned-input and R45 fixes), necessary input/GraphQL/Arrow tests, and minimal __init__.py exports for public models/normalize API. Do not replay old patches. Exclude 9ce04fc package-only, 355637c schema/docs, TS/coordination/evidence.

### NEW-02 - [v1][W1][test] verify bounded reducer regressions and streaming scale

- Source branches: `feat/ingestion`, `feat/r34-python-data-foundation`, `fix/r17-normalizer-boundaries`, `agents/r10-16-finite-overflow-fix`, `agents/r45-04-private-numeric-accounting`. Target: `main`; new branch `release/v1/w1-python-reductions`.
- Files: `python/deepviz/src/deepviz/normalize.py`, `python/deepviz/tests/test_normalize.py`, `python/deepviz/tests/test_r07_finite_overflow.py`, `python/deepviz/tests/test_r17_normalizer_boundaries.py`, `python/deepviz/tests/test_r45_numeric_state_accounting.py`, `scripts/verify_python_scale.py`, `tests/test_release_scale.py`. Estimated size: 300-900 lines; after NEW-01.
- Dependencies: NEW-01. Expected conflicts/resolution: NEW-01 selects latest96 normalizer with reducer fixes already included. NEW-02 adds regression/scale acceptance; do not replay those hunks. Rebase/test after NEW-01.
- Reviewers: REV-02 + REV-03; QA-01 + QA-02 non-authors. Required tests: Exact finite SUM/MEAN and transient-overflow controls; R07/R17/R45 numeric-state/owned-input tests; bounded Arrow streams; scripts/verify_python_scale.py and tests/test_release_scale.py at 10/1K/100K/1M/10M. Machine-readable normalizer evidence now; renderer-linked scale and independent replication before #22 closure. Do not reapply fixes already in NEW-01.
- Merge: squash. Rollback: Revert this squash only; keep NEW-01.

RM source ruling: NEW-01 selects latest96 normalizer with reviewed reducer correctness fixes. NEW-02 does not replay those hunks; add reducer regression/scale acceptance and only newly demonstrated necessary fixes. Historical ec9f669 -> 5ba8603 order is provenance, not replay sequence.

## Wave 2 - Python renderers

Entry: Wave 1 product, #1 roll-up evidence, #8/#30 acceptance and #5 NormalizedData evidence recorded on exact main; #5 Artifact API and #22 renderer-linked scale acceptance remain scheduled for Wave 2/5; #28 owner revision posted and issue superseded; full checks/smoke pass; no unrelated S1/S2 or main-gate regression. Work may continue with the scheduled P0s #20 (W5), #21 (W4), #23 (this wave), #26 (every PR through W5), and #4 (release umbrella through G3). #14, #15 and #25 remain explicitly deferred to v1.1 and outside 0.1.0. Exit: both renderer PRs merge and verify on exact main; #23 visual acceptance passes across all five Python engines and a dashboard; #5 Artifact API acceptance passes; renderer-linked #22 scale proof is independently replicated or stays explicitly pending through Wave 5. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-2`.

### NEW-03 - [v1][W2][feature] add Python Matplotlib, Plotly, and Vega renderers

- Source branches: `feat/renderers`, `test/backend-plotly`, `test/backend-vega`. Target: `main`; new branch `release/v1/w2-python-renderers-a`.
- Files: `python/deepviz/src/deepviz/engines.py`, `python/deepviz/src/deepviz/render.py`, `python/deepviz/tests/test_render.py`. Estimated size: 300-900 backend-specific lines; split if >1,000.
- Dependencies: NEW-01, NEW-02. Expected conflicts/resolution: Source commit 31acb2f6 adds five backends in 1,184 lines; stage only these three and their tests; NEW-04 follows.
- Reviewers: REV-01 + REV-04; QA-01 + QA-02 non-authors. Required tests: backend semantics, real artifact/MIME/manifest, unsafe text; full checks.
- Merge: squash. Rollback: Revert squash; normalized main remains.

### NEW-04 - [v1][W2][feature] add Python ECharts and AntV G2 renderers

- Source branches: `feat/renderers`, `fix/r20-antv-color-scale`, `fix/r23-count-channel`, `fix/r45-17-antv-subnormal`, `agents/r10-03-echarts-numeric-x`, `agents/r38-18-antv-source-review`, `review/r35-12-count-source`. Target: `main`; new branch `release/v1/w2-python-renderers-b`.
- Files: `python/deepviz/src/deepviz/engines.py`, `python/deepviz/src/deepviz/render.py`, `python/deepviz/tests/test_render.py`, `python/deepviz/tests/test_r20_antv_color_scale.py`, `python/deepviz/tests/test_r23_count_channel.py`. Estimated size: 300-900 backend-specific lines; after NEW-03.
- Dependencies: NEW-03. Expected conflicts/resolution: Shares renderer paths; rebase after NEW-03; select independent count/AntV hunks once.
- Reviewers: REV-02 + REV-03; QA-02 + QA-03 non-authors. Required tests: native output, count/color/extreme-value tests and artifact inspection.
- Merge: squash. Rollback: Revert squash; rerun renderer tests.

## Wave 3 - Python integrations

Entry: Wave 2 and #23 visual acceptance verified on exact main; full checks/smoke pass; no unrelated S1/S2 or main-gate regression. Scheduled P0s #20 (W5), #21 (W4), #26 (every PR through W5) and #4 (G3 umbrella) may remain open; #14 remains deferred and outside 0.1.0. Exit: both integration PRs merge and verify on exact main. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-3`.

### NEW-05 - [v1][W3][feature] add recommendations and Deep Agents tools

- Source branches: `feat/integrations`. Target: `main`; new branch `release/v1/w3-python-tools`.
- Files: `python/deepviz/src/deepviz/recommend.py`, `python/deepviz/src/deepviz/tools.py`, `python/deepviz/src/deepviz/__init__.py`, `python/deepviz/tests/test_integrations.py`. Estimated size: 300-900; split API/tool bindings if needed.
- Dependencies: NEW-03, NEW-04. Expected conflicts/resolution: 1,341-line integration source; stage recommendation/tool API before MCP.
- Reviewers: REV-01 + REV-03; QA-02 + QA-03 non-authors. Required tests: in a fresh `.[agents]` environment, construct/inspect/invoke the actual LangChain `StructuredTool` API and run normalize -> recommend -> render with zero skips; separately, a fresh base-only install without LangChain/Deep Agents must import core while optional integrations stay unloaded; full checks.
- Merge: squash. Rollback: Revert squash; preserve renderer APIs.

### NEW-06 - [v1][W3][feature] add safe stdio MCP server and CLI

- Source branches: `feat/integrations`, `fix/r14-mcp-json-budget`, `fix/r41-callback-admission`, `agents/r10-10-stdio-artifact-lifecycle`, `agents/r11-10-strict-mcp-boundaries`. Target: `main`; new branch `release/v1/w3-python-mcp-cli`.
- Files: `python/deepviz/src/deepviz/mcp_server.py`, `python/deepviz/src/deepviz/cli.py`, `python/deepviz/src/deepviz/tools.py`, `python/deepviz/tests/test_integrations.py`, `python/deepviz/tests/test_r14_tool_json_boundary.py`, `python/deepviz/tests/test_r41_callback_admission.py`, `examples/`, `prompts/v1/`. Estimated size: 300-900; split docs if needed.
- Dependencies: NEW-05. Expected conflicts/resolution: Shares package API/entrypoints; select Python MCP-only paths and fix callback order/capacity.
- Reviewers: REV-02 + REV-04; QA-02 + QA-03 non-authors. Required tests: stdio initialize/list/call, safe artifact, malformed JSON and callback admission with `.[mcp]`; exercise actual tool integration in the installed `[agents]` lane and keep the separate base-only lazy-import control; required tests cannot be skipped.
- Merge: squash. Rollback: Revert squash; retain tools; stop MCP wave.

## Wave 4 - Python hardening and correctness fixes

Entry: Wave 3 merged and verified on exact main; full checks/smoke pass; no unrelated S1/S2 or main-gate regression. #21 is scheduled for this wave; #20 (W5), #26 (per-PR process through W5) and #4 (G3 umbrella) may remain open. #14 stays deferred/out of scope. Exit: NEW-07 merges and verifies; #21 security acceptance is recorded; #30 acceptance remains green on exact main. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-4`.

### NEW-07 - [v1][W4][fix] harden Python render bounds and security

- Source branches: `feat/hardening`, `fix/r12-dense-table-budget`, `agents/r10-01-correctness-regressions`, `agents/r10-02-security-boundaries`. Target: `main`; new branch `release/v1/w4-python-hardening`.
- Files: `python/deepviz/src/deepviz/engines.py`, `python/deepviz/src/deepviz/render.py`, `python/deepviz/tests/test_r12_table_budget.py`, `tests/`. Estimated size: 300-900 lines; selected fixes only.
- Dependencies: NEW-03, NEW-04. Expected conflicts/resolution: Renderer paths were changed in earlier waves; rebase on their merged SHAs. Import only Python hardening/test hunks.
- Reviewers: REV-01 + REV-04 (security); QA-01 + QA-02 non-authors. Required tests: dense table preflight, no execution/unsafe path, security regressions; full suite.
- Merge: squash. Rollback: Revert squash; stop release if safety gate fails.

## Wave 5 - Final acceptance and docs

Entry: Wave 4 and #21 security acceptance verified on exact main; full checks/smoke pass; no unrelated S1/S2 or main-gate regression. #20, #26 and #4 remain scheduled for this final wave; #14 stays deferred/out of scope. #28 blocks G3 until its owner revision is published and the issue is superseded; do not substitute counts or a plan note for that public update. Exit: NEW-08, #19 research evidence, #20 Python CI, #22 renderer-linked scale evidence with independent replication at every required size, #24 clean package install, #26 review-gate, #27 process, publicly retargeted #29 report provenance, publicly scoped #4 roll-up and every in-scope P0 are verified on exact main before G3. If any required #22 size is unrun, keep #22 open and block G3; #25 remains deferred with npm to v1.1. Rollback: revert offending squash commit, rerun full tests/smoke, stop release. Tag: `v0.1.0-wave-5`.

### NEW-08 - [v1][W5][test] complete Python release acceptance and docs

- Source branches: `test/acceptance`, `test/aggregation-semantics`, `test/backend-antv`, `test/mcp-transport`, `test/portability`, `perf/verification`, `agents/r10-07-python-clean-distribution`, `agents/r10-11-python-scale-envelope`, `agents/r10-13-ci-negative-controls`, `agents/r10-14-assets-offline-provenance`, `agents/r10-15-owned-input-cleanup`. Target: `main`; new branch `release/v1/w5-python-acceptance`.
- Files: `tests/`, `python/deepviz/tests/`, `.github/workflows/`, `README.md`, `docs/capabilities.md`, `docs/architecture.md`, `docs/research/`, `docs/process/`, `SECURITY.md`, `pyproject.toml`, `python/deepviz/src/deepviz/py.typed`, `python/deepviz/src/deepviz/schemas/`, `python/deepviz/src/deepviz/prompts/`, `schemas/`, `prompts/v1/`, `scripts/performance_suite.py`, `docs/verification/performance.md`, `tests/test_performance_contract.py`. Estimated size: <=1,000; split CI/docs if needed.
- Dependencies: NEW-01..NEW-07. Expected conflicts/resolution: Consolidate acceptance after code; omit duplicate/RED tests until fixed; exclude agent-state/evidence dumps.
- Reviewers: REV-03 + REV-04; QA-02 + QA-03 non-authors. Required tests: Full Python tests/Ruff/mypy/build; clean base/[columnar]/[mcp]/[agents] wheel and sdist installs; in a clean installed `[agents]` lane, construct, inspect and invoke real LangChain `StructuredTool`, then run normalize -> recommend -> render with zero skips; separately verify a fresh base-only install without LangChain/Deep Agents imports core with integrations unloaded; package resource/type-marker and entrypoint checks; five-engine and renderer-linked scale evidence with independent replication (#22); dated primary-source research including licensing/runtime/scale/output trade-offs (#19); exact-main CI (#20); package acceptance (#24); every-PR report/visual audit (#26); labeled/milestoned/dependency-aware process issue map and primary GitHub constraints (#27); publicly retargeted genuine focused-PR report provenance and gallery (#29); public #4 addendum amending the original npm #25 and historical 900-issue acceptance criteria: defer #14/#15/#25 from 0.1.0 and record that 900 remains unmet but is waived for this release using real counts only, then release roll-up.
- Merge: squash. Rollback: Revert acceptance/doc commit only; stop release and repair CI.

Within each wave follow dependency order. INT-01/02 merge sequentially. After each wave run full tests and smoke on main, record exact SHA and QA evidence, then create the lightweight tag. RC follows Wave 5 and G3; final tag requires G4.
