# Independent tester B — browser QA

## Current disposition

**Product acceptance: PENDING. No real engine/browser signoff has been issued.**

The parent has not yet supplied a candidate source commit or real generated engine
artifacts. The seed harness is on isolated branch `test/browser` at
`C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-browser`, created from
`2b2709ec6846ad8e136641257e04b4ae48eded08` on November 26, 2026. That starting tree
contains contracts but no renderer implementation or npm workspace. The harness
does not substitute synthetic output for engine acceptance.

Ownership: only `tests/browser/**` and this report. No production code or other
worker's files changed. No GitHub issues, PRs, reviews, releases, or API operations.

## Harness and acceptance gates

- `tests/browser/qa.mjs`: actual artifact-byte loading; explicit offline Chromium
  contexts; deny-by-default HTTP/WebSocket routes; exact installed-version CDN
  substitution; title/category/numeric draw assertions; native chart marks;
  meaningful filled-color/connected-line raster checks; XSS/DOM/console/exception checks;
  screenshot pixel regressions against environment-pinned references.
- `tests/browser/qa.test.mjs`: manifest/coverage/path/pinned-route/raster/diff unit tests.
- `tests/browser/selftest.mjs`: synthetic positive/negative controls for the harness
  only, including canvas, SVG, PNG and iframe dashboards. Intentional failure cases
  must be rejected by the runner for the expected reason.
- `tests/browser/fixtures.json`: agreed bounded bar/line data and malicious input for
  the actual artifact producer, not generated artifacts.
- `tests/browser/README.md`: artifact manifest contract, deterministic dependency
  requirements, deliberate baseline review, exact CI commands and exit codes.

Missing engines/security cases/dashboards/static outputs are failures, not skips.
Missing baselines are failures. Baseline recording exits 2, never a CI pass. Static
PNG text is not OCR-validated; labels/values/clipping require visual baseline review.

## Fresh execution evidence — seed harness only

Environment: Windows, Node `v26.13.1`; existing global Playwright CLI's transitive
`playwright` `1.66.0-alpha-1794252756000`; Chromium `158.0.8127.18`. No npm packages or
shared-venv dependencies were installed or changed by this tester. A separate Python
distribution sanity build provisioned Hatchling in isolated build environments.
The final candidate run must instead use the
candidate's locked root npm dependencies and matching browser.

Executed on November 26, 2026:

```powershell
node --check tests/browser/qa.mjs
node --check tests/browser/selftest.mjs
node --test tests/browser/qa.test.mjs
node tests/browser/selftest.mjs --deps C:/Users/bagma/AppData/Roaming/npm/node_modules/@playwright/cli --output tests/browser/results/seed-selftest-20261126-f
```

Observed results: syntax checks exit 0; **9/9 unit tests passed**; self-test exit 0
with **15 control groups passed**, across 26 browser-suite invocations (including
expected-rejection mutations). The self-test report says
`HARNESS SELF-TEST ONLY; NOT PRODUCT ACCEPTANCE`. Browser contexts remained offline;
an exact pinned synthetic local asset was fulfilled, whereas unpinned CDN, fetch,
image and WebSocket attempts were blocked and rejected. No real npm renderer was
loaded in those synthetic controls.

Local evidence is ignored, not silently absent:
`tests/browser/results/seed-selftest-20261126-f/selftest.json` plus each `run-*/report.json`,
full screenshot, region crop and failure screenshot. Do not commit synthetic images
as reference baselines for real renderers.

Opened and visually inspected the previous `seed-selftest-20261126-e` synthetic positive SVG page (`run-2/control.png`),
canvas crop (`run-16/canvas-control-region-0.png`), two-frame dashboard
(`run-18/dashboard-control.png`), and decoded PNG (`run-23/static-png.png`), plus the
initial negative axes-only image. Titles, the two category labels and numeric ticks
are visible in those controls. Again, these are not engine-generated charts.
Also opened the final `seed-selftest-20261126-f/run-18/line-control-region-0.png`:
a real, readable two-pixel diagonal canvas line, not a filled-bar stand-in.

### Base-tree repository checks (not candidate release checks)

Using `C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`, with
`PYTHONPATH` set to this worktree's `python/deepviz/src` for pytest:

| Command | Observed result |
| --- | --- |
| `python -m pytest` | **23 passed**, Python 3.12.16, pytest 9.2.0 |
| `python -m ruff check .` | **FAILED**: pre-existing `I001` import order in `tests/test_models.py:2` |
| `python -m mypy` | Passed, 1 source file |
| `python -m build --outdir tests/browser/results/python-package-sanity-20261126` | Built wheel and sdist, isolated Hatchling 1.33.0 |

The Ruff finding is outside tester B's ownership and was not edited. `npm ci`, root
build/typecheck/test/pack could not be run against this seed tree: it has no
`package.json` or lockfile. Those checks remain pending candidate integration; the
direct Node harness checks above are not a replacement for them. Large-stream
performance checks belong to the ingestion/acceptance owners and were not run here.

### Test-first / adversarial evidence

- Initial six unit tests were run against explicit unimplemented harness functions:
  **0 passed, 6 failed**. After implementing validation and pixel comparison they
  passed.
- The first browser self-test found an actual harness false-positive: subpixel-colored
  font edges in an axes-only image satisfied the initial naive colored-pixel count.
  The pixel regression still rejected the image, but the semantic mark gate was weak.
- Added a thin-color-fringe unit test; observed **6 passed, 1 failed** because no
  solid-mark measure existed. Added locally uniform colored-interior detection;
  observed **7/7 passed**, then re-ran all browser controls successfully. The blank
  chart now fails the meaningful-mark gate before baseline comparison.
- Added a small bar-height mutation; watched it incorrectly pass the original
  full-page-only 0.5% check (1,400 changed pixels / 1,228,800 page pixels). Added
  separate 0.1% chart-crop comparisons; the same mutation now fails, while unchanged
  images still compare at zero differences. This is a real tester regression fix,
  not an assertion based on screenshot existence.
- Changed bar color is rejected by measured PNG pixel differences; unchanged images
  compare at exact zero changed pixels in the positive control. Missing titles,
  wrong numeric ticks, blank dashboard panels, console errors, page exceptions,
  script breakout, injected requests and missing baselines all have negative controls.
- A local package-layout fixture additionally verifies all six asset loaders,
  including the scoped AntV package, exact resolved versions, bytes and SHA-256s.
  This unit test is synthetic and does not imply the not-yet-installed real engine
  npm assets have been exercised.
- Added a diagonal thin-line unit test; observed **8 passed, 1 failed** with the
  filled-interior-only metric. Added connected-component count/span measurement so
  valid two-pixel line charts pass while the text-only negative controls remain red.
  Final fresh evidence: **9 unit tests / 15 browser control groups passed**.

## Rulings and limits

- Ruling: consume a manifest from the real artifact producer instead of coding against
  unmerged renderer APIs — parent explicitly supplies artifacts later. Cost: CI must
  generate that manifest, with actual container selectors and full source provenance.
- Ruling: baseline creation is not acceptance, and cross-OS/browser baseline mismatch
  is a failure — prevents auto-approved screenshots and flaky hidden upgrades. Cost:
  first real baseline sets need explicit visual review on the target CI platform.
- Ruling: this tester's branch contains no npm/root CI config edits — those belong to
  their owners. Cost: CI agent must wire the documented direct Node commands.
- Browser text checks cover DOM/SVG and recorded canvas text, not arbitrary image OCR.
  Raster/mark heuristics are tailored to the fixed acceptance fixtures, not all chart
  types or a mathematical proof that chart values are correct. Pixel baselines and
  independent visual inspection provide the additional regression evidence.
- Browser error observation lasts from navigation through final context close; this
  is not an unbounded monitor for future timers or external browser vulnerabilities.

## Required next acceptance run

Parent supplies the exact candidate SHA, locked npm deps, real Python/TypeScript
Plotly/ECharts/AntV HTML (normal + hostile), normal + hostile dashboard, and Vega /
Matplotlib SVG/PNG artifacts plus manifest. This tester then independently runs the
full suite, opens the actual rendered images, records specific defects, and repeats
verification after any fixes. No positive engine claim will be inferred from these
seed controls, from another worker's report, or from artifact existence alone.
