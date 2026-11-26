# DeepViz research dossier

**Access date: November 26, 2026.** This is a design input, not a claim that every recommendation is implemented or benchmarked.

## Read first

- [Library comparison and design lessons](libraries.md): 14 visualization repositories, with specific source files behind the comparison.
- [Public agent capabilities](agent-pipelines.md): documented features versus deliberately labeled design inference.
- [Scaling and measurement](scaling-and-benchmarks.md): chart-specific reductions, memory accounting, and an executable-test blueprint rather than invented results.
- [OpenCode/OmO coordination](coordination.md): current names, version/configuration boundaries, least-privilege workflow; no global changes.
- [Recommended architecture](../architecture.md) and [capability boundaries](../capabilities.md).
- [Machine-readable source index](source-index.json): exact retrieved URLs and immutable repository revisions.

## Method and honest scope

The indexed evidence comprises **100 distinct source URLs: 58 pinned repository files and 42 official documentation/registry/API pages**. We inspected **15 distinct upstream repositories**: 14 visualization projects and one orchestration project. Each repository has a README, license, and at least one runtime/compiler/schema/source-entry-point file in the index. A source entry point that re-exports modules is not a review of every module it imports. AVA's two branches count as **one** repository. OpenCode is a documentation review, not a source-code repository audit, and does not add to the repository count. These counts describe the selected evidence inventory, not every HTTP request made.

Repository inspection means targeted static reading, not a complete dependency audit, build, penetration test, or upstream benchmark reproduction. Development branch HEADs were resolved and recorded before fetching files; they are evidence snapshots, **not recommended dependency versions**. Bokeh's inspected `branch-4.0` source and its published 3.10.2 documentation, for example, are intentionally distinguishable. Pin released packages and run adapter tests before adoption.

Only first-party vendor docs, official project docs, upstream source files, and publisher package metadata support factual claims. Search snippets, forks, badges, stars, uninspected linked projects, and inherited dependency lists do not inflate the count. A failed G2 source path and a rate-limited Observable hostname were not counted; the working upstream paths are indexed. The DuckDB stable URL served a client-side redirect; the substantive canonical 2.0 page was fetched and indexed instead.

## Evidence labels

- **Documented**: a public vendor/project describes the behavior.
- **Source-observed**: the named public revision contains the implementation described; not a promise about every release or deployment.
- **Recommendation/inference**: our design judgment, not an assertion about a proprietary service's architecture.
- **Unverified**: requires a runtime experiment or implementation test. No unrun benchmark becomes a result.

References such as `R03` and `P18` identify records in `source-index.json`. Repository records list every counted file, including the exact license text inspected. Counts exclude failed fetches, duplicate requests, and metadata-only repositories. This work does **not** substantiate a “100+ repositories reviewed” claim, universal chart parity, 10M independent browser marks, or reverse-engineering of ChatGPT, Claude, or Gemini internals.

## Decisions that materially affect the build

1. Keep the existing five-engine plan: Matplotlib, Plotly, Vega-Lite, ECharts, and **G2 v5**, not G2Plot disguised as G2 v5.
2. Normalize, validate, and reduce once; feed the same bounded semantic result to each adapter. Rendering speed cannot repair incorrect aggregation.
3. Treat AVA's current AI workflow and legacy rule-based Advisor separately. Borrow inspectable recommendation principles, not an unbounded raw-data-to-LLM path.
4. Make provenance, approximation, byte/row budgets, and unsupported capabilities visible. Reserve raster density/viewport-query systems for an explicit extension.
5. Keep chart schemas execution-free. Upstream serializable options can still contain unsafe URLs, HTML, regexes, or expression surfaces.
6. Use native OpenCode delegation already available to the parent session. An optional OmO plugin is not required to claim real coordination, and an installed config string is not proof that its runtime tools executed.
