# Runnable checkout examples

Run from the repository root after installing `.[agents,mcp]` into your own
virtual environment. `python` below means that environment's interpreter; these
examples do not require a published PyPI/npm package. Never install dependencies
into another running worker's shared environment.

## Direct CLI, with supplied inputs

```bash
deepviz render examples/data/sales.csv --spec examples/data/chart.json --engine matplotlib --output-dir artifacts/local/cli
deepviz normalize examples/data/sales.csv --spec examples/data/chart.json
deepviz recommend examples/data/sales.csv --goal comparison
```

The CSV has Jan/Feb/Mar revenue 12/18/15 (USD). The explicit sum spec produces
three normalized records; the static chart has three bars, zero baseline, and
February tallest. Artifact names/directories are freshly generated, not stable
paths. Save/open the returned files rather than constructing a guessed name.
`normalize` prints the bounded profile/handle envelope, not raw rows, just like
the agent `normalize_data` tool. A CLI handle expires when that process exits;
use one in-process tool collection or one MCP server for a reusable handle chain.

## Seven tools, no agent or model

```bash
python examples/multi_tool_flow.py --output-dir artifacts/local/integrations
```

This invokes all seven real `StructuredTool` instances from **one** `create_tools`
collection: profile, recommend, then render five alternatives. It reviews the
recommendation by overriding known mappings/title and passes the same source
handle to every renderer. The program prints JSON containing each result's actual
contract; the recommendation has `input_count` but no `output_count`.
The five outputs are the reviewed **original bar mapping**, not an unmodified
recommended mapping or five automatically chosen chart types.

Python output/asset policies differ: Matplotlib PNG/SVG and Vega-Lite SVG render
locally; Plotly embeds its JS bundle; ECharts 5.6.0 and G2 5.4.8 load from jsDelivr.
Writing a browser artifact does not establish that the CDN loaded or the chart
rendered. See the [adapter matrix](../docs/capabilities.md) before choosing kinds.

## Real Deep Agents graph, deterministic decisions

```bash
python examples/deep_agent_local.py --output-dir artifacts/local/deep-agent-local
```

This creates a temporary approved `sales.csv`, attaches a real graph to the tools,
and executes `normalize_data -> recommend_chart -> render_matplotlib`. Its local
`BaseChatModel` only scripts decisions and reads the real tool results; it is not
an LLM, hosted model, recommendation-quality test, or provider smoke test. The
printed JSON contains `mode`, `tools_called`, and the actual artifact envelope.
It reads this checkout's trusted `prompts/v1/system.md`, not an installed resource.

For a separately configured real provider:

```bash
python examples/deep_agent.py --model provider:model-name --policy-file prompts/v1/system.md
```

Replace the deliberately invalid placeholder with your installed provider/model.
Supply keys outside the repository. Omit `--policy-file` only when your installed
distribution has the prompt resources expected by `deepviz.read_prompt`; see the
[source-specific packaging finding](../docs/research/implementation-audit.md).
Deep Agents' own filesystem/extra tools are a separate host permission boundary.

## Real MCP transport and downloaded resources

```bash
python examples/mcp_client.py --output-dir artifacts/local/mcp-demo
```

This starts `sys.executable -m deepviz.mcp_server` through the official MCP client,
initializes, lists seven tools, renders static Matplotlib and interactive ECharts,
then reads returned resource URIs. It does not copy server paths directly. Each
run saves into a fresh `client-*` directory, with separate `matplotlib/` and
`echarts/` children retaining safe resource basenames. Keep `chart.html` beside
`chart.svg`; prefixing only the downloaded SVG filename breaks the static preview.
The ECharts download still needs the disclosed CDN script to display.

For a GUI MCP host, adapt [mcp-config.json](mcp-config.json) with absolute paths to
your environment's interpreter, trusted output directory, and optional approved
data directory. Host support determines inline display. These examples do not
establish a generic chart widget, multi-tenant service, durable handle database,
or production sandbox.

## Example regression checks

```bash
python -m pytest examples/test_examples.py
python -m ruff check examples
```

`examples/` is outside the default pytest `testpaths`, so invoke this regression
file explicitly. It uses real MCP/Deep Agents dependencies and checks the saved
HTML's SVG link plus the actual three-tool graph result. Browser execution,
clean wheel/npm installation, live providers, all kinds and scale measurements
are separate checks; these two regressions do not substitute for them.
