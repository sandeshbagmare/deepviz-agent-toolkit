# Scaling algorithms and a defensible measurement plan

**Design, not benchmark results — 2026-11-26.** No timings, peak-memory numbers or engine rankings in this document were measured for DeepViz. Numeric budgets below are proposed controls or arithmetic examples. Public references are indexed as R01–R15/P01–P42 in [source-index.json](source-index.json).

## 1. Separate four different sizes

1. **Source:** rows/bytes read and how much of the original dataset was covered.
2. **Working state:** parser batches, dictionaries, sketches, sort/spill buffers and aggregators.
3. **Transport:** serialized prepared rows/bytes, compression, browser decode copies.
4. **Rendered representation:** marks, pixels, layers, labels and interaction state.

Bounding number 4 does not bound 1–3. For example, ten million x/y float64 pairs alone require `10,000,000 × 2 × 8 = 160,000,000` bytes (about **152.6 MiB**), before IDs, masks, object/JSON overhead, copies or GPU buffers. A 1920×1080 RGBA image is about **7.9 MiB**; one uint64 count grid at that resolution is about **15.8 MiB**. A density pipeline needs its own aggregate state, not only the final PNG. These are arithmetic lower-bound examples, not memory measurements.

The model's default 2,000 output rows and 100,000 ceiling should remain an **output** budget. Add maximum bytes, groups/series/facets, raster cells, hierarchy nodes, temporary disk and wall time. Derive a total dashboard budget rather than multiplying the largest individual limit by 24.

## 2. Chart-specific reduction plans

Let `N` be input rows, `B` batch rows, `G` retained groups, `K` sample/output budget, `W×H` raster cells, and `S` series. Time/space bounds below describe the proposed reduction algorithm, not every parser/backend allocation.

| Workload | Proposed strategy | Complexity / precondition | Truth and losses to disclose |
|---|---|---|---|
| Category totals/counts | Exact hash aggregation; stable sort after aggregation. Cap `G`, or partition/spill explicitly. | O(N) expected aggregation, O(G log G) ordering; state O(G+B). High-cardinality keys defeat an uncapped map. | Exact per-group count/sum for valid rows; report excluded/null rows and any top-k/other combination. |
| Group means/variance | Maintain count + sum and, if needed, stable online variance state; merge sufficient statistics. | O(N), O(G+B); numeric range/overflow still need checks. | Never average chunk means without weights. Numeric precision and missing-value policy are explicit. |
| Top-k categories | Aggregate exactly first if bounded/spillable; choose top-k and an exact residual. Approximate heavy-hitter path is a separately named algorithm. | Exact state O(G), final selection O(G log K); no claim of constant memory for arbitrary exact categories. | Count-based sketches do not automatically support arbitrary negative weighted sums; approximate candidates need a second pass for exact totals. |
| Time-series overview | Declared time buckets; retain first/last and local min/max per bucket/series, ordered by timestamp. | O(N), O(W×S+B) with known domain and ordered input. Unsorted input needs bounded external sorting or a different plan. | Preserves selected extrema/endpoints, not every oscillation/integral. Preserve gaps, duplicate-time policy and series boundaries. |
| Line detail | Optional LTTB-like shape selection **after a bounded time envelope**, if implemented and tested. | Not advertised as a universal one-pass or extrema-preserving algorithm. | Shape selection can miss narrow events. Never use for exact sums, histograms or quantiles. |
| Scatter overview | Seeded uniform reservoir for a point view, or exact fixed-domain 2D bin counts for a density view. | Reservoir O(N), O(K+B); grid O(N+W×H), O(W×H+B). | Sample is not density and may miss rare outliers. Density preserves counts per bin, not source identity or per-point tooltips. |
| Histogram | Fixed declared edges/domain; count every valid row. Quantile/FD-derived edges require a profiling/sketch pass then replay/spool. | O(N) for fixed bins; state O(number of bins+B). | Boundaries, inclusion rule and overflow bins are part of semantics. A histogram over a sample is labeled approximate. |
| Box/quantiles | Exact external selection/sort where affordable; otherwise per-group KLL sketch with named parameters. | Sketch storage depends on precision and G; cap both. | Report approximate rank error/parameters, not an unsupported error bound in data units. Outlier points require a separate plan. |
| Violin | Bounded histogram/density evaluation with declared bandwidth and optional quantile summaries. | State O(bins×G+B); unrestricted KDE or raw-per-group storage is not bounded by a row cap. | Density shape depends on bandwidth/grid; do not call a box plot a violin. |
| Hierarchy | Aggregate declared paths to finite weights, bound depth/node count and validate cycles. | O(N×depth), O(retained nodes+B). | Preserve parent/child totals; pruning needs an explicit other node, not discarded mass. |
| Geographic overview | Projection-aware bins/tiles or a bounded sample; optionally GPU layers for detail. | Budget tile count, geometry vertices, attributes and layers. | Degree-space bins are not equal-area; density units/projection must be visible. Tiles/base maps can create network/licensing obligations. |

If a streaming domain is unknown, an exact pixel/bin plan generally needs **two passes** or an authorized spool: first establish bounds/edges, then aggregate. Updating the domain while keeping old pixel counts without correct rebucketing misrepresents the data. For a non-replayable stream, require a fixed domain, use a disclosed approximation, or stop with an actionable error.

### Why these library references matter

- **Datashader** explicitly separates projection/aggregation/shading and describes incremental reductions. It is a good reference for all-row density output, not proof all input formats or category counts fit memory. (R12, P21.)
- **Plotly** documents typed-array/WebGL paths and their limits; its million-point examples are not a 10M-row SLA for DeepViz. Raster aggregation is an alternate representation, not invisible simplification of the same point plot. (R07, P18.)
- **deck.gl** highlights binary attributes, update costs and overdraw/picking overhead. A fast GPU does not remove CPU object creation, upload or device limits. (R10, P20.)
- **Altair/VegaFusion** can precompute supported operations, but interactive selections may require transmitting data or using a server-capable runtime. Disabling Altair's 5,000-row guard does not optimize anything. (R14, P23.)
- **KLL** provides a compact mergeable quantile-sketch design with documented rank-accuracy tradeoffs; adopt a maintained implementation rather than invent a homegrown error guarantee. (P28.)
- **Arrow/Parquet pushdown** reduces needless decoding/projection; neither bounds distinct-group cardinality. (P26–P27.)

## 3. Minimal provenance sufficient to reproduce a reduction

Proposed manifest extension (not an existing API assertion): source/extracted/accepted/rejected row counts; selected fields and numeric/time coercion; source fingerprint; grouping/bin boundaries/domain; output rows; strategy + algorithm version; sample seed; approximation/precision parameters; byte budget; overflow/spill decisions; relevant renderer versions.

Record `strategy="reservoir"` only for a real reservoir, not `rows[:K]`. Record a count grid as aggregation, not sampling. For line envelopes, retain event ordering among extrema in each bucket. Cross-engine tests compare identical prepared values and strategy metadata before rendering. Seed alone is insufficient if input ordering/version changes.

## 4. Dataset and workload matrix

Use row scales **10, 1K, 100K, 1M, 10M**. Fixtures must be generated incrementally into local files outside the timed render stage, with reproducible seed, schema, byte count and checksum. Include both numeric-width and string-width stress; a ten-million-row two-column fixture is not representative of a wide nested record.

| Family | Shape / adversarial dimension | Correctness oracle |
|---|---|---|
| Bars | Low G, G≈N, skewed categories, negative weights, long labels. | Independent exact totals and residual mass; deterministic ordering. |
| Lines | Sorted/unsorted timestamps, duplicates, gaps, narrow spikes, many S. | Retained endpoints/extrema/gaps; sample-order and series-boundary invariants. |
| Scatter/density | Uniform, clustered, correlated, extreme outliers and overplotting. | Grid-count conservation and known bin membership; reservoir bounds/repeatability plus multi-seed distribution tests. |
| Distribution | Heavy tails, multimodality, all equal, NaN/Infinity/nulls. | Exact small-fixture quantiles/bins, approximate-rank checks with declared confidence policy. |
| Structures | GraphQL page arrays with null nodes; ragged columns; nested arrays; path-name collisions. | All supplied pages covered, expected row IDs and precise rejection/warning behavior. |
| Security | Script terminators, prototype keys, huge field values, path escapes, deep JSON. | No unexpected execution/network/file access; bounded failure and useful errors. |
| Dashboard | Many children, long legends and mixed renderers/themes. | Total budget and layout; no per-child repeat consumption of a one-shot stream. |

Test one-shot generators that raise if iterated twice, and sources that reveal all row IDs only at the end. `input_count=N` is insufficient if code counted the file but plotted an undisclosed prefix. For density/histograms, assert sum of represented weights equals accepted input count (or known weighted total) subject to explicitly reported exclusions.

## 5. Measurement harness design

### Isolate phases

Use monotonic timestamps for: admission/spec validation; input read/decode; extraction/profile; reduction/sort/spill; spec compilation; serialization; browser launch; renderer-ready; export; artifact verification. Report total end-to-end latency as well as phase durations, and identify overlapping intervals rather than summing them twice. Measure fixture generation separately. Record cold and warm dependency/JIT/browser cache conditions explicitly.

For HTML, readiness is a real engine-specific completion event/promise plus settled fonts and disabled/finished animation, not “file exists” or an arbitrary sleep. Capture browser console, failed requests and unexpected network calls. For static output, verify parseability, nonempty content and semantic labels, not only a PNG signature. A screenshot check includes axes, legends, text clipping and missing plots.

### Measure memory honestly

- Run each scale/strategy/engine case in a fresh process; sample parent and child render processes and report the **simultaneous** aggregate RSS peak. Summing each process's independent maximum is not the same metric.
- On Windows, process RSS includes shared pages and aggregate RSS can double-count them; label it, record OS and sampling interval, and use an OS-enforced job/container limit separately. Do not call aggregate RSS unique physical memory.
- `tracemalloc` is useful for Python allocations but excludes much native NumPy/Arrow/renderer memory. Record it only as a supplementary metric. Include temporary disk high-water and artifact/payload bytes.
- Report browser-process RSS/heap separately. JavaScript heap metrics alone exclude important browser/GPU memory. GPU allocations should be measured only through a reliable platform-specific method or labeled estimated/unavailable.
- Include sampling interval and any OS high-water counter; a sampled peak can miss short spikes. Compare allocation profiles at equal input/data budgets, not just “engine A looked smaller.”

### Repetitions and environment

For smoke checks use a small explicitly labeled run count. For publishable latency distributions, propose three untimed warm-ups and **at least 30 measured repetitions** per selected case; report median, p95, min/max, errors/timeouts and raw samples. A single 10M run is a scale smoke test, not a p95 estimate. Randomize engine order and keep concurrency controlled. Cache/cold-start experiments are separate series.

Record commit, schema, exact package/browser versions, CPU/RAM/GPU/driver, OS/power mode, thread count, dataset checksum/format/bytes, budget/reducer/seed, viewport/device pixel ratio, output type and whether dependencies were local or CDN-loaded. Distinguish optional packages missing, unsupported kinds, timeouts and actual failures; never average missing/failed cases as zero latency.

### Result record proposal

```json
{
  "status": "ok|unsupported|missing_dependency|timeout|failed",
  "dataset": {"rows": 1000000, "bytes": 0, "checksum": "record-real-value"},
  "spec_hash": "record-real-value",
  "engine": "vega",
  "strategy": "record-actual-strategy",
  "input_count": 1000000,
  "output_count": 0,
  "timing_ms": {"total": null, "reduce": null, "renderer_ready": null},
  "memory_bytes": {"aggregate_rss_sampled_peak": null, "browser_rss_peak": null},
  "payload_bytes": null,
  "warnings": [],
  "artifact_paths": []
}
```

This is a **record-format illustration**, with placeholders/nulls, not a stored benchmark result. Do not publish it as evidence. Prefer machine-readable raw run records plus a summary derived mechanically from them.

## 6. Promotion gates

1. Small-fixture semantic equivalence and security tests pass before performance comparisons.
2. Streaming memory grows with batch/group/output budgets rather than N for workloads that claim bounded state; demonstrate with actual RSS curves and a high-cardinality failure/spill test.
3. Every claimed engine produces real inspected output and accurately reports any approximation/dependency requirement.
4. Latency/memory targets are agreed on known hardware **after baseline measurement**. No arbitrary “sub-second 10M” promise or upstream marketing number is a substitute.
5. Keep an honest results ledger: unrun, unsupported and failed remain visible. Screenshots, test logs and raw measurements are attached to the exact commit that produced them.
