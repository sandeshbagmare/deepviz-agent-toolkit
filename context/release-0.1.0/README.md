# DeepViz release 0.1.0 planning index

- Default branch: `main`
- Current main SHA: `54dd12e2d8d5d69e25426e92c313f0f79e00de81`
- Date: 2026-11-28
- Plan version: 1.1 (owner decisions recorded; plan-change PR pending)

The plan baseline is merged on `main@54dd12e2d8d5d69e25426e92c313f0f79e00de81` as PR #39. Wave 1 is current; #40/#41 remain preparation drafts, and fix_norm exclusively owns the unpublished NEW-01 replacement. RM-01 reports 3/3 result-main CI checks green; QA-01 baseline verification passed: fresh Python 3.12, 118 strict tests/0 skips, Ruff/mypy/build/Twine and 12 schema cases. This is existing ChartSpec/source baseline evidence only, not clean-install or future-feature acceptance. The earlier `main@f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` QA results remain historical evidence, not a new QA pass.

The captured inventory, adjusted for the known #39 merge, has 76 refs including main, 11 PR records (8 open/3 merged), 35 genuine issues:34 open/1 closed and10 open P0 including deferred14. TRI-01 receipt at09:43:16Z excludes11 PRs from issue counts; ref/PR inventory is still the captured baseline. Product preparation drafts #40-46 and the stale #31 draft remain open/non-ready until their gates pass. The existing workflow and 22-file planning packet are unchanged.

The original branch and issue disposition tables remain a historical snapshot at `484ff08...`; the audit in `18-current-state-audit.md` records the pre-merge `f692014...` baseline. Current transition details are in the tracker and canonical YAML.

## Index

- [`00-repo-snapshot.md`](00-repo-snapshot.md)
- [`01-branch-inventory.md`](01-branch-inventory.md)
- [`02-pr-inventory.md`](02-pr-inventory.md)
- [`03-v1-scope.md`](03-v1-scope.md)
- [`04-dependency-and-conflict-map.md`](04-dependency-and-conflict-map.md)
- [`05-merge-plan.md`](05-merge-plan.md)
- [`06-pr-plan.md`](06-pr-plan.md)
- [`07-agent-topology.md`](07-agent-topology.md)
- [`08-sdlc-workflow.md`](08-sdlc-workflow.md)
- [`09-review-checklist.md`](09-review-checklist.md)
- [`10-test-strategy.md`](10-test-strategy.md)
- [`11-bug-triage.md`](11-bug-triage.md)
- [`12-release-gates.md`](12-release-gates.md)
- [`13-risk-register.md`](13-risk-register.md)
- [`14-tracker.md`](14-tracker.md)
- [`15-plan-changelog.md`](15-plan-changelog.md)
- [`16-feature-verification.md`](16-feature-verification.md)
- [`17-agent-onboarding.md`](17-agent-onboarding.md)
- [`18-current-state-audit.md`](18-current-state-audit.md)
- [`release-0.1.0.yaml`](release-0.1.0.yaml)

## Local renderer-split proposal

Append-only correction of published PLAN-CHANGE-02@0f6 on baseline main54dd; unpublished until RM scope check, fresh4reports required on the new exact head; no product promotion before merge. User forbids main-to-feature merges, force-push/history rewrite and branch deletion. fix_norm alone owns the UNPUBLISHED normalization-rebased replacement; old #40 is unaccepted/nonpromotable. Published #41-46 remain preserved preparation/source records; after dependency main QA, use fresh unpublished true-rebase/scoped-selection branches, publish once, and map full keeper paths/SHAs before superseding old PRs. All tests/exact2+2/CI/main-QA gates remain.

## Use and amendments

Read only the topic needed. Full paths, PR/issue facts, overlap matrix, assignments and states are in YAML. Owner-confirmed scope is Python-only: shared schema, bounded normalization and reducers, optional Arrow/Parquet input via `[columnar]`, five Python renderers, Deep Agents tools and local stdio MCP. TypeScript #14/#15 and npm package #25 are deferred to v1.1. TRI-01 publicly amended #4 at09:36:12Z, closed #28 not_planned at09:38:15Z, and retargeted #29 at09:41:56Z; #4/#29 remain open and900 remains unmet, not completed. All in-scope product, CI, review, QA and P0 gates still apply.

Any agent may propose a `plan-change` PR limited to this directory. RM-01 reviews/approves; update YAML and matching Markdown together and append a dated row to `15-plan-changelog.md`.
