# Installed asset provenance (R10 role14)

These are independent operator-run checks, not product code or final release approval.
They read only explicitly supplied installed packages, source, archives and existing
browser tooling. Output directories must be new. The Python/Node manifests contain
relative artifact paths and hashes, not machine-specific source/dependency locations.
All paths below are trusted operator inputs, never model-authored ChartSpec fields.

## Prepare locally, without updating dependencies

Use existing build/runtime tooling to produce a wheel **from an sdist** of the chosen
checkpoint and the npm tarball from its own compiled source. Build/pack/install logs
and exact source identities belong in the caller's evidence. Install only those
fresh local toolkit artifacts in new targets; no registry/dependency resolution:

```text
python -B -I -m pip install --no-index --no-deps --no-cache-dir --no-compile --target PY_TARGET WHEEL
npm install --offline --ignore-scripts --no-audit --no-fund --no-package-lock --prefix NPM_TARGET TARBALL
```

The Python consumer deliberately reuses already installed runtime dependencies; it
is **not** a newly resolved standalone environment. The npm package has no renderer
runtime dependencies/bundles. Provisioning new dependencies is outside these probes.

## Run

From the source checkout, with its interpreter's existing dependencies available:

```text
python -B -I tests/r10_probes/role14/asset_manifest.py --source . --source-commit FULL_SOURCE_SHA --installed PY_TARGET --wheel WHEEL --sdist SDIST --out NEW_PY_OUTPUT
node tests/r10_probes/role14/offline_probe.mjs --manifest NEW_PY_OUTPUT/python-manifest.json --npm-package NPM_TARGET/node_modules/@deepviz/agent-toolkit --built-dir packages/deepviz/dist --tarball TARBALL --deps-root EXISTING_DEPENDENCY_CHECKOUT --out NEW_BROWSER_OUTPUT
python -B -I -m pytest -q -p no:cacheprovider tests/r10_probes/role14/test_asset_oracles.py
```

The manifest verifies nine imported Python modules against exact Git-object bytes,
wheel, sdist and installed target; six packaged resources against Git/wheel/target;
then produces actual installed renderer outputs. The Node probe rejects a workspace
symlink and verifies installed npm JS/schema against the separate pinned build.
It hashes the existing development library files/licenses/notices without executing
them. Chromium receives actual generated HTML/SVG bytes only; every other request
is blocked, with no CDN substitution/network fallback.

Expected checkpoint controls: ten offline successes (Python Matplotlib, Plotly,
Vega, Plotly dashboard; npm SVG bar and five native tables) and six **chart failures**
when CDN scripts cannot load (Python ECharts/G2 and npm Vega/ECharts/G2/Plotly).
An exit0 classifies these negatives correctly; it does not make those six charts
valid. Inspect the saved positive and negative screenshots, readiness, real marks,
counts and errors before interpreting any result.

## Limits and independently sourced metadata

Pins are specific to the audited checkpoint, not latest-version claims. The Python
notice constant is the official Plotly.js v3.7.0 LICENSE SHA256, independently
retrieved 2026-11-27:
https://raw.githubusercontent.com/plotly/plotly.js/v3.7.0/LICENSE . A different runtime
tag fails the audited-notice identity rather than silently claiming coverage.
The companion evidence includes exact npm-registry metadata and pinned CDN byte
hashes matched against installed assets. Downloaded bytes were hashed only and
never executed or used as browser responses.

No claim covers every chart kind/theme/geography request, future CDN bytes,
independent dependency resolution, all advisories or all transitive license terms.
Historical R03 evidence remains separate. R10 report/manifest identify source
3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab, not later candidate changes.
