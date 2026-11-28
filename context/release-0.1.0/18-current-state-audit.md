# Current repository and Wave 0 audit

- Repository: `sandeshbagmare/deepviz-agent-toolkit`
- Default branch and exact SHA: `main@f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Audit date: 2026-11-28
- Plan change: v1.1, owner-approved decisions; product branches are published as non-ready drafts for preparation.

## Live Git state and GitHub inventory

- `git fetch origin main` and `git ls-remote origin refs/heads/main` both returned `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`.
- The original inventory counted 68 refs including `main` at the inventory snapshot. The refreshed authenticated GitHub snapshot for this plan review has 76 refs including `main` (75 non-default), 11 PR records (9 open drafts and 2 merged), 35 open issues, and 11 open P0 issues. PRs #40-46 are owner-approved preparation drafts for planned Waves 1-5; they are not ready for merge. PR #39 is the plan amendment draft, and #31 is the stale legacy draft. The plan edits are isolated in the dedicated checkout on branch `plan/release-0.1.0-owner-decisions`, based on current main.
- PRs [#33](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/33) and [#38](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/38) are merged. Open drafts are [#31](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/31) (legacy candidate), [#39](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/39) (plan change), and [#40](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/40) through [#46](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/46) (product preparation across Waves 1-5). #31 remains stale, with 324 changed paths and +36,025/-3; its Python 3.11, 3.12 and 3.13 jobs fail. The focused drafts are not ready for merge before plan approval, dependency completion, rebase, required checks, and exact-head 2+2 evidence.
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
- The caller explicitly revised #28's 900-issue requirement: "as we dont have that many issues will not keep that as requirement". No 900-item evidence exists. #28 remains open P0 until this plan change merges, then publicly amend #4 to waive its historical 900-issue criterion for 0.1.0 while stating it remains unmet; post the authenticated current counts (35 open, 0 closed issues; PRs excluded) and close #28 as superseded. Do not fabricate tickets or closures. All other in-scope issue gates remain.
- [#30](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/30) remains open P0. QA-02 independently ran the strict focused model/schema selection on current main and passed 76 tests; direct model-versus-schema smoke covered valid bar, unknown field, strings/booleans, empty dashboard, and nested dashboard. The exact-main GitHub matrix on #33/#38 ancestry passed Python 3.11-3.13. Record this acceptance after the plan amendment merges, then close only if all issue criteria are met.

## Wave 1 source and risk audit

- NEW-01 source refs exist, but `feat/r34-python-data-foundation` is a broad 94-path, +10,094/-7 branch; `feat/ingestion` is narrower at 3 paths, +1,196. Use selected reviewed Python hunks from a fresh-main branch, never merge either branch wholesale. Do not replay package-only `9ce04fc` or broad schema/README/coordination `355637c` wholesale; the focused selector model/schema changes in current PR #40 are claimed explicitly below.
- NEW-02 source commits are present but based on old shared history; `ec9f669` precedes its child `5ba8603`. Exclude TypeScript hunks and include the additional numeric-state regression test from `96b819a` in the file claim.
- Both PRs share `normalize.py` and `test_normalize.py`; isolated preparation may run in parallel, while integration and final review are explicitly sequential. NEW-01 delivers input adapters and Arrow/Parquet reader tests; NEW-02 adds reducer regression/scale acceptance without replaying fixes already selected by latest96. Two independent reviewers and two testers report on each exact PR head per issue #26.
- Source review found Arrow/Parquet handlers using `to_pylist()` on full 4096-row batches before per-cell/record budget checks. The plan requires an oversized/nested value regression and review of this transient memory risk.

## Agent capacity and next checkpoint

All 22 roles completed the initial read-only audit. Two independent plan reviews and two tester audits found corrections that are now incorporated; they must re-review/retest the exact final commit. Issue #26 is followed as written: every PR requires two independent reviewer reports, two tester reports and committed visual evidence paths in its body. Owner-approved draft preparation may proceed across planned waves; promotion/merge follows approved dependencies and fresh exact-head checks after plan merge.

## Public scope and evidence actions after plan merge

- **#4:** RM-01/TRI-01 must publicly amend the original acceptance criteria: Python-only 0.1.0 excludes TypeScript #14/#15 and npm package #25, deferred to v1.1; the original 900-issue criterion is waived for this release but remains unmet at the live counts, with no fabricated tickets or closures. Keep #28 open until the amendment is published, then close it as superseded. Retain every applicable Python child acceptance, including #19/#20/#21/#22/#23/#24/#26/#27/#29. Keep #4 open until the scoped roll-up and G3 evidence pass; a private plan note alone does not amend its public acceptance criteria.
- **#29:** RM-01 must publicly retarget the old integrated-PR #31 criteria to the focused replacement PRs, linking their keeper/source mapping. Each focused PR needs two genuine independent reviewer reports and two genuine tester reports with session identity, exact SHA, scope, findings and commands/results. Rendering PRs need actual committed gallery output embedded in the body. Plan diagrams are plan evidence only. Keep reports distinct from GitHub APPROVED states; do not self-approve or change repository rules. Keep #29 open until the retargeted workflow is demonstrated and audited.
- **#27:** Publish scoped epics/stories/tasks with real issue IDs, labels, milestones, dependencies, acceptance and planned/implemented/verified/released states. Commit the issue map, remote issue/milestone/label snapshot and review/test/visual policy under `docs/process/`. Record the historical 900 count as unmet and the explicit 0.1.0 owner waiver; never present waiver as 900 completed issues. Cite primary GitHub secondary-limit and author-approval documentation with actual access dates and claim-to-source review before closure: [REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits), [REST best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api), [approving PRs](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews).
- **#28:** Publish the exact owner revision and current real issue counts after this amendment merges, then close as superseded for this release. Until the public update exists, the issue remains open P0.

These are pending external actions, not claims they have occurred. The amendment itself stays within `context/release-0.1.0/`; Wave 5 publishes the process/research deliverables at their claimed product-documentation paths.

## Additional acceptance boundaries

Named #21 negative tests must cover script/title/cell injection, script-closing sequences, dangerous configuration values, traversal, absolute-path escape, arbitrary remote-URL/code execution and unrelated-file overwrite. Document optional network-loaded runtimes. Independently inspect dependencies, diagnostics and packaging for accidental credential disclosure; record exact-commit security review and actual-main test evidence.

For #22, Wave 1 records normalizer-only measurements. Keep #22 open until Wave 2/5 tests bounded renderer payload rows and bytes at 10, 1K, 100K, 1M and 10M rows and non-author QA independently replicates them. Save machine-readable exact-main SHA/date, environment/Python/dependency versions, commands, input/normalized/retained/renderer counts and bytes, strategy/warnings/limits, wall time, memory method/peak, replicator identity, result/failures and explicit unrun limitations. An unrun size is not a pass.

For #19, commit dated primary sources for the five renderers, Deep Agents and MCP; separate observed public behavior, documentation facts, inferences and unknown proprietary internals. Review runtime/dependency, licensing, scale and output-format trade-offs without invented benchmark claims, and map every capability/architecture claim to tested evidence or clearly labeled future work.

## RM scope/size rulings

RM-01 approves focused size exceptions for this coherent plan amendment (approximately 1,100 metadata/documentation changed lines) and NEW-01 (at most 2,750 changed lines across exactly the 10 claimed paths). PR #40 at `a94f85c47e9a18f01009484a6813738eb8259a03` against `main@f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` measures 2,687 additions + 2 deletions = 2,689 changed lines. The 61-line tolerance is only for necessary review/rebase fixes and regenerated normalization evidence within this existing coherent task; additional paths or unrelated scope require a new plan-change ruling. Do not split arbitrarily or omit tests to reach a line count. Two independent exact-head reviewer reports, two tester reports, current-main rebase/checks, dependency order and sequential merge gates remain unchanged.

NEW-01 includes minimal `deepviz.__init__` model/normalize exports so `from deepviz import normalize` is callable; NEW-05 extends tools exports later. Its five additional claimed paths are `python/deepviz/src/deepviz/models.py`, `schemas/chart-spec.schema.json`, `scripts/benchmark_scale.py`, `docs/verification/normalization/normalization-output.json`, `docs/verification/normalization/normalization-output.svg`. They cover the shared selector model/schema boundary, existing smoke harness and measured normalization JSON/SVG evidence only. NEW-02 owns R07/R17/R45 regression tests plus `scripts/verify_python_scale.py` and `tests/test_release_scale.py`.

## Post-merge main54dd baseline update (local amendment)

PR #39 merged at `54dd12e2d8d5d69e25426e92c313f0f79e00de81`; its tree equals reviewed plan `870c556d`. QA-01 independently verified a fresh CPython 3.12.16 source environment: 118 strict tests passed with zero skips, Ruff/mypy/build/Twine passed, and 12 runtime/generated/checked-in schema smoke cases agree. The report has 49 PASS check records and observed the focused Python 3.11/3.12/3.13 GitHub matrix green. This is existing ChartSpec/source and plan-tree baseline evidence only; no clean installed wheel/sdist, CLI/MCP, normalizer, renderer or full-release acceptance is implied.

Local source reports: `%TEMP%/deepviz-qa01-evidence-54dd12e2-7ed9d30e/postmerge-report.md` and `.json`. JSON SHA-256 `6ed531ee2167d10c97371f718b8b8bc291a83b279866b8ff4075310d020c7607`; these are local TEMP references, not new committed galleries. Earlier sections remain the dated pre-merge snapshot. The prior local/unpushed7296 statement was wrong: `7296d672` is published on old #40 and contains a prohibited main-to-feature merge. Preserve that unaccepted branch; only fix_norm writes the unpublished true-rebased replacement, with provenance and all3 boundedness fixes pending final size proof.

## Recovered policy and public receipt (supersedes earlier pending status)

User policy is binding: no main-to-feature merge commits, no force-push/history rewrite, and no branch deletion. Preserve published #40-46 branches as preparation/source records. After each prerequisite is merged and verified on main, build a fresh UNPUBLISHED current-main branch by true rebase of a private copy or scoped product selection, with zero feature merge commits; publish it once, open only the necessary replacement PR, and map every retained/excluded path and source/keeper SHA before RM may supersede the old PR. No quota/duplicate tickets or PRs, no old-draft promotion, no dropped tests; all fresh exact-head 2+2/CI/dependency and non-author main-QA gates remain. Only fix_norm writes unpublished normalization-rebased; observed4199b4d has zero feature merges after54dd and ACTUAL2683/10paths, leaving67 under2750. Fifth Arrow-schema-DAG work-budget fix remains PREPARING with fix_norm in the same paths; historical383/127 at7e is before that fix, not acceptance. Old published40/7296 is unaccepted. StaticA975text/3PNG and NEW04 overlay978text/15paths/8PNG remain preparation, not main QA.

TRI receipt `%TEMP%/deepviz-v010-ops/tri01-publish-20261128T093210Z/final-action-summary.json`, SHA-256 `362fe4855e91e360ae70e6360a9108ac514ceefd67368fc41ef4bf523845217a`, read back2026-11-28T09:43:16Z: #4 amended09:36:12Z/open; #28 closed not_planned09:38:15Z after #4; #29 retarget09:41:56Z/open.35 genuine issues=34open/1closed,11PRs excluded,10open P0 including deferred14. No900 completion/product acceptance. Earlier pending/census text here and in untouched baseline scope/risk documents is historical, superseded by this receipt.
