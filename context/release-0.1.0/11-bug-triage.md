# Bug intake and triage

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

## Issue template

```text
Summary / steps:
Expected / actual:
Exact main SHA:
Environment / optional extras:
Logs and artifact path:
Regression test:
Suspected PR or bisect range:
Severity S1-S4 / priority P0-P3:
Owner / next action:
```

QA reproduces on exact main, files `bug`, `found-on-main`, `wave-N`; TRI-01 deduplicates, assigns S/P and links introducing PR. Use `git bisect` only with deterministic good/bad commits and reproducer.

| Severity | Response |
|---|---|
| S1 crash/data loss/security/main broken | Stop wave; integrator immediately reverts offending PR; triage within 1 hour. |
| S2 major feature broken, no workaround | Reproduce within 4 working hours; fix before next wave. |
| S3 broken with workaround | Triage within one business day; schedule or defer. |
| S4 cosmetic/minor | Triage within two business days; backlog/defer. |

P0 blocks release; P1 required; P2 desirable; P3 post-release. Severity is impact, priority is timing. S1 fix path is `fix/v1/<issue#>-<short-desc>` with regression test. Fix PR follows review/CI/merge workflow; reproduce red before fix, green after, then QA exact main. Triage closes only with main proof.

Current relevant open items: #28 P0 release process; #30 P0 numeric contract (fix #33 merged; issue still open); #32 SVG layout; #35-#37 browser/Plotly/SVG issues. Do not infer a fix from branch name; inspect diff and reproduce.
