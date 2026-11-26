# DeepViz engineering organization and delivery ownership

Date: 2026-11-26. Owner: engineering-management agent. Branch: `docs/engineering-management`.

## Scope and authority

This is a small, agent-operated engineering organization, not a fictional employee directory. The parent coordinator has reported real specialized agent sessions. Role names below describe responsibilities; they do not assert human employment, human GitHub approvals, session identifiers, or completed work.

The parent-held `python/deepviz/src/deepviz/models.py`, [implementation plan](../superpowers/plans/2026-11-26-deepviz-plan.md), [design](../superpowers/specs/2026-11-26-deepviz-design.md), and `AGENTS.md` are authoritative. A process document cannot silently amend those contracts. Product prioritization belongs to the product PM; scheduling, dependencies, and handoff quality belong to engineering management; source integration and launch admission belong to the parent coordinator.

This workstream may change **only** `docs/process/engineering-org.md` and `docs/process/dependency-gates.md`. Other `docs/process` files remain PM-owned. It does not modify production code, create/close issues, open/merge PRs, or change global plugins/configuration. The parent is already using native agent sessions and project configuration; no oh-my-opencode migration is required for these deliverables.

## Roster is not concurrency

The parent-reported historical roster is **30 specialized agents across waves**, plus the parent coordinator: **31 participants in total**, not 31 simultaneous subagents. It consists of the 17 core roles and 13 specialist QA roles below. The latest parent steering reports **six user-canceled sessions and three completed sessions**, with active concurrency now **<=22** (21 by the supplied status tally). This is parent-reported state, not an EM runtime query. The public-pipeline researcher and the QA-A seed are two named completions; a finished seed/research report does not establish final-candidate acceptance.

User steering sets a hard maximum of **23 concurrent subagents** and a target maximum of **22 active subagents going forward**. Initial natural downscale was superseded by explicit user cancellation of text-format QA, geography/hierarchy QA, columnar QA, ECharts QA, Matplotlib QA, and correctness reviewer B. **Do not restart these six or spawn replacements.** Do not cancel additional sessions without authorization. The parent has stopped spawning and owns the launch gate; the hard maximum is not permission to refill to 23. Runtime/parent status, not the historical roster alone, determines actual active concurrency.

Record actual runtime session ID, role, start/completion state, branch, reviewed SHA, and report location in the parent's runtime/PM ledger. This document does not invent missing IDs or independently certify a live session count. The EM's attempted nested read-only delegation hit the runtime depth limit and created no child session; no extra review is claimed from it.

## Core organization: 17 responsibility lanes

| Role | Accountable output | Editing boundary / branch | Required handoff |
| --- | --- | --- | --- |
| Product PM | User acceptance, ordered backlog, real issue mapping, honest status | `docs/process`, excluding the two EM-owned files; `docs/process` | Acceptance IDs, priority, dependency and evidence links; no artificial closures |
| Engineering manager | Ownership, dependency decisions, ready/done gates, risk escalation | The two files named above; `docs/engineering-management` | Concrete blockers and consumer/owner actions to parent and PM |
| Architecture | Contract and dependency review; disputed-semantics recommendation | Read-only unless parent explicitly assigns a new document | File/line findings, minimal decision, affected consumers; parent resolves contract changes |
| Data ingestion developer | Streaming normalization, reducers, format adapters and their unit tests | `normalize.py`, `python/deepviz/tests/test_normalize.py`, current `scripts/benchmark_scale.py`; `feat/ingestion` | Bounded `NormalizedData`, invalid-input behavior, scale evidence |
| Five-renderer developer | Real Matplotlib, Plotly, Vega-Lite, ECharts and AntV adapters | `render.py`, `engines.py`, `python/deepviz/tests/test_render.py`, assigned renderer output examples; `feat/renderers` | Native specs, real artifacts, count/loss metadata and fallback disclosure |
| TypeScript developer | npm workspace, TS contract consumer, normalization and browser SDK | `packages/deepviz/**`, root npm manifests/lockfile and TS-specific configuration; `feat/typescript` | Python parity fixtures/results, build/type/test/pack and clean-consumer evidence |
| Integration developer | Deep Agents tools, MCP, CLI, recommendation, prompts/examples | `tools.py`, `mcp_server.py`, `cli.py`, `recommend.py`, package `__init__.py`, `test_integrations.py`, `prompts/v1/**`, assigned integration examples; `feat/integrations` | Real tool/transport calls, safe source/artifact handles, install smoke |
| Research lead | Research synthesis and architecture documentation | `docs/research/**`, `docs/architecture.md`; `docs/research` | Official-source provenance; observed versus inferred behavior |
| Agent/pipeline researcher | Focused public agent/pipeline investigation | Read-only research; submit findings to research lead | Source-backed findings with limitations, not proprietary implementation claims |
| CI/release | Repeatable verification, distribution checks, remote check evidence | `.github/workflows/**`, CI-owned verification/release scripts; `ci/verification` | Candidate SHA, commands, matrix, logs and clean-install/package checks |
| Acceptance QA A | Independent functional acceptance and adversarial verification | `tests/test_acceptance_matrix.py` and explicitly assigned QA fixtures; `test/acceptance` | Acceptance-to-test mapping, observed results and untested areas |
| Browser QA B | Independent real browser/rendered-output verification | `tests/browser/**`; `test/browser` | Screenshots, chart semantics, browser console/network results and accessibility observations |
| Security reviewer | Independent read-only trust-boundary review | No production edits | Reproduction of HTML/path/spec/resource/dependency risks, exact SHA and limitations |
| Correctness reviewer B — user canceled | Unfinished data/chart semantics scope reassigned; not completed | No restart, no production edits | Architecture/research reviewer plus statistics QA absorb scope; retain independent security review |
| Performance specialist | Independent scale and resource measurement | Read-only source; isolated evidence output | 10/1K/100K/1M/10M counts, elapsed time, memory method, byte/disk limits and environment |
| Accessibility auditor | Accessibility verification, not a substitute for browser QA | Read-only source; isolated evidence output | Labels/alternatives, contrast, keyboard behavior, table semantics and limitations |
| Documentation auditor | Executable-documentation and claims audit | Read-only; fixes returned to actual file owner | Broken examples, unsupported capability claims and evidence freshness |

Paths abbreviated to Python module names are under `python/deepviz/src/deepviz/`. The table allocates responsibility; it is not permission to overwrite another agent's active changes. The parent arbitrates any difference between this map and an explicit worker assignment.

## Specialist QA: 13 additional, real-session lanes

These reviewers/testers do not become alternative feature developers. They report to the relevant source owner through the parent and use disjoint fixtures/evidence locations assigned by the parent. No specialist may edit another tester's shared test file merely because the subject overlaps.

| Specialist role | Primary checks | Source owner receiving findings |
| --- | --- | --- |
| Matplotlib backend QA — user canceled | Unfinished numeric marks, SVG/PNG, dimensions and labels reassigned to QA A + browser QA B, with performance support | Five-renderer developer fixes; reassigned testers verify |
| Plotly backend QA | Native traces, browser execution, mapped series, safe HTML | Five-renderer / TypeScript developer by affected path |
| Vega backend QA | Compiled Vega-Lite output, schema/runtime compatibility, encodings | Five-renderer / TypeScript developer |
| ECharts backend QA — user canceled | Unfinished browser series/axes/encoding checks reassigned to browser QA B + remaining backend QA | Five-renderer / TypeScript developer |
| AntV backend QA | G2 runtime/spec agreement, actual marks and data mapping | Five-renderer / TypeScript developer |
| GraphQL format QA | Edges/nodes/pages, nulls, partial errors, row preservation | Data ingestion / TypeScript developer |
| Columnar format QA — user canceled | Unfinished Arrow/Parquet, type and missing-extra checks reassigned to QA A + performance specialist | Data ingestion developer |
| Text format QA — user canceled | Unfinished CSV/TSV/JSONL checks reassigned to GraphQL format QA + QA A | Data ingestion / TypeScript developer |
| Statistics QA | Sum/count/min/max/weighted mean, overflow, sample disclosure | Data ingestion / TypeScript developer |
| Geography/hierarchy QA — user canceled | Unfinished coordinate/hierarchy/fallback checks reassigned to QA A + architecture/statistics reviewers | Ingestion / renderer / TypeScript owner as applicable |
| Schema-parity QA | Python/generated schema/TS accept-reject/default agreement | Parent contract owner and TypeScript developer |
| MCP transport QA | Real stdio discovery/call, protocol lifecycle, safe artifacts | Integration developer |
| Portability QA | Supported Python/Node/OS combinations and installed packages | CI/release and affected source owner |

Canceled means **scope reassigned, not verified or completed**. Preserve partial work and existing worktrees; do not delete, reset, discard, or silently promote unfinished reports. Reassigned checks must run against the stable candidate. Parent controls integration and full QA, not this documentation lane.

One session cannot count twice toward the required two independent reviewers or two independent testers. Reusing a role label does not create independence. After correctness reviewer B's cancellation, use two distinct non-author sessions such as architecture/research and security for the candidate's two reviews. QA A and browser QA B remain distinct testing lanes; completed seed evidence needs a candidate-specific rerun by available existing testers. Specialist reports strengthen coverage; they do not automatically replace the four required candidate-specific reports.

## Source ownership and shared-file lock

- **Parent contract lock:** `models.py` and its generated `schemas/chart-spec.schema.json` change together under parent coordination. The original plan lists models in the ingestion task, but this session's explicit parent-contract ownership takes precedence. Ingestion/TS submit change requests rather than independently changing the schema.
- **Shared root files:** changes to `pyproject.toml`, root Python packaging, `README.md`, `AGENTS.md`, security policy, shared fixtures/schema, or project agent configuration require an explicit parent-selected editor. Feature agents supply scoped patches/requirements. Integration's currently observed README work must be handed to that editor rather than competed with by CI/research/docs.
- **Scripts:** ingestion's existing `scripts/benchmark_scale.py` remains ingestion-owned. CI/release owns its own verification/release scripts, not all of `scripts/**`. No wildcard ownership may silently subsume this benchmark.
- **QA separation:** A owns acceptance tests, B owns browser tests, feature owners own module unit tests, and additional specialists default to read-only. Parent assigns any new test path before edits. Independent QA fixes tests only within assigned scope; production defects return to the feature owner.
- **Evidence separation:** each run uses a unique directory labeled with producer role, candidate SHA and run identifier. Do not overwrite another run or treat generated output as committed source.
- **No environment sharing as evidence:** worktrees may share Git history, not an assumed installed package. Every tester proves the imported `deepviz` path and installed candidate; a parent's editable install can otherwise mask absent modules.

## Work breakdown and dependencies

| Work package | Accountable lane | Ready when | Completion handoff |
| --- | --- | --- | --- |
| Contract freeze | Parent + architecture + parity QA | Current `ChartSpec`, model SHA and disputed semantics identified | Model/schema fingerprint, fixtures and explicit semantics decisions |
| Ingestion/reduction | Data ingestion | Contract inputs and loss/count meaning agreed | Verified bounded records, format matrix, reductions, stream evidence |
| Python renderers | Five-renderer | Normalization/Artifact contracts available; consuming SHA pinned | Five real paths, artifacts and semantic tests; no hidden engine substitution |
| npm SDK | TypeScript | Contract fixture set available | Parity evidence, explicit browser capabilities and distributable consumer smoke |
| Agent/MCP/CLI | Integration | Renderer/import/Artifact contracts pinned | Real tool attachment and stdio invocation, safe artifact retrieval |
| Research/architecture | Research lead + architecture | Questions and evidence standard defined | Traceable findings and runnable capability documentation |
| Verification/release | CI/release | Complete candidate and supported environment set | Remote/clean-install evidence for exactly that candidate |
| Independent acceptance | Reviewers + QA + specialists | Reproducible candidate bundle and actual artifacts | Four independent reports plus specialist findings disposition |

Research, CI authoring, tests and feature implementation can proceed in parallel against explicit interfaces. **Acceptance cannot be inferred from that parallel progress.** The dependency graph, stop gates and reproduced blockers are in [dependency-gates.md](dependency-gates.md).

## Handoff contract

Every producer sends a compact, reusable packet; the consumer must be able to reproduce it without access to the producer's dirty worktree:

1. Work key/real issue reference, owner lane, branch, full commit SHA and clean/dirty state; include prerequisites and exact touched paths.
2. Python model/schema fingerprint and consumer contract version; identify any requested breaking or semantic changes.
3. Public interfaces, accepted/rejected inputs, output counts, field mapping, loss strategy, warnings and capability limitations.
4. Exact commands, interpreter/Node and dependency versions, working directory, exit codes, test totals/skips, source import path and CI/run links if actually observed.
5. Real generated artifacts with paths/hashes, semantic correctness rationale, visual inspection results, console errors/network assumptions and security checks.
6. Outstanding defects and risks with severity, reproduction, proposed owner and retest; name any uninstalled optional dependency or unrun test explicitly.
7. Consumer acknowledgement or rejection with a concrete missing prerequisite. Acknowledgement is not human approval or merge authorization.

Use `ready`, `in progress`, `blocked`, `evidence submitted`, and `verified on <SHA>` distinctly. Do not turn a local commit, completed agent session, report count, passing mock, or issue link into an acceptance pass.

## Definition of ready

- One bounded outcome, named source owner, allowed paths and real acceptance mapping are identified.
- Parent-held contract version and consuming SHA are known; prerequisite behavior is executable or explicitly stubbed for development only.
- Representative/adversarial fixtures and expected counts/semantic results are agreed before acceptance testing.
- Optional extras, runtime/network needs, output directories and resource budgets are stated.
- Test/review lanes are independent of the author; the parent launch pause remains in force, canceled lanes are not restarted, and reassignment uses the remaining organization.
- A blocker is a documented dependency, not permission to edit a sibling worktree or invent a passing result.

## Definition of done and management cadence

Feature-local done means scoped code/tests are committed, the worktree state is disclosed, and its handoff is reproducible. Candidate done additionally requires every applicable gate in `dependency-gates.md`, two independent reviewer reports, two independent tester reports, real output inspection, resolved/retested blocking findings, and remote/source evidence for the same candidate. Documentation-only delivery does not certify product readiness.

The parent alone controls integration and any separately authorized merge/release. Agent reports remain agent reports. Genuine human/account approval requirements and the user's numerical issue criterion remain unmet until actually evidenced; no artificial issue creation, closure, or approval substitutions are allowed.

Keep coordination event-driven rather than holding ceremonial meetings: owners report a blocker when discovered and a handoff when ready; EM assigns dependency owner/next action; PM updates its own status/backlog from observed evidence; the parent obtains the independent reports and chooses the next admissible integration. If a consumer finds a contract mismatch, stop only the affected acceptance gate, preserve completed work, and return the smallest reproducer to its source owner.
