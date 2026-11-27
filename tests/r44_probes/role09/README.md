# R44-09 — fixed-source independent Python546 acceptance

Only product `546c25ea75ee9d8a41b3832aa639664bc9a683b5`. No TS, render matrix,
10M, installs, environment/digit-limit edits or production edits. Not final-main acceptance.

`original-controls.json` binds nine UNCHANGED original Git blobs, published as
non-discoverable `originals/<copied_name>.txt` byte-exact assets. This avoids adding
an unrelated default-suite environment requirement from the out-of-scope old-base
comparator. None of its assertions or guards is removed or weakened. Materialize
the originals ONLY for this explicitly selected gate in an initially clean OWN
detached exact546 checkout at `tests/r44_probes/role09/<copied_name>`; this retains
the original three-parent checkout depth and strict import guards. The runner verifies
all original Git bytes and all source/config/contract hashes before and after each
group; actual imports and normalize code filename must come from that checkout.
Python `-B -S` plus explicit existing read-only site-packages avoids editable MAIN
hooks. Pytest plugin autoload is disabled by a real CLI option, not an env edit.

After copying this NEW directory to the OWN checkout, materialize each original
with ordinary Python (no environment writes): read the manifest; for each item,
read `originals/(item['copied_name'] + '.txt')`; verify its SHA256 equals the
manifest; write those IDENTICAL bytes to `item['copied_name']` in the same directory.
If a target exists, require exact equality rather than overwrite it. The runner
independently compares each runtime copy against its immutable original Git blob.
Git objects for the manifest's exact commits must be locally available; fail closed
if absent. Do not rename assets back to discoverable test modules on a product branch.

One fresh process/output directory per fixed group, e.g. PowerShell:

```powershell
& '<existing-venv>/Scripts/python.exe' -B -S '<exact546>/tests/r44_probes/role09/run_gate.py' `
  --source '<exact546>' --site-packages '<existing-venv>/Lib/site-packages' `
  --output '<own-evidence>/runs/literal' --group literal
```

Groups: boundaries, fidelity, graphql, lifetime, prefix, literal, policy, known-mean.
No combined pass can hide policy or known-mean RED. The known-mean group is the
UNCHANGED published R38-11-F1 regression, now genuinely executed on546, not a claim
that its older-c1b result already proved546. Four policy cases remain untouched.

Fidelity selects original F1/F3/import guards, not renderer-count tests. Prefix
excludes ONLY the unaffected old-base mean/sample child/env comparator; all
affected numeric/state/budget controls remain unchanged. Original R16's31-file
was READ, not run: its autouse environment-selector setup is not changed or
bypassed. Original R10F1/F3 and published R17 strict scalar/selected-root controls
run instead. Selected/deselected IDs and actual phase outcomes are recorded.

NEW literal controls cover selected-root two-column false/null data, one-pass
late float prefix32.25, weighted other COUNT3, selected late-collision lifetime
with retained traceback for owned and borrowed inputs, actual unchanged16MiB
two-field guard with future borrowed row, large-integer positive controls and
ordinary business-errors data. No expected result is computed by production.
Payload/row bounds are finite test fixtures, not a measured process-RSS ceiling.

Publication packaging does not rerun or relabel the recorded tests: their runtime
paths/bytes stay frozen in the exact546 scratch checkout and receipts. Only this
README and asset storage paths change after testing; the two NEW Python files and
all nine original semantic/source bytes must remain byte-identical in the index.
