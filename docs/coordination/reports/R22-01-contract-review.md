# R22-01 independent strict-numeric first-slice readiness review

**What this change does:** before Pydantic can coerce a numeric field, the model
rejects JSON strings and booleans. Existing integer bounds and mathematically
integral JSON floats remain valid. This is issue#30's narrow contract fix, not
an integration of the later visualization toolkit.

Reviewer:`ses_de5678335ffeI7xJrod5l25Q0Q`, non-author, second reviewer lane.
Proposal:**`e44f667ed494fa272f97792ef99942a364ebca24`**.
Parent:**`715c1f5ca0c13c276110c64d2af8c21deca881ea`**.
Default baseline:**`0ae2cf26426822135fc10d337fcacf580b7ed833`**, actual
`git ls-remote --heads origin refs/heads/main` readback matched this SHA.
Own branch:`agents/r10-01-correctness-regressions`, starting clean ac67f5f.

**This is readiness, NOT a final focused-PR review or approval.** No actual
focused-head SHA/PR/workflow was supplied. All final scoped bytes/context,
independent tester/reviewer reports and actual CI still require verification.

## Concrete prerequisite finding

### R22-01-CI1: two source paths alone do not reproduce the claimed lint gate

**Location:** default `pyproject.toml:35-42` and complete historical
`tests/test_models.py:2-7`. Parent/e44 configuration has the additional accurate
`[tool.ruff.lint.isort] known-first-party=["deepviz"]` stanza at lines41-42.

**Reproduction:** in an OWN ignored fixture containing exact main pyproject plus
unchanged e44 model and COMPLETE e44 test file, run `python -m ruff check .
--no-cache`. Actual exit1:**I001**, the imports in `tests/test_models.py:2-7`.
Default configuration does not classify the nested src-layout `deepviz` as a
first-party module; the original test's separated import group then fails.
`main-context-ruff.log` preserves the real diagnostic.

**Smallest remedy for R04:** include that one classification stanza, or the same
explicit classification in the focused CI command. I tested ONLY the explicit
`--config 'lint.isort.known-first-party = ["deepviz"]'` override on the SAME
unchanged model/test bytes: exit0. No lint rules were disabled, source modified
or original oracle edited. Do not copy the whole later pyproject, particularly
a resource force-include for a schema file that main does not contain.

This is a **focused-main integration prerequisite**, not a new numeric-runtime
regression in e44. If the future focused branch already addresses it, verify its
actual config/command before disposition; do not pretend that head is known now.

## Connected source review

- The exact parent→e44 diff is11 model lines and13 test lines, two paths. Parent's
  model is byte-identical to main; main's seven-file tree has NO tests directory,
  generated schema, workflow, toolkit modules or package initializer. A blind
  cherry-pick of the13-line test hunk is incomplete on main.
- `models.py:38-47` checks exactly version/max_points/width/height/columns before
  coercion. `bool` is explicitly excluded before Python's int-subclass relation
  can admit it. Existing field handling rejects fractional/out-of-range numbers;
  replacing it with indiscriminate StrictInt/strict=True would incorrectly reject
  allowed JSON900.0. The validator returns the original data without mutation.
- Field/default definitions at lines19-36 and dashboard rules at49-57 are
  unchanged. The new logic is a fixed five-field loop per parsed model, not an
  unbounded collection, renderer, filesystem or remote-ingestion interface.
- Extra schema keys remain forbidden, including inside children. Literal labels
  and numeric-looking field names remain ordinary allowed strings. Rejecting or
  HTML-escaping every label here would invent a different contract; downstream
  rendering still needs its own escaping. No eval/callback/code options are added.
- Generated schema, including numeric integer grammar, bounds and forbidden
  extras, is unchanged. Actual independently regenerated parent/e44 sorted UTF-8
  LF bytes both match the historical schema Git blob exactly:
  `f5f0316b592f78f5dc058fce123cd9a7c683d2259685f56524724af27880135a`.
  Runtime defaults are also exactly equal. This fixes runtime acceptance to meet
  the existing numeric schema, not a schema expansion or TypeScript/API change.

No additional numeric-runtime correctness defect was found in the inspected
proposal. This statement is NOT final focused-head approval.

## Complete minimal PR and scoped CI prerequisites

1. Start from fresh default main, preserve its history. Apply only the11-line
   model validator and add the **complete67-line e44 `tests/test_models.py`**,
   not just its13 new lines. The complete module defines30 cases:15 existing
   invalid values,5 forbidden keys, defaults/dashboard/metadata,6 numeric-type
   negatives and1 integral-float positive. I read it; reviewer11 owns its actual
   unchanged30-test run. I do not borrow or invent that result.
2. Handle CI1's first-party import classification. No normalizer, renderer,
   tools, npm, later3K tests or current failing product workflow is needed.
3. A new honest job can be named **contract/schema validation**, with exact
   scoped commands and read-only contents permissions. Use Python>=3.11 and
   minimal Pydantic2/pytest/Ruff/mypy dependencies; jsonschema is needed for the
   generated-schema agreement check. Do not label this full product verification.
4. On the exact focused head: run its complete contract30 tests, strict own
   independent negative/positive controls, unchanged bounds/defaults/schema
   generation, Ruff and root `python -m mypy`. Existing main mypy config checks
   **one implementation file**, not all tests or a package distribution. Verify
   imported module path+commit hash, not only a green test count.
5. Main contains no static schema resource. It can be regenerated from this model;
   these own generated bytes provide output evidence. If the focused PR ships a
   static schema, verify the ACTUAL added file and any packaging changes too.
   Do not add a missing-file force-include or claim installed resources/CLI/tools
   work: main already names later CLI entry points whose modules do not exist.
6. Schema/model output is the applicable real output for this source-only slice;
   no chart-rendering code exists in it. No screenshot/browser/renderer acceptance
   is claimed. R04 must record the scoped output rationale and obtain all four
   genuine reports plus actual green required focused CI before merge/closure.

## Independent NEW execution, not a replay of other lanes

Original30 tests lack negative `model_validate_json` children and generated-schema
agreement coverage. I added ONLY seven bounded NEW controls for that uncovered
invariant; no original test or production file was changed:

| Exact source/check | Actual independent result |
|---|---|
| parent715 NEW nested JSON/schema probes | exit1, **3failed/4passed/0errors/0skips**,0.38s |
| proposal e44 SAME NEW probes | exit0, **7passed/0failed/0skips**,0.26s |
| exact main-context root Ruff | exit1,I001 (CI1 prerequisite above) |
| SAME context with accurate first-party-only CLI override, plus NEW probe | exit0 |
| exact main-context root mypy | exit0,1 source file |
| parent/e44 actual generated schema and default comparison | exit0,exact canonical bytes/defaults equal |

Three genuine baseline failures are nested `width:"900"`, `columns:true`,
`version:true`: generated schema rejects them while the old runtime accepts
all three. E44 rejects all three through the real JSON parser. Positive controls
preserve integral numeric children/defaults, nested forbidden executable keys,
and allowed literal labels/field names. Thus the RED→GREEN is an actual source
change, not a weakened oracle or synthetic payload mutation.

NEW probe:`tests/r22_probes/role01/test_nested_numeric_contract.py`.
Executed bytes SHA256:`54a9bbdfb773d7c81e0179483f763d06bf2dd76949abdd867f7004f75c29db0f`.
Proposal model SHA256:`94824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170`.
Parent/main model SHA256:`9705c4e7809ea03405ef2180f976869fc5f13e0fc63a45190929bd0c4241b461`.

### Import-harness correction, explicitly preserved

A normal PYTHONPATH-only import initially resolved the **later MAIN model**,
not historical e44: the installed editable regular package overrides the old
namespace package. No contract tests ran under that wrong source, and no result
was accepted. `import-harness-diagnostics.json` records the actual observation.

For both real test executions I used Python **-S**, process-local PYTHONPATH
containing ONLY the selected snapshot source and explicit existing dependency
site-packages, with unrelated pytest plugins disabled. Module path and SHA were
asserted against the Git blob BEFORE assertions. No package initializer,
shared environment, dependency, source, original oracle or configuration was
edited. This source-isolation requirement also matters when retesting the focused
head in an already editable-installed developer environment.

Environment:Python3.12.16/Pydantic2.14.4/pytest9.2.0/jsonschema4.26.0/
Ruff0.17.6/mypy2.4.1. No installs were run. Exact argv/cwd/exits/import paths,
source hashes, JUnit and raw logs are under `docs/coordination/evidence/R22-01/`.
`index.json` distinguishes measured raw-byte hashes from published Git-blob
hashes, including native CRLF→LF normalization in the parent failure JUnit file.
Current issue#30 was read through public API; its open acceptance criteria allow
integral numeric floats and require original bounds/defaults/lint/type checks.
No issue/PR/API write was performed by this reviewer.

## Limits / next executable action

**Not checked:** future actual focused head/workflow/PR/remote CI/merge,
original30 execution (reviewer11 lane), testers17+09 results, distribution builds,
Python3.11/other Pydantic versions, TypeScript/renderers/browser/whole-toolkit
security/scale/RSS. No SUM/npm fixture replay, source/workflow/oracle/shared Git
mutation or spawning. R13 SUM F1 remains OPEN P2; this review does not waive it.
No human approval, four-report gate,900-issue completion or full-green claim.

**R04 next:** include the complete original tests and accurate import-classification
prerequisite, publish the real focused head, then notify this SAME reviewer session
with its immutable SHA/PR. I must verify ALL actual scoped paths/context and the
relevant strict controls before a final focused-head review. Do not wait for all
unrelated workers or substitute readiness for that review.