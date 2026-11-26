# Offline browser acceptance (independent tester B)

This is a **test harness**, not renderer acceptance evidence. The initial branch has
no real engine artifacts or reviewed product baselines. See
[`docs/verification/tester-b.md`](../../docs/verification/tester-b.md).

## What it checks

- Opens the **actual artifact bytes**, unchanged, in headless Chromium. No HTML
  reconstructed from expected specs and no screenshot-presence-only assertions.
- Plotly, ECharts, and AntV each need a basic HTML case and a hostile-input HTML case.
  A normal and a hostile dashboard must each have at least two distinct chart regions.
  Vega and Matplotlib each need an actual SVG or PNG case (both formats may be supplied).
- Every region needs native canvas/SVG marks and a raster containing substantial
  colored mark interiors or a long connected colored line, distributed across the
  plot. Axes/text-only pages fail; thin legitimate line charts remain valid.
  Single-accent charts are allowed. These thresholds target these bounded bar/line
  acceptance fixtures, not every possible sparse or monochrome visualization.
- Visible titles/categories are checked against DOM/SVG/canvas-drawn text. At least
  two distinct expected numeric labels must actually be drawn in SVG or canvas, not
  merely occur in inline JSON or the page title. Dashboard text is checked across its
  frames; every panel independently undergoes mark/raster checks.
- Console errors, page exceptions, dialogs, popups, downloads, unexpected navigation,
  injected DOM elements, XSS-canary execution, and unexpected requests are failures.
- Exact PNG pixel comparison against reviewed reference images, including equal image
  dimensions. Channel differences <=16 are tolerated; at most 0.5% of full-page pixels
  and 0.1% of **each chart crop's pixels** may exceed that delta. A small wrong bar
  cannot hide in large page margins. Baseline metadata pins Chromium/Playwright/OS/viewport and expectations.
  Missing baselines or metadata/environment drift fail, never silently update.
- Static PNG/SVG outputs are rasterized/decoded and subjected to the same meaningful
  color and visual-regression checks. **There is no OCR.** A human/tester must inspect
  static titles, axes, numeric labels, clipping, and values before accepting a baseline.

## Offline guarantee and dependency installation

Setup may download npm packages and a browser. **Test execution does not.** Use the
candidate root's locked dependencies; this harness adds no production dependencies.
The root development dependencies must include `playwright`, `echarts`, `@antv/g2`,
`vega`, `vega-lite`, `vega-embed`, and `plotly.js-dist-min`.

```powershell
npm ci
npx --no-install playwright install chromium
node --test tests/browser/qa.test.mjs
node tests/browser/selftest.mjs --deps .
```

Linux browser system libraries must be installed by the CI environment too (for
example Playwright's `install --with-deps chromium` during provisioning).
`--deps <npm-project-root>` allows an isolated QA worktree to use an existing locked
`node_modules` without altering the candidate source or sharing source files.

Each browser context is explicitly offline, service workers are disabled, and HTTP
and WebSocket routing deny all requests except the following:

1. Manifest-listed local artifact bytes, served in memory at an `.invalid` origin.
2. Exact installed-version CDN URLs, fulfilled using the installed package's JS bytes.
   Supported spellings are `cdn.jsdelivr.net/npm/<package>@<exact-version>/<asset>`,
   `unpkg.com/<package>@<exact-version>/<asset>`, and Plotly's exact-version `cdn.plot.ly`
   URL. No `latest`, major aliases, version ranges, redirects, or alternate hosts.
3. The virtual origin's `/favicon.ico`, answered with an empty 204 as browser
   infrastructure, not forwarded to a network.

Assets are `echarts/dist/echarts.min.js`, `@antv/g2/dist/g2.min.js`,
`vega/build/vega.min.js`, `vega-lite/build/vega-lite.min.js`,
`vega-embed/build/vega-embed.min.js`, and `plotly.js-dist-min/plotly.min.js`.
Installed package versions **must equal** the pinned versions used by generated HTML.
Every substituted URL, version, and SHA-256 is recorded. No network fallback exists.

## Candidate artifact producer contract

The integration/CI producer must generate the files through the **real public engine
APIs at the specified source commit**, then create `manifest.json` alongside them.
The parent will supply this producer and candidate commit; the seed harness does not
pretend to implement unmerged renderer APIs. Use [`fixtures.json`](fixtures.json)
for bounded input records/specs and the exact hostile payload. Normal inputs have
values 7, 19, 31; titles are `QA revenue` / `QA trend` (no numeric title shortcut).

For hostile cases put the payload in **title, category values, and field names**.
For example rename `category` to `category` + payload in the spec/data, retain the first
two category values, and change the third to payload. Set the title to `QA revenue ` +
payload. For dashboards, exercise both wrapper and child title escaping. Do not
edit generated HTML to make security cases or swap in a handcrafted chart. The
hostile artifact must retain `DEEPVIZ_QA_32635` and `__deepviz_xss` in its source as
data; executing a script, creating `[data-deepviz-xss]`, or making its request fails.

Manifest format (one case shown; **coverage requirements above still apply**):

```json
{
  "version": 1,
  "sourceCommit": "FULL_40_CHARACTER_LOWERCASE_SOURCE_SHA_FROM_GENERATION",
  "cases": [
    {
      "id": "python-plotly-bar",
      "engine": "plotly",
      "format": "html",
      "path": "python-plotly/chart.html",
      "title": "QA revenue",
      "labels": ["North", "South"],
      "numbers": ["0", "10"],
      "regions": [{ "selector": ".js-plotly-plot", "minMarks": 3 }]
    }
  ]
}
```

- `engine`: `plotly`, `echarts`, `antv`, `vega`, or `matplotlib`.
- `format`: `html`, `svg`, or `png`. `path` is relative to the manifest directory;
  absolute paths, traversal, and symlinks escaping that directory are rejected.
- For PNG/SVG cases only `id`, `engine`, `format`, `path`, `title` are needed.
- `security: true` identifies a real hostile-input case; it cannot replace the basic
  case. `dashboard: true` requires two distinct regions and cannot replace a single
  chart case.
- Region selectors must identify exactly one **actual chart container**, not the body,
  an unrelated legend, or an empty screenshot target. Use a specific container ID for
  ECharts/G2. Plotly bars may use `minMarks: 3` or a more specific chart container.
- If dashboards use iframes, regions can be
  `{ "frame": "iframe#first", "selector": ".js-plotly-plot", "minMarks": 3 }`
  and the equivalent second frame. `frame` is an iframe CSS selector, not its URL/name.
  Inline dashboards instead use distinct chart selectors without `frame`.
- Include any separately linked child HTML/images as cases too so their real bytes
  are available to the offline route. Nothing else is implicitly served from disk.
- Set `sourceCommit` to the exact full commit generated, not `HEAD`, a branch name,
  a shortened hash, or a fabricated provenance string. Reports also record each
  artifact's content SHA-256. Generation provenance remains the producer's duty.

If numeric ticks differ legitimately, inspect the **real output**, then set precise
numeric expectations for that engine. Do not remove the numeric test. If an engine
outputs only PNG, choose its PNG case and perform the explicit static-label review.

## Baseline review and CI commands

Do not create baselines from synthetic self-tests or auto-refresh them in CI.
Supply fresh output directories; runs refuse to overwrite an existing directory.
This example assumes the producer has set `DEEPVIZ_BROWSER_MANIFEST` to its manifest:

```powershell
$stamp = [guid]::NewGuid().ToString('N')
node tests/browser/qa.mjs --manifest $env:DEEPVIZ_BROWSER_MANIFEST --deps . --baselines tests/browser/baselines/win32 --output "tests/browser/results/record-$stamp" --record-baselines
```

**Recording intentionally exits 2** and reports `recorded-not-accepted`, not a pass.
Inspect every full image and region image: real chart geometry, the known relative
values, readable titles/category/numeric labels, no clipping/overlap, and dashboard
composition. Independently review the security inputs/outputs too. Only then retain
the PNG/JSON pairs in a platform-specific baseline directory and run verification:

```powershell
$stamp = [guid]::NewGuid().ToString('N')
node tests/browser/qa.mjs --manifest $env:DEEPVIZ_BROWSER_MANIFEST --deps . --baselines tests/browser/baselines/win32 --output "tests/browser/results/verify-$stamp"
```

Linux CI, after provisioning and generation:

```sh
node --test tests/browser/qa.test.mjs
node tests/browser/selftest.mjs --deps .
node tests/browser/qa.mjs --manifest "$DEEPVIZ_BROWSER_MANIFEST" --deps . \
  --baselines tests/browser/baselines/linux --output "tests/browser/results/ci-$BUILD_ID"
```

Set a unique `BUILD_ID`. **Normal verification exits 0 only on a complete passing
suite; 1 is failure; 2 is baseline recording, not CI success.** Upload the entire
new output directory, especially `report.json`, full screenshots, per-region crops,
and failure screenshots. Candidate results must cite the candidate source commit
and the separate harness commit. Changing Chromium/OS/fonts needs deliberate
baseline review, not a relaxed comparison threshold.

`selftest.mjs` uses known synthetic positive/negative controls (including intentionally
broken charts, XSS, blocked traffic, and changed pixels) to prove the harness catches
failures. Its report explicitly says **not product acceptance**. It does not use or
create the real-engine baseline directory. It never proves a renderer works.
