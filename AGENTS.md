# DeepViz engineering rules

## Contract and ownership
- Python is primary; `python/deepviz/src/deepviz/models.py` defines the versioned schema.
- Regenerate `schemas/chart-spec.schema.json` after changing contracts; test Python/TypeScript agreement.
- Feature work uses isolated branches/worktrees. Do not modify another worker's files.
- Read the design and architecture before implementation. Do not expand model-authored schemas to accept executable code.

## Verification
- Run `python -m pytest`, `ruff check .`, `mypy`, and distribution builds in the project virtual environment.
- Run `npm ci`, `npm run build`, `npm run typecheck`, `npm test`, and `npm pack --dry-run --workspace @deepviz/agent-toolkit` for npm changes.
- Exercise 10, 1K, 100K, 1M, and 10M through the streaming path; report input/output counts, elapsed time and memory methodology.
- Inspect real SVG/PNG/browser output, not just artifact existence. Browser console errors are test failures.
- Record exactly what ran and the source commit. Never promote a skipped test or uninstalled optional dependency to a pass.

## Safety and output
- Never use `eval`, `exec`, shell execution, arbitrary JavaScript expressions, or remote URL ingestion from chart specifications.
- Distinguish data strings from explicitly authorized local file paths. MCP must not expose arbitrary filesystem access.
- Bound reduced data before renderer serialization. Explain all lossy transformations in metadata.
- Escape HTML and script-embedded JSON. Never trust titles, labels, field names or cell values.
- Use unique artifact names/directories; preserve files not produced by the current operation.
- Keep authentication tokens in memory only and out of subprocess arguments/logs/repo files.

## Delivery evidence
Every PR links real issues and includes rendered output plus its correctness rationale, two independent reviewer-agent reports, and two independent tester-agent reports. Agent review comments are not GitHub human approvals. Do not close issues without evidence. Do not manufacture issue counts or performance claims.
