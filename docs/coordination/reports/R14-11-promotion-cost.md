# R14-11 — bounded promoted-SUM cost, counts and state controls

**Observed result, not final scale approval:** 24 fresh Python workers recorded 15 exact matches, 5 genuine reference SUM failures and 4 early budget rejections. **All 10 candidate full-stream runs matched the exact oracle.** Own 46 controls, Ruff and mypy passed. No 1M/10M, full suite or TS runtime was executed. Sources were immutable 6d0 and ec9 Git objects, not dirty files.

Owner: `ses_de567811cffdTBwcb8pF5nDi9v`, same native ID confirmed. Read full R14 common contract + role11, current MAIN checkpoint/RESUME/STATE/own note and full R10-16 producer report. Existing own branch: `agents/r10-11-python-scale-envelope`, clean starting commit **`0c2ce740b353cb87b52f690c365b21049326d3f7`**. Initial MAIN HEAD was 5340; no final freeze.

## Authorized scope and source

Writes are limited to NEW `tests/r14_probes/role11/`, this report, `evidence/R14-11/`, the actual-ID note and own scoped branch publication. No production, existing oracle, schema, environment, sibling, issue/PR or shared-candidate edits; no installs or spawning. Reviewer01 covers source correctness; collision/lifecycle lanes remain separate.

Reference: **`6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce`**. Candidate: published producer source **`ec9f669eff28cd5351da142765b7755e3b2f484f`**, parent 6d0. Role16 had handed source ownership back to R04 before this experiment. Its observed worktree HEAD 0e0748a was a documentation follow-up, not our source pin. The harness copies exact Git object bytes and verifies imported modules before/after; any change invalidates evidence. No moving producer snapshot or polling was needed.

One exploratory lookup guessed a nonexistent R13-16 report; the actual R10-16 report was then read in full. This was a lookup miss, not a test failure.

## Plan / acceptance before implementation

1. Read the producer's 23 Python and 23 TS controls and both normalizer diffs; do not duplicate its full suite.
2. Write strict oracle/count/source-guard tests before the new harness; reuse the existing OS peak helper.
3. Measure ordinary and transient-overflow SUMs against tiny closed-form oracles, lazy inputs, exact exhaustion/counts and explicit loss metadata, **at most 100K rows per worker**. Include actual state-budget rejection.
4. Preserve actual reference failures, candidate results, module identities, timing/memory methods and limitations. If source changes, stop rather than relabel or poll.
5. Run own lint/types/negative controls and publish only scoped work. R04 owns integration/final frozen-source reruns.

## Historical pre-work checkpoint

This report and own note were saved before implementation. The prior 55 passes/9 deselected and original 20 fresh workers/44,404,040 rows remain unchanged historical evidence, not new experiments. Full CI/final-source/900 acceptance remains unmet.

## Source/control inspection and genuine own-harness RED

Read both actual 23-case producer files and the full two-normalizer diff. Producer source/test paths were clean, and later byte readback proved both read test files matched immutable ec9. Python uses one budgeted integer and sentinel -1074; TS charges bounded BigInt state. This is context, not borrowed author approval. The new runtime experiment is **Python only**.

First own TDD check: `pytest tests/r14_probes/role11/test_promotion_probe.py -k exact_result_matches -q -p no:cacheprovider` → **exit1, 1 failed/31 deselected, 0.20s**, missing-harness assertion before implementation. Unique artifact root: `C:/Users/bagma/AppData/Local/Temp/opencode/r14-11-promotion-ses_de567811cffdTBwcb8pF5nDi9v-artifacts`; log `probe-red.log`.

Fixture: six terms `[M, M, g+1, -M, -M, 3]` have exact sum `g+4`. Ordinary `M=1e16` stays finite; `M=1e308` triggers promotion but has the same finite final sum. Four groups form 24-row cycles; any remaining rows (16 at 100K) explicitly contribute zero to g0, never disappear. Counts are 96/6,000/100,000, with three fresh 100K workers and one per smaller count. The oracle is closed form; tiny six-term `Fraction` checks exist only in unit tests, never per measured input. The own pull counter is lazy; existing `peak_memory` and `load_api` helpers are reused. State tests use unique keys with 2,048-byte padding and max_points=100000 under the unchanged 16MiB budget, not an injected limit.

First GREEN: 32 passed/0 skipped in 0.33s, Ruff0. Mypy initially exited1 with four own typing errors (optional `module.__file__` and inferred heterogeneous dictionary mutation). Corrected only explicit filename assertions/type annotations, preserving every oracle. Before measuring, all 32 tests passed again in 0.39s; Ruff/mypy exited0.

## Actual bounded experiment checkpoint

One actual matrix invocation exited0 with **24 fresh-process observations: 15 exact matches, 5 reference promoted-SUM oracle failures and 4 early state-budget rejections**. Collector `observations_complete` means all observations were captured, **not 24 product passes**.

All 20 full-input runs exhausted exactly their requested counts (1,224,384 aggregate rows). Including four early errors gives 1,403,326 total observed pulls, **not one 1M-row run**. Raw `<artifact-root>/matrix/matrix.json` is 111,022 bytes, SHA256 `881df1c7313ba783b85263da100f6c22d97c54f593fdf33ef96d13ca9533ba7c`. Every worker records actual imported module paths, unchanged before/after file hashes and zero snapshot dirtiness. No producer full suite, TS runtime, original scale replay, 1M or 10M run occurred.

At 100K the exact four outputs (g0..g3) are 16,664/20,830/24,996/29,162 for both ordinary sources and candidate promoted sums, with no warnings. All five reference promoted runs instead return four NULLs and `4 non-finite numeric values replaced by null.` despite finite expected values. These remain genuine product failures.

Candidate promoted 100K median was 2.0407962s, versus 1.1501817s ordinary (1.7743×). Reference promoted median 1.0405092s computes wrong values; it is not an acceptable faster implementation. These are concurrent-host observations, not universal regression thresholds.

State rejection pulls: reference ordinary 45,715; reference promoted 45,715; candidate ordinary 45,715; candidate promoted 41,797. Each reports `ValueError: Normalized retained data exceeds 16777216 bytes`, without exhaustion or a result. Earlier candidate promoted rejection is consistent with extra charged state, not an RSS ceiling. On errors, result counts/strategy/warnings remain unavailable, not fabricated.

The next step was independent evidence verification, not another measurement.

Second TDD RED: `pytest tests/r14_probes/role11/test_evidence_guards.py -k real_receipt -q -p no:cacheprovider` → exit1, 1 failed/13 deselected in 0.27s, missing-verifier assertion (`verifier-red.log`). Implemented only the independent checker/compact receipt, not a changed measurement harness or rerun.

## Independent evidence verification and observed cost

Raw and compact verification both exited0 (including actual standalone CLI executions). Own controls: **46 passed/0 failed/0 skipped/0 deselected in 0.22s**, Ruff0, mypy0 (4 files). Thirteen altered-evidence tests reject missing workers, fake OS memory, negative time, incorrect peak deltas, wrong/changed/dirty source, wrong imports, counts, values, hidden loss/reference failures and late rejection. These are harness tests, not 46 product acceptance passes.

Portable `docs/coordination/evidence/R14-11/bounded-matrix.json`: 33,080 bytes, SHA256 `babe1cae3a7c74bb0f34613883b2d8f6e0a858c8eba370ea80c7bea4df6e0439`, explicit UTF-8 LF. It deduplicates identical source manifests via canonical-JSON SHA256 references while preserving every worker's values, counts, warnings, time and OS peak. `check-results.json` records commands/exits, JUnit/log hashes, methods and limits. Executed measurement harness bytes remain unchanged.

|Source/case(100K,threefreshworkers)|Normalizationseconds(each)|Medianseconds|InclusiveOSpeakbytes(each)|Oracle|
|---|---|---:|---|---|
|6d0ordinary|1.105723/1.074407/1.444753|1.105723|41,566,208/41,525,248/41,635,840|exact4groups|
|6d0transientoverflow|1.167920/1.040509/1.018093|1.040509|41,746,432/41,766,912/41,947,136|**RED:fourNULL**|
|ec9ordinary|1.129817/1.150182/1.207433|1.150182|41,713,664/41,545,728/41,811,968|exact4groups|
|ec9promoted|2.119443/2.003692/2.040796|2.040796|41,615,360/41,607,168/41,717,760|exact4groups|

Candidate ordinary median was 4.02% above reference. Three fresh repeats, fixed job order and a concurrently active Windows agent host cannot attribute that difference as an algorithmic regression or define universal performance bounds. Promotion has an observed cost while correcting finite-sum data loss.

Maximum inclusive peak minus the corresponding 96-row peak: 466,944/172,032/90,112/266,240 bytes, respectively. State-case peaks were 61,112,320/61,554,688/61,423,616/60,395,520 bytes. These fixed-four-group observations and early byte-budget errors are narrow evidence; the 16MiB payload budget is **not process RSS**, nor proof for every width/cardinality/native allocator.

## Measurement / exact replay

Windows `GetProcessMemoryInfo.PeakWorkingSetSize` provides fresh-process inclusive lifetime working-set high-water bytes, including interpreter/imports/native allocations/validation. Baseline is the process peak after imports/source checks; its difference is **not exclusive operation allocation**. `perf_counter` times normalization and lazy row generation, excluding imports/hash checks/oracles. Worker wall time separately includes launch/import/provenance. Each worker has one lazy iterator, no length hint or input materialization, and no `Fraction` per input.

Executed commands, own branch and read-only shared interpreter, no installs (actual artifact root named above):

```powershell
$PY='C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe'
$ART='<NEW unique external directory>'
& $PY tests/r14_probes/role11/promotion_probe.py --artifacts "$ART/matrix"
# Exit0; 24 observations; immutable 6d0/ec9 copies; 96/6000/100K only
& $PY tests/r14_probes/role11/verify_promotion_evidence.py "$ART/matrix/matrix.json"
& $PY tests/r14_probes/role11/verify_promotion_evidence.py docs/coordination/evidence/R14-11/bounded-matrix.json
# Both exit0: 24 workers, 15 exact/5 reference RED/4 early errors
& $PY -m pytest tests/r14_probes/role11 -q -p no:cacheprovider --strict-markers --basetemp "$ART/tests" --junitxml "$ART/tests.xml"
& $PY -m ruff check tests/r14_probes/role11
& $PY -m mypy tests/r14_probes/role11
# 46 passed/0 skipped/0 deselected in 0.22s; Ruff0/mypy0
```

Normalizer SHA256: 6d0 `0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83`; ec9 `34e8ed94a479acb2d7360a79ba4f62897bb453928fc1eec97efceb052a5e76f2`. Actual loaded normalize/models/render/engines/init all resolve inside the requested snapshot. Final readback compared all 10 copied Python files per source directly with immutable Git objects; every byte matched. No dirty/current-source relabeling or borrowed reviewer approval.

Next worker action: stage/review/publish only 8 own paths (note/report/4 NEW probes/2 compact receipts), then verify exact remote SHA and save the MAIN receipt. R04 still owns review, integration and final frozen-source gates. Full production, observed green CI and 900 legitimate created-and-resolved issues remain unmet. Original 20 scale measurements and 55-test baseline are unchanged.
