# N01 independent data/security review

## Ownership and scope

- Owner/session: N01, nested independent reviewer under C17; actual session `ses_de6da09ecffeMwVLSxt0fA4s3K` read back from C17's report.
- Assignment: `docs/coordination/tasks/N01-data-review.md`.
- Date: 2026-11-27.
- Allowed writes: this report and N01-owned untracked verification artifacts only.
- Source access: read-only; no production edits, Git mutations, commits, or spawning.
- Candidate at assignment: `468b28c` (incomplete, not independently verified yet).
- Branch: `release/candidate`; assignment base `468b28cfdcfcb7be53beaef2c911bf81cac70f44`.
- First observed integrated HEAD: `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`; tree `8bf9b42841e1171e2e3827685bc17ef44535aa1c` (concurrent integration; not a frozen final candidate).
- Main dirty paths observed: `AGENTS.md`, `opencode.json`, untracked `RESUME.md` and `docs/coordination/`; not modified by N01 except this report.
- Acceptance checks: independent data/security review, exact source/import identity, concrete reproductions and exit codes, bounded-memory/statistics/parser/loss-disclosure checks, explicit limitations; no final-candidate signoff from historical source.

## Status

- Status: **evidence submitted; changes required, not approved for release**.
- Current action: bounded independent review complete; evidence saved, awaiting source-owner fixes and a new candidate for retest.
- Next executable action for C17: assign findings 1–4 to the renderer owner and finding 5/numerical residual to ingestion, integrate scoped fixes, then rerun the exact combined command below on the resulting candidate. N01 made no source fixes.
- Required RESUME/AGENTS/STATE/ROSTER/BRIEF/REQUEST/WORKLOG/design/plan/dependency-gate records read. Prior dependency-gate findings and tester A/B preparation reports read; historical parity/coercion/heatmap/sampling fixes are not being re-reported as new defects.

## Executed identity checks

1. PowerShell structured `git status --short --branch`, `git log -8 --oneline`, `git worktree list --porcelain`: exit 0. Main already advanced to `b6abc8d`; ingestion preserved at `6c412e0f6be7e96a24a7f6c5cbcfdba9a48ef2c5`, renderer at `420a956788c9b78529d3348650a32913090f5671`. Ingestion clean; renderer has only untracked `examples/`.
2. `git rev-parse HEAD`, `git rev-parse 'HEAD^{tree}'`, per-source SHA-256 read-back: Git/hash steps succeeded. Source SHA-256: `normalize.py=5ee60ef4a86a3d22b44f43cb7d072953879ee0edb44955fbdc1a932fbc907a0f`; `render.py=b397f65a44305919f4fdc94cd0b8d62aff2b1f939104c844c46d47f0a161f1fa`; `engines.py=809fbc884059451489a2acc3a595796c2341155eb4a2e92e58943acd3913a028`.
3. Import-identity probe with `.venv/Scripts/python.exe`, absolute candidate `PYTHONPATH`, and `PYTHONDONTWRITEBYTECODE=1`: exit 1. Reviewer probe incorrectly assumed `deepviz.normalize` was a module attribute, but the package exports a function with that name (`AttributeError: 'function' object has no attribute '__file__'`). This is a probe error, not a product failure; no tests ran. Next probe uses `importlib.import_module` explicitly.

## What this change does

The integrated pipeline accepts heterogeneous data, reduces it into bounded rows, and compiles those rows for five chart engines. This independent review checks whether numeric meaning, partial-data warnings, stream replay, and resource disclosure survive those boundaries.

## Must fix — independently reproduced

All line numbers below refer to the first observed integrated source/hashes above. Reproducer file: `docs/coordination/evidence/N01-data-review-20261127/test_independent_data.py`. These are findings on that source, not claims that concurrent fixes are absent.

1. **P1: Count heatmaps draw zero rather than observed frequencies** (`python/deepviz/src/deepviz/engines.py:55-60`, normalizer `:421-428`).
   - What this is: with `kind=heatmap,x=day,y=region` and no color field, normalization correctly produces `count` for every coordinate pair.
   - Problem: the compiler reads the categorical y coordinate as `_heat` and converts it to zero. Two North rows and one South row normalize to counts `[2,1]`, but Plotly/ECharts/Vega/AntV native colors are `[0.0,0.0]` without warning. Four independent assertions fail; explicit color control passes.
   - Fix: resolve the heat measure consistently with the normalizer, selecting generated `count` when color is absent instead of y. Add a renderer-level no-color heatmap test.
   - If skipped: ordinary frequency heatmaps display false uniform zero intensities across all five adapters sharing `channels` (four native specs executed; Matplotlib visually confirmed below).

2. **P1: Missing numeric observations silently become measured zeros** (`engines.py:39-44,55-59`).
   - What this is: a line with y values `[7,None,9]` should preserve the missing point as a gap, as required by architecture §3/§6.
   - Problem: normalization preserves null, but the renderer's `_number(None)` default changes it to `0.0`; Plotly receives `[7.0,0.0,9.0]` and no warning. The same coercion affects distribution summaries and other engines via the common helper.
   - Fix: preserve missing/non-numeric numeric encodings as null or explicitly omit them with disclosed counts, and make geometry/statistical helpers handle missing values rather than fabricating zero.
   - If skipped: charts assert a false crash to zero, and box/violin statistics can include invented measurements.

3. **P1: Automatic scalar histograms bin synthetic row positions** (`engines.py:49-55,86-95`).
   - What this is: scalar input `[10,10,10,20]` has supported normalized `index,value` records.
   - Problem: `kind=histogram` infers x=`index`; `_histogram` preferentially bins numeric x. Observed bin centers `[0.75,2.25]` and counts `[2,2]` describe positions `0..3`, not observation centers `[12.5,17.5]` and counts `[3,1]`. Explicit x=`value` control passes.
   - Fix: recognize synthetic scalar index/value records in histogram channel resolution, or otherwise select the observation measure before binning.
   - If skipped: changing values without changing input length may leave the displayed histogram unchanged.

4. **P1: Dashboard replay changes supported Decimal measures into strings** (`python/deepviz/src/deepviz/render.py:49-56`, normalizer `:343-344`).
   - What this is: ordinary normalization supports `Decimal` as numeric input, including values `2.5` and `3.5`.
   - Problem: the same dashboard renders list input with sum `6.0`, but `iter(rows)` with the same spec sums to null. JSONL replay uses `default=str`, changing Decimal types before child normalization. Both dashboard artifacts were actually generated with ECharts; the manifest assertion fails.
   - Fix: replay a lossless supported scalar representation (or normalize supported scalar types before writing), and reject unsupported values rather than silently stringifying them.
   - If skipped: merely changing a source from list to iterator changes chart numbers; source streaming and materialized inputs are not semantically equivalent.

5. **P2: Selecting data_path suppresses GraphQL partial-error disclosure** (`normalize.py:383-392` versus `:282-285`).
   - What this is: a GraphQL response may include usable data plus errors, which the normalizer otherwise explicitly warns about.
   - Problem: response `{'data':{'users':{'nodes':[{'id':1}]}},'errors':[{'message':'second page unavailable'}]}` emits a partial-error warning without data_path. With `data_path='data.users.nodes'`, the same row is returned and warnings are empty because extraction discards the envelope before error accounting.
   - Fix: account for GraphQL envelope errors while traversing/selecting source pages, before path extraction removes metadata.
   - If skipped: the explicit path needed for ambiguous responses makes known partial data appear complete.

## Independent reproduction result

Command (PowerShell environment set `PYTHONDONTWRITEBYTECODE=1`, absolute candidate `PYTHONPATH`):

```powershell
& .venv/Scripts/python.exe -m pytest docs/coordination/evidence/N01-data-review-20261127/test_independent_data.py -q -p no:cacheprovider --basetemp C:/Users/bagma/AppData/Local/Temp/opencode/N01-data-review-20261127-pytest
```

Exit **1**: **8 failed, 2 passed, 0 skipped in 0.49s**. Four failures are engine variants of finding 1; remaining failures reproduce findings 2–5. Passing controls: explicit heatmap color and explicit scalar histogram field. Failure logs were returned directly by the tool; verification artifacts are in the N01-owned paths above. Corrected import-identity probe exited **0**, selecting candidate `__init__.py`, models, normalize, render, and engines under the main checkout with Python **3.12.16** (`.venv/Scripts/python.exe`).

Earlier checkpoint after initial reproduction: saved findings before proceeding to real static output and bounded parsing/statistics checks. Those next actions were subsequently executed below. No production or Git edits made.

### Existing scoped regressions rerun

```powershell
& .venv/Scripts/python.exe -m pytest python/deepviz/tests/test_normalize.py python/deepviz/tests/test_aggregation_semantics.py python/deepviz/tests/test_graphql_contract.py -q -p no:cacheprovider --basetemp C:/Users/bagma/AppData/Local/Temp/opencode/N01-data-review-20261127-baseline
```

Same interpreter/import environment. Exit **1**: **1 failed, 124 passed, 0 skipped in 4.25s**. This includes the existing generator/high-cardinality tracemalloc controls and installed Arrow/Parquet/IPC tests; their pass does not establish 10M scale or a byte bound. Existing independent test `test_sum_preserves_small_residual_under_large_cancellation_with_documented_tolerance` fails: float sequence `[1e16,1.0,-1e16]` returns `0.0`, independent `math.fsum` oracle gives `1.0`; integer control returns `1`. Root source `normalize.py:497-498` uses naïve repeated addition. **Additional P2 numerical-accuracy finding (not N01-authored original test):** use bounded compensated accumulation for sums (and derive robust mean consistently), with the existing test retained. C17/ingestion owner must resolve or explicitly document a deliberate tolerance policy; the current suite is red.

## Actual visual and resource evidence

Command: `.venv/Scripts/python.exe docs/coordination/evidence/N01-data-review-20261127/probe_artifacts.py` with the same import/bytecode environment and N01-owned `MPLCONFIGDIR=C:/Users/bagma/AppData/Local/Temp/opencode/N01-data-review-20261127-mpl`. Exit **0** (diagnostic generation, not passing acceptance). `artifact-evidence.json` records full paths, counts, warnings, source hashes, SHA/tree before and after; source remained **b6abc8d / 8bf9b428** and all four module hashes were unchanged throughout generation.

Opened and visually inspected all three real Matplotlib PNGs (900×520), not merely their existence:

- `docs/coordination/evidence/N01-data-review-20261127/figures/count-heatmap/deepviz-ou24z73t/chart.png`: both North/South squares have the same zero color; colorbar is approximately −0.1..0.1 despite source counts 2 and 1. Finding 1 is now also visually reproduced in the fifth engine. Artifact warnings empty.
- `.../figures/missing-line/deepviz-eyx9xhzd/chart.png`: a V-shaped line visibly falls from 7 to a marker at zero at t=1, then rises to 9. Finding 2 visually confirmed; expected missing gap absent. Artifact warnings empty.
- `.../figures/scalar-histogram/deepviz-0l7v5zsi/chart.png`: two bars of height 2 span 0..3 even though the actual observation values are 10,10,10,20. Finding 3 visually confirmed. Artifact warnings empty.

Matching SVG/HTML/manifests were generated in each directory. PNGs were opened; no browser run or visual SVG-specific inspection is claimed.

**Existing resource risk R5 concretely confirmed, not counted as a newly discovered issue:** one table row with a **2,097,152-byte** string cell is fully retained with `max_points=10` and **no warning**. This is a small byte-policy probe, not an exploit, memory benchmark, or claim of unbounded row-state growth. The normalizer bounds rows/keys/depth but not cell/total bytes. The artifact evidence records lengths rather than storing the long input. Owner/security/performance lanes must set or document the byte envelope; row caps alone are not a byte bound.

## Independent positive controls (not release signoff)

Command: `.venv/Scripts/python.exe -m pytest docs/coordination/evidence/N01-data-review-20261127/test_independent_controls.py -q -s -p no:cacheprovider --basetemp C:/Users/bagma/AppData/Local/Temp/opencode/N01-data-review-20261127-controls`, with the same candidate import/bytecode environment. Exit **0**: **10 passed, 0 skipped in 7.46s**.

- A one-shot **100,000-row** stream with unique group keys retained exactly **10 rows**, conserved exact integer total **4,999,950,000**, and disclosed the other bucket. Tracemalloc started immediately before normalization and reported peak **218,370 bytes** of **Python-traced allocations** for that probe. This is not process/native RSS, includes neither caller-owned preexisting data nor renderer memory, and does not establish the 1M/10M tiers or wide-cell byte bounds.
- CSV BOM, CRLF, quoted embedded newline/quotes, leading-zero identifier preservation, and Infinity→null warning matched independent expected records.
- JSONL TextIO GraphQL pages preserved all nonnull rows and disclosed the skipped null node.
- Plain URL/path-like strings did not invoke `Path.open`; model execution/remote-source extra fields were rejected; ToolSession without configured data_dir rejected explicit file references and path text.
- Hostile title/category/series strings containing script terminator, img/event markup and Unicode line separators stayed serialized data in ECharts/AntV HTML. An independent HTML parser observed no injected img element and recovered the exact native JSON payload. This tests template/script-context containment, **not browser execution, third-party tooltip behavior or a complete XSS audit**.

## Limits

- Candidate integration is concurrent; current checked source may not be the final candidate. No final release signoff.
- No full Python/npm/remote CI/build/package gate run by N01; no Git writes, dependency installs or source edits.
- No 10M performance claim, peak RSS measurement, browser execution, real MCP transport, broad XSS penetration test, or PNG pixel-exact baseline comparison from this lane.
- Static PNGs were visually inspected for findings 1–3; four browser-engine native specs were evaluated without launching those engines in a browser.

## Final combined reproduction and handoff

Read back the updated C17 report: the complete baseline is explicitly `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`, not the incomplete assignment base. N01's checks and visual artifacts used that integrated candidate; a later fixed candidate requires a new run.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = 'C:/Users/bagma/deepviz-agent-toolkit/python/deepviz/src'
& .venv/Scripts/python.exe -m pytest python/deepviz/tests/test_normalize.py python/deepviz/tests/test_aggregation_semantics.py python/deepviz/tests/test_graphql_contract.py docs/coordination/evidence/N01-data-review-20261127/test_independent_data.py docs/coordination/evidence/N01-data-review-20261127/test_independent_controls.py -q -s -p no:cacheprovider --basetemp C:/Users/bagma/AppData/Local/Temp/opencode/N01-data-review-20261127-final 2>&1 | Tee-Object -FilePath docs/coordination/evidence/N01-data-review-20261127/final-pytest.log
exit $LASTEXITCODE
```

Fresh combined result: exit **1**, **9 failed, 136 passed, 0 skipped in 21.43s**. All five N01 findings and the preexisting independent floating-sum residual failure reproduce together. The warmed-process 100K tracemalloc probe reported **96,616 bytes** (earlier isolated-control run 218,370 bytes); this difference is reported, not hidden, and neither number is total process RSS. Full failure log saved at `docs/coordination/evidence/N01-data-review-20261127/final-pytest.log`.

**Verdict: fix findings 1–5 and resolve the existing numerical-accuracy regression before acceptance.** No source/Git/remote modifications, spawning, final-candidate approval, or issue closure performed by N01. Byte/disk resource envelope remains an explicitly open cross-lane gate, not a new invented issue count.

### Final source continuity and fresh handoff check

- `final-identity.json` (structured Git/status/hash read-back, exit0) confirmed the four reviewed production module hashes unchanged from the initial review. It also observed concurrent dirty test files; N01 did not write them.
- Inspected `git diff` for the three executed existing test modules: each change was exactly one blank line separating pytest from deepviz imports. C17 then committed those import-group-only changes as **`d4ee4e8c19aa80b5257ce8adecb9cb268f7a23a9`**, tree **`b0b628b280504a24bf11ca6f6058ce12985b934d`**.
- An attempted `git diff -- <three test paths> | Tee-Object .../final-reviewed-tests.diff` produced no file because that concurrent commit had already cleared the working-tree diff; subsequent `Get-FileHash` emitted a nonterminating missing-path error (outer PowerShell exit0). This is an evidence-capture race, not a product failure or a passing hash check. No nonexistent diff artifact is relied on.
- Corrected bounded comparison, `git diff b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835 -- <four reviewed production modules>`, returned **no changes**. Comparing the three test modules against that same baseline showed only those blank lines. Full comparisons, final dirty state, SHA and tree are saved in `handoff-identity.json` (exit0). The remaining dirty paths were recovery/config/coordination records, not reviewed product source.
- Fresh independent rerun after observing **d4ee4e8**:

```powershell
& .venv/Scripts/python.exe -m pytest docs/coordination/evidence/N01-data-review-20261127/test_independent_data.py docs/coordination/evidence/N01-data-review-20261127/test_independent_controls.py -q -p no:cacheprovider --basetemp C:/Users/bagma/AppData/Local/Temp/opencode/N01-data-review-20261127-d4ee4e8 2>&1 | Tee-Object -FilePath docs/coordination/evidence/N01-data-review-20261127/handoff-pytest.log
exit $LASTEXITCODE
```

Same absolute candidate PYTHONPATH and bytecode-disabled environment. Exit **1**: **8 failed, 12 passed, 0 skipped in 16.71s**. All five original N01 findings persist; the ten independent positive controls and two explicit-mapping controls still pass. Historical combined/visual evidence remains applicable only to these explicitly unchanged four production modules; no future source revision is approved by continuity assumption.

**Owner handoff:** N05/renderer resolves findings 1–4; N04/ingestion resolves finding5 plus the existing numerical residual failure. N17/security/N11/performance should disposition the already-recorded byte/disk-envelope risk. C17 decides integration/issue mapping; N01 has no authority to edit their source or close issues. Ready for a later exact-candidate independent retest; no execution blocker prevented this bounded review.
