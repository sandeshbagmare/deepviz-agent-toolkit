# Test strategy

- Default branch: `main`
- Main SHA reconciled: `f692014b9c7eb6a9fe0aa6f27b76b40426f053a7`
- Date: 2026-11-28
- Plan version: 1.1

## Commands

- `python -m pytest -q --strict-markers`
- `python -m ruff check .`
- `python -m mypy`
- `python -m build`
- Clean-install wheel/sdist in a fresh venv; run import, CLI and optional MCP smoke.

## Per PR and wave

Per PR: unit + affected integration tests, lint, type check, build if package/resources change, and green CI on exact head. Rerun after rebase. Per wave: full suite on main, smoke/E2E, QA exploration and exact merge-SHA evidence; tag only when green.

| Smoke | Steps | Pass evidence |
|---|---|---|
| Chart contract | Valid bar; reject unknown fields, bool/string numeric coercion, empty/nested dashboard. | Python/JSON schema agree; expected validation errors. |
| Normalize | Records, columns, CSV/JSONL, nested GraphQL pages, duplicate/malformed fields. | Deterministic counts/warnings, no silent page loss, bounded output. |
| Arrow/Parquet | With base install, Arrow input fails with an actionable optional-extra message. With `.[columnar]`, test Arrow Table, RecordBatch, Reader, IPC file/stream, Parquet path/buffer, malformed/duplicate/oversized fields, and bounded iteration. | Actual PyArrow-enabled tests run (not skipped through `importorskip`); verify shape, counts/warnings, limits and cleanup. Include a giant-value/nested-row case to assess batch materialization before byte checks. |
| Five engines | Bar/table/dashboard across five Python backends. | Inspect actual PNG/SVG/HTML and manifest, semantics/MIME/counts/fallbacks. |
| Text/path safety | Hostile title/cell plus traversal/overwrite paths. | Literal text, no execution, denied path cannot overwrite unrelated files. |
| Agent flow | Local normalize -> recommend -> render example without model. | Real artifacts and metadata; no model requirement. |
| MCP | stdio initialize/list/call and retrieve artifact. | Valid protocol, bounded response, safe path, clean shutdown. |
| Package | Build, install wheel/sdist with base, `[columnar]`, and `[mcp]` extras in fresh environments. | Imports, Arrow/Parquet capability, CLI/MCP entrypoints/resources present; base install remains usable without PyArrow. |

RC: clean checkout/install, all checks, all rows in file 16, zero open in-scope S1/S2/P0. The caller explicitly revised #28; post the decision and live issue counts after the plan-change merges, then close #28 as superseded. Keep explicitly deferred TypeScript issue #14 open outside the 0.1.0 gate. Flake: file issue with logs/seed, quarantine only with owner; never retry silently; remove only after stable repeated runs/review. Node checks are deferred with TypeScript/npm to v1.1.

## Issue acceptance evidence

Named #21 negative tests must cover script/title/cell injection, script-closing sequences, dangerous configuration values, traversal, absolute-path escape, arbitrary remote-URL/code execution and unrelated-file overwrite. Document optional network-loaded runtimes. Independently inspect dependencies, diagnostics and packaging for accidental credential disclosure; record exact-commit security review and actual-main test evidence.

For #22, Wave 1 records normalizer-only measurements. Keep #22 open until Wave 2/5 tests bounded renderer payload rows and bytes at 10, 1K, 100K, 1M and 10M rows and non-author QA independently replicates them. Save machine-readable exact-main SHA/date, environment/Python/dependency versions, commands, input/normalized/retained/renderer counts and bytes, strategy/warnings/limits, wall time, memory method/peak, replicator identity, result/failures and explicit unrun limitations. An unrun size is not a pass.

For #19, commit dated primary sources for the five renderers, Deep Agents and MCP; separate observed public behavior, documentation facts, inferences and unknown proprietary internals. Review runtime/dependency, licensing, scale and output-format trade-offs without invented benchmark claims, and map every capability/architecture claim to tested evidence or clearly labeled future work.

The #27/#29 public scope/process actions and exact deliverables are listed in `03-v1-scope.md`; documentation existence alone cannot close them.
