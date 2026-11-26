# Delivery process and live issue map

Date: 2026-11-26. Scope: `docs/process/**`. Branch: `docs/process`.

This backlog translates the [design](../superpowers/specs/2026-11-26-deepviz-design.md) and [implementation plan](../superpowers/plans/2026-11-26-deepviz-plan.md) into distinct acceptance-bearing work. It is not a completion claim. The parent coordinator owns PR creation, integration, independent verification and merge decisions; the process agent does not change `main`, close tickets, or create PRs.

## Authoritative records

- [`backlog.json`](backlog.json): stable work keys, scope, acceptance, dependencies, owner lanes, labels and milestones. This is a seed specification, not an executable batch or current completion database.
- [`issues.json`](issues.json): verified remote issue-number mapping captured after seeding; issue states are a dated snapshot, not automatically live.
- [`status.md`](status.md): observed facts, parent-reported evidence, unmet requirements and next gates.
- [`review-and-evidence.md`](review-and-evidence.md): four-report merge gate, closure policy and copyable PR/report templates.
- [`github-constraints.md`](github-constraints.md): primary-source API and approval restrictions; no invented rate-limit event.

Use GitHub issue/PR state for current progress. Update snapshots only after a read-back; do not infer state from this table.

## Initial remote issue map

All 29 seeded issues were remotely read back **OPEN**; **0** were closed by the process agent. Every issue carries a type, area, priority and milestone. Suggested owner lanes are coordination hints, not GitHub assignments or claims that work is complete.

| Issue | Stable key | Scope | Suggested lane |
| --- | --- | --- | --- |
| [#1](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/1) | EPIC-FOUNDATION | Shared contracts and bounded ingestion | Core |
| [#2](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/2) | EPIC-VISUALIZATION | Five renderers and browser SDK | Rendering / TypeScript |
| [#3](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/3) | EPIC-INTEGRATIONS | Deep Agents and MCP | Integrations |
| [#4](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/4) | EPIC-DELIVERY | Evidence, security and release readiness | Parent coordinator |
| [#5](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/5) | CONTRACT | ChartSpec, JSON Schema, metadata contracts | Core |
| [#6](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/6) | INPUT-FORMATS | Records, columns, CSV/TSV, JSONL, optional columnar formats | Core |
| [#7](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/7) | INPUT-GRAPHQL | Nested JSON, edges/nodes, pages, hierarchy and geography | Core |
| [#8](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/8) | STREAMING | Reduction before bounded materialization | Core |
| [#9](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/9) | RENDER-MPL | Real Matplotlib artifacts | Rendering |
| [#10](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/10) | RENDER-PLOTLY | Real Plotly artifacts | Rendering |
| [#11](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/11) | RENDER-VEGA | Real Vega-Lite artifacts | Rendering |
| [#12](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/12) | RENDER-ECHARTS | Real ECharts artifacts | Rendering |
| [#13](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/13) | RENDER-ANTV | Real AntV G2 artifacts | Rendering |
| [#14](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/14) | TS-CONTRACT | TypeScript schema and bounded normalization | TypeScript |
| [#15](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/15) | TS-BROWSER | Browser artifacts and dashboards | TypeScript |
| [#16](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/16) | TOOLS | Five real structured Deep Agents tools | Integrations |
| [#17](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/17) | MCP | Real stdio discovery/call flow | Integrations |
| [#18](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/18) | PROMPTS | Versioned prompts and runnable examples | Integrations |
| [#19](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/19) | RESEARCH | Official-source research and provenance | Research |
| [#20](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/20) | CI | Remote lint/type/test/build checks | Parent / core / TypeScript |
| [#21](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/21) | SECURITY | HTML/spec/path/dependency boundaries | Cross-cutting |
| [#22](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/22) | SCALE | Measured 10, 1K, 100K, 1M, 10M inputs | Core / independent testers |
| [#23](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/23) | VISUAL-QA | Inspected real outputs and committed evidence | Independent testers |
| [#24](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/24) | PY-PACKAGE | Wheel/sdist and clean install | Parent / integrations |
| [#25](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/25) | NPM-PACKAGE | Tarball, exports/types and clean consumer | TypeScript |
| [#26](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/26) | REVIEW-GATE | Two reviewer reports plus two tester reports | Parent coordinator |
| [#27](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/27) | PROCESS | Traceable backlog, tracker and policy | Process |
| [#28](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/28) | BLOCKER-900 | Unmet legitimate 900 created/resolved requirement | Parent / user acceptance |
| [#29](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/29) | BLOCKER-APPROVALS | Distinct-account GitHub approvals if required | Repository owner |

## Milestones and taxonomy

1. **M1 — Contracts and bounded ingestion**: #1, #5–#8.
2. **M2 — Five engines and browser SDK**: #2, #9–#15.
3. **M3 — Agent and MCP interfaces**: #3, #16–#18.
4. **M4 — Release evidence and hardening**: #4, #19–#29.

No unapproved deadline was invented. Labels created: `type:epic`, `type:story`, `type:task`, `type:blocker`; `area:ingestion`, `area:renderers`, `area:typescript`, `area:integrations`, `area:research`, `area:ci`, `area:security`, `area:scale`, `area:qa`, `area:packaging`, `area:process`; `priority:p0`, `priority:p1`, `priority:p2`; `status:blocked`. Existing default labels were preserved.

Epics link their children in issue bodies; children link their parent and predecessors. These are linked issues, **not a claim that native GitHub sub-issue relationships or a Project board were configured**.

## Planning sequence and critical paths

- Freeze and validate #5 before consumers rely on unreviewed interface assumptions. Core #6–#8, renderer #9–#13 and TypeScript #14 can then progress in their own worktrees with shared fixtures.
- #14 precedes TypeScript browser composition #15. #16 enables the real MCP flow #17 and accurate examples #18.
- #8 precedes measured streaming scale #22; #14/#15 precede clean npm consumer #25.
- Security #21 and evidence #23/#26 are cross-cutting acceptance gates, not last-minute substitutes for per-feature tests.
- #28 and #29 remain visible external/acceptance prerequisites. They must not be hidden by closing an epic with unchecked criteria.

Ruling: keep the initial backlog to 29 genuine, coherent scopes rather than explode tests, chart names or input sizes into hundreds of artificial tickets. This preserves traceability but leaves the user's 900-issue numerical criterion unmet. Future issue creation requires distinct, discovered work with its own acceptance and evidence.

## Current parent handoff

Use `Refs #N` while work is incomplete. Use an auto-closing keyword only after all acceptance evidence and the merge gate are satisfied. Multiple issues may share one PR only when each has independently mapped acceptance evidence; a one-line implementation must not close unrelated scopes. Do not close #27 merely because these documents exist; the process PR needs the same parent-supplied verification gate.
