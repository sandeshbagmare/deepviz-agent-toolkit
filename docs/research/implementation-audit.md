# Implementation and executable-example audit

**2026-11-27; product source `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.**
This addendum audits the integrated implementation and scoped documentation/example
changes, not a released package or every research claim. Product code is unchanged
by this docs branch. Render/normalizer/tool sources still matched the baseline at
the inspected main checkpoint `40c67be`; prompt packaging was separately fixed in
`f67afac`, as qualified below. Later implementation changes require a new audit;
these observations are not automatically final-candidate signoff.

**Final source-delta check:** main `cf27e85` additionally contains `728bbac`
(existing dashboard rules encoded in shared JSON Schema) and `65b3fc4` (strict
MCP discovery/call input models and cleanup of a failed call's fresh artifact
subtree). The exact diffs were inspected; README/schema wording follows those
committed features. No renderer/normalizer source changes appeared in that check,
so C1-C3 observations below remain open. This docs lane did not import or run the
newer main source and does not borrow another producer's test totals as its own.

## Evidence categories

| Category | What supports it | What it does not establish |
|---|---|---|
| Public documented API | Primary LangChain/MCP pages below, re-fetched 2026-11-27 | Private vendor chart internals, host UI support, or every historical package version |
| Local source inspection | Named modules at the product SHA above | A runtime/browser/clean-distribution pass |
| Executed checkout example | Explicit source import, real tool/graph/stdio calls, retained JSON/artifacts | Installed-wheel availability, live-provider behavior, every kind/encoding, scale or release acceptance |
| Design recommendation | [Architecture](../architecture.md), [scaling](scaling-and-benchmarks.md) | Implementation of the proposed sandbox/budgets/provenance fields |

The earlier [source index](source-index.json) remains a separate 2026-11-26
inventory. A local recount finds 15 distinct repository names, 58 distinct
repository-file URLs and 42 page URLs (100 total). This recount checks inventory
structure, **not** a fresh fetch or new audit of all URLs. An independent official
source audit separately retrieved all 100 endpoints with HTTP 200 and inspected
load-bearing excerpts; its shell access interval was November 26, 2026 UTC, while
the project work date was November 27. One large Plotly page initially exceeded a
bounded reader and was subsequently read incrementally; an initial HTTP 403 with
a different client was retained rather than erased. HTTP reachability is not full
content/behavior/security review. Neither activity increases the repository count
or substantiates a 100+ repository review. No proprietary implementation or unrun
benchmark is inferred.

## Official contracts versus DeepViz choices

1. **Documented:** Deep Agents accepts custom tools, a model string or model
   instance, and `system_prompt` through `create_deep_agent`.
   [Official customization/API guide](https://docs.langchain.com/oss/python/deepagents/customization).
   **Local observation:** `create_tools` returns five renderers plus profile and
   recommendation tools; a deterministic local `BaseChatModel` drives the real
   graph in [deep_agent_local.py](../../examples/deep_agent_local.py). Choosing a
   sample-aware chart and correct units remains the caller's responsibility, not
   a fact guaranteed by the upstream constructor.
2. **Documented:** MCP SDK v1 FastMCP exposes tools/resources, binary resource
   content, and client `read_resource`; tool errors are distinguished by `isError`.
   [Official v1 server guide](https://github.com/modelcontextprotocol/python-sdk/blob/v1.x/docs/server.md).
   **Local observation:** DeepViz returns PNG image content plus registered
   `deepviz://artifacts/...` links. The example downloads bytes/text through the
   protocol; it does not need access to the server's paths. Client rendering of
   HTML is a separate host behavior, not promised by MCP resource delivery.
3. **Source-observed upstream:** SDK stdio constructs a safe inherited environment;
   `PYTHONPATH` is not in its default list.
   [Official v1 transport source](https://github.com/modelcontextprotocol/python-sdk/blob/v1.x/src/mcp/client/stdio/__init__.py).
   **Local decision:** the checkout example explicitly forwards only a supplied
   `PYTHONPATH`, not all host environment variables. Without that override a
   worktree client can accidentally launch the environment's other editable
   install. Installed-package users should leave it unset and verify the intended
   environment/interpreter instead.

The upstream URLs above are mutable documentation/branch references, accessed on
the stated date. Observed installed versions were deepagents 0.7.42, langchain-core
1.8.5 and mcp 1.30.0 under Python 3.12.16. This is evidence of that environment,
not a new dependency pin, compatibility range, or claim to the latest releases.

## Source-backed capability corrections

The [matrix](../capabilities.md) is derived from actual
[`engines.py`](../../python/deepviz/src/deepviz/engines.py),
[`render.py`](../../python/deepviz/src/deepviz/render.py),
[`normalize.py`](../../python/deepviz/src/deepviz/normalize.py),
[`tools.py`](../../python/deepviz/src/deepviz/tools.py), and
[`mcp_server.py`](../../python/deepviz/src/deepviz/mcp_server.py), not the upstream
libraries' total feature lists. npm is separately derived from
[`render.ts`](../../packages/deepviz/src/render.ts) and
[`renderers.ts`](../../packages/deepviz/src/renderers.ts).

- Python Vega-Lite radar/sunburst/gauge become line/pie/bar with explicit warnings;
  ECharts/G2 violin becomes box. One-level custom hierarchy and coordinate-only
  geo are not full hierarchy/map subsystems, even when kinds retain their names.
  Vega gauge specifically draws ordinary bars over bounded rows; its baseline
  first-value/fixed-scale/clamping warning overstates the actual fallback.
- Python Plotly heatmap is fixed-size colored-square scatter, not native grid
  cells, despite `rendered_kind=heatmap` and no fallback warning. npm instead
  emits native Plotly heatmap with a z-matrix. Python invalid y may become zero
  without warnings; npm rejects invalid numeric mappings. The open correctness
  findings are disclosures, not fixes or independent rerun passes.
- Python Plotly embeds JS; Python ECharts 5.6.0 and G2 5.4.8 load from jsDelivr.
  The local ECharts bootstrap explicitly selects SVG. Python Vega outputs static
  SVG through `vl-convert-python`. The npm implementation instead defaults to
  CDN-loaded browser libraries, including Plotly, and has an `svg` fifth engine.
- Python `none` can still sample over budget; group overflow can merge categories.
  Dashboard counts mean max(child inputs) and sum(child normalized outputs), not
  a uniform source-count/visible-mark contract. Row limits alone do not cap bytes,
  temporary disk, native-library memory, or total dashboard work.
- `recommend_chart` has `input_count`, not `output_count`; the profile/render
  result provides the latter. A handle caches a source/reference, not an immutable
  source snapshot or a normalized-dataset database. Re-reading a changed file can
  change a later chart.

## Prompt-resource packaging boundary

At the inspected SHA, `deepviz.read_prompt("system")` uses `importlib.resources`
under `deepviz/resources/prompts/v1/`, but the source package lacks those files
and the root wheel force-include mapping includes only the schema. The exact
checkout import therefore raised `FileNotFoundError`; the prior README claim
that installing source necessarily bundles prompts was not supported.

This branch does not edit product packaging. **Subsequent integrated fix
`f67afac` maps `prompts/v1` into the wheel.** Its producer recorded a clean-venv
installed-wheel test of both prompt bytes and a wheel-through-sdist regression;
the main mapping was directly inspected here. This is a packaging-owner result,
not a new clean-consumer run by this docs lane or an installed test of this
branch's later policy edits. Rebuild/retest after those edits are integrated.

Checkout examples explicitly load the trusted source policy, or accept
`--policy-file prompts/v1/system.md`. That remains correct for an arbitrary
source-tree `PYTHONPATH`, which bypasses build-time resource mapping; it is not a
silent fallback in the public loader or a claim the now-fixed wheel still lacks
resources. The installed-resource README wording assumes `f67afac` is included.

## Independent correction disposition (C1-C8)

| Finding | Documentation disposition, not automatic source resolution |
|---|---|
| C1 invalid Python measurements | Root/capability/npm docs explicitly disclose zero coercion versus npm rejection; source fix and all-adapter negative controls remain required. |
| C2 Vega gauge | Ordinary bar fallback, no asserted first-value/fixed 0-100/clamp guarantee. Warning defect remains a source-owner item. |
| C3 Plotly heatmap | Colored-square scatter surrogate, not native grid geometry; unlike npm. No hidden parity/native claim. |
| C4 support/counts | Separate Python fallback and npm rejection tables; 18 model kinds including dashboard, 17 non-dashboard. |
| C5 assets | Exact runtime-specific versions and local/bundled/CDN boundaries; no inference from zero npm runtime dependencies. |
| C6 byte/disk limits | Current character/row/integration-file limits distinguished from unimplemented cell/record/state/spool/combined UTF-8-byte policies. Planned quotas are not published as guards. |
| C7 unpublished install | Root and npm READMEs use checkout/local tarball install, not unverified registry installation. |
| C8 npm geography | `scattergeo` topology-free/no-extra-network guarantee removed pending actual runtime/network evidence; Python Cartesian coordinates remain separate. |

The duplicate-field ruling is also a required behavior, not an established
baseline feature: CSV duplicate-header checks do not prove all-depth encoded JSON
or Arrow duplicate rejection. The resource and duplicate-policy owners must
commit enforcement and independent reruns before these limits/claims are updated.

## Executed checkout flows and retained observations

All commands below used the main project virtualenv interpreter with explicit
N08-worktree `PYTHONPATH=.../deepviz-n08/python/deepviz/src`. Parent and the separate
MCP filtered-environment identity probe both resolved this worktree's
`deepviz/__init__.py`. No shared environment package changes were made.

```text
python examples/multi_tool_flow.py --output-dir artifacts/local/N08/verified-tools
python examples/mcp_client.py --output-dir artifacts/local/N08/verified-mcp
python examples/deep_agent_local.py --output-dir artifacts/local/N08/verified-agent
python examples/deep_agent.py --help
deepviz render examples/data/sales.csv --spec examples/data/chart.json --engine matplotlib --output-dir artifacts/local/N08/verified-cli
deepviz normalize examples/data/sales.csv --spec examples/data/chart.json
deepviz recommend examples/data/sales.csv --goal comparison
```

All seven commands exited 0. The tool flow invoked all seven real StructuredTools;
each renderer reported 3 inputs/3 normalized outputs, sum strategy, values
Jan=12/Feb=18/Mar=15. The real local graph invoked profile -> recommend -> Matplotlib
and produced files. The MCP client discovered seven tools, called two renderers,
and read six resources. The live-model example was checked only through `--help`;
no keys, live model calls, or recommendation-quality measurements were attempted.

The static MCP preview had a real example bug: the client renamed downloaded
SVG/HTML files independently while HTML still referenced `chart.svg`. A real
transport regression first failed on the missing sibling; the fix keeps safe
basenames in per-renderer directories and exclusive file writes. A second
regression executes the deterministic real-graph example. Invoke these explicitly
because `examples/` is outside the repository's default pytest `testpaths`:

```bash
python -m pytest examples/test_examples.py
python -m ruff check examples
```

### Browser/visual evidence is narrower than all-kind acceptance

One-shot Playwright Chromium checks opened the downloaded static companion,
Python Plotly, Vega static companion, ECharts and G2 bar examples; waited for the
image or render promise; checked bounded data-row counts; and captured screenshots.
All five had no console/page/request errors. ECharts/G2 loaded their actual pinned
CDN scripts without substituted assets; Plotly/static companions made no HTTPS
requests. Plotly's runtime trace values were also checked as 12/18/15.

Visual inspection found correct label-to-height mappings and zero baselines in
all five screenshots. The repaired downloaded preview visibly loads its SVG and
shows Jan=12/Feb=18. However, Vega-Lite sorts nominal labels Feb/Jan/Mar, not source
or calendar order, and **ECharts clips the right-end `month` x-axis name** at the
tested layout. These are recorded differences/visual defects, not a full visual
pass hidden behind a console-free script result. The baseline renderer also
coerces missing numeric channel values to zero; source inspection is not evidence
that missing observations are rendered as gaps.

Local evidence stays under `artifacts/local/N08/`: `command-results.json`,
per-command `.stdout`/`.stderr`, `browser-results.json`, screenshots named
`downloaded-static.png`, `plotly.png`, `vega.png`, `echarts.png`, `antv.png`, and
fresh renderer directories. These are local worktree artifacts, not promised
download links or files shipped in the distribution. No full-kind browser,
clean-wheel/npm, resource-adversary, live-provider, scale-tier, remote-CI,
independent-review, or issue-completion pass is established by these examples.
