# R13-13 — recovered CI gate-control publication and repair handoff

Status: RECOVERED / OWN PUBLICATION IN PROGRESS, 2026-11-27. Product CI remains unapproved.

## Recovery identity and boundaries

- SAME native session `ses_de56780caffekQ9gdZ58EgQwb5` reconfirmed in the EXISTING worktree `C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5`.
- Read full MAIN R13 common contract + role13, canonical/RESUME/STATE, OWN note/R10 report and R11/R12 ownership releases. Parent/reservation admission is dispatcher-provided; no worker spawning, new descendants, cancellation revival, source/oracle scope expansion or shared-branch mutation.
- Existing branch `agents/r10-13-ci-negative-controls` is clean at **`dedb41fa8df3fdb90b845eef7a10b5fa4032872c`**, parent **`3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`**. `git status --short --branch`, `git log -3 --oneline`, own `git ls-remote --heads origin refs/heads/agents/r10-13-ci-negative-controls` all exited0; remote branch absent at this one observation. No branch recreation/reset.
- Completed commands reconciled ONCE from saved receipts: run2 control command exit0, full suite command exit1; original full-suite background completion was already received and indexed. No command is marked in flight; no full-suite,31-control,scale/build replay or process polling is needed.
- Saved evidence remains **31 scoped passes** (15NEW+16existingCI) versus **36 full-suite failures /3019passes/5skips630.59s**,13intentionalchildexit1and5positiveexit0. N15sevenarchivalRufffindings stay distinct from clean checkpointRuff0. Original0c5baseline/note/evidence unchanged.
- Allowed: own note, R10 report/evidence publication plus this NEW R13report and `evidence/R13-13/`; existing scoped probes already committed. No production workflows/configuration/schemas/existing tests/dependencies/other evidence edits, installs, issues/PR writes or shared staging/pushes. R04 alone integrates. Full production and900genuinecreatedANDresolved issues unchanged/unmet.

## Next action / acceptance

1. Revalidate existing evidence/source hashes without rerunning tests, prepare exact failure-group/CI-prerequisite/skip-cause commands for eligible source owners.
2. Verify expected authenticated GET `/user` with GCM secret captured only in memory; one read-only currentPR/run/jobs observation, no polling. Root's13:47UTC5340PR31draft/Verification45928608970FAIL/evidence-success is reported context until independently observed.
3. Copy ONLY owned report/note/sanitized evidence into existing own branch, exact-path stage + full staged review/whitespace/credential scan, small meaningful checkpoint commit, non-force own push and actualremoteSHAreadback; record OWNMAINreceipt. No greenCI inference or self-signoff.

Current blocker: none for publication; product36failure groups and5skips remain unresolved final gates. Next executable action: validate saved raw-artifact hashes and protected-source diff, then save compact recovery evidence and executable handoff before publication.

## Recovery evidence — no test replay

Saved raw-log/XML hashes, gate/source files, loaded-module hashes, unchanged N15 bytes and completed command receipts were verified: **23 integrity checks /23 passed**, collector exit0. These are integrity checks, not new product-test passes. Evidence: [`recovery-integrity.json`](../evidence/R13-13/recovery-integrity.json). The original local full-suite log/XML remains under approved temp `r10-13-evidence-ses_de56780caffekQ9gdZ58EgQwb5/full-suite/`; it is not rerun or repackaged as fresh acceptance.

One bounded authenticated GET snapshot independently confirmed `sandeshbagmare`, PR31 open/draft/unmerged at **5340bc69b7203ad7a9166543062482d819f9b705**, **Verification45928608970 completed/failure**, and evidence-policy45928608969 completed/success. All three Python3.11/3.12/3.13 jobs failed at **Unit and contract tests**; integration steps were not successful runs. Lint/types/schema/gate-control prerequisites are distinguishable from unit-suite acceptance. No remote job log or per-test result was downloaded, so **local36 is not asserted as the remote failure count**. This is not a green CI, approval or closure. Exact UTC/status/steps: [`remote-prepublication.json`](../evidence/R13-13/remote-prepublication.json).

Read-only `git diff --exit-code 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab 5340bc69b7203ad7a9166543062482d819f9b705 -- scripts .github pyproject.toml schemas packages python/deepviz/src python/deepviz/tests` exited0. Thus those source/workflow/dependency/test bytes are equivalent between the tested base and published checkpoint, not a guess based on similar branch names. Own two NEW tests/recipe are in dedb41f only; no production fix is claimed.

## Exact gate-repair handoff (R04 / eligible owners only)

[`gate-repair-plan.json`](../evidence/R13-13/gate-repair-plan.json) contains all36 executable pytest node IDs (with `.py`), grouped below, prerequisites, skip causes and source identity. No group has been rerun during recovery.

| Group | Count / actual saved failure | Required disposition, not a blanket waiver |
| --- | --- | --- |
| ECharts native numeric x |20line/area cases; existing `assert_native_xy_values` unconditionally stringifies x for line/area |R04/role03: test numeric value-axis coordinates and unequal horizontal spacing; stringify only actual category axes. Keep categorical/time discriminators, exact data and browser semantics. Do not coerce renderer values to satisfy an obsolete oracle. |
| Vega dashboard titles |10cases; recursive child compilation checks the parent's title in every child SVG |R04/role17: pair native specs with child metadata/titles; inspect visible parent title once in composed output AND each child title/data/geometry/XSS controls. Do not drop title checks. |
| Field-name resource contract |4cases:3exact64KiBname variants +1flattened64KiBname |R04/role04: source has4KiB UTF8names versus64KiBcells. Resolve the declared contract without widening byte/state limits or truncating accepted content; current normalizers remain role16-owned until explicit handback. |
| AntV dashboard wrapper |1case; expected `line`, received top-level `view` |R04/role06: validate line+marker children, their exact measurements, unique independent containers and visible result; do not require raw top-level kind or weaken to arbitrary tag presence. |
| N17 serialization observation |1case; `serialized=[]` where historical test demands invalid >1MiBrow serialized before rejection |R04: preserve early field-count rejection and verify that unsafe row is NOT serialized/output, with valid-small-row controls. A historical observation of expensive work is not a requirement to reintroduce it. |

Production P1 allocation/data-loss/security corrections remain higher-priority retained lanes; this handoff grants **no** source/oracle/workflow edit authority. R04 must decide/test each contract correction rather than remove red cases or add `continue-on-error`.

### Executable focused replay recipe — NOT executed by this recovery

Run from an eligible clean candidate checkout after recording its SHA and the contract decision. Existing tests may still return1 before a legitimate correction. This script runs the36 exact saved node IDs in5groups and creates unique task-owned JUnit results; it does not install, change source or ignore failures.

```powershell
$py = 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe'
$env:PYTHONPATH = Join-Path (Get-Location) 'python/deepviz/src'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:MPLBACKEND = 'Agg'
@'
import json, subprocess, sys, tempfile
from pathlib import Path
root = Path.cwd()
plan = json.loads((root / 'docs/coordination/evidence/R13-13/gate-repair-plan.json').read_text())
out = Path(tempfile.mkdtemp(prefix='r13-13-replay-', dir=r'C:\Users\bagma\AppData\Local\Temp\opencode'))
head = subprocess.run(['git', 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
results = []
for group in plan['groups']:
    argv = [sys.executable, '-m', 'pytest', *group['nodeids'], '-q', '--strict-markers',
            '--junitxml', str(out / (group['id'] + '.xml'))]
    done = subprocess.run(argv, cwd=root, capture_output=True, check=False)
    (out / (group['id'] + '.log')).write_bytes(done.stdout + done.stderr)
    results.append({'group': group['id'], 'argv': argv, 'exit': done.returncode})
(out / 'receipt.json').write_text(json.dumps({'sha': head, 'commands': results}, indent=2))
print(out)
raise SystemExit(1 if any(item['exit'] for item in results) else 0)
'@ | & $py -
```

### CI prerequisites / skips / completion gate

- Intended fresh CI: Ubuntu, Python3.11/3.12/3.13, Node24; declared `python -m pip install -e ".[dev,agents,mcp,columnar]"`, then `npm ci` and `npm run build` **inside each Python job** before parity tests. These are recipes, **not installs executed by this worker**. Node job separately installs Chromium/system dependencies and runs browser tests; its filesystem is not shared with Python jobs.
- Required gates stay: `python -m ruff check . .github/tests`; `python -m mypy`; script-mypy on `scripts/{export_schema,verify_evidence,verify_visual,verify_scale}.py`; schema `--check`; CI control tests; unit `-m "not integration and not scale"`; integration `-m "integration and not scale"`. Run both partitions after fixing unit failures—Actions skips subsequent ordinary steps when the unit command fails. Use new unique JUnit paths and report actual counts/skips for each source.
- Two Windows1314skips are real symlink containment coverage gaps (`test_stdio_registered_artifact_symlink_swap_cannot_read_outside_output_root`, `test_n17_symlink_outside_data_directory_is_rejected`). Recheck on a symlink-capable host without claiming the Windows skip passed. Three native-kind browser skips are opt-in `test_browser_executes_all_native_kinds[plotly/echarts/antv]`; require `DEEPVIZ_BROWSER_TESTS=1`, installed compatible Python Playwright/Chromium and pinned CDN reachability. Installation/network absence is a precise blocker, never a browser pass.
- Dirty MAIN full-root Ruff retains7N15 archive findings. Isolated clean full-root Ruff passes without any exclude/ignore. Keep N15 original byte hashes, do not format/delete evidence, add a broad exclusion or call tracked-only lint full-root. R04 may declare a narrow archival policy separately; this worker makes no change.
- Remote evidence-policy success can be bootstrap or format validation; it is NOT two genuine reviewer/two tester final-source approval or proof every URL is safe/real. This branch has only author self-review plus real independent CLI execution, not non-author review of its own code.

Current action: copy only own note/reports/compact evidence into existing branch, review exact staged content and publish with non-force own-branch push + SHA readback. Next executable action: scoped copy/stage/review/sanitize; no repeat suites, auth change, remote issue/PR write or shared integration.
