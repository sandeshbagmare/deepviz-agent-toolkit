# Test strategy

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

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
| Five engines | Bar/table/dashboard across five Python backends. | Inspect actual PNG/SVG/HTML and manifest, semantics/MIME/counts/fallbacks. |
| Text/path safety | Hostile title/cell plus traversal/overwrite paths. | Literal text, no execution, denied path cannot overwrite unrelated files. |
| Agent flow | Local normalize -> recommend -> render example without model. | Real artifacts and metadata; no model requirement. |
| MCP | stdio initialize/list/call and retrieve artifact. | Valid protocol, bounded response, safe path, clean shutdown. |
| Package | Build, install wheel/sdist with base and `[mcp]` extra. | Imports, CLI/MCP entrypoints/resources present. |

RC: clean checkout/install, all checks, all rows in file 16, zero open S1/S2/P0. Flake: file issue with logs/seed, quarantine only with owner; never retry silently; remove only after stable repeated runs/review. Node checks only if TS scope is confirmed.
