# Persisted user request and operational constraints

Captured during continuation on 2026-11-27. This is the requested scope, **not** a claim that it has been delivered. The versioned design/schema resolve implementation details; this file preserves acceptance intent across chat/session loss.

## Latest operating instructions

- Continue the existing charting toolkit project fully autonomously. Do not ask confirmation questions or pause for routine decisions.
- Use specialized agents, including nested delegation when useful, with a hard maximum of **22 concurrent agents across all levels**. A prior allowance of up to 100 agents refers to total roster/waves, not simultaneous activity.
- Stay below 100 coordinator turns; minimize user-facing replies and routine narration. File-based briefings, reports and handoffs are the default communication channel.
- Preserve assignments, decisions, current work, commands/results, blockers and executable next actions in files so a restarted session can reconstruct the project. Do not promise recovery of unwritten in-flight thoughts or unsaved external sessions.
- Continue productive work around blockers, log real blockers in GitHub issues and use the best safe workaround. Do not fabricate issue counts, completed work, unrun tests or reviewer approvals to appear finished.
- Earlier six canceled sessions remain preserved and canceled; use remaining/new explicitly budgeted responsibilities without reviving those sessions.

## Product

Build a production-quality, Python-first visualization toolkit attachable to the Deep Agents framework. A model supplies a validated declarative chart/data-consumption schema; the toolkit accepts structured datasets and produces charts and multi-chart dashboards. Support arrays, records/columns, JSON/nested objects, GraphQL pages/edges/nodes, CSV/TSV, JSONL, time series, hierarchical/geographic data, sparse/missing/mixed inputs and optional Arrow/Parquet where feasible. Give clear safe errors or explicit mappings for unsupported/ambiguous shapes, not arbitrary executable code.

Scale from 10 through 1K, 100K, 1M and 10M source records using bounded streaming reduction, aggregation/downsampling and appropriate rendering strategies. Prove counts, exact/lossy semantics, memory method and real visible output. Ten million source rows do not require ten million independent browser marks.

At least five working alternatives: Matplotlib, Plotly, Vega-Lite, ECharts and AntV G2. Standard chart breadth includes bar, line, scatter, area, pie, heatmap and other well-known kinds, plus dashboards, recommendations/themes and documented chained normalization/recommendation/render flows. Every capability claim must match actual engine behavior; disclose fallbacks and online dependencies.

## Research

Document publicly observable ingestion -> model/spec -> renderer -> output pipelines for ChatGPT data analysis, Claude artifacts/inline charts, OpenCode and other relevant agents. Do not claim access to private implementation. Use official sources and distinguish documented fact, observation and inference.

Compare AntV G2/G2Plot/AVA, Vega/Vega-Lite, ECharts, Plotly, D3, Observable Plot, deck.gl, uPlot, Datashader, Bokeh, Altair and useful additional libraries/repos. Focus on declarative schema design, large data, auto recommendation and themes. More than 100 repo reviews were permitted, not a reason to fabricate a review count. Persist findings, comparison matrix and recommendations under `docs/research/`.

## Repository and SDLC

- New GitHub repository in the user's account; preserve the existing project rather than recreate it. Verify current public visibility and actual remote state.
- Clean monorepo: Python packages, TS/npm packages, shared schemas, examples, docs and fixtures; justify boundaries in `docs/architecture.md`.
- Use the existing oh-my-opencode/openagent orchestration installation with explicit real-session provenance; never claim an unobserved migration.
- Real PM/engineering/architecture/developer/tester/reviewer/docs responsibilities with branches/worktrees and small scoped commits.
- Epics/stories/tasks/bugs with labels, milestones and genuine acceptance evidence. Requested numerical target: **at least 900 legitimate GitHub issues created and resolved**. It remains unmet until actual issue records demonstrate it; tests are not issues, artificial filler scopes/closures are forbidden.
- Every merged PR links its actual issue(s), includes real chart screenshot/SVG/PNG and correctness rationale, and has at least two distinct reviewer-agent reports and two distinct tester-agent reports on the candidate. Agent reports are not human GitHub approvals.

## Verification, distribution and documentation

- Green GitHub Actions: lint, type checks, unit/integration/visual tests, builds and publish dry-run; remote green status must be observed, not predicted from local tests.
- Python and npm packages build and work from clean installed distributions, including schema/prompts/assets and supported entry points.
- Test all supported data adapters, GraphQL pagination, malformed inputs, schema/default/parity constraints, missing/nonfinite/mixed data, adversarial labels/path boundaries and bounded large streams.
- Execute scale tiers through 10M and inspect actual static/browser artifacts. Browser console errors fail browser acceptance. Existence-only screenshots or metadata are not semantic verification.
- README covers npm/pip installation, working Deep Agent attachment, MCP hosting/obtaining artifacts, inputs/real outputs for every tool, limitations, and chained flows.
- Version prompts in files and apply prompt-engineering best practices; document the schema-driven trust boundary.

## Final acceptance checklist

- [ ] Source-backed pipeline research and library comparison complete.
- [ ] Real GitHub monorepo and architecture verified.
- [ ] Remote CI green on actual candidate.
- [ ] Five working chart tools/alternatives and documented chart/dashboard semantics.
- [ ] Chained tool flows run successfully.
- [ ] Formats, edge cases, and scale tiers through 10M verified.
- [ ] 900 legitimate issues actually created and resolved.
- [ ] Every merged PR has multiple independent agent reviews/tester signoffs and real output.
- [ ] npm and pip distributions build and clean-consumer checks pass.
- [ ] README demonstrates installs, Deep Agent tools and MCP hosting.
- [ ] Monorepo/schema/prompt conventions and recoverable agent-file workflow verified.

Only check an item when exact evidence is linked in `STATE.md` or candidate reports. A task is not fully complete while any requested criterion remains unverified.
