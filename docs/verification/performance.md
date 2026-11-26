# Streaming performance verification

## Status: harness ready; integrated performance evidence pending

This independent harness owns only `scripts/performance_suite.py`,
`tests/test_performance_contract.py`, and this document. It does not change
`normalize.py` or `benchmark_scale.py`. The initial worktree starts at source
commit `2b2709e`; that checkout has models but no normalization or renderer
implementation. **No successful 10M normalization, render, or timing is claimed
for that source.** Missing integration fails rather than skipping or substituting
a benchmark-only reducer. Parent-supplied integrated source is required next.

## Reproduce against integrated source

Use a committed, stable checkout containing the real `deepviz.normalize.normalize`
and `deepviz.render.render` APIs. No new dependency is required for measurement;
PNG inspection uses the project's installed Pillow development dependency.
Choose a fresh evidence directory; the JSON report uses exclusive creation and
each render gets its own unique subdirectory.

```powershell
$python = 'C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe'
$harness = 'C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-perf'
$source = 'C:/path/to/parent-supplied-integrated-checkout'
$evidence = 'C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-perf-evidence-unique'
& $python "$harness/scripts/performance_suite.py" --source-root $source `
  --counts 10 1000 100000 1000000 10000000 --repeats 2 --timeout 900 `
  --artifact-dir "$evidence/artifacts" --output "$evidence/report.json"
```

Default cases are `numeric_sample`, `category_sum`, and `category_mean`. All five
sizes run through all three cases. Numeric sampling runs in two separate workers
per size and compares canonical output SHA-256, not timing. Categorical reductions
run once per size and are checked against independently calculated exact totals.
All five renderers run with source counts 10 and 1,000 by default; their bound is
`min(--max-points, 100)`, so the 1,000-row render case is actually reduced.
Normalization-only cases retain at most `--max-points` (default 2,000) rows.

To run only the 10M numeric and categorical-sum cases, omit renderer checks
explicitly (this is **partial evidence**, not the full gate):

```powershell
& $python "$harness/scripts/performance_suite.py" --source-root $source `
  --counts 10000000 --cases numeric_sample category_sum --repeats 2 `
  --render-counts --timeout 900 --output "$evidence/ten-million-only.json"
```

After cherry-picking the harness into the integrated checkout, run its tests from
that checkout. Explicit `PYTHONPATH` is important with the shared editable venv:
otherwise pytest can import another worktree's models. The harness rejects source
modules outside the requested checkout instead of silently benchmarking them.

```powershell
$env:PYTHONPATH = "$source/python/deepviz/src"
Set-Location $source
& $python -m pytest -q
& $python -m ruff check .
& $python -m mypy
& $python -m mypy scripts/performance_suite.py
& $python -m build --outdir "$evidence/dist"
```

`pytest -m 'not scale'` excludes the nine 100K/1M/10M performance tests; record
that exclusion, never describe it as a full-scale pass. The regular suite includes
the scale tests. A full default CLI run also checks cross-size OS peak growth.

## What the contract checks

- The input is a generator: each row is constructed on demand. No full `list`,
  DataFrame, array, file, or encoded JSON input is prepared. A counting iterator
  records actual pulls and exhaustion independently of the normalizer's metadata.
- Every requested input count must equal both the observed consumed count and
  `NormalizedData.input_count`. Early stop, duplicate consumption, empty output,
  or an output larger than the declared bound is a failure.
- Numeric rows are `{x: i, value: i % 101 - 50}`. Samples must have the exact
  bounded size, unique input-ordered valid rows, unchanged values, and disclosed
  loss when reduction occurs. A fixed 1,000-row regression rejects prefix-only
  truncation and verifies repeatability; the CLI also compares two fresh-worker
  digests at each size.
- Categorical rows are `{category: "group-" + str(i % 7), value: i + 1}`. For
  category index `c`, the independently calculated count is
  `n = (N - 1 - c) // 7 + 1`, its sum is
  `n * (2 * (c + 1) + (n - 1) * 7) // 2`, and its mean is `sum / n`.
  Every category and the reconstructed grand total `N * (N + 1) // 2` are checked;
  means use a documented floating-point tolerance (`rel_tol=1e-10`). Small tests
  also cover the unequal-size, high-cardinality weighted-mean overflow bucket.
  Reports retain the seven actual category values and observed (weighted, for
  means) grand total, in addition to the bounded-output digest.
- Renderers receive only `normalized.records` (a bounded list), with aggregation
  disabled to avoid reducing already-reduced data again. Their input metadata
  must equal that bounded length and output count must remain within the bound.
  The original source count remains a separate report field, not relabeled as a
  renderer input count.
- A missing API, missing dependency, assertion failure, timed-out worker, source
  change, failed artifact inspection, or nondeterministic digest makes the run
  fail. Case/comparison failures are reported in `errors` and the CLI returns
  nonzero; setup/argument failures can exit before a report is written.
  There is no mocked ingestion implementation and no optional-renderer skip.

### Planned matrix (expected counts, not observed results)

| Requested rows | Numeric sample expected output | Sum expected groups | Mean expected groups | Observed integrated result |
| ---: | ---: | ---: | ---: | --- |
| 10 | 10 | 7 | 7 | Pending |
| 1,000 | 1,000 | 7 | 7 | Pending |
| 100,000 | 2,000 | 7 | 7 | Pending |
| 1,000,000 | 2,000 | 7 | 7 | Pending |
| 10,000,000 | 2,000 | 7 | 7 | Pending |

These expectations assume default `max_points=2000`; numeric low-count cases do
not pretend to require sampling when their complete input already fits.

## Measurement methodology and limits

Each measured CLI case gets a fresh child interpreter via `subprocess.run`,
without `shell=True`. The parent captures bounded metadata, never source rows.
No `tracemalloc`, periodic polling, third-party memory monitor, or Python
allocation instrumentation runs over the 10M input.

- **Windows:** standard-library `ctypes` calls `GetProcessMemoryInfo` and reads
  `PeakWorkingSetSize` in bytes. Handles and structure fields use pointer-width
  types. This is a process working-set high-water mark, not private bytes or
  committed virtual memory. Short nonresident allocations may not appear in RSS.
- **Linux:** `resource.getrusage(resource.RUSAGE_SELF).ru_maxrss`, converted from
  KiB to bytes. macOS uses the same API but its value is already bytes. The Linux
  and macOS branches have not yet been executed in this Windows worktree.
- **`peak_rss_bytes`:** inclusive process high-water mark observed at workload
  completion. Includes the interpreter, imported libraries, generator bookkeeping,
  normalizer, bounded result, assertions, digest serialization, and, for renderer
  cases, rendering plus artifact decoding. It excludes other processes' memory
  (including native helpers or browsers), and is not engine-only memory.
- **`baseline_peak_rss_bytes`:** a high-water mark read after required API imports,
  before normalization. **`peak_high_water_growth_bytes`** is the difference of
  the two high-water marks. It is not peak live memory minus current baseline,
  nor an exact allocation delta attributable to normalization. A zero difference
  can mean imports had already established a larger process peak.
- **`elapsed_seconds`:** `perf_counter` around real normalization, including
  on-demand row generation and iterator bookkeeping. Validation and digesting
  follow this timer. `render_elapsed_seconds` times only the rendering call;
  `subprocess_wall_seconds` includes process startup and provenance/report work.
  These are observed wall times, not a CPU-only microbenchmark or promised SLA.
- **Growth check:** for each normalization case, compare the maximum inclusive
  peak across sizes/repeats with the minimum small-stream inclusive peak.
  The default allowed increase is 64 MiB (`--max-peak-growth-mib`). This is a
  configurable regression threshold, not a mathematical proof of O(1) memory,
  and it does not compare renderer/library peaks against normalization peaks.

Every report row records source HEAD, dirty paths, and SHA-256 of all Python
source modules. The worker checks source hashes/HEAD before and after execution;
the parent rejects mixed-source rows and checks the source again at the end.
The top-level report also records harness provenance, Python, platform, requested
sizes, repetitions, checks and failures. Preserve the JSON and matching sources.
Dirty paths are disclosed; a dirty-source run is not a clean-release benchmark.

Artifact checks go beyond existence but are deliberately limited: SVG must parse
and contain drawable geometry; PNG must decode and contain nonuniform pixels;
HTML must have document and script structure. These are **not** a human visual
review or browser execution. HTML reports explicitly say browser execution is
unverified. Separate browser/visual verification must inspect actual output,
validate chart semantics, and treat console errors as failures.

## Harness-only verification ledger — November 26, 2026

Base: `2b2709e` in isolated branch `perf/verification`. All Python commands used
`C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`.

| Command | Observed outcome | Scope |
| --- | --- | --- |
| `python -m pytest tests/test_performance_contract.py -k generator_is_lazy -q` before implementation | 1 failed, 32 deselected | Expected RED: missing harness; not performance evidence |
| `python -m pytest tests/test_performance_contract.py -k changed_source -q` before source-stability helper | 1 failed, 35 deselected | Expected RED: missing source-stability check |
| `python -m pytest tests/test_performance_contract.py -m 'not integration and not scale' -q` | 16 passed, 23 deselected | Generator laziness, independent totals, validation rejection, Windows OS peak read, source stability, artifact inspection; integration explicitly excluded |
| `python -m pytest -q --tb=no` with worktree `PYTHONPATH` | 23 failed, 39 passed | NOT GREEN: no `deepviz.normalize` in this source; no rows normalized for the failing integration/scale cases |
| `python -m ruff check scripts/performance_suite.py tests/test_performance_contract.py` | Passed | Owned Python files only |
| `python -m ruff check .` | Failed | Existing `tests/test_models.py:2` I001 import ordering; unrelated file left untouched |
| `python -m mypy` | Passed, 1 source file | Existing configured model-only source scope at this base |
| `python -m mypy scripts/performance_suite.py` | Passed | Harness explicitly type-checked |
| `python -m build --outdir C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-perf-dist-final-7a0b3348` | sdist and wheel built | Packaging at unintegrated base; not proof of ingestion/render functionality |

The 23 failing cases are: `test_real_normalization_preserves_counts_and_expected_reductions`
(all six count/case parameters), `test_reservoir_is_repeatable_but_not_a_truncated_prefix`,
`test_high_cardinality_mean_other_bucket_is_weighted`,
`test_all_renderers_receive_bounded_records` (all five engines),
`test_fresh_worker_reports_exact_input_and_source_provenance`, and
`test_large_real_stream_contract` (all nine size/case parameters). They remain
failures, not xfails, skips, or inferred passes.

Ruling: the initial branch does not contain other workers' unfinished source;
keep integration tests honestly red until parent supplies the integrated
checkout. Cost: the harness-only branch is not independently merge-green.
Ruling: no whole-plan implementation or extra ledger files were created, because
the delegated ownership explicitly permits only these three files.
Final review: self-review. A fresh nested reviewer was requested but the harness
rejected it with `Subagent depth limit reached (1)`; no independent reviewer
report is claimed. Parent-level independent review remains necessary.
