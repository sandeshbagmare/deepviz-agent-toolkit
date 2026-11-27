# DeepViz Agent Toolkit

Declarative, bounded visualization for Python, Deep Agents, MCP, and TypeScript.
Python exposes **five real LangChain `StructuredTool` renderers**—Matplotlib,
Plotly, Vega-Lite, Apache ECharts, and AntV G2—plus normalization and recommendation
tools. The same seven operations are available from a local stdio MCP server.

**Source installation only:** the package names below identify this repository's
builds, not a verified PyPI/npm publication. No hosted service, API key, or LLM is
needed for direct rendering or the MCP server. An LLM provider is needed only when
you choose to run an agent with a real model.

## Install from the checkout

Python 3.11+:

```bash
python -m venv .venv
# Activate .venv (Windows PowerShell: .venv\Scripts\Activate.ps1)
# macOS/Linux: source .venv/bin/activate
python -m pip install "."
# Optional integrations and development checks:
python -m pip install ".[agents,mcp,dev]"
# Optional Arrow/Parquet ingestion:
python -m pip install ".[columnar]"
```

The Python distribution is `deepviz-agent-toolkit`; the import is `deepviz`.
`agents` brings Deep Agents/LangChain; `mcp` intentionally pins the official MCP
SDK's **1.x FastMCP API** (`mcp<2`), rather than assuming 2.x compatibility. Those
integrations are lazily imported, so base rendering does not require either extra.

Node.js 22+ (from the same repository root):

```bash
npm ci
npm run build
npm test
npm pack --workspace @deepviz/agent-toolkit
# In a consuming project, install the resulting LOCAL .tgz:
# npm install /absolute/path/to/deepviz-agent-toolkit-0.1.0.tgz
```

The npm package is `@deepviz/agent-toolkit`. Its browser renderers are not Python's
Matplotlib adapter, and its framework-neutral tool helpers are not advertised as
LangChain `StructuredTool` instances. See [the package](packages/deepviz/).

## Python: render directly

```python
from deepviz import render

rows = [
    {"month": "Jan", "revenue": 12},
    {"month": "Feb", "revenue": 18},
    {"month": "Mar", "revenue": 15},
]
spec = {
    "version": 1,
    "kind": "bar",
    "title": "Monthly revenue (USD)",
    "x": "month",
    "y": "revenue",
    "max_points": 2000,
    "aggregation": "auto",
}
artifact = render(rows, spec, engine="matplotlib", output_dir="artifacts/local/demo")
print(artifact.to_dict())  # paths, mime_type, engine, counts, strategy, warnings
```

Use `plotly`, `vega`, `echarts`, or `antv` for alternative adapters. ChartSpec v1 is
validated by Pydantic and rejects extra executable options. The schema includes
bar, line, scatter, area, pie, heatmap, histogram, box, violin, bubble, radar,
treemap, sunburst, funnel, gauge, geo, table, and composed dashboard requests:
**18 kinds including dashboard, 17 non-dashboard**, not 18 native layouts per engine.
Not every request is native in every engine: inspect warnings and the output
manifest for explicit fallbacks rather than assuming equivalent semantics.
The [implementation capability matrix](docs/capabilities.md) names those fallbacks,
one-level hierarchy/coordinate-only geographic layouts, and encoding limitations;
it is not a claim that every upstream feature has been tested here.

| Python request | Actual fallback in the inspected adapter |
|---|---|
| Vega-Lite radar | Line |
| Vega-Lite sunburst | Pie |
| Vega-Lite gauge | Ordinary bar, not the fixed-scale gauge contract |
| ECharts violin | Box |
| G2 violin | Box |

Python Plotly heatmap currently uses a **colored-square scatter surrogate**, not a
native heatmap grid, even though its manifest retains `heatmap` without a fallback
warning. The [separate npm allowlist](docs/capabilities.md#npm-is-a-separate-browser-implementation)
rejects unsupported combinations instead; Python warnings are not npm's contract.

### All seven agent tools

[Run the complete no-LLM example](examples/multi_tool_flow.py):

```bash
python examples/multi_tool_flow.py --output-dir artifacts/local/integrations
```

Each row below links to runnable inputs and the corresponding output contract.
The script prints actual output paths; it does not assume a fixed artifact name.
It takes `advice["spec"]` and explicitly overrides it with the known original bar
mapping/title, so the result compares the **reviewed original bar** across engines,
not an unmodified recommendation or model-selected alternative chart.

| Tool | Input example | Output |
| --- | --- | --- |
| `normalize_data` | [small records + spec](examples/multi_tool_flow.py) | [bounded profile + dataset handle](#profile-output) |
| `recommend_chart` | [handle + comparison goal](examples/multi_tool_flow.py) | [editable spec + rationale](#recommendation-output) |
| `render_matplotlib` | [handle + bar spec](examples/multi_tool_flow.py) | [PNG/SVG + metadata](#render-output) |
| `render_plotly` | [handle + bar spec](examples/multi_tool_flow.py) | [HTML + metadata](#render-output) |
| `render_vega` | [handle + bar spec](examples/multi_tool_flow.py) | [Vega-Lite SVG + metadata](#render-output) |
| `render_echarts` | [handle + bar spec](examples/multi_tool_flow.py) | [HTML + metadata](#render-output) |
| `render_antv` | [handle + bar spec](examples/multi_tool_flow.py) | [HTML + metadata](#render-output) |

#### Profile output

`normalize_data` returns `dataset_id`, `input_count`, `output_count`, `strategy`,
`warnings`, and a bounded field-type `profile`, **not raw rows**. The profile uses
only the bounded normalized records. A `dataset_id` is opaque, process-local, and
kept in a 32-entry per-tool-instance cache; reuse one `create_tools(...)` result
for a flow. It is not a durable dataset store. CLI handles expire on process exit.

#### Recommendation output

`recommend_chart` returns `dataset_id`, `spec`, `engine`, `rationale`, `input_count`,
and warnings. It does **not** return `output_count`; use the profile/render result
for that count. Goals are `comparison`, `trend`, `relationship`, `distribution`, and
`composition`. Recommendations infer observed types, not business meaning: users
must verify field mappings, units, ordering, pie-chart part/whole assumptions,
and reduction semantics. Rare types/extremes may be absent from the profile.

#### Render output

In-process tools return artifact metadata with actual local `paths`. Inputs can
be small JSON data, `{"dataset_id": "returned-id"}`, or an allowed file reference.
The original source is re-read and normalized at render time, so a reduced profile
does not reset `input_count` to its own sample size. Keep source files unchanged
during a flow if the profile and chart must describe the same snapshot. Each tool
call gets a fresh output subdirectory; it cannot choose a model-authored filename.

Python Plotly HTML embeds the installed Plotly JavaScript bundle. Python ECharts
HTML loads ECharts **5.6.0**, and AntV HTML loads G2 **5.4.8**, from jsDelivr; those
two outputs need network access. Matplotlib PNG/SVG and Vega-Lite SVG render locally.
Their companion `chart.html` needs its sibling `chart.svg` kept beside it. These
Python details do not describe the separate npm adapters' asset policy.
The bounded records can appear in generated HTML/manifests, so treat artifacts as
containing source-derived data when deciding where to share them.

## Attach to a Deep Agent

The primary attachment point is `create_deep_agent(tools=create_tools(...))`:

```python
from pathlib import Path
from deepagents import create_deep_agent
from deepviz import create_tools

# Run this checkout example from the repository root; the policy is trusted code configuration.
policy = Path("prompts/v1/system.md").read_text(encoding="utf-8")

agent = create_deep_agent(
    model="provider:model-name",  # install/configure your chosen provider separately
    tools=create_tools("artifacts/local/agent", data_dir="/absolute/path/to/approved-data"),
    system_prompt=policy,
)
result = agent.invoke({"messages": [{"role": "user", "content": (
    'Compare revenue in {"file":"sales.csv"}; month is categorical and revenue is USD. '
    "Profile, recommend, render a static chart, then report counts and warnings."
)}]})
print(result["messages"][-1].content)
```

`provider:model-name` is deliberately a placeholder, not a claimed model ID.
[The executable agent example](examples/deep_agent.py) accepts `--model`, creates
a tiny temporary CSV, and accepts `--policy-file prompts/v1/system.md` for a
checkout policy. Without that option it calls `read_prompt("system")` from installed
package resources. The build maps `prompts/v1/` into those resources; source-tree
`PYTHONPATH` mode still needs the explicit trusted file. See the
[packaging boundary and source-specific audit](docs/research/implementation-audit.md).
Configure the provider package and credentials in your own environment.

```bash
# Real graph and tools, deterministic local decisions: no provider, key, or network needed.
python examples/deep_agent_local.py --output-dir artifacts/local/deep-agent-local
# Live model: supply your actual installed provider/model and credentials.
python examples/deep_agent.py --model provider:model-name --policy-file prompts/v1/system.md
```

The [local example](examples/deep_agent_local.py) calls the real Deep Agents graph
with a small scripted `BaseChatModel` and executes profile -> recommend -> render
using a temporary CSV. It proves attachment/tool-result plumbing, **not** LLM chart
selection, model quality, or live provider access. Its JSON output includes all
three tool names and the actual artifact metadata.

For large datasets, reference an approved local file. Do not paste millions of
rows into messages, return full normalized data into context, or ask an agent to
generate arbitrary Python/JavaScript. Our tools do not eval/exec model-authored
code. Deep Agents' own filesystem, execution, and additional tools are outside
this toolkit's path boundary; configure them separately with least privilege.

## MCP: stdio tools, PNG previews, and readable resources

```bash
deepviz-mcp --output-dir /absolute/path/to/artifacts --data-dir /absolute/path/to/approved-data
# Equivalent:
python -m deepviz.mcp_server --output-dir /absolute/path/to/artifacts
```

Add the same `--data-dir /absolute/path/to/approved-data` to the module invocation
if file inputs are needed; the abbreviated invocation above enables inline JSON only.
No `--data-dir` means file inputs are disabled. Inline small JSON still works.
The server reserves stdout for MCP messages. See the [client config](examples/mcp-config.json):
replace every `/ABSOLUTE/PATH` placeholder. On Windows use your virtualenv's
`C:/path/to/.venv/Scripts/python.exe`; do not assume the GUI client's PATH or
working directory matches your terminal.

The server exposes the same seven tool names. Render results include metadata
and `deepviz://artifacts/...` resource links. **PNG bytes are also returned as MCP
image content**. Clients call `resources/read` on returned URIs to obtain bytes or
HTML text; paths on the server's disk are not the only delivery mechanism. HTML
display depends on the host: clients can save/open it but must not assume an
interactive preview inside chat.

```python
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "deepviz.mcp_server", "--output-dir", "artifacts/local/mcp"],
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        print([tool.name for tool in (await session.list_tools()).tools])
        result = await session.call_tool("render_matplotlib", {
            "data": [{"month": "Jan", "revenue": 12}, {"month": "Feb", "revenue": 18}],
            "spec": {"kind": "bar", "x": "month", "y": "revenue"},
        })
        if result.isError:
            raise RuntimeError(str(result.content))
        # result.content includes image content and readable resource links.
        resource = next(block for block in result.content if block.type == "resource_link")
        content = await session.read_resource(resource.uri)
        print(content.contents[0].mimeType)

asyncio.run(main())
```

[The complete MCP client](examples/mcp_client.py) discovers tools, calls both a
static and interactive renderer, and saves resource content in a fresh client-side
directory. It does not rely on direct access to server-local paths:

```bash
python examples/mcp_client.py --output-dir artifacts/local/mcp-demo
```

Downloaded files retain server-provided safe basenames inside separate renderer
directories, so `matplotlib/chart.html` can load `matplotlib/chart.svg`. Open the
downloaded HTML, not the metadata manifest, to view the companion report. ECharts
still needs its disclosed CDN connection after download.

The server is a local stdio process, not a multi-tenant network service. Only
artifacts created in its configured output directory are registered as resources.
File references must stay inside the configured data directory after resolving
symlinks; absolute paths, URLs, and traversal outside it are rejected. This is not
a sandbox against a malicious local filesystem owner or a concurrent symlink race.
Keep both directories under trusted host control. Artifacts remain on disk until
the operator removes them; plan retention/storage quotas for long-lived processes.

## CLI

```bash
deepviz render examples/data/sales.csv --spec examples/data/chart.json --engine matplotlib --output-dir artifacts/local/cli
deepviz normalize examples/data/sales.csv --spec examples/data/chart.json
deepviz recommend examples/data/sales.csv --goal comparison
deepviz mcp --output-dir artifacts/local/mcp --data-dir /absolute/path/to/approved-data
```

The supplied [chart.json](examples/data/chart.json) contains a declarative spec,
not executable code; [sales.csv](examples/data/sales.csv) contains three known rows.
Commands emit JSON on stdout and errors on stderr; invalid input exits nonzero.
Direct CLI file arguments are operator-selected local paths. Agent/MCP tools use
the stricter approved-relative-file boundary.
See [the example guide](examples/README.md) for expected marks, tool flows and limits.

## TypeScript

```javascript
import {writeFile} from 'node:fs/promises';
import {render} from '@deepviz/agent-toolkit';

const artifact = render(
  [{month: 'Jan', revenue: 12}, {month: 'Feb', revenue: 18}],
  {kind: 'bar', x: 'month', y: 'revenue', title: 'Monthly revenue'},
  'echarts',
);
await writeFile('revenue.html', artifact.html, {flag: 'wx'});
console.log(artifact.input_count, artifact.output_count, artifact.strategy, artifact.warnings);
```

This returns HTML in memory, not filesystem paths; the consuming application owns
safe file naming/storage. Browser engine support and format adapters differ from
Python: inspect [the package source](packages/deepviz/src/) and tests rather than
assuming identical ingestion or Matplotlib availability. Async stream APIs exist
for bounded per-chart processing; a parsed in-memory JSON object is already resident.
Its fifth engine is a small native `svg` adapter, not Matplotlib; unsupported
engine/kind combinations are rejected rather than using Python's fallback table.
Default npm Plotly/ECharts/G2/Vega HTML loads version-pinned CDN scripts; Python's
bundled Plotly policy does not apply. `renderStream` rejects streaming dashboards.
See [the separate npm capability/asset section](docs/capabilities.md#npm-is-a-separate-browser-implementation).

## Inputs, limits, and scaling semantics

- The shared normalizer handles supported record/column/nested JSON layouts and
  explicit `data_path` mapping; GraphQL nodes/edges and paginated fixtures are
  adapter cases, not proof of accepting every possible API response.
- Large JSONL/CSV/TSV and supported generator/columnar paths should use streaming
  reductions. JSON documents, strings, already-parsed arrays, and format-specific
  parsers can require materialization. Optional Arrow/Parquet needs `columnar`.
- `max_points` bounds **output records**, not input bytes or source rows scanned.
  Reducing ten million rows to a bounded chart is not rendering ten million
  independent browser marks. Grouped reductions, sampling, and binning are lossy
  and chart-specific. Read `input_count`, `output_count`, `strategy`, and warnings.
- Explicit sum/mean/count/min/max and sampling are different operations. Validate
  your mappings and denominator before drawing conclusions from a reduced chart.
  No benchmark or universal bounded-memory/performance claim is made here.
- In Python, `aggregation="none"` still uses a warned deterministic reservoir
  sample when the source exceeds `max_points`; it does not mean unbounded identity
  output or strict failure on overflow. High-cardinality grouped reductions retain
  the first `max_points - 1` groups and merge remaining contributions into a warned
  `__deepviz_other__` bucket. A sample is not a temporal-extrema-preserving reducer.
- Agent/MCP inline JSON is limited to **1 MB**; use approved file references for
  larger sources. Integration artifacts/resources are capped at **16 MiB per file**.
  Profile fields and cached dataset handles are bounded, not a database or durable
  ingestion service. Schema limits do not replace operating-system resource quotas.
- Those integration caps are not demonstrated per-cell, retained-UTF-8-byte or
  dashboard-spool quotas for Python direct/file rendering. JSON documents can be
  read wholesale, strings can be large, and iterator dashboard replay can exhaust
  temporary disk. Do not treat planned byte budgets as implemented protections.
- **Current Python correctness limit:** null/non-numeric mapped y values can become
  zero in adapter channels without warnings; a wholly absent mapped field is a
  different validation case. npm instead rejects invalid numeric chart mappings.
  Filter/validate measurements yourself and inspect actual output; the policy
  goal of explicit errors/warnings is not proof every current path achieves it.
- All model-authored requests use a fixed declarative schema; arbitrary callbacks,
  code strings, URL reads, and user-selected output paths are not tool features.
  Trusted renderer libraries naturally run their own code; this is not a promise
  that browser libraries never use dynamic compilation internally.

## Verification and scope

The default Python suite includes cross-language parity tests, so build the local
npm package first. This is a **development-test prerequisite**, not a requirement
for Python-only rendering at runtime.

```bash
npm ci
npm run build
python -m pytest
python -m pytest examples/test_examples.py
python -m ruff check python/deepviz/src python/deepviz/tests examples
python -m mypy
python -m build
npm test
npm run typecheck
```

The integration suite in [test_integrations.py](python/deepviz/tests/test_integrations.py)
checks real StructuredTool outputs, a real Deep Agents graph tool call without a
provider, CLI processes, and **real MCP stdio initialize/discovery/call/resource
access**. Run with the optional extras installed; a skipped optional-dependency
test is not evidence of an integration passing. Browser visual checks, scale
measurements, package publication, and live provider tests are separate evidence
and must not be inferred from a unit-test pass.
The example regression command is explicit because `examples/` is outside the
default pytest `testpaths`; it checks the real MCP download's relative image link
and the deterministic Deep Agent chain. It requires both `agents` and `mcp` extras.

## Official integration references

Researched November 26, 2026; API versions above are intentional:

- [Deep Agents customization and `create_deep_agent(tools=...)][deepagents-docs].
- [LangChain `StructuredTool.from_function` and schema parameters][structured-docs].
- [Official MCP Python SDK 1.x server tools, resources, images, and stdio][mcp-server-docs].
- [Official MCP Python SDK version/migration notice][mcp-version-docs].

[deepagents-docs]: https://docs.langchain.com/oss/python/deepagents/customization
[structured-docs]: https://reference.langchain.com/python/langchain-core/tools/structured/StructuredTool/from_function
[mcp-server-docs]: https://github.com/modelcontextprotocol/python-sdk/blob/v1.x/docs/server.md
[mcp-version-docs]: https://github.com/modelcontextprotocol/python-sdk/tree/v1.x

MIT licensed. This toolkit is not an official LangChain, MCP, or renderer-vendor product.
