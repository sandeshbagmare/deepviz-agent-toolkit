# Release gates

- Default branch: `main`
- Main SHA reconciled: `54dd12e2d8d5d69e25426e92c313f0f79e00de81`
- Date: 2026-11-28
- Plan version: 1.1

| Gate | Criteria | Sign-off |
|---|---|---|
| G0 Main green | Exact `54dd12e2d8d5d69e25426e92c313f0f79e00de81`: QA-01 fresh Python3.12.16 source baseline, 118 strict tests/0 skips, Ruff/mypy/build/Twine and 12 schema cases pass; focused Python3.11-3.13 matrix green. Existing ChartSpec/plan-tree baseline only; clean-install and future product gates remain unmet. Local report pointers/limits in `18-current-state-audit.md`. | CI-01 + QA-01 + RM-01 |
| G1 Waves complete | Every in-scope V1 item merged and verified-on-main; no open S1/S2. | INT-01/02, QA, RM-01 |
| G2 Code freeze | Only release fixes/docs; all excluded work labelled v1.1. | RM-01 + owner |
| G3 RC | `v0.1.0-rc.N`; full regression + clean install with base/`[columnar]`/`[mcp]`/`[agents]`; actual StructuredTool API/flow tests in `[agents]` run with zero skips, plus a separate base-only lazy optional-import control; zero open in-scope S1/S2/P0; every in-scope feature row Y; #28 owner revision publicly recorded and issue superseded; #4 public Python-only scope addendum posted (excluding deferred npm #25 and TS #14/#15), #29 public focused-PR retarget implemented, #22 renderer-linked scale independently replicated, and scoped #4 release roll-up accepted. Issues #14/#15 (TypeScript) and #25 (npm package) remain open but are explicitly deferred to v1.1 and are outside this release gate. | QA lead, TRI-01, CI-01, RM-01 |
| G4 Release | Owner sign-off, release notes merged, `v0.1.0`; remaining branches labeled v1.1 or closed. | Owner + RM-01 + INT-01 |

G0 PASS for the existing ChartSpec/source baseline on exact main `54dd12e2d8d5d69e25426e92c313f0f79e00de81` for the existing ChartSpec baseline only; see `18-current-state-audit.md`. G1-G4 are not passed. The caller explicitly revised #28 for 0.1.0; the public issue remains open until the plan-change merges and the actual issue/count update is posted. The P0 schedule and scope exceptions are in `05-merge-plan.md` and `13-risk-register.md`.
