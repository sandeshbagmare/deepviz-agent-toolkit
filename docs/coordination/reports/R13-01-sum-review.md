# R13-01 independent bounded-SUM correctness review

**Disposition: scoped remaining accuracy concern; NOT final-candidate approval.**
Reviewer: `ses_de5678335ffeI7xJrod5l25Q0Q`, non-author role01.
Reviewed source: **`ec9f669eff28cd5351da142765b7755e3b2f484f`**, producer branch
`agents/r10-16-finite-overflow-fix`; diff against released base
`6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce`.

## Finding requiring R04/producer disposition

### P2 R13-01-F1: promotion cannot recover compensation already rounded away

- **Locations:** `python/deepviz/src/deepviz/normalize.py:628-631` and
  `packages/deepviz/src/normalize.ts:462-465`; connected pre-promotion compensation
  at Python:640-645 and TS:474.
- **Reproduction:** normalize records `{g:'a',v:value}` with
  `{kind:'bar',x:'g',y:'v',aggregation:'sum'}` for:

      [1e308,1e200,1,-1e200,1e308,-1e308,-1e308]

  Both languages produce **0 with no warning**; exact binary-input Fraction sum
  correctly rounds to **1**. The subnormal twin
  `[1e308,1,5e-324,-1,1e308,-1e308,-1e308]` produces0 instead of5e-324.
- **Control:** ordering the same multiset to promote first,
  `[1e308,1e308,-1e308,-1e308,1e200,1,-1e200]`, produces1. Both corresponding
  subnormal order controls pass too.
- **Cause/impact:** the unchanged two-double compensation loses the small
  residual before SUM overflows. New exact promotion faithfully copies that
  already-inaccurate prefix. A finite nonzero series can therefore become a
  silent zero, affecting downstream chart values despite successful completion.
- **Provenance:** the exact same two repros on base6d0 produced warnednull in BOTH
  languages, not correct values. This is an **incomplete repair/inherited
  accuracy limitation**, not a new precision regression or an invented defect
  in tie-to-even conversion. Four failing tests are ONE concern, not four issues.
- **Action:** R04/16 must explicitly disposition this against the required
  compensated-cancellation/exact-finite-SUM scope. Retaining exact prefix state
  early enough would avoid this loss but changes performance/budget tradeoffs;
  do not expand source authority or waive these strict tests from this review.
  At minimum, avoid claiming the overflow-only promotion makes all sums exact.
  No source fix or issue/PR mutation was performed by this reviewer.

## Independent commands and exact evidence

Only NEW `tests/r13_probes/role01/` tests ran; completed R10 suites/builds/scale
were not replayed. Shared Python3.12.16/Node26.13.1/compiler were read-only.
An isolated copied source snapshot supplied imports/build output, not sibling
producer dist; no package installation was run.

| Check | Actual result |
|---|---|
| Snapshot TS compiler after complete asset capture | exit0 |
| NEW Python strict suite | **exit1:2failed/65passed/0errors/0skips**,67tests,1.84s |
| NEW Node strict suite | **exit1:2failed/61passed/0skips/0cancelled**,63tests,403.4767ms |
| NEW test scoped Ruff | exit0 |
| Reviewer production/schema diff from3aa checkpoint | exit0/empty |
| Frozen source/import byte identity and exact baseline repro | exit0,18source/config hashes match reviewed commit |

Exact argv, child exits, failure IDs and raw-log SHA256s:
`docs/coordination/evidence/R13-01/verification.json`; full compact RED logs are
`python.log` and `node.log`. Capture-driver exit1 truthfully preserves RED.
No xfail/skip, altered source or original-oracle weakening masks failures.
Read the portable probe README for environment-variable setup. Core commands:

    python -m pytest tests/r13_probes/role01/test_sum_review.py -q --tb=short -p no:cacheprovider
    node --test --test-reporter=tap tests/r13_probes/role01/sum-review.test.mjs

## Bounded-state/caller review and passing controls

Read the full actual diff and connected reducers/flattening/state storage and
public callers, not only the added helper functions:

- Python `_sum_units` is called only from SUM promotion and already-promoted SUM
  updates; `_Reducer` is instantiated by public normalize at:720. TS helpers are
  called only from reducer SUM at:457/465 and finish:514; public sync/async
  entrypoints create reducers at:533/543. Normalization removes nonfinite inputs
  before they enter the finite-unit helpers.
- The fallback retains ONE integer/bigint, not a list of inputs or partials.
  TS safe input-count check:374 bounds finite-double units to about2151bits;
  new512-byte charge occurs BEFORE retaining at:464. Existing group cardinality
  and other-bucket identity/charges remain. This is logical retained-state
  accounting, not a JavaScript heap/RSS ceiling.
- Python retains arbitrary-precision integer policy, not a misleading fixed
  binary64 bound for arbitrary Python integers/counts. `_store`:575-582 charges
  numeric-state growth through existing retained budget before assignment. An
  independent internal shape test checks one integer/no nested partial list,
  bit growth and charge after8194large terms. A512-byte-budget positive/negative
  control passes: ordinary smallsum accepted, promoted large state rejected.
- Exact controls pass for20signed even/odd halfway cases across normal/subnormal
  exponent boundaries,32seeded post-promotion Fraction cases,3nonzero
  compensation-carry cases and2same-multiset order controls. Python pure integers
 96/512/4096bits remain exact; true positive/negative unrepresentable sums remain
  JSON-safe warnednull in both languages.
- Mean and deterministic sampling outputs match the untouched base exactly for
  selected fixtures; source diff leaves their implementations unchanged. The
  Node async source consumes16385inputs and returns one correct aggregate.
  Consumption/output counts alone are NOT a memory measurement.

No concrete new traversal, HTML injection or unbounded-partial-list path was
introduced by this reviewed SUM diff. This statement is limited to the diff;
renderers, MCP and the whole repository were not security-approved here.

## Source identity, interruption and publication

The initial read saw6d0+dirty source. Producer committed while I inspected it;
actual stable snapshot capture saw CLEAN **ec9f669e**. All18copied source/config
hashes were checked against that commit and again after execution. Folder name
`dirty-snapshot` is historical, NOT a claim the reviewed bytes remained dirty.
`source-identity.json` records the corrected identity; `reviewed.diff` is6d0→ec9.
Selected SHA256s:

- Python normalize.py: `34e8ed94a479acb2d7360a79ba4f62897bb453928fc1eec97efceb052a5e76f2`
- TS normalize.ts: `2c730b13f6360fa2e75c66d03ea051ffdb5c253d4922546f51cd8fd60e742c7f`
- Own snapshot built normalize.js: `52d718460e6501ca84a3ef8c9a5b9da92eb4c2b71109bd73a3b9351db85501e5`

Initial isolated compile exited2 because my first snapshot omitted the schema
asset. Copied the exact missing committed JSON asset, then compile exited0;
this was a reviewer harness error, not product failure. One checkpoint shell was
scanner-rejected before any write and then saved successfully. In-progress own
R13 history is preserved in `checkpoint-history.md`.

R10 first unfinished receipt is now genuinely published:
**727ab589ad05e6fcd0d326183a9aaa85d9c8922c**, non-force own push exit0 and actual
remote-SHA readback exit0 at13:53:40UTC; fresh authenticated GET/user verified
sandeshbagmare, GCM credential only in process memory. It fixes rawWindows versus
GitLF manifest provenance, not source/tests. Original c2628b6 strict RED and0c5
baseline evidence are preserved. No service/provider/auth configuration changed.
R13 evidence publication will be claimed only after its own actual push/readback;
no predicted SHA appears here.

## Limits and executable next action

Unverified: final integrated candidate, whole-suite gates/types/distributions,
10M/performance/processRSS, real SVG/PNG/browser chart output, renderer/MCP
security, fresh CI and900 legitimate created AND resolved issues. Historical
145Python/246Node R10 control passes remain historical, not rerun/current passes.
This independent review is not author approval, human approval, merge/release or
final signoff. Source normalizers remain16/R04-owned; no workers were spawned.

**R04 next:** inspect this strict repro and the real producer ec9f669e diff;
record F1 disposition before claiming exact cancellation correctness. If fixed,
rerun these unchanged NEW oracles against an explicitly pinned corrected source,
then remeasure affected frozen-candidate scale/performance gates. Root should
route this genuine actionable remaining concern, not create test-count tickets.