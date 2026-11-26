# C18 — independent restart and coordination-file audit

Owner: fresh child of C00; no spawning. Write only `docs/coordination/reports/C18-recovery-audit.md` in the main checkout. Do not edit production, tests, root docs, roster, state, or another report. Save your report immediately with session ID and current/next action.

Read `RESUME.md`, `AGENTS.md`, `docs/coordination/{REQUEST,STATE,ROSTER,BRIEF,WORKLOG}.md`, C00's report, and saved C17/C18 task briefs. Review the recovery workflow as an independent new session with no prior chat. This is a documentation/coordination audit, not product reviewer or tester signoff.

Check the following concretely, using bounded reads/inline assertions as useful:

1. A restarted agent can locate actual project, current owner, source branch, one next action, acceptance gaps, preserved worktrees, and real report/session mappings without the old chat.
2. Concurrent writers and nested spawn permissions are unambiguous, total reserved/running budgets cannot exceed22, and canceled sessions are not implicitly relaunched. Latest steering gives C17 product-inclusive21 plus your separate1, at most22 total including C00. `C17-capacity-steering.md` supersedes the prior20+1 reservation.
3. Distinguish observed execution from attempted/queued API dispatch, seed reports from candidate acceptance, and product claims from documentation checks. Superseded C16 should not retain integration authority.
4. References to existing authoritative files resolve; future worker reports may be pending but must be labeled honestly. No credentials/PII/private account details were added; project paths may be local recovery pointers, not shipped API data.
5. Reports have task/session/branch/SHA/dirty-state, owned paths, commands/results/skips, limitations and executable next action. Permanent ledgers are not scheduled for deletion.

Record any material contradictions with file/line references and smallest recommended fix, exact commands/exit codes, what was not checked and next action. Do not expand scope or wait/poll for product integration. Work within about8 tool calls if practical; then return only report path plus urgent material findings. C00 will fix recovery docs; C17 owns product completion.
