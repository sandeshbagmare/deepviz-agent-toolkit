# Prompt contract v1

`system.md` defines the trusted visualization policy. `request.md` is a user-input
template. They are ordinary source files, not executable templates. For checkout
examples, read the trusted `prompts/v1/system.md` as UTF-8 or pass
`--policy-file prompts/v1/system.md` to `examples/deep_agent.py`. Then pass the
policy text to `create_deep_agent(system_prompt=...)`.

The public `read_prompt("system")` / `read_prompt("request")` loader reads files
under `deepviz/resources/prompts/v1/` in an installed distribution. Build mapping
added in `f67afac` includes this versioned source directory in wheels; a clean-wheel
consumer regression checks both prompt bytes. An arbitrary source-tree `PYTHONPATH`
does not run that mapping, so checkout examples still use the explicit file path.
See the historical defect/fix distinction in the
[source-specific audit](../../docs/research/implementation-audit.md).

The prompt directs a normalize → recommend → render flow, treats dataset text as
untrusted, forbids arbitrary eval/code, and keeps large raw data out of context.
Runtime Pydantic validation, bounded profiling, fixed output directories, and
file-reference containment enforce parts of this policy; prompting is not a
security sandbox. Deep Agents' own tools/backends require separate least-privilege
configuration if exposed to untrusted users.

Version the directory when changing tool names or the request contract. The public
loader uses `importlib.resources`, not a checkout-relative path. Source edits live
here as the single authority; rebuild/reinstall to include changed policy bytes.
`deep_agent_local.py` exercises
the real graph with deterministic local tool calls and the source policy; it does
not assess whether an LLM follows these instructions.
