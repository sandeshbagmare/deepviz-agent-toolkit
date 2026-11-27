# Independent committed MCP P2 acceptance

Read `docs/coordination/reports/R25-10-mcp-p2-capacity.md` and its source identity.
Target immutable **e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23**, whose production
bytes equal P2 **cd75c459ddba9f3d6bc0a5185b570af369fb4980**. This tester branch's
older product is deliberately not the import target.

Use a fresh exact-source detached checkout, existing dependencies read-only and
unique temporary output. Copy only this new test as untracked; do not replace
source or old tests, install dependencies, or change shared environments.

```powershell
$env:PYTHONPATH='<source>/python/deepviz/src'
$env:R25_PINNED_SOURCE='<source>'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:MPLBACKEND='Agg'
& '<existing-python>' -m pytest `
  python/deepviz/tests/test_r14_mcp_resource_budget.py -q -rs --strict-markers `
  --basetemp '<unique>/author6-tmp' --junitxml '<unique>/author6.xml'
& '<existing-python>' -m pytest tests/r25_probes/role10/test_resource_lifetime.py `
  -q -rs --strict-markers --basetemp '<unique>/novel3-tmp' `
  --junitxml '<unique>/novel3.xml'
```

The actual first run retained two passing SDK tests and one own overly specific
deep-error-message assertion failure; its full XML/log/initial test and exact
assertion-only diff are preserved. Only that stdio case was rerun after matching
the documented deep/nest/recursion error contract; no passed-case replay and no
claim of one nine-case green command. Do not replay historical commands to make
a nicer report.

The tests use actual SDK, all five renderer artifact alternatives, a six-thread
barrier race, and two real stdio processes. They check engine costs4/3/2, failed
reservation release, admission before new output, issued URI/read bounds, exact
128 lifetime resources, caller/earliest retention and host-created reset.
`observed.json`, actual PNG and manifest are retained; inspect the PNG, do not
accept artifact existence alone. One race is not a sustained-concurrency proof.

Optional MCP missing? Report the actual skip without installing/promoting it.
Zero selected skips is not Windows symlink-privilege proof. No browser/CDN,
DeepAgent provider planning, scale, packaging, full-MCP/CI or final-head approval.
P1d65 evidence may only be carried forward after explicit exact-source/hash and
unchanged guard-source proof; this suite does not replace independent security
review or final integrated checks.
