# Current repository and Wave 0 audit

- Repository: `sandeshbagmare/deepviz-agent-toolkit`
- Default branch and exact SHA: `main@f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Audit date: 2026-11-28
- Plan change: v1.1, owner-approved decisions; implementation has not started.

## Live Git state and GitHub inventory

- `git fetch origin main` and `git ls-remote origin refs/heads/main` both returned `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`.
- `git ls-remote --heads origin` returned 68 refs including `main` (67 non-default refs). The repo-root working checkout is on `release/candidate@62344d85f5f471767b7aa3a2005a9e000ca06440` and has 672 modified/untracked paths; it was left untouched. The plan edits are isolated in the dedicated checkout on branch `plan/release-0.1.0-owner-decisions`, based on current main; it contains only release-plan file changes.
- Live PR inventory: [#33](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/33) merged at `31cff73ab057c3fed69bd400ac005f2f11609027`; [#38](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/38) merged at `484ff08ddcae6c36d43ce61de774c00b6c422c88`; subsequent planning commit `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` is current main; [#31](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/31) remains open draft from base `0ae2cf26426822135fc10d337fcacf580b7ed833` to head `62344d85f5f471767b7aa3a2005a9e000ca06440`, with 324 changed paths and +36,025/-3. Python 3.11, 3.12 and 3.13 jobs fail on that draft; keep its useful work only through focused selections.
- Authenticated GitHub issue search returned 35 open and 0 closed issues (PRs excluded). Live labels show 11 open P0 issues; see the tracker and risk register for their scope/wave dispositions.
- The only current-main workflow is `.github/workflows/chart-contract.yml`, a focused ChartSpec test/Ruff/mypy matrix for Python 3.11-3.13. Its latest main run [46089153606](https://github.com/sandeshbagmare/deepviz-agent-toolkit/actions/runs/46089153606) passed all three matrix jobs. There is no full renderer/integration/package workflow on current main.

## Wave 0 verification on exact current main

Commands ran from a clean checkout at `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`, local Python 3.14.8:

| Command | Result |
|---|---|
| `python -m pytest -q --strict-markers` | Failed collection because the package was not installed and `deepviz` was not importable. |
| `$env:PYTHONPATH = (Join-Path $PWD 'python\\deepviz\\src'); python -m pytest -q --strict-markers` | Passed: 118 tests. This matches the workflow's configured source path. |
| `python -m ruff check .` | Passed: all checks passed. |
| `python -m mypy` | Passed: no issues in 1 source file. |
| `python -m build --outdir $outDir` where `$outDir` was `%TEMP%\\deepviz-wave0-build-f692014b` | Passed: built `deepviz_agent_toolkit-0.1.0.tar.gz` and `deepviz_agent_toolkit-0.1.0-py3-none-any.whl`. |
| GitHub workflow on `main@f692014b...` | Passed Python 3.11/3.12/3.13 focused test/Ruff/mypy matrix; run 46089153606. |

This satisfies G0 for the existing ChartSpec baseline. The package's renderer/integration/CLI/MCP modules and `python/deepviz/tests` do not yet exist on current main; clean-install tests with base, `[columnar]` and `[mcp]` extras remain required before RC, not a claim of current feature readiness.

## Owner decisions and issue evidence

- Python-only 0.1.0 confirmed; TypeScript/npm issue #15 deferred to v1.1.
- Arrow/Parquet is required through the existing optional `[columnar]` extra (`pyarrow>=19`); base installation remains PyArrow-free.
- `pyproject.toml` already sets package version `0.1.0`.
- The caller explicitly revised #28's 900-issue requirement: "as we dont have that many issues will not keep that as requirement". No 900-item evidence exists. #28 remains open P0 until this plan change merges, then post the decision and authenticated current counts (35 open, 0 closed issues; PRs excluded) before closing as superseded for 0.1.0. All other in-scope issue gates remain.
- [#30](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/30) remains open P0. QA-02 independently ran the strict focused model/schema selection on current main and passed 76 tests; direct model-versus-schema smoke covered valid bar, unknown field, strings/booleans, empty dashboard, and nested dashboard. The exact-main GitHub matrix on #33/#38 ancestry passed Python 3.11-3.13. Record this acceptance after the plan amendment merges, then close only if all issue criteria are met.

## Wave 1 source and risk audit

- NEW-01 source refs exist, but `feat/r34-python-data-foundation` is a broad 94-path, +10,094/-7 branch; `feat/ingestion` is narrower at 3 paths, +1,196. Use selected reviewed Python hunks from a fresh-main branch, never merge either branch wholesale. `9ce04fc` is package/wheel-only and `355637c` is schema/README/coordination work, so neither belongs in NEW-01.
- NEW-02 source commits are present but based on old shared history; `ec9f669` precedes its child `5ba8603`. Exclude TypeScript hunks and include the additional numeric-state regression test from `96b819a` in the file claim.
- Both PRs share `normalize.py` and `test_normalize.py`; isolated preparation may run in parallel, while integration and final review are explicitly sequential. NEW-01 delivers input adapters and Arrow/Parquet reader tests; NEW-02 adds reducer regression/scale acceptance without replaying fixes already selected by latest96. Two independent reviewers and two testers report on each exact PR head per issue #26.
- Source review found Arrow/Parquet handlers using `to_pylist()` on full 4096-row batches before per-cell/record budget checks. The plan requires an oversized/nested value regression and review of this transient memory risk.

## Agent capacity and next checkpoint

All 22 roles completed the initial read-only audit. Two independent plan reviews and two tester audits found corrections that are now incorporated; they must re-review/retest the exact final commit. Issue #26 is followed as written: every PR requires two independent reviewer reports, two tester reports and committed visual evidence paths in its body. Isolated preparation may proceed in parallel at the owner request. Only the current wave opens PRs; integration/promotion follows approved dependencies and fresh exact-head checks after plan merge.

## Public scope and evidence actions after plan merge

- **#4:** RM-01/TRI-01 must publish a scope addendum linking the owner-approved amendment: Python-only 0.1.0 excludes TypeScript #14/#15 and npm package #25, deferred to v1.1. Retain every applicable Python child acceptance, including #19/#20/#21/#22/#23/#24/#26/#27/#29. Keep #4 open until the scoped roll-up and G3 evidence pass; a private plan note alone does not amend its public npm requirement.
- **#29:** RM-01 must publicly retarget the old integrated-PR #31 criteria to the focused replacement PRs, linking their keeper/source mapping. Each focused PR needs two genuine independent reviewer reports and two genuine tester reports with session identity, exact SHA, scope, findings and commands/results. Rendering PRs need actual committed gallery output embedded in the body. Plan diagrams are plan evidence only. Keep reports distinct from GitHub APPROVED states; do not self-approve or change repository rules. Keep #29 open until the retargeted workflow is demonstrated and audited.
- **#27:** Publish scoped epics/stories/tasks with real issue IDs, labels, milestones, dependencies, acceptance and planned/implemented/verified/released states. Commit the issue map, remote issue/milestone/label snapshot and review/test/visual policy under `docs/process/`. Record the historical 900 count as unmet and the explicit 0.1.0 owner waiver; never present waiver as 900 completed issues. Cite primary GitHub secondary-limit and author-approval documentation with actual access dates and claim-to-source review before closure: [REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits), [REST best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api), [approving PRs](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews).
- **#28:** Publish the exact owner revision and current real issue counts after this amendment merges, then close as superseded for this release. Until the public update exists, the issue remains open P0.

These are pending external actions, not claims they have occurred. The amendment itself stays within `context/release-0.1.0/`; Wave 5 publishes the process/research deliverables at their claimed product-documentation paths.

## Additional acceptance boundaries

Named #21 negative tests must cover script/title/cell injection, script-closing sequences, dangerous configuration values, traversal, absolute-path escape, arbitrary remote-URL/code execution and unrelated-file overwrite. Document optional network-loaded runtimes. Independently inspect dependencies, diagnostics and packaging for accidental credential disclosure; record exact-commit security review and actual-main test evidence.

For #22, Wave 1 records normalizer-only measurements. Keep #22 open until Wave 2/5 tests bounded renderer payload rows and bytes at 10, 1K, 100K, 1M and 10M rows and non-author QA independently replicates them. Save machine-readable exact-main SHA/date, environment/Python/dependency versions, commands, input/normalized/retained/renderer counts and bytes, strategy/warnings/limits, wall time, memory method/peak, replicator identity, result/failures and explicit unrun limitations. An unrun size is not a pass.

For #19, commit dated primary sources for the five renderers, Deep Agents and MCP; separate observed public behavior, documentation facts, inferences and unknown proprietary internals. Review runtime/dependency, licensing, scale and output-format trade-offs without invented benchmark claims, and map every capability/architecture claim to tested evidence or clearly labeled future work.

## RM scope/size rulings

RM-01 approves focused size exceptions for this coherent plan amendment (approximately 1,100 metadata/documentation changed lines) and NEW-01 (approximately 2,000 lines of existing normalizer plus necessary tests/public imports). Do not split arbitrarily or omit tests to reach a line count. Two independent exact-head reviewer reports, two tester reports, current-main rebase/checks and merge gates remain unchanged; larger or unrelated expansion needs a new plan-change ruling.

NEW-01 includes minimal `deepviz.__init__` model/normalize exports so `from deepviz import normalize` is callable; NEW-05 extends tools exports later. NEW-02 owns R07/R17/R45 regression tests plus `scripts/verify_python_scale.py` and `tests/test_release_scale.py`.
