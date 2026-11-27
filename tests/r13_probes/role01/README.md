# R13-01 independent bounded-SUM review oracles

Reviewed source: `ec9f669eff28cd5351da142765b7755e3b2f484f`.
Unchanged comparison base: `6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce`.
This is not a final-candidate approval. Only these NEW reviewer tests are added;
no producer source or existing test is modified.

`exact-cases.json` contains finite inputs and correctly rounded Fraction-oracle
outputs. `make_exact_cases.py` regenerates it independently of either reducer.
The two pre-promotion cases intentionally remain strict RED, not xfailed:

    [1e308,1e200,1,-1e200,1e308,-1e308,-1e308] -> expected 1, actual 0
    [1e308,1,5e-324,-1,1e308,-1e308,-1e308] -> expected 5e-324, actual 0

Ordering either multiset to overflow first preserves its exact residual. The
released base gave warned null for the same failing inputs, so this is a
remaining inherited accuracy limitation/partial fix, not a new precision
regression. R04 owns disposition; do not silently relax the oracles.

## Run against explicit local sources

Use an existing declared-dependency environment; do not install or alter source.
Build the selected reviewed and base TypeScript packages normally in their own
checkouts, including their schema asset. Set these process-local variables:

- `PYTHONPATH`: reviewed checkout `python/deepviz/src`.
- `R13_BASE_PYTHONPATH`: base checkout `python/deepviz/src`.
- `R13_TS_MODULE`: absolute reviewed `packages/deepviz/dist/index.js`.
- `R13_BASE_TS_MODULE`: absolute base `packages/deepviz/dist/index.js`.

Then run from a checkout containing these NEW files:

```text
python -m pytest tests/r13_probes/role01/test_sum_review.py -q --tb=short -p no:cacheprovider
node --test --test-reporter=tap tests/r13_probes/role01/sum-review.test.mjs
```

Python checks exact integer policy, direct internal state shape/charging and a
small monkeypatched retained-byte budget. These are reviewer probes, not a new
public `_Reducer` API contract. Node uses genuine async-generator sources.
Positive controls cover signed even/odd ties, deterministic post-promotion
Fraction cases, compensation carry, unchanged mean/sample outputs, true
nonrepresentable warning/null and complete bounded-fixture consumption.

The async count/output check does NOT measure heap/RSS or prove constant process
memory. The code review establishes one bigint/integer state and accounted
bounds; final-scale/process-memory acceptance remains unverified.