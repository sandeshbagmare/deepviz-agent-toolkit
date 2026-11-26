# N02 independent package and claim review

## Assignment and ownership

- Owner: N02, independent nested QA/reviewer under C17; actual session `ses_de6d9dcf1ffe5D9TNNF3B2hP4V` recorded in C17's report.
- Assignment: `docs/coordination/tasks/N02-package-review.md`.
- Date: 2026-11-27.
- Source policy: read-only production/source/Git review; no commits, no spawning, no sibling-worktree mutations.
- Allowed writes: this report and uniquely named N02 untracked verification artifacts only.
- Candidate baseline reported by assignment: `468b28c` (incomplete; not yet independently verified).
- Branch: `release/candidate`; independently observed integrated baseline SHA `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`, tree `8bf9b42841e1171e2e3827685bc17ef44535aa1c`.
- Main dirty paths at initial check: modified `AGENTS.md`, `opencode.json`; untracked `RESUME.md`, `docs/coordination/`. None changed by N02 except this report.
- Frozen verification snapshot: `C:\Users\bagma\AppData\Local\Temp\opencode\N02-package-review-b6abc8d\source`, created read-only from committed Git archive; all builds/check artifacts stay under the N02 directory. No sibling worktree writes.

## Acceptance checks

- Inspect preserved TypeScript, CI, integrations, package entrypoints/contracts, README and research claims.
- Independently reproduce material packaging, Python/TypeScript schema parity, MCP trust-boundary, and unsupported-claim findings.
- Record exact source identity, commands, exit codes, observed outputs, limitations, and severity/file/line/reproducer for findings.
- Prove imports resolve to tested source; do not treat old-source findings as candidate signoff.
- Read C17's report near completion and audit its exact complete candidate when available.

## Current checkpoint

- Status: in progress; required RESUME/AGENTS/STATE/ROSTER/BRIEF/REQUEST/design/plan/dependency-gates and C17/WORKLOG handoffs read. C17 reports complete baseline integrated; no gate pass yet.
- Current action: Python clean-wheel prompt resource failure reproduced; auditing CI cross-language discovery and MCP boundaries next.
- Next executable action: reproduce Python CI's missing-built-npm prerequisite with a pristine TS archive and `tests/test_cross_language_contract.py`, then run targeted trust-boundary probes on the frozen source.

## Evidence and findings

- Identity commands: `git status --short --branch`, `git log -8 --oneline`, `git worktree list --porcelain` exited 0; observed 24 worktrees. Initial unquoted `git rev-parse HEAD HEAD^{tree}` was mangled by PowerShell and failed; corrected `git rev-parse HEAD 'HEAD^{tree}'` exited 0 and yielded SHA/tree above.
- Environment: Node `v26.13.1`, npm `11.20.0`, shared project Python `3.12.16`. Shared Python import resolves to `C:\Users\bagma\deepviz-agent-toolkit\python\deepviz\src\deepviz\__init__.py`; not used as proof of installed-distribution correctness. `build`, `mcp`, `deepagents`, `pytest`, `jsonschema` available; `hatchling` unavailable in shared environment.
- `git archive --format=zip --output <N02-root>\source.zip <full-SHA>` and `Expand-Archive ...\source`: exit 0. Frozen source identity is the committed tree, independent of concurrent candidate changes.
- No success or candidate-signoff claim is made.

## What this change does

The integrated baseline provides bounded Python normalization, five rendering adapters, agent/MCP tools, an npm SDK and CI checks. This independent review checks the installed interfaces and whether documentation and CI actually exercise the declared contracts. Expected load is the documented local-agent/stdio host, not an untrusted multi-tenant service.

## Must fix

### 1. P1 — Built Python distributions omit both advertised versioned prompts

- **What this is:** `read_prompt()` opens `deepviz/resources/prompts/v1/{system,request}.md` (`python/deepviz/src/deepviz/__init__.py:16-20`); README `135-153` uses this API to initialize the documented Deep Agent.
- **Problem:** `pyproject.toml:24-28` force-includes only the JSON schema. A clean wheel has no prompt files. Both `read_prompt('system')` and `read_prompt('request')` raise `FileNotFoundError` in a genuinely fresh virtualenv after installing the built wheel, so README's claim that the wheel includes them is false on this SHA.
- **Fix:** Package `prompts/v1` at the resource location the API uses, and exercise both prompt reads in an installed-wheel consumer. No API redesign is needed.
- **If we skip it:** The published/source-built Deep Agent example crashes before creating its agent.
- **Exact repro:** From frozen source, project Python `-B -m build --outdir ..\python-dist` (exit 0); `-m twine check --strict ..\python-dist\*` (exit 0); create fresh `..\python-consumer`, install the wheel with ordinary dependencies (exit 0); run `..\python-consumer\Scripts\python.exe -I -B ..\verify_installed.py` (probe exit 0, both intentional error observations saved). Probe and JSON are under the N02 artifact root. Wheel SHA-256 `14025e5d3afcbad656ae8a9625b98360bf8349a34e06987f85d62e871cf6bb08`.
- **Import identity:** `...\N02-package-review-b6abc8d\python-consumer\Lib\site-packages\deepviz\__init__.py`; `mcp`, `deepagents`, `langchain_core` absent there, proving base imports/rendering do not accidentally use those shared optional dependencies.

### 2. P1 — Python CI runs required cross-language tests without building their npm prerequisite

- **What this is:** `.github/workflows/ci.yml:39-54` installs Python dependencies and runs all integration-marked tests. `tests/test_cross_language_contract.py:76-105,130-136` requires the built npm public export; missing prerequisites intentionally fail rather than skip.
- **Problem:** No Python matrix job installs Node/npm dependencies or builds `packages/deepviz/dist`; the independent Node job cannot share its filesystem. On a pristine committed TS archive, the integration fixture fails with `ERR_MODULE_NOT_FOUND` for `dist/index.js`, before its first parity assertion. Thus the integrated workflow cannot reach green on a clean runner as written.
- **Fix:** Set up Node, `npm ci`, and `npm run build` before parity integration tests in the Python job, or move those explicitly selected tests into a combined Python/Node job while ensuring they still run. Do not hide the failure with an unconditional skip.
- **If we skip it:** All three Python matrix integration jobs fail on the clean checkout even though a developer's previously built local checkout can pass.
- **Exact repro:** Git-archive only `packages/deepviz` from the exact baseline into N02 `ci-pristine`; set `PYTHONPATH=<N02-root>\source\python\deepviz\src`, `DEEPVIZ_TS_PACKAGE_ROOT=<N02-root>\ci-pristine\packages\deepviz`, `PYTHONDONTWRITEBYTECODE=1`; run project Python `-B -m pytest <N02-root>\source\tests\test_cross_language_contract.py::test_public_npm_validator_matches_python -q --maxfail=1 --junitxml=<N02-root>\ci-pristine-parity.xml -o cache_dir=<N02-root>\.pytest-cache-ci`. Exit 1; 1 setup error at `[defaults]`, not a semantic parity result. Text log `ci-pristine-parity.txt`. Python import printed and confirmed the frozen source path, not main editable source. This local Windows prerequisite reproduction is not a remote Actions run.

### 3. P1 — Integrated parity corpus still requires coercions the authoritative model now forbids

- **What this is:** `tests/fixtures/schema-parity.json:60,120-121,130-132,149-150,162-164,180-181` labels numeric strings/booleans as accepted and coerced; `tests/test_cross_language_contract.py:122-127` requires those golden results even in the Python-only CI lane.
- **Problem:** `models.py:38-47` deliberately rejects these JSON types, and the built TS validator agrees with Python. Thirteen golden Python tests fail, including `version=true`, `max_points='10'`, `width=' 240 '`, `columns=true`, and nested equivalents. These are stale contract expectations, **not** evidence of current Python/TS disagreement: all public npm-versus-Python comparisons passed with npm built.
- **Fix:** Contract owner should update the 13 fixtures to the agreed strict JSON policy (or explicitly reverse the policy in both implementations); preserve the negative tests. Do not weaken the validator solely to satisfy stale expectations.
- **If we skip it:** The baseline cannot pass its ordinary Python unit gate even after fixing the CI npm prerequisite.
- **Exact repro:** With `PYTHONPATH=<frozen-source>\python\deepviz\src`, `DEEPVIZ_TS_PACKAGE_ROOT=<built-frozen-source>\packages\deepviz`, `PYTHONDONTWRITEBYTECODE=1`, `MPLBACKEND=Agg`, project Python `-B -m pytest tests/test_models.py tests/test_schema_contract.py tests/test_cross_language_contract.py python/deepviz/tests/test_integrations.py python/deepviz/tests/test_mcp_transport.py -q --junitxml=<N02-root>\targeted-tests.xml --basetemp=<N02-root>\pytest-temp -o cache_dir=<N02-root>\.pytest-cache`. Exit 1; **13 failed, 451 passed, 1 skipped**, 79.18 seconds. Durable full failure log `targeted-tests.txt`; JUnit XML records exact cases. Skip reason inspection pending.

## Completed checks and artifacts

All commands below ran in the N02 frozen snapshot unless noted; baseline SHA/tree above applies.

| Check | Exit / totals | Observed result |
| --- | --- | --- |
| `npm ci` | 0 | 160 packages added; npm reports zero vulnerabilities (not an independent security audit) |
| `npm run build` | 0 | Built source TypeScript |
| `npm run typecheck` | 0 | TypeScript compilation check |
| `npm test` | 0; 30 passed, 0 failed, 0 skipped | Included normalization/render/tool-helper tests, not browser acceptance |
| `npm pack --dry-run --workspace @deepviz/agent-toolkit` | 0 | 22 files / 35,412 bytes packed size; JSON schema and public JS/types included |
| `npm run schema:check` | 0 | Existing canonical-schema/default check passed |
| `npm run package:check` | 0 | Existing real tarball clean consumer exercised ESM/public JSON/runtime/declarations; script removes its own consumer on completion |
| Python `-B -m build --outdir ..\python-dist` | 0 | Wheel and sdist built with isolated Hatchling 1.33.0 |
| Python `-B -m twine check --strict ..\python-dist\*` | 0 | Both distribution metadata checks passed; did not catch missing prompts |
| Fresh virtualenv wheel install | 0 | Base dependencies installed without shared site-packages |
| `python-consumer\Scripts\python.exe -I -B verify_installed.py` from N02 root | 0 | Installed schema present, prompts missing; basic Matplotlib bar rendered with 2 input/2 output rows |
| Installed `deepviz.exe --help`, `deepviz-mcp.exe --help` | 0 each | Both console entrypoints resolve; `--help` does not prove MCP transport |
| Pristine TS prerequisite parity reproduction | 1; 1 setup error before first case | Missing built `dist/index.js`; finding 2 |
| Targeted Python/model/schema/parity/agent/MCP suite with npm built | 1; 13 failed, 451 passed, 1 skipped | Stale golden fixtures (finding 3); current runtime Python/TS validator comparisons passed |

- Durable artifacts: `source.zip`, `source/`, `python-dist/`, `python-consumer/`, `verify_installed.py`, `installed-wheel-results.json`, `wheel-render/deepviz-9tbxz9ct/{chart.png,chart.svg,chart.html,manifest.json}` under `C:\Users\bagma\AppData\Local\Temp\opencode\N02-package-review-b6abc8d`.
- Actual PNG opened with image read tool: A bar reaches 2, B reaches 5, zero baseline, readable title/category/value axes; no clipping observed at 900×520. This is one installed-wheel basic-render check, not five-engine/browser/scale acceptance.
- No production/shared-environment edits, commits, or spawned workers.
