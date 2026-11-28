# Live release tracker

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

Initial state: no plan tasks are claimed and no implementation work has started. Update this file and YAML on each transition; `planned` does not imply a PR exists.

| ID | Wave | Owner | State | Blocked by | Claimed files | Scope / claim / implementation / review / CI / merge / QA | Last update |
|---|---:|---|---|---|---|---|---|
| NEW-01 | 1 | IMP-01 | planned | none | python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_graphql_contract.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-02 | 1 | IMP-02 | planned | NEW-01 | python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_r07_finite_overflow.py, python/deepviz/tests/test_r17_normalizer_boundaries.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-03 | 2 | IMP-03 | planned | NEW-01, NEW-02 | python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-04 | 2 | IMP-04 | planned | NEW-03 | python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py, python/deepviz/tests/test_r20_antv_color_scale.py, python/deepviz/tests/test_r23_count_channel.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-05 | 3 | IMP-05 | planned | NEW-03, NEW-04 | python/deepviz/src/deepviz/recommend.py, python/deepviz/src/deepviz/tools.py, python/deepviz/src/deepviz/__init__.py, python/deepviz/tests/test_integrations.py | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-06 | 3 | IMP-06 | planned | NEW-05 | python/deepviz/src/deepviz/mcp_server.py, python/deepviz/src/deepviz/cli.py, python/deepviz/src/deepviz/tools.py, python/deepviz/tests/test_integrations.py, tests/test_r14_tool_json_boundary.py, tests/test_r41_callback_admission.py, examples/, prompts/v1/ | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-07 | 4 | IMP-07 | planned | NEW-03, NEW-04 | python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_r12_table_budget.py, tests/ | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| NEW-08 | 5 | IMP-08 | planned | NEW-01..NEW-07 | tests/, python/deepviz/tests/, .github/workflows/, README.md, docs/capabilities.md, SECURITY.md | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| PR-31 | before wave 1 | RM-01 | blocked (failed CI; supersede after replacements) | NEW-01..NEW-08 | release/candidate | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |
| ISSUE-28 | release gate | TRI-01 + owner | blocked (P0 scope decision) | G3 | - | [ ] / [ ] / [ ] / [ ] / [ ] / [ ] / [ ] | 2026-11-28 |

At each transition, update the matching checkbox and YAML status together. Enter the PR/issue link, exact SHA and evidence link in the associated PR comment or status note. Check a gate only when its acceptance evidence exists. RM-01 reconciles both boards at every handoff and session resume.
