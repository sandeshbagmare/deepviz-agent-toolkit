# R22-11 — independent first-slice readiness review

**What this change does:** e44's 11-line validator stops Python from silently converting JSON strings/booleans into numeric ChartSpec fields. Integral numeric JSON values, defaults and existing bounds remain valid. This is an independently useful contract correction, not the whole visualization toolkit.

**Readiness verdict:** prepare the focused PR, resolving **R22-11-F1** below. Do **not** merge or count this as a review of a future head. Independently observed: e44 **30 passed**, own gap controls **13 passed**, parent model **6 genuine failures/24 passes**; all0skips. Actual focused head, narrow CI and two genuine reviewers/two genuine testers remain pending.

Owner `ses_de567811cffdTBwcb8pF5nDi9v`, SAME native identity confirmed. Read FULL R22 common contract + role11, current MAIN checkpoint and own note. Existing own branch `agents/r10-11-python-scale-envelope`, clean starting SHA **`4a0f7dfbf19e57f78e2e54c6d893c0912e3d97e3`**. No new worktree branch, source release, child or benchmark replay.

## Scope and pre-work facts

Independent non-author readiness reviewer for the first independently usable strict-ChartSpec-numeric slice (#30), not a final review of an unpublished PR head. R04 alone prepares PRs/shared/default branches, integrates/merges/closes issues. Two genuine reviewers and two genuine testers, actual focused head and observed required checks are still required. Latest user steering advances tested parts toward `main`, not a renamed `master` or unsafe all-branch merge.

Allowed writes: this report, own `evidence/R22-11/`, actual-ID note, own branch publication and NEW `tests/r22_probes/role11/` only if novel tiny controls are missing. No production/workflow/schema/existing oracle/environment/issue/PR/shared-candidate writes, installs or spawning. Existing shared venv is read-only. All immutable source/test snapshots and raw outputs use unique external temp directories.

Actual Git preflight exit0: default **`0ae2cf26426822135fc10d337fcacf580b7ed833`** has only seven foundation files, including `models.py` and `pyproject.toml`, **no test file**. Exact proposed fix **`e44f667ed494fa272f97792ef99942a364ebca24`** is parented by **`715c1f5ca0c13c276110c64d2af8c21deca881ea`**, adds11 validator lines and13 test lines in **`tests/test_models.py`** (root tests, not package tests). Blind cherry-pick cannot safely assume that absent test file. Actual MAIN candidate7bc is not our test source.

## Accepted plan / current action

1. Read exact main/e44/parent model, original test file, pyproject/setup/schema/callers. Identify complete minimal paths and dependency prerequisites without dragging later toolkit/dashboard/renderer code.
2. Independently run existing30 contract tests in immutable e44 source/test snapshot, shared venv read-only, actual imported module/hash proof before/after. Check coercion rejection, integral floats, defaults/bounds and schema/failure controls; add only genuinely missing tiny own tests if needed.
3. Record concrete blockers and smallest safe PR plan for R04. No invented PR number/head/checks, merge or final approval. When a focused head is actually supplied, verify exact source equivalence and review that head separately.
4. Meaningful scoped own commit/non-force push/actual remote-SHA receipt; leave current-source/scale/full-toolkit/900 acceptance explicitly unmet.

Historical pre-work action (completed below): `git show e44f667...:tests/test_models.py`, inspect main/parent/e44 model+pyproject diffs and tracked callers. No result was claimed at that checkpoint.

## Exact dependency audit / initial source-guard failure

- Main's model bytes equal parent715; e44 adds only the11-line numeric before-validator. Main needs the **complete e44 `tests/test_models.py`**, not a13-line hunk against a missing file. Main already declares Pydantic>=2.10,<3, pytest in dev and Python>=3.11.
- Parent pyproject's only additions versus main are schema force-include and isort known-first-party; neither is required to execute the model or contract tests. Main has no schema, package initializer, CLI implementation or CI. Do not drag later full toolkit packaging/CLI/renderers into this tiny fix.
- Unique external root: `C:/Users/bagma/AppData/Local/Temp/opencode/r22-11-first-slice-ses_de567811cffdTBwcb8pF5nDi9v-artifacts`. Candidate copies are exact e44 Git-LF bytes; baseline intentionally uses parent715 model with unmodified e44 regressions, explicitly not a parent-tree test run. Copied model/test/pyproject/schema and all origins/hashes before execution.
- Initial attempts on both sources exited1 **before pytest** at actual module identity guard. These are harness source-isolation failures, **not product RED or test results**. Diagnosis proved shared venv's editable `.pth` adds MAIN source; its regular `deepviz/__init__.py` wins over historical e44 namespace package despite PYTHONPATH. Actual import was MAIN and was correctly refused.
- Next: remove only the exact MAIN editable-source entry from **process-local** sys.path before importing; keep third-party/stdlib paths and assert actual model path/hash before/after. No source initializer creation, dependency installs, global/PTH/environment-file edits or oracle changes. Use fresh r2 logs/receipts/basetemps.

## Immediate readiness / actual immutable contract result

**Ready to prepare a focused contract PR, not ready to merge an unpublished head.** Main model equals the parent model exactly. The minimal complete source/test slice is **two paths**: replace `python/deepviz/src/deepviz/models.py` with exact e44 model; add the **whole** e44 `tests/test_models.py` (30 existing cases), not its isolated13-line hunk. No pyproject/runtime dependency change is needed. Parent schema force-include is unnecessary unless R04 deliberately adds a canonical schema deliverable; do not import absent CLI/renderers/npm/dashboard evolutions merely to test this contract.

The process-local path correction removed exactly one MAIN editable-source path, without changing shared files/dependencies. Actual e44 **30 passed,0 skipped,0 deselected in0.15s/exit0**. Before/after loaded model resolves only the immutable candidate path, SHA256 `94824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170`.

Deliberate parent715 model + unmodified e44 regressions: **6 failed,24 passed,0 skipped in0.39s/exit1**. Six exact failures are width-string, height-string, columns-string, max_points-string, version-True and columns-True accepting coercion. These are genuine baseline RED, distinct from the pre-pytest source-guard errors. Unique `*-r2-contract.xml/.log/*-identity.json` receipts preserve exact input/source origins and stable hashes. Environment Python3.12.16/Pydantic2.14.4/pytest9.2.0, shared tools read-only.

Next small gap controls cover JSON truthiness/all five integral-float fields and endpoints/schema equivalence (existing tests have width-only integral positive), then scoped static/source proof and readiness publication. Actual future focused head, required CI and genuine two-reviewer/two-tester reports remain prerequisites; this is not prospective approval.

Own NEW tiny gap file actually **13 passed,0 skipped in0.33s/exit0**. It covers Python/JSON true/false/null/numeric strings for all five fields, integral-float endpoints/fractions/outside bounds, nested child validation, no input mutation and generated schema equality with persisted e44 plus Draft202012 validity. Actual e44 module hash stayed unchanged. Ruff with exact e44 config exited0 on model/original tests/own probe; mypy with main config exited0 on the actual model (1 file).

One main-config Ruff attempt exited2 **before lint** because the exact pyproject copy was named `main-pyproject.toml`, which Ruff treats as flat `ruff.toml` rather than `[tool.ruff]` config. This is a harness filename error, not a product lint failure. Next uses the same immutable main bytes under `main-config/pyproject.toml`; no source/config edits are authorized or made.

## Concrete readiness finding: R22-11-F1

**Must resolve before claiming a clean focused lint gate.** Correctly named exact main config makes Ruff exit1 with **one I001 at `tests/test_models.py:2-7`**. E44's test imports rely on parent pyproject's `known-first-party=["deepviz"]`; main lacks that setting. The model itself passes. This is a real prerequisite, unlike the earlier bad-filename harness error.

Smallest safe **two-path** plan: R04 adds the complete NEW e44 test file on main but reorders only its import block to the existing main Ruff grouping; test bodies/assertions remain identical. Exact model bytes remain e44. Alternative **three-path** plan: add only the small isort known-first-party setting to main pyproject, keeping exact e44 test bytes; **do not copy parent pyproject wholesale**, because its force-include points at a schema absent on main. Next independently checks the import-only proposal via stdin/AST without editing any existing oracle/source.

The import-only proposal was actually checked through Ruff stdin with exact main config: **exit0**. Python AST comparison proves every function/class body and decorator is unchanged. Full e44 test file is **67 lines**, not a13-line patch; original SHA256 `2f15dc277a6298780a6ab32076d642fe8491222cfc2c051fdbf33c0d18afe81b`; proposed LF import-only SHA256 `90b1675f1a2f44d8c66bc9db68f93f2b01c463511d98c586d88da314b1ffdc32`. No source/test file was written or edited. Exact candidate model plus own NEW probe also passed mypy0 on2files with exact snapshot MYPYPATH and no incremental cache reuse.

Fresh read-only expected-identity GitHub checks at15:08:14UTC returned200: user `sandeshbagmare`, repository/default `main`, #30 **open**, default SHA still `0ae2cf26426822135fc10d337fcacf580b7ed833`. Saved `evidence/R22-11/issue30-main-readback.json`. Actual #30 criteria are exactly numeric-string/boolean rejection, integral JSON floats, valid defaults/bounds, regression tests and lint/types. No focused PR/head/check result has been supplied or invented; no issue/PR mutation was made.

## Smallest complete focused slice (R04 only)

Start a new focused branch from fresh actual default `main` (observed0ae2); preserve PR31's broader source and failures separately. Do **not** blindly cherry-pick e44 or parent715 into a tree with no tests/schema.

1. `python/deepviz/src/deepviz/models.py`: exact e44 bytes, SHA256 `94824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170`. Main model exactly equals e44 parent, so this is only11 added validator lines.
2. NEW `tests/test_models.py`: entire67-line e44 file,30 cases. For the two-path plan, reorder imports only to existing main config: `pytest`, `deepviz.models`, `pydantic` in one third-party group. All test bodies/decorators remain unchanged; actual stdin lint and AST equality passed. Expected LF hash after that exact proposal: `90b1675f1a2f44d8c66bc9db68f93f2b01c463511d98c586d88da314b1ffdc32`.
3. A separately scoped **new focused contract CI workflow** is needed because main has no workflow. Call it contract validation, not whole-product verification. Use fresh Python dependencies for the actual model/test/static/schema-output checks, explicit `PYTHONPATH=python/deepviz/src`, preserve regression failures, and show real remote required checks before merge. No workflow was authored/approved by this worker. Alternative step2 can keep exact test bytes by adding only isort known-first-party config (one extra path), but schema force-include is not needed.

Runtime prerequisite is existing main Pydantic>=2.10,<3; tests use its existing dev pytest. CI lint/types need the already-declared Ruff/mypy dev tools. No new runtime dependency, initializer, renderer, CLI implementation, npm package or dashboard field is needed for this fix. Current main entry points already refer to absent CLI modules; that baseline incompleteness must **not** be mislabeled as this contract PR delivering the full package. No package build/release was attempted here.

The validator changes runtime coercion to match the existing schema, not the declared field schema. Actual parent and candidate generated schemas both equal persisted e44 schema and share canonical SHA256 `75972780be039e8dbbbf78a93d0611d9e6a5c9ed6e57a7ecf4239c2af20d6670`. Copying a190-line schema and packaging force-include into main is therefore not required to fix #30. If R04 deliberately promises schema distribution in this slice, that is additional scope needing its own complete paths/verification, not a hidden prerequisite.

## Independent controls and actual output

|Check|Actual result|Scope|
|---|---|---|
|Existing exact e44 `tests/test_models.py`|30passed/0skipped/0deselected/0errors,0.15s,exit0|Immutable e44 model/test/pyproject/schema|
|Same e44 tests on parent715 model|6failed/24passed/0skipped/0errors,0.39s,exit1|Explicit regression RED; not parent test-tree run|
|NEW own tiny gap tests|13passed/0skipped/0deselected/0errors,0.33s,exit0|JSON/Python false/true/null/strings, all5 integral endpoints, fractions/outside bounds, nested children/input mutation/schema|
|Ruff e44 config: model/original tests/own probe|exit0|Actual e44 paths|
|Ruff unchanged main config: original e44 model/tests|exit1,1I001|Real prerequisite R22-11-F1|
|Ruff unchanged main config: stdin import-only proposal|exit0|Proposal only, all AST test bodies unchanged|
|Mypy unchanged main config: exact model+own probe|exit0,2files|Exact MYPYPATH, no incremental cache reuse|

Actual JSON outputs were inspected: `{}` and all-five integral-float specifications serialize identically before/after; candidate rejects `{"width":"900"}`, `{"version":true}`, `{"columns":true}` with ValueError-backed ValidationErrors, while the parent accepts all three. These are real model/schema outputs, **not renderer/browser artifacts**. Main has no renderer to visualize; no image or browser acceptance is claimed.

New review controls remain in `tests/r22_probes/role11/`, separate from existing oracles. Their source-identity/schema fixture requires the external immutable snapshot; **do not blindly copy that reviewer-only setup into main CI**. R04 can select small JSON-boundary cases for the new main test file without weakening any assertion.

## Exact environment / replay limitations

Read-only interpreter `C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`, Python3.12.16/Pydantic2.14.4/pytest9.2.0. No dependency install, current7bc import, full-toolkit/npm/build/scale or1M/10M replay. Other Python/Pydantic versions were not tested here.

Both test invocations were actual `pytest.main(["tests/test_models.py","-q","-p","no:cacheprovider","--strict-markers","--basetemp",<unique>,"--junitxml",<unique>])` calls in fresh Python stdin drivers, with process-local exact MAIN editable-path removal before model import. PYTHONPATH names the requested immutable snapshot source; CWD is that snapshot. Driver asserts actual `deepviz.models.__file__` and every copied source/test/config/schema hash before/after. Snapshot copy origins/commands/full versions remain in `review-checks.json`; logs/XML named above. This avoids a false baseline pass from shared editable package precedence.

Static replay, with correctly named exact main `pyproject.toml`:

```powershell
& $PY -m ruff check --config "$MAIN_CONFIG/pyproject.toml" "$SNAP/python/deepviz/src/deepviz/models.py" "$SNAP/tests/test_models.py"
# Actual1/I001 for exact e44 test; do not claim main lint green.
& $PY -m mypy --no-incremental --cache-dir "$ART/new-cache" --config-file "$MAIN_CONFIG/pyproject.toml" "$SNAP/python/deepviz/src/deepviz/models.py" tests/r22_probes/role11/test_numeric_contract_slice.py
# Actual0/2files with MYPYPATH=$SNAP/python/deepviz/src.
```

## Evidence / next action

Own `docs/coordination/evidence/R22-11/`: `review-checks.json` (SHA256 `a813dab85ae80189ee9bf2507dbb16d191b6870576d9d6a8634da891461c21ce`), candidate30 JUnit, genuine baseline6RED/24pass JUnit, own13 JUnit and actual read-only issue/main receipt. Five evidence files total35,305bytes; raw logs remain in the unique external root, hashed in the receipt. All copied files were compared again with exact Git object bytes; source manifests unchanged. Two pre-test source-guard errors and one Ruff config-filename error are preserved separately from product results.

**Next:** publish this scoped readiness handoff; R04 builds/publishes the smallest complete PR and supplies its exact head. On that actual head this same independent reviewer must check complete diff/workflow/prerequisites, model hash, import-only test AST equivalence and source-specific gates, **not borrow this baseline as final approval**. Genuine reviewer01 plus testers04/09 remain separate. No focused PR existence, merge, closure, final-green/full-production/900 success is claimed here.

## Own publication receipt

Own scoped commit **`e10e64358df4e2c66410ef8555f45de2c0de07fe`** (parent `4a0f7df`), exactly 8 authorized paths, committed after whitespace/secret/JSON/LF/production-scope checks exited0. At 15:18:44UTC, expected GCM identity GET `/user` returned200 (`sandeshbagmare`); remote-before was `4a0f7df` and ancestor check exited0. Non-force push exited0. `git ls-remote` and authenticated GitHub ref GET both exited0/200 and returned exact `e10e64358df4e2c66410ef8555f45de2c0de07fe`. Own worktree clean. Sanitized receipt: `docs/coordination/evidence/R22-11/publication-final.json`.

This is a branch/evidence publication, **not a PR or merge claim**. Credentials remained in memory only; no issue/PR/auth configuration or shared candidate mutation. R04's next action is to create the actual focused head from fresh main, resolve F1, run its narrow real CI and obtain genuine reviewer01/tester04/tester09 reports before deciding merge. If that head arrives, this lane must review the head itself rather than reuse this baseline.

Artifact byte disclosure: raw Windows baseline JUnit is7,265B/SHA256`eff0f89fff2ed5ade333f93c0c36a9246991d96a13df56651d0729141d46b83e` (the raw hash in review-checks). Git normalizes traceback CRLF to LF: committed baseline XML is7,199B/SHA256`7047d2378a1dfa6ca521894149756b99d610b1d77b122dcae99c246ff4597d95`. Actual `raw.replace(CRLF,LF)==Gitblob` passed; no case/value/result changed. Other two JUnit files are unchanged byte-for-byte. Publication receipt records both identities, not a false raw/Git byte-equivalence claim.
