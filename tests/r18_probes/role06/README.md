# R18 role06: independent tiny non-bar SVG acceptance

Frozen product source: `5e595a8f893955ce34a0e26553bb7bf257ea93ae`.
These NEW probes never edit production or original tests. They import a fresh build of that exact clean committed source's public `dist/index.js`, **not this older evidence branch's renderer**. Existing installed TypeScript/Playwright/Chromium are read-only; no installs or external/CDN requests.

Literal4-point x values1/2/4/8; four y profiles (positive, negative, signed-scientific, actual zero). Line/scatter/area/bubble at240² and960², plus one240² scientific pie: **33fixtures/66realSVG+HTMLartifacts**. No authored20bar matrix, reviewer bar cases, old60PythonCDN matrix, density or scaling replay.

## Reproduce in a NEW clean exact-source worktree

From this evidence branch, use existing installed tools (an ignored source-local node_modules junction is permitted on Windows):

```powershell
git worktree add --detach <NEW-source> 5e595a8f893955ce34a0e26553bb7bf257ea93ae
# Point only the NEW source's ignored node_modules at already installed tooling; do NOT run npm ci/install.
npm --prefix <NEW-source> run build --workspace @deepviz/agent-toolkit
npm --prefix <NEW-source> run typecheck
node tests/r18_probes/role06/generate.mjs <NEW-source> <NEW-output>
node tests/r18_probes/role06/browser.mjs <NEW-output>
```

Output directories must be new; no overwrite of previous captures. Browser writes per-artifact progress JSON and a final `browser-report-viewport.json`. Standalone SVG is the first real SVG element of public `spec.svg`; optional pie HTML legend is deliberately checked in public full HTML, not claimed to exist in standalone XML. Measurements include root-logical transformed bboxes, true SVGPointList/circle centers, titles, x-ticks, extreme y-ticks, visible fills/strokes, table order and errors.

`oracle.test.mjs` is an **offline oracle/saved-observation regression**, not a second browser run:

```powershell
node --test tests/r18_probes/role06/oracle.test.mjs
node tests/r18_probes/role06/verify.mjs docs/coordination/evidence/R18-06
```

It checks the published genuine66DOM snapshots against independently literal fixtures and seven blank/value/order/zero/tick/clipping/browser-error corruptions. It does not fake native responses or modify HTML to pass.

## Actual run chronology and limits

- Original25fixtures/50artifacts were captured once to completion after a harness-only fullPage XML screenshot timeout was isolated. Exact original SVG XML and HTML were unchanged. The reliable capture uses real SVG viewport clip, HTML fullPage.
- Original observer had10false failures (float32 ratios8; semicircle large-arc flag2), plus one blank-control TypeError. `reassess.mjs` corrected **observer only**, rescored saved50states, verified50image hashes, and kept original failure values/hash in `observer-errata-controls.json`; it did **not** rerun those completed browsers. Seven corruptions then rejected normally.
- Eight previously unrun zero-anchor fixtures added16artifacts in a separate output: generator's optional last argument `zero` selects only those. Actual aggregate **1403checks pass/0fail/0skip, zero console/page errors and external requests**. Independent 0.02pixel value geometry remains;1e-4 ratio tolerance accounts for SVG DOM float32 centers, not ordinal placement. All-negative inherited domain maximum1 remains disclosed; this is not an axis-domain-policy change.
- `collect.mjs <first-run> <zero-run> <NEW-evidence>` reflects that actual two-run chronology; it verifies66original screenshots and emits compact observations/provenance plus10actual image files. The manual `opened_by_image_read` annotations in the published capture manifest were added only after genuine image-tool opening, not by collector automation.
- Tiny fixed numeric fixtures only: no category-density, arbitrary labels, other engines, arbitrary size ordering, mark-overlap avoidance, package distributions, transport, scale tiers, final HEAD or universal native-kind approval. Literal bubble overlap is not incorrectly classified as blank/clipping. Earlier R10AntV color/negative-heatmap RED and3PythonPlaywright setup failures remain separate and unchanged.

Exact commands/exits/observer failures/publication receipts: `docs/coordination/reports/R18-06-svg-other-kind-test.md`.
