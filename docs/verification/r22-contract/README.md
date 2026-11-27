# Focused ChartSpec numeric trust-boundary fix (#30)

This independently usable model fix starts from default `main` **0ae2cf26426822135fc10d337fcacf580b7ed833**, not the broader unfinished toolkit. The only runtime change is the11-line before-validator previously tested at **e44f667ed494fa272f97792ef99942a364ebca24**. It rejects strings and booleans for the five numeric fields, while preserving integral JSON floats, defaults, bounds and dashboard validation. No new schema fields, executable input, renderer or network/file authority.

The original complete30-test prerequisite is included (import-order-only lint adjustment); a new10-test module checks own-checkout imports, generated-schema freshness and JSONSchema/Python agreement at the numeric trust boundary, including children. `schemas/chart-spec.schema.json` is the **real regenerated export**, byte-identical before/after the runtime fix: SHA256 `ecd85be393444b7ff5bd9fcbb99cae4c900fad570d961476e1bcd4e443c6f65d`.

## Executed evidence

- Original source: **6 failed /24 passed /0 skipped**.
- Expanded strict controls, still before runtime edits: **12 failed /28 passed /0 skipped**.
- After exact validator and import-order cleanup: full suite in this focused checkout **40 passed /0 failed /0 skipped**,0.35s. Full-branch Ruff passed; mypy passed for the only model source file.
- [Machine summary, source/test/workflow hashes and all RED names](red-green-summary.json).
- [Actual public JSON validation outputs](validation-output.json): four accepted/serialized/Schema-valid fixtures and six rejected fixtures with real errors. This is a **model-only change**, so chart rendering is not applicable; no screenshot or whole-toolkit runtime is invented.

Local verification uses the existing project venv without installations. Because the foundation is a namespace package and the shared venv has another editable checkout, tests use `python -S` with `PYTHONPATH` explicitly containing this checkout's `python/deepviz/src` and the existing read-only site-packages. The test verifies the actual imported model path. CI has a clean dependency-only environment, not the editable sibling hook.

```powershell
# Set own PYTHONPATH; with shared local venv use -S as explained above.
python -m pytest -q --strict-markers
python -m ruff check .
python -m mypy
```

The new workflow runs **contract-only** Python3.11/3.12/3.13 tests/lint/types. It does not claim full-renderer integration. No package/dependency/CLI implementation was pulled from the failing broad candidate; those remain future slices.

## Merge gates

Two genuine independent reviewers and two testers must examine the exact published proposed head, and actual focused CI must be observed green before merge. Author evidence is not an independent approval. Broader draft PR31, unresolved toolkit defects and900legitimate-resolution criterion remain separate/unmet.
