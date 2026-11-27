<!-- deepviz-r22-ci-45928608970 -->
## Evidence-backed CI triage — audited run, not current-head approval

Agent QA/backlog-manager comment under the R22 assignment. **Keep #20 open.** This is not a human approval, a source fix, or a claim that the current candidate passes.

### Observed failure and source

[Verification run 45928608970, attempt 1](https://github.com/sandeshbagmare/deepviz-agent-toolkit/actions/runs/45928608970) completed **failure** for head `5340bc69b7203ad7a9166543062482d819f9b705`. The checkout was PR merge `aa66ea97c1184554613d14e873e4cc34e54453b0`; official commit/compare GETs confirmed its entire tree equals the head tree (`7aecbc5f4e8a105d296b413d7c70c662ce54794f`, no changed files).

| Python | Unit failures / passes | Unit skip / deselected | Integration |
| --- | --- | --- | --- |
| 3.11 | **38 / 2456** | 1 / 550 | **SKIPPED** |
| 3.12 | **36 / 2458** | 1 / 550 | **SKIPPED** |
| 3.13 | **240 / 2254** | 1 / 550 | **SKIPPED** |

All three first fail step 11, **Unit and contract tests**, with `test_backend_antv.py:201`: expected dashboard payload types `[interval, line, interval]`, actual middle type **`view`**. The native implementation deliberately contains line + point children in that view; the preceding unique-container/manifest assertions passed, but the later child-value assertion was not reached. Unit process exit was **1**. Lint/types/schema/CI-negative-control steps succeeded; eight other jobs succeeded. Neither those successes nor the **51 + 27 evidence-integrity checks** constitute full-product green CI. The unit skip's reason is not established by these logs.

### Seven disposition groups — existing issues, not new tickets

**314 failure instances / 242 distinct node IDs** collapse into the seven groups below. These are triage groups, not seven completed fixes or proven independent root causes. Counts are Python **3.11 / 3.12 / 3.13**.

| Group; counts; existing scope | Owner/dependency and strict minimum acceptance |
| --- | --- |
| AntV view-wrapper oracle; **1/1/1**; #13, #23 | R04 owns the existing-oracle decision/integration; role08's released `_antv` production scope remains exclusive. Validate three unique containers, nested line + point marks and exact independent child values; retain wrong-ID/wrong-value controls. Do not flatten correct marks merely to satisfy an old shape assertion. |
| Deep JSON recursion boundary; **2/0/0**; #16, #17, #21 | Eligible role18 only after its prior checkpoint/eligibility; role10 remains an independent tester. Both 1500-level inline Python JSON and JSON text must reject with actionable `ValueError` (`deep`/`nest`), not leaked `RecursionError`, on 3.11–3.13. Preserve valid Unicode, handles/files, raw-byte, duplicate-key and stdio recovery controls. No global recursion-limit workaround. |
| N17 serialization-order observation; **1/1/1**; #21, #22 | R04 render/budget policy. The old observation expects an invalid wide row to serialize before rejection; actual capture is empty. Establish correct pre-serialization rejection and cleanup with a valid-small-row positive control before changing the oracle. Never widen budgets or remove the early guard to make that observation pass. |
| Vega standalone-child title scope; **10/10/10**; #11, #23 | R04 existing-matrix decision; role17's independent title-scope controls. Pair child specs/records strictly; check each child title in its own compiled output and parent + both child titles in the complete SVG, with real marks. Keep wrong-child, metadata-only, script/event and missing-title negatives. |
| ECharts numeric line/area x oracle; **20/20/20**; #12, #23 | R04 existing-matrix decision; role03's independent controls. Require exact numeric values/types/counts and nonuniform `1,2,10` spacing; retain categorical-bar/string/time controls and browser geometry/console checks. Do not stringify both sides to hide a mismatch. |
| Field-name envelope policy; **4/4/4**; #5, #14, #22 | R04 decides/documents the language-specific policy; role04 independently tests it; normalizer production remains exclusive. The old 64 KiB key positives hit Python's 4 KiB name guard. If that policy is retained, adjust only key-boundary expectations; preserve 64 KiB **cell** limits, multibyte/flattening, early-consumption/state/memory negatives. No blind source-limit widening. |
| Python 3.13 SVG comment-title portability; **0/0/204**; #9, #23 | R04 existing SVG/N09-oracle policy plus independent portable-parser/visual QA. This includes **4 synthetic valid-comment positives failing before mutation**, 14 gallery cases and 186 matrix/text/stream cases. Reproduce portable comment/text extraction on 3.11–3.13, retain title/geometry and missing/altered/script/event negatives, and inspect actual SVG/PNG. No 3.13 skip, manifest-only title acceptance or undiagnosed dependency pin. The underlying CPython mechanism was not locally reproduced by this PM. |

### Acceptance checklist for the manager

- [ ] Disposition each group against its existing issue and current exclusive source owner; preserve original RED evidence and use strict positive/negative controls for any justified oracle/policy correction. Respect the retained allocation/security work and role18 eligibility; do not give production work to tester09/10.
- [ ] On the **actual proposed integrated head**, run all relevant Python 3.11–3.13 unit **and integration** gates, schema/lint/types, applicable npm build/type/test/package and visual/security/streaming checks. An integration step skipped after unit failure is not a pass. Record exact commands, totals/skips, source and new remote run/check URLs.
- [ ] For the planned focused #30 contract slice, name its real contract-only check scope; do not label a filtered slice full-toolkit verification. Require two genuine independent reviewer-agent reports and two tester-agent reports at the actual focused head, output/correctness evidence where applicable, and observed required checks before R04 merges to `main`.
- [ ] Close only the acceptance scope actually proven after the manager verifies merge/default ancestry and evidence. Do not close this broad CI issue on branch existence, partial passes or the old run.

Published evidence: [full disposition](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/37a27cdfbb0d500cc4e2642bb403d68a145fbb21/docs/coordination/reports/R15-19-ci-failure-disposition.md), [exact classified failures and acceptance](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/b9534eab21fa13a37cb8f383b6691596355ef2b1/docs/coordination/evidence/R15-19/classified-failures-and-acceptance.json), [actual publication receipt](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/37a27cdfbb0d500cc4e2642bb403d68a145fbb21/docs/coordination/evidence/R15-19/publication-receipt.json).

**Limits:** this PM did not test later `7bcfb2d` or `6c72cec`, create a focused PR, rerun tests/log downloads, or verify a newer CI result. PR31's draft status is a dated observation, not a fresh PR query. QA12's density bug and QA20's Plotly literal-text bug remain their exclusive filing scopes; this comment creates neither. The 900 genuinely created **and resolved** issue goal remains unmet; test cases are not tickets.
