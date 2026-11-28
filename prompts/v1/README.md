# Prompt contract v1

`system.md` defines the trusted visualization policy. `request.md` is a user-input
template. They are ordinary source files, not executable templates. Build mapping
bundles this directory under `deepviz/resources/prompts/v1/`. Use
`from deepviz import read_prompt` and `read_prompt("system")` to load UTF-8 package
resources, then pass the policy to `create_deep_agent(system_prompt=...)`.

The prompt directs a normalize → recommend → render flow, treats dataset text as
untrusted, forbids arbitrary eval/code, and keeps large raw data out of context.
Runtime Pydantic validation, bounded profiling, fixed output directories, and
file-reference containment enforce parts of this policy; prompting is not a
security sandbox. Deep Agents' own tools/backends require separate least-privilege
configuration if exposed to untrusted users.

Version the directory when changing tool names or the request contract. The public
loader uses `importlib.resources`, not a checkout-relative path. Source edits live
here as the single authority; build/install the package to include resource changes.
