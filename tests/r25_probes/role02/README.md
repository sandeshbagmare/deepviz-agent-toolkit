# R25 role02: independent MCP P2 mixed-reservation security review

Reviewed source: **e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23**.
P2 source commit: **cd75c459ddba9f3d6bc0a5185b570af369fb4980**.
One NEW missing-boundary test, not a replay of author6/P1author37/role10stdio.

From OWN probe/report checkout, existing installed virtualenv only. Set SOURCE to a
new clean detached e47 checkout. Its source must remain clean; no installs needed.

```powershell
$env:R25_02_SOURCE = (Resolve-Path $SOURCE).Path
$PY = (Get-Command python).Source
$env:PYTHONPATH = Join-Path $env:R25_02_SOURCE 'python/deepviz/src'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$env:MPLBACKEND = 'Agg'
$env:R25_02_RESULTS = Join-Path ([IO.Path]::GetTempPath()) ('r25-role02-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $env:R25_02_RESULTS | Out-Null
& $PY tests/r25_probes/role02/source_identity.py (Join-Path $env:R25_02_RESULTS 'source-before.json')
& $PY -m pytest -q -rs --tb=short -p no:cacheprovider --basetemp (Join-Path $env:R25_02_RESULTS 'pytest') --junitxml (Join-Path $env:R25_02_RESULTS 'mixed.xml') tests/r25_probes/role02/test_mixed_reservations.py
& $PY -m ruff check tests/r25_probes/role02
& $PY -m mypy --cache-dir (Join-Path $env:R25_02_RESULTS 'mypy') tests/r25_probes/role02
& $PY tests/r25_probes/role02/source_identity.py (Join-Path $env:R25_02_RESULTS 'source-after.json')
```

Check each actual exit. Fresh evidence/basetemp paths required; evidence refuses to
replace existing files. Missing MCP/Matplotlib/Vega packages are environment errors,
not skipped passes. Final observed: **1passed/0failed/0skipped3.16s/exit0**.

The real SDK test preloads124resources using Matplotlib4 plus60ECharts2 renders,
then races four workers behind a barrier: Matplotlib4, Vega3, ECharts2, ECharts2.
Read-only per-thread sys.setprofile observes actual ToolSession.render_chart entries,
so capacity-denied calls must not reach output allocation. No method, registry,
renderer, limit or return value is patched; no fake paths or private cache injection.

Allowed schedules produce128resources (Matplotlib4 or twoECharts2) or127(Vega3).
Exactly the accepted engine calls must enter rendering. All125priorfilehashes,
every newly issued resource, earliest URI bytes, host/outside sentinel and ordinary
normalization recovery are checked. A later two-resource request must reject with
no new file. No eviction/deletion/template or concurrency fairness is claimed.
Final actual schedule: twoEChartsaccepted, Matplotlib/Vegadenied,128total/fournewfiles.
Initial same-case execution choseMatplotlib4 and also passed; not two independentcases.

Own saved PNG was actually opened: Alpha3/Beta7, zero baseline/3:7height/fulltitle
and labels visible. No browser/CDN/Plotly/Vega paint or whole memory/RSS guarantee.

P1 controls are NOT rerun. Seven full paths d65=e47 (tools/core/models/recommend/
render/engines/P1test), four released paths cd75=e47; changed MCP module only its
ValidatedMCP admission class source is identical. See source-equivalence JSON.
R22-02-F1 bare-string callback admission gap remains OPEN by unchanged tools/SDK
bytes; old2RED6pass execution is not newly counted on e47 or a whole-MCP approval.

Report: docs/coordination/reports/R25-02-mcp-p2-security.md
Evidence: docs/coordination/evidence/R25-02/
No production/SDK/old-oracle/API/install/spawn writes or author/self-release approval.
