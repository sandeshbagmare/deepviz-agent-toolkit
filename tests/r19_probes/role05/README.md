# Independent committed-budget retest

Target source: **1c721bb6497746641b897eb2eb938cfad52068d2**, in a new clean
detached source worktree. Publication branch retains its original source; use the
detached source's `python/deepviz/src` on PYTHONPATH. No producer dirty copy/merge.

1. Run the unchanged external R13 `test_preoutput_budget.py` from published
   `771cd9e3`. Recorded result: **30 passed /0 failed /0 skipped**,3.06s.
   All20 genuine budget rejects occurred before every allocation tripwire.
2. Run this directory's `test_policy_boundaries.py`. Recorded result:
   **8 passed /0 failed /0 skipped**,0.54s. Novel checks:10,000 inclusive-header
   single/combined request permitted,10,001 rejected; non-table accessible text
   budget checked before native/figure/output across all five engines.
3. `collect_retest.py ARTIFACT_ROOT` performs exactly two unmocked bounded public
   oversized rejects, retaining caller sentinels and requiring no new output.
   It reads the completed R13 small positives under
   `ARTIFACT_ROOT/pytest-unchanged-r13`; it does not rerender those controls.
4. Reuse unchanged R13 `capture_small.cjs ARTIFACT_ROOT/collection` with existing
   Node Playwright dependencies via `DEEPVIZ_NODE_DEPS_ROOT`. Both static companion
   HTML controls showed real images/tables with zero console/external errors.

```powershell
$env:PYTHONPATH='DETACHED_1C_SOURCE/python/deepviz/src'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:R13_EVIDENCE_DIR='NEW_ARTIFACT_ROOT/case-results'
python -m pytest tests/r13_probes/role05/test_preoutput_budget.py -q --tb=short `
  --basetemp NEW_ARTIFACT_ROOT/pytest-unchanged-r13 -p no:cacheprovider
python -m pytest tests/r19_probes/role05/test_policy_boundaries.py -q --tb=short `
  --basetemp NEW_ARTIFACT_ROOT/pytest-novel-boundaries -p no:cacheprovider
python tests/r19_probes/role05/collect_retest.py NEW_ARTIFACT_ROOT
```

Before/after exact Gitblob/import identity and immutable published old-probe hashes
are part of the report. No production/existing-oracle/R13 probe edits or installs.
No memory/latency benchmark, five-engine CDN execution, scale/MCP/DeepAgent/build
replay, later-head acceptance, final greenCI/release, or issue closure is asserted.
The exact10K positives stop safely at native entry; they are not10K image approval.
