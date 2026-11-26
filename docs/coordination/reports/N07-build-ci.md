# N07 packaging and CI report

## Assignment and identity
- Owner: N07 packaging/CI producer; actual session `ses_de6d66e34ffeUCgR75MN8Lp5Ot` from C17 live register.
- Dispatcher: C17; no spawning, remote writes, shared-source edits or shared-venv edits.
- Main checkout: `C:\Users\bagma\deepviz-agent-toolkit`.
- Assigned worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n07`.
- Assigned branch/base: `fix/n07-build-ci` / `b6abc8d`; actual current SHA and worktree state to be recorded before source work.
- Allowed source paths: `pyproject.toml`, `.github/**`, root `package.json` / `package-lock.json`, `packages/deepviz/package.json`, package scripts, `scripts/verify_*.py`, `scripts/export_schema.py`, and new packaging regression tests.
- Forbidden: model/schema data/source engine/normalization edits; shared `.venv` mutation; spawning; push/merge/publish.
- Acceptance: reproduce real packaging or CI defects, fix narrowly with TDD, verify exact installed-source CI and package checks where feasible, commit only scoped tested changes.

## Current checkpoint
- Read `tasks/N07-build-ci.md` first, then `tasks/C17-wave-common.md`.
- Corrected package-path interpretation per dispatcher/user: plural `packages/deepviz`.
- Current action: read recovery/design/plan/dependency contracts and inspect Git identity before creating the assigned worktree.
- Next action: run packaging and CI baseline, preserve failing reproduction, then apply the smallest scoped fix and rerun checks.
- Commands executed: none yet; no gates claimed.
- Source changes/commits/artifacts: none yet.

## Execution checkpoint 1
- Read all required recovery/common/design/plan/dependency contracts, live register and C17 report. No spawning.
- `git status --short --branch`, `git log -8 --oneline`, `git worktree list --porcelain`, `opencode api get /api/session/active`: exit 0. Main baseline `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`; pre-existing dirty main recovery files preserved.
- `git worktree add -b fix/n07-build-ci C:/Users/bagma/AppData/Local/Temp/opencode/deepviz-n07 b6abc8d`: exit 0; own worktree initially clean on exact assigned base.
- Own-source import probe with main `.venv/Scripts/python.exe`, explicit own `PYTHONPATH`: exit 0, Python 3.12.16, `deepviz.__file__` resolves to N07 worktree. `build`, `twine`, `ruff`, `mypy` installed; hatchling absent in shared interpreter (isolated build will install its own build dependencies). Node v26.13.1 / npm 11.20.0.
- Started background own-worktree `npm ci`, `python -m build --outdir artifacts/local/N07/baseline-dist`, Ruff/mypy/script-mypy/schema baseline commands. Logs under approved temp `N07-*.log`; gates pending completion, no pass inferred.
- Audit finding to reproduce: `read_prompt()` expects installed `deepviz/resources/prompts/v1/{system,request}.md`, but wheel force-include currently lists only schema and no source package resource tree exists.
- Ruling: use this assigned main report as the durable scoped ledger; do not create shared-plan workspace files or spawn final review because explicit C17 path/no-spawn ownership supersedes generic skill workflow. Independent N02/N14 and C17 retain acceptance authority.
- Next action: test installed wheel resources and sdist-to-wheel behavior, capture red regression before changing package metadata.

## Execution checkpoint 2: reproduced packaging defect
- Baseline `python -m build --outdir artifacts/local/N07/baseline-dist`: exit 0, wheel + sdist created using isolated hatchling 1.33.0. This success did **not** mean resource correctness.
- Added `tests/test_packaging_regressions.py`: builds wheel through sdist, verifies exact versioned prompt bytes, installs actual wheel with `pip --no-index --no-deps --target` into a temporary directory, and probes it with Python `-I` from outside the checkout.
- RED: `python -m pytest tests/test_packaging_regressions.py -q`: exit 1, **2 failed** in 34.89s. Wheel lacks `deepviz/resources/prompts/v1/system.md`; installed `deepviz.read_prompt()` raises `FileNotFoundError`. Full log `N07-packaging-red.log`.
- Root cause: runtime resource path is valid but no build mapping for `prompts/v1`; schema mapping is the existing correct pattern. Applied one-line `pyproject.toml` wheel force-include for that directory. GREEN rerun pending.
- Own-worktree `npm ci`: exit 0, 160 packages installed, 0 vulnerabilities; main node_modules untouched. Remaining npm commands running with separate logs.
- Exact CI baseline: `python -m ruff check . .github/tests`: exit 1, 10 import-order findings in existing `examples/deep_agent.py`, `python/deepviz/tests/{test_aggregation_semantics,test_backend_antv,test_backend_plotly,test_backend_vega,test_graphql_contract,test_normalize,test_render}.py`, `tests/{test_cross_language_contract,test_schema_contract}.py`. Out of N07 source ownership; not suppressed or edited.
- `python -m mypy`: exit 1, 8 existing errors: engines.py:275/276/362/363, render.py:63/77/136 (N05), tools.py:113 (N06). Exact output `N07-mypy-baseline.log`; route to owning producers/C17.
- `python -m mypy scripts/export_schema.py scripts/verify_evidence.py scripts/verify_visual.py scripts/verify_scale.py`: exit 0, 4 files. `python scripts/export_schema.py --check`: exit 0, schema exact at base; **no schema regeneration proposed or performed**.
- Next action: finish regression green and full suites, then repair CI artifact-consumer coverage rather than weakening gates to hide out-of-scope source failures.

## Execution checkpoint 3: scoped fixes green
- GREEN packaging regression: same command, exit 0, **2 passed** in 36.37s. Both prompts now ship byte-for-byte and are readable from the actually installed wheel. **N06 coordination: no `read_prompt` source/path change is needed.**
- Independently reproduced missing Python-CI npm prerequisite with an unbuilt public-package fixture, explicit `DEEPVIZ_TS_PACKAGE_ROOT`, `pytest tests/test_cross_language_contract.py -m integration -xq`: exit 1, setup error `[defaults]`, `ERR_MODULE_NOT_FOUND` for `dist/index.js`. Log `N07-ci-unbuilt-package-red.log`.
- Updated only `.github/workflows/ci.yml`: each Python matrix job now sets up pinned Node24, runs `npm ci` + `npm run build` before parity tests. No test skips, marker weakening or fixture changes. With built own package, `pytest tests/test_cross_language_contract.py -m integration -k defaults -q`: exit 0, **2 passed / 371 deselected**. This is a prerequisite fix, not a claim every semantic golden is correct.
- Distribution job now installs the wheel into its own fresh venv, checks import prefix + both prompts + schema outside checkout, and exercises both console entrypoint helps. npm distribution check now calls existing `npm run package:check` (real tarball ESM/JSON/runtime/declaration consumer), not dry-run alone.
- `npm run build`, `npm run typecheck`, `npm test`, `npm pack --dry-run --workspace @deepviz/agent-toolkit`, `npm run package:check`: all exit 0. npm tests **30 passed / 0 failed / 0 skipped**. Packed consumer passed ESM, JSON schema, runtime, TypeScript declarations; 22 packed files / 35,412 bytes.
- `pytest .github/tests -q --strict-markers`: exit 0, **12 passed**. Fixed `python -m build --outdir artifacts/local/N07/fixed-dist`: exit 0, wheel+sdist. `python -m twine check --strict <fixed-dist artifacts>`: exit 0, both PASS.
- Own new test Ruff, parsed workflow YAML, `git diff --check`: exit 0. No schema/model/source files edited.
- Read N02 package review and C17 routing after parent notification; findings independently agree. Existing lint owned by parent d4ee4e8/N08; mypy N05/N06; stale13 coercion fixture failures parent-owned. No cherry-pick of these parallel changes into N07 branch.
- Current action: full Python suite running against unchanged b6abc8d product source plus N07 changes; prepare genuinely fresh fixed-wheel consumer, then commit scoped files and record all gate totals.

## Ready commits (C17 may integrate in order)
1. **`08f2e801be917bfd27c9949ee6149d4e73f361b0`** — include versioned prompts in Python distributions; `pyproject.toml` + new TDD regression tests only.
2. **`b53c3aa9d7a9103e949b4c6a41206a39211d66c4`** — build public npm prerequisite before Python parity tests and exercise genuinely installed wheel/npm consumers in CI; `.github/workflows/ci.yml` only.

Both commit commands and staged whitespace checks exited 0. Own worktree now clean on b53c3aa. No source/schema/contract edits. Targeted packaging RED 2 failures -> GREEN 2 passes; npm+CI negative controls/build/twine results recorded above.

## Execution checkpoint 4
- Created **genuinely fresh** `C:/Users/bagma/AppData/Local/Temp/opencode/N07-fixed-clean-consumer` via `python -m venv`, not system-site-packages. Ordinary fixed-wheel install with base dependencies: exit 0; no shared environment edited. Log `N07-clean-install.log`.
- First hand-written clean-consumer probe exited 1 after successful resource reads/render assertions because its *report serialization* incorrectly called `Artifact.model_dump` (public Artifact is a dataclass with `to_dict`). This is a probe defect, not a product failure; corrected probe next. Preserve failure rather than claim a passed consumer prematurely.
- YAML loads with all five jobs, embedded Python compiles with `ast.parse`, extracted Bash passes `bash -n`: exit 0. First one-line PowerShell quoting attempt failed before execution; corrected stdin heredoc check passed. This validates local syntax, not remote Actions.
- Fixed wheel SHA256 `cafbc640fbbfdeaafbb36b4805f31a92877fd182d87f9fa4cb081e436d44548f`; fixed sdist SHA256 `2c26aff296ba548cbc51ca561aeac1fd93b851f91b67e4a57b69f6a8fce3a090` (path-to-hash identity to print explicitly in final check).
- Next executable action: corrected installed-wheel probe + console entrypoints, visually inspect its PNG; then record full-suite result and finalize scoped handoff.
