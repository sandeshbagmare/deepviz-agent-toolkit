# R29 main-first v1 release plan — manager-owned, execution in progress

## Delivery decision and executed repair — 2026-11-27

**The user is right: verifiedmain still has two commits and does not contain the toolkit implementation.** Remote/default16:00:51UTC is `0ae2cf26426822135fc10d337fcacf580b7ed833`; candidate3eab is NOT delivery. Immediate order: **gatedPR33merge → dashboard-schema parity → usablePythondata package → firstnative renderer**. Do not wait for this report, all branches or900issues before merging a usable fullygated slice.

**Executed:** [PR33](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/33) repaired head **`bff9384d1ebe5c8f6f8f0f994300264b32bb98d8`** was committed/non-forcepushed/exactremoteverified16:09:42UTC. Actual01/11Mapping finding accepted, notwaived: oneMappingimport/guard plus42permanentstdlibMapping root/child tests. New42RED36fail6positive→full**82PASS0FAIL0SKIP0.41s**, Ruff0/mypy0/schemaunchanged. SomeREDcases enforceguardmessage on previouslybounds-rejectedbooleans, not36bugs. **Newhead01+11review/17+15test and actualnewheadCI are pending. No merge/#30closure.** Rootmustdispatchusing`tasks/R32-pr33-mapping-repair-head.md`; publishedhashes/receipt`evidence/R31-mapping-publication.json`. Old998/e44JSONGREENisnotbffapproval.

## 1. Actual main capabilities, not candidate capabilities

Allsevenfiles at exact0ae2 were enumerated/hashed: `.gitignore`,LICENSE,README,design,implementationplan,rootpyproject,and`python/deepviz/src/deepviz/models.py`. Gitlogonly0ae2package/contracts+b9f7c17design. Installededitableimports and successfulworkerbranches do notchange that.

| Required capability | Shippedmain0ae2 | Missing source / release gap |
|---|---|---|
| Python contract/publicAPI | ChartSpec/NormalizedData/Artifact modelsource, metadata | PR33strictnumericMapping/schema/CI; no package`__init__`, normalize/render exports or installedconsumerproof |
| Normalization/adapters | **Absent** | Candidateba171/f650/305182/235e/3cf plus16sealedP1`5ba8603`,mean`c1b0b29`;16scalar/GraphQL/SUMwork stillowned |
| Streaming/statistics | **Absent** | Bytebudgets/finiteSUM7bc onbranches; remainingaccuracy/shape and fourfield-policyRED needresolution; old10MevidenceNOTfinal |
| Five engines | **Absent** | Candidate7c62+09f1/bb89/7698/theme6d0e/dense1c;07COUNT/08AntV/18Plotly stillactive |
| Dashboards/accessibility | **Absent** | Pythonrender/engines andTSrender/renderers; finalreplay/payload/geometry/native/browsergates |
| Agenttools/MCP | **Absent** | Base52b8/65b3+P1d65/P2cd75 atsealede47; bare-stringcallbackF1 remainsOPEN despiteP2capacitypass |
| npm/TypeScript | **Absent** | Sevenruntimefiles pluscompletebuild/workspace/schema/assets/package; helper7d8aloneNOTusablepackage |
| CanonicalJSONschema | **No file** | PR33export; later728composition-schema parity mustretainbffguard/regenerateexports |
| Prompts/assets | **Absent** | Pythonf67resources; npm f9integrated262 plusactualbuild/packconsumer |
| CLI/distributions/examples | MetadataadvertisesCLI modules that are **absent** | Implementedentrypoints/typedmarker8b268/resourceinclusion/wheel-sdist-tarball/cleanconsumers; localhatchlingmissing |
| CI/releasegates | **No workflow** | PR33contractCI; broadPR31previousPythonREDnottoolkitapproval |

## 2. Complete all-branch decisions

Onecompletedinventorycommand(exit0,automaticnotification,nopoll/restart): **103localheads/53officialremotebranches/103distinctnames/98uniquetips/134worktrees/36dirty**. One terminalAPIpage exactly matchedlsremote; zero staletrackingrefs/missingobjectfetches. **EVERYbranchhasdisposition** in`evidence/R29-release/branch-inventory.json`(944331B,SHA256`540d45be07d62c30db87b8dfb6eb50dfccaf6d86dd85847b2df55a9dbc83a764`), pluscompactsummary.json. Each exactlocal/remotetip/availability/owner hasproduct,test,otherdiffs vsactualmain; completeunmergedsourcecommitIDs/subjects; candidatedeltas/ancestry; review/test/gatewarnings. All98tipanalyses retained, including16local-ahead-remote. Laterbffpublication isseparate receipt, not rewrittenhistoricalsnapshot.

- `main`: onlysevenfiles. `fix/r22-strict-numeric-contract`: immediateproductdelivery; historical998supersededbyrealbff. `release/candidate`: dependencyblockedbroad draftPR31, **neverblindmerge**. Localreviewed-npm262alreadycandidateancestor; don'trepeat integration.
- Originalfeat/{ingestion,renderers,integrations,typescript,hardening}, fix/n03/n04/n05/n06/n07/n18,CI/performance/olderR02/R04/R12: historicalsource/supersededlanes. Keepvaluableexactcommits/dependencies; copyingoldtips dropslatercorrections. JSONpreserves each branch's own disposition, notsilentomission.
- Active07COUNT/08AntV/12SVG/16normalizers retainexclusiveownership.07local-only857/16local-aheadremote areunpublished/unapproved, **notacceptedhandbacks**. Dirty08/12source+historicalN05engine/N08README edits preserved/unadopted.18publishedproposal isnotpublishedPlotlyrepair.
- npm08f9alreadyintegrated262;12sealed5emarginstillneedsfinite/densityfix;07sealed7d8helperhas01+14reviews/05testsbutrequiresnpmfoundation;sealede47MCPneedscallbackF1repair/dependencies. Tester/review/docsbranches areevidence-onlyor explicitdependencyblockedwhereinheritedsourceexists: **don'twhole-branchmerge/countdocstipasapproval**. No reset/delete/cleanup/dirtyadoption.

## 3. Next four dependency-complete product PRs/tasks

Eachslice startsfromfreshactualmainafterprerequisitemergeor explicitstackedbase. R04ownsPR/default/closures. Namedreview/testlanes areassignmentsNOTapproval; rootrecordsactualSAME-IDreceipts. Originalstrictoraclesremainunchanged.

1. **PR33: usable strictnumericcontract, realissue#30.** Actualbff(parent998/base0ae2),9PRpaths: model/schema/original40+new42tests/focusedCI/actualJSONoutputs. NEW01+11review/17+15test, Mappingcounterexamples/sourceGit+importproof/literal-wire-schema/actual3-versionbffCI. **Published, independentnewgatespending.** Mergeimmediatelyifgreen; verifyPRmerged/actualmergeSHA/defaultancestor; notifyactualmainQA13; close30onlyafteracceptance. No waiting900/inventory.
2. **DashboardJSON-schema parity contract PR.** Exactsource`728bbac47b747501ad27f40525220317ea218064`: narrowmodel`json_schema_extra`compositionrules+regeneratedrootcanonicalschema+newstrictcontrols. Baseactualmergedbff; **retainMappingguard**, nevercopycandidate'solddictguard. Don'taddisolatednpmexporttoabsentpackage. Demonstrateemptydashboard/non-dashboardchildren/nestedchildrawschemaRED→GREEN; runtime/defaults unchanged; all82+neworacles/actualJSON/schema/lint/types/CI. OwnerR04; independent01+11/17+15aftercurrentcheckpoints. Linkexisting#27onlyifactualacceptancefits; otherwiseonereal deduplicatedconcreteissue—notquota. Exactsource-ready nextsmallPR, notanotherreadaudit.
3. **0.1 runnablePythondatafoundation PR.** ImmutablecandidatePythoncontract/normalize/resources/typing/metadatacommitshistories+16sealed5baP1/c1bmean **andactualfinalscalar/GraphQL/SUMhandbacks**. Public`__init__@3eab`eagerlyimportsabsentrender—doNOTcopyunchanged. Exportonlyimplementedinterfaces/documentstagedsurface; don'tadvertiseunimplementedCLI/MCPentrypoints. Include715c/f67schema+prompts/8b268typedmarker. R04packaging/extraction,16sole normalizers.21minimumfile/buildplanfeedsimplementation;03+04sourcereview/05fresh69+15laterlifetimeacceptanceareinputsNOTfinalpackageapproval. Need2newpackagereviews/2tests, allshippedformat/resource/statisticsoracles, realwheel/sdist/typedinstalledconsumer/resources/import/CI. **Blocked:** actual16fixes, fourfield-policyREDdecisionR04, missinglocalhatchling/clean-build-installauthority. No skip/errorwaiver.
4. **0.2 firstnativeMatplotlibAPI/CLI PR.** AfterPythonfoundation:7c62/09f1/7698/6d0e/1cdependencies forrender.py+engines.py/sharedchannels/geometry/outputmanifest plusactualCLI/exports.06providesminimalcompletefile/acceptancerecipe.07COUNTmustbeactuallyreceived/green; don'tsteal08/18functionscope. Ifmonolithicenginesrequirelimitedinitialsurface, explicitboundedengineadmission—notstubs/fakesuccess. PublicAPI+CLIbar/line/negative/time/count/onepassfixtures, inspectedPNG/SVG/HTML/manifest/labels/zerobaseline/hostsentinels/budgets, cleanpackageconsumer/CI/2reviews+2testers. **Blockedbyfoundation/07**, not900/allbranches. Remainingengineoraclesunchangedforlaterfullgate.

**Parallel npm release preparation:**04foundationplan+14exact7runtime/7packagepaths, notanotherhelper-onlyPR. Required`models/normalize/render/renderers/geometry/index/schema.ts`, workspacepackage+tsconfig+assetcopy/schema/scripts/lock/license/README/prompts/tests. Source6561/eb284/d5d6/28878 plus7d8helper/262prompts/5emargin andactual12finite/16normalizerfixeswhererequired;728Python/schemaagreement. Author274npm+9manualconsumer/05helper36+schema40/openedPNGs areboundedinputs, NOTclean npmci/fullpackedconsumer/newintegratedapproval. Newcompleteheadneedsbuild/typecheck/fulltests/schema:check/pack/assetlist/isolatedconsumer/browser0errors/security/2reviews+2testers. Mainhasno npm;unusableone-linecherrypickrejected.

## 4. Planned releases and usable outcomes

Labelsbelowareplanningmilestones, **NOTcreatedtags/releases**; sourceversion0.1.0isnotdelivery. MarkdoneonlywithactualPRURLs/mergeSHAs/defaultancestry/outputgates.

| Milestone | Usefuloutcomeonmain | Status/criticalprerequisites |
|---|---|---|
| **0.1 Pythondatafoundation** | Cleaninstall/importChartSpec+normalize forboundedrecords/CSV/JSONL/explicitmappings/correctreducers+metadata/packagedschema-prompts-types | NOTdelivered:33→schema→datafoundation;16knownfixes/buildblocker |
| **0.2 Firstnativevisualization** | PublicAPI+implementedCLI→inspectedMatplotlibPNG/SVG/accessibleHTML/manifest | NOTdelivered:package+07sharedchannels+nativepath |
| **0.3 Fiveengines+dashboards** | Matplotlib/Plotly/Vega/ECharts/AntV+faithfulboundedcomposition/themes/axes/accessibility | NOTdelivered:07/08/12/18actualfixes/remainingbaselinegroups/replay-payload/native+browser0errors |
| **0.4 DeepAgents/MCP** | Five rendertools+profile/recommendation/safeexplicitdataauthority/stdioresources | NOTdelivered:usablePythonrender+e47+actualcallbackF1repair/SDKstdio4-3-2failure-retention/packagedexamples |
| **0.5 npm/sharedcontract** | Actualpack/installJS toolkit/PythonJSONagreement/portableprompts/browseroutputs | NOTdelivered:completenpmfoundation+12/16fixes/schema+isolatedpackedconsumer |
| **1.0 RC→production** | Reproduciblepackages/examples/allstrictCI/realoutputs/independentreviews/documentedoptionalengines/bounds | NOTready:finalexactmerged-sourcegates;900legitimatecreatedANDresolvedgoalremainsseparatelyunmet—notfabricatedfromtests |

## 5. Honest forecast and actual blockers

**Firstmerge:** nextactivemergewindowafterbff'sfourrealreports+newCIgreen; potentiallythissessionifnonewfinding, **noclocktimepromise/noREDmerge**. ActualmainQA13/acceptancefollowmerge, notsynthetictestmergeSHA.

**Conditionalplanningranges, notcommitments:** afterfirstmerge **andbuild/installationpolicyunblocked**, datafoundationroughly**1–3focusedworkingdaysoptimistic/3–7likely**; nativepathadds**1–2/2–4**; remainingengines/tools/npm/finalRCoverlapbutneedserialsourceintegration/review: **about1–2weeksoptimistic/2–4weekslikelyforfeature-completeusableRC**, lowconfidence. Thesearemanagerengineering/gateestimates, NOTmeasuredthroughput/headcountpercentages/fixeddates/production1.0promise. Unknownbackendpermission/data-loss-numeric/nativebrowser/CIblockersstopforecastclock. Re-estimateafteractualmerges/cleanconsumers. Fullproductionincluding900realissuecompletionshas **nodefensibledate** withoutlegitimatebacklog/resolutionevidence.

Basis: sourceexistsbutpackage→native→toolsrequires≥3serialusableintegrationbases, activecrosscuttingrepairs andexact-headindependentcycles. Focused82tests0.41s/priorfullPythonminutes showCPUtestcountisnotdeliverybottleneck; correctextraction/knownbugs/environment/reviewCIare. No agentcount-as-progressclaim.

## 6. Gates and workforce execution

- ExactfrozenGit/import/buildprovenance; fullshippedPythonstrictsuite/Ruff/mypy/wheel-sdist/typedinstalledconsumer, npmci/build/typecheck/test/schema:check/pack/isolatedpackedconsumerwherepermitted. **Missinghatchling/installpermissionisBLOCKED, notsilentlyinstalledorpassed.** Preserveallstrictoracles/failures/errors/skips; nofourpolicyREDquietlysubtracted/schemaexceptionwaiver.
- Actualnative/browser/SVG/PNGsemantics+accessibledata, openactualoutput; console/page/bootstraperrorsfail. OptionalCDN/columnardependenciesexplicit. PR33modelJSON/schema/erroroutputisapplicable—notfakechartrequirement.
- Finalchangedstreamingpaths10/1K/100K/1M/10M withinput/consumed/outputcounts/values/strategy/warnings/time/memorymethod. Oldscale/authorcostnotfinalcandidateapproval; no duplicate10Mwithoutfreeze/allocation.
- Twoindependentreviewers+twotesters/realissue/actualoutputrationale/observedgreenexactCI. AgentreportsnotGitHubhumanapprovals. Actualmerged=true/mergeSHA/defaultancestry/mainQAprovearrival; onlythenacceptanceclosure/release/tag. No900fakeissues.
- **Savedusefulallocations:**rootactualacceptedR3003P1secondsource-review/05fresh69/20MCPsource-review/06firstnativeextraction/19source-gatepacket;04npm+21PythonplansfeedONEmanager.07/08/12/16/18exclusiveimplementationunchanged. R32realbff→01+11/17+15affectedgatesNOW;02R31callbackproposalfeedsmanager'snextreclaimedtoolsfix. Rootfreshcapacity/SAME-IDactualreturnsONLY/noR04spawns/projected22. Refillusefulactualsliceauthor/review/test/consumergates, notknownunfixedREDreplays/filler.

**Executable nextR04action:** receivebffgates/actualnewCI→mergeifgenuinelygreen/defaultproof/notify13. Whilegatesrun, preparenarrow728schemafollowupfrombffinseparatestackedworktree andclose21/04/06dependency/buildpolicydecisions. Publishthisownedplan/inventorysafelybutneverdelayactualmaincodefordocumentation. Originalsuccesschecklist/historypreserved.

---

## Original pre-work and command history (preserved)

Owner/session: R04 `ses_de56ad930fferPKGibj5Mc304B`,2026-11-27. FULLlatestR29/R26/R27/R30/design/architecture/currentcheckpoint/ownnote read. Onlyrelease manager; rootexecutesvalidown-childadmission/dispatch. No anothermanager/source-coownership. Allworktrees/dirtyfiles/branches/canceleddecisionspreserved.

## Pre-work evidence / acceptance

- LastactualdefaultGET0ae2/seven-filefoundation; focusedPR33published9988paths/allthreePythonversionsGREEN/fouractualfinalreportsinprogress. **DoNOTholdafullygated33forthisinventory/900/wholetoolkit**. Actualmainmerge/defaultancestry/QA13/acceptanceclosurearenotyetclaimed.
- MAINrelease/candidateactual **3eab699b61850a20e91132e16caf8c589085f9ee**, product262b0da, ownscoped17pathcheckpoint/nonforcepush0/exactremote0/PR31draftbodyPATCH200+GETverified15:56:18UTC. Dirtyworker/rootrecordsremainuncommittedandmustNOTbesilentlyadopted. No commandsinflight.
- Boundeddeliverable: completeofficialpaginatedremotebranches+localheads/tracking/worktrees/sourcecommitdiffsagainstfreshactualdefault; EACHbranchdisposition/owner/productvsQA/supersession/unpublishedstate; actualmaincapabilitiesandgaps; next2–4dependencycompletePRs/exactfile-commitprereqs/2review2test/actualoutput-CI-buildgates; milestone/optimistic-likelycriticalpathforecastwithunknowns, notagentheadcount.
- Output `docs/coordination/evidence/R29-release/branch-inventory.json` plusthisplan. Ownmanagerpublicationexplicitpaths/nonforce/readback, nofreshROOTfiles. Source07/08/12/16/18remainexclusive. Supporting04npm/21Python/06staticrenderplansand19source-gatepacketfeedthisONEplan;03/20narrowreviewsfillrealgates. R30rootdispatchpendingactualreceipts, notactivityclaim.

Next executable action: onefreshmemorysafeofficialGitHubdefault/ALLbranchpages+completegitlocalrefs/worktrees/source-logdiffsnapshot; retainactualcounts/paths/hashes/dispositionswithoutdeleting/fetchingdirtywork. Then writeconcretemain-capabilitygap/orderednextPRsandperformnextsourcePRpreparation. IncomingPR33finalreportsinterruptinventorywhenmaterial/fullgatesready.

## Actual inventory command launched once

Externalown`r29-branch-inventory.py` started **shellsh_21dbb9249001rexBcjZSMa22bX/PID31924**, background accepted. Itcapturesofficialpaginatedbranches+lsremoteexactequality/localheads+tracking/ALLworktreesdirtysource/uniquetipdiff+sourcecommitlist/defaultfilehashesandoneexplicitdispositionperbranch. Uniqueoutput`evidence/R29-release/branch-inventory.json`; no credentials/sourcewrites/polls/deletions/force. GitfetchONLYmissingremotecommitobjectsifneeded, no dirtyadoption. **Result/countsNOTYETknown; awaitautomaticcompletion, donotpoll/restart**. Whilethisrunsmanagerhandlesactual33gatecompletions/nextdependencyreadiness—notanotherunrelatedimplementationloop.
