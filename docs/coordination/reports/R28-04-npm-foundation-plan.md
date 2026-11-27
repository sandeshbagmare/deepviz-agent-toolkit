# Npm Foundation Dependency Plan

> **For the existing release manager R04:** this is bounded static dependency/extraction support for R27§3 and R29, not a second all-branch inventory, source grant or execution handoff. R04 alone owns final queue, implementation assignments, product PRs, shared/default merges and closures. Do not spawn from this packet.

**Goal:** identify the smallest dependency-complete npm package slice that can reach actual `main`, then list exact assets/fixes/gates needed for a usable main consumer.
**Architecture:** trace the immutable package public entrypoints through local imports, shared schema and build/runtime assets; compare only named candidate paths against actual remote main. Prefer path-bounded extraction, not blind entire-candidate merge.
**Tech stack:** existing Node/TypeScript npm workspace and shared JSON Schema; exact engine/tooling versions to be read from frozen metadata.
**Spec:** `docs/superpowers/specs/2026-11-26-deepviz-design.md`; manager queue `tasks/R27-manager-queue-and-plotly-release.md`§3; `tasks/R29-main-first-release-planning.md`§04 reservation.

## Prework / scope checkpoint — 2026-11-27

- Owner SAME-ID `ses_de5678314ffeuDXtC7RfGsbD6V`. Full MAIN current AGENTS/R29/R27 and own note read first; canonical/RESUME/STATE re-read. Existing own branch `agents/r10-04-utf8-field-envelope`, clean and exact published **`b235fc6422426df9bdeadae18174240ce9ec922c`**. Prior R22 cleanup evidence stays finite/unchanged and is not rerun.
- Fresh `git ls-remote --symref origin HEAD refs/heads/main refs/heads/agents/r10-04-utf8-field-envelope` exit0 at **2026-11-27T15:59:09.1951810UTC** proves default `main` **`0ae2cf26426822135fc10d337fcacf580b7ed833`**, ownremote b235. Exact `^{commit}` resolutions0: candidate **`3eab699b61850a20e91132e16caf8c589085f9ee`**, npm-integrated **`262b0da145e42c94c2908213272ec3be28771206`**, asset producer **`f9c437286c9dfe2245a7d914995d90346e29c233`**. Named immutable Git objects only, not changing producer working trees.
- Allowed writes ONLY this NEW report, `docs/coordination/evidence/R28-04/`, own actual-ID note and copies on own existing branch. Static Git/file inspection and sanitized evidence commands only. **No production/config/schema/original-oracle/othersnotes/APIwrites/install/test/build/browser/scale/oldbaseline replay; no spawning/shared/default/PR/closure writes.** No source-review duplication of helper14's one-line7d8 correctness/retest.
- Review focus: missing exported dependency; build/pack path escaping workspace; schema/assets absent from tarball; unsafe browser/normalization release blocker; unmerged helper/finite-SVG/COUNT repair accidentally described as shipped. Command recipes are proposals, not executed passes.
- **Current action:** inspect actual main tree and frozen npm metadata/entrypoints/import/build/schema/prompt paths; resolve narrow relevant history and exact dependency closure.
- **Next executable action:** `git ls-tree -r --name-only <main>` plus `git show <262>:package.json`, workspace/package metadata/tsconfig/build scripts and public entrypoint; record blobs/commits and dependency-complete PR order.
- No substantive source analysis yet; no product tests/builds installed or run; no result/approval/ETA claimed.

## Recommendation to R04 — minimum complete extraction, not another manager plan

**No npm product is shipped by the observed default.** Its7files are `.gitignore`, `LICENSE`, `README.md`, design+implementation-plan Markdown, `pyproject.toml`, and `python/deepviz/src/deepviz/models.py`. No public JS import, npm workspace/build, renderer, prompts or canonical schema exists at **main0ae2**. Main's Python metadata alone does not deliver the promised CLI/MCP either; Python21 owns that dependency plan. This task does not inventory other branches or change R04's overall milestones.

**Preferred source identity:** extract a bounded allowlist from **262b0da145e42c94c2908213272ec3be28771206**, preserving its later normalization fixes, then incorporate only genuinely sealed/reviewed successor hunks. **3eab699b61850a20e91132e16caf8c589085f9ee** is262's docs/evidence child, with **zero npm/source/config/asset differences**. **f9c437286c9dfe2245a7d914995d90346e29c233** is the pure4path prompt fix, not a usable base on main; f9's full tree lacks262's updated `normalize.ts` and finite-overflow regression. Original **6561c163ce8dee6882f9248ee0e379067c2d985c** establishes18original paths but predates critical later repairs. **Do not cherry-pick the entire foundation-to-candidate chain** or full stale producer trees.

Full exact paths, source blobIDs/SHA256/last-changing commits,6module import graph, locked metadata,20relevant source-history commits and174successful static Git reads are in [`../evidence/R28-04/npm-foundation-static.json`](../evidence/R28-04/npm-foundation-static.json). File enumeration is evidence of dependencies, **not43tests, issues, shipped features or passes**.

### A. Minimum unchanged public package closure — 18paths

All are absent on actualmain0ae2. The canonical schema becomes an existing path if PR33 or the schema prerequisite merges first; rebase and regenerate, do not add an independent conflicting contract.

| Exact paths from262 | Why these travel together |
|---|---|
| `package.json`, `package-lock.json` | Private root workspace `packages/deepviz`, public build/type/test/schema/package scripts, exact locked development toolchain. Retain both matching files; no dependency upgrade/install is authorized here. |
| `packages/deepviz/package.json`, `packages/deepviz/tsconfig.json` | Package `@deepviz/agent-toolkit`0.1.0, ESM/import+types exports, Node`>=22`, no CommonJS`require` export; strict NodeNext/ES2022/JSON imports, declarations+sourceMaps to`dist`. `prepack` runs build. |
| `packages/deepviz/LICENSE`, `packages/deepviz/README.md` | Files explicitly shipped; root LICENSE already exists but is not a substitute for package-local resource. README needs bounded accuracy changes below, not wholesale candidate rootREADME adoption. |
| `packages/deepviz/src/index.ts`, `models.ts`, `normalize.ts`, `render.ts`, `renderers.ts`, `schema.ts`, `chart-spec.schema.json` | Six TSmodules+JSON. `index→models,normalize,render,schema`; `normalize→models`; `render→models,normalize,renderers,schema`; `renderers→models`; `schema→JSON`. All source imports are local. Removing renderer/schema files while keeping current index breaks dependency completeness. |
| `packages/deepviz/scripts/copy-prompts.mjs` | Build invokes it; fixed source URL resolves to root`prompts/v1/`, independent of CWD, writes3literal files to`dist/prompts/v1/`. Without source prompts a clean build/prepack fails despite already-existing dirtydist locally. |
| `schemas/chart-spec.schema.json` | Canonical Python contract used by schema check and scale provenance. Must semantically agree with current actual Python model, not merely with the npm copy. |
| `prompts/v1/README.md`, `system.md`, `request.md` | Canonical raw Markdown copied byte-identically, exposed through three explicit versioned subpaths; not executable templates, a JS prompt-reader API, or a security sandbox. |

**Public runtime exports:** `chartKinds`, `ValidationError`, `isObject`, `safeKey`, `validateSpec`, `normalize`, `normalizeStream`, `defaultAssets`, `buildRendererSpec`, `render`, `renderStream`, `createTools`, `chartSpecSchema` (**13**, not just the README's headline API). Public TS types come from models/render. `render` defaults toVega; outputs HTML+metadata/`paths:[]`, not files. `createTools` exposes5framework-neutral render helpers, **not Python ToolSession/normalize_data/recommend_chart/MCP or a Matplotlib runtime**. Arrow/Parquet tokens require an external record adapter in JS.

**Expected—not built here—tarball closure:** sixJS+sixdeclarations+sixJSmap files, schema,3Markdown, README/LICENSE/package.json =25members. Installed consumers need only these; they do not need repo sources/copy scripts/Python. Source builds need the whole closure above. No prebuilt/generateddist, node_modules, source fixture or old benchmark JSON should be committed as a substitute.

### B. Test/command closure — 25additional existing paths, not optional oracle removal

Carry exact262 `packages/deepviz/test/` (**20files**) and these5support paths; all43source/support paths are individually listed/hash-pinned in the manifest:

- `packages/deepviz/scripts/check-package.mjs`, `check-schema.mjs`, `benchmark-stream.mjs`, `verify-streaming-scale.mjs`, and `packages/deepviz/.gitignore` (`.verify/`). The copy helper is already counted inA. Root main `.gitignore` already ignores dist/node_modules; no blanket rewrite required.
- `npm test` includes every`*.test.mjs`, including N21's import of `verify-streaming-scale.mjs`; excluding that script to make a small PR leaves a broken test closure. N21unit cases are not proof that all real scale tiers ran.
- Root `test:browser` selects `browser.browser.mjs` and`test_n17_boundaries.browser.mjs`; **it does not run** `native-semantics-n18.browser.mjs`. The latter needs an explicit future command. All three use real installed dev runtime assets/local serving for offline acceptance; dependency/browser installation remains an explicit future environment action.
- Do not import candidate `.github/workflows/ci.yml` wholesale: it assumes full missing Python/package/tools/MCP/scripts/visual/scale foundations. Propose a separately authorized **NEW `.github/workflows/npm-foundation.yml`** alongside the package, preserving PR33's contract workflow, with Node22minimum/24CI clean install/build/type/schema/strict-tests/pack/consumer and declared browser jobs. No workflow is written by this plan.

### C. Shared-schema prerequisite (small, independent of full Python renderer/MCP)

PR33 exact **99841ffb80e0f2ea90c753c1bf0ceff718e0e180** supplies strict numeric validation, **not** candidate dashboard JSON Schema clauses. Static semantic comparison finds exactly `$defs.ChartSpec.{if,then,else,allOf}` missing; formatting accounts for the larger text diff. Runtime main already has dashboard validation; do not silently ship a weaker structural schema as matching runtime.

- After the genuine33merge/default ancestry check, extract **only** the `ChartSpec.model_config.json_schema_extra` dashboard hunk from **728bbac47b747501ad27f40525220317ea218064**, preserving PR33's strict-numeric validator and all subsequentmain changes. Candidate-model diffafter33 is13insertions/1deletion, not a reason to overwrite its wholefile.
- Exact schema-support paths: `python/deepviz/src/deepviz/models.py` scopedhunk; `schemas/chart-spec.schema.json` freshly generated; `scripts/export_schema.py` and unchanged `tests/test_schema_contract.py` from262. These are4paths, distinct from the43npmclosure; canonicalJSON overlaps intentionally. Add/retain strict numeric and dashboard parity controls—do not weaken an old test.
- The export script/test imports `deepviz.models`; main currently has **no `__init__.py`**. In a clean controlled source environment this can use the namespace model without importing renderers. Do **not** copy candidate `__init__.py`: it eagerly imports missing normalize/render. Verify actual imported model realpath; use a fresh isolated gate environment with no stale installedDeepViz shadow, or coordinate with complete Python21foundation. Python fullrender/CLI/MCP is not an inherent npmcompile dependency.
- `npm run schema:check` compares JSONcopies/kinds/defaults, not Python execution. A currentPython→canonical export check plus shared fixture agreement remains mandatory. Regenerate npmJSON from the accepted canonicalblob; no hand-widening to executable schemas.

### D. Release blockers and non-blockers — distinguish foundation from existing source gates

| Item at the named immutable pins | Consequence / correct owner |
|---|---|
| Package sources present262, absentmain | Source inventory is ready for bounded extraction; **no new main/tarball/install/build approval**. R04owns author assignment, issue linkage (existing npmstories#14/#25, verify live), draftPR and exacthead gates. |
| Helper **7d8ccdce22430a9ddf3a14a9e64bf15b2373ae57** not included262 | Integrate only sealed minimal helper hunk+its unchanged strict regression after genuine14source-review/05test returns. **No helper correctness re-review/test here**; that lane supplies helper-specific prerequisites. Full render.ts/tree copy is not the hunk. |
| GraphQL **#34**, known separate F1 sibling preservation | FULL46line R22-03 report records prior5340TS63PASS/10strictRED (6carrier+4F1), not new results.262normalizer changes SUM, not selection/wrapper logic; do not infer a repair.16/R04must supply actual committed repair and independently preserve original carrier/sibling/business-errors/null/partial/count oracles before claiming complete exported normalization behavior. No new bug or waiver. |
| Native SVG **#37**, density **#32** | FULL57line R22-13 report records existing±1e308 range failure/1e200positive at5e.262renderers are **byte-identicalca25parent**, still use `(value-min)/(max-min)`;5e's7+/4−tickmargin patch is not integrated and does not fix range.12/R04must supply sealed stablefinite/readability source and fixed-head native geometry/image gates; not just higher tick precision, more screenshots or silent label/value clamp. |
| Python **COUNT07**, MCP security02/10/e47, Plotly18/#36 and Python readiness#35 | **Not automatically npmcompile dependencies or identical npm defects.** npm explicitCOUNT mapping already chooses`count`; retain realCOUNTvalue/count/otherbucket/large-number gates, not Pythonhunk transplantation. FULL53line R22-14 report identifies Python`engines.py`readiness, not this JSwrapper. PythonMCPpath/security/PythonCOUNT fixes belong to their owners; no blanket cross-runtime green or blame. JS browser text/readiness/security still needs independent exacthead tests. |
| Browser assets/security | Package has zero npm **runtime** imports/dependencies, but four browser engines use6pinned CDN URLs (Vega's3, ECharts/G2/Plotly1each), not bundled binaries. NativeSVG/table use no external renderer URLs. Trusted host`RenderOptions.assets` may override; ChartSpec cannot supply code/URLs. Escaping/scriptJSON/CSP/allowlists are staticstructure, **not a browser sandbox/CDN-health/literaltext proof**; Vega CSP currently contains`unsafe-eval`. Browser rejection, labels/tooltips, unexpected requests/errors and offline fallback need genuine gates. |
| Raw prompt/documentation scope | Preserve3canonicalbytes; Python-specific workflow in rawprompts does not grant JSmissing APIs. PackageREADME's historicalb6character-budget section is stale against262UTF8guards (64KiBcell/key,256KiBrecord,16MiBretained); its checkout-relative capabilitylink will not become an installed doc. Future owner must narrowly correct npm instructions/currentlimits/network/rawprompt/runtime scope without copying allresearch/docs or inventing registryavailability. Not a source edit this task. |

**Existing evidence, not newly executed:** FULL26line manager `R24-reviewed-npm-integration.md` reports exact262 build/type/schema/package/pack0, npm274PASS/0skip and25member47,082Bpack/manualmaterialized9consumerPASS. Independent f9asset scope reports were manager-read. These establish useful bounded package inputs; they do **not** satisfy extractedmain-source identity, currentmain build/install, allbrowser/strictnewbugs/finaltwo+two/CI/release gates. No live issue/PR state refreshed byAPI here.

## Concrete npm-specific PR/preparation order — R04 decides final release queue

### N0 — focused shared schema parity, after actual PR33 merge

- [ ] R04verify actual33merge/currentdefaultSHA; create fresh branch from it (or declare explicit stacking). Use the4paths/hunk inC, not broadcandidatecheckout; keep all numeric/dashboardschema tests.
- [ ] Futuregates: exactownmodel import; schema-generation`--check` no writes; original strictnumeric+dashboardruntime/JSON fixtures; two independent reviewers/two testers/source-specificCI. No fullPythonMCP import required just to export model. Commit/PRlinkedexistingcontractstory; merge onlyactualgreen/defaultancestry, not because plan is published.
- **User-visible result after genuine merge:** actual sharedJSONcontract matches existing dashboardruntime+strictnumerictypes; still no npmpublicpackage untilN1. This is a product prerequisite, not a report-only npmPR.

### N1 — one complete npm foundation PR, all43paths as an exactallowlist

- [ ] R04assign ONEauthor after mainbase is verified; extract43manifestpaths from262 into freshbase, preserving N0canonical schema and regen npmcopy. Do not blindcherry-pick6561/f9/allhistory or copy dirtyproducer trees. Include prompt4pathrepair as already integrated262; **do not make a separate unusable f9PR onto absent package**.
- [ ] Consume only actual sealed helper7d8/16GraphQL/12SVG successor sources with their ownedunchangedstrictoracles; review/revalidate new combinedhead. Those repairs are **not granted to this worker**. If they are notready, open dependency-labelleddraft/stackedfixpreparation, **not a merge-ready packageclaim**. A deliberately narrower publicAPI would require explicit manager decision/newreview/docs, not silently dropping render exports or failing tests to bypass blockers.
- [ ] Add narrowly authorized rootREADMEdiscoverylink, packageREADMEaccuracyfix and scopednpmCI workflow; these are named future adaptations beyond43immutablepaths, not currently approved production/config edits. Do not bring stale benchmarkJSON/hugeartifact/research/agentnotes/allPython/fullCI scaffolding.
- [ ] Futuregates below on exactextracted+fixedhead/actualtarball; genuine2review+2test, linkedissue and observedgreenCI before merge. R04records mergeSHA/mainancestry. **Result:** a local checkout/tarball ESM+TS consumer can validate, normalize/stream, generate nativeSVG/table or engineHTML+metadata, load sharedschema/rawprompts and use5framework-neutral helpers, with explicit asset/format limits. Notregistrypublication/fullPython/MCP/v1completion.

### N2 — independently verified main consumer and release evidence, not another source foundation

- [ ] DedicatedmainQA13 / R04assign disjoint npmconsumer+browser/security testers against **actual mergedN1SHA**, separatefromauthor. Confirm installed ESM/declaration/schema/3rawprompt resolution outside checkout and no source/distshadow; fresh package-memberhash receipt.
- [ ] Retain source-specific COUNT/GraphQL/helper/finiteSVG/literaltext/readiness controls, offline/no-unexpected-request/browsererror gates+openednativeimages; exactvalues/inputoutput/loss against originaloracles. A Pythononlyfix does not supply npmparity.
- [ ] Release-only fullstreamtiers10/1K/100K/1M/10Mwith one-shotconsumption/exactvalueoracle/boundedoutput+serializedpayload/elapsed/heap+RSS methodology; browsernativeoutput checked separately. No million-independent-markpromise or oldbenchmarkreuse. R04alone folds this into the fullPython/npm/MCP releasequeue/timing/issueclosures; unknown producercompletion times mean **no defensible v1date from this support plan**.

### Future commands — proposals only, ALL NOT RUN in this task

```text
# Only in a newly authorized clean extracted/fixed-head environment:
npm ci
npm run build
npm run typecheck
npm run schema:check
npm test
npm run package:check
npm pack --dry-run --workspace @deepviz/agent-toolkit
npm run test:browser
node --test packages/deepviz/test/native-semantics-n18.browser.mjs
# After exact-model-safe import / complete schema prerequisite:
python -m pytest tests/test_models.py tests/test_numeric_schema.py tests/test_schema_contract.py -q --strict-markers
python -m ruff check python/deepviz/src/deepviz/models.py scripts/export_schema.py tests/test_schema_contract.py
python scripts/export_schema.py --check
# Future release scale, NOT a dependency-plan test or a claimed pass:
node packages/deepviz/scripts/verify-streaming-scale.mjs --entry=<exact-consumer-dist/index.js> --output=<new-unique-scale-dir>
node packages/deepviz/scripts/verify-streaming-scale.mjs --visual=<that-scale-dir> --output=<new-unique-visual-dir>
```

`package:check` itself performs real pack/offlineinstall/consumer/type checks; its future execution needs an authorized clean environment, not this task's read-only sharedvenv. Independently inspect exacttarballpublicexports/schema/3promptbytes; buildtree asserts alone do not prove packedresources. Node22advertisedfloor and24CI need explicit runtimecoverage. Existingbrowsercommand omitsN18 as stated. Scale-script sampledRSS/heap can miss transient/native/browserpeaks; record that limitation rather than claim total-memoryboundedness. All new-head commands/skips/outputs/sourcehashes must be recorded by their actual future runner.

## Own work / verification / handoff status

- **Performed only:** named immutable Gitreads/JSON+importgraph/path/hash/metadata inspection; fullrelevantreportedgate packets read. Staticcollector174successfulGitreads/exit0writes oneownedmanifest. No packageimports, npm/pythonproducttests/builds/installs/browser/scale/APIs/source/config/schema/oldoracles/shared/default/PRwrites/spawn. Futurechecklist is intentionally unchecked, not174testpasses.
- **Static selfreview/readback exit0:** all43fileSHA256s re-match exact262Gitblobs;10resolvedsourceobjects unchanged;18+25closure/20existingtestfiles/13publicexports/schema4semanticclauses verified; MAIN+OWNmanifestbytes equal. Report142lines at that checkpoint, manifest70,105B including exact174command/exitledger. Allfuturegates explicitlyNOTRUN. Fresh `ls-remote --symref` exit0 at **2026-11-27T16:14:46.6347521UTC** stilldefaultmain0ae2/ownremoteb235; no PRmerge/CI/issue-state claim. No all-branch inventory or helper14 source-review duplication.
- **Publication preflight exit0:** explicit3OWNpaths only(plan/manifest/actual-IDnote); stagedwhitespace0/JSON/scope/43candidateblobhashes/reportchecklists/credential-patternscan0(no matches)/protectedproduction-config-oldoraclesdiffb2350. ExpectedHTTPSorigin/helpermanager/configuredauthor checked; APIcalls0. Evidence-onlyformatcompactionexit0 preserves identical parsedJSON/all174exactargv+exits, now58,564B/961lines/SHA256 **`b85ad6ae2895d5acf1fe2af1d7222bf2399fbb81b08e5330c66b5072ca5692f3`**, MAIN+OWNbyteequal; not a productcode/testcorrection. Refreshstage then meaningfulowncommit/push/readback; no runtimecommands.
- **Current action:** finalize self-reviewed boundedplan/manifest+ownnote on existingOWNbranch, explicitownedpathscope/JSON/blob/hash/credentialpattern/whitespace checks; meaningfulnonforcepublication and exactremoteSHAreadback. MAINpostpushreceipt will record observedpublication, not prediction/selfreferentialcommit.
- **One executable next action for R04:** consume this43pathmanifest with Python21/N0schema dependency; assign ONEcompleteN1extraction author and reserve actual helper/16/12fix gates, while continuing ready33defaultmerge. R04alone places it in the next2–4productPRqueue; no new manager/allbranchduplicateaudit.

## Plan status

### Static inspection checkpoint

- **Own static-collector failure exit1, no product execution:** initial immutable-metadata collector stopped in `tree()` on `git ls-tree` before writing its manifest. It appended an empty pathspec for whole-tree enumeration; actual stderr/argv require minimal diagnosis before correction. No code/import/build/test/API/source mutation occurred. Preserve this failure as command-harness history, not an npm defect. Next only reproduce `git ls-tree <main> -- ''` versus no empty pathspec, correct own collector and rerun static reads.

- Actual main has exactly7trackedfiles and **no npm workspace/package/JSentrypoints/normalizer/renderers/prompts/canonical schema**. Source3eab is a docs child of262; named npm source/config/assets compareidentical. Candidate262 contains7srcfiles(6TypeScript+JSON), rootworkspace+lock, package metadata/tsconfig, buildcopyhelper and3canonicalprompts. No runtime dependency on Python modules or npm external libraries from emitted module import graph; browser rendering separately loads trusted pinned library URLs, except nativeSVG/table.
- Publicindex eagerly exports models/normalize/render/schema, so exporting normalization alone while omitting render/renderers/schema is not a complete unchanged package. `schema.ts` imports JSON with attributes; `tsc` emits runtime/declarations/JSON and copy-prompts fills distMarkdown. f9is a4pathassetfix, not a standalone package;262 retains later candidate normalization changes absent from f9's fulltree. No entirebranch/cherry-pickchain recommended.
- Contract dependency discovered: PR33numericfix/schema is NOT the final candidate dashboard structuralschema;728bbac adds Python`json_schema_extra`+bothJSONcopies. Npmcheck-schema only compares canonicalJSON/runtime defaults—not actual currentPythonmodel. Need explicit model/schema prerequisite before claiming shared-contract parity; Python runtime/fullrender/MCP are not npmcompiledependencies. Must preserveactualmain/PR33 changes, not overwrite modelwith oldcandidatewholefile.
- Fullsource render/staticmapping read without source review replay: PythonCOUNTproducer07 is not automatically npmCOUNTblocker; npm mapping explicitly picks`count`for explicitCOUNT. NativeSVGfinite scaling uses`(max-min)`/`(xmax-xmin)`at262;5etickpatchnotintegratedandknownstablefinite/readabilityproducer12stillrequired. Helper7d8notin262 and must be integrated onlyafter14/05genuinegates, no duplicatecorrectnessreviewhere. Promptassets are rawPythonworkflowguidance, not implementation of Pythonnormalize_data/recommend/MCP inJS.
- FULLmanager26line`R24-reviewed-npm-integration.md`read: **reported**262build/types/fullnpm274/schema/package/25memberpack/manual9consumer—not our executedpasses/newmaincapability. No test/build/install/browser/scale/APIexecuted inthislane. Next build exact immutable per-file/import/script/test closure/hash/history manifest and bounded2–3PR extraction plan withnamedunmetgates.

- [x] Map main and the named immutable npm candidate dependency closure.
- [x] Specify minimum exact file/commit extraction and practical PR sequence.
- [x] Separate evidence already reported from unmet future gates and blockers.
- [ ] Publish bounded owned plan/evidence with non-force exact-SHA readback.
