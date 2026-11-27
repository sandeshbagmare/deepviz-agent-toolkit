# Independent tester A — acceptance matrix

## Scope and independence

Tester A owns only `tests/test_acceptance_matrix.py`,
`tests/fixtures/acceptance/**`, and this report. No implementation files,
other testers' files, GitHub issues, or GitHub reviews are modified.
Source starting point: `0ae2cf2` (`main`, before parallel implementations).
Schema/design were read before tests were authored.

## Prepared acceptance coverage

- 900 primary engine × kind × theme × source cases: five engines,
  18 chart kinds, two themes, five materially different source adapters.
- Additional TSV, JSONL and one-shot generator rendering; low-n numeric
  preservation for every kind/source; exact independent aggregation totals;
  sampling provenance/count bounds; nested numeric fields and GraphQL pages.
- Artifact identity, counts, path confinement, uniqueness, size bounds,
  escaped adversarial titles, native browser-engine bootstraps and populated
  native configuration, and nonblank static-image semantics.
- Invalid schemas/input, script-bearing specs, nonfinite values, missing mapped
  fields, and preservation of unrelated/previous files.

Cases are test executions, **not** independent issues or completed user issues.
No output existence check alone establishes rendered correctness. Native HTML
configuration checks do not establish successful browser execution; a browser
run and visual inspection remain separate release evidence.

## Initial environment / evidence

On the shared project virtual environment at preparation time: NumPy,
`vl_convert`, Pillow and Ruff were importable; pytest, Matplotlib and Plotly
were not installed. Parallel normalize/render implementations were absent
from the seed commit. Initial commands and results will be appended below.

Actual initial run (the shared environment gained pytest during preparation):

```text
C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe -m pytest tests/test_acceptance_matrix.py -x -q
1 failed in 0.50s; ModuleNotFoundError: No module named 'deepviz.render'
```

This is an expected initial missing-implementation failure, not an engine
defect or completed issue. Tests were not skipped to turn this into a pass.

Preparation checks:

```text
python -m pytest tests/test_acceptance_matrix.py --collect-only -q
1149 tests collected in 0.20s
python -m ruff check tests/test_acceptance_matrix.py
All checks passed!
```

The interpreter for both commands was the shared project `.venv`. Collection
is not execution. The initial import resolved the shared editable installation;
candidate runs will explicitly set `PYTHONPATH=python/deepviz/src` to select the
candidate worktree rather than accidentally testing a different checkout.

## Seed review corrections (before candidate execution)

- Native Vega SVG is accepted and checked for XML/title safety and populated
  compiled `role-mark` groups. Any supplied native Vega/Vega-Lite spec sidecar
  is independently compiled with real `vl_convert` and its result inspected;
  metadata-only output is not accepted as a rendered Vega artifact.
- A different actual backend is accepted only when a warning explicitly names
  the requested kind, actual backend, and fallback. Artifact semantics are then
  checked against that actual backend, never the requested engine's identity.
- Dashboard source `input_count` remains exact. Until the renderer's output
  accounting contract is finalized, `output_count` may report source rows once
  or the exact sum of complete child contributions, not an arbitrary count.
- Nested dashboard children retain explicit `data_path`; text-format children
  retain the declared source format. Import grouping matches the parent's new
  Ruff first-party declaration without editing this branch's project config.

These are acceptance-harness contract corrections, not implementation fixes.
No integrated candidate has been executed.

Post-correction preparation evidence:

```text
python -m ruff check --config "lint.isort.known-first-party=['deepviz']" tests/test_acceptance_matrix.py
All checks passed!
python -m pytest tests/test_acceptance_matrix.py --collect-only -q
1149 tests collected in 0.17s
```

A harness-only Python check also generated a real Vega-Lite SVG using
`vl_convert`, accepted its SVG/native-spec artifact, accepted an explicitly
named cross-backend fallback, rejected the same fallback without disclosure,
and verified nested dashboard child paths. This validates the corrected
inspector, **not** the toolkit's render implementation or any release candidate.

## Candidate verification

Awaiting the parent's integrated release/candidate commit. No candidate pass,
engine availability, performance result, browser success or issue closure is
claimed. Full 10M streaming/memory benchmarking belongs to separate evidence;
this suite checks bounded output/provenance without claiming scale timings.
