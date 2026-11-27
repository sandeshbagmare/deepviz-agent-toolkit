# Capability contract and honest limits

**Implementation inspection: 2026-11-27, source `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.** This is not final-candidate signoff. The matrix below describes actual Python adapter paths at that revision, not the union of upstream library capabilities. Recheck after product changes. [Example execution and claim boundaries](research/implementation-audit.md) separate source inspection, observed runs, and remaining evidence.

## What the shared model establishes

The inspected `python/deepviz/src/deepviz/models.py` declares schema version `1`, rejects extra fields, and names five engines: `matplotlib`, `plotly`, `vega`, `echarts`, `antv`. It defines a `ChartSpec`, `NormalizedData`, and `Artifact` metadata envelope. A model accepting a value is **not** proof its renderer or file adapter exists.

Subsequent source inspection at main `cf27e85` confirms `728bbac` encodes the
existing composition rules in the generated shared schema, not new chart kinds
or runtime behavior. `65b3fc4` uses the same strict input models for MCP discovery
and call validation and cleans only a failed call's fresh artifact subtree.
These are source-observed updates; the example executions below remain on the
explicit baseline, not an independent runtime signoff of those later commits.

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
| Tools and MCP | Five `StructuredTool` renderers, `normalize_data`, `recommend_chart`; same seven stdio MCP operations. | Installed-distribution resource availability, real provider invocation, authorization/resource/adversarial checks. Checkout examples exercise real tools/stdio without an LLM. |
| TypeScript/npm | Separate normalization, stream, browser-spec and in-memory HTML APIs exist in `packages/deepviz/src`. | Schema/default/reduction parity, shared fixtures, clean build/pack/install tests and actual browser execution. Python support is not proof of npm support. |

## Python outputs and asset policy

All render calls also return `manifest.json` with child source records, native specs where applicable, requested/rendered kinds, counts, and warnings. Treat it and the HTML data table as source-derived data, not a redacted summary.

| Engine | Produced files (besides manifest) | Dependency/network behavior |
|---|---|---|
| `matplotlib` | PNG, SVG, companion HTML | Python Agg renderer; local static output, no browser interaction. HTML references sibling SVG. |
| `plotly` | HTML | Embeds installed Plotly JS; no CDN script in this adapter. No static export API exposed here. |
| `vega` | SVG, companion HTML | Vega-Lite v5 schema, compiled locally by required `vl-convert-python`; not a live HTML editor. |
| `echarts` | HTML | SVG renderer, jsDelivr ECharts **5.6.0** script; network required. |
| `antv` | HTML | G2 **5.4.8** script from jsDelivr; network required. Not G2Plot. |

Source: [`render.py`](../python/deepviz/src/deepviz/render.py), [`engines.py`](../python/deepviz/src/deepviz/engines.py). Versions are DeepViz's literal URLs, not claims about the latest upstream releases. A written browser file is not a browser-rendering pass. See [the upstream comparison](research/libraries.md) for upstream features, not DeepViz parity.

## Python kind/layout matrix

**Direct** means a source path emits that layout/mark. It does not certify all field combinations, missing-value treatment, browser completion, or visual parity. All five engines have paths for the 17 non-dashboard model kinds; dashboard composes child paths.

| Requested kinds | Matplotlib | Plotly | Vega-Lite | ECharts | G2 |
|---|---|---|---|---|---|
| bar, line, area, scatter, bubble, pie | Direct | Direct | Direct | Direct | Direct |
| histogram | Pre-binned bars | Pre-binned bars | Pre-binned bars | Pre-binned bars | Pre-binned intervals |
| heatmap | Colored square scatter | **Colored-square scatter surrogate**, fixed 22px markers | Rect marks | Heatmap series | Cell marks |
| box | Box plot | Box trace | Boxplot mark | Boxplot series | Box mark from summaries |
| violin | KDE; exact points for constant/singleton samples | Violin trace | Density-transform area | **Fallback: box** | **Fallback: box** |
| radar | Polar line | Scatterpolar | **Fallback: ordinary line** | Radar series | Polar line |
| treemap | One-level slice-and-dice | Treemap trace, empty parents | One-level slice-and-dice | Treemap series, flat children | One-level slice-and-dice |
| sunburst | One-level annular pie | Sunburst trace, empty parents | **Fallback: pie** | Sunburst series, flat children | One-level annular pie |
| funnel | Centered horizontal bars | Funnel trace | Centered ranged bars | Funnel series, input order | Symmetric transposed intervals |
| gauge | Half-ring, first value | Indicator trace | **Fallback: ordinary bars** | Gauge series | Half-ring intervals |
| geo | Longitude/latitude scatter | Longitude/latitude scatter | Coordinate points | Coordinate scatter | Coordinate points |
| table | Matplotlib table | Table trace | Text marks | Graphic text | Text marks |
| dashboard | Figure subplots | HTML child panels | Vega-Lite concat | HTML child panels | HTML child panels |

### Mapping and approximation caveats

- `_fallback` emits explicit warnings for Vega radar/sunburst/gauge and ECharts/G2 violin. Other custom layouts can retain `rendered_kind == requested_kind`; equality does not mean native hierarchy/geography/heatmap support, or even that a warning is present.
- Hierarchies have **one level**: each x is a child, with no parent/tree reconstruction. Pie/hierarchy/funnel negative weights display as zero with a warning.
- Native/custom gauge layouts use a first-value, fixed-domain representation rather than a configurable multi-gauge subsystem. **Vega gauge is ordinary bars:** the baseline warning incorrectly claims fixed 0-100/clamping/first-value behavior that the fallback compiler does not implement. Do not use that warning as proof of the chart's semantics.
- Python Plotly heatmap is not native heatmap grid geometry: it emits fixed-size colored scatter squares and no fallback warning, despite retaining `rendered_kind="heatmap"`. Native npm Plotly heatmap instead emits a z-matrix. Field-name/kind parity does not establish cell coverage or equivalent geometry.
- Geo is Cartesian longitude=x, latitude=y **without a basemap**, including Plotly. It is not a choropleth or map projection. Heatmap uses x/y coordinates and numeric `color` as measure; upstream features are not automatically exposed.
- Histogram bins and distribution statistics use **bounded normalized rows**, not necessarily every raw observation. Box summaries use min/Q1/median/Q3/max here; backend whisker conventions and KDE behavior differ. Verify reduction/counts before interpretation.
- Bubble size uses adapter-specific scales/units, not guaranteed equal pixel areas across engines. Color is normally categorical except the heatmap measure. Arbitrary continuous scales, callback formatters and raw backend options are not model fields.
- Normalization and visible geometry are separate layers. At this inspected baseline `channels()` converts null/non-numeric y measures to zero **without warnings**; a wholly absent mapped field is a distinct validation error. Do **not** claim missing-as-gap fidelity, equate a zero-height mark with an observed zero, or infer npm rejection parity. This needs renderer QA, not a documentation workaround.
- Line dashes, symbols, legends, themes and HTML data tables exist, but are not an accessibility certification. Long labels, dense tables, small panels, and every color/size combination require visual checks.
- Category ordering is not identical: the executed Vega-Lite bar example sorts nominal month names alphabetically (Feb/Jan/Mar), while the other inspected example outputs retain Jan/Feb/Mar. Values remain mapped to labels, but this is not calendar ordering or a common sort contract. The executed ECharts example also clips the right-end x-axis name; see the dated audit rather than treating console-free rendering as full visual acceptance.

## npm is a separate browser implementation

[`packages/deepviz/src/render.ts`](../packages/deepviz/src/render.ts) exports `render`, `renderStream`, `buildRendererSpec`, `createTools` and `defaultAssets`. `render` returns HTML/native-spec metadata in memory with empty `paths`; it does not write files. `createTools` returns framework-neutral render helpers, not the seven Python `StructuredTool` operations. Browser engine names are `vega`, `echarts`, `antv`, `plotly`, and **`svg`**, not `matplotlib`.

The inspected [`renderers.ts`](../packages/deepviz/src/renderers.ts) allowlist is narrower and rejects unsupported kinds, rather than using Python's fallback matrix:

| npm engine | Source-declared kinds (dashboard composes permitted children) |
|---|---|
| `vega` | bar, line, scatter, area, pie, heatmap, histogram, box, violin, bubble, table |
| `echarts` | bar, line, scatter, area, pie, heatmap, histogram, bubble, radar, treemap, sunburst, funnel, gauge, table |
| `antv` | bar, line, scatter, area, pie, heatmap, histogram, box, bubble, radar, treemap, table |
| `plotly` | All 17 non-dashboard model kinds |
| `svg` | bar, line, scatter, area, pie, bubble, histogram, table |

This is a source allowlist, not per-kind runtime or encoding signoff. Browser renderers also validate required numeric fields differently from Python; do not assume missing-value or reduction parity.

Default npm HTML loads assets from jsDelivr: Vega 6.4.0 / Vega-Lite 6.5.0 / vega-embed 7.4.0, ECharts 6.1.0, G2 5.4.8, Plotly.js 4.3.0. **npm Plotly is CDN-loaded, unlike Python Plotly.** `svg` and table-only output do not require chart scripts. Trusted callers can supply `RenderOptions.assets` local/authorized asset URLs; those options are outside ChartSpec, not model-authored arbitrary remote data sources. The npm Vega CSP permits the library's expression compilation; no model JavaScript/callback field is exposed. Asset/network restrictions and safe publication remain host responsibilities.

npm Plotly geography uses `scattergeo`, not Python's Cartesian scatter. A no-topology-download/offline guarantee is unverified: the CSP's network prohibition does not establish successful geo rendering. Check actual geometry, readiness, requests and errors with the intended asset bundle.

`renderStream` processes one `AsyncIterable`/`Iterable` chart and explicitly rejects streaming dashboards. Materialized JSON/arrays are already resident. These source observations are not clean npm-consumer or browser measurements by this docs lane.

## Reduction and dashboard semantics

Python `auto` sums categorical measures (or counts when no measure exists); other kinds retain/sample bounded rows. `aggregation="none"` **also samples with a warning** over the output limit: it is not strict identity or fail-on-overflow. Sampling is deterministic and preserves source order, not temporal extrema. Group overflow retains the first `max_points - 1` groups and merges remaining contributions into a warned other bucket. Numeric reducers ignore null/non-numeric measures; all-null groups can remain null. See [`normalize.py`](../python/deepviz/src/deepviz/normalize.py), not upstream default reducers.

Dashboard children inherit unspecified parent mappings/reduction/theme settings and each normalize separately. One-shot Python iterators spool to temporary JSONL on disk; replay is not zero-copy and typed scalars may stringify. Returned `input_count` is the **maximum child input count**, not necessarily the top-level source count; `output_count` is the **sum of child normalized row counts**. Per-child metadata is in the manifest. Child row limits do not establish total byte/disk/runtime bounds or crossfilter behavior.

## Tools, resources, and scope limits

`normalize_data` returns a bounded profile/handle, not rows; `recommend_chart` returns an editable spec and `input_count`, not `output_count`. A handle references the original inline source/file, so render re-reads/re-normalizes it. Files may change between calls. Reuse one tool collection/server; handles expire with the process or its 32-entry cache. Default profiling retains at most 200 rows.

Tools allow up to 1,000,000 encoded inline JSON bytes and check each created artifact against 16 MiB. These are not parser/process quotas or total storage caps. File inputs are opt-in under `data_dir`; MCP resource retrieval registers created artifacts only. MCP returns resource links/PNG content, not a generic filesystem API or guaranteed interactive embedding. Filesystem trust, concurrency, disk retention and operating-system limits remain operator responsibilities. See [`tools.py`](../python/deepviz/src/deepviz/tools.py) and [`mcp_server.py`](../python/deepviz/src/deepviz/mcp_server.py).

At this inspected Python source, JSON documents can be read wholesale, scalar strings can retain arbitrary length, and dashboard iterator replay has no demonstrated spool-byte quota. The integration's 16 MiB check happens after file creation. npm's separate character budgets are not evidence of Python UTF-8-byte/state quotas, nor of an all-children dashboard budget. New parent resource-envelope rulings are requirements until actual constants/enforcement and negative controls are integrated and rerun; no pending policy is advertised as an existing guard here.

Duplicate CSV-header rejection does not establish all-depth duplicate JSON-key or Arrow-field rejection. Encoded JSON can overwrite repeated keys at this baseline; reject ambiguity before ingestion until the specific adapter's implemented contract is verified. Planned duplicate-rejection rules are not implementation evidence.

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
