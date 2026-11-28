# Review checklist

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

Every PR needs two distinct independent reviewer-agent reports and two distinct independent tester-agent reports on the exact PR head, as required by issue #26. Each report records identity/session, scope, exact commit, findings, commands, results and limitations; material findings need fix and retest evidence. Rebase or any new commit invalidates prior reports. Human/code-owner approvals required by repository policy remain separate. Never count an author's own report. Commit screenshots/SVG/PNG and embed their repository paths in every PR body, including plan-only and non-rendering changes; artifacts must depict the actual tested input/output or release-plan state, not a log-only substitute.

Check correctness/acceptance, meaningful tests, bounds/overflow/failure handling, safe HTML/spec/path use, secrets, unrelated edits, API consistency, capability/fallback docs, performance, issue/plan link and size (target <=400, hard cap 1,000 except pure rename). Report exact head SHA, command/results, findings with paths, and residual risk. Round-robin by lane, excluding authors and same-lane sole reviewers. Target one business day; reassign after one day, narrow scope after two cycles. Rebase invalidates old review/test evidence.

RM-approved coherent size exceptions are recorded in `05-merge-plan.md` for PLAN-CHANGE-01 and NEW-01; all exact-head independent review/test and merge gates still apply.
