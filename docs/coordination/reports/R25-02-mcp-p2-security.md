# R25-02 independent MCP P2 security review

## What this change does

Exact reviewed final source e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23 contains P1d65dfc0 and P2cd75c459ddba9f3d6bc0a5185b570af369fb4980. P2 reserves bounded artifact slots before rendering and retains at most128issued resources per server lifetime. Prior URIs/files are preserved, not silently evicted or deleted.

Disposition: no NEW P2 blocker established in this bounded review. R22-02-F1 bare-string callback admission remains OPEN by exact unchanged tools/SDK bytes. This is not all-MCP/toolkit/final-release approval, not author signoff, and not a new P1 execution result. R04 reclaimed source ownership; reviewer02/tester10 cannot fix production.

## Scope, source and independence

Owner/native SAMEID ses_de5678328ffeYCFXQhRPKd4a9h. P1 checkpoint was completed FIRST: own2855f7a4d051297e1d9e1246fd3051d35e2a11f0 nonforcepush0/exactremote0 at15:40:15UTC. Its genuine8strictcases2RED6pass0skip1.72s were not waived or replayed here.

Read FULL MAIN R25common/followup/currentAGENTS/canonical/ownnote, full18producerhandoff with retained execution history, actual P2diff,146lineMCP,164lineauthor6testfile, render.py108-229 and installed SDK resource registration/lookup. Initial guessed R24-report path missing was a read error; correct22line tasks/R24-focused-pr33-head.md FULLread. No producer runtime/pending job/dirty state was borrowed or polled. R25 report/note saved BEFORE substantive review.

Unique NEW clean detached e47 source checkout. Four imports resolve there; mixed test additionally checks actual render module import. Seven working/Gitblob pairs and installed SDK versions/hashes unchanged before15:48:41UTC/after15:53:29UTC. Existing environment: Python3.12.16/MCP1.30.0/LangChain-core1.8.5/Pydantic2.14.4, no installs. Source/test proof in source-before/after.json.

Explicit P1 evidence limits, verified by equivalence.py exit0 at15:54:09UTC:
- Full tools/normalize/models/recommend/render/engines/P1author37test bytes equal d65=e47; full toolsSHA25611273c5f5b0ff2eee16e09c6c727e560582a43fcae723bb315b6ef80d5a68495. Installed LC source unchanged. Thus R22-F1 bare-string gap remains applicable without pretending to have newly run P1 on e47.
- All four released source/test paths exactly equal cd75=e47, proving no production/test changes after P2source. MCPfinalSHA2569f1628e04749c3c3d2357607ac4cc0021f74e1119c6237aa36077a0fd67bf480.
- Whole MCP d65 versus e47 is NOT identical. Its complete ValidatedMCP admission class source is identical, SHA25606b5949c1106e73623f9a981ebcb2fb06ab67815c7f8100196ae02716d908e9e. This class equality is static proof only, not a whole-module integration pass or new test execution. Fresh P2 test executes actual e47 server.

## Reservation review with line references

1. Lock and literal policy: mcp_server.py26,69-70,95-101 reserve k=4Matplotlib/3Vega/2other under threading.Lock. Check count+k against128 and increment atomically before ToolSession.render_chart103. A denied call cannot create a request output subtree through that path. Lock guards count only, avoiding render/read deadlock while concurrent work proceeds.
2. Accounting invariant: count includes issued resources plus all outstanding reservations. After qsuccessful registrations from reserved k, slots remaining=k-q. Each registration decreases slots at110-111; finally122-124 removes only remaining slots. On normal return net charge q. Failure before any registration releases all k; failure after qregistrations retains qcharges and old closures, never undercounts successfully issued URIs. No capacity expiry/eviction/deletion. A failed or future fewer-path renderer can release unused slots; current contract always returns exact4/3/2.
3. Fail-closed path-count contract:105-106 rejects unexpected extra paths BEFORE any issuance. Actual unchanged render.py172-225 gives Matplotlib png+svg+html+manifest4; Vega svg+html+manifest3; others html+manifest2, including composed dashboards sharing one artifact set. Checked against source, not an assumption from engine names. Future count changes need mapping/tests update; not a dynamic arbitrary budget knob.
4. Registration/read:72-91 validates actual path and reads current contained regular sized file BEFORE SDK registration. This avoids leaving an uncharged closure if reading/decoding fails. Its read closure80-86 rechecks containment/type/16MiB before bytes, and never retains file content as a lifetime field. Issued paths are fresh successful ToolSession artifacts. Existing ToolSession147-163 restricts destination/size and removes only failed private subtrees; P2 adds no host-file deletion/cleanup.
5. SDK MCP1.30.0 resources/resource_manager.py31-55 registers concrete URI resources;84-110 looks up exact resources/templates and lists current values. P2 adds no templates/unregister/eviction. Concurrent capacity check is guarded in wrapper; no private registry patch was used. Current CPython/SDK tested, not a blanket claim for arbitrary future SDK/thread runtimes.
6. Capacity guidance in server instructions65-66/error100 explicitly requires a host-created new server. A Vega3 winner from124 leaves127 and one unusable slot; rejecting all current minimum2resource renders is intentional documented policy, not evidence of overissue or silent loss. At most128closures is NOT an RSS/native/disk/transport-memory bound.

## NEW independent boundary execution, not old-suite replay

Author6already covers homogeneous8threadECharts at124 plus individual static3/4 nearcapacity. A missing boundary is heterogeneous4/3/2 simultaneous admission with early-allocation observation. Added ONE own strict test in tests/r25_probes/role02/test_mixed_reservations.py. No installed SDK/source/cap/renderer monkeypatches, fabricated outputs/private injection or duplicate old fixtures.

Fresh real server prefilled124resources: one realMatplotlib4 plus60realECharts2. Four worker threads rendezvous at a barrier then call actual public SDK with Matplotlib4/Vega3/ECharts2/ECharts2. Read-only per-thread sys.setprofile records entry to actual ToolSession.render_chart code; prior profile restored in finally, no frames retained. Thus matching accepted-only entry proves the rejected calls never reached output allocation, not just that they returned an error.

Final actual schedule: twoECharts accepted, Matplotlib/Vega denied at capacity before ToolSession entry. Final128resources/fournewfiles; all125priorfilehashes unchanged, earliest URI bytes readable, every new resource readable, host-owned/output and outside sentinel preserved. Subsequent two-slot request rejects without new file; no templates and ordinary normalization input_count2recovers at capacity. No fairness/particular-winner guarantee asserted.

Initial execution also passed, with Matplotlib4winner/threeearlydenials instead. Same ONEcase repeated only after own binary/text file-handle variable rename for mypy, not two independent tests or replay-to-green. Vega-winning127branch is allowed by oracle/static analysis but NOT observed here; author static-case evidence remains reported-only, role10 handles separate acceptance.

Actual own PNG opened after initial AND final runs: Alpha3/Beta7, zero baseline, heights3:7, visible full title/labels. Final SHA2561149288c93627d0e4ea4d4874a9ff122cc8003d8565454c7e1e48659fc28ab62. No browser/CDN/Plotly/Vega-paint claim. Asset saved evidence/R25-02/capacity-alpha-beta.png.

## Exact commands, results and artifacts

Own checkout C:/Users/bagma/AppData/Local/Temp/opencode/r10-02-security-ses_de5678328ffeYCFXQhRPKd4a9h, branch agents/r10-02-security-boundaries. SOURCE C:/Users/bagma/AppData/Local/Temp/opencode/r25-02-mcp-p2-e47-ses_de5678328ffeYCFXQhRPKd4a9h. OUT C:/Users/bagma/AppData/Local/Temp/opencode/r25-02-mcp-security-results-ses_de5678328ffeYCFXQhRPKd4a9h. PY existing MAIN .venv/Scripts/python.exe. Processlocal PYTHONPATH=SOURCE/python/deepviz/src/PYTHONDONTWRITEBYTECODE=1/PYTHONUTF8=1/MPLBACKEND=Agg, no shared environment changes.

- git rev-parse --verify quoted e47commit0/showstat0; git worktree add --detach SOURCE e47fullSHA0; exactHEAD/cleanstatus/whitespace0. P2diff only one source file and NEW author test204add19del, not a moving-main review.
- PY tests/r25_probes/role02/source_identity.py OUT/source-before.json0, then OUT/source-after.json0. Seven Git/worktree pairs, four same-process imports and three SDK source hashes equal before/after. Test independently verifies render import too.
- Initial PY -m pytest tests/r25_probes/role02/test_mixed_reservations.py -q -rs --tb=short -p no:cacheprovider --basetemp OUT/pytest --junitxml OUT/mixed-reservation.xml: exit0,1pass0skip3.72s.
- Initial Ruff0. Mypy1 reported three OWN harness typing errors from reusing binary/text variable stream, not product types. Rename binary handle to png_stream ONLY; assertions/fixtures unchanged. No xfail/skip or expected-value change.
- Final R25_02_RESULTS=OUT/final; same command with basetemp OUT/final/pytest and XML OUT/final/mixed-reservation.xml: exit0,1pass0skip3.16s. Final log/XML hashes saved; same1case, not2independentcases.
- Final PY -m ruff check tests/r25_probes/role02 exit0; PY -m mypy --cache-dir OUT/mypy tests/r25_probes/role02 exit0,2ownPythonfiles. No whole-product lint/type/suite pass inferred.
- PY OUT/equivalence.py exit0 proves exact fullpath/class equalities above, no source writes/test replay. Portable test recipe in tests/r25_probes/role02/README.md.
- Fresh expected-identity/repo GCM GET-only15:55:19.947322UTC:2HTTP200/APIwrites0; token memory-only/notlogs/subprocessarguments/files. No repeated PR/check polling, no issue/PR mutations. Prior P1snapshot15:31PR31draft6c72/threePythonCIRED is dated, NOT current final CI approval.

Compact summary, source/import/SDK/equivalence, actual initial/final mixed results, raw-log/probe/GitLF/artifact hashes and actual opened PNG under docs/coordination/evidence/R25-02/. Local raw command logs/XML retained under OUT. Own-source SHA/publication receipt added only after actual commit/push/readback.

## Limits, unresolved findings and next owner action

NEW P2 review establishes no additional concrete blocker, not full acceptance. Failure/unused-slot release was statically traced with exact invariants; not fault-injected or individually reexecuted here. One bounded real mixed race is not exhaustive scheduler/model checking.128resources does not promise processRSS/heap/transport/native/fullhostdisk cap. Local filesystem owner TOCTOU/hardlink controls remain outside documented model-authored path boundary. No new remote URL ingestion or execution capability introduced by reviewed diff.

P1 R22-02-F1 remains OPEN: tools.py188-196 bare run/arun skips early callback guard. Original strict d65twoRED evidence published2855f7a, sourceequivalence explicit above; no newP1replay or implied closure. Separate role10 does independent SDK/stdio/P2transport acceptance; no author43/gallery11/old32/fullsuite replay or borrowed independent approval. No source/API/install/spawn writes.

Author final54PASS/Ruffmypy0 is reported author evidence only. Full author result42FAIL2521PASS520ERROR5SKIP/buildmissinghatchling remains honest FAIL, NOT subtracted/waived or rerun by reviewer. No npm/build/provider/scale/browser/finalinstalledconsumer proof. PR33model slice/defaultmerge gates and other owners source are unrelated, not approved here. Fullproduction/900legitimatecreatedANDresolvedissues/greenCI unmet.

Executable next action: R04/root disposition P2with independent10transport report, and triage open F1 to an explicitly eligible producer AFTER that owner checkpoint/new source grant. Sourceownership already reclaimedR04; do not assume prior18MCPpermission persists while18Plotly work proceeds. Only affected minimal source/tests integrate into chosen exact candidate after review/retest; preserve independent02/10roles. Unchanged strict F1 must turn GREEN on a new clean committed repair before complete P1callback-admission acceptance. No final approval or source expansion.
Prepublicationactualcheckpoint: pack_evidence.py0 creates8compactOWN+MAINfiles includingopenedPNG; reconcilesboth1caseXML/allsourceimportSDK/probeGitLF/rawloghashes. No test rerun during packing. Current18MCPownershipalreadyR04, no new source grant; F1strictRED remainsopen. Next scopedOWN15paths expected including priorR22actualreceipt/report updates, R25report/evidence/probes/ownnote; explicitpathstage/credential+whitespace+hashscan/one meaningfulcommit/nonforceOWNpush/exactremoteSHA thenhandoff. Sharedcanonical/source/API untouched.
