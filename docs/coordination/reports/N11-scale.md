# N11 streaming scale and resource-adversary evidence

- Owner: N11 tester subagent; session `ses_de6d4ff6bffe8vUW9GONL49CgM` from C17 live register.
- Main checkout: `C:\Users\bagma\deepviz-agent-toolkit`.
- Assigned branch/worktree: `test/n11-scale` at `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n11`.
- Required and verified source base/current: `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`; new `test/n11-scale` worktree created successfully, initially clean. Main is `release/candidate`, dirty only `AGENTS.md`, `opencode.json`, untracked `RESUME.md` and coordination files (preserved).
- Allowed writes: this MAIN report; unique evidence/artifacts and a new scoped harness in assigned worktree. No production changes, shared installs, spawning, GitHub writes, or main candidate Git writes.
- Acceptance: actual generator streaming tiers 10 / 1K / 100K / 1M / 10M; input/output/loss/strategy/warnings; measured elapsed and memory methodology; bounded overflow/cardinality and cell/dashboard resource probes; actual reduced output visually inspected; machine JSON and exact commands/exits.
- Initial command: read `docs/coordination/tasks/N11-scale.md`, then `C17-wave-common.md` (both successful). Existing assigned report absent.
- Current action: all Python/TS scale and 13 bounded resource probes completed; preserve confirmed performance-harness failures and render actual measured reduced values for visual inspection.
- Next action: render 10-row and 10M-row actual category-sum results from machine evidence into Matplotlib PNG/SVG, inspect pixels and native mark heights, then save final checksums/summary.

## Results

## Executed commands and current run

- Read required MAIN recovery/contract/design/plan/dependency-gate documents, task and common contract.
- `git status --short --branch` and `git worktree list --porcelain` (MAIN), exit 0. Historical worktrees preserved; assigned N11 path did not exist.
- `git worktree add -b test/n11-scale C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n11 b6abc8d` (MAIN), exit 0.
- With explicit own `PYTHONPATH` and `PYTHONDONTWRITEBYTECODE=1`, MAIN `.venv\Scripts\python.exe -c ...` import identity check, exit 0: Python 3.12.16, Windows 11 build 26200, `deepviz.__file__` is N11 `python\deepviz\src\deepviz\__init__.py`. `psutil` absent, no installation attempted. OS memory instrumentation uses existing ctypes GetProcessMemoryInfo implementation.
- Started actual command from N11 worktree (completion pending):

```powershell
$env:PYTHONPATH='C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n11\python\deepviz\src'
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' scripts/performance_suite.py --counts 10 1000 100000 1000000 10000000 --cases numeric_sample category_sum category_mean --repeats 2 --render-counts --timeout 600 --max-points 2000 --output artifacts/local/N11/n11-streaming-20261127-r1.json 1> 'C:\Users\bagma\AppData\Local\Temp\opencode\N11-scale-20261127.stdout.log' 2> 'C:\Users\bagma\AppData\Local\Temp\opencode\N11-scale-20261127.stderr.log'
```

- Shell job `sh_2192de1d4001BuRKwvaMcf6Z7F` completed exit 0. Fresh subprocess per case/tier; deterministic numeric repeat, category sum/mean arithmetic oracle, consumed/exhausted count checks, inclusive process OS peak working set with pre-operation high-water baseline. No source list materialized. **20 actual normalization cases passed**, zero errors, all five tiers, sample twice and sum/mean once. `render_counts=[]` deliberately separates this successful scale result from render-harness checks (which fail below). Source SHA/hash unchanged and worktree clean throughout.

## Completed observations and routed findings (2026-11-27)

### Actual all-tier Python execution: PASS on assigned baseline (normalization only)

Machine evidence: N11 `artifacts/local/N11/n11-streaming-20261127-r1.json`.

| Source rows | Sample output | Sample elapsed seconds (two trials) | Sum output / elapsed s | Mean output / elapsed s |
|---:|---:|---:|---:|---:|
| 10 | 10 | 0.001579 / 0.001976 | 7 / 0.002808 | 7 / 0.002361 |
| 1,000 | 1,000 | 0.011629 / 0.013299 | 7 / 0.015213 | 7 / 0.015638 |
| 100,000 | 2,000 | 0.683866 / 0.621042 | 7 / 1.666446 | 7 / 1.017435 |
| 1,000,000 | 2,000 | 7.600707 / 4.939709 | 7 / 14.419164 | 7 / 10.977746 |
| 10,000,000 | 2,000 | 108.775664 / 110.160914 | 7 / 129.786000 | 7 / 90.714617 |

Each generator's actual consumed count equals requested/input count and exhaustion is checked. Sample record values, order, uniqueness and repeat output hash are checked; tiers above 2,000 disclose deterministic sampling and possible missed extrema. 10M sampling discards 9,998,000 source rows; **not 10M displayed marks**. Sum/mean preserve all source contributions in seven groups against arithmetic-progression oracles (mean allows float tolerance). The actual 10M grand sum is 50,000,005,000,000. Full raw records are intentionally not retained.

10M inclusive OS peaks: sample 43,950,080 / 43,974,656 bytes (baselines 42,065,920 / 42,147,840; high-water increases 1,884,160 / 1,826,816), sum 42,401,792 (baseline 42,000,384; increase 401,408), mean 42,385,408 (baseline 42,033,152; increase 352,256). Across fresh tier workers, greatest inclusive-peak growth over smallest-stream minimum: sample 1,757,184 bytes; sum 458,752; mean 585,728, each below the harness 64 MiB gate. These are **whole-process Windows PeakWorkingSetSize** high-water marks, not Python allocation counts or exclusive operation RSS. Scale runs did not enable tracemalloc. Includes interpreter/imports; host contention and working-set trimming affect results. Numeric repeated twice; reductions once. No claim of hardware-independent timing or universal boundedness.

### Bounded resource adversaries: 13 finite probe oracles passed, envelope still incomplete

New evidence-only harness `artifacts/local/N11/n11_resource_evidence.py` (ignored artifact, no production writes), command below, exit 0, 13 passed / 0 failed. Machine JSON `n11-resources-20261127-r1.json` records exact subprocess commands, source hashes/import, current/peak Windows working set, traced Python current/peak, elapsed (with tracing), counts and artifact bytes. One fresh subprocess per finite probe; timeout 120 s; maximum planned source/spool ~17 MB, no deliberate exhaustion.

```powershell
# Same explicit PYTHONPATH and PYTHONDONTWRITEBYTECODE as above; cwd=N11
& 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' artifacts/local/N11/n11_resource_evidence.py --output artifacts/local/N11/n11-resources-20261127-r1.json
```

- High-cardinality sum: 100,000 unique groups -> first nine exact groups + warned other bucket, output 10; sum 5,000,050,000 preserved, other 5,000,049,955. 99,991 source category identities merged into one bucket. Traced peak 212,170 bytes; OS peak 46,874,624.
- Unequally weighted overflow mean: 9 exact groups plus 9,000 values 1 and 1,000 values 101 in overflow; 10,009 consumed -> 10 records, warned other mean 11.000000000000005 (oracle 11), not unweighted group mean 51.
- `aggregation=none`: 100,000 consumed -> 10 ordered reservoir rows; warned override, 99,990 rows omitted. Float sum of two finite 1e308 values -> null with explicit nonfinite warning; mean remains 1e308, no warning.
- 1,024-field, 16-row source -> 10 sampled wide rows, 111,162 normalized JSON bytes. 1,025 fields rejected after first row; cumulative schema overflow rejected after 32 of 33 offered rows. Both raise explicit ValueError without exhausting source.
- **N11-R1 / resource boundary gap, owners C17 + N04/N05/N06:** ten 1,048,576-character cells are all retained (10,485,981 normalized JSON bytes), no truncation, byte rejection or warning; OS high-water grows 13,852,672 bytes; traced peak 14,169,307. Ten 65,536-character cells likewise accepted (655,581 bytes). Finite safe reproducer verifies that max_points alone is not a cell/byte cap. Source inspection agrees `_scalar` passes strings unchanged and no total normalized-byte limit exists. Need parent-owned explicit supported byte envelope/early rejection policy or documented boundary; do not infer unlimited safety from scalar-row benchmarks.
- **N11-R2 / dashboard resource boundary gap, owners C17 + N05/N06:** 512 source rows consumed once; one child -> 10 output records versus 24 children -> 240, each child input_count 512. 24-child OS peak 54,272,000; traced peak 4,601,222; runtime 7.426627 s with tracing. One scratch file 2,118,482 bytes in both cases, cleaned. HTML/manifest expand from 44,342/45,534 bytes to 1,034,210/1,082,550. Separate 2-child/2,048-row/8KiB payload probe creates **16,865,294 scratch bytes** while returning just 20 rows, cleaned successfully. No spool/combined-child byte budget observed; source shows entire iterator is spooled before reductions. This is a confirmed missing guard, not proof of host exhaustion. Browser execution intentionally NOT RUN for envelope artifacts.

### Existing performance/render verifier fails: route to C17 / N07 (harness owner)

Command (same source/PYTHONPATH), exit **1**:

```powershell
& 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' -m pytest tests/test_performance_contract.py -m 'not scale' -ra --junitxml=artifacts/local/N11/n11-performance-pytest.xml > artifacts/local/N11/n11-performance-pytest.log 2>&1
```

Actual result **25 passed, 5 failed, 9 deselected, 0 skipped**, 18.88 s. All five `test_all_renderers_receive_bounded_records` cases fail in `scripts/performance_suite.py:218/221`, not in normalization. Matplotlib/Vega static accessible HTML legitimately has no script but the inspector requires one. Plotly/ECharts/AntV produce valid manifest.json entries but inspector rejects suffix `.json`. Reproducer/log/JUnit are preserved; no existing tests or source were weakened. This blocks a default full `performance_suite.py` render-inclusive PASS on this SHA; separate scalar streaming PASS does not conceal it. Fix verifier to distinguish static HTML and validate manifest JSON, then rerun all five. Renderer semantics require separate visual/browser verification.

### Independent TypeScript streaming (additional, not semantic parity signoff)

- Compiled own unchanged TS source using MAIN's existing compiler only: `& 'C:\Users\bagma\deepviz-agent-toolkit\node_modules\.bin\tsc.cmd' -p packages/deepviz/tsconfig.json`, exit 0. No npm install/shared writes.
- `node --expose-gc packages/deepviz/scripts/benchmark-stream.mjs > artifacts/local/N11/n11-typescript-streaming-20261127-r1.json`, exit 0. Node v26.13.1, win32/x64, baseline `b6abc8d`. All five actual async-generator tiers pass count/output bounds: 10->10, 1K->1K, 100K/1M/10M->2K. Elapsed 3.14, 15.19, 742.61, 6325.48, 63526.10 ms. 10M sampled RSS peak 132,182,016 bytes, baseline 131,481,600; sampled heap peak 40,437,512.
- Method: one process, explicit GC before each tier, memoryUsage sampled every 10K yields and after normalization; prior-tier RSS persists. This is sampled RSS, not continuous or isolated-process peak, and excludes rendering. Existing script checks counts/strategy, not semantic parity/warning correctness; N03 owns those. Original redirection is PowerShell UTF-16; generated UTF-8 copy `n11-typescript-streaming-20261127-r1.utf8.json` contains the same decoded JSON. Raw SHA256 `9e3b03344b963a77ff8c82d4619adbe0c48e68c40d7df3e43dea9c9d91cc0118`.
