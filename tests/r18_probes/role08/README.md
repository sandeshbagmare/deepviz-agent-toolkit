# R18 role08: strict AntV color regressions

Only two defects are in scope: categorical mark colors that disagree with the
visible legend, and an all-negative quantitative heatmap that rejects readiness.
The source remains untouched until a separate, explicit R04 producer transfer.

The eleven fixtures contain four categorical charts (pie, sunburst, treemap,
gauge), five two-cell heatmaps (negative, positive, signed, constant and zero),
and ordinary positive line/scatter controls. Expected labels and values are
literal fixture data, not computed from the emitted native payload.

## Run on a clean pinned source

Use the existing Python virtual environment and existing Node Playwright; do
not install into a shared environment. Set `PYTHONPATH` to the chosen clean
source's `python/deepviz/src`, and set `PYTHONDONTWRITEBYTECODE=1` if the source
must remain completely clean. From this probe directory:

```powershell
python -m pytest test_antv_color.py -q --basetemp <NEW_EXTERNAL_TEST_DIR>
python generate.py --source <CLEAN_SOURCE> --commit <EXACT_SHA> --output <NEW_OUTPUT>
node browser.mjs <NEW_OUTPUT> <EXISTING_NODE_TOOL_ROOT>
```

`generate.py` imports the public Python `render()` boundary. It verifies loaded
module locations and Git blob identity (only CRLF/LF differences permitted),
then writes real HTML/manifests in a new directory. This is Python source
execution, not an npm build or wheel installation.

The browser opens **unchanged** generated HTML against its real pinned
jsDelivr G2 5.4.8 asset. There is no request interception, fake CDN response,
legend suppression, native payload override, or HTML rewrite. A first
navigation has no observer; a separate navigation records the real
`G2.Chart` constructor return with unchanged arguments/options and original
implementation. Readiness/error parity is checked between them. Native
canvas scenegraph, legend labels/markers, pixel samples and actual PNGs are
recorded. Browser errors are strict failures, not swallowed passes.

Both commands must return nonzero while their strict defects persist. A RED
run is evidence, not completion. Distinguish an extraction/selector error in
this new harness from a production failure, retain its original record, and
fix only the owned harness when needed. Actual PNGs must be opened before
claiming visible correctness. An all-negative diagnostic with the legend
hidden is explicitly not a repair.

This bounded, light-theme Chromium test does not certify all chart kinds,
all browsers, accessibility, package consumers, offline mode, large-input
memory, final frozen source, green CI or issue closure.
