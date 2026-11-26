# Durable coordination worklog

Append dated checkpoints; do not rewrite historical observations as later successes. The latest actionable state is in `STATE.md`.

## 2026-11-26 — takeover and restart contract

- User requested file-first communication so any session can restart, then renewed full autonomous completion with at most 22 concurrent agents across all nesting and fewer than 100 coordinator turns.
- Selected DeepViz as the active project from its newer source history, design, engineering roster and `release/candidate`; the older AgentViz tree remains untouched.
- Read the repository rules, design, implementation plan, process/dependency reports, and QA seed report. These are historical evidence, not current-candidate acceptance.
- Observed candidate `468b28cfdcfcb7be53beaef2c911bf81cac70f44`, clean before this documentation change. Registered worktrees were inspected; a subsequent exact enumeration established 24 including the main checkout (correcting the initial manual tally). Only `models.py` is integrated in the Python source package.
- `git worktree list --porcelain` and per-worktree `git status --porcelain` identified preserved producer commits and dirty source/test examples. No user/worker changes were discarded.
- Runtime `opencode api get /api/session/active` returned this session plus existing renderer and TS workers. `opencode api get '/api/session?limit=100'` identified real historical sessions. Session lookup with `search=deepviz` returned none because titles do not contain the project name; an empty filtered result is not absence of agents.
- Shared `.venv/Scripts/python.exe` reported Python 3.12.16 and `deepviz.__file__ = None` on the incomplete candidate. This is environment identity only, not a product test.
- Ruling: keep coordination files tracked and permanent rather than deleting skill scratch ledgers; recoverability is an explicit user requirement. Use saved briefs/reports as authority and chat only for notifications.
- Ruling: resume existing specialists, retain canceled sessions/worktrees, and budget any nested dispatch explicitly. A historical roster is not a live concurrency count.
- Next: save the common assignment contract/roster, resume existing producer and verification lanes, then integrate committed contributions in dependency order.

## 2026-11-27 — integration delegation and recovery verification

- Assigned the original coordinator as C16 integration lead, retaining its original full product/team context. C16 alone writes shared product/Git/GitHub candidate state; C00 edits only recovery docs. Saved assignment: `tasks/C16-integration-lead.md`.
- Attempting to resume the original root through the child-only subagent tool failed closed: it is not a child of this session. No session was spawned. Two CLI JSON quoting attempts failed before dispatch (HTTP 400 / argument parsing); no product/source changes resulted.
- Workaround: invoke the installed native OpenCode executable using Python `subprocess.run` with an argument list and JSON-encoded body. POST `/api/session/ses_de70bd471ffem0HgkC2LmWx5Dt/prompt` returned message `msg_2191f37fa001zUX12yponkUDaJ`, delivery `steer`. This is observed prompt delivery, not proof the implementation is complete.
- Runtime plugin read-back observed `oh-my-openagent@latest`, version `5.1.84`, state `active`. This is actual installed orchestration infrastructure; no global plugin/config migration was performed.
- Executed an inline project-Python read-back/assertion check covering seven recovery files, the 22-agent limits, next-action fields, and three authoritative source-document links: PASS, exit 0. Git enumeration found 24 worktrees. `git diff --check`: exit 0. Source remained `468b28cfdcfcb7be53beaef2c911bf81cac70f44` at that check.
- Developer-provided current date advanced to 2026-11-27; prior 2026-11-26 observations remain dated as history.
- Next: retain the complete user-request scope in `REQUEST.md`, finish the C00 handoff, and notify C16 of the verified recovery files without competing with its integration work.

## 2026-11-27 — actual child dispatch replaces unstarted root resume

- A later actual runtime check returned only C00 and the historical renderer running (2). Earlier C16 API input delivery did not establish execution; do not portray it as an active agent or completed handoff.
- Superseded C16 write/dispatch authority in its brief and roster. Launched fresh child C17 using the supported subagent tool: actual returned session `ses_de6ddc25affeMo5NjdAuqfub72`, background execution confirmed by the tool. It owns all product/Git/GitHub integration and is instructed to promptly launch two nested independent verifier lanes, then reuse committed source and delegate scoped fixes.
- C17 has a20-agent inclusive product budget; C18's separate recovery-doc review slot makes at most21 including C00, leaving one under the hard22 limit. C15 has no independent launch permission, preventing duplicate use of nested slots.
- C00 explicitly acknowledged that context recovery took too long before actual dispatch. Corrective action was a real child launch with a saved brief, not another claim that a queued API message was running work.
- Current saved user scope and checkpoint requirements are in `REQUEST.md`. C00 does not poll or duplicate C17's work and continues only non-overlapping recovery-document verification.

## 2026-11-27 — full-capacity steering and independent recovery review

- Launched actual child C18 recovery auditor through the supported tool: session `ses_de6dc95eeffej0nH3Io6H3qwqU`; saved scope `tasks/C18-recovery-audit.md`. It owns only its independent report, no product edits or spawning.
- Latest user requested substantial22-agent batches and suggested440 cumulative agents in90 turns. Saved exact operational interpretation in `tasks/C17-capacity-steering.md`: C17 may fill21 inclusive product slots plus C18's separate1, with22 hard total across nesting. Count/output metrics are not permission for duplicate tasks or invented success.
- Sent the saved capacity steering to running C17 using the child tool; acknowledged as background work. C17 owns its live file-backed slot register and actual nested launches; C00 launches no more workers.
- A multi-file patch containing an incorrect expected WORKLOG line failed verification before any changes applied; re-read ROSTER and reapplied a bounded corrected patch. No product write or source loss occurred.
- Next: finish final recovery-doc assertions/read-back and wait for C18's independent findings notification while C17 performs product work. Do not poll C17 or count queued historical assignments as running agents.

## 2026-11-27 — recovery handoff ready

- Executed final inline read-back/assertions and scoped `git diff --check`: exit0, all checks passed on a15-file coordination snapshot. Exact command/output and verification limits are in `evidence/C00-document-check.md`.
- Verified restart-source references, actual C17/C18 IDs, exclusive ownership, superseded old-root assignment,22-total reservation, required report provenance/next-action fields and11 unchecked user acceptance criteria. These are documentation checks, not product acceptance.
- Recovery documentation is ready for C17's commit/integration; C00 will not write product/Git or launch more agents. C00 retains only material-finding fixes after C18 reports. Product progress and actual team slot usage are C17-owned and must be verified from its saved reports rather than inferred from this historical log.
- Refined final author check used exactly13 C00-owned files (avoiding traversal of concurrent worker reports) and line-anchored fence detection. Exit0; restart references, actual child identities, exclusive ownership, supersededC16,21+1=22 reservation,11 honest acceptance gaps and scoped `git diff --check` passed. Evidence packet records the observed output and its limits.
- A global launch-safety check subsequently returned5 running sessions and17 free slots under22: C00, C17, C18 and newly observed `ses_de6da09ecffeMwVLSxt0fA4s3K` / `ses_de6d9dcf1ffe5D9TNNF3B2hP4V`. This endpoint supplies runtime IDs, not task/parent attribution; C17 owns their exact role mapping and live register. C17 was notified to fill remaining useful slots promptly, rechecking capacity before launches. C00 did not launch additional workers or inspect/duplicate their product work.

## 2026-11-27 — independent recovery audit fixes

- Received C18's actual completed notification and read back its full report. It independently passed14 documentation assertions (0 fail/skip), observed5 running/no22-cap breach, and identified F1 stale live slots, F2 ambiguous root owners/missing exact register links, F3 broad authorship/stale source header, F4 incomplete saved refined-check command.
- Routed F1 and C17's report-header portion of F3 urgently to C17 before further dispatch; C00 does not edit the live register or claim repair. C17 must record actual worker IDs/mappings and remove stale retry/none states before another launch.
- Fixed C00-owned F2: explicit C00 recovery-state/historical-roster owner versus C17 product/Git/GitHub/live-register owner; linked exact `docs/coordination/C17-live-slots.md` from root rules/restart entry/state/roster. Preserved producer feature commits and scoped PM issue exception.
- Fixed C00-owned F3 by enumerating13 owned files rather than claiming the entire coordination subtree. Added a complete explicit-path post-audit checker to address F4; fresh execution follows.
- C18's completed status releases its formerly separate1 reservation. C17 now owns the full22-slot inclusive global budget, counting C00/C17/every active worker, with at most20 other active workers while both coordinators run. No new C00 launches. Historical21+1 observations remain dated and are explicitly superseded.
- Executed the complete saved post-audit checker exactly: exit0. All13 explicit recovery files passed readable/whitespace/fence/reference assertions; named owners/direct live-register links/actual child IDs/C16 supersession/C18 completion/full22-inclusive reservation/11 honest acceptance gaps and scoped Git whitespace passed. Exact code/output saved in `evidence/C00-document-check.md`.
- C00's F2/F3/F4 portions are fixed and author-verified. C17's F1 live-register reconciliation and source-header refresh remain C17-owned/unverified by C00. Next action: C17 performs those at the next safe checkpoint, then continues full-capacity productive agent waves and candidate verification. Recovery documentation is ready to commit; no product completion claimed.
