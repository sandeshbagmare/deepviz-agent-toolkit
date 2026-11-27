# R21 actual Python tool artifact host probe

These are optional, explicit independent probes for exact product commit
`7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6`, not production changes.
Use the existing interpreter, LangChain-core, Matplotlib and Playwright/Chromium;
no package install/build/CDN requests/new advisory queries are needed.

```text
python -B -I tests/r21_probes/role14/generate_tools.py --repository . --out NEW_GENERATION
node tests/r21_probes/role14/offline_host.mjs --manifest NEW_GENERATION/tool-artifacts.json --deps-root EXISTING_DEPS --prior-inventory docs/coordination/evidence/R10-14/offline-manifest.json --out NEW_BROWSER
python -B -I -m pytest -q -p no:cacheprovider tests/r21_probes/role14/test_live_host.py --host-evidence NEW_BROWSER/host-observations.json --basetemp NEW_TEMP
python -B -I -m pytest -q -p no:cacheprovider tests/r21_probes/role14/test_oracle_controls.py --basetemp ANOTHER_NEW_TEMP
```

The first command materializes/hash-checks immutable Git source objects in a new
caller-owned directory, verifies every imported deepviz module comes from that
snapshot and calls real `create_tools()` StructuredTool.invoke for ECharts, AntV
and Matplotlib. It does not build/install a consumer or call a model/provider.
The two labels `A & B`, `C < D` with3/9 and title containing `<literal>` are inert.
Tool generation counts/warnings are recorded, not mistaken for browser readiness.

The browser routes unchanged generated HTML/SVG, explicitly denies all outbound
requests in two negative fixtures, and separately supplies only real previously
installed exact-version/SHA256 runtime bytes for two labeled positive controls.
It never downloads or swaps a fake library, edits HTML/bootstrap/payload or claims
CDN health. The third positive is static Matplotlib: zero scripts/externalrequests,
actual loaded siblingSVG, safe caption/labels and keyboard data fallback.

Only an observer deadline1500ms bounds readiness discovery; no timeout, loading
spinner or ready API for static HTML is invented. Existing artifact code itself
assigns `window.deepvizReady` and attempts to set body.dataset.renderError on a
catch. The strict tests verify those intended interactive signals under controlled
missing-library failure. On7bc actual result is **2failed/8passed**, not xfail or
all-green. `await undefined` erroneously fulfills; the visible chart stays blank.
The separate four oracle controls pass, proving that missing promise, false fulfill
and missing declared error cannot silently pass. The real failed resource ERR_FAILED
fixture events are recorded separately from page ReferenceErrors and UX assertions.

Both negative cases retain correct safe accessible data tables, reachable by
focusing the real summary and pressing Enter. Both local-runtime controls resolve
real promises/render actual graphics with0console/pageerrors; captures are inspected.
Raw observations distinguish failure status, ARIA/loading/error DOM, spec/data
fallback, implicit-await outcome, observer deadline and literal values. No generic
HTML-existence or screenshot-existence-only pass. Run live tests only with explicit
actual evidence; missing evidence is an error, not a skipped or invented browser run.

Known limit: small bars only, one browser/environment, direct tool invocation not
end-to-end DeepAgent/provider/paid-model flow. Source fixes, final frozen-source
full gates/CI, all kinds/engines/themes and all-offline support remain separate.
The minimal owner proposal is to establish the readiness Promise before executing
renderer callbacks, route sync and async failures through the same catch, keep
safe fallback discoverable and provide an actionable accessible DOM error. No fix
is applied in this evidence-only branch; R04 owns integration and issue decisions.
