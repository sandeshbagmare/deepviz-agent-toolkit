# R46-11 - exact546 private integer accounting proposal

**Material handoff: F1 is CONFIRMED on546c25ea75ee9d8a41b3832aa639664bc9a683b5. Minimal safe-size proposal is UNAPPLIED. Producer04 alone owns the production repair.** This is not a fixed/GREEN normalizer, source approval or final-head acceptance.

## Actual result - unchanged original regression, not c1b replay

The original strict4000digit mean regression from own published8ce82e78bf7df5b4dacd027fdc3bddb01e771357 was copied byte-for-byte (SHA256d7262febf984bd0f83aa29d5a43133d5c083c56aeb97788940218493df28c226). It was executed on actual546Git source, not the oldc1b snapshot or a modified oracle.

- **6tests:1failed,5passed,0errors,0skips,0deselected; pytestexit1,0.48s.** Expected original failure: the mean of10**4000 and -(10**4000) should return0 for2valid inputs, but raises4300digit conversion ValueError at normalize.py737→642→600.
- Exact546 `_store:597-604` and mean add640-643/finish676-680 AST equal c1b, independently checked STATICALLY; no oldc1b runtime/matrix was executed. Internal-size repr at600 is the same defect reached by the exact mean numerator at642.
- Three bounded positive means (one test loop, not three pytesttests) returned: mixed5rows/2validnumeric→2.0; +/-4096bit integer pair→0.0; two1e308 observations→1e308. Actual source pulls5/2/2, each iterated ONCE, output1row and caller input unchanged. Invalid bool/string/null do not change valid mean count; expected warning asserted.
- Natural16MiB retained-state rejection occurred at **1003source pulls out of at most1024**, one iteration, no result returned. Keys/cells/records remained within their own caps, max_points2000 prevented other-bucket reduction; NO budget injection or cap change. This is a negative control, not1003successful output rows/RSS proof.
- Five passing tests comprise two actual546positive/budget controls and three pure UNAPPLIEDhelper/boundary checks. They are NOT five passes of an applied production fix. Scoped new-probe Ruff exit0. Original strict expectation/input/oracle unchanged.

## Minimal UNAPPLIED helper and callsite

`evidence/R46-11/private-integer-accounting.UNAPPLIED.patch` proposes ONE private helper beside _sum_units, and replaces only the numeric-size expression inside existing_store. No actual normalizer/snapshot/producer file was patched or monkeypatched.

```python
def _state_number_bytes(value: Any) -> int:
    if type(value) is int:
        bits: int = value.bit_length()
        return max(1, (bits * 30103 + 99999) // 100000) + int(value < 0)
    return len(repr(value))

# Inside existing _store wide-state branch ONLY:
size = max(size, sum(_state_number_bytes(item)
                     for item in (state[0], value, correction, exponent)))
```

Private normalized integer state is handled without decimal conversion; existing bounded float/None/bool fallback uses the old repr convention. Exact type(int) keeps bool representation accounting unchanged. All old surrounding code remains: >96bit trigger,128bytefloor, keys/state/cap accounting, _check_retained_bytes BEFORE assigning state, count/rounding/other behavior and public recordJSON input policy. The estimate is conservative and can charge a few extra bytes near numeric boundaries; it does not undercharge/widen the budget or promise identical byte-for-byte charge at every old threshold.

**Bound proof:** independent integer arithmetic verified `2**100000 < 10**30103`. For nonzero integer n ofbitlengthb, abs(n)<2**b<10**(b*30103/100000), hence decimal digits<=ceil(b*30103/100000). max1 handleszero; +1 handles minus sign. No logarithm rounding, decimal string or global digit-limit change is needed. For the failing internal value b14362, the safe bound covers its4324digits and proposed total numeric charge stays<16KiB, well below the unchanged16MiB policy.

**Boundary checks:** zero/sign/bool/None/float fallback; powers of10 just below/at/above1,2,9,29,30,127,128,1000digits; both signs; actual old_store and proposed size both retain128floor for0/1/95/96/97bit values;4096bitstate; huge +/-14362bit internal numerator verified with integer comparisons without decimal conversion. Hypothetical AST, held as in-memory text only, differs from546 by this helper and ONE size-callsite; removing them restores exact546AST. PatchSHA256 **e13665c062dddd66f5245cc767900fe8a0650236019320c3c0c5cf461de1f9fc**.

**Bounded cost only:** the OWN pure helper was called6144times (6fixedvalues x1024;bitlengths0/1/97/4097/14362/14362) in0.0026683999894885346s same-process perf_counter wall. This shows the bounded check ran and returned, NOT production stream throughput, speedup, fresh-process memory, allocation cap or10Mscale proof. Cost has no per-integer decimal conversion; no source-sized history/list retained. No old sum/prefix/format/benchmark matrix ran.

## Exact source/command/evidence identity

Owner/session ses_de567811cffdTBwcb8pF5nDi9v; existing OWN branch agents/r10-11-python-scale-envelope at8ce82e78bf7df5b4dacd027fdc3bddb01e771357 before this continuation. FullcurrentR46/21lines(common+row11), R42/23lines and OWNcheckpoint read. New explicit user steer controls over stale R46KEEP11schema/neverstarted text. Same session/job continued at coherent checkpoint; no parallel restart.

Source546c25ea75ee9d8a41b3832aa639664bc9a683b5, parentc5ab299a9ecfd9938e677b04ec146b180835a314. Python normalize Git-LF SHA256 **34b88b4b959349593e9eac4e996c4996d311f9249daed1ee024606afd1af8dfc**. CompletePythonpackage+config12files from immutable Git, checked against Git BEFORE import and again after tests/final packaging. Original and both new proposal/probe files also hash-unchanged before/after. Every actual imported deepviz module is inside this unique snapshot; no installed/MAIN module substituted.

Artifact root C:/Users/bagma/AppData/Local/Temp/opencode/r46-11-accounting-546-ses_de567811cffdTBwcb8pF5nDi9v-artifacts. Guarded readonly shared Python3.12.16 `python -B -I -S -` with explicit snapshot/dependency paths and process-local pytest-plugin isolation; default digitlimit4300 asserted unchanged. Exact pytestargs/interpreter/moduleorigins/allhashes in evidence: UNCHANGEDoriginal test + NEWtest_safe_accounting_proposal.py, `-q -p no:cacheprovider --strict-markers --tb=short --basetemp UNIQUE --junitxml UNIQUE`. Expected failing pytestexit1 is recorded; shell collection success is NOT a product pass.

Evidence/R46-11 contains review-proposal-checks.json, actual546-six.xml, UNAPPLIEDpatch. ChecksSHA256 **72af3e98554be7bda111e22fe9e5cadb96a75ede0e685bdece1b08c1c0689eb1**. It preserves1RED/5PASS counts/raw-vs-GitLF XML hashes, originaloracleidentity,12file before/after module/Git proof, exact1003budget pulls, ASTequivalence, integer upper-bound proof and bounded helper time. New code under tests/r46_probes/role11/ is proposal/testcode ONLY, never production-imported.

Navigation/analysis failures preserved: initial static matcher recognized direct mean comparison but missed finish BoolOp, stopping BEFORE producttests/patchwrites; corrected condition-only AST matcher. First new-probe Ruff found import-order and redundant generator parentheses; formatting-only fixes before product execution, no oracle/assertion/source changes. Corrected Ruff0. No hidden retries of product tests.

## R45 coherent partial - preserve actual history, no redundant approval

R45extra11schema gate ACTUALLYstarted before root read R46, then explicitly withdrawn at coherent checkpoint after other01+04gates reportedly complete. Saved partial17filehash/ASTotherwise31cff/728metadata/original82/17RAWfixture and single guarded export proof; ZEROpytest/productcases and **NOschemaSOURCEapproval** issued. Detailed partial report/evidenceR45-11 preserved with proofSHAd20ba75f7820ace1b22b6868b7b2215718ec67fa160415e43daeebc265a1da37. It is not never-started history or a borrowed fifth gate.

## Next owner / limits

**R04 should feed this actual546F1reproduction and minimal UNAPPLIEDsafe-bound proposal to active producer04 now.** Producer04 retains exclusive production ownership and chooses/implements/tests/publishes the actual repair. No idle wait or head polling. After a real new head is published and this checkpoint is handed off, the unchanged original regression and bounded positive/budget controls can test that exact source. If proposed code is adopted, this proposal must NOT be counted as its independent source approval; noncontributor review/final integration/CI remain required.

No production/source/config/schema/globaldigitlimit/caps/recordJSONpolicy/existingoracle/SDK/deps/install/shared-environment/APIwrite/default/sharedbranch/spawn/poll edits. No04head inspected/approved, no own integrated-productionGREEN/mainQA/PR38merge/CI/TS/full546matrix/fullformats/10M/freshRSS/release claim. Central role11 updated only; full-toolkit and integration ETA **UNKNOWN**, dependency/decision owners04/R04. Own remaining step: ONEmeaningfulscopedcommit/nonforce/exactremoteSHA, promptmaterialhandoff; no receipt-only loop.


## Main-first delivery routing (R48)

At2026-11-27T18:05:37.633093+00:00 FULLliveMAINstatus.md/R48/OWNcentralreadatcoherentcompletion. Main-boundtarget is role07/R04Pythondatafoundation from546+producer04actualrepairhead(PRUNKNOWNhere); thishandoffremovesreproduction/safe-accountingdecisionuncertainty, NOTtheopenproductionbug. Producer04nextconsumesexactproof/UNAPPLIEDpatchandpublishesrealtestedhead; R04assignsgenuineaffectedgates/integration/readymerges. Withdrawnextra11schema gateisNOTreasonholdPR38, andthisnormalizerbugisnotinthatmodel-onlyslice. AskR04nextusefulscopeonlyafterthissinglematerialhandoff, no parallelrestart/poll/replay/receiptloop.
