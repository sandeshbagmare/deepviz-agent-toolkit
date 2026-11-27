# COUNT measure fidelity: strict baseline regressions

These NEW probes do not fix production code or modify existing oracles. They
extend the known R03-01 count-channel defect with unequal caller multiplicities,
five Python adapters (including actual Matplotlib artists), bar/line/bubble,
retained numeric color/size, exact normalized keys/counts and public metadata.
Expected values are caller-authored literals: **A=2, B=3, C=1**, never values
derived from emitted native payloads. The numeric series labels are 90/80/70;
unmapped weights are 900/800/700. Correct counts cannot be replaced by either.

On source `5340bc69b7203ad7a9166543062482d819f9b705`, the semantic Python suite
was **15 RED / 40 PASS / 0 SKIP** in its 55-case run. A subsequently added disjoint
channel/retained-size check ran alone and was **1 RED / 55 DESELECTED / 0 SKIP**.
The final file contains 56 cases; those two commands executed 16 failing and 40
passing distinct cases, **not one rerun of the final 56-case suite**. RED is not
xfail or an accepted passing gate. No source fix was made.
Explicit-y count, categorical color, explicit SUM/none bar+line, exact metadata
and mapped-size rejection are positive controls. Wrong-count marks must fail
until an authorized corrected source is independently retested.

## Portable commands (existing dependencies, no installation)

```powershell
$env:PYTHONPATH = "$PWD/python/deepviz/src"
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m pytest tests/r15_probes/role17 -q --tb=short
python -m ruff check tests/r15_probes/role17
```

For an exact baseline hash check, set `DEEPVIZ_R15_SOURCE_IDENTITY` to the JSON
source ledger published with this report; loaded Python modules must match its
5340 Git-blob hashes. Without that variable only the source-identity check skips;
the **55 semantic cases still run**. A later corrected source must run semantic
checks under its own independently recorded identity, not pretend to be 5340.

For bounded TypeScript public-API parity, build the selected checkout with its
existing TypeScript compiler; set `DEEPVIZ_R15_TS_ENTRY` to that checkout's built
`packages/deepviz/dist/index.js`, then:

```powershell
node --test --test-reporter=tap tests/r15_probes/role17/count-parity.test.mjs
```

These 28 cases cover four native adapters, not Matplotlib or all npm behavior.

## Actual paint and interaction

```powershell
python tests/r15_probes/role17/collect_visuals.py --output artifacts/local/unique-count-run
# Only already-installed Playwright + browser; optional process-only NODE_PATH.
node tests/r15_probes/role17/browser-count.cjs artifacts/local/unique-count-run artifacts/local/unique-browser-run
```

Both output directories must be NEW. Collector exit0 means six real artifacts
were collected, **not** that count fidelity passed. It generates all five Python
engine artifacts plus one explicit-y Plotly control; ECharts/G2 HTML discloses its
network dependency. The browser executes only the two self-contained Plotly
pages, exports genuine SVG/screenshots, moves the real pointer for hover, and
checks actual bar geometry against **literal 2/3/1** through the rendered axis.
Any console/page/request failure fails the browser run. Baseline browser exit1
records wrong implicit-y COUNT; the explicit-y control passes.

Open actual images before claiming paint. The report records opened Matplotlib,
Vega and two Plotly images, zero console errors and honest semantic failures.
This small six-row fixture is not a scale benchmark, universal engine guarantee,
theme/XSS audit, final source review, CI approval, issue closure or release.
