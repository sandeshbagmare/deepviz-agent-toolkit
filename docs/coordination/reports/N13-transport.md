# N13 — independent transport/Deep Agents/CLI tester

## Active checkpoint
- Owner: N13 delegated tester; session ID not supplied by runtime.
- Assigned baseline: `b6abc8d`; intended branch: `test/n13-transport`.
- Main checkout: `C:\Users\bagma\deepviz-agent-toolkit`.
- Intended new worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n13`.
- Allowed writes: this MAIN report; NEW transport regression tests and unique artifacts in assigned worktree only. No production edits, shared environment installs, spawning, integration, or GitHub writes.
- Source identity/current SHA/dirty state: verification pending; no source imported yet.
- First exact read: `docs/coordination/tasks/N13-transport.md` (success). Attempted `docs/coordination/C17-wave-common.md` returned file-not-found; located/read actual `docs/coordination/tasks/C17-wave-common.md` (success).
- Current action: read required project recovery/common-contract documents, inspect worktree state, and establish exact source/package identities.
- Next action: create assigned new worktree at `b6abc8d`, then exercise real MCP stdio initialize/list/call/resource/cleanup, security errors, five tools/chaining, real Deep Agents construction, and installed/source CLI.
- Acceptance: record exact commands and exit codes, actual pass/fail/skip counts and artifact semantics; visually inspect rendered output; save reproducible integration failures for N06 without production changes.

## Results
- Created assigned new worktree with `git worktree add -b test/n13-transport C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n13 b6abc8d` (exit 0). Source/base/current SHA: `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`; initial worktree clean. Existing worktrees preserved.
- Main status at start: `release/candidate`, ahead 20; modified `AGENTS.md`, `opencode.json`; untracked `RESUME.md`, `docs/coordination/`. N13 has not edited those other files.
- Required recovery/design/plan/gates/architecture and integration source/tests read. Common-contract path initial lookup failed (documented above); actual task file located.
- First import probe (main `.venv/Scripts/python.exe`, explicit own-worktree `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`) printed Python `3.12.16` and `deepviz.__file__ = C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n13\python\deepviz\src\deepviz\__init__.py`. Version-list comprehension then exited 1 on missing Python distribution `playwright`; this is a probe limitation, not a transport failure or skip. Will record available versions without aborting and use existing npm browser tooling if available.
- Next executable action: run existing real-stdio/Deep Agents integration tests on exact baseline with persistent unique artifacts, then add independent lifecycle/chaining/CLI regressions.

### Baseline transport/integration execution
- Exact command in N13 worktree (PowerShell): `$env:PYTHONPATH='<N13>\python\deepviz\src'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; $env:MPLBACKEND='Agg'; & '<MAIN>\.venv\Scripts\python.exe' -m pytest python/deepviz/tests/test_integrations.py python/deepviz/tests/test_mcp_transport.py -ra --basetemp artifacts/local/N13/baseline-pytest --junitxml artifacts/local/N13/baseline-junit.xml 2>&1 | Tee-Object artifacts/local/N13/baseline-pytest.log; exit $LASTEXITCODE`.
- Exit 0: **44 passed, 1 skipped, 76.94 s**, Python 3.12.16, pytest 9.2.0. Skip is real Windows symlink privilege `WinError 1314`, not a security pass.
- Includes actual SDK stdio initialize/discovery, all five render calls and resource retrieval, invalid spec/resource/traversal rejection, Unicode protocol-only stdout and graceful process exit, real `create_deep_agent` local chat-model execution, tool workflows and CLI errors. Existing tests are baseline evidence; independent new checks below remain pending.
- Logs/JUnit and original server-rendered files persist in `<N13>/artifacts/local/N13/` (all untracked/ignored artifacts, no production edits).
- Browser dependency discovery: `node -e "...require('<MAIN>/node_modules/playwright')..."` exit 0; Node `v26.13.1`, npm Playwright `1.65.1`, Chromium executable `C:\Users\bagma\AppData\Local\ms-playwright\chromium-1255\chrome-win64\chrome.exe`. No package installs performed.
- Current action: create NEW independent N13 tests for one-session five-engine normalization→recommendation→render/resource chaining with exact semantic oracles, cache/session lifecycle, trust-boundary errors, installed entry-point/source CLI and real Deep Agents five-engine chain. Then visually inspect retrieved artifacts.

### Independent acceptance v1 — PASS on baseline, visual/browser follow-up pending
- Added only NEW `python/deepviz/tests/test_n13_transport_acceptance.py` in N13 worktree (no production edits).
- Exact command: same explicit own-worktree environment as above, main venv `python -m pytest python/deepviz/tests/test_n13_transport_acceptance.py -vv -ra --basetemp artifacts/local/N13/independent-pytest-v1 --junitxml artifacts/local/N13/independent-v1-junit.xml`, tee `artifacts/local/N13/independent-v1-pytest.log`.
- Exit 0: **21 passed, 0 skipped, 91.24 s**. One real stdio process handles normalization, recommendation and all five renderer calls, fetches every resource, checks bytes against actual server files, unique/discoverable URI registrations, PNG inline/resource equality and graceful process exit 0.
- Oracle input: Alpha 2 + Alpha 5, Beta 11, Gamma -3. All five MCP-retrieved manifests contain exactly Alpha **7**, Beta **11**, Gamma **-3**, `input_count=4`, `output_count=3`, `strategy=sum`, requested/rendered bar with category/amount mappings. Normalization/recommendation return a reusable handle/profile, not raw rows. MCP results omit filesystem `paths`.
- Cache/session tests: 33 handles evict oldest from 32-entry cache; expired normalize/recommend/render fail; last handle works; new server cannot reuse old dataset/resource. Default server denies absolute/traversal/URL/path-string file attempts and `file://` / traversal resource URIs; sentinel raw file contents never returned.
- Real `deepagents.create_deep_agent` graph (not mocked) executes actual seven StructuredTools in order: normalize, recommend, five renders. Deterministic local `BaseChatModel` needs no credentials. All statuses success and all five actual artifact manifests match independent aggregation oracle.
- Both source-module CLI and installed `.venv/Scripts/deepviz.exe` with explicit N13 `PYTHONPATH`: normalize/recommend/render success JSON, six error classes each exit 2, no traceback/stdout/chart. Installed executable is editable/source-selected evidence, **not** clean-wheel consumer evidence.
- Exact source/versions and production SHA256s persisted at `<N13>/artifacts/local/N13/source-identity.json`. MCP 1.30.0; deepagents 0.7.42; langchain-core 1.8.5; langchain 1.5.2; langgraph 1.2.24; pydantic 2.14.4; Matplotlib 3.11.2; Plotly 6.9.0; vl-convert 1.9.0.post1; pyarrow 26.0.1. Main venv unmodified.
- Retrieved artifact root: `<N13>/artifacts/local/N13/independent-pytest-v1/test_n13_one_stdio_session_fiv0/retrieved/{matplotlib,plotly,vega,echarts,antv}/`. `calls-and-retrieval.json`, `initialize.json`, `tools.json`, `cleanup.json`, server stderr retained beside it.
- Direct visual inspection of retrieved `matplotlib/chart.png`: three blue bars Alpha=7, Beta=11, Gamma=-3 extending below visible zero; x label category, y amount, readable unclipped labels. Actual title is recommendation default “Visualization,” as expected from returned recommendation (not original input SPEC).
- No confirmed integration defect to hand to N06 yet. Current action: browser-open MCP-retrieved HTML and independently inspect visible marks/axes/console errors, then lint new tests and checkpoint scoped commit.
