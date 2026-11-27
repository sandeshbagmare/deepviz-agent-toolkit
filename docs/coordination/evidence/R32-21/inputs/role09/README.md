# Fixed helper-null retest replacement (verification code only)

This **NEW** recipe replaces future use of `tests/r13_probes/role09/retest-helper-null.ps1` without editing it or its immutable tests. Original R16-21 findings remain historical; independent 21 must retest this published replacement before treating the guard fixes as accepted.

## Fixed, explicit host invocation

```powershell
& .\tests\r22_probes\role09\retest-helper-null.ps1 `
  -Candidate '<clean isolated exact eligible-producer commit>' `
  -ExpectedSha '<actual full 40-character SHA>' `
  -EvidenceDirectory '<new unique EXTERNAL directory>' `
  -Python 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' `
  -ToolsBin 'C:\Program Files\nodejs'
# PLAN_ONLY_NOT_EXECUTED: no gates/evidence created, NOT a test pass.
# Add -Run ONLY for an authorized actual product retest, owned by 05/R04.
```

No installation, API calls, caller-supplied command strings, `eval`, source regeneration, or dynamic test selection. Existing candidate dependencies must already be available; missing tools/dependencies fail, never install. `ToolsBin` must contain `npm.cmd` and `node.exe` (or `node.cmd`); absolute expected paths are resolved once and invoked directly, irrespective of duplicate PATH entries. Caller-selected Python must be the trusted existing interpreter. Commands are nine fixed gates: build, public entry resolution, typecheck, immutable regression, full npm, schema check, Python schema check, fixed four-file Python parity, pack dry-run.

Public entry resolution uses fixed `--conditions=import` so the actual package's import-only export can be resolved from the candidate rather than the external guard directory. A real tiny Node import-only-package control checks the exact planned command; this is not an actual product build.

## Fail-closed evidence

- Exact HEAD, no tracked/unapproved untracked changes; immutable regression hash `08be1d15…` and schema hashes `3bfc9e4e…`, known-unfixed-source guard retained. Root `deepviz`, `deepviz.py`, `deepviz.pyc` rejected even if ignored. No source/oracle changes made.
- Before/after **each** gate and at end: all tracked raw bytes, HEAD, dirty state and this external PS/Python/Node guard's bytes must match. Explicit interpreter/npm/node bytes also checked after each gate. Generated ignored build/cache outputs may change; external evidence must be new.
- Python parity runs actual `pytest.main` in the guard's interpreter. Actual loaded `deepviz.*` file realpaths/raw SHA256 are checked at session start, collection finish, each test setup and after run. `python-origin.json` records collected files/count/modules; no separate-process `python -c` origin claim.
- Node reporter forced to TAP using fixed `NODE_OPTIONS`. Actual TAP header/outer plan/case records/totals checked. **Minimums**: immutable regression 36; full npm 282. Python JUnit minimum 4, all four fixed selected files present, actual collected count equals report count. This is a **nonempty-per-selected-file minimum**, not proof of an expected 689-test baseline. Source/oracle hashes and actual totals must be reviewed by the retester; a missing expected baseline count remains an acceptance limitation, not silently waived.
- **Zero allowed skips/todos/cancellations/failures/errors**. JUnit testcase statuses must agree with suite totals. Missing/malformed/contradictory reports and unexpected source/tool changes fail; future steps stay NOT_RUN. PLAN has zero executed tests and is never scoped PASS. Successful scope is still `SCOPED_GATES_PASS_NOT_FINAL_APPROVAL`.

## Own guard tests (SYNTHETIC, not product acceptance)

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
& '<existing-python>' -m pytest tests/r22_probes/role09/test_recipe_guards.py `
  -q -p no:cacheprovider --basetemp '<new external temp>' --junitxml '<new own XML>'
```

Fixtures are tiny local Git repositories. npm/node are **SYNTHETIC stubs with explicit fabricated case records** used solely to test recipe control flow; they are not builds/product tests. Four tiny Pytests really run/pass/skip/collection-fail. Separate tiny Node tests really generate TAP pass/skip. A declared trusted tool can still lie consistently; this is provenance/report validation, not a sandbox or independent compiler/runtime attestation. It does not prove source line semantics, bytecode/native dependency integrity, all engine rendering, current CI, 36/40 product regressions, scale or release acceptance. There are no product tests/builds/scale reruns in the recorded guard results.

Only NEW own verification paths changed. Actual 05 product retest and 21 independent review are separate; root/R04 decide adoption. Current report/evidence: `docs/coordination/reports/R22-09-retest-recipe-fix.md`, `docs/coordination/evidence/R22-09/`.
