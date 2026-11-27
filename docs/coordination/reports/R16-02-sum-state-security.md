# R16-02 independent SUM state/security review

## What this change does

Commit **ec9f669eff28cd5351da142765b7755e3b2f484f** promotes a SUM that temporarily
overflows to one integer measured in minimum-subnormal units, rather than losing a
finite final answer. Ordinary sums stay on the existing compensated fast path.
This review independently checked state/admission boundaries, not numerical accuracy.

**Disposition: no new security/state-boundedness blocker established in this scoped
review. This is NOT integration approval, author signoff, or final-candidate approval.**

## Identity, assignment and ownership

- Owner/native same session `ses_de5678328ffeYCFXQhRPKd4a9h`, reconfirmed via session_move.
  FULL MAIN R16 common+02/canonical/own note/RESUME/STATE read; prework report and note
  saved before substantive code/probes. No spawn, production edit or source ownership.
- Existing OWN `agents/r10-02-security-boundaries` reused at
  a6da87adac0079e430a0156bfc6848981f9af029. Its only preexisting dirty item was OWN
  untracked R13 publication receipt, preserved. NEW writes: this report,
  evidence/R16-02, tests/r16_probes/role02 and OWN actual-ID note only.
- Consumer is a NEW **clean detached ec9f669** worktree, never dirty MAIN or the author's
  worktree/build. Four Git blobs equal tested working bytes before AND after all runs;
  imported Python normalizer resolves to this pin. Own TS compiler output is external
  to the source tree. Before/after compiled hashes equal; source-map test proves target.
- Read whole four-path commit diff (267add/4del), connected Python/TS planners,
  flatteners/scalars/record accounting/reducers/finish/callers/models/README, and the
  author's report/evidence. Author's results are context, not reused independent passes.
- Scope disjoint from01 correctness,11 performance,15 value/oracle tests,20 artifacts.
  No author23 tests, old32 MCP cases, full suite/scale/browser or producer build replay.

## Independent source assessment and finite reproductions

No finding is manufactured from a theoretical RSS concern. These are verified controls
and explicit limits, not an assertion that every possible security path was tested.

### 1. Promotion is charged before retained state changes

**TS `packages/deepviz/src/normalize.ts:370-394,439-466,488-490`:** safe-integer count
admission precedes reduction; group admission reserves before insertion; SUM fallback
reserves512B before setting `exact`. Already-promoted updates retain one BigInt, not a
partials list. There is no async suspension inside the8BDataView conversion331-335.

**Python `python/deepviz/src/deepviz/normalize.py:575-582,618-631`:** `_store` checks the
updated dynamic state cost before replacing retained values. Unlike TS, arithmetic
already creates temporary integers before this check. That is a bounded transient in
these fixtures, not evidence that16MiB constrains all Python allocations. The public
contract explicitly says payload/state budget, NOT RSS (`:684-700`).

**Novel reproduction:** stream two passes over long legal category values: first
`v=1e308` for every group, then `v=0` as an ordinary positive control or `v=1e308` to
force promotion. No cap/constants/code monkeypatch; all inputs public/local/finite.

| Public fixture | Ordinary completes | Promoted behavior |
|---|---:|---:|
| Python510groups,32700ASCII-byte labels |1020rows,510records,no warning| rejects at **561/1020** consumed rows |
| TS255groups,32640ASCII-byte labels,stream |510rows,255records,no warning| rejects at **427/510** consumed rows |
| TS same fixture,sync record array |510rows,255records,no warning| rejects; array already supplied510rows, **no early-read claim** |

Errors match actual retained-budget messages. Fresh independent calls after rejection
succeed without old warnings. Python rejected-call tracemalloc: peak**18,420,553B**,
current284,406B. This is Python-managed allocation, not RSS/heap cap or a benchmark.
The peak exceeding16MiB is not a new budget violation: inference prefix, caller data,
keys/container overhead and conversion temporaries are explicitly outside that payload
budget. No unbounded partial-list amplification was observed or found in the new code.

### 2. Eviction reuses the charged state; unknown keys do not get fallback states

Python`:590-606` transfers last state object to `other`; TS`:438-450` does the same.
Unknown categories reuse that one state, while retained groups remain independently
addressable. Exact units/exponent/cost are not reset or copied per unknown category.
TS finish`:503-520` clears group references and subtracts original group cost as public
rows are constructed; local state array may coexist transiently until return. Python
`:652-680` builds public records while reducer state is still locally alive. Neither
public normalize call retains a global group registry after returning (`:720`; TS`:533,543`).
The shared JS DataView is constant8B, not a dataset cache.

**Novel reproduction:**1000distinct groups,4096-byte category labels,4000rows forcing
promotion/cancellation, `max_points=10`. Both languages return10public records with one
other-bucket warning, finite JSON and no `exact`/exponent/correction fields. A fresh call
has one record/no prior warnings. Python traced peak989,325B/current736,342B. Public
output alone cannot prove all heap references; the no-per-key-state conclusion also
rests on the inspected control flow. No direct V8 heap-retention measurement was made.

### 3. 2151bits is a representation argument, not measured process memory

Independently computed with stdlib Fraction/int, not either production helper:

- Largest finite binary64 in units2^-1074 has2098bits.
- For JS accepted total count N<=2^53-1 (`:373-374`), seed terms plus remaining input
  terms can be conservatively bounded by N+1 finite terms: first promotion consumes
  at least two rows and forms at most three finite seed terms. That bound has2151bits
  and269payload bytes. This assumes finite internal seed terms; it is not a proof of
  rounding accuracy or reachability of every internal numerical state.
- Production512B reservation is above the269B digit payload; real V8 headers,
  allocation rounding and GC were NOT measured. Do not call512B a whole-process cap.
- Final TS binary representation `:337-345` is at most2151characters under that bound;
  there are a constant number of BigInts/rounding temporaries, not a growing series.
  CPU remains linear in rows with bounded-width operations under that assumption;
  there is no overall elapsed-time/input-row limit for arbitrary finite streams.
- An independently constructed bound-sized CPython integer is312B by `getsizeof`;
  its decimal representation648characters/689B. This demonstrates why Python's
  decimal state charge is not the same as BigInt payload or V8 heap size.
- Python has no JS safe-count ceiling and accepts arbitrary exact integers. Its
  bounds are existing dynamic representation/state/record guards (`:424-444,575-582`),
  NOT the float-only2151bit argument. `_sum_units` adds1074bits to an integer input.
  No universal constant-size claim for arbitrary Python integers is made.

Actual calculation evidence: `state-bound-calculation.json`. No2^53-row run, OOM or
large-scale/performance test is implied by arithmetic on a small constructed integer.

### 4. Pathological public representations reject before reducer entry

Python input record `_record_bytes:436-438` renders numeric values before yielding to
reduction. With actual host repr limit4300digits (unchanged), a late >4300digit integer
after32rows/promoted state raises the existing representation ValueError at row33;
row34 is never consumed. If host disables/raises this limit substantially, this one
probe explicitly skips; that mode is unverified, not pass. Arbitrary Python integer
repr CPU cost is existing code, not a new proven amplification in this four-path diff.

TS `flatten:315-321` excludes nonfinite input numbers and rejects a supplied public
BigInt before it can become internal SUM state. A late BigInt after32rows/promoted
state rejects at row33; no extra row consumed. No crafted objects/getters/custom
conversion hooks, private reducer access, host guard changes or cap patches were used.

Late genuinely nonrepresentable results still go through existing warnednull conversion:
Python`:653-668` and TS`:514-518`. This source handoff was reviewed; numeric edge-value
oracles and native artifact fidelity are deliberately left to15/20, not double-counted.
Evidencepacker firstexit1 FileNotFoundError ts-build.log: silent successful tsc piped to Tee emitted no log file. This was an OWNcollector assumption, not source/build/testfailure; helper failed before creating/copying any evidence directory. Removed missing optionalemptylog from hashlist; actual recorded compilercommand TS_BUILD_EXIT=0 remains evidence. Correctedhelper will reconcile/copy completedresults, not rerun tests/build.

## Executed commands, exits and totals

OWN report/probe checkout: existing `r10-02-security-ses_de5678328ffeYCFXQhRPKd4a9h`.
SOURCE: `C:/Users/bagma/AppData/Local/Temp/opencode/r16-02-sum-ec9f669-ses_de5678328ffeYCFXQhRPKd4a9h`.
OUT: `C:/Users/bagma/AppData/Local/Temp/opencode/r16-02-sum-security-results-ses_de5678328ffeYCFXQhRPKd4a9h`.
PY: existing MAIN `.venv/Scripts/python.exe`; TSC: existing MAIN `node_modules/.bin/tsc.cmd`,
both read-only; no installs. `PYTHONPATH=SOURCE/python/deepviz/src`, bytecode disabled,
`R16_02_SOURCE=SOURCE`, `R16_02_TS_BUILD=OUT/ts-build`; probe JSON written only in unique OUT.

1. Quoted full-pin `git rev-parse --verify 'ec9f669eff28cd5351da142765b7755e3b2f484f^{commit}'`
   exit0; `git worktree add --detach SOURCE ec9f669eff28cd5351da142765b7755e3b2f484f` exit0;
   HEADexactec9/statusclean/diff0/whitespace0. Initial unquoted PowerShell braces caused
   `Needed a single revision`, corrected before consumer setup. A long shell checkpoint
   was scanner-rejected before execution; narrower writes succeeded. Neither is product RED.
2. `TSC -p SOURCE/packages/deepviz/tsconfig.json --outDir OUT/ts-build` exit0. Fresh own
   compilednormalizer SHA25652d718460e6501ca84a3ef8c9a5b9da92eb4c2b71109bd73a3b9351db85501e5;
   unchanged before/after. No npmci/full build/distribution gate inferred.
3. `PY tests/r16_probes/role02/source_identity.py OUT/source-before.json` exit0 at14:33:28UTC,
   repeated **identity capture only** after tests toOUT/source-after.json at14:44:19UTC exit0.
   Four Git/working blobs equal; pin/import/build unchanged. Files/hashes in both JSONs.
4. First new probes (not additional coverage): Python3cases2pass1OWNharnessfail0skip5.48s
   exit1; TS5cases4pass1OWNharnessfail0skip5816.1242ms exit1. Python incorrectly assumed
   dataclass had model_dump; TS synchronous test incorrectly supplied a generator instead
   of JSON record array. Corrected only NEW harness: explicit public fields JSON and array.
   No production edits, private reducer access, changed oracle or cap patches.
5. Final `R16_02_RESULTS=OUT/final`; `PY -m pytest -q -rs --tb=short -p no:cacheprovider
   --basetemp OUT/final/pytest --junitxml OUT/final/python-probes.xml
   tests/r16_probes/role02/test_sum_state_security.py` → **3passed0fail0error0skip2.77s/exit0**.
6. `node --test --test-reporter tap tests/r16_probes/role02/test_sum_state_security.mjs`
   → **5passed0fail0skip4439.0683ms/exit0**, same pinned source/own external build.
7. `PY -m ruff check tests/r16_probes/role02` exit0; `PY -m mypy --cache-dir OUT/mypy
   tests/r16_probes/role02` exit0/2ownPythonfiles. Python3.12.16/Node26.13.1/TSC7.0.2 observed.
8. `PY OUT/state_proof.py` exit0: independent Fraction bound calculation described above,
   not a numerical result/oracle or scale test. `PY OUT/pack_evidence.py` correctedexit0,
   reconciled immutable saved logs/XML/source/builds,13compact JSON evidence files copied
   to OWN R16evidence MAIN and OWNbranch; tests/build NOT rerun during packing.

Portable command recipe and safety constraints: `tests/r16_probes/role02/README.md`.
Raw local initial/final logs/XML hashes and exact test names: `evidence/R16-02/summary.json`.
Working-copy AND CRLF→GitLF hashes recorded separately; no byte-identity claim for
Windows normalized probe text. Source-consumer four paths are genuinely Git-byte-identical.

## Fresh GitHub observation and publication

Safe GCM capture kept token only in process memory, never subprocess arguments/logs/files.
At14:47:05.112594UTC four authenticated GETs HTTP200 verify expected sandeshbagmare/repo,
PR31open/draft/unmerged at5340bc69b7203ad7a9166543062482d819f9b705; Python3.11/3.12/3.13 checks
FAIL although other checks pass. No greenCI claim/issuecensus/issuePR mutation. Sanitized
receipt `evidence/R16-02/github-prepublication.json`. Actual OWN checkpoint **21fc394048755a1df20fb774c85d50d0458bbb89** published
at14:54:26.505650UTC: nonforcepush exit0 and exact remoteSHA readback exit0. Receipt
`evidence/R16-02/publication-21fc394.json`. It contains only OWN19files/858add;
final stagedscan68,232B/zero credentialpatterns/whitespace0/4probeGitLFhashesmatch/
productdiff0. No source edits/integration/finalapproval. This small actual-receipt
follow-up will be separately committed/pushed; its actual latestSHA will be saved to MAIN after
readback, not guessed in advance.

## Limits, decision and executable next action

No new concrete security blocker in this four-path review; keep producer's source-specific
boundedness evidence distinct from a full correctness/security approval. No unbounded heap
exploit, numerical rounding proof, V8 memory/RSS measurement or guaranteed total CPU time
claimed. Python altered/disabled repr-guard hosts untested. Entire schema/render/MCP/HTML/
filesystem boundary not re-audited in this SUM-only lane. Previous MCP strict duplicate/raw
UTF8/resource findings remain untouched; eligible producer18 owns fix, not testers02/10.
No old32cases until actual fix pin, no arbitrary OOM/cap patches/large CPU trial.

Full suite/build/browser/10M/frozen final candidate not checked here. Sourceec9 predates
current other integration changes and has known baseline failures; no blanketgreen/signoff.
Full production/900legitimatecreatedANDresolvedissues remain unmet. No human approval,
issueclosure, merge, release or final delivery manufactured.

Current action: publish only OWN useful probes/report/compact evidence/actual-ID note after
explicit staging/whitespace/credential-pattern scan. Next: R04 dispositions this independent
state review alongside01/11/15/20, integrates only actual chosen source and assigns unchanged
NEWcontrols on the exact frozen resulting pin; root alone performs valid SAME-ID refill.
Precommit actualcheck: explicit19OWNpaths staged; full NEWtest/README stageddiff inspected; stagedwhitespace0; stagedcredentialpatternscan0/zero matches, saved4probeGitLFhashesmatch, productcontractpromptdiff0. Firstscan67,124B beforethischeckpointappend. Sourceconsumer remainscleanec9; OWNbranchproduction remains3aa unchanged. PriorR13ownuntrackedreceipt unstaged/preserved. Next meaningfulindependentreview/probecommit then OWNnonforcepush/exactremoteSHAreadback; no sourcefix/finalapproval.
