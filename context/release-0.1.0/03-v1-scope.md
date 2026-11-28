# Proposed 0.1.0 scope

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

## Definition

**PROPOSED - needs owner confirmation.** 0.1.0 is a source-installable Python-first declarative visualization toolkit with strict ChartSpec, bounded data normalization, five Python renderers, recommendation/Deep Agents tools, and local stdio MCP. A feature is done only after merge, tests pass on exact main, and non-author QA records end-to-end evidence in file 16.

The proposal follows main README, main design spec `docs/superpowers/specs/2026-11-26-deepviz-design.md`, and open story issues #6-#17. It keeps one coherent Python path; npm/TypeScript is deferred rather than included without main verification.

## Scope

| Priority | Capability | Basis |
|---|---|---|
| P0 | Strict ChartSpec and Python/JSON Schema parity | Main model/schema; #33/#38; issues #5/#30 |
| P1 | Deterministic record/column/JSONL/CSV/GraphQL normalization and bounded reductions | Design; feat/ingestion and feat/r34; #6-#8 |
| P1 | Matplotlib, Plotly, Vega-Lite, ECharts, AntV G2 | Design; feat/renderers; #9-#13 |
| P1 | Recommendation and Deep Agents render tools | feat/integrations; #16 |
| P1 | Local stdio MCP tools and safe artifacts | feat/integrations; #17 |
| P1 | Python wheel/sdist, CLI and resources | Main pyproject; feat/r34/hardening; #24 |
| P0 | No executable specs, bounded output, safe text/paths/cleanup | Design/security branches; #21 |
| P1 | Real artifact inspection and end-to-end acceptance | #23/#26; release criteria |

## Out of scope

- TypeScript/npm/browser artifacts and parity: DEFER to v1.1 pending owner decision. Main has no npm workspace; `feat/typescript` adds 3,850 lines/18 paths and `feat/r40-npm-foundation` adds 11,681/-1 over 86 paths; no PR/main verification.
- Arrow/Parquet unless its optional extra is verified; #8 remains open.
- Hosted services, package publishing, model-provider dependency, arbitrary code or remote URL ingestion.
- Research/process branches and unsupported performance claims.

## Priority and severity

Priority: P0 blocks release; P1 required; P2 desired if time; P3 post-release. Severity: S1 crash/data loss/security/main broken; S2 major feature broken with no workaround; S3 broken with workaround; S4 cosmetic/minor. Ship rule: zero open S1/S2/P0. A merged fix does not close an issue until verified on main.

## Owner decisions before Wave 1

1. Confirm Python-only scope or move npm/TypeScript issue #15 into v1.
2. #28 is open P0 and states 900 completed issues are unevidenced. Does it remain a release gate- G3 cannot pass while it is open/P0.
3. Is Arrow/Parquet v1 or v1.1-
4. Confirm v0.1.0 tag matches current package version.
5. #30 remains open after #33; authorize closure only after exact-main regression verification.
