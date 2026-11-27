# R38-06 independent AntV acceptance

**Actual tested source:** `3185e0d9936c7d6f1a9d30b94089b804d75fe991`, parent `1c721bb6497746641b897eb2eb938cfad52068d2`. This is a non-author execution of the unchanged NEW producer21 unit cases and 21-case/254-check browser matrix. It is not approval of another head, actual main, whole toolkit, full CI or all finite extents.

## Reproduction and provenance

Use a fresh clean isolated checkout at that exact source. Before consumers, verify committed raw bytes of `deepviz/{__init__,models,normalize,engines,render}.py` plus the two NEW producer files against Git, not an editable main installation. Required unchanged producer hashes:

- `python/deepviz/tests/test_r20_antv_color_scale.py`: `a40317240262535b77530f416c90e23f66e2eaba6094309f3aaeb510e9e8a299`
- `tests/browser/r20-antv-color-scale.cjs`: `7099808e852770137f3565a99e96bccf45962b2f042d41402ba4777dfea0f668`

The saved `pre-consumer-source.json` binds all seven files, exact Git head/parent and initial clean tree. `pre-consumer-node.json` binds existing tool paths/versions and G2 bytes. Our `consume.py` runs with `-B -I -S`; it adds only the intended source and existing read-only site-packages, verifies all raw hashes before/after and all five actual imported paths before pytest/emission. It processes no editable `.pth` hook. Pytest plugin autoload is disabled. No install, persistent environment/config write, SDK patch, build substitution or source alteration is permitted.

Exact executed argv/cwd/timestamps/exits are in `evidence/R38-06/{actual-run.json,commands.json}`. Structural command recipe:

```powershell
& $ExistingPython -B -I -S consume.py unit --source $Exact3185 --proof $OwnSourceProof --site $ReadOnlySitePackages --output $UniqueRun
& $ExistingPython -B -I -S consume.py emit --source $Exact3185 --proof $OwnSourceProof --site $ReadOnlySitePackages --output $UniqueRun
node --check "$Exact3185\tests\browser\r20-antv-color-scale.cjs"
node "$Exact3185\tests\browser\r20-antv-color-scale.cjs" "$UniqueRun\generated" $ExistingNodeToolRoot
& $ExistingPython -B -I -S collect.py --run $UniqueRun --evidence $NewOwnEvidence --source $Exact3185 --site $ReadOnlySitePackages
```

`collect.py` reads SAVED results/captures only; it does not import product modules, rerender, navigate or change HTML. It verifies the real CDN G2 response SHA/size, original HTML hashes and 21 unobserved/constructor-observed PNG pixel-identical pairs. It copies original screenshots, never generates stand-in chart images. OPEN actual copied production PNGs through an image reader; a pixel/hash check is not visual signoff. Do not rerun completed matrices just to republish receipts.

## Actual bounded result

- NEW producer unit: **21 passed / 0 failures / 0 errors / 0 skips, 0.42s**, exit0.
- Public emitter: 21 fresh fixtures, exit0.
- Browser: **21 cases / 254 passed checks / 0 failed / 0 skipped**, exit0, 43.984s.
- **42 real navigations**, no routes/interception/fake CDN, ready resolved in every production/constructor-observed page, **zero console/page/request errors**.
- All42 genuine G2 5.4.8 responses HTTP200, **1,083,414 bytes**, SHA256 `7e7d346cab68c002a889dc6145bfc1f9ae1391be82ce8d514fb106ef3a6e6412`. Node26.13.1 / Playwright1.65.1 / Chromium159.0.8154.6. This observes those actual requests, not indefinite CDN health/offline acceptance.
- Actual category marks match actual visible legend keys; true negative/signed/constant/zero/missing values and cell grids retained; full finite-extent labels inside real canvas. Ordinary line/scatter spacing/colors and parent-child background controls retained. Ten original production PNGs actually opened; detailed observations and hashes in `visual-readback.json`.

Missing-value `output_count` counts retained normalized records, not painted cells: missing fixture3→3 retains null plus omission warning but paints2cells; all-missing2→2 retains warnings and paints0cells. Gauge input1/output1 produces a declared Value37/Remaining63 native composition. No fake cell or synthetic input-row claim.

No production/config/schema/original oracle/dependency changes. No old670/130/all-engine/npm/scale tests or package builds. Known old root-line/view representation failure and unrelated COUNT/normalizer issues were not rerun or waived; current scope does not repair them. Larger/extreme/denser/new-source/browser/interaction/whole WCAG/full distributions/current-main CI remain outside this bounded acceptance. R04 owns integration and any required affected gates on an actually integrated source head.
