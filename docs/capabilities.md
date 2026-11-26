# Capability contract and honest limits

**Research/design baseline: 2026-11-26.** This is not a passing test report. This research branch inspected the shared model and approved plan; implementation and CI evidence are owned by the integration work. Treat a capability as verified only when the corresponding tests/artifacts from the final commit prove it.

## What the shared model establishes

The inspected `python/deepviz/src/deepviz/models.py` declares schema version `1`, rejects extra fields, and names five engines: `matplotlib`, `plotly`, `vega`, `echarts`, `antv`. It defines a `ChartSpec`, `NormalizedData`, and `Artifact` metadata envelope. A model accepting a value is **not** proof its renderer or file adapter exists.

| Area | Contract / design intent | Evidence still required before claiming support |
|---|---|---|
| Chart kinds | bar, line, scatter, area, pie, heatmap, histogram, box, violin, bubble, radar, treemap, sunburst, funnel, gauge, geo, table, dashboard. | Per-engine semantic tests and real outputs for each claimed kind; explicit unsupported errors otherwise. |
| Field mappings | `x`, `y`, `color`, `size`, optional `data_path`. | Required-field/type checks, ambiguity/collision behavior and stable nesting semantics. |
| Input formats | `auto`, JSON, JSONL, CSV, TSV, optional Parquet/Arrow in the model. Plan includes records/columns, nested JSON and supplied GraphQL page lists. | Fixture-driven extraction tests, chunked file tests, dependency detection, malformed input cases. |
| Aggregation | `auto`, `none`, `sample`, sum, mean, count, min, max. | Defined per-kind planner and reproducible reductions. `none` over budget must not silently become a prefix sample. |
| Output budget | Default `max_points=2000`, accepted range 10–100,000; dimensions bounded by the model. | Memory and byte budgets across parsing, grouping, serialization and rendering; model row limits alone are insufficient. |
| Composition | Up to 24 child specs, 1–6 columns; nested dashboards rejected by the model. | Native layout output, total dashboard budgets, labeling and no accidental shared-state mutations. Not proof of crossfilter/linked selections. |
| Theme | `light` or `dark`. | Actual adapter mapping, contrast/label visual checks and stable fonts. |
| Provenance | Input/output counts, strategy and warnings in artifact envelope. | Accurate full-stream counts, displayed approximations, stage-count semantics, deterministic sample metadata. |
| Tools and MCP | Approved plan calls for Deep Agent tool wrappers and stdio MCP hosting. | Installed-package discovery/call tests, argument validation and safe output-root behavior. |
| TypeScript/npm | Approved plan calls for shared contract/browser artifacts. | Schema parity, shared fixtures, clean build/pack/install tests and actual browser execution. |

## Renderer alternatives are not universal parity

| Engine identifier | Intended target | Must disclose / verify |
|---|---|---|
| `matplotlib` | Static Python-rendered output baseline. | Real supported kinds, image formats and dependencies. Static output has no browser hover. |
| `plotly` | Plotly figure/HTML path. | Bundled versus CDN assets, actual interactions and any SVG/WebGL/export differences. |
| `vega` | **Vega-Lite** adapter, potentially compiled through Vega. | Exact schema/compiler version, image-export extra, supported compositions and no arbitrary external data URLs. |
| `echarts` | ECharts option/HTML path. | Renderer choice, series-specific capability limits, no unsafe user callbacks/HTML. |
| `antv` | **G2 v5**, not the G2 4.x-based G2Plot wrapper. | Version-pinned G2 assets, supported marks and genuine browser completion. |

This file deliberately does not put checkmarks into a 19×5 grid before tests exist. Renderer support should ultimately be generated from adapter capability declarations and test evidence, not inferred from a union of upstream features. See [the upstream comparison](research/libraries.md).

## What not to promise

- “Any data” means a documented adapter and explicit mapping, not arbitrary binary/document understanding or automatic joins.
- Ten million input rows may be summarized into a bounded result; this is not ten million independent DOM/SVG marks, tooltips or source records in a browser.
- A bounded sample does not preserve exact category totals, rare outliers or density. Label the strategy and its losses.
- Streaming input cannot repair an unbounded group map, full JSON load, sort, materialized caller list, or renderer copy.
- A file path or valid HTML string is not proof the browser executed it. CDN HTML is not offline/self-contained output.
- A dashboard is not automatically a live data app or linked crossfilter. A raster density view is not per-point inspection.
- MCP/agent integration does not create a native inline chart component in another vendor's UI.
- No claim of a 100+ repository audit, proprietary reverse-engineering, production-grade isolation, completed benchmark suite, or feature parity is established by this research dossier.

## Extension backlog, not baseline support

Datashader density reduction; deck.gl geographic layers; uPlot high-rate telemetry; server-backed viewport queries; KLL approximate quantiles; persistent selection state; broader neutral field types/units/domain contracts; adapter capability manifests. Each requires schema/API design, dependencies, safety controls, and measurements before promotion to supported behavior. [Architecture](architecture.md) and [scaling](research/scaling-and-benchmarks.md) specify the proposed boundaries.
