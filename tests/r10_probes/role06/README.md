# Role06 real native browser probe

Source and existing oracles are untouched. This harness generates **fresh real Python
`render()` HTML**, then uses installed Node Playwright/Chromium against that exact
output. It does not install dependencies, intercept requests, or fake CDN responses.
AntV/ECharts use their emitted pinned CDN URLs; Python Plotly uses the bundled runtime.
AntV observation preserves `render` arguments/return/options and only retains instances.

From a clean checkout with existing dependencies and **this checkout's** Python source:

```powershell
$env:PYTHONPATH="$PWD\python\deepviz\src"
$out="$PWD\artifacts\local\R10-06\run-$(Get-Date -Format yyyyMMddTHHmmssfff)"
& <existing-python> tests/r10_probes/role06/generate.py --output $out
node tests/r10_probes/role06/browser.mjs $out
```

The output directory must not exist. A second browser run requires fresh generation;
the harness never overwrites earlier evidence. `cases.json` records source SHA and
loaded-module hashes. `browser-report.json` records readiness, data/native values,
geometry/spacing, visible titles/labels, data-table mouse/keyboard interaction, exact
network and console/page errors, and real PNG hashes. An existing local dependency
tree may be referenced read-only; no shared environment edits are required.

`generate.py --case plotly-bar` can run only a named new case when correcting an
observer mistake; it does not justify replaying finished suites. `collect.py`
combines the original 59 cases with that one corrected real pointer case **only
when the complete source/module identity matches**, retains the original failure
as an explicit harness erratum, and exits1 for the remaining genuine failures.

For the all-negative AntV heatmap diagnostic, use fresh outputs:

```powershell
& <existing-python> tests/r10_probes/role06/heatmap_diagnostic.py --output <new-diagnostic-dir>
node tests/r10_probes/role06/heatmap_diagnostic.mjs <new-diagnostic-dir> [original-generated-heatmap.html]
& <existing-python> tests/r10_probes/role06/scale_controls.py --output <new-scale-dir>
node tests/r10_probes/role06/heatmap_diagnostic.mjs <new-scale-dir>
```

The optional original HTML is loaded unchanged and without any chart observer.
Legend-off/explicit-scale fixtures are clearly marked **diagnostic-only overrides**,
not a product GREEN. The legend-off control paints but fails to distinguish negative
cells; merely hiding the legend must not be proposed as semantic acceptance.

```powershell
& <existing-python> tests/r10_probes/role06/collect.py --initial <60-case-dir> --correction <corrected-plotly-bar-dir> --diagnostic <heatmap-dir> --scales <scale-dir> --output <new-evidence-dir>
& <existing-python> -m pytest tests/r10_probes/role06/test_wrapper.py -q
& <existing-python> -m ruff check tests/r10_probes/role06
& <existing-python> -m mypy tests/r10_probes/role06
```

Exit1 means at least one strict check failed, even if every chart painted. In
particular, composition marks with one fixed fill but distinct-category legends
must **not** be approved as correct. Themes are checked against actual computed
child backgrounds, not inferred from the native theme string. AntV tooltip is
explicitly disabled by this adapter; interaction there is the real accessible data
table, not a fictional hover tooltip. Tiny fixtures are not scale evidence.

The existing optional Python test still requires the separately installed Python
Playwright module. A Node bridge does not turn a missing-module pytest failure into
a pass. These checkpoint results do not constitute final-source signoff.
