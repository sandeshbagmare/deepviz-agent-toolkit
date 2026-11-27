# Independent committed P1 transport acceptance

Target exact immutable product source
`d65dfc0fd807d0335b858476de8cdf7c6b958711`, not the older product on this
tester branch. Read the actual committed author test first, then run it unchanged
**once**; this new file covers only missing public `run`/`arun`, real SDK and
stdio combinations. No mocks of production, SDK dispatch or JSON parsing.

Using existing dependencies only, from a clean detached source checkout with
this new probe copied as an untracked file:

```powershell
$env:PYTHONPATH='<exact-source>/python/deepviz/src'
$env:R22_PINNED_SOURCE='<exact-source>'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:MPLBACKEND='Agg'
& '<existing-venv>/Scripts/python.exe' -m pytest `
  python/deepviz/tests/test_r14_tool_json_boundary.py -q -rs --strict-markers `
  --basetemp '<unique-own>/author37-tmp' --junitxml '<unique-own>/author37.xml'
& '<existing-venv>/Scripts/python.exe' -m pytest `
  tests/r22_probes/role10/test_transport_acceptance.py -q -rs --strict-markers `
  --basetemp '<unique-own>/novel4-tmp' --junitxml '<unique-own>/novel4.xml'
```

The four added tests exercise five bad requests each and valid Unicode recovery
after every bad request. Twenty bad-response observations are **not twenty extra
pytest tests**. Real callback observers verify invalid raw input rejects before
LangChain's callback bookkeeping, without replacing its implementation.

Each test retains `observed.json`; stdio also retains actual resources and a PNG
whose inline bytes must match its retrieved resource. Inspect the actual PNG,
read the manifest's literal values/counts and preserve compact sanitized evidence.
Optional dependencies missing? Report the actual skip; do not install or call it
a pass. No symlink test is selected. No P2 registry-capacity, paid provider,
DeepAgent planning, browser/CDN, full-MCP, package or CI claim follows.

Do not replay the old 47-case RED corpus, change old oracles/production, or poll
another worker's suite. This source-specific acceptance needs independent
security review and later committed P2/final-head gates separately.
