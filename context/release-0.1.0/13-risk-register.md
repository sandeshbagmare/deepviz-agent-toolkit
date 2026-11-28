# Risk register

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

| Risk | Likelihood | Impact | Evidence | Mitigation | Owner |
|---|---|---|---|---|---|
| Broad candidate introduces failures | High | Critical | #31: 324 paths, +36,025/-3, three Python jobs fail, no reviews | Replace with focused PRs, independent review/CI, rollback | RM-01/INT-01 |
| Conflict cascade | High | High | 65 branches; 1,818 overlapping pairs; 521 conflicts | Fresh main integration, serialized queue, test after each merge | INT-01/02 |
| Branches mistaken for ready | High | Critical | 62 branches have no PR; many tests/evidence only | Diff review, reproduce, exact-head CI, independent approvals | RM-01/REV |
| P0 release blockers | High | Critical | 35 open issues; #28 P0; #30 P0 open after merge | TRI-01 reproduces; owner decides #28 gate; no G3 until closed | TRI-01/owner |
| Rebase invalidates evidence | Medium | High | Divergent refs and overlapping files | Rebase before review; rerun tests/CI; invalidate old approvals | CI-01/INT-02 |
| Python-only proposal conflicts with #15 | Medium | High | Main README Python-first; npm branch 86 paths/+11,681; issue #15 P1 | Owner confirms before Wave1; otherwise DEFER to v1.1 | RM-01/owner |
| Local Python version differs | Medium | Medium | Local run 3.14; CI runs 3.11-3.13 | Use CI matrix and clean-install tests for support range | CI-01 |
| Unsafe artifacts/text regress | Medium | Critical | Security/asset branches contain RED tests; #21 P0 | Keep negative tests, inspect real artifacts, block unsafe output | REV-04/QA |
