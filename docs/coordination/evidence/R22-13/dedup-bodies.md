# Fresh open-issue deduplication inventory

Observed 2026-11-27T15:25:45.656817+00:00; 31 actual open issues, 1 open PR entries; complete pagination.
Marker `deepviz-r22-finite-svg-range` exact matches: 0.

## #1: [Epic] Shared contracts and loss-aware bounded ingestion
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/1

<!-- deepviz-key: EPIC-FOUNDATION -->
# EPIC-FOUNDATION

## Outcome
Every engine receives the same validated, bounded records and truthful reduction metadata.

## Coordination
- Suggested owner lane: core agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.

## Acceptance criteria
- [ ] CONTRACT, INPUT-FORMATS, INPUT-GRAPHQL and STREAMING are independently verified and closed with evidence.
- [ ] Versioned schema, Python public API and documented normalization semantics agree.
- [ ] Raw streams are not fully materialized before reduction; lossy decisions are surfaced.

## Required evidence
- Linked child PRs and schema/fixture test reports
- Scale and edge-case results at exact reviewed commits

## Child work
- [ ] #5 - CONTRACT: Version and validate the shared ChartSpec and artifact contracts
- [ ] #6 - INPUT-FORMATS: Normalize records, columns and delimited/line-oriented inputs deterministically
- [ ] #7 - INPUT-GRAPHQL: Normalize nested JSON and GraphQL edges/nodes without dropping pages
- [ ] #8 - STREAMING: Reduce large streams before bounded record materialization

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #2: [Epic] Five renderer alternatives and interoperable browser artifacts
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/2

<!-- deepviz-key: EPIC-VISUALIZATION -->
# EPIC-VISUALIZATION

## Outcome
Users can choose Matplotlib, Plotly, Vega-Lite, ECharts or AntV G2 against one mapped/reduced dataset.

## Coordination
- Suggested owner lane: rendering and TypeScript agents (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.

## Acceptance criteria
- [ ] All five renderer stories and both TypeScript stories have verified acceptance evidence.
- [ ] Unsupported kind/engine combinations fail explicitly instead of silently changing meaning.
- [ ] Committed SVG/PNG/screenshots demonstrate the actual generated artifacts and dashboard behavior.

## Required evidence
- Cross-engine parity report
- Inspected output artifacts and browser test report

## Child work
- [ ] #9 - RENDER-MPL: Render real Matplotlib static artifacts from the shared contract
- [ ] #10 - RENDER-PLOTLY: Render interactive Plotly artifacts with explicit runtime requirements
- [ ] #11 - RENDER-VEGA: Render validated Vega-Lite specifications and real artifacts
- [ ] #12 - RENDER-ECHARTS: Render safe ECharts options and browser artifacts
- [ ] #13 - RENDER-ANTV: Render real AntV G2 specifications and browser artifacts
- [ ] #14 - TS-CONTRACT: Validate shared schema fixtures and bounded normalization in TypeScript
- [ ] #15 - TS-BROWSER: Build safe browser engine artifacts and composed dashboards in TypeScript

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #3: [Epic] Deep Agents and stdio MCP visualization workflows
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/3

<!-- deepviz-key: EPIC-INTEGRATIONS -->
# EPIC-INTEGRATIONS

## Outcome
Agents discover safe tools, call them with structured inputs and receive bounded artifact metadata.

## Coordination
- Suggested owner lane: integrations agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.

## Acceptance criteria
- [ ] TOOLS, MCP and PROMPTS acceptance criteria are independently verified.
- [ ] Integration uses real package APIs rather than mock-only compatibility claims.
- [ ] Multi-tool flow, validation failures, artifact paths and dependency requirements are documented.

## Required evidence
- Real integration transcripts with commands and versions
- Independent tester reports

## Child work
- [ ] #16 - TOOLS: Expose five real Deep Agents visualization tools with safe artifacts
- [ ] #17 - MCP: Serve visualization tools over a real stdio MCP session
- [ ] #18 - PROMPTS: Version safe chart-selection prompts and runnable agent examples

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #4: [Epic] Secure, measurable and independently evidenced release readiness
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/4

<!-- deepviz-key: EPIC-DELIVERY -->
# EPIC-DELIVERY

## Outcome
Release claims are backed by repeatable checks, inspected outputs and an honest unmet-criteria audit.

## Coordination
- Suggested owner lane: parent coordinator with QA/research/process owners (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.

## Acceptance criteria
- [ ] RESEARCH, CI, SECURITY, SCALE, VISUAL-QA, PY-PACKAGE, NPM-PACKAGE, REVIEW-GATE, PROCESS and REVIEW-PROVENANCE are verified.
- [ ] Each proposed merge has two independent reviewer-agent reports, two tester-agent reports and committed visual evidence embedded in its PR body.
- [ ] The unmet 900-issue requirement remains explicit; independent agent reports satisfy the review criterion without inventing a distinct-account GitHub approval requirement.

## Required evidence
- Remote workflow/build state and package-install reports
- Final open/closed issue and PR audit excluding PRs from issue counts

## Child work
- [ ] #19 - RESEARCH: Ground architecture and competitor research in dated official sources
- [ ] #20 - CI: Gate Python and TypeScript changes with real lint, type, test and build CI
- [ ] #21 - SECURITY: Prove untrusted specs, HTML values and filesystem paths stay within safe boundaries
- [ ] #22 - SCALE: Measure 10 through 10M input rows on the bounded streaming path
- [ ] #23 - VISUAL-QA: Inspect real renderer outputs and commit reproducible visual evidence
- [ ] #24 - PY-PACKAGE: Build and clean-install Python wheel/sdist with real entrypoint smoke tests
- [ ] #25 - NPM-PACKAGE: Build and clean-install the npm tarball with usable types and exports
- [ ] #26 - REVIEW-GATE: Enforce evidence-bearing PRs with two reviewer and two tester reports
- [ ] #27 - PROCESS: Publish a traceable backlog, evidence policy and honest completion tracker

- [ ] #29 - REVIEW-PROVENANCE: [Constraint/workaround] Preserve independent agent-report provenance without GitHub self-approval

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #5: Version and validate the shared ChartSpec and artifact contracts
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/5

<!-- deepviz-key: CONTRACT -->
# CONTRACT

## Outcome
Python, TypeScript and integrations share one explicit schema and metadata contract.

## Coordination
- Suggested owner lane: core agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #1 (EPIC-FOUNDATION).

## Acceptance criteria
- [ ] Commit schema version 1 and positive/negative fixtures for declared kinds, mappings, nested charts and bounds.
- [ ] Pydantic models and JSON Schema agree on required fields, defaults and invalid values.
- [ ] NormalizedData and Artifact expose input/output counts, strategy, warnings and safe filesystem paths.
- [ ] Public names/signatures match the design or carry an explicit documented decision.

## Required evidence
- Schema validation tests and exact test command
- Fixture parity report

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #6: Normalize records, columns and delimited/line-oriented inputs deterministically
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/6

<!-- deepviz-key: INPUT-FORMATS -->
# INPUT-FORMATS

## Outcome
A caller can normalize ordinary tabular and streaming file shapes without silent row loss.

## Coordination
- Suggested owner lane: core agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #1 (EPIC-FOUNDATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Cover records, column-oriented inputs, CSV, TSV, JSONL and explicit path/mapping selection with fixtures.
- [ ] Define deterministic treatment of nulls, missing keys, mixed values, NaN and infinity.
- [ ] Malformed rows and missing mapping fields produce actionable errors or counted warnings, not silent omission.
- [ ] Optional Arrow/Parquet behavior is tested or explicitly documented as unavailable with dependency guidance.

## Required evidence
- Fixture-based normalization tests including malformed and empty inputs
- Input/output count assertions

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #7: Normalize nested JSON and GraphQL edges/nodes without dropping pages
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/7

<!-- deepviz-key: INPUT-GRAPHQL -->
# INPUT-GRAPHQL

## Outcome
Nested and paginated API results become explicit records using documented mapping rules.

## Coordination
- Suggested owner lane: core agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #1 (EPIC-FOUNDATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Fixtures cover GraphQL edges/node, nodes arrays, multiple pages and nested array/path selection.
- [ ] Flattening rules for colliding keys and nested arrays are deterministic and documented.
- [ ] Hierarchy and geographic record adapters have explicit accepted shapes and mapping failures.
- [ ] Tests prove all selected pages contribute to input counts and no arbitrary remote URL is fetched.

## Required evidence
- Nested/pagination fixtures and assertions
- Documented mapping examples

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #8: Reduce large streams before bounded record materialization
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/8

<!-- deepviz-key: STREAMING -->
# STREAMING

## Outcome
Large inputs have bounded renderer payloads with disclosed sampling and aggregation semantics.

## Coordination
- Suggested owner lane: core agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #1 (EPIC-FOUNDATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] An iterator/JSONL path reduces records before creating the bounded renderer list.
- [ ] Requested aggregation and max_points are honored with deterministic strategy metadata.
- [ ] Counts reflect original inputs and retained/reduced outputs; warnings disclose lossy choices.
- [ ] Tests detect accidental list/materialization of an unbounded stream and cover empty/invalid bounds.

## Required evidence
- Streaming regression tests
- Memory/time benchmark linked from SCALE

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #9: Render real Matplotlib static artifacts from the shared contract
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/9

<!-- deepviz-key: RENDER-MPL -->
# RENDER-MPL

## Outcome
Users obtain readable static images without browser runtime requirements.

## Coordination
- Suggested owner lane: rendering agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #2 (EPIC-VISUALIZATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Supported chart kinds produce actual nonempty PNG/SVG artifacts from bounded normalized records.
- [ ] Mapped fields, titles, units, category ordering and reduction metadata remain truthful.
- [ ] Themes and labels remain readable; unsupported kinds and missing fields fail explicitly.
- [ ] At least one composed/example artifact is opened and inspected; dependencies are disclosed.

## Required evidence
- Renderer unit/integration tests
- Committed inspected PNG/SVG and dimensions

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #10: Render interactive Plotly artifacts with explicit runtime requirements
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/10

<!-- deepviz-key: RENDER-PLOTLY -->
# RENDER-PLOTLY

## Outcome
Users can inspect Plotly charts with the same mappings and reductions as other engines.

## Coordination
- Suggested owner lane: rendering agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #2 (EPIC-VISUALIZATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Supported kinds generate actual Plotly figures and usable HTML artifacts.
- [ ] Shared fixtures assert series, axes and values, including category and missing-value handling.
- [ ] Remote or bundled runtime dependencies and any static-export extras are documented.
- [ ] Untrusted strings cannot execute in the output; an actual browser artifact is inspected.

## Required evidence
- Plotly structure/security tests
- Committed browser screenshot and HTML fixture

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #11: Render validated Vega-Lite specifications and real artifacts
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/11

<!-- deepviz-key: RENDER-VEGA -->
# RENDER-VEGA

## Outcome
A declarative Vega-Lite adapter preserves the shared schema semantics.

## Coordination
- Suggested owner lane: rendering agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #2 (EPIC-VISUALIZATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Supported kinds emit valid Vega-Lite encodings and actual renderable output.
- [ ] Data values and types match shared fixtures; unsupported combinations fail explicitly.
- [ ] Optional vl-convert/runtime requirements and offline behavior are documented.
- [ ] Inspect and commit at least one real SVG/PNG or browser screenshot, not a hand-drawn stand-in.

## Required evidence
- Spec validation/render tests
- Committed inspected render artifact

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #12: Render safe ECharts options and browser artifacts
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/12

<!-- deepviz-key: RENDER-ECHARTS -->
# RENDER-ECHARTS

## Outcome
Users can choose ECharts without changing data normalization or mapping semantics.

## Coordination
- Suggested owner lane: rendering agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #2 (EPIC-VISUALIZATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Supported kinds emit actual ECharts options and executable browser artifacts using the legitimate runtime.
- [ ] Fixture assertions verify series data, legends, axes and dashboard/composition behavior where supported.
- [ ] No model-authored JavaScript callback/eval path is accepted; runtime loading is explicit.
- [ ] Browser checks report console failures and include a committed inspected screenshot.

## Required evidence
- Option parity/security tests
- Browser test report and screenshot

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #13: Render real AntV G2 specifications and browser artifacts
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/13

<!-- deepviz-key: RENDER-ANTV -->
# RENDER-ANTV

## Outcome
AntV G2 is a genuine fifth renderer rather than a renamed fallback engine.

## Coordination
- Suggested owner lane: rendering agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #2 (EPIC-VISUALIZATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Supported kinds produce valid G2 specifications and load the actual G2 runtime.
- [ ] Mappings, reduced values and metadata match shared fixtures and other adapters.
- [ ] Unsupported kinds and unavailable runtime dependencies are explicit; no fake visual fallback is used.
- [ ] An actual browser render is tested, inspected and committed as a screenshot.

## Required evidence
- G2 spec/semantic tests
- Browser execution report and screenshot

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #14: Validate shared schema fixtures and bounded normalization in TypeScript
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/14

<!-- deepviz-key: TS-CONTRACT -->
# TS-CONTRACT

## Outcome
The npm interface rejects invalid inputs consistently with the Python contract.

## Coordination
- Suggested owner lane: TypeScript agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #2 (EPIC-VISUALIZATION).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] Use the same versioned schema and shared positive/negative fixtures as Python.
- [ ] Implement and test documented bounded normalization with truthful counts/warnings/strategy.
- [ ] Strict TypeScript checking and unit tests cover mapping, invalid kinds and unsupported values.
- [ ] Differences from Python semantics are explicit and tested rather than accidental.

## Required evidence
- Typecheck and unit-test commands
- Cross-language fixture parity report

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #15: Build safe browser engine artifacts and composed dashboards in TypeScript
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/15

<!-- deepviz-key: TS-BROWSER -->
# TS-BROWSER

## Outcome
JavaScript callers can generate browser charts and dashboards from the shared spec.

## Coordination
- Suggested owner lane: TypeScript agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #2 (EPIC-VISUALIZATION).
- Depends on: #14 (TS-CONTRACT).

## Acceptance criteria
- [ ] Document and test actual engine support rather than implying all Python-only exports exist in the browser.
- [ ] Dashboard composition preserves per-chart titles, mappings and bounded datasets.
- [ ] HTML serialization escapes untrusted titles/data and rejects executable configuration.
- [ ] An installed/built package generates an inspected browser artifact and committed screenshot.

## Required evidence
- Browser/spec unit tests and HTML security tests
- Build smoke test and screenshot

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #16: Expose five real Deep Agents visualization tools with safe artifacts
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/16

<!-- deepviz-key: TOOLS -->
# TOOLS

## Outcome
A Deep Agent attaches actual structured tools and receives artifact metadata rather than arbitrary code execution.

## Coordination
- Suggested owner lane: integrations agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #3 (EPIC-INTEGRATIONS).
- Depends on: #5 (CONTRACT).

## Acceptance criteria
- [ ] create_tools(output_dir) returns five renderer tools using real compatible integration APIs.
- [ ] Tool schemas validate ChartSpec inputs and surface render/normalization errors predictably.
- [ ] Safe output directories, bounded metadata and renderer/dependency errors are tested.
- [ ] A real attachment and multi-tool invocation flow is demonstrated; mocks alone do not satisfy acceptance.

## Required evidence
- Integration command and package versions
- Tool discovery/invocation transcript

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #17: Serve visualization tools over a real stdio MCP session
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/17

<!-- deepviz-key: MCP -->
# MCP

## Outcome
MCP clients discover and call the toolkit using a genuine protocol server.

## Coordination
- Suggested owner lane: integrations agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #3 (EPIC-INTEGRATIONS).
- Depends on: #16 (TOOLS).

## Acceptance criteria
- [ ] A stdio client initializes, lists tools and successfully calls an actual renderer tool.
- [ ] Protocol stdout remains valid; diagnostics are not mixed into the message stream.
- [ ] Invalid requests, unsafe paths and missing optional dependencies return structured errors.
- [ ] CLI/entrypoint and startup instructions work from a built/installed package.

## Required evidence
- Real client/server discovery and call test
- Installed-entrypoint smoke transcript

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #18: Version safe chart-selection prompts and runnable agent examples
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/18

<!-- deepviz-key: PROMPTS -->
# PROMPTS

## Outcome
Users see reproducible workflows that choose charts, reduce inputs and explain limitations.

## Coordination
- Suggested owner lane: integrations agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #3 (EPIC-INTEGRATIONS).
- Depends on: #16 (TOOLS).

## Acceptance criteria
- [ ] Commit prompts/v1 and runnable examples for normalization, chart selection and multi-tool workflow.
- [ ] Prompts forbid arbitrary code/URL execution and require disclosure of lossy reduction.
- [ ] Examples use the actual tool schemas and declare credentials, optional extras or network needs.
- [ ] Document chart-choice rationale, artifact paths and a failure/recovery example.

## Required evidence
- Executed examples or explicit unavailable-prerequisite notes
- Prompt/version documentation review

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #19: Ground architecture and competitor research in dated official sources
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/19

<!-- deepviz-key: RESEARCH -->
# RESEARCH

## Outcome
Architecture choices and public comparisons are traceable without claiming access to proprietary internals.

## Coordination
- Suggested owner lane: research agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).

## Acceptance criteria
- [ ] Research cites primary documentation with access dates for five renderers, Deep Agents and MCP.
- [ ] Separate observed public behavior, documentation facts, inferences and unknown proprietary internals.
- [ ] Record runtime/dependency, licensing, scale and output-format trade-offs without invented benchmark claims.
- [ ] Architecture and feature support claims agree with implemented/tested capabilities or are clearly future work.

## Required evidence
- Committed source-linked research notes
- Claim-to-source and capability review

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #20: Gate Python and TypeScript changes with real lint, type, test and build CI
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/20

<!-- deepviz-key: CI -->
# CI

## Outcome
Remote PR checks run the same meaningful verification documented locally.

## Coordination
- Suggested owner lane: parent/core and TypeScript owners (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).

## Acceptance criteria
- [ ] Workflow runs Python lint/type/unit/integration and TypeScript type/test/build/package checks as applicable.
- [ ] Visual/security/scale smoke checks are explicit; expensive full benchmarks have a documented invocation.
- [ ] Use minimal workflow permissions and no committed secrets; optional dependency failures are visible.
- [ ] A remote workflow run on the proposed commit is recorded, or its real blocker stays open.

## Required evidence
- Workflow file and remote run URL/status
- Local-to-CI command mapping

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


### Comment 7221697848
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/20#issuecomment-7221697848

<!-- deepviz-r22-ci-45928608970 -->
## Evidence-backed CI triage — audited run, not current-head approval

Agent QA/backlog-manager comment under the R22 assignment. **Keep #20 open.** This is not a human approval, a source fix, or a claim that the current candidate passes.

### Observed failure and source

[Verification run 45928608970, attempt 1](https://github.com/sandeshbagmare/deepviz-agent-toolkit/actions/runs/45928608970) completed **failure** for head `5340bc69b7203ad7a9166543062482d819f9b705`. The checkout was PR merge `aa66ea97c1184554613d14e873e4cc34e54453b0`; official commit/compare GETs confirmed its entire tree equals the head tree (`7aecbc5f4e8a105d296b413d7c70c662ce54794f`, no changed files).

| Python | Unit failures / passes | Unit skip / deselected | Integration |
| --- | --- | --- | --- |
| 3.11 | **38 / 2456** | 1 / 550 | **SKIPPED** |
| 3.12 | **36 / 2458** | 1 / 550 | **SKIPPED** |
| 3.13 | **240 / 2254** | 1 / 550 | **SKIPPED** |

All three first fail step 11, **Unit and contract tests**, with `test_backend_antv.py:201`: expected dashboard payload types `[interval, line, interval]`, actual middle type **`view`**. The native implementation deliberately contains line + point children in that view; the preceding unique-container/manifest assertions passed, but the later child-value assertion was not reached. Unit process exit was **1**. Lint/types/schema/CI-negative-control steps succeeded; eight other jobs succeeded. Neither those successes nor the **51 + 27 evidence-integrity checks** constitute full-product green CI. The unit skip's reason is not established by these logs.

### Seven disposition groups — existing issues, not new tickets

**314 failure instances / 242 distinct node IDs** collapse into the seven groups below. These are triage groups, not seven completed fixes or proven independent root causes. Counts are Python **3.11 / 3.12 / 3.13**.

| Group; counts; existing scope | Owner/dependency and strict minimum acceptance |
| --- | --- |
| AntV view-wrapper oracle; **1/1/1**; #13, #23 | R04 owns the existing-oracle decision/integration; role08's released `_antv` production scope remains exclusive. Validate three unique containers, nested line + point marks and exact independent child values; retain wrong-ID/wrong-value controls. Do not flatten correct marks merely to satisfy an old shape assertion. |
| Deep JSON recursion boundary; **2/0/0**; #16, #17, #21 | Eligible role18 only after its prior checkpoint/eligibility; role10 remains an independent tester. Both 1500-level inline Python JSON and JSON text must reject with actionable `ValueError` (`deep`/`nest`), not leaked `RecursionError`, on 3.11–3.13. Preserve valid Unicode, handles/files, raw-byte, duplicate-key and stdio recovery controls. No global recursion-limit workaround. |
| N17 serialization-order observation; **1/1/1**; #21, #22 | R04 render/budget policy. The old observation expects an invalid wide row to serialize before rejection; actual capture is empty. Establish correct pre-serialization rejection and cleanup with a valid-small-row positive control before changing the oracle. Never widen budgets or remove the early guard to make that observation pass. |
| Vega standalone-child title scope; **10/10/10**; #11, #23 | R04 existing-matrix decision; role17's independent title-scope controls. Pair child specs/records strictly; check each child title in its own compiled output and parent + both child titles in the complete SVG, with real marks. Keep wrong-child, metadata-only, script/event and missing-title negatives. |
| ECharts numeric line/area x oracle; **20/20/20**; #12, #23 | R04 existing-matrix decision; role03's independent controls. Require exact numeric values/types/counts and nonuniform `1,2,10` spacing; retain categorical-bar/string/time controls and browser geometry/console checks. Do not stringify both sides to hide a mismatch. |
| Field-name envelope policy; **4/4/4**; #5, #14, #22 | R04 decides/documents the language-specific policy; role04 independently tests it; normalizer production remains exclusive. The old 64 KiB key positives hit Python's 4 KiB name guard. If that policy is retained, adjust only key-boundary expectations; preserve 64 KiB **cell** limits, multibyte/flattening, early-consumption/state/memory negatives. No blind source-limit widening. |
| Python 3.13 SVG comment-title portability; **0/0/204**; #9, #23 | R04 existing SVG/N09-oracle policy plus independent portable-parser/visual QA. This includes **4 synthetic valid-comment positives failing before mutation**, 14 gallery cases and 186 matrix/text/stream cases. Reproduce portable comment/text extraction on 3.11–3.13, retain title/geometry and missing/altered/script/event negatives, and inspect actual SVG/PNG. No 3.13 skip, manifest-only title acceptance or undiagnosed dependency pin. The underlying CPython mechanism was not locally reproduced by this PM. |

### Acceptance checklist for the manager

- [ ] Disposition each group against its existing issue and current exclusive source owner; preserve original RED evidence and use strict positive/negative controls for any justified oracle/policy correction. Respect the retained allocation/security work and role18 eligibility; do not give production work to tester09/10.
- [ ] On the **actual proposed integrated head**, run all relevant Python 3.11–3.13 unit **and integration** gates, schema/lint/types, applicable npm build/type/test/package and visual/security/streaming checks. An integration step skipped after unit failure is not a pass. Record exact commands, totals/skips, source and new remote run/check URLs.
- [ ] For the planned focused #30 contract slice, name its real contract-only check scope; do not label a filtered slice full-toolkit verification. Require two genuine independent reviewer-agent reports and two tester-agent reports at the actual focused head, output/correctness evidence where applicable, and observed required checks before R04 merges to `main`.
- [ ] Close only the acceptance scope actually proven after the manager verifies merge/default ancestry and evidence. Do not close this broad CI issue on branch existence, partial passes or the old run.

Published evidence: [full disposition](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/37a27cdfbb0d500cc4e2642bb403d68a145fbb21/docs/coordination/reports/R15-19-ci-failure-disposition.md), [exact classified failures and acceptance](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/b9534eab21fa13a37cb8f383b6691596355ef2b1/docs/coordination/evidence/R15-19/classified-failures-and-acceptance.json), [actual publication receipt](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/37a27cdfbb0d500cc4e2642bb403d68a145fbb21/docs/coordination/evidence/R15-19/publication-receipt.json).

**Limits:** this PM did not test later `7bcfb2d` or `6c72cec`, create a focused PR, rerun tests/log downloads, or verify a newer CI result. PR31's draft status is a dated observation, not a fresh PR query. QA12's density bug and QA20's Plotly literal-text bug remain their exclusive filing scopes; this comment creates neither. The 900 genuinely created **and resolved** issue goal remains unmet; test cases are not tickets.


## #21: Prove untrusted specs, HTML values and filesystem paths stay within safe boundaries
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/21

<!-- deepviz-key: SECURITY -->
# SECURITY

## Outcome
Model-authored inputs cannot execute arbitrary code, escape output roots or overwrite unrelated files.

## Coordination
- Suggested owner lane: parent with core/rendering/TypeScript/integrations owners (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).

## Acceptance criteria
- [ ] Negative tests cover script/title/cell injection, script-closing sequences and dangerous configuration values.
- [ ] Reject traversal, absolute-path escape and arbitrary remote-URL/code execution pathways.
- [ ] Artifact creation avoids unrelated-file overwrite and documents optional network-loaded runtimes.
- [ ] Review dependencies, diagnostics and packaging for accidental credential disclosure.

## Required evidence
- Named negative tests and results
- Independent security review with exact commit

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


### Comment 7221530866
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/21#issuecomment-7221530866

<!-- deepviz-r04-dense-preflight-20261127 -->
## Reproduced P1 sub-work item: sparse rows amplify into a dense table before resource checks

Source owner/integration manager: **R04** (`fix/r12-dense-table-budget`); actual GitHub account assignee is the project maintainer, not an invented independent approval.

Minimal public repro: `render([{f"f{i}": i} for i in range(128)], {"kind":"table","aggregation":"none"}, "echarts", NEW_OUTPUT)` (also through ToolSession). 1700B/128 sparse records imply128 union columns and16,512 expanded header/body cells. Before:16512 native graphics,30,698,790B traced Python allocations/3.8151666s. Expected: explicit rejection BEFORE Cartesian/native/HTML/figure/output-directory allocation, preserve caller files, no silent truncation.

Permanent new tests were genuinely18 RED/7 positive controls then25 GREEN. Published source d5b68c470416f93127c8187e8111d0d27d20b108 is integrated as **1c721bb6497746641b897eb2eb938cfad52068d2** in draft PR #31. Guard is10,000 expanded cells including headers and16MiB estimated table bytes, NOT a total-memory ceiling. Actual same public tool fixture now rejects with no artifacts/caller overwrite;69,587B per-call Python tracemalloc peak/0.0114637s (not OS RSS/native/browser memory).

[Exact permanent regression](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/1c721bb6497746641b897eb2eb938cfad52068d2/python/deepviz/tests/test_r12_table_budget.py) ? [source/output/failure evidence, five actual images and reproduction](https://github.com/sandeshbagmare/deepviz-agent-toolkit/tree/6c72cec40e3feb8d710ab55167453194f643d650/docs/coordination/evidence/R17-integrated).

**Status: candidate fix implemented and author/integration-tested, NOT closed/merged/release-approved.** Full non-scale source7bc still36failed/3043passed/5skipped/9deselected. Independent unchanged pre-output controls are being retested by QA05; final two-reviewer/two-tester and green-CI/default-merge gates remain. This does not close the broader security issue or the separate Plotly/MCP findings.


## #22: Measure 10 through 10M input rows on the bounded streaming path
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/22

<!-- deepviz-key: SCALE -->
# SCALE

## Outcome
Scale claims describe measured processing and retained marks instead of promising ten million browser marks.

## Coordination
- Suggested owner lane: parent/core owner with independent testers (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).
- Depends on: #8 (STREAMING).

## Acceptance criteria
- [ ] Run and record 10, 1K, 100K, 1M and 10M input scales using a generated/streamed source.
- [ ] Report environment, command, wall time, memory measurement method and input/output counts.
- [ ] Verify bounded renderer payloads and disclose aggregation/sampling at every scale.
- [ ] Failures, unavailable memory metrics and unrun engines/scales are explicit, not extrapolated as passes.

## Required evidence
- Machine-readable benchmark results and reproducible command
- Independent tester replication or explicit limitation

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


### Comment 7221532807
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/22#issuecomment-7221532807

<!-- deepviz-r04-bounded-sum-20261127 -->
## Value-correctness dependency for fresh scale acceptance: finite SUM transient overflow

Owner: normalizer producer16, integration managerR04. Public repro `normalize([{"g":"a","v":v} for v in [1e308,1e308,-1e308]], {"kind":"bar","x":"g","y":"v","aggregation":"sum"})` previously produced warnednull despite finite expected1e308. Strict18-case permanent controls first failed11/passed7 in each language; final23 controls/language pass. Producer **ec9f669eff28cd5351da142765b7755e3b2f484f** is integrated as **7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6**, published checkpoint6c72cec/draft PR #31. Bounded integer fallback is charged before retention, not an input list.

[Python exact controls](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6/python/deepviz/tests/test_r07_finite_overflow.py) ? [TS exact controls](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6/packages/deepviz/test/test_r07_finite_overflow.test.mjs) ? [integrated results/hashes](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/6c72cec40e3feb8d710ab55167453194f643d650/docs/coordination/evidence/R17-integrated/summary.json).

**Important independent review blocker remains OPEN P2:** [R13-01-F1](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/dd73e9d498295567e5b90c9d396acfa748e02751/docs/coordination/reports/R13-01-sum-review.md) shows residuals lost BEFORE promotion: `[1e308,1e200,1,-1e200,1e308,-1e308,-1e308]` gives0 vs exact1; subnormal twin gives0 vs5e-324. Both languages2 RED/65Python+61Node positives. This is inherited/incomplete accuracy repair, not universal exact summation, and is explicitly assigned to renewed16normalizer followup after owned-input cleanup/mean/scalar fixes.

No fresh10M or final frozen-head scale claim from these controls. Current local integrated full non-scale result is3043pass/36fail/5skip/9scale deselected; npm269pass/0skip. Remeasure10/1K/100K/1M/10M on the final corrected source, with exact input/output/value oracles and declared process-memory methodology; older pinned baselines are not acceptance for this commit. Keep #22 OPEN pending those gates/default merge.


## #23: Inspect real renderer outputs and commit reproducible visual evidence
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/23

<!-- deepviz-key: VISUAL-QA -->
# VISUAL-QA

## Outcome
Chart correctness includes readable labels and actual browser/static renders, not just nonempty files.

## Coordination
- Suggested owner lane: parent coordinator and independent tester agents (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).

## Acceptance criteria
- [ ] Generate committed SVG/PNG/screenshots for representative outputs of all five engines and a dashboard.
- [ ] Inspect clipping, labels, legends, axes/units, accessible contrast and semantic agreement with source fixtures.
- [ ] Browser checks detect runtime/console errors and state whether network access was required.
- [ ] Each PR embeds committed visual evidence and identifies which exact commit/output was inspected.

## Required evidence
- Committed visual files and generation commands
- Two independent tester reports per PR

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #24: Build and clean-install Python wheel/sdist with real entrypoint smoke tests
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/24

<!-- deepviz-key: PY-PACKAGE -->
# PY-PACKAGE

## Outcome
The Python distribution works outside the source checkout with honest optional-extra requirements.

## Coordination
- Suggested owner lane: parent/core and integrations owners (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).

## Acceptance criteria
- [ ] Build wheel and sdist; inspect metadata, included schemas/prompts and declared extras.
- [ ] Install from built artifacts in a clean environment and import the public API.
- [ ] Smoke-test a real render and available CLI/MCP entrypoints from the installed package.
- [ ] Record versions, commands and limitations; do not publish to a public registry without authorization.

## Required evidence
- Build and clean-install logs
- Installed artifact/entrypoint smoke results

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #25: Build and clean-install the npm tarball with usable types and exports
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/25

<!-- deepviz-key: NPM-PACKAGE -->
# NPM-PACKAGE

## Outcome
Consumers install a real tarball whose exports and declarations match documentation.

## Coordination
- Suggested owner lane: TypeScript agent and independent testers (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).
- Depends on: #14 (TS-CONTRACT).
- Depends on: #15 (TS-BROWSER).

## Acceptance criteria
- [ ] Build, typecheck, test and npm pack the package with no credentials or unrelated local files.
- [ ] Inspect exports, declarations, runtime requirements and shared-schema inclusion.
- [ ] Install the tarball in a clean consumer and compile/run a representative chart example.
- [ ] Record commands and package contents; public npm publication is not authorized by this task.

## Required evidence
- Pack file list and tarball checksum
- Clean-consumer compile/run report

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #26: Enforce evidence-bearing PRs with two reviewer and two tester reports
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/26

<!-- deepviz-key: REVIEW-GATE -->
# REVIEW-GATE

## Outcome
Every merge decision has genuine independent analysis and testing attached to the exact proposed commit.

## Coordination
- Suggested owner lane: parent coordinator (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).

## Acceptance criteria
- [ ] Each PR has two distinct reviewer-agent reports and two distinct tester-agent reports, independently produced.
- [ ] Reports record agent/session identity, scope, exact commit, findings/commands/results and limitations.
- [ ] Fixes resolve material findings with retest evidence; changed commits identify stale reports and receive appropriate renewed verification.
- [ ] Commit screenshots/SVG/PNG and embed their repository paths in the PR body before merge.
- [ ] Do not equate reports or comments submitted through one account with two GitHub APPROVED reviews.

## Required evidence
- Per-PR evidence checklist with four report links
- Committed visual embeds and remote PR head/merge state

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #27: Publish a traceable backlog, evidence policy and honest completion tracker
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/27

<!-- deepviz-key: PROCESS -->
# PROCESS

## Outcome
The team can map the design to real issues and distinguish planned, implemented, verified and released work.

## Coordination
- Suggested owner lane: PM/process agent (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.
- Parent epic: #4 (EPIC-DELIVERY).

## Acceptance criteria
- [ ] Create distinct scoped epics/stories/tasks with labels, milestones, dependencies and acceptance criteria.
- [ ] Commit issue mapping and review/test/visual evidence policy under docs/process only.
- [ ] Document GitHub secondary content limits and the single-author approval restriction from primary sources.
- [ ] Leave every issue open until parent-supplied implementation and independent review/test evidence meets acceptance.
- [ ] Record requested 900 created/resolved issues as unmet rather than padding, duplicating or inventing closures.

## Required evidence
- Remote issue/milestone/label snapshot
- Process-doc commit and parent-provided verification before closure

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


### Comment 7221698876
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/27#issuecomment-7221698876

<!-- deepviz-r22-sdlc-triage -->
## Managed incremental delivery — public traceability, not branch-count completion

Agent QA/backlog-manager triage under R22. **Keep #27 open** until its process acceptance is evidenced. This is not a human GitHub approval, final product signoff, a new issue census or a claim that a focused PR/merge already exists.

### Evidence and remaining gap

The [published CI disposition](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/37a27cdfbb0d500cc4e2642bb403d68a145fbb21/docs/coordination/reports/R15-19-ci-failure-disposition.md) audits [run 45928608970](https://github.com/sandeshbagmare/deepviz-agent-toolkit/actions/runs/45928608970), **head `5340bc69b7203ad7a9166543062482d819f9b705` only**: Python **38 / 36 / 240 failures**, all three integration steps **SKIPPED**; **314 instances / 242 distinct nodes / seven disposition groups** mapped to existing #5/#9/#11/#12/#13/#14/#16/#17/#20/#21/#22/#23. Seven analysis groups are not seven new tickets or completed fixes. The **51 + 27 process checks** verify evidence integrity/publication, not product acceptance. This PM did not test later `7bcfb2d` or `6c72cec`.

Branches and genuine saved QA reports are useful progress; they do not supply the missing end-to-end public **issue → fix branch → exact-head independent review/test → PR → tested `main` merge → acceptance closure** chain. The broader [PR31](https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/31) was last observed draft/open/unmerged at head5340 by the manager at **14:18:48 UTC, 2026-11-27**; that is a dated observation, not a fresh PR query in this task.

### First focused delivery path — PLANNED, not an invented PR

- [ ] **R04 manager:** prepare the independently usable **#30 strict ChartSpec JSON numeric-types** slice from current default **`main`**, not a new `master`. Inspect the original `e44f667` fix and its prerequisite tests/schema/config; do not blindly cherry-pick a test hunk onto a foundation lacking its test file, or drag unrelated renderer/dashboard defects into this slice. Publish the actual focused branch/head and real issue acceptance.
- [ ] **Independent gates at that actual head:** planned reviewer lanes **11 + 01** and tester lanes **17 + 09** must supply genuine, source-specific reports after receiving the focused head; preflight `e44` results are not final-PR approval. Resolve material findings; retain original RED and strict positive/negative contract cases. Record actual commands/totals/skips, applicable output/correctness rationale and required remote checks. Agent reports are not human `APPROVED` reviews.
- [ ] **Actual focused PR:** R04 creates the small PR to `main`, links #30 and all four independent reports, and records the returned PR URL/number/head. Until then it is **planned**, not created. Contract-only CI must be honestly named/scoped; it does not turn the failing broader pipeline green.
- [ ] **Actual merge and acceptance:** only after the focused slice's required checks are observed green and its review/test/output gates are met, R04 merges that slice; verify `merged=true`, merge/default SHA ancestry and #30 acceptance before closing **that issue only**. Keep broad parents/PR31/this process issue open for their remaining scope. Do not wait for all branches, the entire toolkit or 900 issues before integrating an independently usable fully gated slice; do not merge RED work.
- [ ] **QA feedback into backlog:** QA12 exclusively files/reuses the demonstrated category-density bug; QA20 exclusively files/reuses the demonstrated Plotly literal-text sink bug, each deduplicated with exact source/repro/real-output evidence. This manager comment creates neither and does not multiply test cases/screenshots into tickets. Source fixes still need manager-owned priority, an eligible exclusive producer and independent retest at the fixed head.
- [ ] **Continue small slices:** after manager review/dependencies, apply the same chain to prompt-copy, numeric-margin and SUM work; keep residual accuracy/policy failures explicit. Record issue dependencies/status and actual bug/PR/merge URLs rather than inferred completion from branches or reviewer assignments.

The concrete CI group/owner/minimum-acceptance checklist is in #20's R22 triage and the [published failure ledger](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/b9534eab21fa13a37cb8f383b6691596355ef2b1/docs/coordination/evidence/R15-19/classified-failures-and-acceptance.json); [verified OWN publication receipt](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/37a27cdfbb0d500cc4e2642bb403d68a145fbb21/docs/coordination/evidence/R15-19/publication-receipt.json) is process evidence, not release evidence.

**900 legitimate issues created AND resolved remains unmet.** No padding, duplicate bugs, artificial approvals or evidence-free closures. R04 retains issue closure, PR creation/shared publication/default merge authority; this role's exception is exactly one idempotent triage comment here and one on #20.


## #28: [Blocker] 900 genuinely resolved issues are not presently evidenced; bulk API limits constrain seeding
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/28

<!-- deepviz-key: BLOCKER-900 -->
# BLOCKER-900

## Outcome
Keep the numerical request visible without treating ticket volume as completed engineering.

## Coordination
- Suggested owner lane: parent coordinator / user acceptance (not a claim of GitHub assignment).
- Initial status: planned; no implementation or independent verification evidence recorded by this seed.

## Acceptance criteria
- [ ] Do not close until at least 900 distinct legitimate issues have verified deliverables, or the user explicitly revises the requirement.
- [ ] Any future decomposition must identify unique scope, acceptance and evidence; no empty/duplicate tickets or automatic closure.
- [ ] Plan API mutations against the account-wide content budget; do not evade limits with alternate accounts/tokens/interfaces.
- [ ] Publish actual remote created/open/closed issue counts excluding pull requests and disclose what remains unmet.

## Required evidence
- Primary GitHub rate-limit documentation accessed 2026-11-26
- Remote issue audit and linked completed deliverables

## Observed constraint
Observed starting state was zero issues. This seed is 29 genuine issues, not 900 completions. At least 900 genuine creates plus 900 closes require at least 1,800 mutations before other process work. GitHub documents general secondary limits of 80 content-generating requests/minute and 500/hour, potentially lower or undisclosed endpoint limits, and no queryable secondary-budget status. 900 creates alone exceed a single documented 500/hour content window; issue updates/closures, labels, milestones, comments and other agents' writes require additional shared budget. This is a feasibility/planning blocker, not a claim that GitHub has actually returned 403/429. Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api .

## Closure and merge gate
Keep this issue open until a verified deliverable satisfies every acceptance criterion and the parent coordinator supplies evidence. Do not close on code existence or a claimed pass. Every merged PR requires two independent reviewer-agent reports, two independent tester-agent reports, and committed screenshots/SVG/PNG embedded in the PR body. Agent reports/comments are not GitHub APPROVED reviews. No empty duplicate tickets or invented completions.

## Source of scope
- docs/superpowers/specs/2026-11-26-deepviz-design.md
- docs/superpowers/plans/2026-11-26-deepviz-plan.md
- docs/process/backlog.json


## #29: [Constraint/workaround] Preserve independent agent-report provenance without GitHub self-approval
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/29

<!-- deepviz-key: REVIEW-PROVENANCE -->
# REVIEW-PROVENANCE

## Outcome
Satisfy the user's independent-agent review criterion through genuine reports while accurately describing GitHub account-level review states.

## Coordination
- Parent epic: #4 (EPIC-DELIVERY).
- Suggested owner lane: parent coordinator (not a claim of GitHub assignment).
- Classification: ordinary process task / documented platform constraint and implemented workaround; not a blocker to the user's independent-agent criterion.
- Status: open until the parent supplies evidence that the report workflow is genuinely implemented.

## Acceptance criteria
- [ ] Document that the user requires two actual independent reviewer-agent reports and two actual independent tester-agent reports per merged PR, not distinct GitHub human approvals.
- [ ] Implement the workaround on the integrated candidate PR: publish or link the four genuine reports as GitHub comments and/or committed source evidence with session identity, exact reviewed/tested SHA, scope and observed findings/results.
- [ ] Embed the committed actual gallery image in the integrated candidate PR and keep report provenance distinct from platform APPROVED review states.
- [ ] Do not attempt self-approval or change repository rules merely to claim completion; this constraint is not a blocker to the user's agent-review criterion.

## Required evidence
- Four genuine independent agent-report links/files on the integrated candidate PR, with exact commit provenance
- Documented workflow and actual committed gallery image embedded in the candidate PR body

## Constraint and workaround
Parent clarification on 2026-11-26: distinct GitHub human approvals are not a user requirement. One coordinator account may post independently produced agent reports as comments or committed source evidence; account identity must not be confused with agent/session independence. GitHub's author self-approval restriction is a platform constraint only, not a new acceptance requirement. The same issue number #29 is retained; its former key BLOCKER-APPROVALS is historical. Close only after the documented workaround is genuinely implemented and parent evidence is supplied. Source: https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews .

## Delivery strategy
The parent is assembling one integrated release/candidate PR while preserving all original feature branches. The user asks for multiple reviewer agents, not distinct GitHub human approvals. Actual independently produced agent reports may be posted through one coordinator account as GitHub comments and/or committed source evidence, with each session and reviewed/tested commit identified. No new agents are launched by this process update.

## Closure and merge gate
The parent may close this issue when the documented workaround is genuinely implemented: two actual independent reviewer-agent reports, two actual independent tester-agent reports, exact commit provenance, and an embedded committed actual gallery image on the integrated candidate PR. Do not close on documentation existence alone. Do not invent a self-approval or human-approver requirement. Agent reports/comments are not GitHub APPROVED review states.

## Source of scope
- Parent clarification on 2026-11-26
- docs/process/review-and-evidence.md
- docs/process/github-constraints.md
- docs/process/backlog.json


## #30: Bug: Python chart schema coerces strings and booleans unlike JSON Schema
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/30

## Reproduction

The generated JSON Schema declares numeric fields, but the Python runtime accepted numeric strings and JSON booleans through Pydantic coercion:

```python
ChartSpec.model_validate({"width": "900"})
ChartSpec.model_validate({"version": True})
ChartSpec.model_validate({"columns": True})
```

This diverges from JSON Schema and a schema-validating TypeScript consumer.

## Acceptance criteria

- Reject string values for numeric schema fields and booleans for version/columns.
- Continue to accept mathematically integral JSON numeric values, such as `900.0`, consistent with JSON Schema integer semantics.
- Preserve valid defaults and all existing bounds.
- Add regression tests and run lint/type checks.

## Observed test evidence

Before fix: `python -m pytest tests/test_models.py -q`: **6 failed, 24 passed** (all six failures were unexpected acceptance).

After adding a before-validator: full current checkout suite `python -m pytest -q`: **30 passed**; Ruff and mypy passed for the changed implementation/tests. This evidence concerns the schema-only branch, not the unfinished integrated product.

Leave open until the reviewed release PR merges the fix.


## #32: Bug: native SVG category labels overlap at valid 240px width
https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/32

<!-- deepviz-qa-key: R17-12-D1-category-density -->
## Reproduced defect (one layout cause)

The TypeScript native SVG renderer successfully returns a chart at the schema-valid
minimum240x200dimensions, but its category labels overlap. Both standalone SVG and
generated HTML retain all eight correct values/marks while the visible labels are unreadable.
This is not the separate numeric-tick clipping fix and is not a request for a ticket per case.

Related parent scopes:#15,#23. Fresh complete open-issue review found no specific duplicate;
those are broad browser/visual stories, not this bounded defect report.

## Exact source and already-executed QA evidence

- Renderer source:[5e595a8f893955ce34a0e26553bb7bf257ea93ae](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/5e595a8f893955ce34a0e26553bb7bf257ea93ae/packages/deepviz/src/renderers.ts).
- Probe/evidence:[4867f144507436ba5d81cec515a4976723c4a698](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/tests/r17_probes/role12/category-density.test.mjs).
- Actual imported compiled`renderers.js`SHA256:`7640f5147a11e795f3f78564409adae0fb21421bf59f2b95c2d4a9b83c28c4b1`; source SHA256:`be34bcb2be9e44459cb30d145386c3606933bcbdea389ba2fd3fca8d738fac80`.
- Node26.13.1/Chromium159.0.8154.6/Windows. Single strict NEW test command: **exit1,5pass/4fail/0skip**,4141.2145ms. Four failures are genuine final pairwise text-box overlap assertions; four full-size browser controls plus one overlap-oracle self-control pass.
- All eight cases preserve literal category text/order, eight nonempty marks, original1..8values, height ratios/common zero and dimensions. All eight have **0console/page/runtime errors,0external/failed requests and0clipped text boxes**. Containment and correct values do not imply readable category labels.
- Actual PNGs were opened and inspected. Exact[DOM boxes/gaps/mark values](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/browser-cases.jsonl),[summary](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/summary.json),[actual TAP](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/density.tap.log).

## Bounded reproduction

Eight finite records:`{group: 'g0', value:1}`…`{group:'g7', value:8}`.
One additional finite Unicode fixture uses`東京都東部支店1`…`東京都東部支店8` with the
same1..8values, below the existing18-character abbreviation threshold.
Spec:`{kind:'bar',x:'group',y:'value',aggregation:'none',max_points:10,width:240,height:200}`;
engine`svg`. Repeat at`width:960,height:540` as positive control; inspect rawSVGandHTML.

From the immutable probe commit with matching built`dist/`and an already available
Playwright/Chromium (see[probe README](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/tests/r17_probes/role12/README.md)):

```powershell
$env:DEEPVIZ_PLAYWRIGHT_ENTRY = 'C:/path/to/existing/node_modules/playwright/index.mjs'
$env:DEEPVIZ_R17_OUTPUT = 'C:/path/to/NEW/unique/output'
node --test --test-reporter=tap tests/r17_probes/role12/category-density.test.mjs
```

No tests/build/browser/10Mwere replayed to file this issue; these are the recorded R17 results.

| Fixture/dimensions | Plot/slot(px) | Label bbox width(px) | Minimum adjacent gap(px) | Overlapping pairs | Actual SVG screenshot | Actual HTML screenshot |
|---|---:|---:|---:|---:|---|---|
| Ordinary8,240x200 |103/12.875|13.598|-0.723|7|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-240-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-240-html.png)|
| Ordinary8,960x540 |823/102.875|13.598|89.277|0|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-960-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-960-html.png)|
| Unicode8,240x200 |103/12.875|92|-79.125|28|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-240-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-240-html.png)|
| Unicode8,960x540 |823/102.875|92|10.875|0|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-960-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-960-html.png)|

## Cause, expected outcome and open decision

Current tick selection uses category count(`ceil(n/12)`) without the remaining plot width
or actual category glyph boxes. All eight labels are selected even when each slot is narrower
than its label. This is ONE layout cause across both carriers/fixtures. The existing HTML
accessible-data disclosure does not make the visible chart labels nonoverlapping.

- [ ] For supported finite fixtures, provide readable complete labels without positive-area overlap or clipping in actual SVG+HTML, keeping values/order/mark meaning/usable plot and readable text size.
- [ ] If the requested dimensions truly cannot fit the complete finite labels, follow an **explicitly approved** descriptive density-infeasibility policy rather than successful unreadable output. No silent hiding/truncation/category or value change, arbitrary global schema-minimum expansion or unlimited-Unicode-text promise.
- [ ] Preserve the960positive controls and numeric-axis containment; add strict future fixed-head controls for any approved rejection/no-output path rather than calling the current RED a pass.
- [ ] Obtain genuine non-author fixed-head review/retest before closure. This QA author also authored the separate numeric-margin change; this report is not self-signoff on it.

**Policy/implementation owner:R04; layout-policy and eligible-producer release decision remain OPEN.**
The[bounded stagger/infeasibility proposal](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/reports/R17-12-category-density.md)
is not an approved or implemented fix. Font fallback metrics above are actual Chromium/Windows
measurements, not a universal font guarantee. Leave this genuine bug open until the manager's
evidence-based acceptance/merge/closure process is satisfied. No900-count padding or final
visual/scale/release approval is claimed.

