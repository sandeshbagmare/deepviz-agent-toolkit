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

## Candidate verification

Awaiting the parent's integrated release/candidate commit. No candidate pass,
engine availability, performance result, browser success or issue closure is
claimed. Full 10M streaming/memory benchmarking belongs to separate evidence;
this suite checks bounded output/provenance without claiming scale timings.
