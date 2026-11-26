# N05 Python renderer producer

- Status: starting scoped renderer/backend investigation, 2026-11-27.
- Owner/session: N05 child; runtime session ID not exposed in this conversation. Dispatcher: C17 only. No spawning.
- Main checkout: `C:\Users\bagma\deepviz-agent-toolkit` (report only).
- Assigned new worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n05`.
- Assigned branch: `fix/n05-python-render`; base/current source before creation: `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.
- Allowed source paths: `python/deepviz/src/deepviz/render.py`, `python/deepviz/src/deepviz/engines.py`, new scoped `test_n05*.py` regressions. Unique artifacts only under `artifacts/local/N05` or approved temporary directory.
- Prohibited: main source/Git candidate writes, shared venv changes, models/normalization/integrations edits, spawning, unrelated worktree edits.
- Observed main dirty paths: `AGENTS.md`, `opencode.json`, untracked `RESUME.md`, `docs/coordination/`; preserved untouched.
- Executed `git status --short --branch`, `git rev-parse HEAD`, `git worktree list --porcelain` in main; exit 0. Main source at assigned base, no N05 worktree yet.
- Acceptance: concrete failing renderer/backend regression first, smallest scoped correction, targeted and renderer/backend suites with explicit own `PYTHONPATH`/import identity, native artifact visual inspection, scoped commit and durable result evidence.
- Current action: read mandatory coordination/design/gates, then create assigned worktree.
- Next executable command: `git worktree add -b fix/n05-python-render C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n05 b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.

## Baseline checkpoint

- Created assigned new worktree/branch at exact base; `git worktree add ...` exit 0. No historical worktree changed.
- Interpreter: main `.venv\Scripts\python.exe`, Python 3.12.16; explicit `PYTHONPATH=C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n05\python\deepviz\src`, bytecode disabled. Printed `deepviz`, `deepviz.render`, `deepviz.engines` paths all resolve inside N05 source.
- Executed `python -m pytest python/deepviz/tests/test_render.py python/deepviz/tests/test_backend_plotly.py python/deepviz/tests/test_backend_vega.py python/deepviz/tests/test_backend_antv.py -q`; exit 1, **9 failed, 188 passed, 3 skipped**, 27.92 s. Full log `C:\Users\bagma\AppData\Local\Temp\opencode\N05-baseline-render.log`.
- Failures: Plotly line mode expected `lines` vs actual accessible `lines+markers`; Vega signed ARIA U+2212 numeric parsing, missing temporal x typing, missing bubble size title, heatmap ARIA mark query mismatch, SVG viewBox differs from outer dimensions, dashboard native payload mutated; AntV line test expects flat mark instead of accessible layered view; AntV HTML plain text U+2028/U+2029 test expects total absence.
- Ruling: do not remove accessible markers/layered AntV marks or alter correct Unicode numeric glyphs merely to satisfy structural assumptions. Investigate actual semantic failures and add independent scoped regressions. Existing tests remain untouched.
- Current action: TDD for Vega temporal spacing and preserve standalone dashboard child payloads; inspect mapped nonfinite/count behavior and available verifier findings.
- Next executable command: `Get-Content python/deepviz/tests/test_backend_vega.py` in N05 worktree, followed by scoped regression creation.

No fix or candidate signoff is claimed yet. Shared-contract, global scale/release and independent review remain outside this worker.

## TDD checkpoint 1

- New scoped regressions `python/deepviz/tests/test_n05_renderer_regressions.py` observed **8 failed** on unmodified production (exit 1; `N05-red.log`): all five adapters display zero instead of reduced no-color heatmap counts 3/1; Vega elapsed-time gaps render 1:1 instead of 29:1; size ARIA label fails to identify population; dashboard export removes standalone child schema/theme.
- Root causes: common channel `_heat` read categorical y instead of normalizer's `count`; Vega x typing only numeric/nominal; missing explicit mapped size title; dashboard composition pops keys from the same dicts later written to manifest.
- Smallest fixes in assigned source only: map no-color heatmap `count`, recognize valid ISO dates for continuous Vega mark x, use mapped size title, copy/filter dashboard composition child roots rather than mutate native payloads.
- Received C17 baseline mypy assignment; fixed renderer-local type inference using table column variable distinction, typed layout/charts, explicit actual-kind `str`, independently typed manifest warnings. No suppressions or contract changes.
- `python -m pytest python/deepviz/tests/test_n05_renderer_regressions.py -q`: **8 passed**, exit 0, 3.99 s.
- `python -m mypy python/deepviz/src/deepviz/engines.py python/deepviz/src/deepviz/render.py`: exit 0, no issues in 2 files, explicit own `MYPYPATH`/`PYTHONPATH`.
- Scoped Ruff found one import-block blank line in new test; corrected using patch, rerun pending.
- Full baseline `python -m pytest -q` timed out at 120 s (exit 143; progress at18%, no completed total). Preserved partial log `N05-baseline-full.log`; not a pass. Will rerun with a sufficient timeout after scoped fixes.
- Current source remains b6abc8d + only assigned production/test changes (uncommitted checkpoint).
- Next command: scoped renderer/backend pytest plus Ruff; generate native PNG/SVG temporal/count/dashboard artifacts for visual inspection before committing.

## Independent review findings checkpoint

- Read `C17-review-routing.md`, full N01 report and exact independent repro file; accepted N01 findings1–4 and N09 grouped-area same-spec semantic mismatch. No data/model edits.
- Added 38 additional scoped semantic cases, watched **38 failed, 8 passed** (exit1, `N05-red-review.log`): missing numeric gaps/omission disclosure across five engines and box/violin/pie/scatter/gauge, scalar histogram observation bins, supported Decimal replay, unsupported-value rejection, and actual scenegraph grouped-area baseline.
- Fixed common numeric channel to preserve null instead of zero; connected paths retain missing gaps, non-path geometry/statistics omit invalid observations with explicit per-child/artifact warnings. Matplotlib uses NaN only inside native line artists, never JSON. Heatmap invalid measures omit rather than invent zero. All retained normalized source records remain unchanged in manifests.
- Histogram implicit mapping now prefers observation numeric field over synthetic scalar `index`; finite observations alone are binned. Vega grouped areas explicitly disable implicit stacking to match other adapters' independent-zero baseline.
- Replay now canonicalizes supported Decimal/Real/Integral/date/time/numpy/Mapping values rather than `default=str`; unsupported objects raise before output creation. Full replay byte envelope still being added under routing row13.
- `python -m pytest python/deepviz/tests/test_n05_renderer_regressions.py -q`: **46 passed**, exit0,93.18s (`N05-green-review.log`). Subsequent combined tool timed out while running mypy, after reporting `_number` default return typing; added precise overloads (no behavioral change). Ruff/mypy rerun pending.
- Current action: replay byte-budget regression and canonicalization edge controls, actual native missing-gap visual verification, scoped/full test runs and commit.
- Next executable command: main interpreter with own PYTHONPATH runs mypy/Ruff for the two owned sources and new regression file; execute renderer/browser suites with sufficient tool timeout.
