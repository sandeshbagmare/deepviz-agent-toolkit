# Independent inspector-claim regressions

These NEW tests do not modify the inspector or existing test oracles. The four
malformed SVGs are the original R03/N09 controls; the five positives set explicit
stroke/fill. Structural acceptance is **not** a geometry or paint-validity pass.

From a checkout, using an existing project environment:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'python/deepviz/src')
python -m pytest tests/r10_probes/role05/test_inspector_claim.py -q
```

For baseline sensitivity, set `R10_INSPECTOR_SOURCE_ROOT` to an authorized local
checkout of `0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43`; the same tests load that
exact harness/docs without changing its files. Expect 12 failures / 4 passes.
Unset it for the checkpoint claim correction.

Optional actual browser check (installed Playwright/Chromium and Pillow required;
no installation or network assets are performed by these probes):

```powershell
# Set this only when borrowing an existing dependency tree read-only.
$env:DEEPVIZ_NODE_DEPS_ROOT = 'path/to/checkout/with/installed/node_modules'
node tests/r10_probes/role05/capture_primitives.cjs NEW_OUTPUT_DIRECTORY
python tests/r10_probes/role05/verify_paint.py NEW_OUTPUT_DIRECTORY
```

The capture refuses existing output directories. Inspect `contact.png` plus
`verified.json`; positives must paint with zero browser errors. The malformed
rectangle/radius/points intentionally produce browser errors and remain invalid,
blank negative controls. A successful probe run verifies those observations and
the claim disclosure; it does not approve those invalid artifacts or a release.
