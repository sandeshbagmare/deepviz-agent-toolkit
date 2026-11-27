# Security policy and threat model

DeepViz treats datasets, model-authored schemas, chart text, and MCP arguments as untrusted. Report vulnerabilities privately through the repository owner's GitHub contact or a private security advisory; do not attach sensitive datasets to public issues.

## Trust boundaries

- **No code in schemas:** schemas select fields and enumerated transformations; arbitrary Python, SQL, JavaScript, HTML, or shell expressions are not a supported feature.
- **No automatic remote ingestion:** the runtime does not fetch model-supplied URLs. Applications must implement their own authenticated, size-limited data retrieval and pass the resulting data.
- **Explicit local files:** direct Python/CLI callers may deliberately pass local paths. Agent/MCP JSON payloads must not implicitly promote strings to paths. Run MCP with the minimum necessary filesystem access and use a dedicated artifact directory.
- **Output:** generated HTML is executable application output, not inert text. Text and JSON must be escaped. Some interactive backends load a pinned upstream script from a CDN and therefore require network access; use offline Matplotlib/Vega output for sensitive or disconnected environments. Do not put private data into public artifact hosting.
- **Resources:** reductions bound the records sent to engines, not the size of an already resident caller-provided dataset. Large file/string parsing and high-cardinality aggregation have distinct memory characteristics; use the streaming paths and verify the chosen strategy. Deployment operators must also enforce request-body limits, process timeouts, disk quotas, and concurrency budgets.
- **MCP:** stdio transport assumes a trusted local client. Do not expose the process as an unauthenticated network service. Artifact access must remain within the configured output root; symlinks and path traversal must not grant arbitrary reads.

## Supply chain

Use isolated environments and lock npm dependencies. Python package extras opt into agent, MCP, or columnar dependencies. Build checks are not evidence that a release exists on PyPI or npm; registry publication is a separate authorized operation.

## Known assurance limits

An agent code review is not a security certification. Browser CDN availability, browser sandboxing, and downstream model behavior remain application responsibilities. See verification reports for tests actually run on the delivered revision.
