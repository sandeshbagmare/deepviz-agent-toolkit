# Actual focused PR33 independent tester17

Tested immutable source: `99841ffb80e0f2ea90c753c1bf0ceff718e0e180`.
These NEW helpers do not modify production, provided tests, schema or the
previously published 79-case independent test. They invoke the actual 40-case
focused suite and that **unchanged** 79-case suite separately, with exact source
and import proofs in each process. Both completed once; do not replay merely
for status. Full logs, JUnit, commands and actual JSON/schema outputs are in
`docs/coordination/evidence/R25-17/`.

## Reproduction when a source-specific retest is actually needed

1. `git -c core.autocrlf=false archive --format=zip --output <NEW-archive> 99841ffb80e0f2ea90c753c1bf0ceff718e0e180`.
2. Extract into a unique isolated directory and compare EVERY tracked file's
   raw working bytes with `git show <source>:<path>` before testing. Save an
   identity JSON beside the extracted tree using the evidence's schema:
   `product_source_sha`, `actual_model_path`, `source_files` entries with `path`
   and SHA256, and `independent_unchanged_79_probe.sha256`. No source edits.
3. Use the existing read-only venv, `python -S`, process-only `PYTHONPATH` with
   that snapshot's `python/deepviz/src` first and existing site-packages next.
   Do not process an installed sibling's editable `.pth` hooks or install
   anything. Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONIOENCODING=utf-8`.
4. Run each mode with its own NEW output directory:

```powershell
python -S tests/r25_probes/role17/run_pr33.py provided <identity.json> <NEW-output40> tests/r22_probes/role17/test_contract_slice.py
python -S tests/r25_probes/role17/run_pr33.py independent <identity.json> <NEW-output79> tests/r22_probes/role17/test_contract_slice.py
python -S tests/r25_probes/role17/inspect_json.py <identity.json> <NEW-public-json-output.json>
```

`provided` imports the actual public `deepviz.models` in the SAME process before
pytest and checks its file/hash. `independent` leaves that module unimported;
the unchanged79 fixture explicitly imports the selected trusted committed file
and records its actual path/hash. Both verify all snapshot source hashes before
and after tests and preserve pytest failures. The 15 JSON output inspections
are **not extra pytest cases**; they record real accepted canonical JSON and
actual child validation errors for independent literal expectations.

Result on the frozen PR head: **40 passed (0.35s) + 79 passed (0.75s), across
TWO commands**, zero failed/errors/skips; 15 output inspections passed separately
(4 accepted / 11 rejected). This is one independent source-specific tester
result, not whole-toolkit integration, human GitHub approval, current remote CI,
merge or release acceptance. R04 owns the other three independent reports,
current-head green-check verification and actual merge. No API was called here.

The OLD worker branch contains unrelated historical work; do not wholesale
merge it into PR33. These helper/evidence paths are tester-owned only. A changed
product head requires affected source checks/retest, not borrowing this verdict.
