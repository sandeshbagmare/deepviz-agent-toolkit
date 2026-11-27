# N03 TypeScript normalization/parity producer

- Owner/session: N03 subagent; runtime session ID not provided.
- Assigned branch: `fix/n03-ts-correctness` in NEW worktree `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n03`.
- Required base: `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`; current SHA not yet inspected.
- Allowed source paths: `packages/deepviz/src/models.ts`, `packages/deepviz/src/normalize.ts`, and NEW TypeScript normalization/parity regression test files only.
- Shared-path ownership: this assigned report in main checkout only. No main source edits, shared environment changes, spawning, GitHub writes, merges, or pushes.
- Acceptance: concrete failing regression before each smallest scoped fix; npm build/typecheck/targeted tests; explicit source identity, SHA/dirty state, commands, exit codes and test counts; commit tested scoped changes.
- Completed: read assignment and `C17-wave-common.md` before other work. Report saved immediately as required.
- Current action: add failing text-ingestion and stream/path regression tests against confirmed authoritative Python behavior.
- Next action: run new tests RED on baseline, then apply minimal fixes in `normalize.ts` only.

## Setup and baseline evidence

- Read required recovery/coordination/design/plan/dependency-gate/architecture files and existing TS tests, Python normalizer/model, and cross-language contract suite. Latest AGENTS ownership clarification honored. No spawning; C17 retains independent review responsibility.
- `git status --short --branch`, `git log -8 --oneline`, `git worktree list --porcelain` from main: exit 0. Main at exact required base, existing recovery/opencode changes preserved; existing worktrees untouched.
- `git worktree add -b fix/n03-ts-correctness C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n03 b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`: exit 0, fresh branch/worktree created. Worktree began clean.
- `npm ci` in own worktree: exit 0, 160 packages installed, 0 vulnerabilities; no shared venv writes.
- Node `v26.13.1`; main `.venv/Scripts/python.exe` is Python 3.12.16. Set explicit own `PYTHONPATH=C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n03\python\deepviz\src`, `PYTHONDONTWRITEBYTECODE=1`; actual `deepviz.__file__` is that worktree's `python/deepviz/src/deepviz/__init__.py`.
- `npm run build`: exit 0. `npm test`: exit 0, 30 passed / 0 failed / 0 skipped on pristine base (build occurs inside test).
- Inline Python semantic probe: exit 0. Confirmed auto JSONL yields both records; auto JSON numeric scalar yields index/value; CSV whitespace numeric coercion uses stripped content while preserving nonnumeric text; NaN/scientific overflow become warned null; all-empty delimited rows and quoted-empty cells remain rows; standalone GraphQL edge unwraps. Invalid undelimited content rejects. Current TS source contradicts these cases.
- Existing Python model now explicitly rejects string/boolean numeric spec inputs, matching current TS; no coercion-policy/schema change is needed. Sampling PRNG identity and byte-budget/truncation policy are contract decisions, not independently changed here.
- Ruling: assigned report serves as durable execution ledger rather than writing broader shared plan workspaces; explicit scope/no-spawning constraints supersede generic skill workflow. Only scoped new regression tests and `normalize.ts` may change.

## TDD checkpoint 1: text ingestion

- Added NEW `packages/deepviz/test/normalization-regressions.test.mjs` with 18 literal-behavior regressions/guards. `node --test packages/deepviz/test/normalization-regressions.test.mjs` against pristine built baseline: exit 1, 2 passed / 16 failed / 0 skipped. Observed JSONL SyntaxError, JSON scalars silently returning no records, BOM parse failure, invalid content silently accepted as a header, whitespace content inventing a row, CSV all-empty/quoted-empty rows dropped, numeric/nonfinite cells kept as strings, standalone edges incorrectly flattened, and per-page path validation aborting before later matches. One failure additionally identified inconsistent raw SyntaxError instead of public ValidationError.
- Fixed text parsing only: JSON-first auto detection (scalars included), validated JSONL fallback, BOM handling, explicit invalid-content error, row-preserving CSV lexer, stripped numeric/null cell conversion, nonfinite-to-warned-null behavior, and whitespace-only header rejection. No byte budget/truncation/default policy change.
- `npm run build`: exit 0. `node --test --test-name-pattern='automatic|CSV' packages/deepviz/test/normalization-regressions.test.mjs`: exit 0, 12 passed / 0 failed / 0 skipped (6 unrelated tests not selected).
- Current action: fix the remaining already-RED standalone-edge and source-global path regressions, preserving per-row/page streaming.

## TDD checkpoint 2: path/edge semantics and mixed-type disclosure

- Fixed standalone GraphQL edge unwrapping/null skipping; path matches/missing branches now accumulate over the entire JSONL/async source before deciding whether selection failed. Still processes each source record/page incrementally. Empty sources remain valid; wholly missing paths still reject.
- First complete GREEN: `npm run build` exit 0; focused regression file 18 passed / 0 failed / 0 skipped; `npm test` exit 0, 48 passed / 0 failed / 0 skipped.
- Added four further literal regressions: CSV path selection and missing-path rejection, empty-stream path syntax validation, and mixed numeric/nonnumeric field warning. `node --test --test-name-pattern='CSV data_path|empty streams still|mixed numeric' packages/deepviz/test/normalization-regressions.test.mjs`: exit 1, 0 passed / 4 failed / 0 skipped. Confirmed CSV skipped path selection entirely, path syntax was only validated when data existed, and mixed fields were undisclosed.
- Minimal fixes: route decoded CSV rows through the same selector, validate path syntax before consuming the source, and store bounded per-schema type masks rather than only field membership. Mixed-type disclosure now mirrors Python without changing input values, grouping, or defaults.
- Latest commands (own worktree): `npm run build` exit 0; focused file 22 passed / 0 failed / 0 skipped; `npm run typecheck` exit 0; `npm test` exit 0, 52 passed / 0 failed / 0 skipped; `npm pack --dry-run --workspace @deepviz/agent-toolkit` exit 0, 22 packaged files. No actual tarball publication.
- Read N12's current `reports/N12-parity.md` once: initial setup only, no findings yet. An initial guessed filename `N12-schema-parity.md` was absent; glob resolved the assigned report, no repeated polling. Read N01's completed report: renderer findings belong to renderer lane; Python partial-GraphQL-error warnings and numerical cancellation belong to N04/C17. TS also needs the agreed partial-error/numerical policy eventually; do not silently change cross-language arithmetic or resource contracts here.
- Current action: exact import/schema parity, source review and scoped commit; preserve explicit remaining limitations rather than claiming release signoff.

## TDD checkpoint 3: align N04's reported numerical/disclosure fix

- Read N04's report once after its RED→GREEN checkpoint. N04 explicitly chose constant-size Neumaier sum correction with compensation carried into the other bucket and GraphQL error accounting during nonterminal path traversal. Mirrored that reported behavior independently; no dirty sibling source copied, no contract/schema edit.
- Added five literal regressions for `[1e16,1,-1e16] -> 1`, an evicted group's correction surviving the other bucket, selected-path partial errors, paginated partial errors and error-only envelope rejection. RED command `node --test --test-name-pattern='compensated|cancellation|partial-error|error-only' packages/deepviz/test/normalization-regressions.test.mjs`: exit 1, 0 passed / 5 failed / 0 skipped.
- Added empty GraphQL error-array control; separate RED command `node --test --test-name-pattern='empty GraphQL errors' packages/deepviz/test/normalization-regressions.test.mjs`: exit 1, 0 passed / 1 failed / 0 skipped. Existing code treated empty JS arrays as actual errors.
- Implemented one correction scalar per group; transfer is automatic because overflow preserves the group object. Nonfinite overflow remains warned null (not converted back to a finite residual). Shared envelope check runs before path metadata is discarded and in ordinary unpacking; empty errors collections are not partial failures. Existing bounded warning Set avoids duplicated notices across pages.
- GREEN: `npm run build` exit 0; focused regression file 28 passed / 0 failed / 0 skipped; full `npm test` exit 0, 58 passed / 0 failed / 0 skipped; `npm run typecheck` exit 0.
- Current action: final exact public-import/schema parity and diff review before committing only the two allowed source/test files. No whole-product/renderer/final-candidate signoff.

## Parity gate failure retained, not weakened

- Confirmed public Node import resolves `file:///C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-n03/packages/deepviz/dist/index.js`; Python again imports own worktree source via explicit `PYTHONPATH`, using main's unmodified Python 3.12.16 interpreter.
- Command: `C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m pytest tests/test_cross_language_contract.py tests/test_schema_contract.py -q -p no:cacheprovider` with explicit own `PYTHONPATH`, `DEEPVIZ_TS_PACKAGE_ROOT`, `PYTHONDONTWRITEBYTECODE=1`.
- Result: exit **1**, **13 failed / 377 passed / 0 skipped**, 105.42s. Every failure is `test_python_chart_spec_matches_contract_corpus`, whose historical fixture expects coercion contrary to current authoritative `preserve_json_numeric_types` validator. The public npm-vs-current-Python comparisons did not fail.
- Exact failing case IDs: `version-true-coerces`, `max-points-string-coerces`, `max-points-decimal-string-coerces`, `width-string-coerces`, `width-decimal-string-coerces`, `width-whitespace-string-coerces`, `height-string-coerces`, `height-decimal-string-coerces`, `columns-string-coerces`, `columns-decimal-string-coerces`, `columns-true-coerces`, `dashboard-child-string-coerces`, `dashboard-child-version-true-coerces`.
- Owner handoff N12/C17: update/disposition historical corpus expectations against the already strict current Python model; these files are outside N03 ownership. N03 will not change validation to satisfy obsolete coercion assumptions.
- Following `npm run schema:check` in the same foreground batch hit the overall 120s tool timeout (exit 143) before finishing; no schema-check pass inferred. Later diff/status commands in that batch never ran. Next action: rerun that independent check and diff review with a sufficient timeout, then commit tested scoped changes.
