# R44-01 independent dashboard-schema SOURCE2 review

What this change does: add declarative JSON Schema composition constraints matching the existing ChartSpec dashboard validator. It adds no runtime validator, accepted kind, execution hook or rendering path.

Reviewed source **dd1c4080095c7e739582dc5c631bc419047c48d2**, parent actual-main **31cff73ab057c3fed69bd400ac005f2f11609027**.
Non-author reviewer ses_de5678335ffeI7xJrod5l25Q0Q; distinct from04 source and14/20 acceptance lanes.

## Verdict

**No new must-fix in this narrow schema change. Independent SOURCE2 gate clear on exactdd1.** This is not author118/tester approval, runtime acceptance, CI, publication/PR verification, main merge or full-toolkit clearance.

ALL4 changed paths read: models.py14-line diff/full93-line module; canonical47-line addition/full237-line schema; new191-line portable oracle; new48-line pytest consumer. Original82 test definitions/current workflow/pyproject also read. Actual tree has only a models namespace, not renderer/CLI consumers; no review of absent production code is invented.

## Independent identity/equivalence checks

- ALL17 current tree files materialized directly from immutable Git blobs and raw-byte compared. Model SHA256 **be2cb15f6f91f2de4b9ebd4e283ea677e9e39490932db3ecd9934f2d6c1e4a1f**; schema **35b5a2786db65051ff8f0289901424d74a7b2a9df87fc6c59342ced5834cd18d**.
- Removing ONLY model_config assignment: ENTIRE module AST AND raw surrounding bytes equal31cff. Imports, Mapping guard, numeric fields/defaults/bounds, dashboard validator, dataclasses and to_dict are unchanged. Removing ONLY json_schema_extra leaves the original extra-forbid ConfigDict AST unchanged.
- Entire new config value AST equals **728bbac47b747501ad27f40525220317ea218064**. No whole728 model was copied into the reviewed tree; main's Mapping import/guard remain intact.
- Canonical ChartSpec definition's four added metadata keys equal the model's literal metadata exactly. Removing only if/then/else/allOf restores the ENTIRE parent schema JSON, not just selected properties. Root reference, recursive child reference, types, cardinalities, extra-forbid and numeric constraints all remain intact.
- Original test_models.py/test_numeric_schema.py/test_native_mapping.py are byte-identical to31cff; no old oracle weakening. Entire new portable oracle equals published155e42786ecfcdd8e04aed215c0751cd20ec3331 original bytes, SHA935c768e6e9bba81f425d11ba709c5bafbeffaec60a92c87e32fb746708501ea.

## Composition and compatibility reasoning

- models.py:23 and schema:33-42 require kind inside the condition. Missing kind therefore follows the non-dashboard branch, matching runtime's default bar; it is not accidentally treated as dashboard by vacuous properties validation.
- models.py:24/schema:222-231 require charts and at least one child for dashboard. Missing and empty charts both reject. Existing field max24 stays in force.
- models.py:25/schema:26-32 permit only empty/absent charts for non-dashboard, including default-kind objects. Explicit empty charts remains valid; default/non-dashboard with nonempty children rejects.
- models.py:26-30/schema:5-24 reject children explicitly marked dashboard, including structurally valid nested dashboards. The required-kind inside not is essential: a child with omitted kind remains a valid default bar. Existing recursive reference and child constraints still apply.
- Malformed/non-object/null/array child values, malformed charts fields and deeper default-kind nesting remain rejected by the unchanged object/array/ref constraints plus the new composition metadata. No schemas replace or bypass existing field validation.
- Integral JSON numbers remain permitted by unchanged integer schemas/runtime validation. Numeric strings/booleans, root/child extra fields and unsupported kinds remain prohibited. Native UserDict/MappingProxy behavior and nonmutation are unchanged by exact preservation of runtime code; this is a source argument, not a new runtime pass claim.

## Tests and callers inspected, not counted as our passes

Portable oracle tests/dashboard_schema_oracle.py:18-36 contains17 literal RAW JSON decisions,5accept/12reject. It never derives expected answers from schema, model output or expanded defaults. Its two guard checks plus two checks per payload define36 CLI tests; the new pytest file independently consumes the SAME17 payloads for34 semantics plus2 guards. These commands do not represent72 distinct payloads or independent fixtures. Source/import isolation and export-equality checks were inspected in full.

Original82 preserved tests: models.py test consumer66lines, numeric_schema59lines, native_mapping45lines. The mapping tests keep valid UserDict/MappingProxy defaults/integral values, rejection of strings/booleans and nested handling. The existing numeric suite keeps actual export equality and original integer bounds. No source test expectation was edited for this review.

Current callers are these tests and the portable harness, plus read-only-contents focused workflow:34lines and unchanged pyproject:42lines. CI runs the actual shipped tests without filters on PRs to main/main pushes; fix/r42 branch-push CI is not promised by its older branch allowlist. Package/renderer/native execution is not implied by model-only CI. Public consumer/source-integration packages are separate upcoming gates.

## Actual execution and limitations

**Product imports/calls:0. Pytest/portable-oracle tests run:0. New probes:0.** Stdlib Git/hash/AST/literal-JSON comparison checks exited0. No concrete new source gap justified a strict counterexample or duplicate14/20 runtime matrix. Author118 results and04 review are NOT borrowed. Generated-schema freshness/runtime outcomes belong to the actual new-head acceptance gates, not this static comparison.

Initial snapshot helper assumed an initializer absent in BOTH parent/new namespace trees and failed1 before any product execution. Its corrected proof helper initially had an escaped-newline SyntaxError1 before execution. Two combined-write requests were scanner-rejected before execution; bounded helpers/status/report writes succeeded. All are recorded as reviewer harness/tool failures, not product RED or passing tests; no source/schema/config/oracle/dependency changes were made.

At assignment remote publication was reported absent. This reviewer did not poll publication, PRs, CI or main; current product remote/PR/CI/merge are UNVERIFIED here. No installs/env/API/shared/default writes or spawning. Only own report/evidence/note/role01 central status and own review branch changed.

## Handoff

R04 can consume this exactdd1 SOURCE2 clearance with genuine04 source review,14/20 acceptance and actual exact-head CI for prompt usable schema merge. Notify07/08 of the published model/canonical pair when real publication is proven; do not copy728 whole model or assume integration approval on another head.

Prior c1b report remains Python-mean SOURCE-only. Known11 mean finding and546/data/native/visual blockers remain separate; this gate is NOT full data/toolkit clearance or a replacement for actual-main QA.