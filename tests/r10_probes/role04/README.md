# Independent UTF-8 envelope regressions (R10 role04)

Source checkpoint: `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`.
These are NEW tests, not changes to normalizers, policy or existing oracles.
The shared JSON contains literal expectations, never imports private producer counters.

| UTF-8 byte budget | Python checkpoint | TypeScript checkpoint |
|---|---:|---:|
| Extracted raw/flattened field names, inclusive | 4096 | 65536 |
| String cells, inclusive | 65536 | 65536 |

This **intentional test expectation difference describes the checkpoint**, not a
new policy decision. R04 owns that decision. The original N11 four64KiB-key
preservation failures remain untouched. Lowering the TypeScript field limit or
raising Python's limit should change these fixtures only after explicit policy
review, not by silently importing whatever production constant is present.

## Portable execution

From the repository root, use an already prepared Python environment with
declared dev dependencies and Node/TypeScript dependencies. No test needs
network, optional Arrow, a renderer or a paid provider.

PowerShell:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'python/deepviz/src'
python -m pytest tests/r10_probes/role04/test_utf8_field_envelope.py -q
python -m ruff check tests/r10_probes/role04/test_utf8_field_envelope.py
python -m mypy tests/r10_probes/role04/test_utf8_field_envelope.py
npm run build
node --test tests/r10_probes/role04/utf8-field-envelope.test.mjs
```

POSIX shell:

```sh
PYTHONPATH="$PWD/python/deepviz/src" python -m pytest tests/r10_probes/role04/test_utf8_field_envelope.py -q
python -m ruff check tests/r10_probes/role04/test_utf8_field_envelope.py
PYTHONPATH="$PWD/python/deepviz/src" python -m mypy tests/r10_probes/role04/test_utf8_field_envelope.py
npm run build
node --test tests/r10_probes/role04/utf8-field-envelope.test.mjs
```

An isolated review worktree may use an existing read-only compiler instead:
`node <installed-typescript>/bin/tsc -p packages/deepviz/tsconfig.json`.
Both paths must build **this checkout's source**, not another checkout's dist.

## Coverage and limits

- Shared literal4095/4096/4097 plus65535/65536/65537-byte names and
  65535/65536/65537-byte cells across1-/2-/3-/4-byte Unicode units; short ASCII
  padding hits exact lengths. Accepted keys and values must remain identical.
- Raw, complete composite and array-index names. Dots and`.0` count toward the
  budget. Near4096 composite tests have individually safe components, so an
  earlier raw-name rejection cannot masquerade as the flattened-boundary check.
- Invalid row1or41of80stops consumption precisely there, even after the32-row
  inference prefix/10-row reservoir fills. TS asserts iterator closure; Python
  asserts pulls only, not ownership/lifecycle behavior reserved to another lane.
- Lazy512×61440-byte payloads: a small reservoir/group result must consume every
  input, preserve count512, retain10rows and disclose sampling/cardinality loss.
  Large retained reservoirs/groups must reject with the **16MiB state** error
  before row275, not accidentally pass on field/cell/record errors. All individual
  field names and cells in state tests fit both implementations.

These finite tests are **not** 10M-scale, process-RSS, continuous-memory,
distribution, visual-output or final release acceptance. Sampling choices may
differ across languages; each preserves original source order and full values.
