# Plan changelog

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

| Version | Date | Change | Reason | Impact |
|---|---|---|---|---|
| v1.0 | 2026-11-28 | Initial plan | Inventory of 65 non-default refs, 3 PRs and 35 open issues; proposed Python-first scope and 22-agent SDLC. | Six waves and eight planned PRs; npm/TS and #28 still pending owner decision in that snapshot. |
| v1.1 | 2026-11-28 | Owner-confirmed Python-only 0.1.0 scope, live-state and P0 schedule reconciliation (plan-change PR pending). | Main `f692014...`, live GitHub audit, and caller response explicitly revising #28: "as we dont have that many issues will not keep that as requirement". | Add Arrow/Parquet test ownership; serialize shared normalizer work; correct source selection; map all live P0s to scoped waves; treat #28 as waived only after its public update; defer TypeScript/npm and #14 to v1.1; specify in-scope G3; correct #38 merge SHA, NEW-01 exclusions, NEW-02 patch order and NEW-08 dependencies/package/doc claims; require public #4 scope addendum and #29 retarget, full #21 negatives and #27 constraints evidence; split #5/#22 closure across renderer waves; authorize isolated parallel preparation while retaining merge and exact-head gates; record RM coherent size exceptions, latest96 NEW-01 selection/minimal exports and NEW-02 regression/scale-only scope; require exact-head reports and committed visual paths on every PR. |

| v1.1 | 2026-11-28 | Review follow-up: explicitly defer npm #25 and require real optional-agent integration verification. | Final plan review found #25 missing from the canonical deferred list and NEW-05 could pass while agent tests were skipped. | Add #25 to the owner-confirmed v1.1 deferrals; require installed `[agents]` StructuredTool/API and real-flow tests with zero skips plus a separate base-only lazy-import control; synchronize NEW-05/06 QA assignments and G3 clean-install evidence. No release gate is weakened. |

| v1.1 | 2026-11-28 | Review follow-up: synchronize refreshed live counts, track published draft PRs, and allow owner-approved future-wave preparation drafts. | Exact-head reviewers found stale current counts and tracker state, open PRs across planned waves, and ambiguous #22 closure wording. | Refresh canonical live counts to 76 refs, 11 PRs (9 open/2 merged), 35 issues and 11 P0; list open drafts #31 and #39-#46 in current_state; explicitly keep future-wave PRs non-ready until dependencies/rebase/checks and exact-head 2+2 pass; block G3 when any required #22 size remains unrun; synchronize NEW-08 installed [agents] acceptance; publicly amend #4 to defer npm #25/TS #14/#15 and waive the unmet historical 900-issue criterion for 0.1.0 with no fabricated counts; distinguish 0.1.0 release scope from v1.1 plan version. The original branch/PR disposition remains labeled historical inventory. |

Append future amendments; do not overwrite history. Require `plan-change` PR, RM-01 approval, and synchronized YAML/Markdown with impact on waves, agents and gates.
