# Independent R17 SVG tick review

New finite native SVG/HTML checks for assigned immutable source
`5e595a8f893955ce34a0e26553bb7bf257ea93ae`. This reviewer did not author its fix or tests.

From this OWN branch, after building a clean detached consumer with the existing compiler:

```powershell
$env:R17_13_SOURCE = '<detached 5e595a8 checkout>'
$env:R17_13_PLAYWRIGHT = 'C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-n21/node_modules/playwright/index.mjs'
$env:R17_13_OUTPUT_PARENT = '<NEW owned output directory>'
node --test --test-reporter=tap tests/r17_probes/role13/svg-tick-review.mjs
```

The script pins Git identity, proves source blobs, imports only the detached consumer's build,
and saves actual Chromium DOM geometry, PNGs, runtime errors and hashes. It fails on actual
numeric-label clipping, nonpositive plot width, changed coordinate scales/zero baselines/data,
literal-label corruption or runtime/network errors. It covers bounded bar, numeric line/area,
scatter/bubble, histogram, empty/single bar and HTML pie/one-series fixtures.

Pie and color-series raw output contains an existing HTML legend sibling; those two controls
use the real HTML carrier, not an XML-fragment rewrite. Category-label nonoverlap/readability
is **not** inferred from numeric containment; its known narrow-chart density issue is role12's
separate task. The finite-format sweep is representative, not every IEEE754 bit pattern or OS
font. No install, full suite, scale benchmark, old31CIcontrols, source or existing-test edit.

`finite-range-regression.mjs` is a separate strict positive/negative control for a **pre-existing**
range-overflow defect: signed `1e200` passes, signed `1e308` returns accepted data with zero/NaN
bar geometry. Run with the same `R17_13_SOURCE` environment using `node --test`. Expected
current outcome is one real pass/one real failure, not an expected-failure waiver. The tick-margin
patch does not change the overflowing vertical-scale expression; a production owner must decide
and fix it separately without silently changing the accepted values.
