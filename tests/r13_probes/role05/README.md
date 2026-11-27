# Public render budget / output ownership probes

Independent NEW tests; no production code or existing oracle is edited.
Baseline target: published `5340bc69b7203ad7a9166543062482d819f9b705`.

From the checkout with an existing environment:

```powershell
$env:PYTHONPATH=(Join-Path (Get-Location) 'python/deepviz/src')
$env:PYTHONDONTWRITEBYTECODE='1'
$env:R13_EVIDENCE_DIR='NEW_LOCAL_ARTIFACT_ROOT/case-results'
python -m pytest tests/r13_probes/role05/test_preoutput_budget.py -q --tb=short `
  --basetemp NEW_LOCAL_ARTIFACT_ROOT/pytest-public -p no:cacheprovider
```

On that baseline: **20 failed / 10 passed**. These are real strict REDs, not
xfails. `AllocationReached` is a safe test-only tripwire, never a valid production
resource rejection. Native/figure and output-directory calls are instrumented
only within each call; normalization remains real. An actual budget `ValueError`
must occur before those boundaries and leave new output absent/caller files intact.

Cell fixtures: 128 sparse rows x128 union columns including headers =16,512 cells;
two80-row/80-column table children =12,960 request cells (6,480 individually).
They use only1,957 /1,181 compact source bytes. Small positives exercise all five
engines, preserve sentinel files and assert values/counts/warnings/strategies.

Optional baseline-only actual-output collection (Pillow required; uses the
completed positive renders, then two bounded uninstrumented ECharts calls):

```powershell
python tests/r13_probes/role05/collect_public.py NEW_LOCAL_ARTIFACT_ROOT
# Existing installed Node Playwright/Chromium, no installation:
$env:DEEPVIZ_NODE_DEPS_ROOT='checkout/with/existing/node_modules'
node tests/r13_probes/role05/capture_small.cjs NEW_LOCAL_ARTIFACT_ROOT/collection
```

Collector refuses existing output except explicit `--resume-existing`; that mode
reads completed artifacts without rerendering. The recorded recovery used this
mode after an own SVG-comment parsing assertion. Unpersisted timing/allocation
numbers are null; tracemalloc is **not RSS**. Browser controls are static companion
HTML only, with actual images/tables and zero external requests; no CDN claim.

For a future fix: wait for an actual R04 commit, pin that clean source on its own
PYTHONPATH and run the same NEW strict pytest tests. Do not copy dirty producer
source, weaken REDs, or run the baseline-pinned collector against a changed source.
No final signoff, full build/format/scale/MCP/DeepAgent gate or issue closure is
asserted by this narrow baseline report.
