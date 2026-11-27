# R17-12: category-density RED with full-size positive controls

This strict NEW browser regression reuses the existing compiled native SVG renderer. It does
not build, install, change product code, rerun the20R11numeric cases or measure10Mrows.

```powershell
# From repository root, with an existing build and installed Playwright/Chromium.
$env:DEEPVIZ_PLAYWRIGHT_ENTRY = 'C:/path/to/existing/node_modules/playwright/index.mjs'
$env:DEEPVIZ_R17_OUTPUT = 'C:/path/to/NEW/unique/output'
node --test --test-reporter=tap tests/r17_probes/role12/category-density.test.mjs
```

Eight bounded1..8 observations use ordinary`g0`…`g7`labels and one justified Unicode branch-name
fixture (`東京都東部支店1`…`8`, below the existing18-character abbreviation threshold).
Both240x200and960x540, standalone SVG and generated HTML are opened offline in Chromium.
Real text bounding boxes, category order, literal strings, mark titles/values/ratios/zero,
console/page errors, screenshots and hashes are saved before the strict assertion. Font
fallback is browser/OS-dependent: the probe measures actual boxes, not8px-per-Unicode guesses.

Pairwise positive-area axis-aligned text-box intersections fail. On the current horizontal
axis this tests visible layout density, not merely containment. The oracle has overlap,
edge-contact and separate-row self-controls. A future rotated layout should reassess whether
conservative axis-aligned intersections need an actual glyph-quad oracle; do not weaken a
current RED to an expected pass. No fake assets/network responses or label hiding is used.

At source5e595a8, minimum-width ordinary and Unicode cases are expected genuinely RED;
full-size cases are positive controls. This is one category-layout finding, not a ticket
per fixture. Numeric tick containment is a different gate. Publication of this test is
not a green product claim, independent review, category-density fix or final signoff.
