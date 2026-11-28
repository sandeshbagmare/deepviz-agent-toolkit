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

G0 PASS for the existing ChartSpec/source baseline on exact main `54dd12e2d8d5d69e25426e92c313f0f79e00de81` for the existing ChartSpec baseline only; see `18-current-state-audit.md`. G1-G4 are not passed. The caller explicitly revised #28 for 0.1.0; TRI-01 posted #4 scope09:36:12Z, closed #28 not_planned09:38:15Z and retargeted #29 at09:41:56Z; #4/#29 remain open for scoped acceptance, not900 completion. The P0 schedule and scope exceptions are in `05-merge-plan.md` and `13-risk-register.md`.

PLAN-CHANGE-02 must merge before product promotion. User policy is binding: no main-to-feature merge commits, no force-push/history rewrite, and no branch deletion. Preserve published #40-46 branches as preparation/source records. After each prerequisite is merged and verified on main, build a fresh UNPUBLISHED current-main branch by true rebase of a private copy or scoped product selection, with zero feature merge commits; publish it once, open only the necessary replacement PR, and map every retained/excluded path and source/keeper SHA before RM may supersede the old PR. No quota/duplicate tickets or PRs, no old-draft promotion, no dropped tests; all fresh exact-head 2+2/CI/dependency and non-author main-QA gates remain.
