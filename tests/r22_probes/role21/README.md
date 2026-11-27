# Frozen-source scale envelope (R22-21)

One stdlib script, not a benchmark framework. It never edits the product or the
original 09/11 recipes. Default mode runs Git checks and prints a plan; it creates
no output directory and executes **zero performance commands**. Exit 0 for a plan
is **not a passing scale gate**.

## Future use by the integration owner

Use an isolated, reviewed **exact 40-character source commit** and a fresh external
output directory. Use the existing project venv. Review the pinned runner before
execution: the fixed command runs that commit's `scripts/performance_suite.py`.
The paths below are operator placeholders, not commands executed in this task.

```powershell
& $py tests/r22_probes/role21/frozen_scale_envelope.py $isolatedSource $fullSha $newExternalEvidence
# Only after R04 authorizes the frozen scale run:
& $py tests/r22_probes/role21/frozen_scale_envelope.py $isolatedSource $fullSha $anotherNewExternalEvidence --run
```

Optional host-authorized data inputs are `--allow-input relative/data.csv=SHA256`.
Tracked, nonignored-untracked and ignored-explicit data files are hash-frozen;
undeclared nonignored untracked inputs reject. These data paths are **not read by
the scale generator** and never grant code execution. Code/config extensions and
traversal reject. No shell strings, arbitrary command option, URL or model-authored
code. Existing output directories and in-checkout outputs reject, not overwrite.

## Guarded boundary

- Exact HEAD and tree, clean tracked state; source/runner/tests under `python/`,
  `scripts/`, `tests/`, root/nested TOML/INI/CFG/lock files, requirements, Git
  attributes/ignore and explicit data inputs are hashed before and after.
- Tracked raw bytes must match Git blob bytes (LF checkout, not silently normalized
  CRLF). Hashing is streamed. Dirty files hidden by assume-unchanged still reject.
- Unexpected root/script import shadows and ignored additions in the source import
  directory reject. User-site/PYTHONHOME/optimization are disabled for the child;
  a fresh external pycache prefix avoids borrowing candidate bytecode caches.
- Always check after return, including nonzero/timeout execution. Original source,
  runner, tests and config are not patched. Own envelope bytes are checked too.
- Only a complete passed 20-worker matrix (5 scales, two numeric repeats and one
  each sum/mean), exact disk-source hashes/HEAD, integer counts, full consumption
  and expected bounded outputs can pass the **provenance/count** gate. Missing,
  skipped, incomplete, wrong-source/count/repeat and >4 MiB reports reject. Logs
  go to files rather than unbounded in-memory capture.

`PROVENANCE_AND_COUNTS_PASS_NOT_SCALE_APPROVAL` means exactly that. The result
always says `measurement_verified: false` and explicitly states that same-process
imported paths/bytecode are **not attested**. The existing child `load_api` guard
must independently reject foreign imports; add a child-origin/hash hook before
making a stronger import claim. This task did not execute that production guard.

This is not the independent 11 value/loss/memory-method validator: it does not
prove category arithmetic, sample digests, RSS limits or measurement truth.
Run those independent semantic/memory gates on the same immutable receipt before
acceptance. Old 11 validators may require zero dirty paths: an explicitly allowed
untracked data file here is **not** a waiver of that independent policy.

Installed interpreter/dependencies/Git, unrelated ignored files and the operating
system are trusted external tools, not fully snapshotted environments. Endpoint
snapshots cannot detect changes reverted during the child run or stop a concurrent
writer. Use an isolated frozen worktree. No benchmark, CI or release approval is
conferred by the script or the synthetic fixtures.

## Verification performed here

Only `test_frozen_scale_envelope.py` and scoped Ruff/mypy were run. Test runners at
the fixed path are tiny, explicitly synthetic programs generating metadata, not
DeepViz or 10M data. A positive metadata fixture is not a real measurement. No
original 27-oracle, production test suite, build or scale replay; no dependencies
installed. See the owned R22 report and exact command receipts for actual counts.
