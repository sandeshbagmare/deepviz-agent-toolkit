# Review checklist

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

Every PR needs at least one approving reviewer-agent report; two for P0, security-sensitive or >400-line PRs. Human/code-owner approvals required by repository policy remain separate. Never count an author's own report.

Check correctness/acceptance, meaningful tests, bounds/overflow/failure handling, safe HTML/spec/path use, secrets, unrelated edits, API consistency, capability/fallback docs, performance, issue/plan link and size (target <=400, hard cap 1,000 except pure rename). Report exact head SHA, command/results, findings with paths, and residual risk. Round-robin by lane, excluding authors and same-lane sole reviewers. Target one business day; reassign after one day, narrow scope after two cycles. Rebase invalidates old review/test evidence.
