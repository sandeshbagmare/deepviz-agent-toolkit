# R30-20 exact commands and result ledger

Source-only. Working directory is existing OWN worktree `C:\Users\bagma\AppData\Local\Temp\opencode\r10-20-plotly-ses_de567801cffeGZFlt50oYv0Dnt`. Existing Python is `C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe`. No product imports, pytest collection/execution, SDK/server calls, stdio, browser, installs, CI poll or worker spawn.

## Immutable source inspection

```powershell
git status --short --branch
git rev-parse HEAD
git log -3 --oneline
git show -s --format="%H %P %s" e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23
git log --oneline --max-count=5 e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23
git diff --stat 5340bc69b7203ad7a9166543062482d819f9b705 e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23 -- python/deepviz/src/deepviz/tools.py python/deepviz/src/deepviz/mcp_server.py tests
git worktree list --porcelain | Select-String -Pattern 'r10-20|r14-18|mcp|e47f870|d65dfc0|cd75c45' -Context 0,2
git show --format=fuller --stat d65dfc0fd807d0335b858476de8cdf7c6b958711
git show --format=fuller --stat cd75c45
git diff 5340bc69b7203ad7a9166543062482d819f9b705 e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23 -- python/deepviz/src/deepviz/tools.py python/deepviz/src/deepviz/mcp_server.py
git ls-tree -r --name-only e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23 python/deepviz tests | Select-String -Pattern 'r14|mcp|tool|sdk|packag|integration|test_json|resource'
```

Two commands groups exit0. OWN HEADeb98261567d05300b9c7d79af78c83f04812c853 clean/tracking. No reset/worktree creation/producer-file writes. First diff-stat `tests` filter did not include nested author tests; corrected P1/P2 showstat and source inventory above/AST below include both NEW files.

```powershell
$sha='e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23'
foreach ($path in @('python/deepviz/src/deepviz/tools.py','python/deepviz/src/deepviz/mcp_server.py','python/deepviz/tests/test_r14_tool_json_boundary.py','python/deepviz/tests/test_r14_mcp_resource_budget.py','python/deepviz/pyproject.toml')) {
  Write-Output "===== SEALED $path ====="
  $i=0; git show "${sha}:$path" | ForEach-Object { $i++; '{0,4}: {1}' -f $i,$_ }
}
```

Exit1 ONLY last guessed path absent. Source/test207/146/178/164 lines were printed/read; root pyproject path corrected next, not a product failure. Same line-numbering pattern then read `pyproject.toml`, `__init__.py`, `render.py`, `recommend.py`, `cli.py`, `docs/architecture.md`: exit0. Strict normalize73-86 read via first140lines. Exact connected inspection:

```powershell
git grep -n -E '^(from|import) ' $sha -- python/deepviz/src/deepviz/normalize.py python/deepviz/src/deepviz/engines.py python/deepviz/src/deepviz/models.py
git ls-tree -r --name-only 0ae2cf26426822135fc10d337fcacf580b7ed833
git log --reverse --format="%H %s" 0ae2cf26426822135fc10d337fcacf580b7ed833..$sha -- python/deepviz/src/deepviz/tools.py python/deepviz/src/deepviz/mcp_server.py pyproject.toml
git grep -n -E 'ToolSession\(|create_server\(|create_tools\(|render_chart\(' $sha -- python/deepviz/src examples README.md
git grep -n -E 'files\(|resources/|plotly-js|read_prompt' $sha -- python/deepviz/src/deepviz/engines.py python/deepviz/src/deepviz/__init__.py pyproject.toml
git ls-tree -r --name-only $sha python/deepviz/src/deepviz
git show --stat --oneline 52b817d29eb1fc55538f5b7f8f30d1356e584223
git show --stat --oneline 65b3fc4a4202fd834a524bc2e0ab33c7430f179e
git show --stat --oneline 4a766c4a2dce49992c09cc4844492ccc6abd9460
git show --format=fuller --stat 1c721bb6497746641b897eb2eb938cfad52068d2
git show 1c721bb6497746641b897eb2eb938cfad52068d2 -- python/deepviz/src/deepviz/render.py
git show e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23:python/deepviz/src/deepviz/models.py
git log --reverse --format="%H %s" 0ae2cf26426822135fc10d337fcacf580b7ed833..5340bc69b7203ad7a9166543062482d819f9b705 -- python/deepviz/src/deepviz/normalize.py python/deepviz/src/deepviz/render.py python/deepviz/src/deepviz/engines.py | Select-Object -First 30
git show 0ae2cf26426822135fc10d337fcacf580b7ed833:pyproject.toml
```

All groups exit0. Native read/glob/grep also inspected exact installed MCP SDK server318-422/595-664, tools/base100-126, whole tool_manager/resources manager, func_metadata67-191, FunctionResource40-106; LangChain base758-819/1048-1109/1170-1237 and source symbol search. SDK source hashes/versions recorded without invoking these methods. FULL separate02 reports read only after own source trace, solely for known-finding dedup/limits; tests not reused.

Final exact provenance readback exit0: `git show 3051823906a2a869ab7ca941a21ef621ee994dd2 -- python/deepviz/src/deepviz/normalize.py | Select-Object -First 115`; `git show 715c1f5ca0c13c276110c64d2af8c21deca881ea -- pyproject.toml`; `git show f67afac5fb13a7950202671e858491856c72908d -- pyproject.toml`. Clarified report that305adds strict duplicate-key semantics, not the already-existing `_json` helper. Source/oracle-preservation `git diff --name-only eb98261567d05300b9c7d79af78c83f04812c853 -- python packages schemas tests prompts .github pyproject.toml README.md` empty, pre-stage index empty.

## Own static identity helper and checks

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe docs\coordination\evidence\R30-20\source_audit.py
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m ruff check docs\coordination\evidence\R30-20\source_audit.py
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m mypy --follow-imports=silent --ignore-missing-imports --cache-dir C:\Users\bagma\AppData\Local\Temp\opencode\r30-20-mypy-ses_de567801cffeGZFlt50oYv0Dnt docs\coordination\evidence\R30-20\source_audit.py
```

First actual chain: audit0/Ruff0/mypy1 ONE own helper `SimplePath` typing at103. Added ONLY `str(...)` around metadata locate_file result. Final exact chain: **audit0/Ruff0/mypy0 (1 own file)**. Final audit2026-11-27T16:18:05.475857UTC:12sealed Git blobs/8 SDK hashes, all12equalP2=e47, P1tools + MCPadmission AST equal,37+6declared author cases read/not executed. No DeepViz module was imported. two-file.diff exact Git bytes SHA25643c137868913c4a3914bcbe5d65e6941f5e189580830f3e28b890a0d413f69ea.

Totals: producttest0/SDKcall0/stdio0/browser0/newcounterexample0/APIwrite0/install0/spawn0. Skipped suites are explicitly NOT RUN, not passed/skipped test cases. No new source finding justified extra execution. No new bug ticket or #36 write.

## Publication

Fresh read-only identity preflight exit0 at2026-11-27T16:23:01.997929UTC. `git config --get-all credential.helper` returnedmanager; configured author present. Captured GCM output stayed in Python memory; exact `origin` HTTPS checked before credentials. GET`/user`, GET`/repos/sandeshbagmare/deepviz-agent-toolkit`, GET`/repos/sandeshbagmare/deepviz-agent-toolkit/git/ref/heads/agents/r10-20-plotly-literal-labels`:3HTTP200, expectedsandeshbagmare/exactrepo/ownremoteeb98261567d05300b9c7d79af78c83f04812c853. No API mutations/issues/PR/check polling, headers/tokens/redirectURLs persisted. Whitelist receipt`auth-before.json`. Native session_move confirmed SAME actualID before review.

Pending exact owned-path/source-oracle-preservation/whitespace/credential scan, meaningful small OWN commit/nonforce push and immediate actual remote-SHA readback. Sole owned branch is `agents/r10-20-plotly-literal-labels`; no shared/default/source integration authority. Final actual publication receipt belongs in own report/note/evidence, not a recursive follow-up commit requirement.
