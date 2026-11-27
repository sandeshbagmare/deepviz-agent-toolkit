# N04 Python ingestion producer — active checkpoint

- Owner: N04 child of C17; runtime session ID not exposed in this child context.
- Assignment: `docs/coordination/tasks/N04-python-data.md`; common contract `C17-wave-common.md`.
- Date: 2026-11-27.
- Main observed source: `release/candidate`, `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.
- Main dirty paths observed (preserved): `AGENTS.md`, `opencode.json`, `RESUME.md`, `docs/coordination/`.
- Intended own worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n04`.
- Intended own branch/base: `fix/n04-python-data` / `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.
- Allowed source: `python/deepviz/src/deepviz/normalize.py`; new `test_n04*.py` normalization regression tests only. This main-checkout report is the sole coordination write.
- Forbidden: other main source, shared venv/package installs, models/renderers/tools/schema/root edits, spawning, full-scale benchmarks owned by N11.
- Acceptance: reproduce current concrete normalization defects RED; implement smallest allowed fixes; targeted regressions GREEN; run existing normalization/statistics/GraphQL/format coverage and scoped lint/type checks; commit only tested allowed paths and report hash. Disclose counts, loss and sampling semantics for N03/N12.
- Commands already run: read assignment/common contract, RESUME, AGENTS, STATE; `git status --short --branch; git rev-parse HEAD; git worktree list --porcelain` (exit 0). No source changes or product checks yet.
- Current action: read required coordination/design/dependency instructions, then create new isolated worktree.
- Next executable command: `git worktree add -b fix/n04-python-data C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n04 b6abc8d` (from main root, after required instruction reads).
- Blockers: none observed.

## 2026-11-27 baseline checkpoint

- Created own worktree/branch with `git worktree add -b fix/n04-python-data C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n04 b6abc8d` (exit 0), clean base `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.
- Required coordination/design/plan/dependency instructions read. Loaded ponytail, systematic-debugging, TDD, Python best-practices and executing-plans guidance. Ruling: assignment's sole durable main report replaces generic skill scratch ledgers; no fresh reviewer is spawned because this lane explicitly prohibits spawning and independent N01/N02/C17 review exists.
- Set `PYTHONPATH=C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n04\python\deepviz\src` and `PYTHONDONTWRITEBYTECODE=1`; main interpreter identifies Python 3.12.16 and imports own `deepviz/__init__.py` and `normalize.py`.
- Baseline command: `C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m pytest python/deepviz/tests/test_normalize.py python/deepviz/tests/test_aggregation_semantics.py python/deepviz/tests/test_graphql_contract.py -q` (own worktree). Exit **1**, **1 failed / 124 passed / 0 skipped**, 9.65s. Full log `C:\Users\bagma\AppData\Local\Temp\opencode\N04-baseline.log`.
- Concrete existing RED: `test_sum_preserves_small_residual_under_large_cancellation_with_documented_tolerance`; `[1e16,1.0,-1e16]` gives `0.0`, `math.fsum` reference `1.0`. Root cause naïve repeated addition in `_Reducer.add`; integer control retains 1.
- Independent N01 finding accepted for reproduction: selecting `data_path` discards GraphQL partial-error metadata before `_expand` sees it. Will add own `test_n04*` regressions, preserve row counts and deterministic one-warning accounting.
- Current action: add bounded compensated-sum and path-disclosure RED tests before any production edit.
- Next executable action: run new `python/deepviz/tests/test_n04_normalize_regressions.py` using the same interpreter/PYTHONPATH, then implement smallest confirmed fixes.

## RED→GREEN checkpoint

- Added only own `python/deepviz/tests/test_n04_normalize_regressions.py`. Before implementation, new regression run exit **1**: **8 failed / 1 passed / 0 skipped**, 1.17s; log `C:\Users\bagma\AppData\Local\Temp\opencode\N04-red.log`. Concrete failures: repeated float cancellation, evicted/overflow-state compensation, three selected paths suppressing partial-error warning, paginated warning suppression, and error-only envelopes yielding the wrong error or returning error objects as successful data.
- Small fixes in own `normalize.py`: a constant-size Neumaier compensation term for sum states, preserved when the last retained group is moved into the other bucket; shared GraphQL error accounting used during nonterminal path traversal and normal expansion. Existing integer-exact and non-finite→null policies preserved. No schema/API or inference/sampling changes.
- GREEN command: same interpreter, own `PYTHONPATH`, `python -m pytest python/deepviz/tests/test_n04_normalize_regressions.py python/deepviz/tests/test_normalize.py python/deepviz/tests/test_aggregation_semantics.py python/deepviz/tests/test_graphql_contract.py -q` (own worktree). Exit **0**, **134 passed / 0 failed / 0 skipped**, 14.32s. Log `C:\Users\bagma\AppData\Local\Temp\opencode\N04-green.log`.
- Semantics for N03/N12: float sum tracks one extra correction per group; integers remain integers. Group-cap overflow still keeps first `max_points-1` exact groups and merges all remaining observations into one warned other bucket; compensation transfers with evicted state. `data_path` now preserves one GraphQL partial-error count per encountered envelope before selection strips metadata; error-only GraphQL envelopes fail consistently even when a path selects `errors`.
- Current action: run scoped Ruff/mypy and full ordinary project suite. Ruling: explicitly exclude existing `scale` marker because assignment forbids duplicating N11's 100K/1M/10M benchmark lane; report deselection, not a full-scale pass.
- Next executable command: `python -m pytest -m 'not scale' -q` with own `PYTHONPATH`, shared interpreter, own worktree.

### Ordinary-suite timeout (not a pass)

- `python -m pytest -m 'not scale' -q` exceeded the foreground **120s** tool limit, exit **143/SIGTERM**. Partial log `N04-suite.log` shows 10% completion, at least nine failures and one skip but no final test totals or failure names yet. No release/suite success claimed. Process check found no remaining N04 pytest process.
- Next action: rerun ordinary suite as one background job with completion notification, while running only scoped static checks and inspecting the two changed files. Do not poll or duplicate this job.

### Static-check checkpoint

- Ordinary suite background job started (shell `sh_21931f34d001NzuCth1pFJyvaU`); waiting for automatic completion, not polling.
- First static batch: `python -m ruff check python/deepviz/src/deepviz/normalize.py python/deepviz/tests/test_n04_normalize_regressions.py` exit **1** (new test import spacing); `python -m mypy python/deepviz/src/deepviz/normalize.py` exit **1** (mypy does not narrow mutable `state[1]` through `abs`); `git diff --check` exit **0**.
- Corrected only import grouping and bound `previous=state[1]` for stable type narrowing, no numeric/path behavior change. This occurred after the background suite started: that run is diagnostic on the dirty implementation, not immutable final-source signoff. Final targeted checks will rerun after all edits.
- Next action: rerun scoped static checks, inspect regression coverage and independent findings; await background completion automatically.

## C17 routing / next bounded fixes

- Read `tasks/C17-review-routing.md`: N01 warning and cancellation findings explicitly owned here; mean accuracy and normalizer byte envelope also assigned. Strict numeric JSON model policy remains unchanged; stale coercion fixtures are C17-owned.
- Ruling / counterpart handoff to N03, N05, N12: reject oversize input rather than silently truncate. Proposed internal envelope implemented/tested next: **1 MiB UTF-8 per string cell**, **4 KiB UTF-8 per flattened field name**, **2 MiB compact UTF-8 JSON per record**, **16 MiB compact UTF-8 JSON retained output**. Apply retained budget incrementally to reservoir/retained grouping states and final output, not cumulatively across the entire consumed stream. Large valid streams remain streamable; byte-oversize cells/records raise an explicit ValueError. Already-allocated host inputs and JSON decoding are distinct memory limits, not covered by a retained-output claim.
- Current targeted Green remains 134; static retry Ruff exit0, mypy exit1 because the numeric `row.get` value retains Optional typing after exact-type validation. Will make the existing null guard explicit without widening runtime numeric types.
- Next actions: reproduce mean cancellation and output byte-envelope violations in own regression tests, implement bounded fixes, rerun targeted tests/static checks and commit allowed files. N11 owns scale verification; no benchmark duplication or model changes.

- Second RED run: `python -m pytest python/deepviz/tests/test_n04_normalize_regressions.py -q` exit **1**, **7 failed / 11 passed / 0 skipped**, 2.57s; log `N04-red-bytes-mean.log`. Mean `[1e16,1,-1e16]` actually returns **-0.5** instead of `1/3`; 1MiB+ ASCII/UTF-8 cells, 4KiB+ field name, 2MiB+ multi-cell record and 16MiB+ retained sampling/group-key states are currently accepted. Overflow-safe mean and reducible >16MiB total-stream controls already pass and must remain passing.
