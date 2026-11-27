# N18 TypeScript native-engine semantics producer

- Task/owner: N18; dispatched by C17. Actual session ID `ses_de6d35898ffeRXd361GiG9aGSO`, returned by `session_move`.
- Status: in progress (2026-11-27).
- Main source observed: `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`, branch `release/candidate`; dirty `AGENTS.md`, `opencode.json`, untracked `RESUME.md`, `docs/coordination/` (preserved).
- Intended own worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n18`; branch `fix/n18-ts-render`; base `b6abc8d`.
- Allowed source: `packages/deepviz/src/render.ts`, `packages/deepviz/src/renderers.ts`, NEW TypeScript renderer tests only. Main checkout write authority limited to this report. No shared installs, candidate source edits, spawning, pushing, merging, or schema/normalize/models/root edits.
- Acceptance: confirm concrete native mapping defects with failing tests before fixes; inspect actual native specs/browser screenshots and console; run applicable npm gates with exact source/dependency identities; scoped commits and truthful engine/fallback/network limitations.
- Initial commands: `git status --short --branch` (0; state above); `git rev-parse HEAD` (0; exact SHA above). Read N18 task and common contract first, then RESUME, STATE, AGENTS, BRIEF.
- Current action: read remaining coordination/design/plan/dependency contracts, establish isolated worktree, inspect render implementation and tests.
- Next executable action: `git worktree list --porcelain` followed by creation of assigned new worktree if absent.

## Checkpoint 1 — isolated checkout and dependencies

- `git worktree list --porcelain` exit0: assigned path absent; all historical worktrees preserved. `git worktree add -b fix/n18-ts-render C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n18 b6abc8d` exit0. Session moved into this own worktree; source HEAD remains base above.
- Read remaining required REQUEST, C17 task/report, design, plan, architecture and dependency gates; loaded TDD/debugging/ponytail guidance and TDD test-writing reference. Source inspection limited to renderer callers and normalization contract (read-only).
- `npm ci` hit tool timeout120s, exit143; own `node_modules` partially existed. Retried `npm ci --loglevel=info` after inspecting state; timeout300s, exit143. Node26.13.1/npm11.20.0; dependency fetches reported cache hits and audit POST200, no dependency install pass asserted. A fresh own-worktree `npm ci --prefer-offline --no-audit --no-fund` is now background shell `sh_2193ac0d1001wss7jiSznyXOqS` (PID18588); waiting for automatic completion, no shared environment touched.
- Concrete code-path hypotheses to reproduce (not yet fixed): Plotly uses null as both real group and no-group sentinel, duplicating other groups into null trace; bubble incorrectly disallows signed y coordinates while negative size fields are clamped; Plotly heatmap uses first matching cell for duplicate coordinates; ECharts heatmap fixes visualMap minimum at0 even for signed color measures. Pie/category legends and AntV numeric heatmap axes need actual runtime inspection.
- Next action: add scoped failing native semantic tests, then run baseline/current browser suites when own dependency install completes.
