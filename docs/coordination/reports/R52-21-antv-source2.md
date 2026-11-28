# R52-21 AntV SOURCE2 and finite-scale deduplication

## Scope and exact source

Owner: role21, ses_de5678018ffezK8JGDUaSzvcWn. Own branch: agents/r10-21-recovery-git-bootstrap, starting at a3c972fd0525a980b1168a2b1dc613f52cc07758, clean before this report/evidence. Main-bound target: AntV/renderer lane, planned PR4; actual PR UNKNOWN.
Assignment: second non-author SOURCE2 and finite-scale dedup only, bounded source proof. No product imports or edits, test/oracle edits, old matrix replay, issue/PR/merge action, or product test/browser run.

Product target is exactly 4429f0521612b97eee3790f0d8d0fbc3cad3f8be, parent 3185e0d9936c7d6f1a9d30b94089b804d75fe991.
git diff --name-status shows exactly three paths: python/deepviz/src/deepviz/engines.py, new python/deepviz/tests/test_r45_antv_subnormal_heatmap.py, and new tests/r45_probes/role17/native.cjs. Production change is only 19 added lines at _antv heatmap lines 694-712; no deletions.
Exact Git blob IDs, SHA-256 values and byte counts for every changed path and connected caller are in evidence/R52-21/source-proof.json. The production engines.py parent blob is d3e437ee1688e4bdff86274a8f4fc6504777246a, SHA-256 d519700c20007009ffffb6e8343696c30335949b0df798aa4a83ac8b0025fc29, 44787 bytes; target blob is 05d2fc411333bf36e72cfd538aab1397f90c47c6, SHA-256 2b83e10c82fbf2705db16c4a5e5fc6a28ef3c68fb86ab6add4dd5aa99bffe4ad, 45877 bytes.
AST comparison proves the other 22 top-level functions, imports and module statements are identical; render.py, models.py, normalize.py, and existing AntV tests have identical Git blobs at both pins.

## Finite-span disposition - one deduplicated issue candidate

Prior exact-3185 observations are one failure mechanism, not separate issues: role18 R38-18-F1 used [-MAX,0,+MAX]; role21 R39-21-F1 used [-1e308,+1e308]. Their actual G2 linear-scale evidence records high-low = Infinity, invalid/NaN upper normalization/color, and no browser runs. R39 negative control [-7,-2] mapped correctly. Original reports and fixtures were read, not replayed.
At target lines 694-700, when span is non-finite, the new scale inserts low/2 + high/2 and three palette stops, keeping raw _heat values unchanged. Arithmetic-only checks for both +/-MAX and +/-1e308 produce midpoint zero and two finite adjacent spans. At lines 701-709 the legend switches to unit coordinates while preserving literal endpoint labels and domainValue. This statically addresses the prior infinite-segment cause. It proves arithmetic/native-spec construction only, NOT G2 mapping, painted cells, legend layout or browser behavior. The independent role05 exact-head report is separately attributed; no author results are borrowed.
A related boundary was checked rather than guessed: constant minimum-subnormal input hits existing padding = abs(low) * .05 or 1 at lines 685-688. An underflowed zero padding falls back to 1; no zero-span reciprocal occurs in that case. Standalone arithmetic proof is evidence/R52-21/constant-min-subnormal-arithmetic.json; it is not a product test and yields no finding.

## Separate painted blocker retained

Do not close or merge the scale arithmetic and painted-layout results. Role05 prior independent exact-head R51 report R51-05-F1, P2, reproduces [-sys.float_info.max,+sys.float_info.max] at legal width240, height520: actual G2/Chromium output had two marks and zero browser errors, but endpoint label boxes overlapped 98.98046875px and the right label ended at x=299.746px, outside the 240px canvas. Evidence is evidence/R51-05/minimum-width-max-label/label-bounds.json; full report and evidence SHA are in prior-evidence-manifest.json. It points to engines.py:710-712. This is a real painted legend-layout defect, distinct from native high-low overflow, and remains OPEN for R04; arithmetic source clearance does not waive it.
Keep earlier R38-17 subnormal blank-heatmap report as its own baseline: four finite subnormal values produced zero cells on 3185; its internal cause was explicitly unconfirmed. The 4429 author report says its affected suite passed; role05 non-author exact-head report says original strict subnormal cases passed during its 10-case run. I did not replay either suite or claim a new painted result. Preserve these records; R04 decides closure from exact independent evidence. Do not merge subnormal layout with finite-span overflow.

## Connected-source safety and evidence

Changed code operates only on bounded _antv data already produced by normalizer/geometry; no record mutation, filtering, HTML sink, filesystem path, callback, URL ingestion, executable schema, new import or dependency was added. Connected render.py/safe_json and current AntV backend tests are byte-identical to parent; existing original tests untouched. Static review found no new data-loss, HTML-injection, traversal or memory-growth path in this 19-line hunk. This is scoped source review, not approval of other chart kinds, full toolkit, packaging, CI or release.
Evidence: source-proof.json (Git identities, diff, AST, connected blobs, arithmetic derivation); dedup-disposition.json (explicit finding separation/status); prior-evidence-manifest.json (hashes of exact MAIN reports/evidence read); constant-min-subnormal-arithmetic.json. Prior hashes are provenance only, not reproduced behavior.

## Verdict and handoff

SOURCE2 review completed; candidate disposition REQUEST CHANGES. The second non-author review gate is satisfied as a review handoff. Prior role18/R39 MAX cases deduplicate to one finite-span issue candidate whose arithmetic is changed by 4429; no new native/browser pass is claimed. Known exact-head role05 width-240 painted label defect remains a separate OPEN P2 blocker, so this is not candidate merge clearance. Main PR number, issue number, CI and default status remain UNKNOWN/not verified.
Next owner: R04, sole integration/PR manager. Read this report/evidence; preserve R51-05 label clipping as separate; decide issue dedup/closure for native MAX-span candidate and subnormal baseline from exact existing reports; route a minimal authorized label-layout repair if required, then require fresh exact-head non-author source/tests and current CI before integration. Remaining effort UNKNOWN.

## Exact commands and limits

- Read-only Git object existence/status/log/diff/show/rev-parse checks: product objects exist; target diff three paths and all target blobs/hashes captured.
- python -B docs/coordination/evidence/R52-21/source-proof.py: exit0; 22 protected functions and module statements unchanged; no product import/runtime.
- python -B docs/coordination/evidence/R52-21/build-evidence.py: exit0; hashes and dedup receipt generated.
- python -B docs/coordination/evidence/R52-21/prior-evidence-manifest.py: exit0; exact MAIN files hashed.
- Standalone Python floating-point arithmetic check: corrected run exit0, four assertions true; confirms the existing or-1 constant-domain fallback, not product behavior.
- Harness errors preserved: initial arithmetic expectation exit1 was wrong because lines685-688 fall back to padding1; corrected arithmetic has no finding. First source proof path locator used wrong parent (FileNotFoundError exit1); corrected locator produced exit0. PowerShell Get-FileHash InputStream misuse exit1; Git blob hashes were used instead. These were harness/setup errors, not product failures.
- NOT RUN: product tests, public render, G2 runtime, browser, PNG, scale/10M benchmarks, build, CI, PR/API/issue/default queries. No tests counted as skipped or passed by this review.
Exact machine-readable command inventory: evidence/R52-21/verification-results.json. Static and arithmetic command exits are recorded there; product tests=0, browser=0, build=0, CI=0; test skips=0 because no product tests were started.
A first mirror check ran after creating verification-results.json and correctly found that one new file had not yet been copied to MAIN (verification harness exit failure, not product). The missing own evidence file was copied; a follow-up Python SHA-256 comparison verified all eight owned R52-21 evidence files byte-identical between the work branch and MAIN. No other path touched.

OWN publication: commit 9fdf63a97ef6bf070513fe104d6da77362564dca on agents/r10-21-recovery-git-bootstrap; non-force push exit0 and immediate ls-remote exact readback exit0 at 2026-11-28T00:08:28.6346965Z. Exact receipt: evidence/R52-21/publication-receipt.json. Product source remains unmodified. No PR/CI/merge/default approval.
