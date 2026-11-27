# R10-16 bounded finite-overflow SUM handoff

Owner/session: `ses_de567808bffdXko8hyKFRhPv77`. Released producer base: `6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce`. Own branch: `agents/r10-16-finite-overflow-fix`. R07 scoped release/R10 own-branch publication/R13 same-ID recovery; no spawning, installs, shared branch or issue/PR mutation.

## Immutable source handback

**`ec9f669eff28cd5351da142765b7755e3b2f484f`** — `fix: retain bounded finite sums after transient overflow`; parent exact6d0e72e. Only released files:

- `python/deepviz/src/deepviz/normalize.py`
- `packages/deepviz/src/normalize.ts`
- NEW `python/deepviz/tests/test_r07_finite_overflow.py`
- NEW `packages/deepviz/test/test_r07_finite_overflow.test.mjs`

Explicit four-path staging, whitespace/allowed-path/credential-pattern checks all exit0/zero secret matches; commit0. Fresh GCM memory-only authenticated GitHub GET verified `sandeshbagmare`, expected repository/push permission, own branch absent. Explicit non-force own-branch push0, `git ls-remote --heads origin refs/heads/agents/r10-16-finite-overflow-fix`0, authenticated postpush GET200 at2026-11-27T13:58:43UTC all verify exactec9f669. PR31 open/draft/unmerged5340; no issue/PR writes.

**Both normalizers handed back to R04. No further role16 source/test edits under this release.** R04 may inspect/cherry-pick source commit and continue queued GraphQL/scalar/owned-iterator fixes. Root coordinates independent01 review; author evidence is NOT independent approval. This later documentation checkpoint is separate from the four-file integration commit.

## Fix and bounded-state rationale

Existing ordinary compensated sums and mean/count/sampling paths remain. On first overflowing SUM, promote current total+compensation+new value to one integer in units2^-1074, then add subsequent contributions there; final conversion rounds once. No input/partial list or overflow-key set. Group eviction transfers the same exact state and existing cost accounting. True unrepresentable final sums remain warned JSON-safe null; finite final cancellation no longer becomes warned null.

- TS finite binary64 input in these units has<2098bits; safe-integer input_count bounds one accumulator to<=2151bits. Reserve512bytes BEFORE retaining it, with unchanged group state overhead and a fixed8byte synchronous decoder. Binarystring/rounding temporaries are bounded; tie-to-even final rounding precedes rescaling. No await occurs during shared decoder access.
- Python uses an existing state slot and SUM-only exponent sentinel-1074, disjoint from mean's nonnegative scaling exponent. Existing `_store` dynamic retained/count/serialized-size guards remain; Python exact-int fastpath unchanged. Arbitrary Python integers are not described as fixed binary64 state. No universal correctly-rounded promise for every pre-promotion compensated sequence.

Author review traced all callers: Python normalize→_Reducer and TS normalize/normalizeStream→Reducer; no schema/model/render/tools/dependency/existing-oracle changes. This state-budget argument plus strict public early-abort controls is NOT an observed10M/OS-memory result.

## Actual commands and results

All commands ran in existing own temp worktree with readonly shared `.venv`, own `PYTHONPATH=python/deepviz/src`, `PYTHONDONTWRITEBYTECODE=1`; npm PATH uses readonly shared node_modules/.bin. Unique adjacent `...-artifacts` keeps raw logs/XML, no dataset copies. Full sanitized source/build/command-result/hash/failure/skip manifest: **[summary.json](../evidence/R10-16/summary.json)**, SHA256`40c77f153bb489529daf1b41354f4e33890270c8b0535cdace0617b26ee21269`, collector0,4/4working/committed source-test bytes identical,28rawlocal log/XML hashes. Detailed live MAIN report preserves every pre-work/meaningful/failure/commit checkpoint; this is its portable handoff.

| Actual command/check | Result |
|---|---|
| BASE `python -m pytest python/deepviz/tests/test_r07_finite_overflow.py -q -p no:cacheprovider --basetemp <own>/pytest-red-corrected --junitxml <own>/python-red-corrected.xml` | 11failed7passed0skipped12.58s exit1 before source edits; independent Fraction/literal oracles |
| BASE own `tsc.cmd -p packages/deepviz/tsconfig.json`; `node --test packages/deepviz/test/test_r07_finite_overflow.test.mjs` | build0;11failed7passed0skipped2971.0724ms exit1 before source edits |
| Initial fixed18-case suites, own build | Python18passed2.40s/TS18passed1162.0587ms,0failed0skipped/exits0 |
| Final broad Python numerical/resource/format/parity suite (exact file list below) | 1217passed4knownfield-policyfailures0skipped19.65s exit1; allNEW23exact/boundary cases pass |
| BASE0c5source N11field policy (normalizer/models/init/oracle byte-identical to6d0) | Same4key failures/3cell passes0skip exit1, not changed/waived |
| `python -m ruff check python/deepviz/src/deepviz/normalize.py python/deepviz/tests/test_r07_finite_overflow.py`; scoped `mypy` | both0 |
| `python -m ruff check .`; `python -m mypy python/deepviz/src/deepviz` | both0, mypy9source files |
| `npm.cmd run build`; `npm.cmd run typecheck`; `npm.cmd test` | all0; fullnpm269passed0failed0skipped3325.7339ms=246existing+NEW23 |
| `npm.cmd pack --dry-run --workspace @deepviz/agent-toolkit`; `npm.cmd run schema:check` | both0;22file dryrun only; canonical Python/schema/TS defaults agreement PASS |
| `python -m pytest -m 'not scale' -q -p no:cacheprovider --basetemp <own>/pytest-full-nonscale --junitxml <own>/python-full-nonscale.xml` | **45failed3006passed5skipped9deselected3errors262.02s exit1**; allNEW23 and ALL30non-scale performance contracts pass |
| After committing source, ONLY `python -m pytest tests/gallery/test_generate_gallery.py -q -p no:cacheprovider --basetemp <own>/pytest-gallery-committed --junitxml <own>/python-gallery-committed.xml` | 11passed0failed0skipped10.40s exit0; resolves prior5dirty-source provenance failures+3fixture errors, not fullsuitegreen |
| `python -m build --no-isolation . --outdir <own>/python-dist-corrected` | exit1: hatchling.build unavailable, no permitted install, distribution BLOCKED |

Final broad Python command:

```text
python -m pytest python/deepviz/tests/test_r07_finite_overflow.py python/deepviz/tests/test_normalize.py python/deepviz/tests/test_aggregation_semantics.py python/deepviz/tests/test_graphql_contract.py python/deepviz/tests/test_n04_normalize_regressions.py python/deepviz/tests/test_n04_format_guards.py python/deepviz/tests/test_n04_shape_policy.py python/deepviz/tests/test_n19_formats.py python/deepviz/tests/test_n19_format_regressions.py tests/test_n11_resource_policy.py tests/test_n12_authoritative_parity.py tests/test_n12_contract_edges.py tests/test_cross_language_contract.py -q -p no:cacheprovider --basetemp <own>/pytest-numeric-resource-format --junitxml <own>/python-numeric-resource-format.xml
```

Full failure/error/skip names and30performance outcomes are in the manifest. Baseline failures include AntV old structure expectation, N17observation,10Vega-title/20ECharts-axis acceptance cases,4inspector claim cases,4N11field-name policy cases. All original strict oracles remain unchanged. N11 key cases expect64KiB but base Python field-name limit4096B; no policy repair authorized here.

Skips: two Windows symlink-privilege checks and three opt-in browser engines. Scale:9cases deselected, no100K/1M/10M remeasurement. FullPython was once-started before interruption; automatic completedexit1/PID10080 absent checked once at recovery, no duplicate fullrun/progress polling. Existing dirty worktree preserved, no recreation/reset/provider/auth/service change. Initial NEW Python decorator typo caused collectionexit2, corrected before genuineRED; initial build used wrong `python/deepviz` source argument→exit1, corrected command then hit missingbackend. Both harness failures retained, not product defects/passes.

## Acceptance limits / next action

Genuine shared finite-final cancellation-overflow finding R03-16-F1 is fixed on this immutable source with strict exact/rounding/permutation/group/other-bucket/residual/subnormal/count/mean/null/state-budget controls. No fullgreen, installed-distribution, CI, render paint/semantics, independent signoff, issue closure,10M scale or900issue completion claim. Signedzero/sample membership policy unchanged. No npmci/installs. Final frozen integrated source requires independent review/test/affected-scale verification.

Next: R04 inspect/cherry-pick **ec9f669eff28cd5351da142765b7755e3b2f484f**, obtain root-coordinated independent review/retest, then continue its queued normalizer changes and frozen-source acceptance. This worker's remaining work is only owned report/evidence publication receipt.

### Manifest newline verification correction

The first pre-staging manifest check exited1 because the collector reported its encoded LF-string hash while Windows `Path.write_text` wrote430CRLFs. Investigation confirmed OWN and MAIN files byte-identical, all4product source/test hashes unchanged, indices45/3/5 and30performance outcomes correct. Actual working-file SHA256 is **`8de09181adba377b27332484b91a8fcc10f369349d007b593826e5d030b6d37f`**; the earlier **`40c77f153bb489529daf1b41354f4e33890270c8b0535cdace0617b26ee21269`** is the **LF-normalized/Git-blob** hash (`.gitattributes * text=auto eol=lf`, core.autocrlf=true). Validation must check both explicitly and staged Git blob, not claim the working bytes had the LF hash. No product/evidence-result change, no test rerun, and failed verification retained as own collector-harness error.
