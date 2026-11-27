# Owned-input lifetime regressions (intentionally RED)

Source checkpoint: `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`. These NEW tests do not
change the normalizer or existing tests. They preserve strict R03-15-F1 cleanup
acceptance and add error-phase/carrier and caller-owned-stream controls.

From the repository root with the project's existing Python environment:

```powershell
$env:PYTHONPATH = (Join-Path $PWD 'python/deepviz/src')
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest tests/r10_probes/role15/test_owned_input_cleanup.py -q --strict-markers -rs --tb=short -o junit_family=legacy --junitxml=owned-cleanup.xml
```

POSIX equivalent: `PYTHONPATH=python/deepviz/src PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/r10_probes/role15/test_owned_input_cleanup.py -q --strict-markers -rs --tb=short -o junit_family=legacy --junitxml=owned-cleanup.xml`.

Choose a new output path on every run. Arrow/Parquet cases precisely skip when
optional `pyarrow` is unavailable; no dependency installation is performed by the
tests. Actual execution used pyarrow26.0.1 with **zero skips** on Windows/Python3.12.16.

Published-version outcome: **30 passed / 13 failed / 0 skipped**, exit1,1.91s.
Eleven failures leave owned handles open after downstream errors; every one also
records an actual WinError32 rename lock. Two failures prematurely close borrowed
JSONL streams (StringIO and caller-opened real file). The first-line parse control
and remaining positive controls pass. These are ownership-work-item manifestations,
not thirteen separate issue claims. No xfail/weakening hides the failures.

The `.closed` oracle is portable; actual Windows rename impact is additional
evidence, not a claim about POSIX deletion semantics. Tests retain caught traceback
references and close only their captured synthetic resources after observations.
No garbage collection, private normalizer cleanup, or production monkeypatch is
used to make the strict assertions pass. Acquisition wrappers observe real files.

R04/16 owns the normalizer fix. Require all owned-error handles closed AND all
borrowed streams usable before declaring GREEN. See the role report and compact
evidence under `docs/coordination/` for exact provenance and limitations.
