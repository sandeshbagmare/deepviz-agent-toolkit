# Risk register

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

| Risk | Likelihood | Impact | Evidence | Mitigation | Owner |
|---|---|---|---|---|---|
| Broad candidate introduces failures | High | Critical | #31: 324 paths, +36,025/-3, three Python jobs fail, no reviews | Replace with focused PRs, independent review/CI, rollback | RM-01/INT-01 |
| Conflict cascade | High | High | 65 branches; 1,818 overlapping pairs; 521 conflicts | Fresh main integration, serialized queue, test after each merge | INT-01/02 |
| Branches mistaken for ready | High | Critical | 62 branches have no PR; many tests/evidence only | Diff review, reproduce, exact-head CI, independent approvals | RM-01/REV |
| P0 schedule and release gates | High | Critical | Live audit found 11 open P0s. #1/#4 are umbrella epics; #5/#8 are Wave 1; #14 is TS-only and deferred; #20 is Python CI/W5; #21 security/W4; #23 renderer QA/W2; #26 process/per-PR through W5; #28 is explicitly revised by caller but public update is pending; #30 exact-main acceptance is tracked. | Map each P0 to its acceptance wave in `05-merge-plan.md`; no unrelated S1/S2/P0 can pass a wave; #28 blocks G3 until the public update/closure; keep #14 open and outside scope; close umbrella issues only after applicable child evidence. | TRI-01/RM-01 |
| Rebase invalidates evidence | Medium | High | Divergent refs and overlapping files | Rebase before review; rerun tests/CI; invalidate old approvals | CI-01/INT-02 |
| Python-only scope and Arrow support | Medium | High | Owner confirmed Python-only/issue #15 deferred and Arrow/Parquet required through `[columnar]`; current main has metadata only. | Add Arrow/Parquet implementation and non-skipping optional-extra coverage in NEW-01/02; clean install before RC. | RM-01/IMP-01/02 |
| Arrow batch materialization can exceed payload budgets transiently | Medium | High | Source review found `to_pylist()` materializes a full 4096-row batch before per-cell/record byte checks. | Add oversized/nested-value regression; assess row-wise or preflight conversion and document peak-memory limitation. | IMP-02/REV-04 |
| Local Python version differs | Medium | Medium | Local run 3.14; CI runs 3.11-3.13 | Use CI matrix and clean-install tests for support range | CI-01 |
| Unsafe artifacts/text regress | Medium | Critical | Security/asset branches contain RED tests; #21 P0 | Keep negative tests, inspect real artifacts, block unsafe output | REV-04/QA |
