# DeepViz release 0.1.0 planning index

- Default branch: `main`
- Current main SHA: `54dd12e2d8d5d69e25426e92c313f0f79e00de81`
- Date: 2026-11-28
- Plan version: 1.1 (owner decisions recorded; plan-change PR pending)

The plan baseline is merged on `main@54dd12e2d8d5d69e25426e92c313f0f79e00de81` as PR #39. Wave 1 is current; #40/#41 remain preparation drafts, and INT-01 exclusively owns NEW-01 integration onto current main. RM-01 reports 3/3 result-main CI checks green; QA-01 baseline verification passed: fresh Python 3.12, 118 strict tests/0 skips, Ruff/mypy/build/Twine and 12 schema cases. This is existing ChartSpec/source baseline evidence only, not clean-install or future-feature acceptance. The earlier `main@f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` QA results remain historical evidence, not a new QA pass.

The captured inventory, adjusted for the known #39 merge, has 76 refs including main, 11 PR records (8 open/3 merged), 35 open issues and 11 open P0 issues. This local draft does not claim a fresh full inventory fetch. Product preparation drafts #40-46 and the stale #31 draft remain open/non-ready until their gates pass. The existing workflow and 22-file planning packet are unchanged.

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

Local scope/evidence and renderer-split amendment only, based on merged `main@54dd12e2d8d5d69e25426e92c313f0f79e00de81` (tree equal to plan `870c556d9aaf98e3a94c1ee17e2a77fc5daf83d3`). PR #39 and its checkout remain untouched; no new GitHub PR or merge is authorized. Wave 1 is current, NEW-01/02 remain drafts, and INT-01 exclusively owns NEW-01 current-main integration. QA-01 verified the existing ChartSpec baseline only; future feature/release acceptance stays unverified. Actual renderer child bases must be their future verified dependency merges. Proposed sequence: `NEW-02 -> NEW-03A -> NEW-03B -> NEW-04`. Nine top-level entries map ten currently declared product PR slices across eight logical changes, including NEW-08 package/CI children; actual GitHub counts are the captured baseline above. NEW-03 completes only after both child merges are verified on main. See `05-merge-plan.md` and canonical YAML; the existing wave-map SVG remains baseline evidence and is not a new amendment approval.

## Use and amendments

Read only the topic needed. Full paths, PR/issue facts, overlap matrix, assignments and states are in YAML. Owner-confirmed scope is Python-only: shared schema, bounded normalization and reducers, optional Arrow/Parquet input via `[columnar]`, five Python renderers, Deep Agents tools and local stdio MCP. TypeScript #14/#15 and npm package #25 are deferred to v1.1. The caller explicitly revised #28; publish the decision and real issue counts after this plan change merges, then close #28 as superseded. All in-scope product, CI, review, QA and P0 gates still apply.

Any agent may propose a `plan-change` PR limited to this directory. RM-01 reviews/approves; update YAML and matching Markdown together and append a dated row to `15-plan-changelog.md`.
