# DeepViz architecture and safety decisions

**Design recommendation, 2026-11-26.** This document extends the [approved design](superpowers/specs/2026-11-26-deepviz-design.md); it does not claim implementation of every extension below. [Capabilities](capabilities.md) distinguishes the baseline contract from unverified/advisory features. Public-source evidence and alternatives are in [research](research/README.md).

## 1. Boundary: tools produce artifacts, not proprietary chat widgets

DeepViz is a Python-first normalization/reduction/compiler pipeline with five independent adapter targets: Matplotlib, Plotly, Vega-Lite (`engine="vega"`), ECharts, and AntV G2 v5 (`engine="antv"`). A TypeScript package consumes the same versioned contract. Agent tools and MCP are callers of that pipeline, not separate implementations of its semantics.

An HTML artifact is interactive only when its scripts and browser environment are available. An MCP response containing its path does not automatically embed it inside ChatGPT, Claude, Gemini or OpenCode. Those products have host-specific presentation, permissions and lifecycle behavior. See [documented product boundaries](research/agent-pipelines.md).

## 2. Dataflow and ownership

```text
Caller / Deep Agent / MCP
  -> strict ChartSpec validation + request/resource policy
  -> authorized input adapter -> projected record batches
  -> explicit extraction + type/null validation + bounded profile
  -> deterministic chart/reduction plan
  -> bounded normalized records + provenance
  -> adapter capability check -> trusted compiler -> render worker
  -> artifact validation + manifest -> caller
```

**Python owns** ingestion, field mapping, type policy, aggregation and output-count truth. **Adapters own** only translation of the prepared result into renderer-native structures and output files. **The browser owns** interaction with the bounded result, not invisible access to every original row. **The caller owns** credentials, source authorization and publication decisions.

The existing public interfaces remain the integration boundary:

- `normalize(data, spec) -> NormalizedData`: bounded `records`, `input_count`, `warnings`, `strategy`.
- `render(data, spec, engine, output_dir) -> Artifact`: file paths, MIME type, engine, input/output counts, reduction strategy and warnings.
- `create_tools(output_dir)`: agent-facing operations wrapping the same pipeline.

Do not make every renderer normalize independently. Cache/share a prepared result by its immutable data/spec identity when rendering alternatives; never reread a one-shot generator five times. A dashboard also needs a **total** row/byte/work budget, not just 24 independent child limits.

### Contract evolution, not silent widening

The present model forbids unknown fields. Preserve that property. Proposed internal `DataProfile`, `ReductionPlan`, and richer provenance objects are **design concepts**, not exports asserted to exist. If exposed publicly, version them with schema generation and Python/TypeScript shared fixtures. Reject mismatched major versions; do not drop unknown keys and continue.

Preserve explicit semantic facts in a future manifest: selected field types/units, source fingerprint, count stages, grouping/bin boundaries, domain, ordering, missing/nonfinite treatment, reduction algorithm/version/seed, approximation/error information, renderer/package versions, theme version, external dependencies, and artifact hashes. Never put credentials or raw sensitive samples in that manifest.

## 3. Ingestion without accidental row loss

| Input | Required adapter behavior |
|---|---|
| Records / column arrays | Check equal column lengths, explicit field mapping, primitive types and ragged/missing values. Caller-owned materialized inputs are not retrospectively “streamed.” |
| Nested JSON | Require a unique array path when more than one plausible table exists. Flatten object paths with a defined escaping/collision rule; do not invent a Cartesian join of nested arrays. |
| GraphQL | Extract `nodes` or each `edges[].node`, traverse every supplied page, preserve order and null-node counts. A supplied page list is not evidence that the remote API was fully paginated. No implicit remote fetching. |
| CSV/TSV / JSONL | Iterate chunks/records; bound bytes, fields, nesting and string lengths. A line-size cap is needed even with streaming. Validate before accumulating. |
| Arrow / Parquet | Optional batch scanner, project only needed columns, push safe predicates down where supported; make the extra dependency explicit. |
| Hierarchy / geography | Validate shape, cycles/depth and finite coordinates; require declared mappings and geometry limits. Do not claim all nested JSON is a hierarchy or all coordinate pairs are geographic. |

Record input count **after declared extraction and before chart-row filtering**; distinguish accepted, missing, invalid and reduced counts when the manifest evolves. Preserve missing numeric values as missing, not zero. Reject or deliberately transform NaN/Infinity before strict JSON serialization. Keep timestamps/time zones and numeric-string coercion explicit, and do not guess that an integer identifier is a measure. These are proposed invariant tests, not a statement that every adapter already enforces them.

Arrow's columnar/batch format and DuckDB's Parquet projection/filter pushdown are useful references, not dependencies required for every request. A columnar format cannot by itself cap group cardinality or avoid a full JSON materialization. (Research sources P26–P27.)

## 4. Bounded planning and adapter compilation

`max_points` bounds the **prepared renderer dataset**, not the number of source rows analyzed or every backend's private memory. Also cap serialized bytes, distinct groups, series/facets, hierarchy nodes, raster dimensions, dashboard totals and runtime. Apply projection before object allocation where possible.

Select a chart-specific plan: exact grouped aggregation, fixed-domain bins, time-bucket extrema, deterministic reservoir, or raster density. [Scaling guidance](research/scaling-and-benchmarks.md) explains what each preserves and loses. Overflow must fail clearly, spill to an authorized bounded temporary store, or use a disclosed alternative; silent prefix truncation is not acceptable.

Compile the reduced result so upstream renderers do **not** aggregate it again. For grouped mean, carry sufficient statistics until the final calculation; never average partial means without weights. Preserve bin edges and counts for histograms/density; `output_count` is not the number of source observations represented.

Every adapter should declare supported kinds, required fields, output types, dependency/network needs, interaction features and known semantic differences. A validated chart kind is not proof all engines implement it. For unsupported cases, return an explicit error or a caller-accepted, labeled fallback. Do not silently turn a treemap into bars, a violin into a box, or geographic coordinates into an ordinary scatter.

## 5. Execution-free schemas and isolated rendering

### Trust boundaries

1. **Request/data:** model-authored schemas, cell strings, titles, paths, URLs, filenames and source metadata are untrusted input, including text that looks like instructions.
2. **Compiler:** reviewed application code alone chooses renderer APIs and template functions. Do not execute a schema's Python/JavaScript, formatter string, Vega expression, arbitrary SQL or regular expression.
3. **Runtime:** renderer libraries and browser assets are dependencies with their own supply-chain and resource risks. JSON validation is necessary but is not a sandbox.
4. **Artifact consumer:** opening generated HTML is code execution in a browser context. Publishing data or enabling network access requires an explicit policy.

### Required controls and tests

| Surface | Policy / implementation requirement | Minimum adversarial case |
|---|---|---|
| File access | Resolve against an authorized root; reject traversal/absolute paths where disallowed, symlink/junction escapes and unauthorized outputs. Use random task-owned names and atomic creation, never overwrite unrelated files. | `../`, Windows drive/UNC paths, reserved names, link escape, concurrent same-name request. |
| HTML/JSON | Serialize data, escape script terminators and HTML contexts, use text APIs for labels; never interpolate untrusted values into executable syntax. Protect `__proto__`/constructor keys in JavaScript dictionaries. | `</script><script>…`, U+2028/U+2029, quotes, event attributes, prototype keys, malicious tooltip text. |
| Renderer options | Allowlist trusted structured options; disable supplied callbacks, raw HTML, regex transforms, arbitrary expressions and remote images/data links. | ECharts formatter/regex URL tricks, Vega `data.url`, hostile SVG/image URL. |
| Browser | Isolated render worker with denied network by default, no credentials or host filesystem mounts, bounded CPU/memory/time, kill on timeout. CSP and sandbox flags are defense-in-depth, not the only isolation. | Attempt fetch to loopback/private IP, worker escape from output root, infinite render workload. |
| Assets | Lock exact library versions and hashes; package local assets for offline/private mode. If CDN mode exists, disclose remote loading and fail honestly when blocked. | Offline run, wrong hash, CDN error, unexpected network request. |
| Parsing | Limit compressed/uncompressed bytes, record width/depth, line size, cardinality and geometry complexity. | Compression bomb, single huge JSONL record, deep JSON, millions of unique keys. |
| Tools/MCP | Use trusted output root fixed by server setup; small result envelopes with artifact metadata rather than bulk raw data; preserve errors. No client path authority from a model-supplied filename alone. | Cross-request file read/write attempt, huge response, leaked source secrets. |
| Logging/cache | Redact secrets/PII, opt-in data retention, scoped permissions, deletion policy and access-controlled content hashes/cache keys. | Cross-tenant cache collision and raw-data/error-stack disclosure. |

ECharts explicitly documents risks from untrusted HTML, URLs, JavaScript callbacks and regex filters; Vega exposes its own expression/dataflow surface. A “declarative” label does not remove those boundaries. (Research P13, P17.) Privacy-sensitive recommendation should send only approved profiles/redacted examples to an LLM. The current AVA generator is a reference implementation, not permission to exfiltrate data. (R03.)

## 6. Theme, interaction, and exports

Translate a common trusted token theme to each adapter; do not let one renderer's defaults define the others. Label units and approximations, keep a zero baseline for ordinary magnitude bars, represent missing observations as gaps when appropriate, and include an accessible summary/table. Test both themes and long labels.

Static images, standalone HTML and live server views are distinct artifact types. A screenshot proves visual output, not that a chart is editable or interactive. Retain the validated source spec and prepared data alongside a preview where policy permits. A future viewport-query service must authorize each query, cap work, and invalidate stale requests; it is not part of the initial file-artifact contract.

## 7. Verification and rollout

1. Shared fixtures verify extraction, types, counts and aggregated values in Python and TypeScript.
2. Adapter contract tests verify required native structures and explicit unsupported cases.
3. Browser tests await real renderer completion/fonts, capture console/network errors, exercise tooltips/legend interactions that are actually promised, and inspect output images.
4. Large-input tests generate input incrementally and measure ingestion, reduction, payload, render readiness and process/browser memory separately.
5. Package tests run from installed wheels/npm tarballs in clean environments, with optional dependencies absent as well as present.

The full [measurement design](research/scaling-and-benchmarks.md) separates targets from results. No test, release, screenshot, review, native host embedding or 10M-row guarantee should be reported as verified without its actual evidence artifact.
