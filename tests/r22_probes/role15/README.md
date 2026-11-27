# R22-15 schema/wire interoperability

Independent tester2 for the first #30 strict-numeric-contract slice, distinct
from tester17's direct Pydantic lane. This publication is **e44 preflight only**;
it is not focused-PR or final-head approval.

Use a new clean detached worktree at the approved source commit and existing
Python/Pydantic/pytest/jsonschema dependencies read-only. No installs required.
The old e44 tree has no `deepviz/__init__.py`; plain PYTHONPATH can silently import
the later MAIN package. The probe instead standard-imports only the trusted,
raw-Git-verified models.py under a unique module name and asserts no `deepviz`
package was imported. No schema-authored Python or executable schema features.

```powershell
$env:R22_SOURCE_ROOT = '<absolute clean detached source worktree>'
$env:R22_EXPECTED_PIN = 'e44f667ed494fa272f97792ef99942a364ebca24'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:PYTHONPATH = (Join-Path $PWD 'tests/r22_probes/role15')
python -m pytest tests/r22_probes/role15/test_schema_wire.py -q --strict-markers -rs -p no:cacheprovider -o junit_family=legacy --basetemp=<fresh-own-directory> --junitxml=<fresh-own-output.xml>
```

Actual e44 result: **74pass/0failure/0error/0skip2.93s**, Ruff/mypy0.67literal
wires:19accepted/48rejected, plus schema equality,3invalidJSON tokens and3negative
schema/oracle controls. Pydantic2.14.4/jsonschema4.26.0/Draft202012 installed.

The approved numeric ranges/defaults and expected booleans are explicit literals
in wire_cases.py, not extracted from the model/schema. Each JSON wire is checked
against actual same-model generated schema, committed schema if present, and
model_validate_json. Accepted values must canonicalize to literal bounded integer
defaults/overrides and pass roundtrip validation. Includes strings/bools/nulls,
integral900.0/nonintegral floats/exponents/boundaries/extra executable keys and
nested valid-chart numeric fields. Nonstandard NaN/Infinity tokens are rejected
before a JSON Schema instance exists: that schema stage is N/A, not a pass.

Three deliberate mutations (wrong positive oracle, permissive extra properties,
string numeric type) must be caught. They do not modify production or old oracles.
No full dashboard structural-equivalence claim: custom after-validator rules are
outside this focused numeric slice. Render output N/A: no renderer in this slice.
No TS source at e44, no later dashboard model, SUM/scale/old-test replay, APIs,
installs, spawns or product edits.

For actual focused-PR signoff, provide the real committed head and a new clean
source worktree, change only R22_EXPECTED_PIN/source environment, and execute
these same unchanged probes afresh with full Git-byte/import/test-hash evidence.
Reports/evidence: `docs/coordination/{reports/R22-15-contract-wire-test.md,evidence/R22-15/}`.
