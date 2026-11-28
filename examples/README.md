# Local integration examples

Install the package with the adapter you use:

```sh
python -m pip install -e '.[mcp]'
python examples/mcp_client.py --output-dir artifacts/mcp-demo
```

The client starts a local stdio server, discovers its tools, renders real charts,
and saves the returned resources in a fresh client directory. It does not require
an LLM or an API key. Server logs go to stderr; stdout contains the saved paths.

For a local Deep Agents tool chain without calling a model:

```sh
python -m pip install -e '.[agents]'
python examples/multi_tool_flow.py --output-dir artifacts/tool-demo
```

`mcp-config.json` is a host configuration template. Replace every absolute-path
placeholder before use. A Windows virtual environment uses `Scripts/python.exe`;
Unix environments use `bin/python`. File inputs are disabled unless the host sets
`--data-dir`; references must stay inside that directory. Use a dedicated output
directory and read returned `deepviz://` resources through MCP `resources/read`.

The stdio server issues at most 128 artifact resources during its lifetime.
Restart it when that limit is reached. Successful artifacts persist on disk;
failed render requests remove only their own newly created output directory.
Browser HTML may need network access for its declared renderer assets. Inspect
the returned warnings and counts before treating a chart as complete.
