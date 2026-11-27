# R22-01 novel nested-JSON / schema guards

Historical proposal: e44f667ed494fa272f97792ef99942a364ebca24.
Parent:715c1f5ca0c13c276110c64d2af8c21deca881ea.
These seven NEW checks are not the original30 root-value tests (reviewer11's lane).
They cover three previously untested nested JSON coercion counterexamples,
integral numeric children, unchanged schema generation, nested forbidden extras,
and preservation of allowed literal labels/field names.

Use a clean environment or Python `-S` plus process-local `PYTHONPATH` entries for
ONLY the selected snapshot's `python/deepviz/src` and existing dependency
site-packages. The historical model is a namespace package: an installed later
editable regular `deepviz` package otherwise wins even over PYTHONPATH. The probe
fails before tests if imported model path or Git-sourced expected SHA is wrong.

Set `R22_EXPECTED_MODEL`, `R22_EXPECTED_MODEL_SHA256` (from the selected commit's
Git blob, NOT merely the copied target), and `R22_SCHEMA_FILE` (the historical
schema JSON). Then run the owned test path with existing pytest, Pydantic2 and
jsonschema. Disable unrelated pytest plugins for the bounded contract check.

    python -S -m pytest -q tests/r22_probes/role01/test_nested_numeric_contract.py

The parent counterexamples must remain RED. No original oracle is modified.
Readiness on e44 is not approval of a future focused PR; verify actual focused
paths/context and rerun the relevant tests on the published immutable head.
No renderer/browser/tool/scale/npm/SUM matrix is run by these fixtures.