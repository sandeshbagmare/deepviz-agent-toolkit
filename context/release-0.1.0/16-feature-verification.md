# Feature verification on main

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

Every feature starts N. Only non-author QA may set Y after E2E execution on exact merged main and record real commands, outputs and artifacts. Unit tests alone do not count. G3 requires all Y.

| Feature | PR(s) | Test files | Smoke scenario | Verified on main | Verified by | Main SHA/date | Result/notes |
|---|---|---|---|:---:|---|---|---|
| Shared ChartSpec and JSON Schema contract | PR #33, #38 | `tests/test_models.py; tests/test_numeric_schema.py; tests/test_dashboard_schema.py` | Strict types, dashboard rules and schema parity. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Bounded normalization and supported formats | NEW-01, NEW-02 | `python/deepviz/tests/test_normalize.py; test_graphql_contract.py` | Records/columns/CSV/JSONL/GraphQL; check counts, warnings and bounds. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Matplotlib renderer | NEW-03 | `python/deepviz/tests/test_render.py` | Render bar/table; inspect real PNG/SVG and manifest. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Plotly renderer | NEW-03 | `python/deepviz/tests/test_render.py` | Render hostile labels; verify literal text and artifact. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Vega-Lite renderer | NEW-03 | `python/deepviz/tests/test_render.py` | Render and inspect SVG/fallback metadata. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| ECharts renderer | NEW-04 | `python/deepviz/tests/test_render.py` | Render bar/heatmap and inspect output semantics. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| AntV G2 renderer | NEW-04 | `python/deepviz/tests/test_render.py` | Render bar/heatmap and inspect color/domain behavior. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Recommendation and Deep Agents tools | NEW-05 | `python/deepviz/tests/test_integrations.py; examples/multi_tool_flow.py` | Run local normalize->recommend->render without model. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Stdio MCP and CLI | NEW-06 | `python/deepviz/tests/test_integrations.py; tests/test_mcp_transport.py` | Initialize/list/call and retrieve safe artifact. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Python wheel/sdist and entrypoints | NEW-08 | `tests/test_packaging_regressions.py; tests/test_r34_offline_wheel.py` | Clean build/install; verify resources and CLI. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
| Safety and artifact lifecycle | NEW-07, NEW-08 | `tests/test_r17_normalizer_boundaries.py; tests/test_portability.py` | Hostile text, traversal, overwrite, overflow, cleanup, bounds. | N | - | - | Not yet verified on merged main; record output/artifact paths. |
