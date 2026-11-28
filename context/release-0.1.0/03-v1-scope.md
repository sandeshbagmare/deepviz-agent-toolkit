# Python-only 0.1.0 scope

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

## Definition

**OWNER-CONFIRMED (2026-11-28).** 0.1.0 is a Python-only, source-installable declarative visualization toolkit with strict ChartSpec, bounded data normalization and reductions, optional Arrow/Parquet input through the existing `[columnar]` extra, five Python renderers, recommendation/Deep Agents tools, and local stdio MCP. Package metadata already declares version `0.1.0`. TypeScript/npm, including TypeScript issues #14/#15 and npm package issue #25, is deferred to v1.1. A feature is done only after merge, tests pass on exact main, and non-author QA records end-to-end evidence in file 16.

The proposal follows main README, main design spec `docs/superpowers/specs/2026-11-26-deepviz-design.md`, and open story issues #6-#17. It keeps one coherent Python path; TypeScript #14/#15 and npm package #25 are explicitly deferred to v1.1.

## Scope

| Priority | Capability | Basis |
|---|---|---|
| P0 | Strict ChartSpec and Python/JSON Schema parity | Main model/schema; #33/#38; issues #5/#30 |
| P1 | Deterministic record/column/JSONL/CSV/GraphQL normalization and bounded reductions | Design; feat/ingestion and feat/r34; #6-#8 |
| P1 | Optional Arrow Table/RecordBatch/Reader, IPC and Parquet input via `[columnar]` | Owner decision; existing `pyarrow>=19` extra; #8 |
| P1 | Matplotlib, Plotly, Vega-Lite, ECharts, AntV G2 | Design; feat/renderers; #9-#13 |
| P1 | Recommendation and Deep Agents render tools | feat/integrations; #16 |
| P1 | Local stdio MCP tools and safe artifacts | feat/integrations; #17 |
| P1 | Python wheel/sdist, CLI and resources | Main pyproject; feat/r34/hardening; #24 |
| P0 | No executable specs, bounded output, safe text/paths/cleanup | Design/security branches; #21 |
| P1 | Real artifact inspection and end-to-end acceptance | #23/#26; release criteria |

## Out of scope

- TypeScript/npm/browser artifacts and parity: DEFER to v1.1 by owner decision; TypeScript issues #14/#15 and npm package issue #25 are outside confirmed Python-only 0.1.0. Keep all three issues open for v1.1; main has no npm workspace and the candidate branches remain unmerged.
- Hosted services, package publishing, model-provider dependency, arbitrary code or remote URL ingestion.
- Do not merge historical research/process branches wholesale; publish only the scoped Python-specific release evidence required by #19, #27 and #29. Unsupported performance claims remain out of scope.

## Priority and severity

Priority: P0 blocks its applicable in-scope release gate; P1 required; P2 desired if time; P3 post-release. Severity: S1 crash/data loss/security/main broken; S2 major feature broken with no workaround; S3 broken with workaround; S4 cosmetic/minor. G3 requires zero open in-scope S1/S2/P0; issues explicitly deferred by approved scope, including TypeScript #14, remain open and are tracked for v1.1. A merged fix does not close an issue until verified on main.

## Owner decisions recorded

- Python-only 0.1.0 confirmed; TypeScript/npm issue #15 deferred to v1.1.
- Arrow/Parquet support required through the optional `[columnar]` extra; the base install remains PyArrow-free.
- Release version `0.1.0` confirmed by `pyproject.toml` on current main.
- The caller explicitly revised #28's 900-issue criterion for 0.1.0: "as we dont have that many issues will not keep that as requirement". The 900 count is not a 0.1.0 ship criterion. After the plan-change PR merges, update #28 with the decision and current real issue counts, then close it as superseded for this release; do not fabricate issues or closures.
- #30's strict numeric fix is present on current main. QA-02 independently verified 76 focused tests and model/schema smoke on exact `f692014...`; retain the issue until its post-merge evidence is recorded after the plan amendment.
- See `18-current-state-audit.md` for exact current-main, PR, issue, CI and baseline evidence.

## Public scope and evidence actions after plan merge

- **#4:** RM-01/TRI-01 must publish a scope addendum linking the owner-approved amendment: Python-only 0.1.0 excludes TypeScript #14/#15 and npm package #25, deferred to v1.1. Retain every applicable Python child acceptance, including #19/#20/#21/#22/#23/#24/#26/#27/#29. Keep #4 open until the scoped roll-up and G3 evidence pass; a private plan note alone does not amend its public npm requirement.
- **#29:** RM-01 must publicly retarget the old integrated-PR #31 criteria to the focused replacement PRs, linking their keeper/source mapping. Each focused PR needs two genuine independent reviewer reports and two genuine tester reports with session identity, exact SHA, scope, findings and commands/results. Rendering PRs need actual committed gallery output embedded in the body. Plan diagrams are plan evidence only. Keep reports distinct from GitHub APPROVED states; do not self-approve or change repository rules. Keep #29 open until the retargeted workflow is demonstrated and audited.
- **#27:** Publish scoped epics/stories/tasks with real issue IDs, labels, milestones, dependencies, acceptance and planned/implemented/verified/released states. Commit the issue map, remote issue/milestone/label snapshot and review/test/visual policy under `docs/process/`. Record the historical 900 count as unmet and the explicit 0.1.0 owner waiver; never present waiver as 900 completed issues. Cite primary GitHub secondary-limit and author-approval documentation with actual access dates and claim-to-source review before closure: [REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits), [REST best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api), [approving PRs](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews).
- **#28:** Publish the exact owner revision and current real issue counts after this amendment merges, then close as superseded for this release. Until the public update exists, the issue remains open P0.

These are pending external actions, not claims they have occurred. The amendment itself stays within `context/release-0.1.0/`; Wave 5 publishes the process/research deliverables at their claimed product-documentation paths.
