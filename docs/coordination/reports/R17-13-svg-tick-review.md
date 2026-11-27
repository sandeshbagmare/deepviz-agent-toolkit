# R17-13 — independent native SVG tick-margin review

Status: INDEPENDENT REVIEW / TARGETED RETEST COMPLETE; OWN PUBLICATION NEXT, 2026-11-27. Narrow tick fix acceptable; inherited finite-range RED and known category-density issue remain. Not final-head signoff.

**What this change does:** `5e595a8` reserves native SVG horizontal space for the formatted numeric endpoints and sets a consistent 12px monospace axis font. Marks, axes and ticks all use the revised left edge; data, dimensions, vertical zero and pie geometry are unchanged.

**Own execution:** clean exact-source build0; unchanged author tests **11 pass**; NEW bounded checks **29 pass** (28 Chromium SVG/HTML captures plus one format/bounds control), zero browser/runtime/network errors. Separate NEW extreme-range regression **1 pass / 1 genuine fail**; no test waiver. Four own PNGs opened. Details and limits below.

## Review finding — must fix before general finite-domain output approval

1. **P2: Two accepted finite values can erase both bars** (`packages/deepviz/src/renderers.ts:225`, connected mark construction at252–259).
   - **What this is:** the vertical scale divides each value's distance from the minimum by the full numeric range.
   - **Problem:** public input `[{group:'negative',value:-1e308},{group:'positive',value:1e308}]`, bar/none/240×200, is accepted unchanged. `max-min` becomes Infinity: the negative bar has height0 and the positive bar has `y="NaN" height="NaN"`. Signed1e200 control produces two correct35px bars. Exact py expression is identical in parent and reviewed source: this is an **inherited** bug, not caused by the tick fix and not a new variant of category crowding.
   - **Smallest recommendation:** the eligible renderer owner should normalize finite endpoints before subtraction to avoid overflowing the range, preserving values and zero; add this strict regression. Do not silently clamp values, hide failed marks or expand schema limits. An explicit validation error is safer than returning invalid SVG if exact layout cannot be produced.
   - **If skipped:** the native renderer still claims a successful artifact/count while the visible quantitative data is absent. This lane has no production authority; R04 owns disposition/release.

**Tick-patch verdict:** no newly introduced defect found in the changed11lines or connected bounded cases. The numeric-clipping fix is suitable for integration with the disclosed density and finite-range limitations; it is not full visual/product approval. **Product verdict: fix1 before general finite-domain output approval.**

Not checked: full suites, scale, author20browser/full257npm replay, other engines, every IEEE754 value/OS font, standalone XML with existing HTML legend siblings, final integrated head/CI/four signoffs. Known narrow category crowding remains role12's separate work. Full production/900legitimate issues remain unmet.

- Actual reviewer/session: `ses_de56780caffekQ9gdZ58EgQwb5`, not the role12 source/test author. Full MAIN `tasks/R17-tick-fix-independent-and-density.md` common+13, canonical and own checkpoint read; dispatcher verified admission/parentage. No spawning/new descendants or runtime polling.
- Exact source under review: **`5e595a8f893955ce34a0e26553bb7bf257ea93ae`**. Source ownership handed back to R04; this task permits NEW tests/review evidence only, not production edits. Author's11unit/20browser/257npm results are reported context, NOT own results.
- Existing OWN publication worktree/branch: `C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5`, `agents/r10-13-ci-negative-controls`, clean at `1317dd12a00b128edf2bac7479500a513e5859a3`; observed status0/source-stat0. Prior31controlpasses versus36fullsuiteRED/3019pass/5skip and N15seven remain unchanged; no replay.
- Planned independent consumer: uniquely named clean detached checkout at exact5e595a8, using already-installed tools read-only. Prove actual Git blobs and imported build hashes; generated ignored build artifacts are allowed, production files remain unchanged. No installs or dependency/config/workflow/oracle changes.
- Owned new writes: this report; `docs/coordination/evidence/R17-13/`; `tests/r17_probes/role13/`; own actual-ID note. Publication remains existing OWNbranch, explicit staging/non-forcepush/actualremoteSHA after expected authenticated account verification. R04 alone integrates/sharedpublishes/issues/PRs.

## Acceptance / bounded plan

1. Read the11line renderer diff and connected native SVG axis/mark/tick formatting, font assumptions, legal240px bounds, pie/scatter/bubble and empty/single-group behavior; inspect public callers and schema constraints.
2. Run author's unchanged11NEWstrict unit tests ONCE on independently built exact source. No fullnpm/fullPython/scale/old31control reruns. Record commands/exits/counts/source/build/tool paths.
3. Add targeted NEW finite fixtures and actual rawSVG+HTML Chromium checks for positive/negative/scientific240px ticks, quantitative coordinates/zero/order/mark ratios/literal strings/dimensions. Include small multi-kind/empty/single-group controls and measured-font/bounds checks. Zero browser errors required; capture and OPEN own actualPNG. Do not mistake containment for nonoverlap/readability; knowncategorycrowding stays separate.
4. Save concrete findings/minimal recommendations and scope/limits, actual executions versus skips; publish small meaningful OWNprobe/review/evidence commits after diff/secret review and exact remoteSHAreadback. Non-author preintegration review is NOT four final-head signoffs or fullproduction/900acceptance.

Current blocker: none observed. Next executable action: inspect source-only diff/callers and author tests/report, verify exactsource object and unique consumer path absence, create detached consumer, then build/run bounded checks with read-only installed tools.

## Checkpoint 1 — source review / independent units / interrupted new browser probe

- Clean detached exact5e595a8 consumer created0; source/Gitblob equality proved. Connected public `render`→`buildRendererSpec`→`svgHtml`, mapping/normalization/dimensions and all renderer geometry read. Only renderer7insertions/4deletions; top/right/bottom remain65, horizontalaxis/marks/ticks consistently useleft/w, pie keepsleft65. Finite-format sample longest12ASCIIglyphs→left128→47pxpositive240pxplot; this is not a universalfontguarantee.
- Read-only existingTS build0; independent unchanged author-unit command **11passed/0failed/0skipped167.3585ms**. Evidence `evidence/R17-13/source-build-unit.json` pinsargv/Gitblobs/source/build hashes. This is an actual own run, unlike author's20browser/257npm.
- Added only NEWOWN`tests/r17_probes/role13/{svg-tick-review.mjs,README.md}`. Newbrowser command outer shell **timedout120s/exit143**, collector bufferedchildoutput, so no completed TAPtotal exists and no browserpass inferred. Seven ownDOM/PNGobservations were saved (positiveSVG/HTML,negativeSVG/HTML,scientificSVG/HTML,fixednegativeSVG); one boundedOWNprocesssnapshotexit0found no matching nodeprocess. Preserved `interrupted-run1.json` and originaloutputdirectory; no livecommandpoll/replay or productedit.
- Next executable action: diagnose the NEWprobe's bounded locator/screenshot stage using the saved rawSVG in a tiny read-only browser diagnostic; fix ONLY ownharness after observing cause, then run unfinished checks with streamedlog/finiteperoperationtimeouts. Production layout finding is not inferred from outertimeout.
- Boundeddiagnosticexit0: savedvalidrawSVG`:root`tag=`svg`; Playwrightnested`:scope > title`count0, directDOM`querySelector('title').textContent`=`R17 <literal> Ω`. Ownharness scopedselector(notproductionSVG) caused30sautowaits perrawcase and outertimeout. MinimalOWNfix uses directDOMtitlequery, adds5soperation/10stestlimits; originalsavedrun retained. Next correctedrun streamsTAPdirectly to unique log so futureinterruptioncannot lose completed results.

## Checkpoint 2 — actual independent browser geometry and image inspection

- Corrected NEWOWNprobe command exit0 **29passed/0failed/0skipped13,249.4049ms** (28actualChromium rawSVG/HTML cases +1finiteformat/minwidthvalidation control). Exactsource remains5e595a8; source/import/build/probe hashes and actualChromium version saved in new `browser-t8Ma12/identity.json`; fullTAP/argv/env in `evidence/R17-13/browser-run2.json`. Author's20browser/257npm were NOTreplayed or counted.
- Ownmeasuredpositive/negative/signedscientific/fixedtinynegative/1.5e308positivebar240px and measured8aggregate960px; numericline/area x[-3,0,9] unequal spacing, scatter, bubble r10/20/30, histogram2bins/4sourceobservations, empty/onebar, onepie, singlecolorseries with Unicodeandliteralmarkup. Alloriginalnormalizedvalues/order/counts/dimensions, expectedquantitativecoordinates/barheight/commonzero, area baseline, bubble radius, pie geometry and numeric label boxes passed; no externalrequests/console/page/runtimeerrors. Axisfontmeasured12pxmonospace with actualadvance≤8forASCIIendpoints on this host.
- OPENED via image-read actualOWN`scientific-signed-240-svg.png`,`aggregate-960-html.png`,`bubble-240-html.png`,`unicode-one-series-240-html.png`. Numericendpointsfullyvisible, scientificsigns/valuesunchanged;8aggregatebars arevisiblynear-equal; finitebubblepositions/radii present; shortUnicode/literalcategoryandfieldlabels remainvisible. PNGscreenshotsaloneareNOTexactdataevidence; DOM/normalizedrecords/geometry assertthat separately.
- No negativeusablewidthfound: 12glyphsampleworstleft128 yields47pxplotat240; actualmeasuredlabelsretain24pxleftspaceforaxislabel. Thisis measuredChromium/installedfontscope, not universalsystemfontproof. Known8categorynarrowcrowdingseparate/unresolved, no generalnonoverlap/readabilityclaim. Pie and color-series rawfragment has existing HTMLlegend sibling; those cases intentionallytestedrealHTMLonly rather than fabricate XMLstandalonecompatibility.
- Current action: complete connected numerical/bounds review, assess any concrete inheritedfinite-range failure separately from11linepatch, then preservecompactDOM/hashsummary+actuallyopenedPNGs. Next executable action: focused2finitevalues boundarydiagnostic on exactconsumer(no fullsuite/replay), then finalreview/disposition/ownedpublication.
- FocusedNEWfinite-rangecommandexit1 **1passed/1failed/0skipped201.4248ms**. Public2rowbarvalues[-1e308,+1e308] remainacceptedandnormalizedexact, but unchanged `(value-min)/(max-min)` overflowsrange→negativebarheight0/positivey,heightNaN. Signed1e200positivecontrolpasses. Parent/currentGitblobscontainEXACTsamepyexpression: inheriteddefect, NOTintroducedbytickmargin. StrictNEW`finite-range-regression.mjs`retainsfailure; no productionedit/xfail/hiding. Separatefromcategorydensityandprior36fullsuitecases; no countorremoteCIinference.
- Firstcompactsummaryassemblyexit1 beforeanysummary/PNGwrites: Windowsdefaultcp1252readfailedonUnicodeDOMJSON. Thisis OWNcollectorencodingerror, not productfailure; exact UTF8read fixesassemblyonly, no testsrerun or originalevidenceedit.

## Final source/geometry review and evidence checkpoint

- Native session move reconfirmed actualID `ses_de56780caffekQ9gdZ58EgQwb5`; publication worktree remains existingOWNbranch. Consumer stays detached exact5e595a8 with **empty tracked status**, no test/source/config/workflow/dependency/oracle edit. Build imported from that consumer, not MAIN editable source. Renderer SHA256 `be34bcb2be9e44459cb30d145386c3606933bcbdea389ba2fd3fca8d738fac80`.
- New margin work is constant-size formatting and does not add per-row work or collections; existing bounded normalized records/geometry flow remains. Min/max decimal/scientific `toPrecision(4)` output is ASCII; Unicode fields/categories are still escaped at their existing sinks. This inspection is not a benchmark/security audit of unrelated paths.
- **Measured Chromium159.0.8154.6:** all28 raw observations and input/PNG hash pairs verified; overall numeric-label leftmost ink31px and largest actual ASCII glyph advance6.878125px versus8px reserved. Signedscientific240 axis `M120,65 V135 H175`, numeric ink left39.421875px, bar heights35/10.501050105010506/35 and sharedzero100. Fixedtinynegative240 hasleft128→47pxplot and actualnegativeheight0.000034999982489125614: positive nonzero data geometry, not a claim that subpixel marks are legible.
- Numeric line x[-3,0,9] renders x[104,121.75,175], preserving1:3unequalintervalratio; area zero closure retained. Bubble centers[72,97.75,175], radii[10,20,30] retain square-root sizing. Aggregate960 plotwidth791 and8bars79.1wide retain exact originalvalues/height ratios. Empty zero marks, singlebar, histogram4source→2bins, piecirclecenter120,100/r35, single-series literalUnicodecontrols pass.
- Compact durable evidence: [`source-build-unit.json`](../evidence/R17-13/source-build-unit.json), [`browser-run2.json`](../evidence/R17-13/browser-run2.json), [`finite-range-regression.json`](../evidence/R17-13/finite-range-regression.json), [`geometry-summary.json`](../evidence/R17-13/geometry-summary.json), [`artifact-manifest.json`](../evidence/R17-13/artifact-manifest.json). Four actually opened own PNGs included alongside; original interrupted run directory/log receipts retained. UTF8summary reassembly exit0 is artifact-integrity work, not new product passes.
- Fresh safe GCM-captured in-memory authenticated GET `/user`200=`sandeshbagmare`, repo pushpermissiontrue; exactOWNremote tip1317dd1 matches localbase. GETPR31 stillopen/draft/unmerged/head5340; currentcheckruns show allthree Pythonjobsfailed, other listed checks success. No job-log/per-test count inference; these checks are not source5e final verification. [`github-prepublication.json`](../evidence/R17-13/github-prepublication.json) records the bounded GET-only snapshot. No shared/PR/issue mutation or credentials persisted.

## Exact commands and next integration action

Build and original11unit argv/log hashes are in `source-build-unit.json`. From the clean detached source, existing read-only compiler:

```powershell
node C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-n21/node_modules/typescript/bin/tsc -p packages/deepviz/tsconfig.json
node --test --test-reporter=tap packages/deepviz/test/test_r11_svg_tick_margin.test.mjs
```

From OWNprobe branch (source/build still pinned to the detached consumer):

```powershell
$env:R17_13_SOURCE = 'C:/Users/bagma/AppData/Local/Temp/opencode/r17-13-tick-consumer-ses_de56780caffekQ9gdZ58EgQwb5'
$env:R17_13_PLAYWRIGHT = 'C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-n21/node_modules/playwright/index.mjs'
$env:R17_13_OUTPUT_PARENT = '<NEW unique OWN output directory>'
node --test --test-reporter=tap tests/r17_probes/role13/svg-tick-review.mjs
node --test --test-reporter=tap tests/r17_probes/role13/finite-range-regression.mjs
```

Secondcommand intentionally remains strictRED on actual defect; do not turn it into expected-pass/xfail. Existing11unit ran once; only OWNinterruptedharness was corrected/restarted, no completed suite replay. No installs/fullnpm/fullPython/scale/old31CIcontrols.

Current blocker: inherited finite-range failure needs R04 owner disposition; does not invalidate measured numeric clipping repair. **Next executable integration action:** R04 inspect `git diff 5e595a8^ 5e595a8 -- packages/deepviz/src/renderers.ts` plus this report, integrate only scoped source/tests through its normal lane, keep categorydensity open, route separate stable-scale correction to an eligible producer, and perform true final-head gates later. Worker next action: explicit-path stage/scope/secret/whitespace review, meaningful OWNprobe/evidence commit, nonforceOWNpush and actualSHAreadback.

## Owned publication preflight

Explicit16OWNpaths staged/reviewed, 2NEWmjs syntaxchecks0, JSONparse/scope/credentialpatternchecks0, stagedwhitespace0. Geometrysummary losslessly condensed to43lines (all28cases/hashpairs/values retained); no observation/evidence deleted or test rerun. Sourceconsumer stillcleanexact5e, publishedbranchbase1317dd1; no sharedsource/workflow/existingoraclepaths staged. Next meaningfulOWNprobe/reviewcommit and nonforcepush/readback; publication not yet claimed.
