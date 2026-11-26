# @deepviz/agent-toolkit

Validated, bounded visualization artifacts for TypeScript and JavaScript agents.
Version **0.1.0**, ESM + TypeScript declarations, Node.js **22+**, zero runtime
dependencies. Import the public API from `@deepviz/agent-toolkit`.

```sh
npm install @deepviz/agent-toolkit
```

## Quick start

```ts
import { render, type ChartSpecInput } from '@deepviz/agent-toolkit';
import { writeFile } from 'node:fs/promises';

const spec: ChartSpecInput = {
  kind: 'bar', title: 'Revenue', x: 'region', y: 'revenue',
  aggregation: 'sum', max_points: 2000,
};
const artifact = render([
  { region: 'West', revenue: 12 },
  { region: 'East', revenue: 9 },
  { region: 'West', revenue: 5 },
], spec, 'vega');
// The caller controls the destination. `wx` avoids overwriting existing files.
await writeFile('revenue.html', artifact.html, { flag: 'wx' });
console.log(artifact.input_count, artifact.output_count, artifact.strategy); // 3, 2, sum
```

The package performs no filesystem writes, URL ingestion, shell execution, or
arbitrary expression evaluation. `paths` is consequently `[]`; callers may set
their own artifact paths after safely writing `html`.

## Public API

| Export | Behavior |
| --- | --- |
| `validateSpec(input?: unknown): ChartSpec` | Strict runtime validation, fresh defaults, rejects extra keys and invalid dashboards. |
| `normalize(data: unknown, spec?: unknown): NormalizedData` | Normalize and reduce JSON-compatible data or delimited text. |
| `normalizeStream(source: AsyncIterable<unknown> \| Iterable<unknown>, spec?: unknown): Promise<NormalizedData>` | Consume records/pages incrementally without retaining source rows. |
| `buildRendererSpec(data, spec?, engine?): RendererResult` | Return bounded normalized data, resolved ChartSpec, engine-native `spec`, and dashboard `children`. |
| `render(data, spec?, engine?, options?): HtmlArtifact` | Return HTML and metadata; defaults to `vega`. |
| `renderStream(source, spec?, engine?, options?): Promise<HtmlArtifact>` | Single-chart streaming equivalent; streaming dashboards are explicitly rejected. |
| `createTools(options?): RenderTool[]` | Five framework-neutral agent helpers: `render_vega`, `render_echarts`, `render_antv`, `render_plotly`, `render_svg`. |
| `chartSpecSchema`, `defaultAssets` | Canonical structural JSON Schema and pinned default browser asset URLs. |
| `ValidationError`, `chartKinds` | Validation error class and contract chart-kind list. |

Types include `ChartSpec`, `ChartSpecInput`, `NormalizedData`, `DataRecord`,
`Scalar`, `Artifact`, `HtmlArtifact`, `BrowserEngine`, `Engine`, `RenderOptions`,
`RendererResult`, and `RenderTool`. The shared Python `Engine` union includes
`matplotlib`; this JavaScript implementation does **not** run Matplotlib.
`BrowserEngine` is `'vega' | 'echarts' | 'antv' | 'plotly' | 'svg'`.

```ts
import schema from '@deepviz/agent-toolkit/chart-spec.schema.json' with { type: 'json' };
```

The shipped schema is copied from Python's `ChartSpec.model_json_schema()`.
Like that generated schema, it is structural: `validateSpec` also checks that
only dashboards contain children, dashboards are non-empty, and no dashboard
is nested. JavaScript validation intentionally does not coerce strings into
numbers. Model-authored schemas cannot supply code, renderer options, or URLs.

### Contract defaults

`version: 1`, `kind: 'bar'`, `title: 'Visualization'`, `description: ''`,
`x/y/color/size/data_path: null`, `format: 'auto'`, `aggregation: 'auto'`,
`max_points: 2000`, `width: 900`, `height: 520`, `theme: 'light'`, `charts: []`,
`columns: 2`.

Bounds: title 500 Unicode characters, description 2000; `max_points` 10–100000;
width 240–4096, height 200–4096, columns 1–6, dashboard children at most 24.
All sizes/counts are integers. Optional fields accept strings or null.

## Inputs and reductions

Supported directly:

- Record arrays and scalar arrays (scalar values become `{ index, value }`).
- Equal-length column objects, e.g. `{ x: ['a', 'b'], y: [1, 2] }`.
- Nested objects/arrays flattened to dotted field names/indices; colliding keys fail.
- GraphQL `edges[].node`, `nodes`, `data`, `items`, `results`, `records`,
  and `pages`; page arrays are traversed without truncating later pages.
- Explicit dot-separated `data_path`, including traversal across page arrays
  and numeric indices, e.g. `pages.data.users` or `data.rows.1`. Missing branches
  and null GraphQL nodes are skipped with warnings; wholly unmatched paths fail.
  Ambiguous collections require an explicit path; malformed GraphQL edges fail.
- JSON text; explicit `format: 'jsonl'`; CSV/TSV with quoted delimiters,
  escaped quotes, embedded newlines, BOM, and CRLF. Duplicate headers and
  inconsistent column counts are errors. CSV/TSV empty cells become null;
  finite JSON-number syntax becomes a number; other cells remain strings.

`auto` text detection chooses JSON for `[`/`{`, TSV for a tabbed first line,
otherwise CSV. Use explicit `jsonl` for JSON Lines. Arrow/Parquet tokens remain
in the shared contract, but binary ingestion requires an external adapter that
yields ordinary records. Nested record arrays flatten to indexed fields; select
a collection with `data_path` when each nested item should become a row instead.
Dates and class instances must be converted to JSON first.

`aggregation` accepts `auto`, `none`, `sample`, `sum`, `mean`, `count`, `min`, `max`.
Like Python, `auto` infers mappings from at most 32 initial rows and sums a numeric
measure for categorical bar/pie/radar/treemap/sunburst/funnel charts (or
counts rows when no numeric measure exists). Other chart kinds remain unreduced
up to the bound. `none` and `sample` also retain rows up to `max_points`, then use
a deterministic seeded reservoir sample with a warning, preserving source order
in the result. This is not a cross-language promise of identical Python/JavaScript
sample membership. Explicitly set mappings/strategy for heterogeneous streams.
Grouped reductions group on inferred/explicit `x` and optional `color`. `count`
produces `y`, or `count` if y is absent. Other reducers exclude null/non-numeric
measurements; non-numeric and missing mapped values are warned, and an all-null
group yields null. Too many distinct groups keeps the first `max_points - 1`
groups exact and merges every other contribution into a warned final
`__deepviz_other__` bucket (weighted by raw observations for mean). This matches
Python's bounded reduction policy rather than dropping unseen categories.
Heatmaps instead group by both x/y coordinates and sum the numeric `color`
measure; without color, automatic reduction counts rows per cell into `count`.

`NormalizedData` is `{ records, input_count, warnings, strategy }`. Render artifacts
also include `output_count`, `mime_type`, `engine`, `paths`, `html`, and
`renderer_spec`. Sampling and text/non-finite-value changes produce warnings.
Non-finite values normalize to null; chart numeric mappings reject null/missing
measurements rather than turn them into zero. Non-finite reduction results become
null with a warning.

Safety budgets: nesting depth 64; 1024 flattened fields per record/schema; text fields
truncate at 10000 UTF-16 code units; normalized records have a 100000-character
budget, retained normalized data a 16-million-character budget, and HTML a
20-million-character budget. Character budgets are not exact heap-byte limits.
Output rows and retained group states are bounded independently of input count.
JSON strings must still be parsed in memory; true incremental input uses an
async source of records/pages, not raw text chunks.

```ts
import { renderStream } from '@deepviz/agent-toolkit';
async function* rows() {
  for (let i = 0; i < 100_000; i++) yield { time: i, value: Math.sin(i / 100) };
}
const artifact = await renderStream(rows(), {
  kind: 'line', x: 'time', y: 'value', aggregation: 'sample', max_points: 1000,
}, 'svg');
// input_count = 100000, output_count = 1000, strategy = 'sample'
```

## Rendering and dashboards

All engines support bar, line, scatter, area, pie, histogram, bubble and table.
Further support is explicit; unsupported combinations throw:

| Engine | Additional chart kinds |
| --- | --- |
| Vega-Lite (`vega`) | heatmap, box, violin |
| ECharts (`echarts`) | heatmap, radar, treemap, sunburst, funnel, gauge |
| AntV G2 (`antv`) | heatmap, box, radar, treemap |
| Plotly (`plotly`) | heatmap, box, violin, radar, treemap, sunburst, funnel, gauge, geo |
| Native SVG (`svg`) | No extra kinds; dependency-free output |

For heatmaps, x/y identify cells and `color` is the numeric measurement (or the
generated `count` field if omitted). Scatter
and native SVG bubble charts require numeric x/y. Gauges require exactly one
measurement. Hierarchy engines currently render a **single level** with x as
the leaf label and y as its weight; nested hierarchy arrays are not supported.
Plotly geo uses x=longitude and y=latitude, with coordinate graticules but no
external basemap/topology download. Table output is native, escaped HTML.
Vega violin estimates a density of y across the selected data, not per-color
distributions. ECharts scatter/bubble size fields map to per-point numeric marker
sizes (clamped to 4–60 pixels) without executable callbacks. Native SVG color
series share an x domain, have separate polylines, and use a color/dash-cued key.
Long native axes use predictable tick thinning and ellipsis with full values in
SVG titles; narrow containers scroll instead of shrinking text to illegibility.
Native SVG is a small static engine with axes and
an accessible data table, not a substitute for the browser libraries' full APIs.
ECharts duplicate categories are retained unless color grouping makes alignment
ambiguous, in which case explicit aggregation is required.

```ts
const dashboard = render(data, {
  kind: 'dashboard', title: 'Overview', columns: 2,
  charts: [
    { kind: 'bar', title: 'Totals', x: 'region', y: 'revenue', aggregation: 'sum' },
    { kind: 'scatter', title: 'Points', x: 'cost', y: 'revenue' },
  ],
}, 'plotly');
```

Each dashboard child normalizes independently with its own bounds/aggregation;
`data_path` and non-auto `format` fall back to the parent. `output_count` sums
child output rows. `input_count` is the maximum child input count, with a warning
if paths select unequal counts. Strategies are `dashboard` at the parent.

### Browser assets and security

Default HTML uses **pinned CDN assets** (Vega 6.4.0, Vega-Lite 6.5.0,
Vega-Embed 7.4.0, ECharts 6.1.0, G2 5.4.8, Plotly 4.3.0). Opening these HTML
files requires network access. Native SVG/table output needs no external assets.
To work offline, serve the installed dev-dependency bundles yourself:

```ts
render(data, spec, 'vega', { assets: {
  vega: '/assets/vega.min.js',
  vegaLite: '/assets/vega-lite.min.js',
  vegaEmbed: '/assets/vega-embed.min.js',
} });
```

Other asset keys: `echarts`, `antv`, `plotly`. Asset configuration is a **trusted
caller option**, never part of ChartSpec. Only HTTP(S) or explicit relative URLs
are accepted. HTML escapes every title, description, cell, field label, and
script-embedded payload; tooltips are disabled. A per-artifact random CSP nonce
restricts script execution. Vega's trusted compiler requires CSP `unsafe-eval`;
it does **not** permit schema-authored expressions. Renderer specs/data are
deterministic for the same input; HTML nonce bytes intentionally are not.
Keep external libraries trustworthy and serve saved HTML from an isolated origin.
Successful initialization sets `globalThis.deepvizReady = true`; failures are
reported in `globalThis.deepvizErrors` and displayed as text in the chart region.

## Agent helpers

```ts
import { createTools } from '@deepviz/agent-toolkit';
const tools = createTools();
const result = await tools.find(t => t.name === 'render_svg')!.invoke({
  data: [{ x: 'A', y: 2 }], spec: { x: 'x', y: 'y' },
});
```

Helpers expose `{ name, description, inputSchema, invoke }`; `invoke` is async
and validates unknown input. They are framework-neutral, **not** a claim of
native LangChain/MCP registration; adapt these fields to the chosen SDK.

## Development checks

From repository root: `npm ci`, `npm run build`, `npm run typecheck`, `npm test`,
`npm run lint`, `npm run package:check`. Default tests use Node's built-in test
runner and **do not require an installed browser**. `lint` is the strict
TypeScript no-unused/type check, not a separate style linter.

`npm run test:browser` requires Playwright Chromium (`npx playwright install
chromium`), serves local bundles, and tests real renderer output, XSS defenses,
dashboards, and browser errors. `package:check` runs `npm pack --dry-run`, creates
a real tarball, installs it into an isolated temporary consumer, and checks ESM,
JSON Schema exports, runtime behavior, declarations, README and license.

Large-input support means bounded **reduction**, not rendering millions of
independent browser marks. `npm run benchmark:stream` reproduces an async-record
sampling workload. Observed on Windows x64 / Node 26.13.1, production source
commit `363b926`, max_points 2000:

| Input rows | Retained rows | Elapsed ms | Sampled peak heap MiB | Sampled peak RSS MiB |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 10 | 2.32 | 5.01 | 38.54 |
| 1,000 | 1,000 | 10.79 | 5.27 | 40.81 |
| 100,000 | 2,000 | 318.73 | 16.45 | 61.26 |
| 1,000,000 | 2,000 | 3,891.94 | 46.56 | 117.68 |
| 10,000,000 | 2,000 | 18,848.55 | 38.42 | 118.10 |

One process, explicit GC before each scale, `process.memoryUsage()` sampled every
10000 yielded records and at completion. These are **sampled**, not continuous
or isolated-process peaks; RSS includes runtime/prior-scale allocations. No
rendering is included and no source array is materialized. The dev-only raw
record is `benchmarks/2026-11-26-node26-windows.json` in the repository. Timing
depends on hardware, input shape and concurrent load; it is not an SLA or a claim
that the browser renders 10M independent marks.
