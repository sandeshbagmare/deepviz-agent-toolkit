# R24-06: eight strict finite-domain non-bar cases

Independent tester/non-author; tested product source **`5e595a8f893955ce34a0e26553bb7bf257ea93ae`**. This is the same finite-range cause already demonstrated by role13's two bars, not a new bug filing. Production and old oracles are untouched.

## Exactly what runs

- Eight public `render(...,'svg')` cases, four rows each at960×520; four ordinary positive controls and four signed extremes. Line isolates extreme y, scatter isolates extreme x, area/bubble exercise both. ±1e308 and±5e307 stay finite and original normalized data/counts/order/warnings are checked independently.
- One actual Chromium HTML page per case, not a fake response or screenshot-only pass. Full nativeSVG strings/coordinate counts/finite values are checked before the DOM can sanitize NaN to0 or erase a polyline. Actual DOM marks, pixel positions, ticks, titles, accessible table, readiness and all console/page errors are retained.
- Expected fractions are literal quarter/midpoint/endpoints and1:1:2x-gap ratios. **No `(input-min)/(max-min)` or copied renderer scale formula** appears in the oracle. Only bounded pixel extents of the actual finite axis are interpolated. Area closures share literal zero; explicit zero samples must hit the midpoint in signed cases. Bubble radii are separately literal7.5/15/22.5/30.
- Exactly two area screenshots (control/extreme) were captured and opened with the image tool. No old33-fixture/1403-check replay, category-density matrix, other engines, scale, builds or installs.

## Actual strict result — NOT green

`node --test --test-reporter=tap tests/r24_probes/role06/finite.test.mjs` exited**1**, **4passed/4failed/0skipped**,7364.3565ms.144checks112pass32fail. Four successful artifacts contain invalid or collapsed geometry; no honest explicit rejection occurred. Eight SVG parse console errors, zero page errors and external requests; the zero-browser-error gate **FAILS**. Native readiness true/empty deepvizErrors do NOT certify valid geometry. Both opened images are published: valid control area and blank extreme area with collapsed ticks.

All four original executed `.mjs` hashes are pinned in `identity.json`; collector was added after the one actual run and never reruns product/browser cases. `collect.mjs` verifies saved measurements and18rawartifact hashes only. Numeric NaN observations serialize as JSONnull, but original raw SVG/attribute strings still contain literal`NaN`; no error evidence is lost or reclassified as valid finite data.

## Portable exact-source retest

Do **not** replay baseline now. Root will supply producer12's actual future committed repair; none was received/tested in this checkpoint. Reuse the unchanged eight-case fixture only against a clean immutable source and a genuine matching build manifest. The existing baseline reuses the proven R18 own build with11source/configGitblob+working hashes and19compiled hashes, without a rebuild.

Child-only environment (the runner requires a NEW output directory):

```text
R24_SOURCE=<clean immutable exact-source worktree>
R24_EXPECTED_SHA=<actual 40-character committed product SHA>
R24_BUILD_PROOF=<genuine matching build identity JSON>
R24_OUTPUT=<NEW unique own output directory>
node --test --test-reporter=tap tests/r24_probes/role06/finite.test.mjs
```

For baseline use `docs/coordination/evidence/R18-06/identity.json` and exact5e. For a **received** repair, independently build only that new clean exact source using already installed tooling and record actual command/exit/output and source/compiled hashes. Supply a matching identity JSON with `source_sha`,11`sourceProof` entries (`file`,`git_blob`,`working_sha256`) and19`buildProof` entries (`file`,`sha256`). A copied5e manifest fails immediately on a repaired SHA. No dirty producer import or inferred build provenance is accepted. The public entry is realpath-checked and imported from that worktree's `packages/deepviz/dist/index.js`; tests are not silently pointed at this older evidence branch's source.

A clearly identified `ValidationError` for unsupported finite layout BEFORE artifact return may be separately reported as **honest explicit rejection**, never as rendered success; ordinary positive controls must still render correctly. Successful blank/collapsed/NaN output or any browser error remains strict RED, with no skip/xfail waiver.

After a real repair retest, write new evidence rather than replacing the original RED. The baseline-specific `collect.mjs` intentionally asserts its4RED/8errors receipt and is not a post-fix acceptance command. Report actual changed/failing totals and inspect at most two representative images as separately authorized. Full candidate/CI/four-agent approval and prior AntV RED remain out of scope.
