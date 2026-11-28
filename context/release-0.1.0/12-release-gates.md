# Release gates

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

| Gate | Criteria | Sign-off |
|---|---|---|
| G0 Main green | At exact `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`: 118 tests, Ruff, mypy, wheel/sdist build; current GitHub Python 3.11-3.13 focused matrix green. Evidence and caveat about source-path setup are recorded in `18-current-state-audit.md`. | CI-01 + QA-01 + RM-01 |
| G1 Waves complete | Every in-scope V1 item merged and verified-on-main; no open S1/S2. | INT-01/02, QA, RM-01 |
| G2 Code freeze | Only release fixes/docs; all excluded work labelled v1.1. | RM-01 + owner |
| G3 RC | `v0.1.0-rc.N`; full regression + clean install with base/`[columnar]`/`[mcp]`; zero open in-scope S1/S2/P0; every in-scope feature row Y; #28 owner revision publicly recorded and issue superseded; #4 public Python-only scope addendum posted (excluding deferred npm #25 and TS #14/#15), #29 public focused-PR retarget implemented, #22 renderer-linked scale independently replicated, and scoped #4 release roll-up accepted. Issue #14 remains open but is explicitly deferred with TypeScript/npm to v1.1 and is not in this release gate. | QA lead, TRI-01, CI-01, RM-01 |
| G4 Release | Owner sign-off, release notes merged, `v0.1.0`; remaining branches labeled v1.1 or closed. | Owner + RM-01 + INT-01 |

G0 PASS on current main `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` for the existing ChartSpec baseline only; see `18-current-state-audit.md`. G1-G4 are not passed. The caller explicitly revised #28 for 0.1.0; the public issue remains open until the plan-change merges and the actual issue/count update is posted. The P0 schedule and scope exceptions are in `05-merge-plan.md` and `13-risk-register.md`.
