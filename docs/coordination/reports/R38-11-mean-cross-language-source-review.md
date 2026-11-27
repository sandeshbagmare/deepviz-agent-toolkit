# R38-11 - cross-language mean SOURCE and cost review

**What this change does:** Both normalizers now keep one exact numerator in units of the smallest binary64 subnormal, then divide by the valid observation count at emission. This avoids overflowing/subnormal-rounded intermediate means and retains weighted other-bucket contributions without retaining input history.

**Verdict: fix finding 1 first. REQUEST CHANGES on exact c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19.** The TypeScript rounding/state implementation has no additional material defect found by this source review, but Python rejects a valid two-record integer mean because internal accounting converts a widened integer to decimal. No author pass, newer546c handback, final CI/main or wholetoolkit approval is borrowed.

## Must fix

### 1. [P2] Mean state accounting rejects accepted large integer inputs

**R38-11-F1** - new path `python/deepviz/src/deepviz/normalize.py:627-629`, connected `_store:584-591` (especially587), `_sum_units:565-568`. Accepted-input contract/scalar/byte accounting:388-407,426-441,687-705.

- **What this is:** Each numeric mean observation is now shifted into integer units of2^-1074. The existing retained-state helper measures a wide integer by constructing its decimal repr.
- **Problem:** Accepted input10**4000 has4001decimal digits; its internal shifted numerator has4324digits. On ordinary Python with the default4300digit limit, repr fails before the second opposite observation can cancel it. Two input records total<16KiB and have exactly representable mean0, but the public operation raises ValueError. This is not input exceeding the256KiB record or16MiB retained-state budget. The public Python contract explicitly supports integer reductions beyond JS-safe range; no cross-language precision outside that range is being demanded.
- **Smallest fix direction:** Charge wide integer state conservatively from bit_length without requiring a giant decimal conversion. Preserve current payload caps and accepted input support; do not disable interpreter digit protection, expand budgets, coerce away values or weaken the strict regression. R04/the sole normalizer owner decides the source implementation.
- **If skipped:** A valid Python mean that should produce0 aborts at accounting rather than returning its bounded result. The new exact numerator adds a hidden input restriction unrelated to documented payload limits.

Actual new two-record reproduction on immutablec1b, without changing interpreter settings:

```python
from deepviz import normalize
big = 10**4000
normalize(iter([{"g": "only", "v": big}, {"g": "only", "v": -big}]),
          {"x": "g", "y": "v", "aggregation": "mean", "max_points": 10})
# Expected records [{"g": "only", "v": 0.0}], input_count2, warnings[].
# Actual ValueError: Exceeds the limit (4300 digits) for integer string conversion
# normalize.py728 ->629 ->587 len(repr(internal_numerator)).
```

Own strict NEW `tests/r38_probes/role11/test_large_integer_mean.py:7-16`: **1failed /0passed /0skipped /0errors /0deselected**,0.23s pytest,0.3404386s driver wall,exit1. Input JSON<16384bytes is asserted before the call; expected0 is independent exact cancellation, not production-computed. No input dataset committed. No old oracle/source/global digit limit edited. Internal numerator has14362bits; integer comparisons independently prove4324decimal digits without requesting its repr. This is separate from the known scalar-column/protocol, GraphQL error-carrier and prefix-SUM residual failures. Later546c was NOT reviewed or declared fixed here.

## Exact source, scope and protected code

Owner/session ses_de567811cffdTBwcb8pF5nDi9v, independent second cross-language reviewer11, distinct reviewer01 Python-focus lane. Read FULLMAINR38common+11(33lines), currentAGENTS51, canonical latest, fullown158line checkpoint before work. Existing OWNbranch agents/r10-11-python-scale-envelope cleanab4a0c53fd339315f1e457c70c6da88ab10e64d9. R39 saved reservation/admission is root's reported evidence, not a worker spawning/count claim.

- Reviewed source **c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19**, parent79232fb2f402bf21d455fbc021f1c238d19abe80. Full4pathdiff read:27lineTS/17linePython algorithm changes plus new producer controls,118insertions20deletions overall.
- Git-LF Python normalizer SHA256 **f3cc6e78e188ed97f62133a954154dbfdd416128c97cd4b154144ae62f778296**; TS **7e10c7a686044532ffe21b9fcc79aabed1c5d1ed953fdee12be4b2de3eec9c15**.
- CompletePythonpackage, TSsrc, exact configs and both producer control files copied from Git into unique external snapshot24files. All24hashes checked before/after the one counterexample and again against Git at evidence packaging. Same-process actual normalize module path/hash asserted before pytest; Python-S with explicit snapshot and readonly existing sitepackages, no editable hooks/wrong MAIN module.
- Full Python AST/source proof: only _Reducer.add/finish change; all other top-level functions (including _scalar/_records/_plan/_sum_units/publicnormalize) and _Reducer.__init__/_store are byte-identical to parent. No parent source was executed or baseline PASS invented. The parent diff explains why previously ordinary state accounting is now reached with a larger internal integer.

## Full cross-language and connected-source review

**TypeScript** `packages/deepviz/src/normalize.ts`:1-115 budget/string/warning/carrier/publiccontract context,250-329 selection/flatten/scalar filtering,330-356 shared sumUnits/sumFromUnits/new meanFromUnits,358-537 COMPLETE reducer state/update/group-transfer/reserve/finish,539-557 actual sync/async public consumers. `models.ts:1-97` scalar/result/spec types and runtimevalidation read. Full changed helper/update/finish delta and complete NEW42line producer test file read. No TS product build or runtime test was run in this source lane.

**Python** `normalize.py`:1-75 publiccontract/constants/imports,320-441 record expansion/scalar/input-byte policy,430-776 flatten/_records/_plan/shared units/COMPLETE reducer/publicnormalize/warnings. Complete new producer mean test additions read: ten literal scenarios x records/onepass, Fraction-based independent expected and signedzero assertion, plus valid-count weighted-other case. Neither language's producer PASS totals are our evidence; no producer/full-format/oldSUM matrix replay.

### Rounding/conversion proof and costs

- TSsumUnits330-336 decodes binary64 bits into exact integer subnormal units. Max finite binary64 is2098unit bits. Overall input_count is checked safe-integer at383-384 before reduction, so valid group count<=2^53-1 and numerator<=2151bits. Independent integer calculation confirms these bounds; no empirical time/RSS claim.
- New TSmeanFromUnits348-355 obtains quotient bit-length after count division, shifts only enough to keep53significand bits, then uses exact remainder/tie parity for nearest-even. Rounded integer<=2^53 (including carry) converts exactly to Number; multiplier exponent spans-1074..971 for finite binary64 averages. It avoids an overflowing Number numerator and an early rounded subnormal quotient. Negative underflow uses the preserved numerator sign to yield-0. Exact total0 has the ordinary zero numerator in both languages.
- Python565-568 converts accepted int/float values exactly to units. New mean629 retains that numerator and667-671 divides by(count<<1074) directly at finish, avoiding prior scaled floating partials. This numerical path is sound for bounded finite-double states, but its unchanged decimal _store accounting produces finding1 on larger accepted Python ints. Python integer/count width is not globally fixed2151bits; it grows with accepted integer size/logcount and must remain safely budget-accounted, not silently narrowed to TS.
- TSmean468-471 charges512bytes BEFORE first retained wide state; exact subsequent updates do not charge again. <=2151bits is269payload bytes, with separate key/base/count/state charges;512is a budget convention, NOT a measured RSS/allocation ceiling. Python_store checks computed retained delta before assigning state. Conversion/addition create only bounded per-state arithmetic temporaries for finite-double inputs, no partial/input list. Python decimal conversion work per observation is a real constant cost for bounded doubles and problematic for larger ints; no benchmark or general faster claim is made.

### Counts, other bucket, warnings, one pass and inputs

- Both filter null/non-numeric measures before validcount; booleans/strings do not enter mean. Flatten/_scalar sanitizes nonfinite numeric input to null with existing warning. All-null groups retain null and never call mean conversion with denominator0. TSchecks exact!==undefined, so an exact0numerator is not mistaken for missing state; Python distinguishes stateNone before finish.
- Other-bucket overflow MOVES the existing last group state/numerator/count rather than averaging group means. Subsequent non-retained contributions update the same state, preserving observation weighting. Label collision handling and cardinality/non-numeric/missing/mixed/nonfinite warning families remain unchanged; no new warning on a merely large but finite mean numerator. Python counts/messages and TSSet notices retain their preexisting language-specific formatting, not a newly claimed byte-identical warning protocol.
- Public input/model/schema/adapter signatures are unchanged in this4pathdelta. Python retains<=32row inference prefix then chain(prefix,rows); TSsync/for-await feed the reducer once per selected yield. No new caller re-enumeration, iterator ownership, filesystem path, remoteURL, HTML/JS execution or output file authority is added. Existing wider scalar/GraphQL/prefix defects are not waived by this arithmetic review.
- Retained group count still capped by max_points including moved other. Existing schema/prefix/payload guards remain; temporary copies/metadata are not a physical process-RSS bound. No unbounded row or partial history introduced. Finding1 is the concrete resource-accounting/input-integrity defect, not an invented HTML/path exploit or scale claim.

## Commands, evidence, publication and next owner action

Unique artifact root C:/Users/bagma/AppData/Local/Temp/opencode/r38-11-mean-c1b-ses_de567811cffdTBwcb8pF5nDi9v-artifacts, snapshot source/. Actual same-process identity/assertions recorded before pytest.main with NEWtest path, `-q -p no:cacheprovider --strict-markers --tb=short --basetemp UNIQUE --junitxml UNIQUE`. Existing readonly MAINvenv Python3.12.16, default sys.get_int_max_str_digits()4300 unchanged. Source/probe before-after hashes and actual module path/interpreter are in evidence. Shell wrapper accepted expectedpytestexit1 for collection; this is NOT a product pass. New probe Ruff using exact snapshot pyproject/no-cache exit0; no assertions changed afterward.

Owned evidence/R38-11: review-checks.json, large-integer-mean.xml. Review-checks SHA256 **531841dc7b59b179a1902ad1635b7dd83c5d5054f6c49ec9c8c56d3df4e8af33**. It preserves one actual RED, raw/GitLF XML identities, complete24file/import/probe manifest, protected Python source proof, independent bit-bound calculations, commands/exits/counts and limits. Initial guessed TSdiff/report paths matched nothing (actual paths then located); these are navigation issues, not extra tests/product failures. One meaningful OWNscoped commit/nonforce/exactremoteSHA receipt follows actual confirmation; no self-receipt loops.

**R04 next:** disposition F1 with sole normalizer owner, repair safe wide-integer accounting without changing caps/strict oracles/syslimit, freeze actual integrated source and run this unchanged new regression plus the assigned independent mean review/acceptance gates. This request-changes report is for c1b only, not unreviewed546c/defaultmain. Do not replay old fullprefix/scale matrices or delay a separate already-fully-gated usable PR for this scoped blocker.

**Not checked:** TSruntime/compiler/product tests, author producer passes, parent runtime baseline, newer546c/scalar/GraphQL/exactprefix changes, final integrated source/CI, main31cff QA, broader build/package/npm/fullformats/Arrow/browser/rendering/memory/10M/release. Nothing unrun is green by implication.
