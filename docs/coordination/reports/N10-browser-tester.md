# N10 independent real-browser tester B

- Owner/session: N10, external child session (session identifier not provided).
- Assigned branch/worktree: `test/n10-browser`, `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n10` (not yet created).
- Assigned base: `b6abc8d`; current SHA and dirty state pending verification.
- Allowed writes: this MAIN-checkout report; unique browser QA tests and `artifacts/local/N10` in the new own worktree only. Production is read-only. No spawning, shared installs, merges, pushes, or GitHub writes.
- Current action: read common contract and required recovery/design/dependency records, then create isolated worktree and inspect browser harness.
- Acceptance: actual engine dependencies load, browser console errors fail; known-value Python five-engine and TypeScript browser semantic/screenshot inspection; exact source identity, commands, failures, limitations and artifact evidence recorded.
- Commands so far: dedicated file read of assigned task and common contract; initial common-contract path at `docs/coordination/C17-wave-common.md` absent, located correct file at `docs/coordination/tasks/C17-wave-common.md`.
- Next action: read required MAIN recovery and coordination files; verify Git state and create new assigned worktree at base `b6abc8d`.

## Results

In progress. No test or rendering success claimed.

## Checkpoint 1 — isolated source and dependency setup

- Required recovery, contract, design, plan and dependency-gate files read. Browser skill loaded. No subagents spawned.
- MAIN inspection: `git status --short --branch` exit 0: `release/candidate` ahead 20, existing dirty `AGENTS.md`, `opencode.json`, untracked recovery/coordination files preserved. `git worktree list --porcelain` exit 0.
- `git worktree add -b test/n10-browser C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n10 b6abc8d` exit 0. Exact baseline `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.
- Own `npm ci` foreground call timed out after 120 seconds (tool reports exit 143); no install pass claimed. A read-only process/state check found the child `npm-cli.js ci` still running and some package files present. Do not launch a competing install.
- Environment: Node `v26.13.1`, npm `11.20.0`. No shared environment changes.
- Next action: prepare independent known-value Python/TS artifact and real-browser verifier while the own dependency operation finishes; then build and run with resource/console capture.

## Checkpoint 2 — generator harness correction (not a product defect)

- Added only own independent QA files `tests/browser/n10/{cases.json,generate.py,generate-ts.mjs}` with known bar/line/scatter/pie/heatmap/grouped-series/dark-theme/dashboard inputs and semantic oracles.
- First Python generator command used main interpreter with own explicit `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`; exited 1 after all 45 product renders returned. Harness mistakenly called `Artifact.model_dump()` although the public artifact is a dataclass with `to_dict()`. Corrected QA harness only; first log/manifest will be preserved as harness-error evidence, not reported as 45 product failures.
- Proved imported source is `deepviz-n10/python/deepviz/src/deepviz/__init__.py`, baseline full SHA unchanged. Versions: Python3.12.16, Matplotlib3.11.2, Plotly6.9.0, vl-convert-python1.9.0.post1, Pydantic2.14.4; schema SHA256 `f5f0316b592f78f5dc058fce123cd9a7c683d2259685f56524724af27880135a`.
- Native dependencies are actual installed engines, no stubs. No product source edits.
- Next executable action: preserve first output, rerun corrected generator, finish own npm/build, run actual Chromium resource/console/semantic inspection.

## Checkpoint 3 — native Python artifacts ready

- Corrected Python generator exited 0: 45/45 actual native artifacts generated, 0 generation errors (nine cases per Matplotlib/Plotly/Vega-Lite/ECharts/G2). This is generation evidence, not browser/semantic acceptance yet.
- Evidence root: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n10\artifacts\local\N10`. `python-manifest.json` records every source input/spec, paths, native manifest and exact import/schema/package identity. `python-generate.log` contains current successful generation command output. Earlier harness failure preserved as `python-generate-harness-error.log` and `python-manifest-harness-error.json`; product output folders remain untouched.
- First npm child was confirmed gone before retry; retry launched once in background with durable `npm-ci-retry.log`. Awaiting automatic completion, no competing/shared install.
- Independent browser driver `tests/browser/n10/inspect.mjs` prepared: unmodified default HTML through localhost, external CDN resources requested normally (no route interception/stubs), script response SHA/bytes/status, true engine versions, actual native Plotly calcdata/ECharts layout, SVG geometry/text and observational canvas text capture, real screenshots and raster summaries. Optional TS local-asset mode uses supported public render options and real npm library bytes, explicitly not default-network acceptance.
- Harness syntax command exited 0: `node --check tests/browser/n10/inspect.mjs`; `node --check tests/browser/n10/generate-ts.mjs`; main Python `ast.parse(...)`.
- Next action: after own npm completion, `npm run build`, generate TS cases, execute default native browser inspection and preserve all failures for N05/N18.
