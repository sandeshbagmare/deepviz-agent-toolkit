# DeepViz Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development or executing-plans to implement this plan task-by-task. Autonomous subagent execution was requested by the user.

**Goal:** Deliver tested schema-driven visualization tools with Python, npm, Deep Agents, and MCP interfaces.

**Architecture:** Shared schema drives bounded normalization and five independent renderers. Python owns ingestion, aggregation, and integration; TypeScript offers browser spec generation and HTML artifacts.

**Tech Stack:** Python 3.11+, Pydantic, NumPy, Matplotlib, Plotly, vl-convert, MCP, TypeScript, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-26-deepviz-design.md`

## Global Constraints
- Keep credentials out of the repository and logs.
- Do not claim unobserved tests, issue closures, or approvals.
- Preserve bounded output for ten-million-point inputs and record lossy decisions.
- Use separate feature branches/worktrees and evidence-bearing PRs.

## Review Focus
- GraphQL pagination and nested arrays must not silently lose rows.
- NaN, Infinity, mixed values, and missing fields require deterministic behavior.
- Malicious title/cell strings must not become executable HTML.
- Large streams must not be materialized before reduction.
- Different engines must consume the same mapped/reduced data.

### Task 1: Contracts, ingestion, and aggregation
Files: `python/deepviz/src/deepviz/{models,normalize}.py`, `schemas/chart-spec.schema.json`, `python/deepviz/tests/test_normalize.py`.
Write failing fixture-driven tests; implement the shared interfaces; test scale and invalid input; commit the passing contract.

### Task 2: Five renderer alternatives
Files: `python/deepviz/src/deepviz/{render,engines}.py`, `python/deepviz/tests/test_render.py`, `examples/outputs/`.
Write failing semantic and output tests; implement Matplotlib/Plotly/Vega-Lite/ECharts/AntV adapters using the shared contract; generate actual artifacts; inspect and test them; commit.

### Task 3: TypeScript package
Files: `packages/deepviz/`, root npm workspace and TypeScript configuration.
Implement schema validation, bounded normalization, engine specs, HTML output, dashboard composition, test shared fixtures, build and pack.

### Task 4: Agent/MCP interfaces and prompts
Files: `python/deepviz/src/deepviz/{tools,mcp_server,cli}.py`, `prompts/v1/`, `examples/`.
Write integration tests before implementation; expose safe file artifacts, five tools and multi-tool flow; verify MCP discovery/call and Deep Agents attachment.

### Task 5: Research, CI, release documentation
Files: `docs/research/`, `docs/architecture.md`, `.github/workflows/ci.yml`, `README.md`, `scripts/`.
Ground research in official sources; implement CI and deterministic visual checks; build both distributions; record independently verified checks and limitations.

### Task 6: Independent review and completion audit
Multiple reviewer and tester agents inspect each PR and rendered outputs before merge. File real defects, fix and retest. Audit remote issue/PR/workflow state and every user success criterion; leave unmet work explicitly open rather than manufacturing evidence.
