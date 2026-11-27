# R10 role02 independent security probes

These are strict tests, not production fixes or final signoff. Reviewed checkpoint:
`3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`. All product source is unchanged on this branch.

## Reproduce

Use an existing environment with the project, pytest, and the declared `agents`/`mcp`
extras installed. No test installs dependencies or fetches remote data. From the repo
root, select that environment's Python; this PowerShell recipe uses `python` on PATH:

```powershell
$PY = (Get-Command python).Source
$env:PYTHONPATH = (Resolve-Path 'python/deepviz/src').Path
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$env:MPLBACKEND = 'Agg'
$out = Join-Path ([IO.Path]::GetTempPath()) ('r10-role02-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $out | Out-Null
& $PY tests/r10_probes/role02/source_identity.py (Join-Path $out 'source.json')
& $PY -m pytest -q -rs --tb=short --basetemp=(Join-Path $out 'pytest') --junitxml=(Join-Path $out 'junit.xml') tests/r10_probes/role02
& $PY -m ruff check tests/r10_probes/role02
& $PY -m mypy --cache-dir=(Join-Path $out 'mypy') tests/r10_probes/role02
```

Always use a fresh output directory: pytest owns and clears its supplied basetemp.
The source guard rejects accidentally testing the shared editable MAIN installation.
The code has no machine-specific Python/worktree path. Platform-neutral path objects
are used; no symlink privilege, shell from a specification, browser, remote request,
private source, credential or paid model is needed. Stdio starts the same interpreter
with an explicit source PYTHONPATH. Optional dependency absence is an explicit skip,
not a pass. The identity helper itself requires the documented extras.

## Actual checkpoint outcome

Windows/Python3.12.16, MCP1.30.0, LangChainCore1.8.5, Pydantic2.14.4:
**22 passed / 10 failed / 0 skipped**, 8.31s, pytest exit1. Ruff exit0; mypy exit0
(four own files). The earlier 30-case run is overlapping, not additional coverage.

- 14 novel controls pass: reference-looking cells stay data without file authority;
  literal percent-encoded filenames are not decoded as URLs; sibling-root prefixes
  do not pass containment; original/copied file handles recheck missing/directory
  sources before allocating output; exact URI issuance is server-local; registered
  oversize/missing/directory artifacts reject before bulk reads and recover without
  breaking their peer resource.
- Six duplicate-key failures: data fields and file-control keys across ToolSession,
  LangChain and the actual SDK. The core normalizer positive rejection control passes.
- Two SDK plus two real-stdio failures: a greater-than1,000,000-byte padded JSON string
  is decoded before the tool's raw-byte check. Direct/LangChain checks reject it;
  real MCP responds isError=false. Small row/JSON/file controls pass.

Keep these regressions strict. Do not add xfail, truncate input, raise the budget,
weaken the duplicate-key oracle or call this RED branch green. R04 owns integration
and production fixes. After a fix, independently rerun against its exact source SHA.

Full review/evidence: `docs/coordination/reports/R10-02-security-boundaries.md` and
`docs/coordination/evidence/R10-02/`. The unchanged R03 report preserves separate
baseline renderer/memory/browser findings; this follow-up does not duplicate role20.
