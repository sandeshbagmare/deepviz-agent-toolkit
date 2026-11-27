# R22-03 duplicate review — before any POST

At2026-11-27T15:19:23.862089UTC, authenticated readonly GET/user200 verified
`sandeshbagmare`; intended public repo GET200/defaultmain. Complete open issues
endpoint pagination exhausted at first short page32items: **31issues +1PR**.
All31issue comments were separately paginated to a short page; marker
`deepviz-r22-graphql-error-carrier` matched **0bodies/0comments**. No mutations.

Full open issue titles/bodies were saved locally and read. Relevant GraphQL/input
and TypeScript bodies include:

- **#7 INPUT-GRAPHQL**: broad nested/page/path story, all-pages/counts/no remote
  URL acceptance. No specific failed error-only page accepted as an ordinary row,
  carrier differential, minimal repro or regression ID; **0comments**.
- **#14 TS-CONTRACT**: shared fixtures/bounded normalization/truthful metadata/
  parity story. Not a specific error-only page-array bug; **0comments**.
- **#6 INPUT-FORMATS**: ordinary tabular malformed/empty/optional-format story.
  No specific GraphQL array/JSON failed-page bypass; **0comments**.
- **#1 EPIC-FOUNDATION/#5 CONTRACT/#8 STREAMING**: broad parents/prerequisites,
  not duplicate defect reports; **0comments** each.
- Other keyword candidates#9/#16/#17/#23/#32 refer to renderer/tool/runtime
  errors or category density, not this cause. #32is the already-filed separate
  density issue, not GraphQL. OpenPR31is broad candidate work, not an issue.
- Remaining open titles/bodies and all comment pages contain no matching
  specific carrier bug or idempotency marker. Known local R10-01F1 unexpected
  connection-sibling loss is explicitly outside this ticket, even though four
  permanent tests remain RED in the same suite.

**Decision:** prepare ONE specific bug linked to existing parent#7 and related#14,
not comment on a broad feature story as if it were the same specific bug. Recheck
fresh open enumeration/comments/marker immediately before one bounded POST;
idempotent marker/specific match means GET/reuse or stop for decision, not another
POST. 403/429or ambiguous POST failure STOP/handoff, no retry/account bypass.
Exactly one cause covers three failed-data forms times two carriers; no6tickets,
closure/fix/CI/final-signoff or900completion claim.
