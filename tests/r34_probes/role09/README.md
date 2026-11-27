# R34 role09: fixed c3ee finite-only gates

This is ONE independent review/test lane, not two reviewers or a release approval.
Product source is fixed at `c3ee1edbfc65406cef7fd809f5a6887471d576a5`.
No density342/d017, fullnpm/browser matrix, package install, scale, API or production edits.

## What ran

- Fresh build using existing read-only TypeScript7.0.2; ten tracked files exactly equal Git bytes,19fresh dist files hashed.
- Unchanged source-owner13 unit cases:13PASS/0FAIL/0SKIP.
- Original role13 two strict cases from38ce71e:2PASS/0FAIL/0SKIP. The copied adapter changes ONLY one setup HEAD constant; all raw values,35px heights and common-zero assertions remain byte-identical.
- One new public ±1e308 artifact, two browser carriers SVG/HTML:1PASS/0FAIL/0SKIP; actual literal mark geometry/metadata, all text boxes contained, zero errors/network requests. Both actual PNGs OPENED.
- Initial own preload Windows-path error happened before product cases, retained as0pass/1module-load failure. Fixed only NEW runner setup to file URI. Build/completed tests were not replayed. Final wrapper end-to-end was not rerun; its exact corrected test commands were executed successfully against the same fresh build.

## Portable commands (existing dependencies only)

Use a NEW clean detached checkout at the exact pin, without existing dist. Choose an existing empty evidence directory. Do not run against a dirty producer or overwrite prior observations.

```powershell
$source = '<NEW clean exact c3ee source>'
$tools = '<existing readonly TypeScript bin/tsc>'
$out = '<NEW existing empty own evidence directory>'
$probe = '<this tests/r34_probes/role09 directory>'
& '<existing Python>' (Join-Path $probe 'prepare_and_test.py') --source $source --compiler $tools --output $out
# The preparation runs exactly the13units + original2cases, with Git/raw-hash checks.
$env:R34_SOURCE = $source
$env:R17_13_SOURCE = $source
$env:R34_EVIDENCE = $out
$env:R34_PLAYWRIGHT = '<existing readonly playwright/index.mjs>'
node --test --test-reporter=tap (Join-Path $probe 'bounded-finite-browser.test.mjs')
```

`source-proof.mjs` verifies the fixed Git SHA, clean tracked state, all ten source/config/test hashes and all19 freshly compiled file hashes BEFORE importing the exact public declared dist/index.js. There is no MAIN editable import or dependency copying.

`prepare_and_test.py` derives the original oracle from the immutable Git object, makes precisely one allowed setup-identity replacement and saves both hashes/original bytes. It never changes an original oracle or production file. The browser probe checks literal geometry, not production helper-derived expected values. Output uses fresh directories/exclusive writes.

Evidence and chronological failures: `docs/coordination/evidence/R34-09/` and `reports/R34-09-finite-only-review-test.md`. R33 consumer work was superseded before code was written; no R33 product result is implied.
