# R10-02 independent security-boundary review and strict probes

## Identity, scope and verdict

Owner/native actual ID: **ses_de5678328ffeYCFXQhRPKd4a9h**, reconfirmed by session_move.
Date: 2026-11-27. Assignment: full R10 common contract plus role02, SAME-ID continuation.

What this change does: publishes independent security review and NEW portable tests, not
production fixes. It preserves the completed R03 baseline and tests novel trust/path/file-handle/
resource-authority controls at **3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab**. This is a checkpoint,
not a final source freeze, human approval, project completion or reduction of the full goal.

Owned branch: `agents/r10-02-security-boundaries`. Owned worktree (WT):
`C:/Users/bagma/AppData/Local/Temp/opencode/r10-02-security-ses_de5678328ffeYCFXQhRPKd4a9h`.
Initial clean branch at exact base; only own notes/reports/evidence/new probes added. MAIN was
release/candidate with pre-existing dirty coordination preserved. Original R03 WT/probes and
report/evidence remain unchanged. No spawning, dependency installations, source/existing-oracle
edits, shared Git staging/checkout, issue/PR writes or role20 label-browser duplication.

**Verdict: fix the parser/byte-limit defects and preserved baseline blockers before acceptance.**
Actual focused result: **22 passed / 10 failed / 0 skipped**, pytest exit1, 8.31s.
Focused own-probe Ruff and mypy exit0; this is an intentionally RED review/test branch, NOT green CI.

## Must fix

### 1. P2 - real MCP bypasses the documented raw-inline-byte limit

- **File/line:** `python/deepviz/src/deepviz/mcp_server.py:40-43`, connected
  `tools.py:18,74-90` and README339-342. Installed MCP1.30.0
  `mcp/server/fastmcp/utilities/func_metadata.py:153-189` explains the preprocessing.
- **What this is:** the MCP override validates structural models whose data field is Any,
  then forwards the original string to the SDK. SDK json.loads runs before ToolSession.
- **Problem/reproduction:** `raw = " " * 1_000_001 + json.dumps(payload)`, where payload is
  `[{'category':'Alpha','value':3}]` or `{'file':'rows.json'}` with a host-approved local file.
  The two raw UTF-8 sizes are **1,000,036** and **1,000,022** bytes. ToolSession and LangChain
  reject both with `Inline data exceeds`; the SDK and **real stdio MCP** successfully normalize
  both and return `isError=false`. Small row/JSON/file controls succeed. The original raw byte
  count is lost before tools.py75 sees the value. Four strict current-source tests are RED.
- **Smallest fix direction:** enforce raw bytes and shared duplicate-rejecting JSON decoding
  BEFORE SDK preprocessing, then forward validated canonical JSON, not a resolved Path.
  Share the strict decoder with ToolSession/cache; do not only fix ToolSession or enlarge the cap.
- **If skipped:** the advertised MCP input boundary is not enforced, and callers disagree about
  accepted envelopes. This finite ~1MB test is a resource-policy bypass, NOT an OOM/exhaustion
  measurement, filesystem escape, network exploit or JavaScript-execution claim.

### Preserved baseline findings, explicitly source-specific

The immutable report is `R03-02-security-review.md`, source
`0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43`; original 102pass/1WinError1314skip remains baseline
only. Full 0c5-to-3aa diff inspection found four changed files/50add4del. The only product
boundary change is engines.py727 adding an enum-derived background color. The following sinks
and tools/MCP/normalizer/model/render code are unchanged; baseline measurements are NOT rerun
claims or final approval of 3aa/later fixes.

| ID | Finding and source | R10 disposition |
|---|---|---|
| R03-02-1 P1 | Dense sparse-table expansion before byte checks, engines.py573-579/render.py145-150 | Implementation unchanged; original128row/1,700byte public repro ->16,512graphics/30.7MB traced peak preserved, not remeasured. |
| R03-02-2 P2 | Duplicate JSON silently overwrites values, tools.py78,113 and mcp_server.py40-43 | Fresh six strict RED cases across direct/LangChain/SDK: duplicate data fields AND duplicate file-control keys. Core normalizer rejection control passes. This is semantic loss/ambiguity, not proof of unauthorized file access. |
| R03-02-3 P2 | Plotly category/series creates live HTML links, engines.py355-358 | Sink unchanged. Original actual Chromium evidence preserved; role20 owns fresh literal-label/browser regressions. No new browser or script-execution claim here. |
| R03-02-4 P2 | Unbounded successful resource registrations, mcp_server.py55-93 | Registry code unchanged. Original64render/128resource finite evidence preserved. New exact-issuance/invalid-file controls do not prove a registry lifetime cap. |

## Novel positive controls - 14 pass

`tests/r10_probes/role02/test_trust_controls.py` uses fabricated local canaries only.

- Three reference-shaped data cases, including a mixed file+dataset_id record, remain literal
  data without any data_dir grant. No host canary appears in returned artifacts.
- Four original/copied file-handle cases recheck missing/directory sources before output
  allocation, preserve prior files, and work again after the allowed source is restored.
  Cached recommendation/profile metadata is not misrepresented as a fresh authorized read.
- Literal percent-encoded filenames stay literal, not URI-decoded traversal. A real sibling
  data-shadow directory does not pass containment just because its name starts with data.
- Two issuance controls: an unregistered same-leaf host file and a different server sharing the
  output root cannot be read via guessed/unissued URIs; the original issued resource still works.
- Three registered-file controls: oversize16MiB+1/missing/directory states reject BEFORE bulk
  reads (observational Path.read_bytes spy, still delegates actual I/O). Peer resource preserved;
  restoring the file restores the original resource. No symlink privilege is needed.

These controls exercise public ToolSession and actual SDK APIs/native artifacts. They are not
browser-paint or multi-engine visual signoff, a local-owner/race sandbox, or generic stdio-flow
replacement for role10. Only the new byte-policy case is additionally tested through real stdio.

## Minimal policy proposal to R04 - no source change in this branch

Existing real issue **#21**, observed open, covers this trust boundary. Distinct acceptance:
raw input admission MUST run on the original data argument before any SDK JSON decoding.
The current named constant is exactly **1,000,000 UTF-8 bytes** (not1MiB); do not silently
reinterpret or expand it. Check original string bytes first, then strict JSON decoding with
rejected duplicate object keys and actionable nesting/recursion errors. Forward only validated
canonical JSON to the SDK; preserve exact explicit file/dataset reference semantics and host
configured roots. Never canonicalize to a raw filesystem Path or treat a data string as a path.
Non-string inline objects retain the current finite/byte limits. Cache only the validated
canonical source/reference, so a second permissive json.loads cannot undo this boundary.

Acceptance needs all32 unchanged tests here, role10's independent strict JSON/registry tests,
exact limit/limit+1/UTF-8 controls and valid small file/copy/eviction/resource controls. Registry
capacity/lifetime requires its own explicit policy: fail BEFORE render/registration at capacity
or document bounded expiry with useful errors; never silently delete successful host files or
expose a catch-all filesystem resource template. Original64render/128resource result is not a
capacity test pass. Source ownership: R13 corrects older release assumptions - **02 and10 are
independent testers and cannot edit production**. R04 must record an eligible general-producer
transfer for tools.py/mcp_server.py before implementation, then request independent exact-source
retests. This report does not implement, self-review or approve that future fix.

## Exact commands, outcomes and recovery

Existing interpreter `C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe` used read-only.
Environment: `PYTHONPATH=WT/python/deepviz/src`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`,
`MPLBACKEND=Agg`; imports assert six actual module paths and record SHA256 hashes. No installs.
Own temp root (OUT):
`C:/Users/bagma/AppData/Local/Temp/opencode/r10-02-security-results-ses_de5678328ffeYCFXQhRPKd4a9h`.
The committed README gives a machine-independent recipe with a fresh UUID output directory.

| Command/check | Exact result |
|---|---|
| `git cat-file -t 3aa521a5...`; status/log/worktree checks | Commit exists; initial ownbranch absent (show-ref expected1); MAINdirtycoordination preserved. |
| `git worktree add -b agents/r10-02-security-boundaries WT 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab` | exit0, clean ownbranch. Native session_move reconfirms same actualID. Not recreated on recovery. |
| `git diff --stat 0c5fa825...3aa521a5`; full connected product diff | exit0, fourfiles50add4del; only product change is chart background. Sources/sinks above inspected with callers/SDK. |
| `python tests/r10_probes/role02/source_identity.py OUT/source-identity.json` | exit0; expected3aa source, Python3.12.16/MCP1.30.0/Pydantic2.14.4/LangChainCore1.8.5. |
| `python -m pytest -q -rs --tb=short --basetemp=OUT/pytest-001 --junitxml=OUT/probes-junit.xml tests/r10_probes/role02` | exit1,22pass8fail0skip6.75s; preliminary30cases overlap final run. |
| `python -m pytest -q -rs --tb=short --basetemp=OUT/pytest-002 --junitxml=OUT/final-junit.xml tests/r10_probes/role02` | **exit1,22pass10fail0skip8.31s**,32cases; two realstdio controls added. Raw final log/JUnit retained outside Git; compact exact failure IDs/counts/hashes committed. |
| `python -m ruff check tests/r10_probes/role02` | initialexit1 oneUP017; finalexit0 All checks passed. Only own helper UTC alias corrected. |
| `python -m mypy --cache-dir=OUT/mypy-cache tests/r10_probes/role02` | initialexit1 two optional-module-file errors; finalexit0,4ownfiles. Added explicit non-None import guard only. |
| `python OUT/pack_evidence.py` | exit0; parsed saved JUnit:32/10fail/0error/0skip/22pass;14novel trust passes; compact5evidencefiles copied, oldreport/evidence copied byte-for-byte to ownbranch. |
| `git diff --exit-code -- python/deepviz/src packages/deepviz/src schemas prompts`; `git diff --check` | exit0; production/contracts/prompts untouched. |

Initial long combined shell here-string writes were scanner-rejected before execution; absent
paths were checked and narrower writes succeeded. One Python -c helper edit failed at parse-time
because native Windows argument quoting stripped quotes; no mutation executed, file-backed own
helper rewrites used instead. These were harness/startup errors, not product failures or passes.
No backgrounds or commands were left running; on R13 recovery the saved foreground exits above
were reconciled rather than rerun. Same-session source/branch/probes were reused unchanged.

## Durable evidence and limits

Compact `docs/coordination/evidence/R10-02/` contains source identity/hash/dependency JSON,
pytest exact counts/failure IDs/probe hashes, own final Ruff/mypy logs, and dated sanitized
GitHub GET metadata. Raw final log SHA256
`bfcfef57d9d52e983554492e36e37f7ae49d07606584962fc1100b04246bc572`;
JUnit SHA256 `a9298351beed2b0ddf8a2796f01a48f2a65f2d63c9a0b664380ef211b1b3aee6`.
Original R03report/evidence copied unchanged, not relabeled as current or independent new runs.

First authenticated observation02:28:34.961580UTC: captured GCM output/token in memory only;
GET/user verified sandeshbagmare; fiveGETs HTTP200/no writes. Public expected repo, PR31
open/draft/unmerged atca25af486bf443949125df789f5b5fd1fda8bba8, threePythonjobsfailed, one10M
still in progress. This is dated metadata, not a progress poll or CI acceptance. Identity will
be freshly verified before publication; push/actualSHA receipt remains separately recorded.

NOT RUN: fullpytest/repositorylinttypes/builds/npm/scale/browser/CDN/paidmodels. No maximum-size
OOM, filesystem race/junction/hardlink or actual privileged symlink coverage; prior Windows
WinError1314 skip remains unverified. No final-source assertion beyond stated3aa. No issue/PR
mutation, release, human approval, closed-issue count or manufactured signoff. Full production
and900legitimatecreated/resolved requirements remain unmet. This branch must not be merged as a
passing fix; its strict RED tests preserve evidence for an eligible producer and later review.

## Publication

R10 authorizes ownbranch/ownedpaths only. Publication receipt is pending, not inferred from
local files. Explicit-path stage, staged-whitespace/sanitization review, small commit,
non-force ownbranch push and actual remoteSHA readback must precede a successful publication
claim. R04 retains sharedcandidate/integration/issues/PRs. R13 recovery note records the actual
receipt when available; no earlier baseline blanket publication ban is used to block this scope.
