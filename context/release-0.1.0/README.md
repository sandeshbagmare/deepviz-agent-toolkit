# DeepViz release 0.1.0 planning index

- Default branch: `main`
- Main SHA verified for this status update: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1 (owner decisions recorded; plan-change PR pending)

Live state is reconciled to default branch `main` at `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`. Owner decisions confirm Python-only 0.1.0, Arrow/Parquet support through the optional `[columnar]` extra, and version `0.1.0`; TypeScript issues #14/#15 and npm package issue #25 are deferred to v1.1. The caller explicitly revised #28 for 0.1.0; the plan-change PR must merge before the issue is updated/closed. Wave 0 checks are recorded in `18-current-state-audit.md`; Wave 1 remains queued until this plan change is approved and merged.

The repo currently has **76 remote branches** including `main` (75 non-default), **11 PR records** (9 open, 2 merged), **35 open issues**, and **11 open P0 issues**. Seven product PRs (#40-#46) are open drafts for planned Waves 1-5, with plan-change PR #39 and stale draft PR #31 also open. Product drafts are preparation only; future-wave drafts remain non-ready until dependencies complete. The only current-main workflow is the focused ChartSpec matrix. The planning packet contains 22 files: README, 00-18, canonical YAML, and the committed wave-map SVG evidence.

The original branch and issue disposition tables remain a historical planning snapshot at main `484ff08...`; live counts and status at `f692014...` are in `18-current-state-audit.md` and the tracker below.

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

## Use and amendments

Read only the topic needed. Full paths, PR/issue facts, overlap matrix, assignments and states are in YAML. Owner-confirmed scope is Python-only: shared schema, bounded normalization and reducers, optional Arrow/Parquet input via `[columnar]`, five Python renderers, Deep Agents tools and local stdio MCP. TypeScript #14/#15 and npm package #25 are deferred to v1.1. The caller explicitly revised #28; publish the decision and real issue counts after this plan change merges, then close #28 as superseded. All in-scope product, CI, review, QA and P0 gates still apply.

Any agent may propose a `plan-change` PR limited to this directory. RM-01 reviews/approves; update YAML and matching Markdown together and append a dated row to `15-plan-changelog.md`.
