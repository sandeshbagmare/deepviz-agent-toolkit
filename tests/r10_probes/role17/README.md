# Portable Vega dashboard oracle (R10 role17)

This independent harness uses the public renderer and installed real `vl_convert`.
It does **not** import or replace the existing acceptance matrix. The latter has
ten known parent-title-on-standalone-child failures; retain them as RED evidence.

The new checks require the visible literal parent **and each correct child**,
compile native children under their own titles, verify mapped observations,
irregular quantitative x spacing, bar heights/zero baseline and point geometry.
They reject metadata-only/hidden titles, wrong child titles, mutated values/drawn
geometry, executable/foreign/style elements, event attributes and external hrefs.
Tiny fixtures are embedded; no MAIN paths, extra fixtures, downloaded scripts,
arbitrary expressions or dependency installations are needed.

From a checkout with the project's existing dependencies installed:

```powershell
$env:PYTHONPATH = "$PWD/python/deepviz/src"
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -m pytest python/deepviz/tests/test_backend_vega.py tests/r10_probes/role17 -q
python -m ruff check tests/r10_probes/role17
python tests/r10_probes/role17/vega_contract.py --output artifacts/local/role17-unique-run
```

The output directory must be new. CLI output includes original composed SVG,
real PNG, exact composed payload, module paths/hashes and relative original
wrapper paths. It also works from another CWD with a relative output directory.
Existing source/oracles are never edited. The geometry fixture is intentionally
small: three rows, six dashboard contributions, x=0/1/10 and y=2/8/4, **not** a
scale benchmark or a universal renderer certification.

Optional actual-browser supplement (already-installed Playwright and browser):

```powershell
# Only if Playwright is installed elsewhere, point NODE_PATH at that node_modules.
# No install, shared environment mutation, login or CDN is performed by this script.
node tests/r10_probes/role17/browser.cjs artifacts/local/role17-unique-run
```

Windows defaults to installed Edge; set the process-only
`DEEPVIZ_BROWSER_CHANNEL` to select another installed Chromium channel.
The ephemeral localhost fixture server supplies only the output directory and
HTTP204 favicon. All browser console/page/request errors fail the supplement.
Direct SVG DOM/text/bounds checks plus original-wrapper screenshots complement
converter PNG inspection; direct-SVG page screenshots are not attempted.

The XML guard rejects common hidden sinks but is not a full CSS/paint engine.
Open the actual PNG/browser captures before making a visible-output claim.
Expected branch/source/results and baseline-versus-new distinctions are in
`docs/coordination/reports/R10-17-vega-visible-title.md`; publication is not final
candidate signoff, a source fix, remote CI approval or issue closure.
