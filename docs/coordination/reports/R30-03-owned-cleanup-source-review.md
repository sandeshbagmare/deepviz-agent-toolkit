# R30-03 — Second independent source review: owned-input cleanup

**Independent source verdict:** no new must-fix defect found in the bounded cleanup delta at **5ba860305dcc86ac2f95f01705b984d2b40f2799**. Accept this cleanup **source gate only**. Not tester approval, a usable-main claim, or approval of the whole parent/later normalizer. **Zero product imports, tests, builds or API calls.** Release extraction and exact-final-head gates remain R04's.

## Before-work checkpoint

- Owner SAME native-confirmed session `ses_de5678315ffeDxQVEpE9V9WSTE`; existing isolated OWNworktree/branch `agents/r10-03-echarts-numeric-x`, HEAD **fd115828f414c1a753790860adea67941d1e700f**, trackedclean/only own untracked artifacts. Fresh OWNremote exactfd11582 and defaultmain **0ae2cf26426822135fc10d337fcacf580b7ed833** readback0. Default/source/PR states otherwise NOT audited/polled.
- Read FULL MAIN `tasks/R30-release-critical-support-allocations.md` COMMON+03, currentAGENTS/canonical/RESUME/STATE/ownnote. Root actual capacity/admission is supplied by dispatcher, no newIDs/spawns. R04 is sole release manager/shared/default/PR/closure owner; this is a narrow SECOND independent SOURCE review, not tester approval, manager role or a production grant.
- Exact review source **5ba860305dcc86ac2f95f01705b984d2b40f2799**, parent **ec9f669eff28cd5351da142765b7755e3b2f484f**; initial `git show -s` and `diff-tree`0 confirm ONLY modified `python/deepviz/src/deepviz/normalize.py` and NEW `python/deepviz/tests/test_r17_normalizer_boundaries.py`. Existing OWNcheckout is NOT5ba; sealed Gitblob extraction/read-only review will avoid dirtyproducer source or pretending currentcheckout is target.
- Scope: full exactdiff + touched normalizer/adapters, connected public normalize/render/tools/MCP/CLI paths, ownership of handles vs borrowed iterators/futureArrowbatches, deterministic finally/error/retainedtraceback cleanup and statistics preservation. Read existing04narrow18PASS/lifetimefinding context without borrowing approval. Identify minimal dependency-complete first usable Python foundation extraction and any must-fix/source gate; main does not yet contain this code.
- Allowed NEW writes ONLY thisreport, `docs/coordination/evidence/R30-03/`, ownactual-IDnote, optional NEW `tests/r30_probes/role03/` only if a genuinely material finding needs a tiny counterexample; unique ownlocal artifacts. No production/oldoracles/config/deps/env/API issuewrites/fulltests/GraphQLmatrix/compiler/build/browser/producerpoll/sharedGit/spawn. OWNmeaningfulcommit/nonforcepush/exactSHAreadback authorized.
- Acceptance: exact raw Gitblob IDs/SHA256/source/module provenance; independent line-level lifetime review and connected-caller/dependency map, concrete findings/cases or bounded no-new-must-fix conclusion; tiny proof only if needed. No test/CI/finalrelease/merge/futureGraphQLfix acceptance inferred. Existing04context not approval, source16GraphQLretest only after actual laterSHA handback.

**Current action:** before-work/sourceidentity checkpoint saved, no review/test execution yet. **One executable next action:** extract exact5ba/parent source and changed five tests via raw `git show` to unique ownartifact snapshots; record hashes/blobIDs/diff, then trace full source/callers independently before reading04context disposition.

Initialrawextractor **exit1** because OWNhelper incorrectly included nonexistent nested `python/deepviz/pyproject.toml` (`git show`128). Raw source copies before failure are isolated only, no product execution/edit. Read-only exact`ls-tree` diagnosis **exit0** confirms project metadata livesatROOT`pyproject.toml`; corrected ONLYownextractor pathlist toactualtree. **Next executable action:** correctedrawextractor once then independentdiff/callflowread; no install/build/test fallback.

## Independent first source checkpoint

Correctedrawextractor **exit0**,13sealedfiles copiedbyte-exact Gitblobs; normalizerblob`423d2e08f5da7531a407c282b4720915e7045920`, rawSHA256 **eef44a7df71926932fc14b33ff47225903b30824c2435e74b9707b49ed357f2b**,781lines; fullsource+NEWtestsdiffSHA256`6b50cf8c166912e5cb3df026400a873ccfc7ee4f30f390a58cf537c797a93382`. Fullnormalizer781lines/NEW87linefivecases/render229/tools191/CLI60/MCP115/init27/models92/recommend115/rootmetadata49 read fromsealedonly. ExactGitgrep callers/diffnumstat/sourcehistory/rootmainmetadata-delta commands all0. Independent initial ownership trace finds explicit root adapter close before traceback escapes, no explicitclose of borrowedrawiterator/TextIO/RecordBatchReader; statisticalstatements appear unchanged by indent-only wrapping pendingASTcheck. Full04R22review65lines and original15R13report60lines nowread **context only**, neither counts toward my execution/review conclusion.

Mainroot0ae2has7paths/noinitializer/normalizer/render/tools/CLI/MCP. Raw5badiffONLY+78/-66normalizer andNEW87tests; importingunchanged5bainitpullsrender→engines, normalizer'sinternaldependencyonlymodels. Connectedtoolsnormalize/fileauthority/datasetfailurecache/rendercleanup andMCP/CLI reach sharednormalizer; no alternativeowned-inputbypassfound. BorrowedArrowfuturebatchmeaning is **not rollback of alreadyconsumedcurrentbatch**; for-loop doesnotcallcallerclose, prefix/batchconsumptionunchanged. No new concrete material finding so **NOtinycounterexample/test warranted/run**. Existingmean/scalar/GraphQL/SUM problems outsidecleanupremainunadjudicated, not green.

ReadFULL21's237linefoundationproposal/architecture/design ascontextafterownsourcegraph. It independently matches data-onlyinitializer/metadata recommendation; not borrowing its14structuralchecks/buildstatus/approval. **Current action:** finishstaticASTnormalization/statisticsequality and exactrelative-import closure/sourcechain proof. **One executable next action:** runOWN AST/TOML/Git-onlycollector comparingparent5bahelpers/_plan/_Reducer and cleanup-unwrappedbodies, record concreteownership/releasegate table and boundedsourceverdict without productimports/tests/builds.

## What this change does

It makes `normalize` finish cleanup of the adapters it creates before a failure
returns to the caller, even when the caller keeps the exception traceback alive.
It also removes close-forwarding from the BOM wrapper so cleanup does not take
ownership of caller-supplied text streams. It changes no reduction or sampling
computation.

## Independent connected-source review

All line references below are the **sealed5ba Git blobs**, not the OWNcheckout,
the current producer tree, the 04 report's test modules, or later source.

| Source boundary | Independently checked behavior and ownership |
|---|---|
| `normalize.py:692–755` public function | Validation precedes adapter creation. The new `try/finally` spans 32-row inference, planning, reducer creation/add/finish and reservoir accumulation. `rows` is always this function's `_records` generator. Calling its `close()` does not call `data.close()` directly. On normal exhaustion its finalizer has already run; closing the exhausted generator does not rerun that body. |
| `normalize.py:481–521` `_records` | Saves the **original internal adapter** before wrapping it in `data_path` selection. A planner/budget/downstream error while `_records` is suspended is now driven through its finalizer. A retained outer traceback can keep frame references alive, but cleanup no longer waits for those references to disappear. Finalizer explicitly closes the saved internal adapter, not the selected-path view or caller input. |
| `normalize.py:239–264` `_source` | Plain records, mappings and caller iterators return unchanged (`source is data`), so they are not owned. Text streams create parser wrappers; the wrappers are owned, not the streams. Path JSON/auto uses an eager `with` before `_records`'s `try`; read/decode failure already exits that context. Lazy Path/binary adapters open resources only during iteration, inside their own contexts. Validation before first iteration therefore has no open handle to leak. |
| `normalize.py:89–103,116–135` text borrowing | `_without_bom` now loops instead of delegating to the underlying iterator. Closing/destroying this library wrapper therefore adds no forwarding `close()` to the borrowed stream. `_jsonl`/CSV reader iteration and original syntax errors/cause chaining are unchanged. No arbitrary `close()` method is called on a decoded JSON field named `close` or an ordinary record. |
| `normalize.py:228–236` owned CSV/TSV/JSONL Path | Closing `_path_rows` unwinds its `with path.open(...)`; delegation into its own parser is appropriate. The file stream is internally opened. The same parser used with a supplied `TextIOBase` has no owned `with` around that caller stream. |
| `normalize.py:204–225` owned binary Path/bytes | Parquet opens `ParquetFile` in a context. IPC file/stream opens the input stream/BufferReader in a context, including the IPC file-to-stream fallback. Explicitly closing the retained adapter reaches those contexts on post-prefix failures. No remote source or arbitrary path authority is introduced. |
| `normalize.py:171–184` borrowed Arrow future batches | A supplied `RecordBatchReader` is traversed with `for batch in batches`, not `yield from batches`, and never explicitly closed by these wrappers. The inner delegation is over a converted Python row list, not the caller reader. Closing the library generator introduces no caller-reader `close`/drain call. **This is source proof, not a fresh native-reader usability test.** Already consumed rows/current conversion batch are not rolled back; future batches remain caller-managed. |
| `normalize.py:267–297,326–385` path/expansion views | Nested views retain their existing traversal/count rules; the adapter root is not lost when selection wraps it. Raw borrowed iterables remain non-owning `for` traversal. Closing the root need not close every view to release its owned file context. |
| Error propagation / close | No new exception handler suppresses planner, parser, reducer, I/O, `GeneratorExit` or cancellation errors. Cleanup failures are not caught or converted into success; Python exception context is not stripped. No new close-error suppression policy is needed for this delta. This is not a guarantee for arbitrary hostile monkeypatched `Path.open`/native extension behavior. |
| `normalize.py:756–781` final output | Result byte validation, warning construction, mixed-type notices and `NormalizedData` creation occur after row cleanup. Exceptions here cannot leave the adapter newly open. Resource closure is the intended effect, not a promise of zero traceback-retained memory/RSS. |

### Public callers and resources beyond the normalizer

- `__init__.py:8–12` exports the same normalizer. No second implementation or
  wrapper with a new cleanup policy is inserted by5ba.
- `render.py:92,109–141`: single charts call shared normalize. Dashboard iterators
  are spooled with a library-owned write context; per-child replay files have an
  explicit `with source.open(...)` owned by **render**, while normalize borrows
  that replay handle. This patch correctly leaves that handle for render's context
  to close. Original iterator spooling is a non-owning `for` and is unchanged.
  Temporary replay directories are handled by the existing `TemporaryDirectory`.
- `tools.py:56–101`: file authority is checked before converting an allowed file
  reference to a Path. Shared normalize opens that Path internally. A failed
  normalization occurs before `dataset_id` insertion (`102–118`), so the cleanup
  patch does not turn a failed prefix into a reusable success handle.
- `tools.py:135–159`: shared render uses a fresh owned output subtree, with
  failure cleanup restricted to that subtree. Input files are not deleted.
- `cli.py:37–52` funnels normalize/recommend/render into ToolSession; its
  `54–55` error path retains existing behavior. `mcp_server.py:45,77–102` and
  `create_tools` (`tools.py:175–191`) use the same session methods. This is a
  connected-caller review only, **not security approval of old tools/MCP source**;
  the separate e47 repair/source review remains necessary before releasing them.

## Statistics/computation preservation: independent static evidence

`PY artifacts/r30-03/static_review.py` **exit0**. It parsed source as data, without
loading `deepviz` or importing any renderer/SDK. Evidence:

- **26** other top-level functions/classes are AST-identical to parentec9,
  including `_Reducer`, `_plan`, byte guards, `_source`, `_expand` and adapters.
- The only changed definitions are `_without_bom`, `_records`, `normalize`.
- After removing **only** the specifically verified new ownership assignment,
  finalizer shells and Generator return annotation, `_records` and `normalize`
  executable computations are AST-identical to the parent. After substituting the
  explicit loop back to the original delegation, `_without_bom` is identical.
- Thus row counting, full-stream consumption loops, reducer state/result math,
  RNG seed/order, sample size, metadata/warning assembly and resource **limits**
  are not altered by this patch. The AST comparison is not a runtime test or a
  claim that inherited numeric/GraphQL behavior is correct.
- Exact9-module import graph and7-commit normalizer history were derived from
  Gitblobs. JSONs: `static-change-proof.json`, `dependency-closure.json`,
  `source-chain.json`, plus `static-commands.json` (actual argv/exits/hashes).

**New findings / probes:** no new concrete material defect found in the cleanup
delta. No new counterexample was warranted; **0 probes/0 product tests** were run.
This is not 26 test passes. Existing04's18PASS and prior15's lifetime failures
were read as context only, not replayed or counted as this review's execution.
Author's unchanged five cases were read in full, not run or relabeled independent.

## Minimal dependency-complete first Python foundation: impact on R04's slice

This is scoped advice for R04, not a competing branch inventory or release plan.
Defaultmain readback **0ae2** has7files, including only `models.py` from the
package. **The cleanup commit cannot be cherry-picked as a standalone usable
feature onto main**: its normalizer is absent, and its five tests use the public
`from deepviz import normalize` export which main also lacks.

1. **Keep the actual focused contract fix/new Mapping disposition.** The cleanup
   module internally imports only `ChartSpec`/`NormalizedData`; it does not need
   replacing main's contract with5ba's older model/validator. Do not regress the
   R31 Mapping-boundary fix while extracting a cleanup patch. No claim that the
   contract PR is merged is made here.
2. **Extract the complete reviewed normalizer file/hunks, not only the cleanup
   patch onto missing source.** Exact Python history is ba171160 →479550927 →
   f65096434 →305182390 →235e7e361 →ec9f669ef →5ba860305. Earlier parsing/shape/
   boundedness/heatmap/SUM prerequisites must not disappear. ec9 also touches npm;
   a Python foundation need not cherry-pick unrelated TypeScript paths/history.
   `source-chain.json` lists full commit paths/blobIDs for deliberate extraction.
   This review approves **only5ba-versus-ec9 cleanup**, not all those prerequisites.
3. **An intentional data-only initializer is the small dependency closure.**
   Normalize needs only models internally. The unchanged sealed initializer
   eagerly imports render→engines, so copying it creates a5-module eager closure;
   preserving all its public factory/CLI/MCP behavior expands to **all9modules**.
   Request an authorized small data-only export boundary instead. No new glue was
   implemented here, and reviewed canonical resources/typing/schema must still be
   included if exposed by the foundation API.
4. **Do not ship dangling entry points.** Rootmain metadata already names missing
   `deepviz.cli:main` and `deepviz.mcp_server:main`. Existing normalize CLI imports
   ToolSession/recommend and indirectly rendering; it is not a standalone data
   CLI. R04 should either explicitly defer those scripts/claims in the data-only
   slice or assign a separately reviewed narrow CLI. Do not import old tools/MCP
   merely to make a console command resolve. Both choices require source authority
   and package/consumer tests outside this source-only assignment.
5. **Carry the actual ownership acceptance and final integration gates.** Include
   the unchanged five5ba cases and the original owned/borrowed/reducer/Arrow future
   batch/error/retained-traceback/Windows rename controls, on the **actual assembled
   foundation SHA**. This source review is one independent reviewer gate; it is not
   a tester result or a substitute for the other genuine reviews/tests, package
   build/installed consumer/CI. R30-05's separate testing assignment is not polled
   or assumed completed. Its future result must name its real source.
6. **Do not silently call whole normalization ready.** Later mean/scalar/GraphQL
   and prefix-SUM limitations remain separately owned. They require an actual
   sealed source-owner handback and affected strict retests/disposition before
   broader foundation claims. No future GraphQL SHA was read, polled or tested;
   this worker may retest it only on a real later assignment/SHA.

**Verdict:** accept the narrow5ba cleanup **source review**; no additional must-fix
introduced by that delta was found. Block any unconditional main/foundation/v1
approval until R04 has the complete source boundary and genuine exact-final-head
gates above. No new bug ticket, policy weakening or new production grant requested.

**Not checked:** runtime/OS/Arrow behavior, full or selected suites, old GraphQL
matrix, later source fixes, builds/install consumers, npm, charts/browser visuals,
MCP/Deep Agent transport, scale/memory/RSS, current CI/PR status, release or900issues.
These are **out of scope/not run**, not passing tests or optional skips.

**Current action:** independent source review complete; prepare compact exact
commands/source/review evidence and own scoped publication. **One executable next
action:** preserve this bounded verdict/limits, stage only NEWR30-03 report/evidence
and own note; verify source/old-oracle hashes unchanged, explicit scope/whitespace/
secrets, meaningfulOWNcommit→nonforceOWNpush→exactremoteSHA, then hand R04 the source
gate and dependency constraints. No producer polling or product/test replay.

Publicationcheckpoint: OWNpreflighthelper **exit0**, exact11OWNpaths/stat1443insertions,
whitespace0/credentialpatterns0/source-config-ALLoldtestsdifffd11582=0 and13rawsealed
Gitblobsrechecked. Fullactualstagedreport/verdict/COMMANDSdiff readexit0. **Next
executable action:** refresh onlyfinalowncheckpoint/hashsnapshot, final11pathcheck,
meaningfulOWNcommit/nonforcepush/exactremoteSHA/copyownedcompactevidenceMAIN;
acceptSOURCEgateonly/no test or producer replay.
