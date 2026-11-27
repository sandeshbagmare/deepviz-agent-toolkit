# N17 independent adversarial boundary QA

- Status: in progress, 2026-11-27. Owner: N17 child of C17; actual session `ses_de6d39a86ffee58AlO2c44vVZy` returned by session_move.
- Assignment: `docs/coordination/tasks/N17-boundaries.md`; common contract: `docs/coordination/tasks/C17-wave-common.md`.
- Main checkout: `C:\Users\bagma\deepviz-agent-toolkit`; production read-only.
- Assigned worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n17`; branch `test/n17-boundaries`; base/current `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`. Created successfully with git worktree add, exit 0; session moved here. `git status --short --branch` exit 0: clean.
- Allowed writes: this MAIN report; NEW scoped `test_n17*.py` / JS adversarial regression tests and unique `artifacts/local/N17` in assigned worktree. No production changes, shared venv installs, spawning, integration, push, or GitHub writes.
- First completed commands: read assignment/common contract/RESUME/STATE. `git status --short --branch` (main), exit 0: `release/candidate` ahead 20, modified AGENTS.md/opencode.json and untracked recovery documents; preserved unchanged.
- Current action: inspected normalize.py/render.py/tools.py/mcp_server.py and TS normalize/render boundaries. Preparing bounded byte, replay, path, and escaping regression probes.
- Next action: create scoped `python/deepviz/tests/test_n17_boundaries.py` and run with main interpreter plus explicit own PYTHONPATH.
- Environment command exit 0: Python 3.12.16; `deepviz.__file__` points to this worktree `python/deepviz/src/deepviz/__init__.py`; pytest/mcp/numpy/vl_convert/plotly available, Python playwright absent. No shared environment modification.
- `npm ci` in OWN worktree timed out after 120 s, exit 143; not a pass and no source changes. Will use existing main read-only compiler/runtime dependencies if own install remains incomplete, documenting exact source identity.
- No product result, security pass, or approval claimed.

## First substantive execution / findings (baseline b6abc8d)

Command (own worktree): `$env:PYTHONPATH='<own>/python/deepviz/src'; $env:PYTHONDONTWRITEBYTECODE='1'; & '<main>/.venv/Scripts/python.exe' -m pytest python/deepviz/tests/test_n17_boundaries.py -q -s`.

**Actual exit 1: 3 failed, 26 passed, 1 skipped, 8.37 s.** Unmarked failing regressions are deliberately preserved; no xfail or synthetic passing status.

1. **N17-F1 P1 correctness, owner N05:** `python/deepviz/src/deepviz/render.py:49-55`, especially `json.dumps(... default=str)` at 54. `test_n17_dashboard_decimal_replay_preserves_supported_scalar_semantics` fails: two supported Decimal values 2.5/3.5 sum to 6.0 via normalizer/list but iterator-dashboard replay serializes them to strings and produces `v=None` instead of 6.0. This is a supported typed-Python input semantic defect, **not** arbitrary filesystem authority. Baseline test source line 172-182.
2. **N17-F2 P2 resource cleanup, owner N06 (N05 renderer cleanup subcase):** `tools.py:140-150` creates per-call destination before render, with no failure cleanup. `test_n17_failed_tool_render_does_not_accumulate_orphan_directories` leaves `out/echarts-*` after missing-field rejection. `test_n17_artifact_limit_rejection_reclaims_its_own_files` safely lowers only the test's artifact cap to 100 bytes; rejection leaves complete generated HTML/manifest and both directories. The real 16 MiB cap is **not** stress-tested by lowering it, but the actual failure path demonstrably fails to reclaim its own disk state. Baseline test lines 209-227.
3. **N17-O1 open byte-envelope observation, owners N04/N05:** `normalize.py:333-335,352-379,539-559` retains arbitrary cell/key lengths. Three cells (131072 emoji each) produce **1,572,933 UTF-8 JSON bytes with no warning**, despite max_points=10; one key of **131072 bytes** also survives with no warning. This is measured bounded input, not an OOM attempt; no invented numeric rejection contract. Existing row/field/depth caps do not establish byte safety. Need source-owner agreed byte policy and pre-serialization budget, then independently rerun.

Passing checks are narrow: width 1024/1025 and cumulative schema width; depth/cycle rejection; 1000-row high-cardinality exact sum and retained group oracle; 10 model path traversal/drive/URL cases; string-vs-explicit-Path and explicit allowed file reference; 32-handle expiry/renewal; inline UTF-8 byte limit; script JSON and HTML parsing attacks for four native engines; failed replay spool removed; unique output paths preserve sentinel. These are not blanket security acceptance.

One skip: Windows host denied `os.symlink` privilege; symlink containment remains unverified until directory-junction or capable-host check. Chromium 159.0.8154.6 launched from own partially installed node_modules (exit 0). Own TypeScript successfully compiled with main's read-only `node_modules/typescript/bin/tsc -p packages/deepviz/tsconfig.json` (exit 0); next: independent actual browser hover/injection and TS byte/dashboard probes.
