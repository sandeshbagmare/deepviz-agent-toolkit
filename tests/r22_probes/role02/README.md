# R22 role02: independent committed MCP P1 security controls

Exact production source: **d65dfc0fd807d0335b858476de8cdf7c6b958711**.
Run from this OWN probe/report checkout, not its older production source. Point
`SOURCE` at a separate clean detached d65 checkout, never the producer's dirty P2
worktree. Existing environment only: Python3.12.16, pytest, MCP1.30.0,
LangChain-core1.8.5 and Pydantic2.14.4 were observed; nothing installed.

## Portable PowerShell reproduction

```powershell
$env:R22_02_SOURCE = (Resolve-Path $SOURCE).Path
$PY = (Get-Command python).Source
$env:PYTHONPATH = Join-Path $env:R22_02_SOURCE 'python/deepviz/src'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$env:R22_02_RESULTS = Join-Path ([IO.Path]::GetTempPath()) ('r22-role02-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $env:R22_02_RESULTS | Out-Null
& $PY tests/r22_probes/role02/source_identity.py (Join-Path $env:R22_02_RESULTS 'source-before.json')
& $PY -m pytest -q -rs --tb=short -p no:cacheprovider --basetemp (Join-Path $env:R22_02_RESULTS 'pytest') --junitxml (Join-Path $env:R22_02_RESULTS 'security.xml') tests/r22_probes/role02/test_p1_security.py
& $PY -m ruff check tests/r22_probes/role02
& $PY -m mypy --cache-dir (Join-Path $env:R22_02_RESULTS 'mypy') tests/r22_probes/role02
& $PY tests/r22_probes/role02/source_identity.py (Join-Path $env:R22_02_RESULTS 'source-after.json')
```

Check each actual exit, not just the last command. Use fresh result/basetemp paths;
pytest owns its basetemp and evidence files reject replacement. The identity helper
checks exact commit, clean source, five Git/working byte pairs and four imports;
it also records actual installed SDK bytes/versions. No optional-dependency skips:
missing required packages are an environment error, not an independent pass.

## Expected result at this exact P1

**2 failed / 6 passed / zero skipped; pytest exit1, final1.72s.** The failures are
real strict findings, not xfails and not test-runner errors. Do not change the oracle.

- `test_all_supported_call_forms_admit_before_callback[bare-run]`
- `test_all_supported_call_forms_admit_before_callback[bare-arun]`

Public `run(raw, callbacks=[spy])` and `arun(raw, callbacks=[spy])` send invalid raw
strings to LangChain callbacks **before** later rejection. Three finite fixtures:
escaped duplicate key49bytes; Unicode JSON1,000,001UTF8bytes but999,994characters;
encoded5000depth/10,000bytes. No remote callback or secret is used: spy saves only
length/public-marker flag, not payload. Dictionary-form calls reject before callbacks;
bare valid exact1,000,000byte input and small recovery calls succeed. Thus bare strings
are a real supported call form, not a fabricated invalid invocation.

MCP four invalid cases enter SDK permissive JSON preparse **zero times**, ordinary
valid input once, measured by read-only `sys.setprofile` code-entry observation.
It restores the prior profile, retains no frames and patches no method. Canonical
escaped file/handle keys keep relative dict sources; decoded traversal/URL rejection,
local-file reread and untouched outside sentinel pass. No artifacts are rendered.

Source findings: `docs/coordination/reports/R22-02-mcp-p1-security.md`.
Compact observations/hashes: `docs/coordination/evidence/R22-02/`.
No original32/author37/fullsuite/stdio/browser/scale replay; role10 owns transport.
P2 registry capacity/lifetime/concurrency is not in this P1 and remains untested.
No production/source/oracle/SDK/cap changes, API writes, installations or final approval.
