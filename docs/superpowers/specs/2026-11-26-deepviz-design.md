# DeepViz design

## Intent and authorization
Build a Python-first, schema-driven visualization toolkit for Deep Agents, with npm interoperability, MCP hosting, five renderer alternatives, and verifiable output. The user explicitly authorized autonomous implementation and agent delegation. The builder chooses a private repository because publication visibility was unspecified.

## Architecture decisions (builder defaults)
Use a shared, versioned JSON schema and Pydantic models. Normalize bounded data and stream large inputs; aggregate before transporting data into any renderer. Do not claim to display all ten million independent marks in a browser. Preserve input counts, warnings, aggregation strategy, and sampled count in output metadata. Five renderer alternatives: Matplotlib, Plotly, Vega-Lite, ECharts, and AntV G2. Data processing is Python-first; the TypeScript package consumes the same schema and builds browser artifacts. No arbitrary Python/JavaScript or remote URL execution in model-authored schemas.

## Goals
- Ingest records, columns, nested JSON, GraphQL edges/nodes and page lists, JSONL, CSV/TSV, optional Arrow/Parquet, hierarchy and geographic records.
- Declarative standard charts and composed dashboards, consistent accessible theming, deterministic artifacts, explicit validation failures.
- Measure scales 10, 1K, 100K, 1M, and 10M using a bounded-memory streaming path.
- Real Deep Agent tools, stdio MCP server, versioned prompts, npm and Python distribution builds.
- CI lint/type/unit/integration/visual/build/package gates; evidence-based multi-reviewer and multi-tester PRs.
- Research grounded in public official documentation; clearly distinguish observed public behavior from proprietary inference.

## Boundaries and risks
Rendering optimizations are chart-specific and lossy where stated. Universal acceptance means a documented normalization adapter plus explicit schema mapping, not automatic semantic understanding of every opaque binary encoding. Optional engines may require extras or network-loaded browser dependencies; disclose those requirements. No invented issue resolutions, fake reviews, or unrun benchmarks. Track the requested 900 legitimate completed issues as an unmet criterion until the remote repository proves it.

## Shared interfaces
`ChartSpec`: version `1`, kind in bar/line/scatter/area/pie/heatmap/histogram/box/violin/bubble/radar/treemap/sunburst/funnel/gauge/geo/table/dashboard, title, x/y/color/size fields, data_path, format, aggregation, max_points, width/height, theme, charts, columns.
`normalize(data, spec) -> NormalizedData`: records (bounded list of flattened dictionaries), input_count, warnings, strategy. Streaming reductions should operate before this bounded result is made.
`render(data, spec, engine='matplotlib', output_dir=None) -> Artifact`: filesystem paths, MIME type, engine, input_count, output_count, strategy, warnings. Engines do not receive unbounded raw datasets.
`create_tools(output_dir) -> list[BaseTool]`: five render tools plus normalization/recommendation where useful.
Artifacts must escape untrusted HTML and reject unsafe paths/spec execution. Files must not overwrite unrelated user files.
