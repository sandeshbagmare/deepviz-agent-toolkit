# R24-01 independent helper-null SOURCE review

**No concrete must-fix finding in this one-line repair. Source review only:**
I ran no package build, helper tests, imports or browsers. Tester05 separately
owns the unchanged36+40 matrix; none of its results are borrowed here.

Exact source:**7d8ccdce22430a9ddf3a14a9e64bf15b2373ae57**.
Parent:**5340bc69b7203ad7a9166543062482d819f9b705**.
Reviewer:`ses_de5678335ffeI7xJrod5l25Q0Q`, non-author.
Own branch:`agents/r10-01-correctness-regressions`, starting clean d9e4dcc.

## Diff and connected correctness

The complete package diff is `render.ts:140` plus the NEW97-line original-author
`test_r07_tool_spec_null.test.mjs`. Seven other committed paths are producer
notes/evidence, not additional product changes. I read the FULL minimal diff,
original tests, public input/exports/schema and connected normalization/rendering.

- **Default versus null:** `packages/deepviz/src/render.ts:133-142` creates all
  five helpers through one closure. Previously `input.spec??{}` converted explicit
  null into a valid default. The new undefined-only default passes null unchanged
  through `render:113-114`→`buildRendererSpec:49-55`→`models.ts:64-68`; object
  validation now rejects it BEFORE normalization/output construction. This fixes
  the demonstrated mismatch with `inputSchema:137`, whose ChartSpec reference
  is an object (`src/chart-spec.schema.json:233`), not null.
- **Preserved accepted inputs:** omission and explicit JavaScript undefined still
  select `{}`; the latter is a callable-JS convention, not a JSON value. For every
  other ordinary JSON spec value, the argument is identical to before. In
  particular false/0/empty string/arrays are NOT replaced by defaults; all reach
  unchanged `models.ts:49-50,68` rejection. There is no newly accepted malformed
  JSON shape or string/number coercion in this repair.
- **Extras and dashboards:** wrapper own-data/key checks at `render.ts:139` remain
  unchanged. Spec extras including code/url/engine/data/options remain unknown
  at `models.ts:70-71`. Field mappings/defaults/bounds and valid nonempty bounded
  dashboards still use the same parser at73-96. The only top-level value whose
  behavior changes is null. No rejection policy for ordinary label strings is
  invented; null optional mapping FIELDS remain allowed at84-85.
- **Data/engine authority:** the first render argument is still `input.data`, not
  something merged from spec. The closure still selects vega/echarts/antv/plotly/
  svg from `renderers.ts:6`; host options stay in the factory closure. Supported
  mappings at27-61 and dashboard child/data-path preparation at `render.ts:57-71`
  are untouched. The wrapper cannot select an alternate engine via a JSON extra.
- **Errors and safety:** `invoke` stays async without catch/wrapping, preserving
  `ValidationError` rejection semantics. Null now produces the existing
  `ChartSpec must be an object` error instead of silently making a chart. No new
  filesystem, URL ingestion, arbitrary execution, raw HTML sink, reduction or
  unbounded collection is introduced; this is not a whole-renderer security audit.
  Exotic getters/proxies/custom JS objects are outside this ordinary JSON
  argument-equivalence analysis; no new sandbox guarantee is claimed.

## Evidence and execution limits

Actual read-only Git commands: `git show`, `git diff parent source --
packages/deepviz`, `git grep` for helper/public callers, and binary Git-blob/hash
comparisons. All completed exit0. Eleven exact source/context files were captured
and reverified. Nine connected files are byte-identical to parent; only render
and the new author test differ. The two shipped schema copies are byte-identical.
Exact byte proof also verifies that replacing the ONE `input.spec??{}` occurrence
with the new expression reproduces the complete changed render.ts, no hidden edits.

`evidence/R24-01/reviewed.diff`, `source-identity.json` and
`static-connected-review.json` contain the actual diff/source hashes/results.
No helper runtime tests were run and **zero runtime passes** are asserted.
The original tests were read, not executed; no new controls were added because
no concrete uncovered JSON boundary emerged that justified duplicating05's lane.
No core689/fullnpm/browser/scale/SUM/prompt replay, install, source/oracle/workflow
edit, API/issue/PR/shared Git write or worker spawning occurred.

**Disposition:** this one-line source repair completely addresses the demonstrated
explicit-null helper/schema mismatch for ordinary JSON inputs without broadening
accepted malformed specs. Integration head, packaging/build execution, tester05
results, renderer/browser correctness and remote CI remain unverified here.

**Next:** R04 can consider this source report with05's genuine execution evidence
for a later helper slice. I remain the actual focused#30 reviewer: upon receiving
its immutable head/PR/workflow, checkpoint this review then verify ALL focused
paths/context and rerun affected strict controls on THAT head. R22/e44 readiness
is NOT final approval. No idle head polling or invented PR/merge/signoff.
