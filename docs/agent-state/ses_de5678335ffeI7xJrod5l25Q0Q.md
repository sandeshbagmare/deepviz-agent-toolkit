# R03-01 correctness review: initial checkpoint

Owner/actual session: ses_de5678335ffeI7xJrod5l25Q0Q (native session_move confirmed), 2026-11-27.
Source PIN: 0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43. Initial MAIN release/candidate HEAD matched pin, ahead47; dirty coordination history/artifacts preserved.
Read fully: R03 COMMON+01, R05, PROJECT_STATE, RESUME, STATE; supplied AGENTS/design and ponytail-review guidance loaded.
Scope: independent READONLY normalization/reduction/models Python/TS correctness review with concrete count/shape/numerical/resource repros. Baseline only, not final signoff.
Allowed writes: own actual-ID MAIN note, MAIN R03-01 report, own sanitized docs/coordination/evidence/R03-01/, one NEW detached unique pinned worktree probes/artifacts. No source/shared Git/GitHub/others notes/installs/spawning.
Acceptance: exact source and module hashes, commands/exits/totals/skips/artifacts/limits and actual repros with lines.
Executed: initial git rev-parse HEAD/status/worktree list and Test-Path own paths/shared venv, exit0; note/report absent and venv present.
Failure: combined initial note+worktree shell rejected by portable scanner invalid-structure; followup Test-Path exit0 confirms no files/worktree created. No tests run yet.
Current action: save initial checkpoint, create isolated clean detached pinned worktree, read diff/connected source/contracts.
Limit: live GitHub status unverified, no immutable-source dependency. No results or approvals invented.
Next executable action: git worktree add --detach C:/Users/bagma/AppData/Local/Temp/opencode/r03-01-correctness-ses_de5678335ffeI7xJrod5l25Q0Q 0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43

## Checkpoint after isolated source inspection

- Isolated worktree: `C:/Users/bagma/AppData/Local/Temp/opencode/r03-01-correctness-ses_de5678335ffeI7xJrod5l25Q0Q`, detached HEAD `0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43`, clean at inspection. No source edits.
- Read Python `normalize.py`/`models.py`, TS `normalize.ts`/`models.ts`, architecture and C17 resource/format/schema policies, N04/N03 reports and relevant normalization/parity tests.
- Module hashes from pinned worktree: Python normalize `0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83`; Python models `890ecb0e29e1345364b2bf4840bdea7a542067003caf54d7b0855536ee2b6a76`; exact source SHA is pin.
- Node `v26.13.1`, npm `11.20.0`; main installed TypeScript compiler used read-only; detached `node .../typescript/bin/tsc -p packages/deepviz/tsconfig.json` exit0 and produced own `packages/deepviz/dist` only. No npm install.
- Initial focused Python command was attempted in a parallel batch but its module-hash expression imported `deepviz.normalize` through the package-level `normalize` function and raised `AttributeError`; pytest portion did not execute (exit1). This is a harness error, not a test result. Corrected command pending.
- Static source review identified two candidate correctness repros pending execution: Python `_expand` unwraps a top-level scalar array under known wrapper names, while TS preserves it as a named column; Python `_Reducer.add` canonicalizes every numeric group key through `float`, which can merge unsafe large integer categories or raise OverflowError for huge integers.
- Current action: run corrected focused tests and isolated probes; classify only actual reachable defects.
- Next executable action: run own isolated probes against the Python pinned module and Node public built `dist/index.js`, saving logs under own ignored artifact root.

## First independent verification checkpoint

- Corrected focused command (main interpreter, pinned PYTHONPATH, PYTHONDONTWRITEBYTECODE=1): `python -m pytest python/deepviz/tests/test_normalize.py python/deepviz/tests/test_aggregation_semantics.py python/deepviz/tests/test_n04_normalize_regressions.py tests/test_n12_authoritative_parity.py -m 'not integration' -q --tb=short -p no:cacheprovider` exited0, **301 passed /106 deselected /0 skipped**,7.73s.
- Pinned public npm parity command: same interpreter/environment, `python -m pytest tests/test_n12_authoritative_parity.py -m integration -q --tb=short -p no:cacheprovider` exited0, **106 passed /161 deselected /0 skipped**,0.49s.
- Node focused four-file command for normalization-policy/bytes/means/unicode-coercion: exit0, **38 passed /0 failed /0 skipped**,2529.481ms. This is not whole-package/final candidate acceptance.
- Actual raw Python/TS probes confirm wrapper scalar-column mismatch: Python `{rows:[1,2]}` becomes index/value records and loses the `rows` column name; TS preserves `rows` values. All five Python wrapper names behave alike. Policy disposition pending more explicit-map tests.
- Initial numeric-key suspicion is **disproved**: `_Reducer.add` stores `float` as a type tag, NOT `float(value)`. Python retains distinct 2**53 and 2**53+1 and distinct huge integers 10**400 and 10**400+1, with correct separate sums and no errors. Do not report numeric key merging as a finding. TS unsafe-integer precision remains documented, not a new defect.
- Another attempted resource/model batch used a nonexistent path `python/deepviz/tests/test_models.py`; exited4 with zero tests. Correct path is `tests/test_models.py`; pending corrected rerun. No pass inferred.
- Source diff verification exit0 and detached status clean: production files remain identical to PIN. TS normalize SHA256 `d1b45d2a55dfd05361184a57da952a0da735e9b6d72c2491f908ef27bda22371`, TS models `d43d5ae0bef1d43f251ed71899a9b507c6575562e4403bd2e2ac02bd7caa43e6`.
- Checkpoint append attempt via Python -c was rejected by quoting SyntaxError (no successful write); corrected here-string Add-Content saved it. One accidental read of nonexistent `C:/Users/bagma/bad` returned file-not-found; no file writes or substantive impact.
- Current action: isolated probes for direct GraphQL sibling loss/custom wrapper ambiguity and preservation of count measure after channel inference. No source fix performed or authorized.
- Next executable action: run an owned `tests/r03_probes/role01/` case driver against pinned Python and TS modules, save actual command/exits/values in own evidence subtree.


## Confirmed material repro checkpoint

1. P1 TypeScript silent sibling data loss: normalize.ts:130-141 consumes only nodes in nodes-array envelopes with unexpected version or audit sibling. Sync and stream return id=1/count1 with zero warnings; Python rejects ambiguous siblings. Explicit data_path nodes is a passing control.
2. P1 Python invalid count mapping: normalize.py:547-548 correctly produces g=a,s=100,count=2 for two rows with x=g,color=s,aggregation=count. engines.py:59-73 re-infers y=s, not count. ECharts/Plotly/AntV/Vega native payloads encode100 instead of2 without warning. Connected-code invariant only; no renderer/theme fix.
3. P2 Python wrapper scalar-column mismatch: normalize.py:364-376 turns rows:[1,2] into index/value and explicit y=rows fails. TS sync preserves rows and succeeds. C17 schema-shape contract requires preserving generic columns or rejecting ambiguity; recognized-wrapper policy disposition needed.
Owned observation drivers ran exit0 (observations, NOT pass-count tests): python tests/r03_probes/role01/probe.py and node tests/r03_probes/role01/probe.mjs. Actual values/module paths/hashes are saved in own isolated artifacts/local/R03-01/python-observations.json and typescript-observations.json. Source/cases in owned tests/r03_probes/role01/.
Additional small subnormal mean observation: [1,5e-324,-1,5e-324,5e-324] returns0 in both languages versus exact rounded5e-324; route role16 as numerical edge, not ordinary cancellation or scale failure.
Current action: own strict bounded regressions and positive controls, durable raw logs, corrected resource/model tests. No source/oracle edits.
Next executable action: run owned Python/Node regression tests after writing only tests/r03_probes/role01/ files.


## Raw-log verification checkpoint

Owned run_checks.py exit0 collected7 commands (driver success is NOT overall verification success); raw argv/exits/hash paths in isolated artifacts/local/R03-01/verification-v1/summary.json. Observed/read back:
- Python independent regressions: exit1,10 failed/6 passed/0 skipped,0.42s. Five failures are count channel/native values100 vs2; five scalar-column-name oracles fail. These are2 defect groups, not10 issues.
- TypeScript independent regressions: exit1,9 failed/7 passed/0 skipped,170.4158ms. Eight direct nodes/edges sibling ambiguity failures plus custom GraphQL wrapper policy failure; explicit-path/metadata/column positive controls pass.
- Corrected existing resource+models: exit1,4 failed/52 passed/0 skipped,2.29s. Exactly64KiB field-name expectations conflict with implemented Python4KiB field ceiling; role04 owns policy disposition, not a newly inferred memory bug.
- Existing models+cross-language+raw/default contract: exit0,630 passed/0 skipped,2.41s. Own rebuilt public package used; no stale sibling dist.
- Complete existing Node test directory: exit0,246 passed/0 failed/0 skipped,6201.3148ms. Thus new source-backed regressions expose gaps not covered by this green existing suite.
- git diff --exit-code PIN -- Python source TS source: exit0; detached source unchanged. Dirty only new own tests/r03_probes/ directory; own ignored dist/artifacts.
- Read full diff from b6abc8d to PIN for normalize.py/models.py/normalize.ts/models.ts and connected callers (render.py/engines.py + TS mapping). Diff command exit0; full retained tool log path sh_21ab9dc4f001MPwYXhqqcVeszH.out. Last HEAD0c5fa82 only changes no-truncation oracle; no claim every finding was introduced by that commit.
Current action: verify provenance (existing vs introduced defects), preserve sanitized own evidence in MAIN, write final bounded report and ownership note.
Next executable action: save git-blame/repro provenance and copy own small raw logs/summary to docs/coordination/evidence/R03-01/.

## Final durable handoff checkpoint (2026-11-27)

- Status: bounded independent baseline review submitted; production is NOT approved. Final report: docs/coordination/reports/R03-01-correctness-review.md. Sanitized own evidence: docs/coordination/evidence/R03-01/; full local-only logs/probes remain under the unique detached worktree artifacts/local/R03-01/ and tests/r03_probes/role01/.
- Exact source remains 0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43, detached; source diff against pin exit0. Only own NEW probe directory is untracked; own ignored dist/artifacts preserved. No source changes, old test edits, installs, GitHub writes, staging/commits or spawning.
- Material findings: F1 TypeScript direct nodes/edges silently drops unexpected scalar/object siblings (8 genuine regression failures plus1 related custom-wrapper policy failure); F2 Python count=2 becomes native chart value100 because numeric color is re-inferred as y (5 genuine channel/native failures); F3 Python scalar wrapper-named columns lose names versus TS (5 independent failures; policy disposition remains root-owned). Exact source lines/repros/fix scope/provenance in final report.
- Final captured test results: ownPython10failed/6passed; ownNode9failed/7passed; existingresource+models4failed/52passed (role04 field-budget oracle disposition); existingmodel/schema/crosslanguage630passed; completeexistingNode246passed. Zero skips in those commands. Earlier focused301pass/106deselected, N12integration106pass/161deselected and focusedNode38pass are separate overlapping checks, not summed as unique coverage.
- Evidence capture finalize_evidence.py exit0 wrote12 sanitized own MAIN copies plus index.json; this is evidence capture, NOT an overall test pass. Source/module hashes and exact command argv/exits/log hashes in review-summary.json. Original in-progress report preserved under own artifacts/local/R03-01/report-before-final.md; no other agent's note modified.
- Low-magnitude follow-up: exact-Fraction oracle rounded5e-324 vs actual0 for mean([1,5e-324,-1,5e-324,5e-324]) in both languages; role16 routing recommended. Numeric group-key conversion suspicion was disproved and must not be propagated as a finding.
- Unverified: later R04 source, full Python/lint/type, distributions, all-tier/10M/total RSS, real browser/visual/security/MCP/GitHub acceptance. No skipped command or saved historical report promoted to a pass. No issue closure or human approval claimed.
- Current action: read back report/evidence and verify exact hashes/source one final time, then return the durable report paths. No own background job remains from this review (all executed work ran foreground).
- One executable next action for root/R04: from the isolated pinned worktree run `node --test --test-reporter=tap tests/r03_probes/role01/correctness.test.mjs` (expected exit1/9fail7pass), route F1 to TS normalization owner and F2 to Python shared mapping owner, then request fresh review on a corrected immutable pin. Baseline findings are not signoff on the future candidate.


Final readback verification exit0: all12 copied evidence hashes, loaded module paths/hashes, raw red/green totals, exact detached HEAD and empty production diff verified. Final report read back fully. Details: docs/coordination/evidence/R03-01/readback-verification.json. Bounded review is handed off with RED findings, not approval; next action remains the integrator reproduction/routing command above.


## R10 SAME-ID continuation: pre-work checkpoint

- Actual identity reconfirmed native session_move: ses_de5678335ffeI7xJrod5l25Q0Q. Latest user/R10 COMMON+role01 read fully; own R03 baseline report/note and current PROJECT_STATE read. Laptop GitHub workflow loaded. POC=point of contact; full production/900 honest issues remain; no spawning.
- Scope: portable NEW strict connection-sibling/count-measure/scalar-column regressions and positive controls against exact checkpoint3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab; preserve immutable0c5fa825 baseline. Production normalizers16/R04 and enginesR04 remain forbidden; no existing oracle edits.
- OWN branch authorized: agents/r10-01-correctness-regressions in NEW isolated worktree. Allowed source writes: tests/r10_probes/role01/, own R10 report/evidence, own actual-ID note only; own GitHub branch publication now explicitly authorized by R10, superseding baseline publication ban only for owned paths/branch. No MAIN stage/checkout/shared Git/GitHub issue/PR writes or installs.
- Acceptance: exact checkpoint source/import identity; strict reproducible RED plus passing controls, no stale sibling dist or false green; explicit owned staging/diff/whitespace/secret scan; configured author; authenticated GET/user sandeshbagmare with GCM token in memory only; small honest commit, non-force OWN branch push and actual remote SHA readback.
- Current action: safe local/source/worktree/remote identity discovery, authenticated GET/user, create own branch at exact checkpoint; results not yet observed.
- GitHub state unverified in this continuation; prior evidence is historical. No test/push/current-head approval claimed.
- Next executable action: git rev-parse HEAD; git status --short --branch; git cat-file -t 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab; git worktree list --porcelain; safely check origin/credential helper and authenticated GitHub identity before publication.


## R10 source/authentication checkpoint

- Authenticated GitHub GET/user HTTP200 verified sandeshbagmare. GET repo HTTP200 verified intended public sandeshbagmare/deepviz-agent-toolkit; credential-free HTTPS origin verified, configured author nonempty, GCM helper manager. Token captured only in process memory, never printed/persisted/arguments. Own remote branch GET returned404 before writes. GET issue23 HTTP200: open renderer-output evidence issue; no issue/PR mutation/census. Sanitized discovery record in unique local evidence path (not all copied to public evidence).
- Created new isolated branch agents/r10-01-correctness-regressions at exact checkpoint3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab; git worktree add exit0, own clean status. Worktree: C:/Users/bagma/AppData/Local/Temp/opencode/r10-01-correctness-ses_de5678335ffeI7xJrod5l25Q0Q. R03 worktree/source left untouched.
- Production diff from0c5baseline to3aacheckpoint affects only3theme lines in engines.py among targeted normalizer/mapping files; new exact-checkpoint probes still required, baseline outcomes not promoted.
- Current action: author small portable NEW Python/Node strict regressions and README under own tests/r10_probes/role01/. Check source identity, genuine RED plus explicit path/metadata/numeric-color/heatmap/scalar-record positive controls; no production edits.
- Next executable action: build own TypeScript dist with existing read-only compiler, then run both new test files with captured raw exits/counts/module hashes.

## R10 checkpoint-source RED verified before publication

- Exact source3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab; own branch agents/r10-01-correctness-regressions. NEW portable tests only, no production/old-oracle edit. Shared read-only Python3.12.16 and installed TypeScript compiler; own dist only; no installation.
- Captured build exit0. NEW Python exit1:33tests,12failed/21passed/0errors/0skips,0.96s. Failures:5explicit scalar-column mappings and7count-channel/native checks (including numeric labels0,100,-4). NEW Node exit1:30tests,11failed/19passed/0skip/0cancel,246.6305ms. Failures:10direct/async/encoded connection-sibling cases plus1custom-wrapper ambiguity case. This is3finding families, not23issues.
- Positive controls pass: explicit paths/metadata, nested arrays retain parent fields, explicit count measure, categorical series, heatmap y-coordinate preservation, TS native count values. Actual raw logs read back fully.
- Existing Python normalize/statistics/models exit0:145passed/0skip. Existing full Node directory exit0:246passed/0fail/0skip. Scoped new-test Ruff exit0. Production/schema diff versus checkpoint exit0/empty. No full Python/whole-release/browser/scale/type pass inferred.
- Exact argv, test IDs, module/source/test hashes and logs: OWN worktree artifacts/local/R10-01/run-v1/summary.json (capture.py overall exit1, preserving RED). Initial pre-execution redundant Node-identity block removal command was rejected by shell scanner invalid-redirect; no write occurred, corrected own unexecuted file via here-string. It is not a source or test failure.
- Current action: copy compact sanitized own evidence, report and note into own branch; inspect explicit staged scope/diff/whitespace/credential patterns; commit the useful strict RED tests honestly, non-force own push and actual remote SHA readback.
- One next executable action: git diff --cached --check after explicit owned-path staging in the R10 isolated worktree, followed by non-force OWN-branch publication only after staged review.
