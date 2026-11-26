# Verification and integration handoff

## Scope and implementation plan

This implements task 5 of `docs/superpowers/plans/2026-11-26-deepviz-plan.md`
and its design's verification requirements, without owning the package build
configuration, generated schema, normalization or renderer implementation.

1. Test deterministic schema export and stale/missing-schema rejection.
2. Test the negative controls for evidence, raster geometry and streaming counts.
3. Add read-only, SHA-pinned Python/Node/visual/scale/distribution workflows.
4. Add honest issue/PR evidence templates and an opt-in declaration validator.
5. Validate scripts/configuration locally; run integrated jobs after other branches land.

Ruling: use semantic raster geometry instead of a font-sensitive screenshot
baseline. Four real Matplotlib bar PNGs cover two value orders and both themes.
Saturated mark pixels must match an independently computed bar silhouette with
intersection-over-union >= 0.94. Empty images, changed bar order/heights/count,
and wrong theme backgrounds fail. Text/gray pixels are intentionally excluded;
this is not a claim to verify every label or every renderer.

Ruling: `evidence-required` is opt-in for bootstrap. When set, the declaration
gate requires a same-repository issue URL, embedded image, correctness explanation,
four distinct reviewer/tester session IDs, report URLs, and reports for the current
PR head SHA. It checks declaration structure, not report truth, identity authenticity,
issue existence or GitHub human approvals. Maintainers must inspect the actual
reports. Never use a green bootstrap run as independent evidence. The workflow uses
`pull_request`, not privileged `pull_request_target`, and never injects PR text into shell.

## Parent integration requirements

- Keep Python >=3.11, the `dev`, `agents`, `mcp`, `columnar` extras and
  pytest `integration`/`scale` markers. Install all integration dependencies;
  no API keys or live hosted services are needed for the tests.
- Generate and commit the parent-owned schema with
  `python scripts/export_schema.py`. CI's `--check` never changes it. The JSON
  artifact is the literal `ChartSpec.model_json_schema()` export; Python's
  dashboard validators remain additional semantic checks, not JSON Schema rules.
- Supply root `package.json` and committed `package-lock.json`, workspace
  `@deepviz/agent-toolkit`, and root scripts `build`, `typecheck`, `test`,
  `test:browser` and `package:check`.
  CI deliberately does not use `--if-present` or auto-create a lockfile.
- Node 24 must be compatible with that lockfile and package engine constraints.
  Every Python matrix job also builds the npm package before its required parity
  tests; the separate Node job does not share its filesystem with Python jobs.
- `normalize(iterable_of_records, spec)` must consume a generator once, report the
  entire input count, and sample to `min(input_count, max_points)` records with
  `aggregation='sample'`. Reduced results must explain their lossy strategy.
- `render(data, ChartSpec(...), engine='matplotlib', output_dir=Path(...))`
  must return `Artifact`, including exactly one PNG per simple fixture. Its paths
  must be unique so the four fixtures do not overwrite one another.
- The Node job installs Chromium with
  `npm exec --no -- playwright install --with-deps chromium` and runs
  `npm run test:browser` against locked local renderer assets. Browser console/page
  errors must fail that suite; never add `--if-present` or continue-on-error.
  This complements the separate strict real-image raster regression gate.
- The distribution job installs the built wheel and dependencies into a fresh
  virtualenv, checks its import prefix, both versioned prompts, schema, `py.typed` and console
  entrypoints outside the checkout. `npm run package:check` packs and installs a
  real tarball and checks public runtime, JSON exports and TypeScript declarations;
  a successful metadata check or pack dry-run alone is insufficient.

## Local commands after integration

```text
python -m pip install -e ".[dev,agents,mcp,columnar]"
npm ci
npm run build
python scripts/export_schema.py --check
python -m ruff check . .github/tests
python -m mypy
python -m mypy scripts/export_schema.py scripts/verify_evidence.py scripts/verify_visual.py scripts/verify_scale.py
python -m pytest .github/tests -q --strict-markers
python -m pytest -m "not integration and not scale" --strict-markers
python -m pytest -m "integration and not scale" --strict-markers
python scripts/verify_visual.py --output artifacts/visual
python scripts/verify_scale.py --count 10 --output artifacts/scale-10.json
python scripts/verify_scale.py --count 1000 --output artifacts/scale-1000.json
python scripts/verify_scale.py --count 100000 --output artifacts/scale-100000.json
python scripts/verify_scale.py --count 1000000 --output artifacts/scale-1000000.json
python scripts/verify_scale.py --count 10000000 --output artifacts/scale-10000000.json
python -m build
python -m twine check --strict dist/*
npm run typecheck
npm test
npm exec --no -- playwright install --with-deps chromium
npm run test:browser
npm pack --dry-run --workspace @deepviz/agent-toolkit
npm run package:check
```

Use a fresh result filename per scale run; the script refuses to overwrite old
evidence. The Linux scale job enforces a 512 MiB process-lifetime peak RSS ceiling
and a 512 MiB traced Python-allocation ceiling in a fresh process per scale.
`tracemalloc` excludes native allocations and adds timing overhead; Linux
`ru_maxrss` includes interpreter/import/native memory. Windows reports traced
Python memory only, explicitly, not a fabricated RSS figure. Time is observed,
not asserted against an uncalibrated machine-specific performance baseline.

## Action provenance and permissions

Action SHAs were resolved on November 26, 2026 with `git ls-remote` against the
official `actions/checkout`, `actions/setup-python`, `actions/setup-node`, and
`actions/upload-artifact` repositories at the version tags in workflow comments.
Dependabot proposes updates. All workflows have only `contents: read`; checkouts
disable credential persistence. There are no publishing steps, secrets, OIDC,
write permissions or automatic approvals. Uploaded artifacts aid diagnosis and
never turn a failing command into success.

## Observed branch-only verification

The initial negative-control run failed because all four scripts and the generated
schema were absent. After implementation, the gate tests plus schema tests other
than the parent-owned checked-in artifact passed (28 passed, one deselected).
The unfiltered default `python -m pytest -q` run reported 16 passed and one failed:
`test_checked_in_schema_matches_python_contract`, because the parent-owned schema
is absent on this branch. It is deliberately not skipped or auto-generated.
Ruff, package/verification-script mypy, YAML parsing, and
actionlint 1.7.12 passed locally. Actionlint's Windows archive was checked against
the SHA-256 digest published on its official release before execution.

Provisional smoke checks used the render/core agents' in-progress source directories
on `PYTHONPATH`, not an integrated release commit: four actual PNG fixtures had
silhouette IoU 1.0. A 1,000-record generator was fully consumed with 1,000 output
records; a 100,000-record generator produced 2,000 sampled records, disclosed the
lossy strategy, took 5.293 seconds under tracing, and peaked at 0.703 MiB of traced
Python allocations. Native allocations were not measured on Windows. These checks
cannot establish the final integrated commit's correctness.
Full package/renderer/streaming/npm checks must run after integration. Record the
exact integrated source SHA in `GITHUB_SHA` for local visual/scale evidence; CI sets
it automatically. Local Windows/Python 3.12.16 checks do not establish Linux RSS
or Ubuntu's Python 3.11/3.12/3.13 matrix results.

The worker's final review is an author self-review, not an independent signoff:
nested reviewer dispatch was blocked by the session depth limit. The parent must
obtain the actual independent reviewer/tester reports required by repository policy.
