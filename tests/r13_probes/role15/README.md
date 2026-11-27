# R13 reducer failure / early-stop ownership (strict RED)

NEW tests, independent of the R10 field-validation cases. Requested source:
`5340bc69b7203ad7a9166543062482d819f9b705`. Reused own branch parent60599dd has
**byte-identical entire Python package source**, verified by:

```text
git diff --exit-code 5340bc69b7203ad7a9166543062482d819f9b705 HEAD -- python/deepviz/src
```

Use the existing project Python environment; tests never install dependencies:

```powershell
$env:PYTHONPATH = (Join-Path $PWD 'python/deepviz/src')
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest tests/r13_probes/role15/test_reducer_source_ownership.py -q --strict-markers -rs --tb=short -o junit_family=legacy --junitxml=r13-owned-result.xml
```

POSIX: prefix that command with `PYTHONPATH=python/deepviz/src PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.
Choose a fresh output path. Optional pyarrow absence precisely skips columnar cases;
actual execution used pyarrow26.0.1 and skipped **zero**.

**17 passed / 4 failed / 0 skipped,5.73s,exit1** on Windows11/Python3.12.16.
Four strict REDs are actual retained-state reducer guard failures at row256 after
32 valid inference rows, for CSV/JSONL/ArrowIPCstream/Parquet owned paths. Each
records `.closed=False` and WinError32 rename failure with retained traceback;
after explicit test-owned cleanup, rename succeeds. No xfail or guard monkeypatch.

Fixtures are finite270rows with legal65,520byte string keys (each file<18MiB).
One-group full-consumption controls use the same data volume but small state.
Borrowed text streams and Arrow reader must remain usable. Actual EIO is injected
deterministically at text reads after48validrows; it is not a physical disk fault.
Samplingmax_points10 must consume all64source rows, not stop at output limit.

This is one existing ownership-cleanup work item with new reducer/error-phase
acceptance, **not four new tickets**. Normalizers remain16-owned; no production
fix, previous-test replay, final approval, RSS benchmark or complete SDLC claim.
