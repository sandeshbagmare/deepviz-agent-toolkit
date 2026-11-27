# R10-12 native SVG numeric-tick containment

Strict browser regression for [issue #23](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/23).
It uses eight reduced records, **not a 10M-row rerun**. No production code is changed.

```powershell
# From repository root; use an already installed TypeScript compiler if this snapshot has no node_modules.
npm run build
# Optional: absolute existing playwright/index.mjs, otherwise normal package resolution is used.
$env:DEEPVIZ_PLAYWRIGHT_ENTRY = 'C:/path/to/installed/node_modules/playwright/index.mjs'
$env:DEEPVIZ_R10_OUTPUT = 'C:/path/to/NEW/unique/output'
node --test --test-reporter=tap tests/r10_probes/role12/tick-containment.test.mjs
```

Requires installed Playwright and Chromium; this test never installs/downloads them. It loads
real generated local HTML and raw SVG offline, aborts external requests (no fake responses),
records actual DOM geometry/console/page failures and PNGs, then fails if labels are clipped.
Raw SVG uses a viewport screenshot because it has no HTML body for full-page sizing.
Output names use exclusive writes; choose a new output directory for each run.

Three fixtures each exercise native SVG and HTML: small values (positive controls), the exact
eight group sums from the previously measured 10M workload, and signed long-exponent labels.
Checks retain literal min/max tick strings, category/axis labels, eight nonempty marks, exact
titles, relative absolute heights and a common zero baseline. Text cannot be hidden, reduced
below 10px, or silently abbreviated to pass containment.

At checkpoint `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`, long ticks are expected to be genuinely
RED; a published test branch is **not** a green candidate or final approval. Renderer owner must
fix label layout and independently rerun these controls. All prior scale/memory claims remain
source-specific in the R03 baseline report.
