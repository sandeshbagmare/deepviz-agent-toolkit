# R39-04 independent dashboard-schema SOURCE review

What this change does: Exact728bbac47b747501ad27f40525220317ea218064 adds dashboard composition constraints to the generated shared schema. This review covers only that config/schema hunk and connected existing runtime checks, with the approved bff Mapping numeric guard retained as an invariant; it does not approve copying the old whole model onto main.

## Before-work checkpoint 2026-11-27

- SAME actual-ID ses_de5678314ffeuDXtC7RfGsbD6V; ownbranch agents/r10-04-utf8-field-envelope clean/published9087bb28e7981244fa3973e0d28db7f6c6c3b5da, freshremoteGit0/exactsame17:01:13.2353324UTC. Prior COUNT review complete/sourceonly/0runtime, not a schema gate.
- FULL MAIN R39common+04, both related R38 packets, currentAGENTS/canonical/ownnote read. Root direct reservation/admission is16+2upper18<=22, not proof22running; no selfdispatch/spawn/poll. R04 alone owns actual schema PR from actualmain31cff73ab057c3fed69bd400ac005f2f11609027.
- Exact immutable728parent40c67beef133663d8bb50c9db66494d5a0fbf826 identity0. Four changed paths: models.py, canonical schemas/chart-spec.schema.json, npm schema copy, tests/test_schema_contract.py. Oracle source155e42786ecfcdd8e04aed215c0751cd20ec3331 exists; find exact935c blob/path and read unchanged.
- Allowed writes only NEW reports/R39-04-dashboard-schema-source-review.md, evidence/R39-04/, ownactualnote/OWNbranch. No production/schema/config/oldoracle/install/env/API/shared/default/PR/closure/spawn/poll writes; no productmatrix/runtimebaseline replay. One NEW strict counterexample only if genuine material gap.
- Acceptance: full config/schema diff plus runtime dashboard composition/model validators/render inheritance/nesting/requiredcharts/JSONdump and schema consumers; exactGit/rawhash proof, strict bff Mapping import+guard preservation, unchanged14oracle. Old728wholemodel is NOT approved bff. New31cff-basedhead needs actual byteequivalence/affectedgates when provided, not inferredGREEN.
- Current action: immutable source diff/full related functions/schema structure/oracle and bff guard read NOW. Next bounded actual source finding or no-must-fix with limits; ownmeaningfulcommit/nonforcepush/exactremoteSHA and prompt ONEhandoff, not receipt loops.

## Meaningful source checkpoint

- Read FULL728 fourpathdiff/models92lines, canonical/NPM47lineclauses, semantic test change, entire export script, Pythonruntime composition validator62-69/publicrender136lines/CLI+ToolSessionvalidation, npm parseSpec97lines/schemaimport/checkscript. Required kind in BOTH if and nested-not is deliberate: absentkind defaultsbar and defaultchild{} stays valid.
- FULL unchanged14oracle191lines from155e427 read:17literalRAWJSONcases, runtime+generated/published schema decisions,2identity/export checks (36declared tests, NOT RUN), isolatedGit-before-import provenance. ReadbffnativeMapping45linecontrols and exactbff-vs728diff; actualmain31cffmodel byte-identicalbff (diff0). 728wholemodelhasdictguard, bffhasMappingimport/guard: copyingwhole728 WOULDundoapprovedfix; onlyconfig/schemahunkin-scope.
- Composition hunk mirrors existingruntime: dashboard requires nonemptycharts; non-dashboard including omittedkind allowsabsent/emptyonly; direct/nested dashboardchildrenforbidden; chartsarray/max24andallordinaryfields unchanged. Render's inheritance never changeskind/charts; no consumer execution was replayed. Previousdisplay loop printed artificial blankindices139-170 beyondactual136line728render; correctedboundedFULLread136 above, no sourceblanks/citations inferred.
- No genuine new material gap or warrantedcounterexample identified. Next exactraw/AST/schema4key/oracle935cproof plus retainedbffguard-invariant record; actualnew31cff-basedR04head NOTprovided/notapproved/notpolled. Source-only no-must-fix pending finalproof; no test/CI/main/v1 acceptance.
## Final independent source review

NO MUST-FIX in the CONFIG/SCHEMA HUNK at728bbac47b747501ad27f40525220317ea218064 against40c67beef133663d8bb50c9db66494d5a0fbf826. NOT approval of the whole old728model, unprovided newR04head, actualmain/v1/CI or GitHub human approval.

### Complete connected composition logic

- models.py:19-31; canonical JSON:33-42,222-231: explicit dashboard REQUIRES charts and minItems1, matching runtime models.py:62-64. Missing and empty charts are both rejected. Only minItems would miss an absent property; required is present.
- canonical JSON:26-42; runtime models.py:65-66: the else branch limits charts to0items. The if itself REQUIRES kind, so omittedkind follows defaultbar/non-dashboard semantics: rawemptyobject and explicitbar/emptycharts stay valid; omittedkind/nonemptycharts is rejected. Default annotations do not replace this conditional.
- canonical JSON:5-24; runtime models.py:67-68: every child with explicit dashboard kind is forbidden, empty or nonempty. The nested not REQUIRES kind too, deliberately preserving defaultchild emptyobject. Recursive itemref validates ordinary child fields; arraytype/max24/localref and all field types/bounds/extra-forbid are unchanged.
- FULL136line Pythonrender read, especially:30-46: validates rawspec before composition. Inheritance copies mappings/reduction/format/limits/theme/dimensions, NEVERkind/charts. Existing nonempty/no-nesting validators protect layout; no changed runtime mutation. CLI:41-48 and tools.py:94-100,132-142 validate before render. The historical renderer/toolkit is not approved wholesale.
- FULL npm models.ts:64-97 matches defaultbar, arraymax24, nonemptydashboard, ordinary nochildren, no nested dashboard. Only JSONcopy changes, not parser. schema.ts imports localJSON. export_schema.py:20-28/check-schema.mjs were read: exporter derives actualmodel; JS check compares copies/defaults, not every raw composition. Future actual-head generation/equality is a real gate, not replaced by this static review.

### Exact scope, immutable oracle and safety

- Fourchangedpaths only: Pythonmodel/canonicalJSON/npmJSON/tests-test_schema_contract. Model13added1removed; eachJSON47added; test4added1removed. Restoring only single original model_config line yields ENTIREparentmodel bytes. AST excluding that assignment is identical. All model fields/functions/dataclasses/runtime composition validators remain untouched.
- Removing only the four composition keys if/then/else/allOf yields semantically identical parent JSON. Static model config literal equals those exact clauses; canonical and npm copies are RAWbyte-identical. charts remains array/max24/localref; all other schema semantics retained. No executable callback/expression/HTML/path/network/parser/file-deletion or unbounded collection is added. Existing renderer spool/backend/resource issues are not approved by unchanged source.
- tests/test_schema_contract.py:52-63 is strengthened: missingcharts/omittedkind cases and BOTH runtime/schema rejections. The existing positive test uses expanded model_dump and alone could hide rawdefault/absence errors; retain the independent RAWoracle.
- FULL191line UNCHANGED oracle from155e42786ecfcdd8e04aed215c0751cd20ec3331, tests/r33_probes/role14/dashboard_schema_oracle.py, SHA256935c768e6e9bba81f425d11ba709c5bafbeffaec60a92c87e32fb746708501ea. Seventeen literal RAWJSON fixtures plus runtime/schema decisions and2identity/export controls =36DECLARED checks, ZERO RUN here. Snapshot/Git-before-import/isolated -B-I-S/explicit existingdeps/no unrelateddeepviz provenance read, not bypassed; no model_dump substitution or oracle edits.

### Mandatory approved-bff Mapping invariant

- Approvedbff9384d1ebe5c8f6f8f0f994300264b32bb98d8 and mergedbase31cff73ab057c3fed69bd400ac005f2f11609027 model Gitbytes are identical, SHA2568532ec73be4a212d822aab2ee5b021e9d56a7cc266ddbd9ae111ed8310b7262d. Mapping import and preserve_json_numeric_types guard MUST remain. check_dashboard function bytes match728/parent/bff.
- Whole728 still uses dict guard; copying wholemodel would undo the KNOWN nativeMapping repair. FULLbff tests/test_native_mapping.py:13-45 read, NOT RUN: UserDict/MappingProxyType root/child numericstring/boolean rejection, valid integralnumbers/defaults/no-mutation. This is the assigned known integration hazard, NOT a new duplicated finding or evidence that unprovided newhead actually regressed.
- In-memory reference applies ONLY728config to bff and retains exact Mapping import/guard. Reference LFmodelSHA256be2cb15f6f91f2de4b9ebd4e283ea677e9e39490932db3ecd9934f2d6c1e4a1f is NOT an actual produced/newhead hash or GREEN gate: neverwritten as production, imported, executed or tested. Actual new31cff-basedR04head NOTprovided/notpolled; actual byte-equivalence/affected gates remain required when supplied.

### Evidence, limits and handoff

- Staticcollector31Gitreads all0, raw/AST/schema4key/oracle935c/bff-reference assertions0; git show --check7280. Exactsource/consumer/testhashes and commands/exits in evidence/R39-04/source-review.json, MAIN+OWNbyteequal. These are syntax/metadata checks, not runtime testpasses.
- ZERO productruntime,14oracle,old82Mappingmatrix,NEWcounterexample,browser/matrix/scale,build/install,API,production/config/schema/oracle/envwrites,spawn/poll. No material new gap warranted a strict counterexample. PriorCOUNT/npm review and producerpasses are not this source gate.
- NextR04: retain bffMapping while applying only config/schemahunk atop31cff; on ACTUALfrozennewhead prove equivalence/guard and run unchanged14raworacle plus affected schema/numeric/nativeMapping/export checks with realsource/import/JSONidentity/appropriateCI. No predicted green/merge or waived gate. Deliver usable reviewed product onto main, not another foundationplan.
- Finalreport append initially scanner-rejected invalid-structure BEFOREexecution; tailverified noappend, shorterreplacement used. This is a document-write harness limitation, not productfailure.

Verdict: Ship this reviewed config/schema HUNK to affected-head gates; no must-fix source finding. Do NOTcopy wholeoldmodel or infer newhead/main/v1/CI/human approval.

Not checked: unprovided newR04head, runtime/import/export/oracle execution, tester results/CI/defaultstatus, images/builds/fulltoolkit. No productmatrix replay.