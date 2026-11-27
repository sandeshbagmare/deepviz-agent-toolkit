# Independent R16 role02 SUM state/admission probes

Reviewed **ec9f669eff28cd5351da142765b7755e3b2f484f**, not this report branch's older
production bytes. Reports/probes stay on the owned security branch; production is a
separate clean detached source checkout. These are NEW small public safety controls,
not author23 exact-value tests, a benchmark, a renderer test, or final approval.

## Reproduce without installing dependencies

Use an existing environment with the project's declared dependencies, pytest, Ruff,
mypy, Node>=22 and TypeScript. Set SOURCE to a **clean detached** checkout of ec9f669;
set TOOLS to a checkout with existing node_modules. Never use a moving dirty source.
Run from this probe/report checkout in PowerShell:

```powershell
$env:R16_02_SOURCE = (Resolve-Path $SOURCE).Path
$PY = (Get-Command python).Source
$env:PYTHONPATH = Join-Path $env:R16_02_SOURCE 'python/deepviz/src'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$env:R16_02_RESULTS = Join-Path ([IO.Path]::GetTempPath()) ('r16-role02-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $env:R16_02_RESULTS | Out-Null
$env:R16_02_TS_BUILD = Join-Path $env:R16_02_RESULTS 'ts-build'
& (Join-Path $TOOLS 'node_modules/.bin/tsc.cmd') -p (Join-Path $env:R16_02_SOURCE 'packages/deepviz/tsconfig.json') --outDir $env:R16_02_TS_BUILD
& $PY tests/r16_probes/role02/source_identity.py (Join-Path $env:R16_02_RESULTS 'source-before.json')
& $PY -m pytest -q -rs --tb=short -p no:cacheprovider --basetemp (Join-Path $env:R16_02_RESULTS 'pytest') --junitxml (Join-Path $env:R16_02_RESULTS 'python.xml') tests/r16_probes/role02/test_sum_state_security.py
node --test --test-reporter tap tests/r16_probes/role02/test_sum_state_security.mjs
& $PY -m ruff check tests/r16_probes/role02
& $PY -m mypy --cache-dir (Join-Path $env:R16_02_RESULTS 'mypy') tests/r16_probes/role02
& $PY tests/r16_probes/role02/source_identity.py (Join-Path $env:R16_02_RESULTS 'source-after.json')
```

Fresh results/basetemp are required: pytest owns its basetemp, evidence files reject
replacement. Capture/check each real exit; do not combine the last command's exit
with all preceding commands. No remote data, installations, private cap changes,
producer's compiled output, source edits or patched reducer are needed. The identity
helper rejects wrong SHA, dirty source, wrong import and different Git/working bytes.
It hashes the own emitted JS; the JS test checks its actual source-map target.

## Scope and actual result

Windows/Python3.12.16/Node26.13.1/TypeScript7.0.2: **Python3 pass / TS5 pass / zero
failures or skips**, final2.77s/4439.0683ms; focused Ruff/mypy exit0 (2 own Pythonfiles).
Initial harness-only failures are preserved in the report; never product REDs.

- Near16MiB state with long allowed category values fits without promotion, then
  fails on promotion. Python510groups/1020rows rejects at561; TS255groups/510rows
  streaming rejects at427. Synchronous arrays are fully supplied: no early-read claim.
- 1000 unknown groups/4000rows merge into10 outputs, retain one other warning,
  expose only finite public fields and do not taint a fresh call. This public
  behavior plus source review is evidence, not direct V8 object-retention measurement.
- Python's existing integer-repr guard and TS's non-JSON BigInt guard reject a later
  row after promotion, without reading the next row. Python guard is never changed;
  a host with guard disabled/unusually large is an explicit skip for that one test.

Only small finite inputs were exercised. No safe-integer-count maximum, OOM, full
scale, full suite, browser, old32 MCP cases or author's23 cases were replayed.
16MiB is a retained payload/accounting budget, **not RSS**. Python tracemalloc measures
Python-managed allocations only; no V8 heap measurement or universal CPU cap claimed.

Review: `docs/coordination/reports/R16-02-sum-state-security.md`.
Evidence: `docs/coordination/evidence/R16-02/`.
