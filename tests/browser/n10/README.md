# Independent native-browser semantics evidence (N10)

This is an observation-only QA harness, not a renderer replacement. The product
source under test is recorded in the generated manifest/browser reports. The
original run used `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.

## Run in a fresh worktree

Use the project's existing development interpreter, with render extras, and
install npm dependencies only in this worktree. Do not modify a shared virtual
environment. PowerShell commands used on the original Windows environment:

```powershell
$python = 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe'
$env:PYTHONPATH = (Resolve-Path python/deepviz/src).Path
$env:PYTHONDONTWRITEBYTECODE = '1'
& $python tests/browser/n10/generate.py
npm ci
npm run build
node tests/browser/n10/generate-ts.mjs
node tests/browser/n10/inspect.mjs python-default py-
node tests/browser/n10/inspect.mjs ts-default ts-
& $python tests/browser/n10/static_semantics.py
& $python tests/browser/n10/contact_sheets.py
& $python tests/browser/n10/analyze_evidence.py
& $python tests/browser/n10/semantic_regressions.py
```

The browser must already be available to Playwright. Output lives in
`artifacts/local/N10/`; browser run directories are fresh-only and will refuse to
overwrite evidence. Use a new run name for a rerun, e.g. `ts-rerun-01`. The final
analysis scripts intentionally select the original `python-default` and
`ts-default` folders; change their inputs deliberately for a different candidate.

## What this establishes (and does not)

- `cases.json` contains independent known-value inputs and semantic oracles for
  bars, numeric lines, scatter, pies, heatmaps, series, dark theme and dashboards.
- `generate.py` records the actual imported Python module, SHA, dirty state,
  versions, schema hash, inputs and native manifests; no product files change.
- `generate-ts.mjs` produces default artifacts and, separately, artifacts using
  supported explicit local-library URLs. An unsupported SVG heatmap is reported,
  not silently substituted with a different engine.
- `inspect.mjs` serves the unmodified default HTML through localhost and really
  loads the dependencies its scripts request. It does not intercept requests or
  inject library stubs. It records script HTTP status, bytes, SHA256, real global
  versions, actual native Plotly/ECharts values/layout, SVG geometry, screenshots,
  console exceptions and failed requests. A transparent Canvas `fillText` wrapper
  observes text while calling the original method unchanged. Optional `local`
  run mode uses genuine npm assets and is not default-CDN acceptance.
- Native Python Matplotlib/Vega outputs render as actual companion SVG images,
  so their geometry is separately parsed by `static_semantics.py`.
- Contact sheets are labeled reductions of the real browser screenshots. Open
  these and relevant full-size individual images; raster counts alone do not
  prove mapping, theme readability, correct kind, or actual mark proportions.
- `analyze_evidence.py` checks actual native values/geometry and hashes captured
  screenshots/resources. Passing it is **not** a semantic signoff.
- `semantic_regressions.py` checks original screenshot/DOM failure observations.
  On the recorded baseline it intentionally exits1 with seven failures: G2
  filled Python line, same-color Python pie, overlapping TS grouped bars, dark
  ECharts labels, and three unlabeled pie-category cases. The grouped-bar gate
  explicitly expects six non-overlapping bars; a documented stacked composition
  needs a different oracle. It is not evidence that later producer fixes ran.

Original driver failures due to tiny G2 scatter glyphs and a substring-prefix
selection bug are preserved in the raw reports, not reclassified as product
errors. The corrected driver uses exact ID prefixes and a narrower scatter ink
threshold; exact point count/spacing is still independently inspected.

The detailed source-specific outcome, limitations and N05/N18 handoff are in
`docs/coordination/reports/N10-browser-tester.md` in the coordination checkout.
No newer integrated candidate, CI run, package build or external issue is
certified by these baseline artifacts.
