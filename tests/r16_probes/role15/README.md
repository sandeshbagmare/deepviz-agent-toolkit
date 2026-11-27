# Independent exact SUM tests — ec9f669 only

Non-author tests of source commit
`ec9f669eff28cd5351da142765b7755e3b2f484f`, not the older source on this evidence
branch. Create a **new, clean detached source worktree** at that commit. Keep this
test directory unchanged on the evidence branch. No dependency installs required;
use existing project Python/pytest and TypeScript7.0.2 tools read-only.

```powershell
$env:R16_SOURCE_ROOT = '<absolute clean detached ec9 source worktree>'
$env:PYTHONPATH = "$env:R16_SOURCE_ROOT/python/deepviz/src"
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
# From clean source worktree; dist must not already exist:
python -m pytest python/deepviz/tests/test_r07_finite_overflow.py -q --strict-markers -rs -p no:cacheprovider
tsc -p packages/deepviz/tsconfig.json
node --test packages/deepviz/test/test_r07_finite_overflow.test.mjs
# From this evidence worktree (same environment):
python -m pytest tests/r16_probes/role15/test_sum_independent.py -q --strict-markers -rs -p no:cacheprovider -o junit_family=legacy --junitxml=<fresh-output.xml>
```

Actual independent results: unchanged23Python pass2.37s, unchanged23Node pass889.057ms;
new17fixtures pass2.71s, all exit0/zero skips. Scoped Ruff/mypy and Node syntax pass.
Initial own dataclass-serialization harness errors are retained in the report,
not presented as product bugs. Production and existing tests were never edited.

The new oracle sums literal binary64 values exactly using `fractions.Fraction`,
then uses Python's independent float rounding. Inputs transported to Node must
preserve exact bits; outputs match expected binary64 bits. Fixed explicit group
memberships avoid copying candidate eviction logic.17fixtures cover ties around
an odd mantissa, subnormal residuals, positive/negative promotion, pre-promotion
compensation, late promotion, interleaved groups and other-bucket promotion before
and after eviction. Genuine unrepresentable finals separately require warnednull.

Each fixture exercises Python records/one-pass iterator and TS records/sync/async
streaming, with count/exhaustion/strategy/warning parity and finite JSON. These
are85mode executions inside17tests, **not85new tests or issues**. Max42inputrows.
One ordinary compensated control is not a universal correctly-rounded fastpath
claim. No new mean, full-suite, scale, performance, gallery or package checks.

Identity/outcomes: `docs/coordination/evidence/R16-15/`; detailed report:
`docs/coordination/reports/R16-15-sum-independent-test.md`.
