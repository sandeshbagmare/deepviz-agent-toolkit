# Merge plan and release waves

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

Six waves (0-5), eight focused PRs. Wave 0 is the verified baseline. Open one wave at a time; target <=400 changed lines and split before the 1,000-line hard cap.

## Wave 0 - Foundation (complete)

Entry: main `484ff08ddcae6c36d43ce61de774c00b6c422c88`. Exit evidence: 3/3 CI, 118 tests, Ruff, mypy, wheel/sdist pass. No new PR; #33/#38 are already merged. Do not merge product PRs until G0 remains green. Rollback: revert any later regression. Tag after verification: `v0.1.0-wave-0`.

## Wave 1 - Python input core

Entry: previous wave merged, full checks + smoke pass on exact main SHA, and no open S1/S2/P0. Exit: each PR approved, CI green, merged and verified on main. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-1`.

### NEW-01 - [v1][W1][feature] add bounded Python input normalization

- Source branches: `feat/ingestion`, `feat/r34-python-data-foundation`, `test/graphql-contract`, `agents/r10-04-utf8-field-envelope`. Target: `main`; new branch `release/v1/w1-python-normalization`.
- Files: `python/deepviz/src/deepviz/normalize.py`, `python/deepviz/tests/test_normalize.py`, `python/deepviz/tests/test_graphql_contract.py`. Estimated size: 300-900 lines; split input-format hunks.
- Dependencies: none. Expected conflicts/resolution: Ingestion and R34 share normalize.py; use reviewed R34 base and only unique format/GraphQL hunks.
- Reviewers: REV-01 + REV-02; QA-01 non-author. Required tests: normalization, GraphQL and format tests; full pytest/Ruff/mypy.
- Merge: squash. Rollback: Revert squash, rerun main suite, stop wave.

### NEW-02 - [v1][W1][feature] add bounded streaming reducers

- Source branches: `feat/ingestion`, `feat/r34-python-data-foundation`, `fix/r17-normalizer-boundaries`, `agents/r10-16-finite-overflow-fix`, `agents/r45-04-private-numeric-accounting`. Target: `main`; new branch `release/v1/w1-python-reductions`.
- Files: `python/deepviz/src/deepviz/normalize.py`, `python/deepviz/tests/test_normalize.py`, `python/deepviz/tests/test_r07_finite_overflow.py`, `python/deepviz/tests/test_r17_normalizer_boundaries.py`. Estimated size: 300-900 lines; after NEW-01.
- Dependencies: NEW-01. Expected conflicts/resolution: Shared normalize.py; apply Python-only fixes after NEW-01 and rebase/test.
- Reviewers: REV-02 + REV-03; QA-02 non-author. Required tests: aggregation, GraphQL/scalar fidelity, finite overflow, 10/1K/100K/1M/10M smoke.
- Merge: squash. Rollback: Revert this squash only; keep NEW-01.

## Wave 2 - Python renderers

Entry: previous wave merged, full checks + smoke pass on exact main SHA, and no open S1/S2/P0. Exit: each PR approved, CI green, merged and verified on main. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-2`.

### NEW-03 - [v1][W2][feature] add Python Matplotlib, Plotly, and Vega renderers

- Source branches: `feat/renderers`, `test/backend-plotly`, `test/backend-vega`. Target: `main`; new branch `release/v1/w2-python-renderers-a`.
- Files: `python/deepviz/src/deepviz/engines.py`, `python/deepviz/src/deepviz/render.py`, `python/deepviz/tests/test_render.py`. Estimated size: 300-900 backend-specific lines; split if >1,000.
- Dependencies: NEW-01, NEW-02. Expected conflicts/resolution: Source commit 31acb2f6 adds five backends in 1,184 lines; stage only these three and their tests; NEW-04 follows.
- Reviewers: REV-01 + REV-04; QA-01. Required tests: backend semantics, real artifact/MIME/manifest, unsafe text; full checks.
- Merge: squash. Rollback: Revert squash; normalized main remains.

### NEW-04 - [v1][W2][feature] add Python ECharts and AntV G2 renderers

- Source branches: `feat/renderers`, `fix/r20-antv-color-scale`, `fix/r23-count-channel`, `fix/r45-17-antv-subnormal`, `agents/r10-03-echarts-numeric-x`, `agents/r38-18-antv-source-review`, `review/r35-12-count-source`. Target: `main`; new branch `release/v1/w2-python-renderers-b`.
- Files: `python/deepviz/src/deepviz/engines.py`, `python/deepviz/src/deepviz/render.py`, `python/deepviz/tests/test_render.py`, `python/deepviz/tests/test_r20_antv_color_scale.py`, `python/deepviz/tests/test_r23_count_channel.py`. Estimated size: 300-900 backend-specific lines; after NEW-03.
- Dependencies: NEW-03. Expected conflicts/resolution: Shares renderer paths; rebase after NEW-03; select independent count/AntV hunks once.
- Reviewers: REV-02 + REV-03; QA-02. Required tests: native output, count/color/extreme-value tests and artifact inspection.
- Merge: squash. Rollback: Revert squash; rerun renderer tests.

## Wave 3 - Python integrations

Entry: previous wave merged, full checks + smoke pass on exact main SHA, and no open S1/S2/P0. Exit: each PR approved, CI green, merged and verified on main. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-3`.

### NEW-05 - [v1][W3][feature] add recommendations and Deep Agents tools

- Source branches: `feat/integrations`. Target: `main`; new branch `release/v1/w3-python-tools`.
- Files: `python/deepviz/src/deepviz/recommend.py`, `python/deepviz/src/deepviz/tools.py`, `python/deepviz/src/deepviz/__init__.py`, `python/deepviz/tests/test_integrations.py`. Estimated size: 300-900; split API/tool bindings if needed.
- Dependencies: NEW-03, NEW-04. Expected conflicts/resolution: 1,341-line integration source; stage recommendation/tool API before MCP.
- Reviewers: REV-01 + REV-03; QA-03. Required tests: local normalize -> recommend -> render without model; full checks.
- Merge: squash. Rollback: Revert squash; preserve renderer APIs.

### NEW-06 - [v1][W3][feature] add safe stdio MCP server and CLI

- Source branches: `feat/integrations`, `fix/r14-mcp-json-budget`, `fix/r41-callback-admission`, `agents/r10-10-stdio-artifact-lifecycle`, `agents/r11-10-strict-mcp-boundaries`. Target: `main`; new branch `release/v1/w3-python-mcp-cli`.
- Files: `python/deepviz/src/deepviz/mcp_server.py`, `python/deepviz/src/deepviz/cli.py`, `python/deepviz/src/deepviz/tools.py`, `python/deepviz/tests/test_integrations.py`, `python/deepviz/tests/test_r14_tool_json_boundary.py`, `python/deepviz/tests/test_r41_callback_admission.py`, `examples/`, `prompts/v1/`. Estimated size: 300-900; split docs if needed.
- Dependencies: NEW-05. Expected conflicts/resolution: Shares package API/entrypoints; select Python MCP-only paths and fix callback order/capacity.
- Reviewers: REV-02 + REV-04; QA-03. Required tests: stdio initialize/list/call, safe artifact, malformed JSON, callback admission; install [mcp].
- Merge: squash. Rollback: Revert squash; retain tools; stop MCP wave.

## Wave 4 - Python hardening and correctness fixes

Entry: previous wave merged, full checks + smoke pass on exact main SHA, and no open S1/S2/P0. Exit: each PR approved, CI green, merged and verified on main. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-4`.

### NEW-07 - [v1][W4][fix] harden Python render bounds and security

- Source branches: `feat/hardening`, `fix/r12-dense-table-budget`, `agents/r10-01-correctness-regressions`, `agents/r10-02-security-boundaries`. Target: `main`; new branch `release/v1/w4-python-hardening`.
- Files: `python/deepviz/src/deepviz/engines.py`, `python/deepviz/src/deepviz/render.py`, `python/deepviz/tests/test_r12_table_budget.py`, `tests/`. Estimated size: 300-900 lines; selected fixes only.
- Dependencies: NEW-03, NEW-04. Expected conflicts/resolution: Renderer paths were changed in earlier waves; rebase on their merged SHAs. Import only Python hardening/test hunks.
- Reviewers: REV-01 + REV-04 (security); QA-01. Required tests: dense table preflight, no execution/unsafe path, security regressions; full suite.
- Merge: squash. Rollback: Revert squash; stop release if safety gate fails.

## Wave 5 - Final acceptance and docs

Entry: previous wave merged, full checks + smoke pass on exact main SHA, and no open S1/S2/P0. Exit: each PR approved, CI green, merged and verified on main. Rollback: revert offending squash commit, rerun full tests/smoke, stop next wave. Tag: `v0.1.0-wave-5`.

### NEW-08 - [v1][W5][test] complete Python release acceptance and docs

- Source branches: `test/acceptance`, `test/aggregation-semantics`, `test/backend-antv`, `test/mcp-transport`, `test/portability`, `perf/verification`, `agents/r10-07-python-clean-distribution`, `agents/r10-11-python-scale-envelope`, `agents/r10-13-ci-negative-controls`, `agents/r10-14-assets-offline-provenance`, `agents/r10-15-owned-input-cleanup`. Target: `main`; new branch `release/v1/w5-python-acceptance`.
- Files: `tests/`, `python/deepviz/tests/`, `.github/workflows/`, `README.md`, `docs/capabilities.md`, `SECURITY.md`. Estimated size: <=1,000; split CI/docs if needed.
- Dependencies: NEW-01..NEW-08. Expected conflicts/resolution: Consolidate acceptance after code; omit duplicate/RED tests until fixed; exclude agent-state/evidence dumps.
- Reviewers: REV-01 + REV-04; QA-01/02/03 non-authors. Required tests: full pytest/Ruff/mypy/build, five-engine/integration smoke, clean wheel/sdist install.
- Merge: squash. Rollback: Revert acceptance/doc commit only; stop release and repair CI.

Within each wave follow dependency order. INT-01/02 merge sequentially. After each wave run full tests and smoke on main, record exact SHA and QA evidence, then create the lightweight tag. RC follows Wave 5 and G3; final tag requires G4.
