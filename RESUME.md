# Resume DeepViz here

This repository, **DeepViz Agent Toolkit**, is the active charting project. The older AgentViz project is separate and must not be overwritten.

## Read in this order

1. `AGENTS.md` — safety, ownership, verification, and file-first communication.
2. `docs/coordination/STATE.md` — current action, blockers, and ordered next actions.
3. `docs/coordination/ROSTER.md` — historical ownership, plus **`docs/coordination/C17-live-slots.md`** — actual current worker IDs, reservations, states and concurrency budget. Reconcile this live file with runtime before any launch; missing/stale IDs are not permission to relaunch.
4. `docs/coordination/WORKLOG.md` and the relevant files in `docs/coordination/reports/` — decisions and reproducible handoffs.
5. `docs/coordination/REQUEST.md` — complete requested scope and latest operational limits.
6. `docs/superpowers/specs/2026-11-26-deepviz-design.md`, `docs/superpowers/plans/2026-11-26-deepviz-plan.md`, and `docs/process/dependency-gates.md` — product contract and acceptance gates.

## First commands after any restart

Run from the repository root in PowerShell:

```powershell
git status --short --branch
git log -8 --oneline
git worktree list --porcelain
opencode api get /api/session/active
```

Compare these observations with the ledger before writing or launching agents. Existing feature worktrees are preserved; some contain uncommitted work. Agent sessions do not need to remain alive for their saved work to survive, but **work not yet written to files cannot be recovered from these notes**. Reuse recorded sessions where possible. Do not infer that a missing session is a completed task.

## User constraints

- Work autonomously on the complete Python-first visualization toolkit, npm SDK, five engines, Deep Agents tools, MCP, research, CI, scale and rendered-output verification.
- Communicate assignments, progress, decisions, failures and handoffs primarily in files so a fresh session needs no previous chat.
- At most 22 concurrent agents, counting nested agents; fewer than 100 coordinator turns. Nested dispatch needs an explicit reserved slot.
- Every merged PR needs two independent reviewer-agent reports, two tester-agent reports and real rendered output, all tied to the reviewed source. Agent reports are not human GitHub approvals.
- Track the requested 900 legitimate created-and-resolved GitHub issues honestly. Do not manufacture defects, fake closures, or equate test cases with closed issues.
- Never claim unlimited input formats, 10M visible independent browser marks, proprietary implementation access, or a passing gate without evidence.

## Recovery contract

The coordinator maintains the current-state files. Workers own separate reports and source worktrees. At each checkpoint save: task/status, session, branch/base/current SHA, dirty paths, completed checks and exact results, blocker/decision, and **one executable next action**. A brief chat reply points to the report rather than replacing it. Keep durable reports; generated datasets/caches remain untracked.
