# R10-01 strict correctness regressions

These NEW independent tests turn R03-01 findings into portable, reusable oracles.
They intentionally fail on source checkpoint
`3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`; they are not xfailed or relaxed.
Production source and existing tests are unchanged. This evidence branch is not
ready for candidate integration until the owning producer fixes the failures.

## Run from the repository root

Use an existing environment containing the project's declared test dependencies.
No dependency installation is required by these probes. Build this checkout's
TypeScript output with an already installed compiler (use its absolute path if
it lives outside the checkout):

```text
node node_modules/typescript/bin/tsc -p packages/deepviz/tsconfig.json
```

Set `PYTHONPATH` to this checkout's `python/deepviz/src`, then run:

```text
python -m pytest tests/r10_probes/role01/test_correctness_regressions.py -q --tb=short -p no:cacheprovider
node --test --test-reporter=tap tests/r10_probes/role01/correctness-regressions.test.mjs
```

PowerShell example: `$env:PYTHONPATH = "$PWD/python/deepviz/src"`.
POSIX example: `export PYTHONPATH="$PWD/python/deepviz/src"`.
Python's identity guard rejects an accidental sibling/installed source import;
Node imports only this checkout's freshly built package entry.

## Literal invariants and controls

- **F1:** unexpected siblings beside `nodes`/`edges` require explicit selection;
  they must not disappear from successful normalization. Tests include sync,
  genuine async-generator and encoded-JSON inputs. Valid metadata and explicit
  paths remain accepted. Custom GraphQL wrappers require an explicit path.
- **F2:** two observations count as **2**, not numeric series labels **0, 100 or
  -4**. Python shared channels and four native payloads must agree with the
  reduced count. Positive controls preserve explicit measure names, categorical
  series and heatmap y coordinates; the equivalent TS native payloads pass.
- **F3:** scalar columns named rows/records/items/results/data retain their names
  under explicit mapping. Arrays inside records retain their parent identity,
  rather than being confused with top-level column input.

Observed checkpoint result: Python **12 failed /21 passed /0 skipped**; Node
**11 failed /19 passed /0 skipped**. These are three finding families, not23
issues. Detailed source locations, exact commands, hashes and owner routing are
in `docs/coordination/reports/R10-01-correctness-regressions.md` and its evidence.
No browser paint, final-head approval, paid-provider call or issue closure is
claimed. R04 owns source integration; normalizers remain with16/R04 and shared
Python renderer mapping withR04.