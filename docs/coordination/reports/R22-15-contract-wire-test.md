# R22-15 numeric schema/wire interoperability — e44 preflight only

Owner `ses_de56780c8ffe7LgwvwdfR5qFQD`, genuine tester2 replacing queued09;
reviewers11+01/testers17+15. FULL MAIN R22 common+15/currentcanonical/AGENTS/
ownnote read, native SAME-ID confirmed, prework saved before source/tests.
Own branch `agents/r10-15-owned-input-cleanup`, parent55a9a3b. Production on
this evidence branch is **not** the source tested. No source ownership granted.

## Exact source and import proof

Created a new clean detached worktree at
**e44f667ed494fa272f97792ef99942a364ebca24**, exit0. Read actual model/schema/
existing tests/pyproject. All13tracked files byte-equal raw Git blobs before and
after testing. Model SHA25694824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170;
original test2f15dc277a6298780a6ab32076d642fe8491222cfc2c051fdbf33c0d18afe81b
and schemaf5f0316b592f78f5dc058fce123cd9a7c683d2259685f56524724af27880135a unchanged.

Old e44 has no package __init__; ordinary PYTHONPATH could import later MAIN.
Probe standard-imports only exact trusted models.py under a unique module name,
checks actual __file__/ChartSpec module, asserts no `deepviz` package imported.
No later dashboard model or moving7bc import. No TS source at this pin.
Actual `ChartSpec.model_json_schema()` and committed schema both valid Draft202012,
equal with canonical SHA25675972780be039e8dbbbf78a93d0611d9e6a5c9ed6e57a7ecf4239c2af20d6670.
Existing readonly Python3.12.16/Pydantic2.14.4/jsonschema4.26.0/referencing0.37.0/
pytest9.2.0; no installs or optional-validator skip.

## Independent wire oracle and actual execution

67literal wire cases with explicit approved expected outcomes/ranges/defaults,
not generated from production/schema. Check actual generated and committed schema
against wire instances, model_validate_json, canonical bounded integer defaults/
overrides, finite-JSON roundtrip.19accepted/48rejected. Strings/bools/nulls for
all5numeric fields; integral900.0/exponents, nonintegral floats, bounds/defaults,
large exponent overflow, unsafe extra fields, nested child numeric fields and
literal untrusted title. Distinct from17's direct Pydantic lane.

Plus1schema equality,3invalidJSON NaN/Infinity tokens (schema stage N/A because
no valid JSON instance),3mutation controls. Wrong positive oracle, permissive
additionalProperties and corrupt string-width schema must trigger assertion.
No production/schema/old-oracle mutations and no custom-dashboard equivalence claim.

Actual publication-version commands from evidence worktree:

```text
python -m pytest tests/r22_probes/role15/test_schema_wire.py -q --strict-markers -rs --tb=short -p no:cacheprovider -o junit_family=legacy --basetemp=artifacts/r22-15/pytest-preflight-published --junitxml=artifacts/r22-15/preflight-wire-published.xml
python -m ruff check tests/r22_probes/role15
python -m mypy tests/r22_probes/role15 --cache-dir artifacts/r22-15/mypy-cache
```

R22_SOURCE_ROOT exact detachede44/R22_EXPECTED_PINe44, ownrole15 PYTHONPATH;
PYTHONDONTWRITEBYTECODE1/PYTEST_DISABLE_PLUGIN_AUTOLOAD1. Existing projectvenv.
**74passed/0failed/0errors/0skipped2.93s**, exit0; Ruff0/mypy0(2sourcefiles).
Readonly postrun source/import/schema/XML67literaloutcomes/hash gate exit0.
Portable commands/requirements in NEW probe README; hashes/summary in R22-15 evidence.

## Corrections and limitations

Initial run74pass4.12s/Ruff0, mypy2own typing errors (Generator return/module-file
optionality) corrected only in own NEW probe. Initial metadata collector exit1
due own positive-case handcount22 vs actual19; preserved error capture, diagnostic
XML then corrected readonly collector0. Earlier53literal estimate corrected to
67, no rows/oracles/source changed. These are not product findings.

Raw logs/XML/generated schema/identity/output remain local untracked; compact
sanitized source identity and summary published. Own commit/push/remote SHA receipt
saved MAIN only after actual commands. No API calls, source/workflow/oldoracle edits,
installs/spawns, SUM/scale/old-test replay or shared branch/PR/issue mutations.
Rendering N/A: schema-only slice has no rendering implementation. No TS/package/
full-product build or greenCI claim.19wire rounds are not19issues or independent tests.

**No discrepancy in this scoped e44 preflight; NOT focused-PR approval.** Actual
first focused committed head is still pending supply. Mandatory next action:
R04 supplies actual head; SAME-ID tester verifies all relevant raw Git/import/
existing-test bytes and runs these unchanged controls afresh on a new clean
immutable source worktree before any final non-author tester signoff.
