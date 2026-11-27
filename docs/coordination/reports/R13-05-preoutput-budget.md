# R13-05: independent public-render pre-output budget tests

## Assignment and pre-work checkpoint

- Owner/session: `ses_de567830effe0E5yIwQgDACLMD` (same native ID confirmed 2026-11-27).
- Read FULL MAIN R13 common+05, own note, canonical/RESUME/STATE, R12 retained-budget task and producer report. Completed inspector113-pass/9-deselected handoff at7ddb752 is preserved and NOT rerun.
- Target published source: **5340bc69b7203ad7a9166543062482d819f9b705**. MAIN is at that SHA with shared dirty records preserved. R04's separate dirty R12 lane is not a test target and is not copied.
- Reuse existing clean own worktree `C:\Users\bagma\AppData\Local\Temp\opencode\r10-05-inspector-ses_de567830effe0E5yIwQgDACLMD`, branch `agents/r10-05-inspector-claim-retest` at7ddb752. An ordinary OWN-branch merge of5340 will preserve old commits and make the tested source exactly match published5340; actual Git HEAD and source identity are recorded separately. No shared branch mutation. Immutable R03 baseline0c5 stays untouched.
- Allowed writes: own actual-ID note, this NEW report, `docs/coordination/evidence/R13-05/`, NEW `tests/r13_probes/role05/`. No production/existing test edits, other notes, dependency installs/shared environment changes, shared Git/issues/PR writes, worker spawning or duplicate scalar10M.

## Independent acceptance / SDLC

1. Bounded oversized sparse-table and aggregate-dashboard fixtures exercise public `render()`; use deterministic tripwires to prevent large native/artifact allocations on defective source, never deliberate OOM.
2. Required rejection must be a real resource `ValueError` BEFORE output-directory creation/artifact allocation. An instrumentation tripwire is evidence of a missing guard, never relabeled as valid rejection.
3. Existing caller-owned files/directories must remain byte-identical; new output paths must remain absent on rejection.
4. Valid small table/dashboard controls must return exact input/output counts and truthful strategy/warnings; inspect actual compact rendering, not existence only.
5. Preserve strict RED tests on the source where a guard is missing; publish portable NEW probes, compact results/output and exact commands/exits/source hashes. Wait for actual R04 committed fix before any later independent retest; no dirty-source/future-GREEN claims.

Existing resource/output issue mapping will be verified read-only (21/22/23 as relevant); R04 owns disposition/closure. R12 proposed limits are10,000 expanded cells including headers and16MiB estimated expansion, not process RSS. This tester does not author that policy or implementation.

## Startup evidence and next action

Native session_move returned actual ID above. Git readback: MAIN5340, own published branch7ddb752 clean; source object5340 exists. Combined startup shell exit0; optional nonexistent new R13 branch lookup exit1, deliberately not created because recovery requires reuse of the existing own branch/worktree. No R13 tests executed yet (0 totals, no pass/skip claim).

Next: safe captured-GCM authenticated GET/user + target repository/ref + PR31/checks + resource issues, sanitized receipt only. On verified expected account, ordinary OWN-branch merge5340, source-byte identity check, read actual public call order, then NEW strict tests before any claim. The upstream service error has unknown cause and is not code-failure evidence.

## Exact source and remote preflight

Authenticated captured-GCM GET exited0 at13:54:27UTC: expected account/repository; public release/candidate and draft/open/unmerged PR31 both5340; three Python checks failed, other nine listed checks succeeded; issues21/22/23open. Sanitized `evidence/R13-05/github-preflight.json`; no token in files/arguments/logs.

Reused own clean branch/worktree, `git merge --no-ff --no-edit 5340bc69b7203ad7a9166543062482d819f9b705` exit0→mergeHEAD`a439d4d463a51115cc9139dbd5561eeab592f553`. This imports already-published coordination history, not new worker changes to those files. Source comparison `git diff --exit-code 5340bc69b7203ad7a9166543062482d819f9b705 -- python/deepviz/src/deepviz scripts schemas packages/deepviz/src` exit0 proves exact5340 production bytes. Completed inspector tests/publication untouched. No sharedcheckout/branch, R04 dirty source or existing oracle changed.

Read actual public call order and architecture: render normalizes each child, builds native payloads, then creates outputroot/artifactfolder. Matplotlib root/folder creation precedes figure construction; accessible HTML expansion occurs after native/static export. At5340 no whole-request dense expansion preflight exists. Next independent tests will distinguish native-boundary tripwires from actual budget `ValueError`, and observe real bounded ECharts output separately. No R13 tests yet.

## First strict public regression result (RED preserved)

```powershell
$artifact='C:\Users\bagma\AppData\Local\Temp\opencode\r13-05-preoutput-ses_de567830effe0E5yIwQgDACLMD-artifacts'
$env:PYTHONPATH=(Join-Path (Get-Location) 'python\deepviz\src')
$env:PYTHONDONTWRITEBYTECODE='1'
$env:R13_EVIDENCE_DIR=Join-Path $artifact 'case-results'
& 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' -m pytest tests/r13_probes/role05/test_preoutput_budget.py -q --tb=short --basetemp (Join-Path $artifact 'pytest-public') -p no:cacheprovider
```

Exit **1:20failed/10passed/0skipped3.66s** on exact5340 production bytes/ownHEADa439d4d. All20strict negative cases (table/dashboard×5engines×newoutput/existingcallerfiles) reach `AllocationReached`, an explicit test safety stop, NOT a real production budget rejection. Four Matplotlib cases reached outputroot/artifactfolder allocation first; other native boundaries are reached before output allocation but still lack required whole-request preflight. No fake resource-rejection pass or OOM. All10real small table/dashboard positive controls pass exact values/counts/strategies/warnings and caller-sentinel preservation.

Own helper dynamically spies public normalization (actual routine) and filesystem/native/figure boundaries; runtime monkeypatches are restored, production source bytes are untouched. Test-only error is not a subclass of ValueError. Input fixtures are128sparse rows/128unionfields=16,512expandedcells and80sparse rows/80unionfields/twochildren=12,960requestcells (6,480each). Newtable inputs1,957UTF8JSONbytes, dashboard1,181; under all preexisting row/source caps. Raw`public-budget-red.log` and20caseJSONs live only inuniqueownartifactroot. Next aggregate preciseevents and real boundedpublicoutput; open real smallrender image/browser, then lint/types and portablepublication. No R04fix observed or retested.

### Own collector/check failures (not hidden)

`python tests/r13_probes/role05/collect_public.py <artifactroot>` exit1 AFTER both bounded actual ECharts calls saved fresh artifacts. Own finalSVGtextassert incorrectly assumed text nodes; Matplotlib stores glyphpaths and literalcommentlabels. ActualSVG grep confirms `<!-- label -->`, `<!-- value -->`, `<!-- R13 small table -->`; ETdefault dropscomments. Pillow also warned own`getdata`deprecated. First-run timing/tracemallocvalues were held in memory and NOTsavedbeforefailure, therefore no values are claimed. Recovery will READ existingcompletedrenders, not duplicate allocations; ownresume mode will markmetricsnull/unpersisted and inspectcomments plusactualPNG/browser.

Initial scopedRuff exit1(two own import-order findings), mypy exit1(one own Optionalmodule`__file__` pathassertmissing), Node syntaxexit0. Fixesrestrictedtonewprobe importorder/nonnullassert/commentparser/pixelaccess/resumeexistingcollector. Strict20productRED tests and existing source/oracles remain unchanged. Raw`actual-public-collection.log`,`ruff.log`,`mypy.log` retained; no false all-checkspass.

## Recovered real output / actual visual inspection

OwncorrectedRuffexit0; mypyexit0(3NEWsourcefiles). `python tests/r13_probes/role05/collect_public.py <artifact> --resume-existing` exit0 read BOTHcompletedboundedEChartsoutputs and10existingpositivecontrols, **no rerender of oversized controls**. Missingfirst-run elapsed/memorymetrics explicitlynull/unpersisted; methodwouldbetracemalloc per-call Pythonallocations, NOTRSS/native/processpeak. No numericmemory/elapsedclaimborrowedfromR04.

| Actualunmockedpubliccall | Counts / nativeexpansion | Allocatedartifacts | Callerfiles |
|---|---|---|---|
|128rowsparseEChartstable|128input/128output, `none`,16,512graphics|HTML1,701,344B + manifest3,684,662B inNEWartifactfolder|unchanged|
|2×80rowssparseEChartstable dashboard|80input/160output,`dashboard:none,none`,12,960graphics|HTML1,295,087B + manifest2,853,376B inNEWartifactfolder|unchanged|

Bothreturns are missing-budgetguard reproductions, **NOTallowedoversized-renderpasses**. Onlynetworkdependencywarningreported, no truncation/rejection. The128rowfixtureis1,957compactUTF8JSONbytes anddashboard1,181B; bounded peak wasneverdeliberatelypushedtoOOM. LargeHTML/manifests remainexternalartifacts, notpublishedbulkdata; onlycompactsummary/hashes.

`$env:DEEPVIZ_NODE_DEPS_ROOT='C:\Users\bagma\deepviz-agent-toolkit'; node tests/r13_probes/role05/capture_small.cjs <artifact>/collection` exit0: installedChromium159.0.8154.6, twoactualstaticcompanionHTMLcontrols withvisibleimages,1/2accessibletables,A3/B7/C5,**0consoleerrors/0externalrequests**. SourceSVGparser nowretainsMatplotlibglyphcomments for literalchecks; realPNGisalsononblank. Openedactual`collection/small-table/chart.png`,`small-dashboard/chart.png`,`browser/dashboard.png`; observedcorrectheadings/headers/threevaluesandbothdashboardpanels, no clipping/overlapforthesefixedcontrols. Thisisboundedstaticinspection, NOTfive-enginebrowser/CDNacceptance.

Next: finalNEWtests/qualitychecks afterowncollector/importfixes, compactpublishedartifacts/report/explicitOWNcommit/nonforcepush/readback; strict20REDpreserved untilactualR04committedfix isreceived, notpolled.

## Final checked-file commands / exact result

Same readonlyMAINPython (`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe`), owncheckoutPYTHONPATH, noinstalls:

```powershell
$env:R13_EVIDENCE_DIR=Join-Path $artifact 'final-case-results'
python -m pytest tests/r13_probes/role05/test_preoutput_budget.py -q --tb=short --basetemp (Join-Path $artifact 'pytest-final') -p no:cacheprovider --junitxml (Join-Path $artifact 'final-tests.xml')
python -m ruff check tests/r13_probes/role05
python -m mypy --cache-dir (Join-Path $artifact 'mypy-cache-final') tests/r13_probes/role05
node --check tests/r13_probes/role05/capture_small.cjs
git diff --exit-code 5340bc69b7203ad7a9166543062482d819f9b705 -- python/deepviz/src/deepviz scripts schemas packages/deepviz/src
```

Actualexits **1/0/0/0/0**. Finalpytest **20failed/10passed/0skipped3.97s**, same20strictnegativecases, noxfail/deselection. Mypy3NEWfilesclean. Raw`final-tests.log/xml`,`ruff-final.log`,`mypy-final.log`preservedexternalartifactroot. No fullformats/scales/MCP/DeepAgent/distributionbuild rerunsforthisnarrownewtask; prior completedinspector/publication notrerun. A partialREDcommit is usefulbug/regressionevidence, notgreenCI/releaseacceptance.

## Findings / disposition / future retest dependency

**R13-05-F1 (P1, existingissue21resourceparent):** exact5340 publicrender lacks whole-request densecellpreflight; all20boundedoversizedtestsreachnativerenderboundary, fourMatplotlibcasesfirsttouchoutputroot/artifactdirectory. TwoactualEChartsoutputsconstruct16,512/12,960graphicsandallocateartifactsratherthanreject. A per-childcheckalonewouldmissthetwo6,480celldashboardtotal. Minimalproducerrecommendation: onewhole-requestpreflight afterrealnormalization andBEFOREnative/figure/outputroot/foldercreation; conservativeheader+missingcell/estimatedbytesaccounting; conciseValueError; no truncation/postserialization-onlygate. R04alreadyownsR12sourcefix, no competingimplementationhere.

Caller-ownedfilespassedall20instrumentednegativechecks plus10smallpositives andbothactualboundedcalls; this does NOTwaivefail-before-allocation. Smallpositivesretainexact3input/3tableoutput or6dashboardoutput,recordsA3/B7/C5,none/dashboard:none,none,andtruthfulCDNwarningsforECharts/AntV. No evidenceofcallerfileoverwriteinthisscope; do notinventanotherfinding.

FutureGREENBLOCKEDonactualR04committedfix. Awaitexplicitcleancommit/sourceownershiphandoff, runSAMEstrictNEWtests onthatpin, independentlyinspectrealoutput/preservationandcompareevents; donotcopydirtyfixorpollduringproduction. No issueclosure/finalsignoff/greenCI/900completionclaimed.

## Publication preparation checkpoint

Compactexport checked20negativeevents,30JUnitcases/20actualfailure names,4exactsourcehashes,2actualboundedrenderobservations,10smallpositivecount/strategy/warningrecords and2cleanstaticbrowsercontrols. Publishedcandidateevidenceincludes3genuinelyopenedPNGs(8,288/15,154/33,609bytes); no model-generated substitute. RawlargeHTML/manifests/logs/datasets/caches/venv/dependencies remainlocal. Initial16explicitstagedownedpaths scope/credential-shapedbytes/UTF8scanexit0; added17thactualstagedGitblobSHA256manifest, whitespacecheckexit0. No modifiedsource/existingoracle/oldinspectorpathwasstaged.

Currentaction: finalnote/reportcopy, stagedhash/scope/diffreadback, meaningfulstrictREDregression/evidencecommit onexistingOWNbranch, safenonforceOWNpush andactualremoteSHAreadback. R04futurefixnotreceived; no dependentGREENclaim.
