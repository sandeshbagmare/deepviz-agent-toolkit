# DeepViz engineering rules

## File-first coordination and restart recovery
- Read `RESUME.md` and `docs/coordination/STATE.md` before starting or resuming work. Chat is a notification channel, not the project memory.
- Every assignment and handoff lives under `docs/coordination/`. Before substantial work, record owner/session, branch, base SHA, allowed paths, acceptance checks, current action and next action in the assigned report. Update it after meaningful progress, a failed check, a blocker, a commit, and before returning.
- Reports include exact commands, exit codes, test totals/skips, source identity, artifact locations, decisions and limitations. Do not record credentials, hidden reasoning, or invented success. Save a useful partial checkpoint even when interrupted.
- C00 alone updates recovery `STATE.md`, `WORKLOG.md` and the historical `ROSTER.md`. C17 alone owns candidate integration/shared-branch Git/GitHub writes and the live reservation register `docs/coordination/C17-live-slots.md`. Producers may commit tested scoped work on their own feature branches; the explicit PM issue-management exception in `BRIEF.md` remains scoped to its assignment. Each worker writes only its assigned report/source paths. Preserve these records across session restarts; never delete handoffs as temporary scratch.
- Latest user steering: fewer than 100 coordinator turns, no more than **22 concurrent agents total across all nesting levels**. Prefer resuming existing sessions over duplicate workers. The old launch pause is superseded by renewed autonomous delegation authorization, but six previously canceled sessions are not restarted. Only the explicitly budgeted coordination lane may launch nested workers; all other workers must not spawn.
- Before dispatch, save the brief and reserve its slot in C17's live register `docs/coordination/C17-live-slots.md`; record the returned session ID there immediately. `ROSTER.md` is C00's historical ownership map, not the live launch register. C17 supersedes the unstarted C16 assignment. No independent nested launches outside C17's total budget. Unknown historical state is not proof of completion; reconcile actual active sessions and all returned worker IDs before adding workers.
- On restart, inspect Git/worktrees and read saved reports, then resume the first unfinished action. Never reset, discard dirty worktrees, rerun completed integrations blindly, or count a historical report as current-candidate verification.

## Contract and ownership
- Python is primary; `python/deepviz/src/deepviz/models.py` defines the versioned schema.
- Regenerate `schemas/chart-spec.schema.json` after changing contracts; test Python/TypeScript agreement.
- Feature work uses isolated branches/worktrees. Do not modify another worker's files.
- Read the design and architecture before implementation. Do not expand model-authored schemas to accept executable code.

## Verification
- Run `python -m pytest`, `ruff check .`, `mypy`, and distribution builds in the project virtual environment.
- Run `npm ci`, `npm run build`, `npm run typecheck`, `npm test`, and `npm pack --dry-run --workspace @deepviz/agent-toolkit` for npm changes.
- Exercise 10, 1K, 100K, 1M, and 10M through the streaming path; report input/output counts, elapsed time and memory methodology.
- Inspect real SVG/PNG/browser output, not just artifact existence. Browser console errors are test failures.
- Record exactly what ran and the source commit. Never promote a skipped test or uninstalled optional dependency to a pass.

## Safety and output
- Never use `eval`, `exec`, shell execution, arbitrary JavaScript expressions, or remote URL ingestion from chart specifications.
- Distinguish data strings from explicitly authorized local file paths. MCP must not expose arbitrary filesystem access.
- Bound reduced data before renderer serialization. Explain all lossy transformations in metadata.
- Escape HTML and script-embedded JSON. Never trust titles, labels, field names or cell values.
- Use unique artifact names/directories; preserve files not produced by the current operation.
- Keep authentication tokens in memory only and out of subprocess arguments/logs/repo files.

## Delivery evidence
Every PR links real issues and includes rendered output plus its correctness rationale, two independent reviewer-agent reports, and two independent tester-agent reports. Agent review comments are not GitHub human approvals. Do not close issues without evidence. Do not manufacture issue counts or performance claims.
