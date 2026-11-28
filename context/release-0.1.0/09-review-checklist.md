# Review checklist

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

Every PR needs two distinct independent reviewer-agent reports and two distinct independent tester-agent reports on the exact PR head, as required by issue #26. Each report records identity/session, scope, exact commit, findings, commands, results and limitations; material findings need fix and retest evidence. Rebase or any new commit invalidates prior reports. Human/code-owner approvals required by repository policy remain separate. Never count an author's own report. Commit screenshots/SVG/PNG and embed their repository paths in every PR body, including plan-only and non-rendering changes; artifacts must depict the actual tested input/output or release-plan state, not a log-only substitute.

Check correctness/acceptance, meaningful tests, bounds/overflow/failure handling, safe HTML/spec/path use, secrets, unrelated edits, API consistency, capability/fallback docs, performance, issue/plan link and size (target <=400, hard cap 1,000 except pure rename). Report exact head SHA, command/results, findings with paths, and residual risk. Round-robin by lane, excluding authors and same-lane sole reviewers. Target one business day; reassign after one day, narrow scope after two cycles. Rebase invalidates old review/test evidence.

RM-approved coherent size exceptions are recorded in `05-merge-plan.md` for PLAN-CHANGE-01, NEW-01, and the NEW-02-only <=1,300-line/seven-path exception; all exact-head independent review/test and merge gates still apply.

Recovered user constraints: User policy is binding: no main-to-feature merge commits, no force-push/history rewrite, and no branch deletion. Preserve published #40-46 branches as preparation/source records. After each prerequisite is merged and verified on main, build a fresh UNPUBLISHED current-main branch by true rebase of a private copy or scoped product selection, with zero feature merge commits; publish it once, open only the necessary replacement PR, and map every retained/excluded path and source/keeper SHA before RM may supersede the old PR. No quota/duplicate tickets or PRs, no old-draft promotion, no dropped tests; all fresh exact-head 2+2/CI/dependency and non-author main-QA gates remain. The plan2-only <=1,200-line/12-context-path exception is distinct from product exceptions; preserve every test and require final actual numstat.
