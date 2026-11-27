# R50-10 — selected-record contract code proposal (unapplied)

## Scope and admission

Owner: `ses_de56782e3ffeI5D4lzsNVeLcDk`, SAME-ID continuation, actual parent
`ses_de58eb849ffeOMwi2kb0VSqy3B`. Admission is recorded in
`docs/coordination/evidence/R42-root/r50-04-10-admission.json`: role10 was
inactive before this call; 12 active before, 14 upper bound after two admissions;
no source or GitHub writes in the admission proof.

Main-bound target: **Python data foundation PR2**, with the sealed `546c25ea…`
normalizer dependency consumed later by role07/08. Blocker addressed by this
handoff: one cross-language record-vs-protocol contract question. Next owner:
**R04** decides A/B/C below and, only after that decision, grants a narrow
implementation patch and affected retest to the appropriate producer. PR/merge/
CI/default-main status remains UNKNOWN from this role.

## Inputs read before analysis

- Live root `status.md`, live central `docs/coordination/status/role10.md`,
  `AGENTS.md`, `RESUME.md`, `docs/coordination/STATE.md`, `docs/PROJECT_STATE.md`.
- Full R50 row/common: `docs/coordination/tasks/R50-eight-next-data-repair-gates-and-code.md`.
- Full R41 report: `docs/coordination/reports/R41-10-normalizer546-test.md`.
- R41 evidence and exact module boundaries at product pin `546c25ea…`.
- Canonical API/design docs: `docs/architecture.md`, `docs/capabilities.md`,
  `docs/superpowers/specs/2026-11-26-deepviz-design.md`.

## Preserved actual R41 outcome (not replayed)

- 460 unchanged controls independently passed: Python226 + Node234.
- Two separate homogeneous ownership positives passed.
- New diagnostic cohorts remain Python13PASS/12FAIL and Node15PASS/8FAIL.
- The 14 warning-assumption failures remain diagnostic-harness assumptions,
  not product bugs; the 2 Python AUTO-pages cases remain a disclosed policy
  ambiguity; the 4 selected-record failures are one family; the 4 field-policy
  tests remain RED. None were edited, waived, replayed, or relabeled.
- Exact F1 object and JSON cases produced Python `Ambiguous GraphQL connection
  fields; select rows with data_path` and TypeScript `Column arrays must have
  equal length`. These are preserved observations from R41 evidence, not fresh
  executions in R50.

## Contract analysis

The exact F1 expected output is supported by the current record semantics:
`data_path: outer` selects a list of ordinary records; each row boundary must be
retained; nested arrays flatten to dotted field names; no Cartesian join occurs.
The Python normalizer docstring explicitly says record collections retain nested
arrays and column inference applies to top-level mappings. The architecture also
separates records/column arrays and requires explicit paths for nested JSON.

However, the public docs do not define precedence for a selected ordinary row
whose field is named `nodes` or `edges`, nor whether a null item in an explicitly
selected non-GraphQL collection is a null GraphQL node or an ordinary scalar row.
The exact four F1 cases therefore justify one narrow contract decision, but not a
blind one-line source change.

## Decision matrix and proposed bounded literals

See `docs/coordination/evidence/R50-10/decision-matrix.md` and
`tests/r50_probes/role10/selected_record_contract_cases.json`.

The first two literals are the unchanged R41 F1 object/JSON inputs with expected
records. Two new bounded literals distinguish nested object cells and the
`nodes`/`edges`/`items` sibling-name precedence. Existing partial-data and
error-only controls are listed as immutable controls and are not replayed.

## Conditional implementation shape (NOT applied)

If R04 chooses **A — record-first explicit selection**, the minimal safe shape is
an internal selection-provenance mode shared by Python and TypeScript:

1. Mark whether `data_path` selected an exact GraphQL connection/member boundary
   or an ordinary collection. Do not infer this from a nested row's field names.
2. Flatten ordinary selected rows directly, retaining nested arrays as dotted
   fields. Do not route them through GraphQL connection or top-level column
   inference.
3. Keep exact connection extraction, edge unwrapping, null counts, partial-data
   warnings, and error-only rejection unchanged. Edge unwrapping occurs only at
   a proven edge boundary.
4. Add only the four affected bounded independent retests after implementation;
   do not rerun the R41 matrix or change any original oracle.

A blind `record=True`/`record=true` toggle at the current Python `_records` or
TypeScript `selected` call site is explicitly **not** proposed: it risks changing
`data.users`, `.nodes`, `.edges`, null-node counts, and nested protocol-shaped
records. The patch requires R04’s boundary decision first.

## Limits and exact next action

No source/oracle/schema/config/default/API/install/CI/browser/scale/security
behavior was changed or replayed. No paid provider or optional dependency claim.
No symlink privilege result is implied. No implementation authority is claimed.
Estimate for this proposal is **UNKNOWN** until R04 selects a contract option;
the role10 analysis/handoff itself is complete. R04’s next executable action is
to choose A/B/C, record the decision, and route any authorized minimal source
patch plus exact affected retest. Overall R41/R50 selected acceptance remains
**RED**, with all four policy REDs preserved.
