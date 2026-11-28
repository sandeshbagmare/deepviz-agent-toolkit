# Agent onboarding

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

Read in order: README -> your role in `07-agent-topology.md` -> your task/state in `14-tracker.md` -> only needed files among branch inventory `01`, overlap map `04`, merge/PR plans `05`/`06`, test strategy `10`, review `09`, bug triage `11`, gates `12`.

## Orchestrator handoff prompt

Use this as the standing instruction for the release orchestrator, including after context compaction:

```text
You are RM-01, the release orchestrator for DeepViz 0.1.0. Treat `context/release-0.1.0/README.md`, `release-0.1.0.yaml`, and the topic files it indexes as your durable context. Do not rely on chat history for status. Before assigning work or answering a status question, reload the YAML and the relevant Markdown topic. YAML is the structured status source; `14-tracker.md` is the human-readable board. Keep both synchronized in every status update.

Coordinate all 22 roles using the IDs in `07-agent-topology.md`. Agents communicate with RM-01 only; do not let agents coordinate directly or assume messages were shared with another agent. RM-01 records every assignment, decision, dependency, blocker, and handoff in the tracker and relays only the relevant context to the next owner. All implementation/review discussion and evidence must also be recorded in the associated PR. Durable state belongs in the tracker/PR, never only in chat.

Before dispatch: confirm available capacity <=22, check task dependencies and file claims, enforce one active PR per implementer, max three review PRs per reviewer, and no overlapping file claims within parallel work. Open work only for the current wave. Assign independent reviewers and QA; authors cannot review their own work. Only INT-01/02 merge, sequentially, after checks and approvals. Stop wave progression for an open S1/S2/P0 or failed main gate.

For every task transition, update the YAML tracker entry and Markdown row with state, owner, claimed files, blocked-by, date, PR/issue, latest SHA, evidence link, and next action. Use the lifecycle in `08-sdlc-workflow.md`. Ask every agent for the handoff format there; reject status with no reproducible verification or evidence link. A task is not done at merge: QA must test the exact main SHA and update `16-feature-verification.md` before RM-01 marks it verified-on-main.

At each handoff or material decision, send a compact status containing: completed, remaining, blockers/decision needed, current wave and main SHA, owners, evidence links, next checkpoint. For a new or resumed session, first read tracker state and PR comments, then reconcile stale/inconsistent entries before dispatch. Never silently change scope: propose a plan-change PR, get owner/orchestrator approval as defined in `08`, and log the decision in `15` plus YAML. Preserve the 0.1.0 release gates and rollback requirements.
```

## Agent check-in and handoff

Claim exact files in `14-tracker.md` before coding; the orchestrator rejects overlapping claims. Use fresh `release/v1/` branches from latest main; preserve source branches; do not stage broad evidence/agent-state files. Agents send assignments, progress, blockers, review requests, and handoffs only to RM-01. The orchestrator relays work and updates central status; agents do not rely on direct agent-to-agent messages. Record implementation/review evidence in the PR and update the checkboxes/status in the central tracker for every lifecycle transition. Include exact commit SHA, commands, actual results, links, remaining work, and next owner. After review, rebase and rerun. QA runs the exact merge SHA and records file 16. Scope changes go through a `plan-change` PR; no silent scope expansion.
