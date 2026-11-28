# Agent topology and assignments

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

## 22-agent roster

| # | ID | Role | Count | Responsibility |
|---:|---|---|---:|---|
| 1 | RM-01 | Release Manager / Orchestrator | 1 | Plan/status, assignments, wave transitions, go/no-go; no feature code. |
| 2 | INT-01..02 | Merge Integrators | 2 | Fresh integration branches, rebases, conflict resolution, sole main merges. |
| 3 | IMP-01..08 | Implementers | 8 | At most one active PR each; implement/fix scoped slices. |
| 4 | REV-01..04 | Reviewers | 4 | Independent review; never review own or sole-review a same-lane change. |
| 5 | QA-01..03 | QA/Test agents | 3 | Per-PR and exact-main E2E, exploratory tests, bug reports. |
| 6 | TRI-01 | Bug triage | 1 | Reproduce, deduplicate, assign S/P, route and verify. |
| 7 | CI-01 | CI/Build guardian | 1 | Main CI, build and flake gates. |
| 8 | DOC-01 | Docs/release notes | 1 | Install/use docs, release notes. |
| 9 | RES-01 | Reserve/surge | 1 | Current bottleneck only. |
| | | **Total** | **22** | |

## Phase allocations

| Phase | RM | INT | IMP | REV | QA | TRI | CI | DOC | RES | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Wave 0 | 1 | 2 | 3 | 2 | 4 | 1 | 2 | 1 | 1 | 17 |
| Feature waves | 1 | 2 | 8 | 4 | 3 | 1 | 1 | 1 | 1 | 22 |
| Stabilization/RC | 1 | 2 | 5 | 2 | 7 | 2 | 1 | 1 | 1 | 22 |

## First assignments

| Agent | First task |
|---|---|
| RM-01 | Confirm scope and own tracker/gates. |
| INT-01 | Build NEW-01 fresh-main integration branch; preserve sources. |
| INT-02 | Preflight current PR conflict set and rebase queue. |
| IMP-01 | NEW-01 input formats. |
| IMP-02 | NEW-02 bounded reductions/GraphQL after NEW-01. |
| IMP-03 | NEW-03 Matplotlib/Plotly/Vega. |
| IMP-04 | NEW-04 ECharts/AntV. |
| IMP-05 | NEW-05 recommendations/tools. |
| IMP-06 | NEW-06 MCP/CLI. |
| IMP-07 | NEW-07 correctness fixes selected by triage. |
| IMP-08 | NEW-08 clean package/install acceptance. |
| REV-01 | Review NEW-01/03 if independent. |
| REV-02 | Review NEW-02/06. |
| REV-03 | Review NEW-04/05. |
| REV-04 | Second security/large-change review. |
| QA-01 | Verify main baseline and exact-main normalization/render merges. |
| QA-02 | Five-engine artifact/safety smoke tests. |
| QA-03 | Deep Agents + MCP exact-main workflow tests. |
| TRI-01 | Triage #30/#32/#35-#37; close only after proof. |
| CI-01 | Preserve matrix, add package/integration jobs after code lands. |
| DOC-01 | Python install/use docs and release notes after behavior stabilizes. |
| RES-01 | Surge only into longest review/test queue. |

All reallocations require RM-01 and a tracker update; idle capacity does not create filler work.
