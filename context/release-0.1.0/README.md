# DeepViz release 0.1.0 planning index

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

This plan targets verified default branch `main` at `484ff08ddcae6c36d43ce61de774c00b6c422c88`. It is a proposed release plan, not approval to merge product work. Owner: RM-01. Live status is sourced from `release-0.1.0.yaml`; Markdown explains it. The requested names produce **20 files** (README, 00-17, YAML).

There are **65 non-default remote branches**, **3 PRs** (2 merged, 1 open draft), **35 open issues**, six proposed waves and eight focused new PRs. Branch dispositions: `CLOSE-SUPERSEDED` 4, `DEFER` 25, `V1-CONSOLIDATE` 25, `V1-FIX-FIRST` 11. PR dispositions: `CLOSE-SUPERSEDED` 1, `V1-MERGE` 2. Wave 0 is green; no product PR is ready to merge.

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
- [`release-0.1.0.yaml`](release-0.1.0.yaml)

## Use and amendments

Read only the topic needed. Full paths, PR/issue facts, overlap matrix, assignments and states are in YAML. Scope is **PROPOSED - needs owner confirmation**: Python-first shared schema, bounded normalization, five Python renderers, Deep Agents tools and local stdio MCP. TypeScript/npm is deferred to v1.1 pending confirmation: main README says Python-first and the separate npm branch is +11,681/-1 over 86 paths with no main verification. Issue #28 is open P0 and blocks G3 under the supplied gate.

Any agent may propose a `plan-change` PR limited to this directory. RM-01 reviews/approves; update YAML and matching Markdown together and append a dated row to `15-plan-changelog.md`.
