# Independent R30-05 owned-input lifetime acceptance

**PASS only at sealed `5ba860305dcc86ac2f95f01705b984d2b40f2799`.**
One fresh non-author run: **69 passed / 0 failed / 0 skipped**, pytest11.99s.
Split: unchanged producer5 + published independentR10 43 + independentR13 21.
PyArrow26.0.1 actually exercised; real Windows rename checks, no privilege waiver.

## Evidence

- `process-command.json`: exact executable/argv/CWD/exit/wrapper hash and raw log hashes.
- `pytest-command.json`: exact SAME-process pytest.main arguments/environment, no subprocess source substitution.
- `identity-before.json`, `identity-after.json`: all9Python source files+config+schema raw Gitblob exact; all3 original immutable tests. Own source imports, not MAIN/installed/producer.
- `before-case-origins.json`: all69 pre-case same-process normalizer/API object and code-origin guards.
- `strict69.xml`, `case-reports.json`, `collected.json`: complete actual outcomes/properties/collection, no xfail/skip/waiver.
- `verified-results.json`: independent saved-result readback; exact file-path classification5+43+21; owned close/Windowsrename, expected borrowed EIO locks, stage/input counts.
- `summary.json`, `strict69.stdout.log`: actual gate summary and stdout. Published stdout ONLY normalized CRCRLF/CRLF→LF; raw original retained and hashed in `raw-artifact-index.json`. Other exported raw files byte-identical to completed run.
- `audit-failures-and-limits.json`: two OWN read-only audit errors, actual messages/exits and saved-results-only correction; not product failures. Raw stdout/stderr of those two ad-hoc audit commands were returned in tool history, not separately logged; critical facts are preserved without inventing raw files.
- `publication-conversions.json`, `published-bytes.json`: actual Git text-newline differences and actual committed Gitblob SHA256s. Raw artifact copies above are byte-exact **before Git**; any NEW evidence CRLF→LF change during publication is explicitly distinguished. Original source/oracles and executed wrapper stay untouched.

## One-run recipe (already completed; do not replay for this handoff)

Read frozen source and immutable files/reports first. `PIN` is hardcoded in the
wrapper and must be5ba. Use a clean exact detached source and a NEW nonexistent
artifact directory; wrapper refuses reuse and stale source/oracle bytecode.
No npm/TS/distribution build or dependency installation is needed for this gate.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH="$SRC\python\deepviz\src"
Remove-Item Env:PYTEST_ADDOPTS -ErrorAction SilentlyContinue
& "$MAIN\.venv\Scripts\python.exe" -B -S `
  "$PUB\tests\r30_probes\role05\run_owned_lifetime.py" `
  --source $SRC --oracles $READONLY_ROLE15_TREE `
  --site-packages "$MAIN\.venv\Lib\site-packages" --artifacts $NEW_ARTIFACTS
```

Working directory is`SRC`; exact completed path values are in process-command.
`-S` avoids shared editable `.pth` imports; wrapper inserts ONLY explicit own src
and read-only installed site-packages before importing actual DeepViz in the
same process as pytest. All original test bytes are checked before import, and
public normalize function binding/connected origins are checked before each case.

## Scope/limits

Owned reducer late-error resources close before caller observes the retained
traceback, including CSV/JSONL/Arrow/Parquet at input256/prefix32; owned EIO48
also closes. Borrowed EIO inputs intentionally remain open, with actual Windows
WinError32 lock until caller cleanup; borrowed stream/future Arrow batch0256 is
usable. EIO is deterministic test injection, not a physical-disk-failure claim.
Finite270row/≤18MiB fixtures are not scale/RSS/performance measurements.

No production/existing-oracle/config/installation/API/shared-branch/spawn edits.
No old helper/build/browser/fullsuite517/npm/scale/consumer/matrix replay.
This is an independent **tester** gate, not03/04 source review, later dirty mean
or GraphQL validation, final extracted foundation approval, green CI or release.
R04 must apply affected gates to the actual dependency-complete extracted head.
