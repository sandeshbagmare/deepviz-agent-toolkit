# R21 public recommendation fidelity

NEW independent task-level tests, not a replay of `test_integrations.py`'s six
kind-only recommendations or previous field/collision/aggregation suites.
Test target: clean immutable `7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6`.

With the existing dev environment (no install required):

```powershell
$source = '<clean exact 7bc checkout>'
$env:PYTHONPATH = Join-Path $source 'python/deepviz/src'
$env:DEEPVIZ_R21_SOURCE_ROOT = $source
$env:DEEPVIZ_R21_ARTIFACT_ROOT = '<own unique ignored artifact directory>'
python -m pytest tests/r21_probes/role04/test_recommendation_fidelity.py -q
python -m ruff check tests/r21_probes/role04
python -m mypy tests/r21_probes/role04
```

`DEEPVIZ_R21_TARGET` can explicitly identify a later exact source for an authorized
independent rerun; the default is7bc, never a moving MAIN. The autouse guard
verifies actual imported modules and immutable Git bytes. Publication can remain
on a different own test branch; no source copy/patch is needed.

The flow exercises public `ToolSession.normalize_data/recommend_chart`, recommended
spec normalization and real Matplotlib artists for five goals. Literal values,
names, dates, independent scatter pairs, histogram mass and pie proportions have
independent expectations. A real public static render uses the recommended spec
unchanged and an observation-only forwarder returns the actual figure untouched
to production `savefig`. Open the resulting PNG before any visual signoff.

Temporal input is already ordered; the recommendation explicitly requests review
of ordering/time semantics. Numeric IDs or mixed strings do not imply semantic
omniscience: the contract is bounded observed types plus editable review warnings,
not a perfect choice. Profile100-field/256-character limits and missing-measure
safety are checked through the public tool, including sentinel-value privacy.

No provider, model, LangChain execution, browser, CDN, other engine, source change,
large-scale memory or release certification is involved. Caller input and spec
must remain unchanged. Artifact loss/count warnings are checked, not hidden.
