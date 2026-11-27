# Completion-wave agent roster and ownership

Updated: 2026-11-27. C00 edits this historical roster; C17 owns its separate live product slot register. Session runtime, not this table alone, determines whether a worker is active. All role briefs include `BRIEF.md`; each worker persists its exact assignment in its report before acting.

## Launch budget

Hard ceiling: **22 running agents total**, including coordinator and nested children. C18's completion notification has been received, releasing its earlier separate1 reservation: **C17 owns the full22-slot inclusive budget**, counting C00, itself and every other active/historical/product worker. This means at most20 other workers while C00 and C17 are active, not22 additional children. Use substantial assignments/productive waves; the suggested440 cumulative agents is not a completion metric or permission for filler work. C17's authoritative live launch register is `docs/coordination/C17-live-slots.md`; reconcile it with `/api/session/active` and every returned worker ID before dispatch. C18's audit F1 requires repairing stale/missing mappings before further launches. C17 replaces unstarted C16's write/dispatch authority. C15/C18/C00 have no further launch authority.

| Task | Existing actual session | Role / assigned scope | Report | Dispatch state |
| --- | --- | --- | --- | --- |
| C00 | `ses_de6e9da62ffe4nQ5DMuAaht0xL` | Recovery documentation only; no product/Git/GitHub writes while C17 owns integration | `reports/C00-recovery.md` | active |
| C01 | `ses_de7083225ffe9hX1vqJ6JD7SC3` | Five Python renderers, own renderer worktree | `reports/C01-renderers.md` | already running; file protocol pending |
| C02 | `ses_de708059dffe0sI5fOTQt2bCRI` | TypeScript SDK, own TS worktree | `reports/C02-typescript.md` | already running; file protocol pending |
| C03 | `ses_de7085536ffeyecPC6bloK2HO4` | Ingestion/reduction producer, own core worktree | `reports/C03-ingestion.md` | resume queued |
| C04 | `ses_de707bd4cffeBCZ3CfQPzW3fWV` | Tools/CLI/MCP producer, own integrations worktree | `reports/C04-integrations.md` | resume queued |
| C05 | `ses_de7063f89ffeXXYK9ECOj2fwmy` | CI/build/package producer, own CI worktree | `reports/C05-ci.md` | resume queued |
| C06 | `ses_de7066935ffeqnltHoY5WyyUOH` | PM: issue mapping, exact remote audit, own process worktree | `reports/C06-delivery.md` | resume queued |
| C07 | `ses_de703c6a3ffeYjHKGtgOBaYHKz` | Independent browser QA, own browser tests | `reports/C07-browser.md` | candidate trigger pending |
| C08 | `ses_de705c840ffeBguNbPBWNLuA63` | Independent acceptance QA, own acceptance tests | `reports/C08-acceptance.md` | candidate trigger pending |
| C09 | `ses_de7015c41ffeQD4ru9MCBw5KV9` | Independent security review, no source edits | `reports/C09-security.md` | candidate trigger pending |
| C10 | `ses_de707df1affeBlK7XUxdANukpl` | Research/architecture and independent correctness review | `reports/C10-research-review.md` | resume queued |
| C11 | `ses_de7011d26ffeHo2Qy4UIfAtnTj` | Streaming scale/performance evidence | `reports/C11-performance.md` | candidate trigger pending |
| C12 | `ses_de6fc269cffeCP5vGJQg98QT2z` | Schema/Python/TS parity QA | `reports/C12-parity.md` | candidate trigger pending |
| C13 | `ses_de700a831ffeWWIa0iZacXW1YP` | README/examples/prompts documentation audit | `reports/C13-docs.md` | candidate trigger pending |
| C14 | `ses_de6fb759bffeWvSMTgOTP6fhEj` | Independent real MCP transport + tools verification | `reports/C14-mcp.md` | candidate trigger pending |
| C15 | `ses_de7017cf3ffeufzsaUkPJhnDFW` | Engineering coordination: acceptance audit, no spawning | `reports/C15-management.md` | resume queued |
| C16 | `ses_de70bd471ffem0HgkC2LmWx5Dt` | Historical original coordinator; context source only; write/dispatch assignment superseded by C17 | `reports/C16-integration-lead.md` | API delivered, execution not observed |
| C17 | `ses_de6ddc25affeMo5NjdAuqfub72` | Fresh integration/QA lead: exclusive product/Git/GitHub writer; owns nested dispatch within global cap | `reports/C17-integration.md` | launched through child tool |
| C18 | `ses_de6dc95eeffej0nH3Io6H3qwqU` | Independent recovery-doc/ownership/cap audit only; no source edits or spawning | `reports/C18-recovery-audit.md` | completed; evidence received; slot released to C17 |
| N01 | dispatch pending returned ID | Nested independent statistics/format/security review, read-only source; saved `tasks/N01-data-review.md` | `reports/N01-data-review.md` | reserved by C17; active endpoint showed 2 before launches |
| N02 | dispatch pending returned ID | Nested independent package/claim review, read-only source; saved `tasks/N02-package-review.md` | `reports/N02-package-review.md` | reserved by C17; active endpoint showed 2 before launches |

Six canceled historical roles (correctness reviewer B, Matplotlib QA, ECharts QA, columnar QA, text QA, geography QA) remain canceled. Their worktrees/partial files are preserved. The original root could not be resumed through the child-only tool; API delivery alone did not prove running execution. C17 replaces the unstarted C16 assignment. C00 owns only restart/coordination documentation while C17 is active; no duplicate Git integration or issue writing.

## Preserved producer branches at takeover

| Branch | Observed HEAD | Integration / dirty-state note |
| --- | --- | --- |
| `release/candidate` | `468b28cfdcfcb7be53beaef2c911bf81cac70f44` | clean before coordination files |
| `feat/ingestion` | `6c412e0f6be7e96a24a7f6c5cbcfdba9a48ef2c5` | 2 commits not in candidate; clean |
| `feat/renderers` | `31acb2f6e58bc83f71c1736af9d4be37c56ad59c` | 1 unintegrated commit; untracked examples |
| `feat/integrations` | `6731720cfc4c7b0a729c4958a7d2e2f4fe614107` | 1 unintegrated commit; clean |
| `feat/typescript` | `381be19b8fd6faaaa43b7ac04e019e55cb0a7fd5` | 2 unintegrated commits; active dirty changes |
| `ci/verification` | `635c98bc46be9c33e412900131fa095dac163cf6` | 1 unintegrated commit; clean |
| `docs/research` | `0aef12464ab9d02e4904bcefa5e7bc5af22c2c26` | 1 unintegrated commit; clean |
| `docs/process` | `900a9583ea3eab61534bafcc8bac1d610206f4a1` | 2 unintegrated commits; clean |

These are takeover observations, not frozen final handoffs or current runtime states. C01-C16 pending/running labels above are historical unless C17's live register supplies current confirmation. Refresh heads/status before integrating. Use `docs/coordination/C17-live-slots.md` for all current nested tasks, sessions, reservations and source/report mappings.
