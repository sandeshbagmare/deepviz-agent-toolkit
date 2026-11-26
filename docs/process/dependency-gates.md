# DeepViz dependency gates and integration risk register

Date: 2026-11-26. Owner: engineering-management agent. This document defines verification gates and records a point-in-time architectural audit; it does **not** declare the release passed.

Authority: parent-held `python/deepviz/src/deepviz/models.py`, [implementation plan](../superpowers/plans/2026-11-26-deepviz-plan.md), [design](../superpowers/specs/2026-11-26-deepviz-design.md), and `AGENTS.md`. Ownership and concurrency rules are in [engineering-org.md](engineering-org.md). PM owns the remaining process/status/evidence documents; this is not a duplicate live issue tracker.

## Dependency graph and integration order

```text
parent contract + generated schema + shared behavior fixtures
    |-- Python ingestion/reduction ---> Python renderer adapters ----+
    |-- TS validation/normalization --> TS browser/package ----------+-- candidate
    |                                  Python tools/CLI/MCP <-------+   |
    +-- research/architecture + CI authoring + independent test design --+
                                                                      |
                     installed-package + real output + scale + review gates
                                                                      |
                                            parent integration/release decision
```

These are dependency gates, not a demand for serial development. Features can be developed in parallel, but an isolated producer's pass cannot certify its consumer. Parent first resolves shared semantics and selects actual prerequisite SHAs; ingestion/rendering/integration consumers then run together on a complete candidate. TS proceeds against the same contract fixtures and joins parity/browser/package checks. CI, research and specialist QA prepare in parallel. No EM merges or branch rewrites are authorized by this document.

The branches observed at initial inspection were `feat/ingestion`, `feat/renderers`, `feat/typescript`, `feat/integrations`, `docs/research`, `ci/verification`, `test/acceptance`, `test/browser`, `docs/process`, and `feat/hardening`. This EM branch is separate. Several producer implementations were uncommitted at inspection; reading a sibling worktree is advisory evidence, not a reproducible integrated candidate or permission to copy it.

## Gate vocabulary and evidence identity

Use `NOT RUN`, `BLOCKED`, `FAIL`, or `PASS on <full SHA>` with a report/run link. A skip, missing optional extra, unavailable browser, CDN outage or mocked integration is not a pass. `PASS` requires the command result plus its semantic/visual acceptance evidence, not an artifact filename alone.

Every gate packet identifies source SHA, dirty diff/hash if applicable, schema fingerprint, environment, command and working directory, exit code, test/skip counts, output hashes, observations and limitations. Dirty snapshots are suitable for early feedback, not final candidate acceptance. After a relevant code/dependency/schema change, invalidate affected reports and rerun them. A docs-only change may reuse product evidence only with an explicit unchanged-code comparison, not by assumption.

## Ready-to-integrate gates

| Gate | Producer -> independent verifier | Required evidence | Stop condition |
| --- | --- | --- | --- |
| G0: bounded work and launch admission | PM/EM -> parent | Named outcome, paths, owner, prerequisite SHAs, acceptance mapping; actual active-session count | Missing owner/contract, overlapping edits, or a new launch while the parent gate is closed; existing work may finish |
| G1: model/schema/TS agreement | Parent contract owner + TS -> parity QA + architecture | Regenerated schema; Python/JSON Schema/TS shared valid/invalid/default fixtures; explicit coercion/dashboard rules | Different accept/reject/default behavior without a deliberate, documented boundary |
| G2: ingestion and reduction | Ingestion -> remaining format/statistics QA + QA A + architecture reviewer | Row-preserving records/columns/nested/GraphQL/text/optional-columnar tests; missing/mixed/nonfinite behavior; aggregate/sample/count oracle | Silent row loss, incorrect mean/count, inconsistent policy or unbounded retained state |
| G3: five real renderers | Renderer + TS -> backend QA + browser QA B | Native specs and actual SVG/PNG/browser output, mapped marks/series, requested/rendered kinds, warnings, theme/labels/size/color checks | Wrong engine identity, silent fallback, incorrect marks/axes, console errors or nonrendering output |
| G4: dashboard and metadata | Renderer + integration + TS -> statistics/architecture reviewers + performance QA | One-shot source consumed once; independent child mapping/reduction; input/output count definition; child and total budgets | Reusing a consumed iterator, hidden data mutation, misleading counts or multiplying resources without bounds |
| G5: tools, MCP and trust boundary | Integration -> MCP transport QA + security reviewer | Real Deep Agent attachment, real stdio initialize/list/call/cleanup, handle lifecycle and safe artifact retrieval | Mock-only evidence, arbitrary reads/URLs/execution, escaped paths, reused/overwritten artifacts or unbounded payloads |
| G6: scale/resource envelope | Ingestion/renderer -> performance specialist + acceptance QA A | 10, 1K, 100K, 1M, 10M streaming rows; input/output counts, strategy/loss, elapsed time and memory method; cardinality/width/byte/disk adversaries | Materializing full streams, misleading memory claim, count mismatch, nonfinite results or missing tier |
| G7: quality/build/distribution | CI/release + TS -> portability QA + independent tester | Exact Python/npm commands below; wheel/sdist and npm tarball installed in clean consumers; entry points, schema/prompts/assets present | Wrong source imported, tests outside discovery, missing package files or a failing advertised runtime |
| G8: evidence and claim audit | Authors -> security + independent architecture/research reviewer; QA A + B; accessibility/docs auditors | Two distinct non-author reviewer reports and two distinct tester reports on the candidate, rendered-output rationale, specialist finding dispositions and honest capability docs | Self-review double counted, canceled/unfinished reports promoted to passes, stale reports, fake human approvals or unchecked blocking findings |

G0 applies to every work item; G1-G8 apply according to impact, with the full applicable set required on the release candidate. A specialist backend/format report is additional coverage, not automatically a replacement for one of the four independent reports.

### Exact command obligations

From the complete candidate root, in its project virtual environment, CI/release must record the actual commands and outcomes for `python -m pytest`, `ruff check .`, `mypy`, Python distribution builds, and distribution validation/clean installs. `python -m build` and `python -m twine check dist/*` are the conventional distribution checks; use the repository's actual supported invocation and record it. Do not run product verification in this docs-only worktree and mistake missing sibling modules for a release defect.

For npm changes record `npm ci`, `npm run build`, `npm run typecheck`, `npm test`, and `npm pack --dry-run --workspace @deepviz/agent-toolkit`. A dry run alone does not prove a tarball works: also install the actual packed tarball in a clean consumer and exercise exports/types/browser output. Package tests must consume the distributed artifact, not rely solely on monorepo source or undeclared workspace dependencies.

Prove `deepviz` imports from the intended candidate or its installed wheel, not a parent's editable install. Record Python and Node versions and all advertised combinations; the observed project requires Python >=3.11. Multiple local Python versions were visible in worker-generated caches, which is a portability test prompt, not evidence of a regression. Inspect pytest's discovered test locations and npm's actual test script so new independent tests cannot silently fall outside CI.

For scale, state whether memory is process peak RSS, sampled RSS, Python allocations, or another method; include subprocess/native allocations limitations. Record baseline, peak/delta convention and repeatability. Streaming 10M inputs into <=`max_points` rows is not equivalent to rendering 10M marks. For dashboards record child row totals separately from source counts. Exercise high-cardinality grouping, wide rows, long strings and dashboard fanout as well as scalar row count.

## Independent dependency audit: observed snapshot

The following results were obtained by the EM on 2026-11-26 through **read-only source inspection and small, inline Python/Node probes**, not through a complete test suite. Source branches were still being edited. Recheck on committed producer SHAs before accepting or closing any finding.

| Snapshot | Git identity / qualification |
| --- | --- |
| Parent and EM base | `2b2709ec6846ad8e136641257e04b4ae48eded08`; parent design file was dirty; EM began clean |
| Ingestion, renderer, TypeScript, integration bases | `0ae2cf26426822135fc10d337fcacf580b7ed833`; implementations under inspection were uncommitted |
| Parent `models.py` SHA-256 | `9705c4e7809ea03405ef2180f976869fc5f13e0fc63a45190929bd0c4241b461` |
| Ingestion `normalize.py` SHA-256 at probe setup | `c513ca21b7409214c7260afafee67226e4d0924172543df04ff0598b32433943` |
| TS `src/normalize.ts` SHA-256 at probe setup | `ba3d107ebbafa7d9b3fce7e53359c49df7449543d54e91e395ebb2a3d6ac1a40` |
| Executed TS `dist/normalize.js` SHA-256 at probe setup | `0cbd4e275f2e9e34f1ba3b2710804c9bc8f6d4c67970d1fbdb382ceb9124c603` |

Python probes used the parent's project virtual-environment interpreter with the ingestion worktree's `python/deepviz/src` explicitly first on `sys.path` and bytecode writing disabled. Node used `--input-type=module` and imported the TypeScript worker's **existing built JS** by absolute file URL. EM did not rebuild or modify that worker. These hashes identify early feedback; they do not establish a clean source-to-dist build or a product-level pass.

### R1 — P0, observed: normalization semantics differ across languages

| Minimal input/spec | Python observed | TypeScript built JS observed |
| --- | --- | --- |
| `[{"g":"a","v":1},{"g":"a","v":2}]`, `{"x":"g","y":"v"}` | One row `{"g":"a","v":3}`, strategy `sum`, input count 2 | Two original rows, strategy `none`, input count 2 |
| Eleven `{"g":str(i),"v":i}` rows, `x=g,y=v,aggregation=none,max_points=10` | Ten-row reservoir sample plus explicit warning | `ValidationError`: input exceeds `max_points` |
| Same eleven unique groups, `aggregation=sum,max_points=10` | Nine exact groups plus other bucket with value 19 and warning | `ValidationError`: group cardinality exceeds `max_points` |
| `[{"id":1,"tags":["a","b"]}]`, `kind=table` | `id`, `tags.0`, `tags.1` flattened record | `ValidationError`: nested array at `tags` |

**Source evidence:** ingestion `normalize.py:316-338,369-387,390-449,452-515`; TS `normalize.ts:119-149,151-200` in the inspected snapshots. The TS engine may consequently render separate/first categorical values where Python renders a sum; identical `ChartSpec` is not enough to guarantee equal meaning.

**Smallest handoff:** parent/architecture choose the intended public behavior; ingestion and TS implement the same golden cases without parallel schema expansion. Add null/non-numeric measures, weighted overflow means, `data_path` missing branches/numeric indices, scalar indexing, auto JSONL and sample determinism to the parity matrix. Different deterministic sampling algorithms need an explicit equality policy: exact sampled rows or documented distribution/count invariants. **Gate:** G1/G2 remain blocked for parity until committed implementations run these fixtures together. This is an EM finding, not an issue closure or an instruction to change the parent model.

### R2 — P0, observed: schema acceptance has multiple authorities

The parent Pydantic model accepted `{"max_points":"10"}` and `{"version":true}` and produced normalized numeric values; TS rejected both. The probes also confirmed that numeric `width=900.0` is accepted by both languages, so that is **not** a reported mismatch. Parent `models.py:16-36` uses Pydantic defaults; TS `models.ts:63-95` implements separate strict validation. TS `schema.ts:5-25` separately authors a structural schema, while its comments leave dashboard semantic checks to `validateSpec`.

**Smallest handoff:** the parent decides coercion policy explicitly. Generate `schemas/chart-spec.schema.json` from the parent model, compare the shipped TS schema to that artifact, and run the same accept/reject/default cases through Python, JSON Schema and TS, including dashboard constraints that a structural schema alone may omit. TS security-specific restrictions must be documented/tested rather than silently claimed as universal parity. Do not independently add execution/expression fields. **Gate:** G1 requires a committed schema/fingerprint and demonstrated agreement, not two manually similar field lists.

### R3 — P1, source-observed/inferred impact: normalized count fields may not drive renderer inference

Python's reducer can infer its measure and emits `count` for count aggregation without an explicit `y` (`normalize.py:369-387,438-449`). The `NormalizedData` contract contains records/count/warnings/strategy, but no resolved x/y mapping (`models.py:49-54`). Consumer renderer inference is therefore a separate decision. Dashboard children can apply different mappings/reducers to the same source. This is a coupling risk, not a demonstrated wrong chart in the unfinished renderer.

**Smallest handoff:** renderer QA plus the remaining architecture/statistics reviewers add direct mark-height/series-value checks for inferred y, `aggregation=count` with/without explicit y, missing measures, mixed fields and reordered object keys. Include input rows where the first numeric field is not the intended measure. Confirm that all five Python engines and the TS engine consumers choose the same reduced fields. Prefer a small shared resolution rule/fixture over widening `models.py` without parent agreement. **Gate:** G3/G4 require semantic oracles, not only manifest presence.

### R4 — P1, source-observed/inferred impact: dashboard replay and count semantics need a common definition

The renderer snapshot `render.py:31-41` spools one-shot dashboard iterators into temporary JSONL and re-normalizes each child; serialization uses `default=str`. Its return path `render.py:95-104` uses the maximum child `input_count` and sum of child row counts. The model allows 24 children and up to 100,000 retained points each. Child `data_path` selections can have different logical row counts; typed Python inputs can change interpretation during JSON replay. The source shows the mechanism, not a completed failure reproduction.

**Smallest handoff:** renderer + ingestion owners define whether dashboard `input_count` means original logical source records or maximum selected child records, and retain child counts. Test one generator, different child `data_path`/reducers, non-JSON-but-supported scalar types, failure cleanup, and 24-child resource use. Require byte/disk budgets for replay; RAM boundedness does not imply bounded temporary disk. **Gate:** G4/G6 need honest metadata and no silent semantic conversion, without asserting that disk-backed replay itself is defective.

### R5 — P1, source-observed/inferred impact: point caps do not bound serialized bytes

Python `NormalizedData.records` has arbitrary values at the type boundary and the ingestion snapshot bounds fields/depth/rows but not string byte size. TS truncates strings at 10,000 characters and uses different field/depth limits (`normalize.ts:4-6,133-143`), introducing another lossy-policy difference. The integration snapshot checks inline size after JSON decoding (`tools.py:73-89`) and rejects artifacts larger than 16 MiB only after rendering (`tools.py:130-149`). Its 32-handle cache retains original small sources (`tools.py:107-114`). These are resource-envelope questions; no memory/latency benchmark or exploitable denial of service was claimed by EM.

**Smallest handoff:** security/performance reviewers specify and test input bytes, per-cell bytes, total normalized bytes, dashboard total bytes, handle cache budget, output bytes and temporary disk policy. Enforce rejection early enough to protect parsing/serialization, or explicitly bound the supported host envelope. Test a few huge strings and many wide rows, not just many tiny rows. Decide truncation versus rejection and disclose every loss. Source owners implement their own boundary; do not move arbitrary filesystem access into a chart spec. **Gate:** G5/G6 cannot infer byte safety from `max_points` alone.

### R6 — P1, observed source: capability lists can overstate semantic support

TS `renderers.ts:7-13` declares engine/kind support, but ECharts size encoding uses a constant marker size (`renderers.ts:110`), with an explicit source-only shortcut comment. A spec's `size` can therefore validate without affecting visible marker size. Other chart-specific semantics (heatmap axes/value role, hierarchy and geographic mapping) need runtime verification rather than a generic bar-like success criterion. Browser dependencies and optional engines also require their actual runtime versions.

**Smallest handoff:** TS and reassigned backend/browser QA verify bubble size with unequal values and inspect the real rendered marks; either implement size encoding or surface a user-visible limitation/rejection rather than relying on a code comment. Maintain an engine/kind/encoding capability matrix with requested/rendered kind and warnings. QA A and browser QA B must fail on console errors and distinguish offline-capable artifacts from network-dependent output. **Gate:** G3/G8 block unsupported capability claims; a warning is not permission to label a different engine as native.

### R7 — P1, observed coordination risk: root files and installed environments are shared dependencies

The integration worktree already had a modified `README.md`, while the plan also assigns release documentation to research/CI. The ingestion worktree has `scripts/benchmark_scale.py`; a blanket CI ownership claim to `scripts/**` would collide. The base `pyproject.toml` exposes CLI/MCP entry points before all producer modules are integrated. Separate tests may also import the parent's editable install instead of their own branch.

**Smallest handoff:** parent selects one root-file editor, retains feature ownership of the benchmark, receives scoped documentation/dependency requests, and produces a full candidate before entry-point smoke tests. Have CI print import location and run wheel/sdist/npm clean-consumer checks. **Gate:** G0/G7 enforce source ownership and actual installed-artifact provenance. Missing sibling work in an intentionally isolated branch is a dependency, not an artificial defect ticket.

## Risk disposition and immediate parent actions

All R1-R7 above were **open at EM inspection**. They are local risk labels, not GitHub issues, human approvals, or artificial work-completion counts. PM may map a confirmed finding to an existing real acceptance item; create additional work only if it is genuinely distinct and authorized. A fix report needs its producer SHA, independently rerun reproducer and affected regression results.

1. **Resolve R1/R2 first:** parent + architecture + schema-parity/statistics QA publish one behavior-fixture decision; ingestion/TS respond with exact commits. This prevents independently green implementations from diverging in meaning.
2. **Pin a complete candidate:** ingestion -> renderer -> integration prerequisites plus TS/CI, without copying uncommitted sibling files. Parent chooses the integration mechanism; this EM does not merge.
3. **Use the remaining specialist bench:** schema/statistics/GraphQL QA plus QA A absorb canceled text/columnar/geography checks; browser QA B and remaining backend QA absorb Matplotlib/ECharts checks. MCP transport QA uses real stdio; performance/security check byte/disk limits; portability QA checks built consumers. Correctness reviewer B's unfinished scope transfers to architecture/research plus statistics QA; security remains an independent second review. The parent reports active <=22 after six explicit user cancellations and three completions. Do not restart canceled sessions, launch replacements, cancel additional sessions or delete partial work; parent controls the paused launch gate and full QA.
4. **Run G1-G8 on that candidate and disposition findings:** do not count the completed QA-A seed or public research report as final-candidate signoff. Keep agent reviews distinct from any required human/account approvals.
5. **Keep product claims honest:** no claimed release success, 900 legitimate resolved issues, human approvals, full scale, optional engine, or browser pass without direct evidence. Documentation delivery itself closes none of those acceptance criteria.

## EM verification boundary

EM performed Git/worktree and ownership inspection, source/dependency reading, SHA-256 snapshot identification, the four Python/TS normalization probes and three schema-input probes described above. Python and Node probe commands exited successfully; their stdout intentionally contains differing outputs/errors under comparison, so successful probe execution is **not** a product test pass. Full Python/npm suites, scale tiers, real MCP/Deep Agent sessions, rendered artifacts, remote product CI and independent four-report review were not run by this docs-only lane.

The documentation delivery must separately verify only the two allowed files changed, Markdown/local references are coherent, patch whitespace checks pass, a real Git commit is created and the requested branch push is read back. That publication evidence belongs in the handoff, not an invented product acceptance verdict.
