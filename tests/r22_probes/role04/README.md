# Independent owned-input unwind review (R22-04)

Target local partial-source commit: `5ba860305dcc86ac2f95f01705b984d2b40f2799`.
This is **not** author16's final handoff, source publication or release signoff.
No producer in-flight source is used, and no original test expectations change.

Use an exact clean detached5ba checkout and the existing dev venv, read-only.
Extract this byte-exact immutable original to an own ignored artifact directory:

`8a10108752567f6d0faac700240c4acf77b32556:tests/r13_probes/role15/test_reducer_source_ownership.py`

SHA256 must be `5a9ebaba4968381624d20f646afbd8105531be4bfd179fe56fa5accb7118314e`.
Only its four `test_reducer_state_guard_releases_owned_source_after_valid_prefix`
parameter nodes are selected, not the21case matrix. The unchanged87line author
`python/deepviz/tests/test_r17_normalizer_boundaries.py` runs once (5cases).

Set `PYTHONPATH` to `<5ba>/python/deepviz/src;<own>/tests/r22_probes/role04`,
`PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, and set absolute
`DEEPVIZ_R22_SOURCE_ROOT`, `DEEPVIZ_R22_EXTERNAL_CWD`,
`DEEPVIZ_R22_ORIGINAL_TEST`, `DEEPVIZ_R22_IDENTITY_RECEIPT`.
From the fresh unique external CWD run:

```text
<existing python> -m pytest -p provenance_guard -c <5ba>/pyproject.toml
  <5ba>/python/deepviz/tests/test_r17_normalizer_boundaries.py
  <immutable-original-copy>::test_reducer_state_guard_releases_owned_source_after_valid_prefix
  <own>/tests/r22_probes/role04/test_owned_unwind_review.py
  -q --strict-markers -rs --tb=short -o junit_family=legacy -p no:cacheprovider
  --basetemp=<unique-own-basetemp> --junitxml=<own-result.xml>
```

The plugin checks actual imported source realpaths/Gitbytes and exact author,
original test/config plus NEW fixture bytes before **and after in that same
pytest process**; CWD must match the external directory with no deepviz shadow.
It does not patch imports/source or fabricate a product result.

Nine independent controls use actual text files/Win32 rename+unlink, exact once
owned close and zero borrowed-close before explicit caller cleanup, late real
malformed CSV/JSONL causes, and same-object read/iterator exceptions. EIO is
explicit deterministic fault injection over a real file, not a physical disk
failure claim. Original reducer fixtures are finite270rows,≤18MiB/carrier and
exercise the real16MiB retained-state guard after32valid prefix rows; no cap
monkeypatch/private-reducer call, giant committed data, broad43/64replay or RSS
benchmark. Optional columnar dependencies must be separately disclosed if absent.
