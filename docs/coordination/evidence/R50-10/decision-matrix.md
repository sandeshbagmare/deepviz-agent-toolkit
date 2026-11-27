# R50-10 selected-record contract matrix

Product source under review: `546c25ea75ee9d8a41b3832aa639664bc9a683b5`.
This is a **proposal/decision artifact only**. It does not modify Python,
TypeScript, schema, original tests, or the R41 oracle set.

## Contract evidence read

- `docs/architecture.md`: records/column arrays are distinct inputs; nested JSON
  requires a unique array path; GraphQL extracts `nodes` or `edges[].node` and
  preserves null-node counts.
- `python/deepviz/src/deepviz/normalize.py` docstring: record collections retain
  nested arrays as fields; column inference applies to top-level mappings.
- `docs/capabilities.md`: `data_path` is an explicit field mapping and evidence
  still required includes ambiguity/collision behavior and stable nesting.
- `docs/superpowers/specs/2026-11-26-deepviz-design.md`: bounded flattened
  records, explicit mappings, and no silent semantic conversion.

These sources make the expected output for the exact F1 ordinary-row fixture
clear. They do **not** define precedence when an ordinary selected row contains
fields named `nodes`/`edges`, or how nulls inside an explicitly selected array
should be classified when that array is not proven to be a GraphQL connection.
That remaining precedence is one R04 contract decision, not four defects.

## Matrix

| Selected value / path | Intended interpretation | Python 546 | TypeScript 546 | Proposal disposition |
|---|---|---|---|---|
| `outer` → list of ordinary rows; each row has `nodes` and `items` arrays | Two ordinary records; flatten nested arrays (`nodes.0`, `items.0`) | Rejects as ambiguous GraphQL fields | Rejects as unequal columns | **F1 contract gap**. Explicit ordinary record selection must not reinterpret row fields as protocol/columns. |
| Same F1 value encoded as JSON | Same as above after decode | Same rejection | Same rejection | Four unchanged R41 failures are one cross-language family, not four bugs. |
| `data.users` → exact GraphQL connection object | Use existing `nodes`/`edges` protocol extraction | Existing behavior | Existing behavior | Preserve; no patch may weaken this. |
| `data.users.nodes` → selected GraphQL member collection | Node members are records; preserve order/null count and partial-error warning | Existing controls remain source of truth | Existing controls remain source of truth | Any patch must carry GraphQL selection provenance rather than infer from nested row field names. |
| `data.users.edges` → selected edge collection | Unwrap each `edges[].node`, then flatten node record | Existing behavior | Existing behavior | Preserve edge-only unwrapping; do not generalize to every row with an `edges` field. |
| Ordinary selected row with exact protocol-looking sibling fields (`nodes`, `edges`, `items`) | **Underspecified**: record-first and reserved-protocol-first are both plausible | Can raise GraphQL ambiguity | Can raise column raggedness | R04 must choose precedence or add an explicit mode/escape; do not silently choose in this proposal. |
| Top-level / path-selected GraphQL error-only response | Reject before producing records | Existing rejection | Existing rejection | **Immutable security invariant**. |
| Top-level partial data plus GraphQL errors | Keep usable rows and one warning | Existing warning | Existing warning | **Immutable public behavior**. |

## Conditional minimal repair shape (unapplied)

If R04 confirms the record-first row semantics for explicit ordinary paths, the
smallest safe implementation is an internal **selection-provenance mode**, not
a field-name exception:

1. Python `_select_path`/`_records` and TypeScript `pathValues`/`selected` mark
   whether the selected root is an exact GraphQL connection/member boundary or
   an ordinary record collection.
2. Ordinary selected collections pass each selected row directly to existing
   flattening with protocol/column inference disabled for that row. Nested
   arrays remain dotted fields and never form a Cartesian product.
3. Exact GraphQL connection roots retain current connection/error/null handling.
   Edge wrappers unwrap only at the recognized edge boundary; selected node
   records then flatten nested fields as records.
4. The error-only and partial-data checks execute before/alongside selection as
   they do now. No new schema field, cap, warning waiver, or parser relaxation.

A blind `record=True` toggle at the current `_expand`/`unpack` call site is **not
   approved**: it would risk changing `data.users`, `.nodes`, `.edges`, null-node
   counting, or nested protocol-shaped records. R04 must decide the provenance
   boundary before a producer receives implementation authority.

## Exact bounded literals

`tests/r50_probes/role10/selected_record_contract_cases.json` contains six
bounded cases. The first two are the unchanged R41 F1 object/JSON inputs and
expected records. The next two are new ordinary-record discriminators. The last
two are preserved GraphQL partial/error-only controls and are explicitly marked
not to replay here. `verify_fixture.py` checks fixture integrity only; its pass
is not a product test.

## Decision requested from R04

Choose one, explicitly:

- **A — record-first explicit selection (recommended by the current record
  docstring):** exact ordinary selected rows preserve `nodes`/`edges` as fields;
  GraphQL behavior is retained only at proven connection boundaries. Grant a
  narrow implementation patch plus four affected independent retests.
- **B — reserved protocol names:** rows containing `nodes`/`edges` remain
  protocol candidates even after explicit selection. Keep both R41 failures as
  expected validation and document a field-escaping/renaming rule; this does
  not satisfy the record-first reading.
- **C — reject ambiguity identically:** both languages reject the F1 shape with
  one shared error. This is safest without a contract expansion but preserves
  the usability gap and requires updated public documentation, not a silent
  source fix.

Until R04 selects A/B/C, no source proposal is implementation-ready and the
R41 acceptance remains RED.
