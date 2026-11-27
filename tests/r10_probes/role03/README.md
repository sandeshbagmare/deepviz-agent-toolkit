# Independent ECharts numeric-x controls (R10 role03)

These new tests use the public Python renderer and a separate literal-coordinate
oracle. They do not edit/import the existing acceptance-matrix oracle, install
dependencies, or depend on saved screenshots/local machine paths.

From the repository root with project dependencies already installed:

```powershell
$env:PYTHONPATH = "$PWD\python\deepviz\src"
python -m pytest tests/r10_probes/role03/test_echarts_numeric_x.py -q --strict-markers
```

The fixture **declares** the expected `value`, `category`, or `time` axis. The
oracle never trusts the generated axis to choose its expected result. Numeric
x stays numeric (including signed fractional values); literal numeric-looking
category labels stay strings; ISO timestamp strings require time rather than
category. Per-series exact coordinate Counters preserve duplicates and group
membership. Native HTML JSON and manifest must agree. Deliberately damaged local
copies prove changed types, values, multiplicity, axes and line/area geometry are
rejected. There are no mocks, xfails or dependency skips in the ordinary36 tests.

Optional **fresh** browser/SVG probe (existing Playwright and Chromium required):

```powershell
# First command: project interpreter with DeepViz dependencies. Output must be NEW.
python tests/r10_probes/role03/visual_probe.py generate artifacts/role03-fresh
# Second command: an already installed Playwright interpreter, same or different.
python tests/r10_probes/role03/visual_probe.py capture artifacts/role03-fresh/fixtures.json
```

The browser uses real declared CDN assets without interception/stubs; network is
required. Absence of tooling/network is a blocker, not a passing test. It checks
all six line/area × numeric/category/time combinations, records pinned runtime
bytes/hash/status, rejects browser errors, and compares actual SVG path vertices
to native mapped pixels within SVG four-decimal precision. Numeric/time x gaps
must have ratio2 for fixture deltas3 and6; categories must have ratio1. No
hardcoded screenshot pixel locations or old artifact-directory dependencies.

Run the original matrix separately to preserve its known checkpoint RED state:

```powershell
python -m pytest tests/test_acceptance_matrix.py -k 'test_engine_kind_theme_source_acceptance and echarts and (line or area)' -q
```

At checkpoint `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`, the new controls pass
but the original20 fail because they unconditionally stringify expected numeric
line/area x. Do not mark those tests xfail, delete their assertions, or force
quantitative source geometry to category just to satisfy them. Minimal owner
proposal: stringify only category expectations while independently requiring
value/time axes for the corresponding fixtures; retain exact mapped values and
multiplicity plus irregular-spacing controls. This branch is independent
checkpoint evidence, not final-candidate approval or a whole-repository pass.
