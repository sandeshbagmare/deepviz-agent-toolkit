# Independent strict numeric contract slice tests

This is a NEW, bounded tester suite for the execution-free ChartSpec contract.
It does not edit production code, workflows, existing tests, schemas or package
initializers. Expectations are caller-authored JSON literals, not inferred from
validation results. It tests the real selected model and its generated JSON
Schema together; a correct schema does not conceal a coercing model.

The initial preflight source is the immutable old model at
`e44f667ed494fa272f97792ef99942a364ebca24`, SHA256
`94824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170`.
There is no package initializer in that commit, so an explicit trusted-file
import avoids resolving the installed newer dashboard model accidentally.

## Run against one explicitly identified source

Using the existing environment with pytest, Pydantic and JSON Schema installed:

```powershell
$env:DEEPVIZ_R22_SOURCE_IDENTITY = '<unique-extracted-source>/identity.json'
$env:DEEPVIZ_R22_EXPECT_SOURCE = '<exact-source-commit-sha>'
$env:DEEPVIZ_R22_OUTPUT = '<NEW-unique-output-directory>'
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m pytest tests/r22_probes/role17/test_contract_slice.py -q --tb=short
```

The identity JSON records `product_source_sha`, `actual_model_path`, and
`source_files` entries with committed relative `path` and actual SHA256. The
model bytes must be verified against Git before creating that identity. Its
parent must contain the same-source `schemas/chart-spec.schema.json`.
The suite checks the actual module path/hash and saves actual model/schema and
loaded dependency provenance. It never imports installed `deepviz.models`.

Covered: defaults, five numeric fields, integer/integral-float boundaries,
width900.0 canonicalization, numeric strings, true/false, null/containers,
fractional numbers, out-of-range values, forbidden executable/remote/callback
keys, ordinary literal mapped text, model/schema agreement, and four oracle
calibration controls. Those controls deliberately use wrong expectations or one
weakened **local schema copy** and require the detector to fail; they are not
product defects or passes for corrupt schemas. No mock model, chart code
execution or remote fetching is involved.

An e44 baseline pass is **not actual focused-PR approval**. When R04 supplies
the real focused head, verify its source bytes and rerun these tests with that
head's independently created identity before making a PR-specific judgement.
This narrow schema slice requires no chart/browser output; it makes no rendering,
escaping, scale, full-suite, CI, release or 900-issue-completion claims.

This existing worker branch also contains unrelated historical work and known
COUNT regressions. Do not merge its whole branch into the focused #30 PR. These
NEW tests are independently run tester evidence; adopting an integration test
requires an explicit actual-head source-identity setup, not silently importing
the installed package or skipping a missing source identity.
