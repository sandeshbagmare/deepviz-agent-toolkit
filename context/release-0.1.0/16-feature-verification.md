# Feature verification on main

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

Newly scoped features start N. Only non-author QA may set Y after E2E execution on exact merged main and record real commands, outputs and artifacts. Unit tests alone do not count. G3 requires all in-scope rows Y.

| Feature | PR(s) | Test files | Smoke scenario | Verified on main | Verified by | Main SHA/date | Result/notes |
|---|---|---|---|:---:|---|---|---|
| Shared ChartSpec and JSON Schema contract | PR #33, #38 | `tests/test_models.py; tests/test_numeric_schema.py; tests/test_dashboard_schema.py` | Strict types, dashboard rules and schema parity. | Y | QA-02 | `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7` / 2026-11-28 | 76 focused tests passed; direct runtime-versus-schema smoke covered valid bar, unknown field, numeric strings/booleans, empty dashboard and nested dashboard. Full release readiness remains unverified. |
| Bounded normalization and supported formats | NEW-01, NEW-02 | `python/deepviz/tests/test_normalize.py; test_graphql_contract.py` | Records/columns/CSV/JSONL/GraphQL; check counts, warnings and bounds. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Bounded streaming scale | NEW-02, NEW-03/04, NEW-08 | `python/deepviz/tests/test_normalize.py; scale harness` | W1 normalizer proof; W2/W5 bounded renderer payloads at 10/1K/100K/1M/10M with independent replication and machine-readable environment/timing/memory/counts/strategy/limits. | N | - | - | Issue #22 remains open after W1; no renderer-linked scale or replication result yet. |
| Optional Arrow/Parquet inputs | NEW-01, NEW-02 | `python/deepviz/tests/test_normalize.py; python/deepviz/tests/test_n19_formats.py` | Base install gives actionable optional-extra error; `[columnar]` install reads Table/Batch/Reader, IPC file/stream and Parquet with malformed/duplicate/oversized input controls. | N | - | - | Required for 0.1.0 via optional PyArrow extra; no implementation on current main. CI must install `[columnar]` and report zero skips. |
| Matplotlib renderer | NEW-03 | `python/deepviz/tests/test_render.py` | Render bar/table; inspect real PNG/SVG and manifest. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Plotly renderer | NEW-03 | `python/deepviz/tests/test_render.py` | Render hostile labels; verify literal text and artifact. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Vega-Lite renderer | NEW-03 | `python/deepviz/tests/test_render.py` | Render and inspect SVG/fallback metadata. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| ECharts renderer | NEW-04 | `python/deepviz/tests/test_render.py` | Render bar/heatmap and inspect output semantics. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| AntV G2 renderer | NEW-04 | `python/deepviz/tests/test_render.py` | Render bar/heatmap and inspect color/domain behavior. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Recommendation and Deep Agents tools | NEW-05 | `python/deepviz/tests/test_integrations.py; examples/multi_tool_flow.py` | In installed `.[agents]`, construct/inspect/invoke actual LangChain `StructuredTool` and run normalize->recommend->render with zero skips; separately, a base-only install without LangChain/Deep Agents imports core and confirms optional integrations remain unloaded. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Stdio MCP and CLI | NEW-06 | `python/deepviz/tests/test_integrations.py; tests/test_mcp_transport.py` | With installed `[mcp]`, initialize/list/call and retrieve a safe artifact; exercise the real tool call with installed `[agents]` and no skipped required tests; keep the base-only lazy-import control separate. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Python wheel/sdist and entrypoints | NEW-08 | `tests/test_packaging_regressions.py; tests/test_r34_offline_wheel.py` | Clean build/install; verify resources and CLI. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Safety and artifact lifecycle | NEW-07, NEW-08 | `tests/test_r17_normalizer_boundaries.py; tests/test_portability.py` | Hostile text, traversal, overwrite, overflow, cleanup, bounds. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
