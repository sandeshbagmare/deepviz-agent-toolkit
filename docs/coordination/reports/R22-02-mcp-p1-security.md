# R22-02 independent committed MCP P1 security review

## What this change does

Exact source d65dfc0fd807d0335b858476de8cdf7c6b958711 checks original UTF-8 data bytes, strictly parses encoded JSON before MCP SDK preprocessing and caches canonical relative references. It adds pre-callback validation for dictionary-form LangChain inputs.

Disposition: fix R22-02-F1 before claiming complete pre-callback admission. MCP admission controls pass within the scope below; broader P1/P2 integration is NOT approved. This reviewer changed no production files.

## Must fix

1. [P2] Bare-string StructuredTool inputs bypass the new early validation.

Location: python/deepviz/src/deepviz/tools.py lines186-196, especially conditions189/194 and superclass calls191/196.
What this is: public StructuredTool methods run and arun accept either a data dictionary or a bare string. Both actually work for these defaulted normalization tools. LangChain explicitly supports this string form; the new subclass guards only dictionaries containing data.

Problem: a bare string reaches LangChain on_tool_start before the eventual tool function checks it. Rejected duplicate JSON, over-budget raw data and excessive nesting are passed in full to configured callbacks before later ValueError. Existing normalizer validation still rejects; this is an incomplete early-admission repair, NOT acceptance of invalid data by normalization.

Reproduction: find normalize_data from create_tools, call its run method with raw encoded data and callbacks=[local_spy], or await arun with the same arguments. New tests/r22_probes/role02/test_p1_security.py provide the exact unchanged strict fixture/assertion. A 49byte escaped duplicate-key input containing the public PUBLIC_R22 marker calls the spy once before Duplicate JSON object key ValueError. Also reproduced with 1,000,001 UTF8bytes but999,994characters of padded ordinary Unicode JSON, and encoded5000depth/10,000bytes. Each invokes one callback in both methods.

Controls: identical inputs wrapped in a data dictionary reject with zero callbacks. Bare valid JSON at exactly1,000,000rawUTF8bytes succeeds; ordinary small requests recover on the same tool. Thus this is a supported form, not a fabricated invalid invocation. Spy is local and stores only byte length/public-marker flag, never the payload. No remote callback, secret or external service used.

Smallest fix: validate bare strings before both superclass calls too, preferably canonicalize them to a validated data dictionary so defaulted tool arguments still work. Preserve strict duplicate/raw-byte/depth and valid string behavior. Do not patch SDK, waive failing tests or silently remove supported calling form. Only eligible producer18/R04 may repair production.

If skipped: configured tracing/log callbacks may retain raw data intended to fail before bookkeeping; pre-callback size admission remains bypassable. No remote exfiltration, code execution, normalization acceptance or measured OOM claimed.

Connected installed LangChain1.8.5 source: langchain_core/tools/base.py779-815 accepts strings; sync on_tool_start1074 precedes argumentparse1092; async1202 precedes1217. Exact installed-source hashes saved. These line numbers are dependency-specific, not product file locations.

Strict findings: test_all_supported_call_forms_admit_before_callback[bare-run] and [bare-arun] remain two genuine failures from ONE cause. No xfail/skip or modified expected results; not six separate bugs/tickets.

## Independent verified controls

- MCP mcp_server.py48-53 validates argument model and inline data before superclass/SDK. tools.py24-29 checks original rawUTF8bytes then uses strict normalizer JSON73-86. Decoded escaped-equivalent value/file keys cannot evade duplicate detection.
- Actual order evidence: read-only sys.setprofile counts installed FuncMetadata.pre_parse_json code entry, restores prior profile in finally, retains no frames and patches no method/cap/decoder. Four bad inputs enter SDK preparse zero times: escapedduplicate,1,000,001rawUTF8bytes,5000depth,escapedfilecontrol duplicate. Then ordinary valid Unicode enters once and returns count1. SDK path server.py359-362 through tool manager and utilities/func_metadata.py94-115,153-191. This is actual SDK invocation, NOT stdio transport acceptance, which role10 owns.
- NEW canonical escaped-file/safe-dot-json and escaped dataset_id copy controls store two original relative dict sources, not resolved Paths: tools.py98-123. Escaped traversal and URL reject before source use; outside public sentinel preserved; denied references add no entries. Changed authorized local file then re-normalized via copied handle changes input_count1to2, proving reread rather than stale reduced cache.
- File authority review tools.py77-95 requires sole file key/configured data_dir, rejects colon/absolute/Windows drive paths and resolves containment. Nested reference-shaped ordinary data is not elevated by this code. No new arbitrary local-file capability found in P1.
- All observed bad errors concise under500characters; ordinary recovery works. Profile-only controls create no artifacts or deletion needs. No visual-paint claim.

Cached recommendation125-137 is advice, not file authority; render139-145 rechecks source. Wrapper147-163 keeps a fresh private destination, contained size-checked artifacts and failure-only subtree cleanup. MCP exposure65-85 rechecks containment/type/size on read. These connected paths reviewed, not broad artifact/HTML/registry retested. No executable expression/remote ingestion/HTML sink added in P1 diff.

## Identity, scope and independence

SAME native session ses_de5678328ffeYCFXQhRPKd4a9h reconfirmed through session_move. FULL MAIN R22common+02/currentAGENTS/canonical/ownnote/RESUME/STATE read. Report/note saved BEFORE substantive work; no source authority/spawn. Initial own branch agents/r10-02-security-boundaries ac73f94cb8817aa124e3b87644b7f5035a16cebb retains older3aa production bytes, NOT tested P1. Two preexisting own untracked R13/R16 terminal receipts preserved and unstaged.

NEW clean detached consumer at d65dfc0fd807d0335b858476de8cdf7c6b958711. Full commit6paths302add24del; whole source/test diff,207line tools,125line MCP,178line new author test read, connected strict JSON parser, SDK preprocessing/callback/run/arun/conversion, lazy wrapper/CLI/examples and README112-224 reviewed. No dirty P2 source/runtime borrowed.

source-before at15:11:08UTC and source-after at15:29:38UTC: five Git blobs equal working bytes; four imports resolve to this pin; installed SDK source hashes/versions equal before/after. ToolsSHA25611273c5f5b0ff2eee16e09c6c727e560582a43fcae723bb315b6ef80d5a68495; MCP77b3ff80e52b88b79e322a15fd9db2a39eec9a1dbd8505480fca0cb54724fcce. Python3.12.16, LangChain-core1.8.5, MCP1.30.0, Pydantic2.14.4 observed.

All tests use fresh local public sessions and synthetic data. Cache inspection read-only, no injected entries; no private reducer/cap/SDK changes or symlink privileges. No old32 probe replay, no author37 replay/borrowed result. Role10 independently owns those committed37tests and transport. NEW8cases target callback order/escaped keys/canonical provenance, not padded coverage.

## Commands, exits and saved evidence

Run from OWN report/probe checkout r10-02-security-ses_de5678328ffeYCFXQhRPKd4a9h. SOURCE C:/Users/bagma/AppData/Local/Temp/opencode/r22-02-mcp-p1-d65-ses_de5678328ffeYCFXQhRPKd4a9h. OUT C:/Users/bagma/AppData/Local/Temp/opencode/r22-02-mcp-security-results-ses_de5678328ffeYCFXQhRPKd4a9h. PY existing MAIN .venv/Scripts/python.exe read-only. PYTHONPATH=SOURCE/python/deepviz/src, PYTHONDONTWRITEBYTECODE=1, PYTHONUTF8=1. No dependency install or environment mutation.

1. Quoted git rev-parse --verify fullPIN commit0; git worktree add --detach SOURCE fullPIN0; exactHEAD/cleanstatus/diffcheck0. No existing worktree reset/discard.
2. PY OUT/inspect_sdk.py0 records installed source and complete actual run/arun/input-conversion methods. First ad-hoc -c inspection1 PowerShell quotes/NameError in own helper, corrected written helper; not product failure. PY OUT/first_callback_repro.py0 observed same issue on small duplicate; not extra test coverage.
3. PY tests/r22_probes/role02/source_identity.py OUT/source-before.json0; after tests same helper OUT/source-after.json0. All saved source/import/SDK bytes unchanged.
4. Initial own8case pytest: exit1,2failed6passed0skipped2.35s. Failed own text-replacement command intended to mark known bare cases xfail: marker-not-found1 before writing. Ruling: DO NOT relabel failures; no xfail mark added. Keep original strict assertions and real RED.
5. First Ruff0. First mypy shell scanner rejected extra-parenthesis command before execution; corrected actual mypy1 one OWN local-container inference issue at testline84. Added explicit observations:list[dict[str,Any]] annotations only. No fixture/expected/assertion changes.
6. Final R22_02_RESULTS=OUT/final; PY -m pytest tests/r22_probes/role02/test_p1_security.py -q -rs --tb=short -p no:cacheprovider --basetemp OUT/final/pytest --junitxml OUT/final/security-probes.xml: exit1,2failed6passed0skipped1.72s. Initial/final same8cases, not16independentcases.
7. Final PY -m ruff check tests/r22_probes/role02 exit0; PY -m mypy --cache-dir OUT/mypy tests/r22_probes/role02 exit0,2ownPythonfiles. These focused harness checks do NOT imply whole product lint/types/tests pass.
8. Large report write twice scanner-rejected before execution; smaller plain-prose scoped writes succeeded. No command/test result/source lost or fabricated. Exact portable command recipe saved tests/r22_probes/role02/README.md.

Compact actual JSON observations, source/SDK/probe/GitLF/raw-log hashes and reconciliation under docs/coordination/evidence/R22-02. Full local initial/final logs/XML retained in OUT; no raw payload or secrets saved by callbacks.

## Publication, limits and executable next action

Fresh authenticated expected identity/repo at15:31:20.250222UTC,4GET/HTTP200/APIwrites0. GCM token memory-only, no subprocess arguments/files/logs. PR31open/draft/unmerged head6c72cec40e3feb8d710ab55167453194f643d650; Python3.11/3.12/3.13checksFAIL, othersseenSUCCESS. Dated source-specific observation, not focused-PR readiness/issuecensus/greenCI. OWN meaningful checkpoint/nonforcepush/exactremoteSHA pending actual operations, not guessed.

NOT CHECKED: P2resource128lifetime/concurrency/capacity is NOT in P1 and remains open until producer18 actual committed handoff. No P2dirty-file inspection/progress poll/reassignment. No fullsuite/build/install/old32/author37/stdio/DeepAgent/provider/browser/scale/memory measurements. UTF8 policy is data admission, NOT total transport/allocation1MB or RSS limit. Profile-only review visual output N/A; prior artifact/Plotly/registry findings not closed. Altered SDK versions not exercised.

Next executable action: root/R04 disposition F1 and send strict probes/report under existing eligible18 lane AFTER its current command checkpoint. Only18/R04 may repair accepted bare-string path; reviewer02 and tester10 remain non-author. Retest unchanged strict controls on clean resulting committed pin with explicit new identity proof, not final-source signoff from oldd65. No approval, source integration, issue closure or release invented. Fullproduction/900legitimatecreatedANDresolvedissues/greenCI remain unmet.
ActualP1checkpoint: pack_evidence.py exit0 reconciles initial/final8XML/real2fail6pass0skip, beforeafterfiveGitblob/fourimports/SDKsame and13compactJSONfiles copiedMAIN+OWN. No tests rerun during collection. LatestuserP2handoff acknowledged: AFTERthis P1publicationcheckpoint, NEWP2diff review finalimmutablee47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23/P2cd75c459ddba9f3d6bc0a5185b570af369fb4980, sourcegrantR04reclaimed; no longer infer producerjobstillrunning. P1observationsremain d65-specific until exactunchangedpathhashproof; F1remainsstrictRED/no sourcefixpermission. Next explicitOWN18filesstage/credential+whitespace+GitLFscan/meaningfulcommit/nonforcepush/exactremote beforeP2newreview.
ACTUALP1publicationcheckpoint15:40:15.427237UTC: OWN2855f7a4d051297e1d9e1246fd3051d35e2a11f0 nonforcepush0/exactls-remote0;18files924add/74,918Bstagedscopecredentialscan0zeromatches/whitespace0/3probeGitLFhashesmatch/productdiff0. Receiptpublication-2855f7a.json savedMAIN+WT; this actualpostpushobservation willjoinnextOWNP2checkpoint ratherthanreceiptloop. NewP2reviewbeginsONLYNOWafterP1checkpoint; P1F1strict2REDcarriednotapproved/sourceuntouched.
