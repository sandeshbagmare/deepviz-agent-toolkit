# Python release verification

`chart-contract.yml` remains the existing focused ChartSpec check.
`python-release.yml` is the full Python release workflow. It must be integrated
after its listed implementation, test, browser, scale and packaging files land.
Missing commands or files fail the workflow. A green focused ChartSpec run does
not satisfy the Python release gate.

The workflow runs on pushes and pull requests targeting `main`, plus manual
dispatch. It checks out the exact PR head or push SHA and records the checked-out
SHA in artifacts. Rebase and rerun after dependencies merge; approvals or test
evidence from an earlier SHA do not apply to a new head.

## Python matrix and package checks

Python 3.11, 3.12 and 3.13 each run:

```sh
python -m pip install -e '.[dev,agents,columnar,mcp]'
python -m ruff check .
python -m mypy
python -m pytest -q --strict-markers --junitxml=artifacts/tests.xml
python -m pytest -q --strict-markers \\
  python/deepviz/tests/test_normalize.py python/deepviz/tests/test_n19_formats.py \\
  -k 'arrow or columnar or parquet' --junitxml=artifacts/columnar.xml
python -m build
python -m twine check --strict dist/*
```

The focused Arrow/Parquet selection must execute at least one test and record
zero skips with PyArrow installed. The full suite is unfiltered and includes all
unit, integration and scale-marked tests. No external model or hosted-service
credentials are used.

For both the wheel and sdist, each Python matrix job creates a fresh venv outside
the checkout and installs the artifact with base, `[columnar]`, and `[mcp]`
requirements resolved by pip. Isolated Python probes verify imports come from the
venv, resources/schema and `py.typed` are present, normalization and Matplotlib
produce real output, and installed `deepviz`/ `deepviz-mcp` commands start. The
base consumer verifies Arrow use gives an actionable extra-install error and that
optional packages are not installed. The columnar consumer runs the actual
normalization/format tests with zero skips and exercises Arrow Table and Parquet
input. The MCP consumer runs the actual CLI/MCP tests with zero skips, including
the stdio client/server path. A separate wheel consumer installs `[agents]`,
runs all of `test_tools_api.py` with zero skips, and verifies lazy imports in the
base install.

## Local tool, safety and browser acceptance

The Python 3.12 release-evidence job runs these repository paths directly:

```sh
python examples/multi_tool_flow.py --output-dir artifacts/tool-flow
python -m pytest -q --strict-markers \\
  tests/test_mcp_cli.py tests/test_release_security.py \\
  python/deepviz/tests/test_tools_api.py --junitxml=artifacts/safety.xml
```

The example executes local normalization, recommendation and all five renderer
tools without a model. The test files exercise actual stdio MCP and CLI behavior,
artifact retrieval, resource limits, callback boundaries and unsafe input/path
handling. Browser acceptance uses Playwright 1.65.2 with its matching Chromium and runs
`python -m pytest -q --strict-markers python/deepviz/tests/test_browser_acceptance.py`
with `DEEPVIZ_BROWSER_TESTS=1`, local Chromium, and offline-runtime routing.
It downloads ECharts 5.6.0 and AntV G2 5.4.8 runtime files from fixed jsDelivr
URLs, verifies their SHA-256 hashes, then runs chart, dashboard and failure
scenarios without allowing browser network access. Screenshots and browser
observations are retained as workflow artifacts.

This browser suite currently covers ECharts and AntV G2. It is not a blanket
visual certification of Matplotlib, Plotly and Vega-Lite or every chart type.
Independent QA must inspect each in-scope engine's actual artifacts on exact
merged `main` and record results in
`context/release-0.1.0/16-feature-verification.md`.

## Streaming scale evidence

A separate Python 3.12 job runs the accepted generated-stream harness:

```sh
python scripts/verify_python_scale.py \\
  --source-root "$GITHUB_WORKSPACE" \\
  --counts 10 1000 100000 1000000 10000000 \\
  --cases sample sum mean --max-points 2000 --timeout 900 \\
  --output artifacts/python-scale.json
```

The harness starts a fresh process for each count/reducer case, verifies full
one-pass consumption and independent sample/sum/mean oracles, records elapsed
time and the platform's actual RSS measurement method, and refuses to overwrite
evidence. Its current acceptance checks the results and records memory; it does
not enforce a memory ceiling. No performance limit or native-memory claim may be
reported from this harness unless separately implemented and verified. The
workflow timeout is six hours because the ten-million-row cases run sequentially.

## Permissions and retained evidence

Every job has `contents: read`; checkout disables credential persistence. Pip's
download cache is keyed to `pyproject.toml`, while each consumer install uses a
new virtual environment. Workflows use unprivileged `pull_request`, no secrets,
no OIDC, no write permissions, and no publishing. JUnit logs, built packages,
scale JSON, browser screenshots and observations upload for 14 days even after
failures. Uploads support review and do not turn failed checks green. Link durable
reports to the PR and tracker before temporary artifacts expire.

The workflow pins official GitHub Actions to these verified commits:

- `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1)
- `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` (v7.1.0)
- `actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9` (v7.0.2)

The existing focused contract workflow remains unchanged. TypeScript/npm is
deferred under the approved Python-only 0.1.0 scope and has no CI jobs here.
