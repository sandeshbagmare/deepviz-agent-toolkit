# R41 role10 — exact546 independent acceptance and strict diagnostics

Product pin: `546c25ea75ee9d8a41b3832aa639664bc9a683b5`.
This is independent testing, **not a release approval** or production change.

## Actual results / do not conflate cohorts

- All unmodified producer86Python/98Node, published R15GP73each and R13prefix
  67Python/63Node: **460 independent PASS**. Fresh OWN Git bytes/compiledJS,
  not author totals or sibling/installed artifacts.
- First new literal diagnostics: Python13PASS12FAIL; Node15PASS8FAIL. Kept
  assertions and inputs **unchanged after execution**. Fourteen failures are
  our overly strict empty-warning expectations despite established mixed-type
  warnings, not fourteen product bugs. Two Python AUTO-pages expectations hit
  a previously disclosed inference-policy question. Four failures (two carrier
  variants per language) identify ONE selected-record/protocol-cell boundary
  question for R04. Do not call these twenty failures twenty new bugs.
- Required positive JSONL ownership was not reached by the mixed-type warning
  diagnostics. A separate homogeneous three-row file supplies **two additional
  actual passes**: owned file closes/Windows rename works, borrowed reader stays
  open/reusable, host content unchanged. Original diagnostics were not changed.
- Four original 64KiB-key policy tests remain **four strict failures** against
  the unchanged4096Bfield-name guard. No xfail, cap, schema or oracle edits.
- First Node launch used an invalid Windows `--import C:\...` and stopped before
  consumers. Saved all four FILE-level errors; corrected ONLY the preload URL
  to file://, then ran the previously-unexecuted Node cases once on SAMEownJS.
  No Python/original-policy/rebuild replay. Initial own mypy two annotation errors
  were corrected before product execution. Failures stay in evidence.

## Portable execution (existing dependencies ONLY)

Use a clean Git worktree at the exact pin, a NEW output directory and read-only
existing Python/TypeScript installations. In PowerShell, set process-local
`PYTHONPATH` to the existing venv's **Lib/site-packages only** and
`PYTHONDONTWRITEBYTECODE=1`. Run with that venv Python and **-S**; no .pth/editable
site initialization. No dependency install, project-config or source edit.

```text
python -S tests/r41_probes/role10/driver.py setup --source <clean546worktree> --output <NEWartifactdir> --compiler <existing-node_modules/typescript/bin/tsc>
python -S tests/r41_probes/role10/driver.py run --bindings <NEWartifactdir>/bindings.json
python -S tests/r41_probes/role10/driver.py ownership --bindings <NEWartifactdir>/bindings.json
```

The full diagnostic `run` returns **1**, honestly retaining the strict diagnostic
and policy failures. `ownership` returns0 on the observed head. The `node` mode
exists ONLY for resuming a launch that stopped before any Node consumer ran; it
does not rebuild or replay completed Python/policy checks. Avoid blind reruns.

Setup copies canonical Git blobs into a unique fixture layout required by the
original GP physical-root import guard. It compiles candidate and untouched
comparison base6d0 with the read-only compiler. Every source/oracle/emitted/tool
hash is verified before consumers and after each process. Original R13 baseline
comparison still executes its unchanged script in a real subprocess, with only
-S/source-provenance binding added (no output/numeric oracle mocked). Node loads
proven OWN modules through a provenance preload before any original test import.

## Narrow outstanding boundary (R04 decides contract/fix)

Input: `{"outer":[{"nodes":[0,false],"items":[null]},{"nodes":[-2],"items":[true]}]}`
with `{kind:'table', aggregation:'none', data_path:'outer'}`. Ordinary-record
flattening would retain two rows/nested scalar-cell positions. Python instead
raises ambiguous GraphQL connection fields; Node raises unequal column arrays.
The existing scalar-column/sibling/true-page controls are all preserved, so do
NOT "fix" this by weakening them, dropping sibling fields or changing tests.
R04 must disposition the nested protocol-field/ordinary-record distinction;
no novel-issue count, production repair or final approval is asserted here.

No COUNT/MCP/fullnpm/old-format-matrix/10M/cost/browser/provider/install/CI/main
acceptance was run or implied. No symlink privilege result or Arrow/Parquet
acceptance follows from zero skips in these selected cases.
