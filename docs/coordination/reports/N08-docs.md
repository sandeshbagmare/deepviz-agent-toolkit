# N08 documentation/examples producer report

- Owner: N08 subagent; runtime session ID not supplied.
- Assignment: `docs/coordination/tasks/N08-docs.md`; common contract `docs/coordination/tasks/C17-wave-common.md`.
- Main checkout: `C:\Users\bagma\deepviz-agent-toolkit`.
- Assigned worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n08` (created clean).
- Assigned branch: `docs/n08-delivery`; base/current: `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835` before docs edits.
- Allowed source paths: `README.md`, `docs/architecture.md`, `docs/capabilities.md`, `docs/research/**`, `prompts/v1/**`, `examples/**`, excluding existing dirty sibling copies.
- This report is the only main-checkout write. No product source, other coordination/process documents, main Git candidate operations, or subagent launches.

## Current action and next command

- Current action: scoped example fix and real deterministic Deep Agents example are green; source-backed capability/README/prompt corrections drafted. Full baseline pytest is running in background once, not polled.
- Next command: run the updated three examples into `artifacts/local/N08/verified-*`, inspect downloaded/static/browser outputs, finish the research addendum and run scoped Ruff/docs checks before commit.
- Acceptance checks: independently execute documented examples using main virtualenv with explicit worktree `PYTHONPATH` and imported source identity; validate changed documentation against actual implementation and primary official sources; inspect real renderer output; commit only allowed scoped files and record exact commands, exit codes, test totals, limitations, and commit SHA here.

## Evidence

- Read assignment and common wave contract. Common contract first attempted at coordination root (not found), then located/read under `tasks/`. No source edits yet.
- Required RESUME/AGENTS/STATE/BRIEF/REQUEST/C17 task/report/design/plan/dependency context read. Main Git status: candidate `b6abc8d`, modified `AGENTS.md`, `opencode.json`, untracked recovery/coordination records; preserved. `git worktree add -b docs/n08-delivery C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n08 b6abc8d` exit 0.
- Baseline commands used main `.venv\Scripts\python.exe`, `$env:PYTHONPATH = "$PWD\python\deepviz\src"`, `$env:PYTHONDONTWRITEBYTECODE = '1'` from assigned worktree. Import identity printed own `python/deepviz/src/deepviz/__init__.py`. Python 3.12.16; deepagents 0.7.42, langchain-core 1.8.5, mcp 1.30.0, matplotlib 3.11.2, plotly 6.9.0, vl-convert-python 1.9.0.post1.
- `python -c "...; print(len(deepviz.read_prompt('system')))"` exit 1: `resources/prompts/v1/system.md` absent. Root build config only force-includes schema, contrary to README/prompts claim that source installation includes prompts. **N07-owned packaging blocker; no product/root-config edits here.** Will correct prose to mark source prompt use explicitly until packaging owner fixes it.
- `python examples/multi_tool_flow.py --output-dir artifacts/local/N08/baseline-tools` exit 0, all seven real StructuredTools returned, 3 input/3 output records, sum strategy; ECharts/AntV CDN warnings. Artifacts retained in named directory. No browser rendering pass claimed.
- `python examples/mcp_client.py --output-dir artifacts/local/N08/baseline-mcp` exit 0, seven tools discovered, two render calls and six resource reads succeeded. Source inspection found copied static `chart.html` references `chart.svg` but example renames that resource `matplotlib-1-chart.svg`, breaking the downloaded companion preview. Scoped example fix follows a failing reproducer.
- `python examples/deep_agent.py --help` exit 0; no live model invocation/credentials attempted. A deterministic real-graph example is planned so attachment can be exercised without a provider.
- Shell combined baseline ended exit 0 because final help succeeded; individual prompt failure is preserved above, not hidden by aggregate exit code.
- Ruling: assigned MAIN report is the durable task ledger; no additional global-plan workspace/process files. No child reviewer launch is permitted by assignment; N15 owns independent source/research audit.
- RED: `python -m pytest examples/test_examples.py -q` exit 1, **1 failed** (`test_mcp_download_keeps_static_preview_sibling_links`), actual real-MCP download missing sibling `chart.svg`. Minimal fix preserves safe server basenames in unique per-engine client directories, rejecting non-basename resource names and retaining exclusive file creation.
- Next RED after adding local-example acceptance: same command exit 1, **1 failed, 1 passed**; missing `deep_agent_local.py` executable. Added deterministic `BaseChatModel` example attached to real `create_deep_agent`, using approved temporary CSV, real handle chain, source policy and metadata output. This is not an LLM-quality/provider test.
- GREEN: same command exit 0, **2 passed in 25.37s**. Both graph/MCP subprocesses ran against explicit N08 `PYTHONPATH`. `python -m ruff check examples` initially exit 1, one preexisting unsorted nested import in edited `deep_agent.py`; fixed import spacing, rerun pending.
- Updated `deep_agent.py` with explicit trusted `--policy-file` checkout option, and multi-tool example now uses/overrides actual recommendation spec before rendering alternatives.
- Drafted matrix at exact base: 17 non-dashboard kinds, five explicit fallbacks (Vega radar->line/sunburst->pie/gauge->bar; ECharts/G2 violin->box), flat hierarchy, coordinate-only geo, bounded-row statistics, exact Python CDN versus bundled asset behavior. Source-observed important caveat: baseline `channels()` maps missing/non-numeric y to zero; N05 renderer QA should disposition, not documentation concealment.
- An initial multi-hunk capabilities patch failed exact-context matching (Unicode multiplication character differed); re-read unchanged file and applied corrected scoped patch successfully. No partial write carried forward.
- Background command launched once: `python -m pytest > artifacts/local/N08/full-pytest.log 2>&1` with N08 source identity/environment. Shell ID `sh_219398dd4001TeNTN9KfZruKoh`, PID 14272. Result not yet received; no suite pass claimed.
- Primary docs re-fetched 2026-11-27: `https://docs.langchain.com/oss/python/deepagents/customization` (tools/model instance/system_prompt contract) and official SDK `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/v1.x/docs/server.md` (resource reading/binary transport/error semantics). Existing 100-URL research inventory left separate, not inflated by repeats or claimed as >100 repositories.
- Visually inspected actual baseline Matplotlib PNG: exactly Jan/Feb/Mar bars at 12/18/15, zero baseline, correct month/revenue axes/title, no clipping. Browser/other renderer visual acceptance pending rather than inferred from file creation.
