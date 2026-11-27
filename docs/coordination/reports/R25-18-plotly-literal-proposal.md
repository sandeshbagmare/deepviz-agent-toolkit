# Plotly literal-text implementation proposal (R25 role18)

## Final proposal checkpoint; R27 production transition approved separately

Three NEW guarded controls actual **3failed/0passed/0errors/0skipped0.97s/exit1**, exact own7bc source proven in same process. Own Ruff0/mypy0; patch `git apply --check`0, production/existingtests/schema diff0. Compact results/source/test/XML/log/patch hashes in `evidence/R25-18/results.json`; exact unapplied function-only diff alongside. This is genuineRED, not a fixed candidate. No old browser9case/20matrix/core/full-suite/build/scale replay. One earlier mypy1str-kind inference corrected using typed NEWcases, no existing test changes.

After this command completed, FULL MAIN **R27 manager release25lines** and **R29 latest priority48lines** read. Actual R04 now grants eligible18 exact `_plotly`+optional adjacent pure `_plotly_literal`, **NO imports/other functions**,2NEWtestpaths, exact7bc/newfixbranch; no wrapper/oldtests grant. This supersedes earlier pending/proposal-only statuses for the NEXT separate production branch, not retroactively this proposal. Ruling: finish this one meaningful proposal publication, then save R27 prework and TDD on mandated NEW `fix/r27-plotly-literal-text`; preserve this immutableRED/evidence and manager's unique release plan. Old quote-entity oracle conflict remains disclosed, cannot edit under grant.

> For the authorized implementer: use executing-plans/TDD inline after a saved R04 source grant. This document and its patch are proposals, not authorization or an implemented repair.

**Goal:** make Plotly display untrusted strings literally without activating data-authored HTML, corrupting quotes/entities, or changing numeric/time values, record metadata or other engines.
**Architecture:** one local string-only display helper inside `_plotly`; reuse the existing `html.escape` import with `quote=False`. Map only Plotly display values through it; leave normalized records, schemas, JSON script serialization, outer HTML escaping and all other engine functions untouched. Dashboards use the same per-child `_plotly` mapping, so no dashboard wrapper change is proposed.
**Tech:** Python/Pydantic, existing Plotly runtime; standard-library escaping, no dependency changes.
**Spec/authority:** FULL MAIN R25 common+18/R26; QA20 R03/R10/R13/R22 findings and unchanged permanent probes. **Production grant still pending.**

## Owner, source and allowed paths

- Owner actual SAME-ID `ses_de567805bffdER1GlVd0ngLgKg`, native session_move confirmed after creation of this NEW isolated worktree.
- OWN branch `agents/r25-18-plotly-literal-proposal`, base exact **7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6**. `git worktree add -b ...7bc` exit0, initial HEAD7bc; prior R14/e47 branch untouched.
- Allowed NEW own report/evidence `R25-18/`, actual-ID note, up to3 genuinely uncovered strict controls in `tests/r25_probes/role18/`; no production/existing oracle changes. No API/issues/PR/config/install/spawn, no old9casebrowser/20matrix/fullbuild/fulltest/scale replay.
- Prework report and MAIN note saved before substantive work. Current action is source/sink/probe analysis and concrete unapplied patch; no tests or product edits executed yet.

## Source grant requested NOW (R04 decision required)

Release **only `python/deepviz/src/deepviz/engines.py::_plotly`**, including a nested literal-display helper inside that function. **No new import needed:** existing `from html import escape` suffices. No module-level helper/import/channels/browser_html/native_spec/_antv/render.py/schema/normalizer change is requested. Release ONE NEW test file `python/deepviz/tests/test_r25_plotly_literal_text.py` when implementation is approved, with optional NEW producer-owned browser regression helper only if R04 includes it explicitly. Existing QA20 files remain read-only and independent20+02 must later retest the frozen fix.

This avoids overlap with07`channels`,08`_antv`,12TypeScript and16normalizer owners. The parent/root request is a dispatch notification, not R04's grant. Until an explicit saved function/helper/test grant is read, **no production edits anywhere**. No dashboard wrapper grant needed: exact `native_spec`727 calls `_plotly` for each child and browser_html loops payloads with unchanged safe_json/outer escaping.

## Findings read in full; no replay or exploit inflation

- FULL QA20 R03 report51lines: native category anchors1/chart2/dashboard; no JS execution/click. R10 report41lines and complete2permanentprobe files: strict2RED/4numeric-timePASS, complete literal strings required and original manifest/table preserved.
- FULL R13 report86lines and complete2sinkprobe files: isolated legend anchor, geo hover anchor only after pointer movement, native title visible `&quot;`;3RED,0console. Existing9case acceptance recipe is independent followup, **not rerun here**.
- FULL R22 report57lines: actual bug **#36**, `https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/36`, QA20's sole authorized creation201/readback200. This is reported file evidence, not a fresh API observation by this agent. No further mutation authority here.
- Exact7bc `_plotly`385–444: raw trace.name/x; raw shape labels/box/violin x/heatmap x+y/radar theta/geo.text; title/axis/table use default quote=True. Outer browser_html737–803 correctly escapes headings/attributes/table and safe_json escapes script-sensitive characters. Those contexts must NOT adopt text-only quote=False indiscriminately.

## Review focus and smallest implementation plan

1. Entity-looking source strings (`&lt;`, `&amp;`) remain distinct from angle-bracket strings; encode once at native display mapping, never mutate source records.
2. Numbers (including numeric category values) retain Python/native types; numeric-looking strings and ISO date strings are not coerced or formatted.
3. Less-common literal sinks (heatmap both axes, hierarchy/pie/funnel labels, radar theta, box/violin categories) must not remain raw after a bar-only repair.
4. Quote/ampersand exactness applies to native titles/axis fields/table headers/cells; retain separate HTML-attribute/script safety in browser wrapper.
5. Chart and dashboard use identical display semantics; hover/legend need actual independent browser checks and no inferred GREEN from unit encoding.

- [ ] Save/read exact R04 grant before product edits, verify current source and unaffected owners; new branch if manager specifies another source base.
- [ ] NEW3uncovered unit controls only: entity-like label distinction with numeric/time/record invariants; non-cartesian/heatmap label sinks; title/axis/table quote/entity exactness. Run genuine RED against this immutable7bc and retain IDs/output (no old matrix replay).
- [ ] After approval, implement local `_plotly` helper `literal(value: Any) -> Any`: `escape(value, quote=False)` for strings, original object otherwise. Apply to display-string lists/name/text/table/title/axis only; retain original numeric transforms per kind. No global record sanitization or arbitrary callbacks.
- [ ] Run the NEW controls and scoped existing Python Plotly unit tests on committed source. Run own lint/type check; independently20+02 run unchanged nine real-browser cases/fresh outputs, assert full literal text/0anchors/handlers/console and numeric/time/geo geometry.
- [ ] Publish a meaningful scoped source+NEWtests commit/non-force own push/remote SHA after grant. R04 owns dependency-complete PR/two-reviewer/two-tester/CI/merge/closure. Proposal-only publication is not source approval or bug36 closure.

## Current action / blocker / next command

Source-grant request is saved MAIN and here; no production edits. Next: produce an exact-context unapplied patch under own evidence, write only genuinely uncovered unit controls if useful, run those3once, record real RED/positive results and immutable module/Git hashes. Publish one meaningful proposal commit with exact remote readback; no endless receipt-only commits. If grant arrives, checkpoint it before TDD; do not poll for one.

## Genuine NEW RED; connected compatibility issue found

`P -m pytest tests/r25_probes/role18/test_plotly_literal_boundaries.py -q --tb=short --junitxml A/new-boundaries-red.xml` **exit1/3failed0passed0skipped0.68s**. All failures are expected native-boundary behavior, no errors: raw entity-like categories;9unencoded noncartesian/heatmap display channels;5quote-corrupted title/field/table sinks. Numeric/time values/types, original rows and native numeric geometry positives executed before each final strict assertion and passed. New test names in XML/log, no old probes or browser run. Separate preflight imported engines/models at exact own7bc and compared Git blobs; engines SHA256`a5c39893b011623ea0813b448a988e59f767412d96d4af9b2c07b86b38cae225`, models`890ecb0e29e1345364b2bf4840bdea7a542067003caf54d7b0855536ee2b6a76`. Same-process fixture guard will be added to NEWtests before final scoped verification; no result silently upgraded.

**Compatibility disposition needed, no old oracle edit:** existing `python/deepviz/tests/test_backend_plotly.py:192–205` explicitly asserts quote-entity strings in native table cells. A correct native literal-text quote=False repair necessarily changes that representation, so this unchanged test is expected to conflict. Do not weaken/delete it secretly or claim existing suite GREEN. R04 must authorize a narrowly explained expectation correction only after browser-native full quote/text proof, or split/defer table-quote repair with the limitation visible. Proposed grant currently excludes existing tests. Independent20+02 must confirm actual Plotly decoder behavior, not approve from these encoding-level controls alone.

Dependency note: default main currently ships only the model foundation in the saved packet; a2filePlotlyfix is not independently usable on that default without the renderer prerequisites. R04 owns dependency-complete PR sequencing/stacking; this proposal does not authorize unrelated renderer/package/workflow/schema publication.

Scoped verification checkpoint: unappliedpatch `git apply --check`0, source/existingtests/schema `git diff --exit-code`0. Own Ruff0; own mypy1 because tuple loop inferred unrestricted str for ChartSpec.kind. Added explicit NEW test-case tuple annotation using existing `ChartKind`, no cast/ignore or schema/source change; pytest guarded rerun had NOT started because shell stopped on mypy. Next rerun scopedlint/types then only3guardedcontrols. Failedtypecheck retained, no inventedGREEN.
