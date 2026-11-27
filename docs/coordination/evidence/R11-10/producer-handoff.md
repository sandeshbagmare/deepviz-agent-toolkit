# R11-10 strict RED producer handoff

Source: `ca25af486bf443949125df789f5b5fd1fda8bba8` (same product Python bytes as
`3aa521a5`). Tester session: `ses_de56782e3ffeI5D4lzsNVeLcDk`.

**No production fix is authorized for this tester.** R04 must transfer ownership
to an eligible producer; keep these strict tests unchanged, not skipped/xfail.

## Results

| Selection | Pass | Fail | Skip | Exit |
|---|---:|---:|---:|---:|
| New two-file strict suite, after own harness correction | 14 | 47 | 0 | 1 |
| Final resource-only typed/observational recheck (overlap) | 0 | 3 | 0 | 1 |
| Existing integration/lifecycle/concurrency suite | 77 | 0 | 1 | 0 |

The skip is a genuine Windows WinError1314 artifact-symlink privilege limitation.
New-file Ruff/mypy and existing production mypy pass. Module/test hashes and
individual outcomes are adjacent JSON evidence. Full raw logs/artifacts remain
under the report's unique temp directory; no installed-wheel/provider/CI claim.

## Priority 1: preserve raw admission before MCP SDK preprocessing

- `tools.py`: shared duplicate-rejecting decoder for both `_source` and cache
  snapshots. Count original UTF-8 bytes before parsing; catch excessive parser
  recursion as concise `ValueError`. Preserve valid Unicode, handles, explicit
  authorized files and literal-data/path distinctions.
- `mcp_server.py`: validate/canonicalize the original encoded `data` before
  `super().call_tool` invokes SDK `pre_parse_json`. SDK1.30.0 otherwise silently
  loses duplicates and leading bytes. Forward canonical JSON/data, not `Path`.
- Reuse the existing normalizer decoder read-only if suitable; do not edit the
  normalizer, installed SDK, schema, environment or existing strict oracles.
- Raw UTF-8 sizes 1,000,082 inline / 1,000,022 authorized-file bytes are accepted
  by actual stdio normalize/recommend/render, although direct/StructuredTool calls
  reject them. Duplicate key loss and two leaked `RecursionError`s are separate
  admissions of the same decoder/boundary problem, not invented new issue counts.

## Priority 2: explicit capacity proposal, NOT existing policy

Proposed **128 issued resources per MCP server lifetime**, no eviction/deletion.
At exhaustion, reject further rendering before generation; normalization,
recommendation, discovery and all previously issued reads remain useful. A fresh
server starts a new registry; prior host-owned files remain untouched.

Reserve the renderer's resource upper bound atomically before entering
`ToolSession.render_chart`: current Matplotlib4, Vega3, other engines2. Commit
actual issued counts only after validating the complete output set; release
reservations on failure/cancellation. No partial registration, hidden historical
unbounded list, arbitrary-filesystem resource template or silent host-file cleanup.
Protect accounting/publication against concurrent peers without blocking
unbounded work under a lock. Preserve unique request directories and old resources.

Observed real SDK/stdio: 64 ECharts calls ->128 resources; 65th succeeds ->130 and
two new files. A delegating observation sees generation called once after full.
At124 slots, four queued async SDK peers all succeed ->132 instead of proposed
two successes/two capacity errors ->128. SDK sync handlers may serialize; this is
not proof of native thread race safety. No exhaustion/RSS benchmark was attempted.

The product owner must explicitly accept/document 128 or choose another finite
policy with updated reviewed tests. Do not silently weaken these acceptance
oracles. README/render/private-SDK paths are not released here; request expansion
before touching them. Prefer a separate tested GREEN priority1 producer commit
before any more complex capacity change. R04 owns integration/review/CI/issues.
