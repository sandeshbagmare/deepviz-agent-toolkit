# R35-03 second independent finite-only SVG SOURCE review

BEFORE WORK: SAME native ID ses_de5678315ffeDxQVEpE9V9WSTE; own branch agents/r10-03-echarts-numeric-x HEAD9c387bc51265fcb7097c28413c25009ebae80b52 equals actual own remote, tracked clean except own artifacts. Full R35 common+03/root dispatch/current AGENTS/canonical/ownnote and ponytail-review read. Prior cleanup0tests is a different gate. R04 sole manager,09 separate finite reviewer/tester,12 active author not self-review.

Exact sealed c3ee1edbfc65406cef7fd809f5a6887471d576a5 parent5e595a8f893955ce34a0e26553bb7bf257ea93ae; initial gitshow/difftree0 confirms renderer+NEWunit+NEWbrowser three paths. No342/d017 density. Source-only full numeric19line diff and public geometry/finiteJSON/error-before-artifact paths; one tiny NEW strict counterexample only if a real material gap needs it.

Allowed NEW R35-03 report/evidence/ownnote/own branch publication and optional justified tiny probe only. No production/config/schema/oldoracles/SDK/API/install/env/shared/default/PR/closure/spawn/jobpoll/receiptloop, no old13/29/npmwhole/browserfull/scale replay or borrowed author results. Exact raw Git/hash proof and own meaningful nonforce publication/readback required.

Initial combined checkpoint shell request was scanner-rejected invalid-structure BEFORE execution, no file/source command ran. This simpler checkpoint replaces only that failed write. Next executable action: raw Git extract sealed3paths/parent/connected TS sources, full read, bounded independent verdict or ONE needed tiny proof; no full suites.

R35 extractor exit1: own collector wrongly requested absent root tsconfig.json, gitshow128; partial own raw copies only, no product execution. Exact tree diagnosis0 locates package-local config. Correct only collector path selection before raw extraction once; no production/config edit or suite fallback.

## What this change does:

The finite-only patch prevents opposite-sign finite axis endpoints from overflowing during coordinate subtraction. It shares the safe fractional mapping between Y marks, numeric X marks and numeric X ticks, and rejects nonzero Y measurements that would otherwise be emitted at the zero baseline.

**Independent verdict: accept the narrow finite-only SOURCE gate at c3ee1edbfc65406cef7fd809f5a6887471d576a5. No new concrete must-fix found in the reviewed delta.** This is a non-author source review, not tester, whole-SVG/density, final-head, CI, merge or v1 approval. ZERO product imports/tests/probes/builds/browser runs; author results were read, not borrowed.

## Source and exact-diff evidence

- Raw Git target c3ee1edbfc65406cef7fd809f5a6887471d576a5, parent5e595a8f893955ce34a0e26553bb7bf257ea93ae. Renderer blob7d0b0caa1d4f44bfd26bb1b18ed01337b3581142, SHA256 0538490fbf14a8ca4f1f39f7f880db5ea17d94c6873362243778e1160bc77b4a;285lines/22,357bytes. Twelve source/test/metadata files copied from raw binary Gitshow and rechecked byte-exact. OWNcheckout remains9c387, not target; no dirty producer file was read.
- Complete THREE-path functional change inspected: renderer +16/-3 =19changedlines; NEW86line unit file; NEW91line browser file. New filenames contain density but these sealed versions contain only finite-coordinate controls, not342/d017 density changes.
- Static check exit0 reconstructs the complete parent renderer byte-for-byte by undoing ONLY the new fraction/py block and the two numeric X mark/tick replacements. Every byte outside svgHtml is identical. Font sizes, margins inherited from5e, stride, label shortening/escaping, legend, mapping, other engines and geometry branch selection remain unchanged. No hidden font/density change.
- Full renderer285/NEWunit86/NEWbrowser91/render143/models97/index4/package metadata read. Connected normalize flatten/retained reducer/public sync+stream sections and bounded payload callers read. source-identity.json/renderer.diff/static-proof.json retain identities and exact diff. This is source provenance, not loaded module identity; no product module was loaded.

## Independent connected numeric and geometry review

References are packages/deepviz/src at EXACTc3ee, not our old OWNcheckout or later density work.

| Code | Source review conclusion |
|---|---|
| renderers.ts:225-232 fraction | The divisor stays1 unless low<0 and high>Number.MAX_VALUE+low flags a potentially overflowing mixed-sign range. In particular, same-sign MAX differences and subnormal-only intervals retain the original subtract-before-divide ordering. This guard is conservative near rounding boundaries, not an exact if-and-only-if test for overflow. When selected, division by the larger endpoint magnitude bounds the subsequent subtraction; the resulting fraction must be finite or raises ValidationError. |
| renderers.ts:220-238 domain/Y | The inherited Y domain includes zero and at least1, so it is never the constant-domain branch. Symmetric signed endpoints yield endpoint fractions0/1 and zero1/2; signed bar lengths and common baseline are preserved. Asymmetric endpoints use the same affine transform, not sign clipping, absolute values or replacement of literal data. |
| renderers.ts:233-238 nonzero/literal guard | zeroY and py use the same arithmetic. A nonzero measurement whose final coordinate rounds onto zeroY raises a typed ValidationError, rather than returning a successful artifact with an invented zero. This is a deliberate rejection of unrepresentable requested geometry, not input truncation or an error-as-pass. It does not claim all distinct observations must occupy distinct pixels. |
| renderers.ts:236 negative zero | JavaScript negative zero compares equal to zero, so value!==0 is false for either zero sign; true zero bars are not incorrectly rejected. The numeric domain and string serialization keep existing zero behavior. This is code reasoning, not an executed negative-zero test. |
| renderers.ts:239-245 numeric X | Scatter/bubble and all-numeric line/area use the shared fraction. A constant X domain returns0, matching the old left-edge behavior instead of a zero denominator. Empty rows have no mark/tick calls, so internal Infinity/-Infinity extrema are never emitted as geometry. |
| renderers.ts:245,277-279 mark/tick agreement | Numeric point and tick X coordinates both use fraction(value,xmin,xmax), then the same left+w mapping. Categorical grouping positions are unchanged. MAX-adjacent same-sign inputs keep direct differences; subnormal X intervals keep direct division before pixel multiplication. No clamping, stringification of numeric X, ordering change or raw row rewrite is introduced. |
| renderers.ts:264-274 native geometry | Bar/histogram top and height still use py(0)/py(value), line uses original ordered px/py pairs, area adds original zero-baseline closure, scatter/bubble use the same pair; radius/size/grouping logic is unchanged. All five requested native shapes reach the shared Y guard. Numeric X ticks cannot retain the former overflow path while marks take the new transform. |
| models.ts:64-95; normalize.ts:292-327,352-377,464-500 | Public spec validation supplies bounded integer dimensions/point counts. Normalization admits finite numeric scalars, replacing nonfinite inputs with null; mapping then rejects null/missing Y and numeric-X requirements. Existing retained-data byte/count limits precede geometry. The new helper adds constant work/state per coordinate and no unbounded data copy. It does not repair inherited normalizer math or unreviewed optional paths. |
| renderers.ts:21-25,27-61; render.ts:74-107 | Existing field/series/title HTML escaping and script-JSON escaping are byte-unchanged. New code interpolates no data string or executable expression; it only computes numeric coordinates and a fixed error message. Literal normalized rows/metadata are not rescaled. No new HTML, filesystem, remote input or code execution surface. |
| render.ts:40-71,112-123,133-140 | render and stream/tool callers share buildNormalized. checkPayload enforces the existing32MiB combined normalized payload budget first. svgHtml must complete before buildNormalized/RendererResult returns and before artifact creates HTML; unrepresentable Y throws with no successful artifact. This npm API has no file writes (paths=[]), so a caller cannot receive partial persisted output from this delta. |

## Read-only acceptance controls and limitations

The new unit file was read in full: symmetric/asymmetric extremes, five kinds, shared numeric X ticks, adjacent MAX X spacing, subnormal X ratios, all-negative bars, empty/zero/constant domains and nonzero-Y rejection with input-literal preservation. The new browser file was read in full: SVG plus HTML for five kinds, actual mark/text geometry,12px minimum, viewport containment, no browser/network/runtime errors and literal coordinates. These are actual assertions present in the commit, NOT this worker's executed results. No author13/270 or10browser passes are counted as our approval.

No concrete new material counterexample arose from this source trace, so NO tiny runtime proof was warranted or executed. This is not a zero-failure test run: tests/probes collected0, totals/skips N/A. Active09 owns separate finite review/testing; no duplicate matrix or polling. Original tests/oracles remain untouched.

This review does not certify arbitrary input, unrelated native histogram binning/pie behavior, later342/d017 density, browser font/layout under all labels, unchanged prior defects or renderer-wide release readiness. Preserving old behavior byte-for-byte is not evidence that every old behavior is correct. Source-only finite validation cannot replace real exact-final-head geometry/consumer/independent test and CI gates.

## Commands and honest execution record

1. FULL task/current instructions/ownnote read, native session_move SAMEID. Initial gitstatus/revparse/gitshow/difftree/OWNlsremote exit0. Only owned branch remote was read, no API/PR/CI poll.
2. Initial long prework shell was scanner-rejected invalid-structure BEFORE execution; simpler checkpoint write exit0. No source command/write occurred in the rejected request.
3. First raw extractor exit1 because OWNcollector guessed absent ROOTtsconfig.json (nested gitshow128). Read-only exact root/package tree diagnosis exit0 proved package-local tsconfig. Corrected only collector path list; corrected raw extractor exit0/12exact Gitblobs. No production/config edit, install, compiler or test fallback.
4. Source-only Python stdlib/Git byte-restoration/hash proof exit0:19numericchangedlines/threefunctionalpaths/allnon-svgHtmlbytesidentical/all12rawhashesexact. JSON proof is static evidence, NOT test pass counts or imported-source execution.
5. Exact commands/source identities and publication limits in evidenceR35-03/COMMANDS.md. All product imports/tests/browser/oldmatrix/npmwhole/scales/compiler/build/install/SDK/API/sharedGit/spawn/jobpoll counts ZERO.

## R04 bounded handoff

Verdict: accept this c3ee-versus5e finite-only SOURCE gate; no new must-fix in that delta found. Do not merge density342/d017 under this review, borrow prior cleanup approval, or call this a tester/final integrated acceptance. Require the actual independently tested assembled-head gates for the intended PR. No production grant or new issue requested.

Current action: review complete; prepare meaningful OWNreview/evidence/note commit, nonforcepush and exact remoteSHA readback. One executable next action: explicit owned-path/hash/source-and-old-oracle integrity preflight, own publication and prompt durable handoff to R04; no suite/probe/receipt replay or author polling.

Additional source contract read: FULL sealed package README and exact SVG geometry-contract grep exit0. Review assumes bounded prepared output up to100000records and existing32MiBcombinednormalizedpayload guard, not independent10Mbrowsermarks. README historical budget/benchmark claims are not fresh measurements. RESUME/STATE recovery redirects read later before publication (not asserted as prework reads). No change to bounded source-only verdict.

Local prepublication review precision correction: conservative range guard is not described as an exact overflow detector; same-sign/subnormal spacing reasoning unchanged. Original local bb60599 was not pushed. Amend only this report and its preflight hash before single nonforce publication, no source/probe/test rerun.
