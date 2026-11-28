# PR creation and consolidation plan

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

## Existing PR actions

| PR | Disposition | Planned action |
|---:|---|---|
| #33 | V1-MERGE | Already merged; leave unchanged. |
| #38 | V1-MERGE | Already merged; leave unchanged. |
| #31 | CLOSE-SUPERSEDED (conditional) | Keep the draft untouched until selected code is preserved in granular PRs; after NEW-01..NEW-08 land, close it with links. Do not rebase/merge its 324-path diff. |

## New PRs

### NEW-01 - [v1][W1][feature] add bounded Python input normalization

- Action: create fresh branch `release/v1/w1-python-normalization` from latest main; apply only listed files/hunks. Source branches: feat/ingestion, feat/r34-python-data-foundation, test/graphql-contract, agents/r10-04-utf8-field-envelope.
- Ordered cherry-pick source SHAs: `a711ea5c9f4b97d53a80e1cac86c42e25c9d4dbc`, `9ce04fcc0e91c1896979e3efb9740294dae38240`, `9531dab2b4d629c6fffdff9b7dc7dfcebb3def03`, `355637ca3de44afb69b7ee0c80999affaf0816bd`, `6c412e0f6be7e96a24a7f6c5cbcfdba9a48ef2c5`, `429890b45bb1e85087507e07b95dcd382aa53ab4`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-1`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-01 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issues #6, #7, #8; plan item NEW-01.
## Source branches consolidated
feat/ingestion, feat/r34-python-data-foundation, test/graphql-contract, agents/r10-04-utf8-field-envelope
## Depends on (PRs that must merge first)
none
## Files touched
python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_graphql_contract.py
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Ingestion and R34 share normalize.py; use reviewed R34 base and only unique format/GraphQL hunks. Rollback: Revert squash, rerun main suite, stop wave.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-02 - [v1][W1][feature] add bounded streaming reducers

- Action: create fresh branch `release/v1/w1-python-reductions` from latest main; apply only listed files/hunks. Source branches: feat/ingestion, feat/r34-python-data-foundation, fix/r17-normalizer-boundaries, agents/r10-16-finite-overflow-fix, agents/r45-04-private-numeric-accounting.
- Ordered cherry-pick source SHAs: `6c412e0f6be7e96a24a7f6c5cbcfdba9a48ef2c5`, `5ba860305dcc86ac2f95f01705b984d2b40f2799`, `ec9f669eff28cd5351da142765b7755e3b2f484f`, `c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19`, `a7363be273d7b3bbcb1b52ef79a58bb4e6d0e3be`, `7ab546251029df169604358448ecd462d8db5e6f`, `546c25ea75ee9d8a41b3832aa639664bc9a683b5`, `96b819aee5b01ba88b5a609b587331a528aaa070`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-1`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-02 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issues #6, #8, #22; plan item NEW-02.
## Source branches consolidated
feat/ingestion, feat/r34-python-data-foundation, fix/r17-normalizer-boundaries, agents/r10-16-finite-overflow-fix, agents/r45-04-private-numeric-accounting
## Depends on (PRs that must merge first)
NEW-01
## Files touched
python/deepviz/src/deepviz/normalize.py, python/deepviz/tests/test_normalize.py, python/deepviz/tests/test_r07_finite_overflow.py, python/deepviz/tests/test_r17_normalizer_boundaries.py
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Shared normalize.py; apply Python-only fixes after NEW-01 and rebase/test. Rollback: Revert this squash only; keep NEW-01.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-03 - [v1][W2][feature] add Python Matplotlib, Plotly, and Vega renderers

- Action: create fresh branch `release/v1/w2-python-renderers-a` from latest main; apply only listed files/hunks. Source branches: feat/renderers, test/backend-plotly, test/backend-vega.
- Ordered cherry-pick source SHAs: `31acb2f6e58bc83f71c1736af9d4be37c56ad59c`, `420a956788c9b78529d3348650a32913090f5671`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-2`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-03 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issues #9, #10, #11; plan item NEW-03.
## Source branches consolidated
feat/renderers, test/backend-plotly, test/backend-vega
## Depends on (PRs that must merge first)
NEW-01, NEW-02
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Source commit 31acb2f6 adds five backends in 1,184 lines; stage only these three and their tests; NEW-04 follows. Rollback: Revert squash; normalized main remains.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-04 - [v1][W2][feature] add Python ECharts and AntV G2 renderers

- Action: create fresh branch `release/v1/w2-python-renderers-b` from latest main; apply only listed files/hunks. Source branches: feat/renderers, fix/r20-antv-color-scale, fix/r23-count-channel, fix/r45-17-antv-subnormal, agents/r10-03-echarts-numeric-x, agents/r38-18-antv-source-review, review/r35-12-count-source.
- Ordered cherry-pick source SHAs: `31acb2f6e58bc83f71c1736af9d4be37c56ad59c`, `420a956788c9b78529d3348650a32913090f5671`, `3185e0d9936c7d6f1a9d30b94089b804d75fe991`, `4429f0521612b97eee3790f0d8d0fbc3cad3f8be`, `85796dbe3360fb88686f2e7188122e2da80d54c2`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-2`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-04 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issues #12, #13; plan item NEW-04.
## Source branches consolidated
feat/renderers, fix/r20-antv-color-scale, fix/r23-count-channel, fix/r45-17-antv-subnormal, agents/r10-03-echarts-numeric-x, agents/r38-18-antv-source-review, review/r35-12-count-source
## Depends on (PRs that must merge first)
NEW-03
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_render.py, python/deepviz/tests/test_r20_antv_color_scale.py, python/deepviz/tests/test_r23_count_channel.py
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Shares renderer paths; rebase after NEW-03; select independent count/AntV hunks once. Rollback: Revert squash; rerun renderer tests.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-05 - [v1][W3][feature] add recommendations and Deep Agents tools

- Action: create fresh branch `release/v1/w3-python-tools` from latest main; apply only listed files/hunks. Source branches: feat/integrations.
- Ordered cherry-pick source SHAs: `6731720cfc4c7b0a729c4958a7d2e2f4fe614107`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-3`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-05 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issue #16; plan item NEW-05.
## Source branches consolidated
feat/integrations
## Depends on (PRs that must merge first)
NEW-03, NEW-04
## Files touched
python/deepviz/src/deepviz/recommend.py, python/deepviz/src/deepviz/tools.py, python/deepviz/src/deepviz/__init__.py, python/deepviz/tests/test_integrations.py
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
1,341-line integration source; stage recommendation/tool API before MCP. Rollback: Revert squash; preserve renderer APIs.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-06 - [v1][W3][feature] add safe stdio MCP server and CLI

- Action: create fresh branch `release/v1/w3-python-mcp-cli` from latest main; apply only listed files/hunks. Source branches: feat/integrations, fix/r14-mcp-json-budget, fix/r41-callback-admission, agents/r10-10-stdio-artifact-lifecycle, agents/r11-10-strict-mcp-boundaries.
- Ordered cherry-pick source SHAs: `6731720cfc4c7b0a729c4958a7d2e2f4fe614107`, `d65dfc0fd807d0335b858476de8cdf7c6b958711`, `cd75c459ddba9f3d6bc0a5185b570af369fb4980`, `f48c72e26000560b48f3dfd137696fa9acf17637`, `91d62f4218302b3f3659a01611e76234398cdc98`, `6cba2d49eb4de82d5df64f790803e23c08f07b9d`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-3`, `type:feature`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-06 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issues #17, #21; plan item NEW-06.
## Source branches consolidated
feat/integrations, fix/r14-mcp-json-budget, fix/r41-callback-admission, agents/r10-10-stdio-artifact-lifecycle, agents/r11-10-strict-mcp-boundaries
## Depends on (PRs that must merge first)
NEW-05
## Files touched
python/deepviz/src/deepviz/mcp_server.py, python/deepviz/src/deepviz/cli.py, python/deepviz/src/deepviz/tools.py, python/deepviz/tests/test_integrations.py, python/deepviz/tests/test_r14_tool_json_boundary.py, python/deepviz/tests/test_r41_callback_admission.py, examples/, prompts/v1/
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Shares package API/entrypoints; select Python MCP-only paths and fix callback order/capacity. Rollback: Revert squash; retain tools; stop MCP wave.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-07 - [v1][W4][fix] harden Python render bounds and security

- Action: create fresh branch `release/v1/w4-python-hardening` from latest main; apply only listed files/hunks. Source branches: feat/hardening, fix/r12-dense-table-budget, agents/r10-01-correctness-regressions, agents/r10-02-security-boundaries.
- Ordered cherry-pick source SHAs: `d5b68c470416f93127c8187e8111d0d27d20b108`, `2b2709ec6846ad8e136641257e04b4ae48eded08`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-4`, `type:fix`, `P0`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-07 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issues #21, #23; plan item NEW-07.
## Source branches consolidated
feat/hardening, fix/r12-dense-table-budget, agents/r10-01-correctness-regressions, agents/r10-02-security-boundaries
## Depends on (PRs that must merge first)
NEW-03, NEW-04
## Files touched
python/deepviz/src/deepviz/engines.py, python/deepviz/src/deepviz/render.py, python/deepviz/tests/test_r12_table_budget.py, tests/
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Renderer paths were changed in earlier waves; rebase on their merged SHAs. Import only Python hardening/test hunks. Rollback: Revert squash; stop release if safety gate fails.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

### NEW-08 - [v1][W5][test] complete Python release acceptance and docs

- Action: create fresh branch `release/v1/w5-python-acceptance` from latest main; apply only listed files/hunks. Source branches: test/acceptance, test/aggregation-semantics, test/backend-antv, test/mcp-transport, test/portability, perf/verification, agents/r10-07-python-clean-distribution, agents/r10-11-python-scale-envelope, agents/r10-13-ci-negative-controls, agents/r10-14-assets-offline-provenance, agents/r10-15-owned-input-cleanup.
- Ordered cherry-pick source SHAs: `12e7b6109e7fa6eebabf9a20912fcaf06f56f5a7`, `e6a8a8c2126dc90f10de8a3b0b16a9eaad829478`, `5f7ab4cf0e3e43075e781a20344c40c57d6fc7f7`, `c799dc5e3a9ffbdd522cab96419c466f86e04401`, `f1e71035b1818bd280037efaa1394adf500139fb`, `146f0276323918307b642bc86d1414dbb3b686d9`, `06c04900466f66d7919b68a5c3626d94df248ea6`, `2b4f0a8a2de7540a53d8399c2b87bbdd19b137e6`, `ccb0bf0856cde5c6a866b9418a7b6fca66f2c7cf`, `dedb41fa8df3fdb90b845eef7a10b5fa4032872c`, `9bcf27dd0888778a6826fbd1f3203bc4652cec40`. Apply mixed commits with `--no-commit`, stage only named hunks, and record paths. Never merge main into source branches.
- Labels: `v1`, `wave-5`, `type:test`, `P1`, `planned`; update lifecycle state label. Rebase before review and rerun checks.
- Merge: squash.
- Filled PR body:

```markdown
## What
Implement the focused change described by NEW-08 in `05-merge-plan.md`.
## Why (links: issue #, plan item)
Required by proposed Python 0.1.0 scope; issues #23, #24, #26; plan item NEW-08.
## Source branches consolidated
test/acceptance, test/aggregation-semantics, test/backend-antv, test/mcp-transport, test/portability, perf/verification, agents/r10-07-python-clean-distribution, agents/r10-11-python-scale-envelope, agents/r10-13-ci-negative-controls, agents/r10-14-assets-offline-provenance, agents/r10-15-owned-input-cleanup
## Depends on (PRs that must merge first)
NEW-01..NEW-08
## Files touched
tests/, python/deepviz/tests/, .github/workflows/, README.md, docs/capabilities.md, SECURITY.md
## How tested (commands + results)
Record exact commands and actual output after running; no pass may be claimed before execution.
## Risk & rollback
Consolidate acceptance after code; omit duplicate/RED tests until fixed; exclude agent-state/evidence dumps. Rollback: Revert acceptance/doc commit only; stop release and repair CI.
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```


## Reusable PR body template (verbatim)

```markdown
## What
## Why (links: issue #, plan item)
## Source branches consolidated
## Depends on (PRs that must merge first)
## Files touched
## How tested (commands + results)
## Risk & rollback
## Checklist
- [ ] Rebased on latest main
- [ ] CI green
- [ ] Tests added/updated
- [ ] No unrelated changes
- [ ] Docs updated if behaviour changed
```

Do not close source branches during this planning run. Close only after the replacement PRs are merged and their source content is preserved.
