# R16 role16: mean/column producer followups, NOT a source fix

NEW strict tests for known representable-subnormal mean loss and Python/TS wrapper-like scalar-column parity. Python uses `Fraction.from_float` and separately checked literal rounded means. JS uses the same finite binary64 fixtures and literal mathematical results, not the production reduction algorithm. Both record and one-pass stream mean paths are checked; explicit-path/custom/multicolumn/record-wrapper controls protect supported semantics.

Source baseline is immutable `ec9f669eff28cd5351da142765b7755e3b2f484f`, normalizers handed back to R04. No production/old-test edit, new SUM algorithm, GraphQL-page/path-collision/prototype test duplication, ownership64test replay or scale claim.

In a clean isolated source checkout (with existing tooling, no install), build TypeScript and set:

```powershell
$env:DEEPVIZ_R16_SOURCE='<absolute clean source checkout>'
$env:DEEPVIZ_R16_EXPECTED_COMMIT='ec9f669eff28cd5351da142765b7755e3b2f484f'
$env:PYTHONPATH=Join-Path $env:DEEPVIZ_R16_SOURCE 'python/deepviz/src'
$env:PYTHONDONTWRITEBYTECODE='1'
node <existing-typescript>/bin/tsc -p (Join-Path $env:DEEPVIZ_R16_SOURCE 'packages/deepviz/tsconfig.json')
python -m pytest tests/r16_probes/role16/test_mean_scalar_followups.py -q -p no:cacheprovider
node --test tests/r16_probes/role16/mean-scalar-followups.test.mjs
```

Tests may live in the owned probe branch while product imports/build come from the explicitly selected detached source. Guards require exact selected commit and Python/TS source Git bytes; published evidence records built JS/test hashes and loaded module path. For an authorized fixed source, deliberately set BOTH source path and expected commit, rebuild that checkout and preserve probe bytes. No expected failure/skip hides a defect. Zero-sign policy, ambiguous nested/null column inference, universal exactly-rounded means, 10M performance and resource lifetimes are not inferred from these checks.
