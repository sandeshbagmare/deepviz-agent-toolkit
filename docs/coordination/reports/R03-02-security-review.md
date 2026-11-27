# R03-02 independent pinned-source security review

## Identity and verdict

Date2026-11-27. Actual native session ID **ses_de5678328ffeYCFXQhRPKd4a9h**, returned by session_move. Assigned R03 COMMON CONTRACT+section02 and R05; no spawning/source fixes/installs/commits/GitHub mutations/other notes.

**Exact source: 0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43.** One new detached worktree (WT): `C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-ses_de5678328ffeYCFXQhRPKd4a9h`. Initial clean; final tracked diff empty, only own untracked tests/r03_probes/. MAIN initially release/candidate at this SHA,ahead47, with many existing dirty notes/artifacts preserved; no remote state claimed. Allowed writes: own MAIN note/report/evidence/R03-02, own WT probes/temp artifacts only.

**Verdict: fix1-3 before treating this baseline as release-ready; address4 for bounded long-lived MCP operation.** Independent reviewer-agent baseline, NOT final signoff/human approval/project completion. Later source is not covered.

## What this source does

Tools validate declarative ChartSpec, reduce input, cache32dataset handles and write request-owned unique artifacts. MCP exposes seven tools and registers generated artifact resources. Inspected diffs52b817d,65b3fc4,4a766c4 plus pinned HEAD/stat and connected source/tests. Expected load: documented local stdio/agent flow, not a multi-tenant network service.

## Must fix

### 1. P1: sparse tables allocate dense native objects before byte checks

**File/line:** `python/deepviz/src/deepviz/engines.py:573-579`; connected `render.py:145-150`, HTML `engines.py:716-723`.

- **What this is:** ECharts creates one text-graphic object per retained row times every field anywhere, including missing cells.
- **Problem:** native_spec constructs the entire Cartesian product BEFORE render.py149 checks32MiB serialized payload. Tiny sparse retained records bypass a useful pre-allocation byte bound. HTML densifies again.
- **Repro:** own probe_security.py runs normalize/native_spec with `rows=[{f"f{i}":i} for i in range(n)]`, table,aggregation=none,max_points1000. n64/128/256: input812/1700/3620bytes becomes4160/16512/65792graphics; traced adapter peaks1811860/7156324/28492468bytes BEFOREserialization. Native JSON438727/1761145/7090925bytes. Public ToolSession.render_chart n128also succeeds: input/output128/128,16512graphics,30698762tracedpeak,6.52s, HTML1700301bytes and manifest3683638bytes from1700inlinebytes. No limit reached.
- **Fix:** preflight a declared dense-cell/estimated-byte budget before native table/HTML allocation; reject clearly or use a bounded representation. Do not silently truncate or rely only on post-allocation JSON/file checks.
- **If skipped:** small valid sparse input can exhaust CPU/memory before rejection. Measured only finite sizes; NOOOM/maxmatrix/RSS/10Mrender attempted. Tracemalloc is traced Python allocation, not inclusive continuous OS memory. Field/row maxima still permit very large products (normalize.py46-51/models.py43); larger-size impact is code-derived, not benchmarked.

### 2. P2: tool/MCP JSON decoding silently drops duplicate fields

**File/line:** `python/deepviz/src/deepviz/tools.py:74-84,111-116`; MCP `mcp_server.py:40-43`; strict parser `normalize.py:73-85,136-158`.

- **What this is:** plain json.loads before normalization/cache keeps only the last duplicate value.
- **Problem:** this bypasses deliberate duplicate-key rejection in normalize. A successful handle/chart can contain altered data with no warning. MCP structural validation does not prevent the installed SDK plain-json preprocessing of Any-valued strings.
- **Repro:** raw `[{"name":"original","name":"replacement","value":1}]`, table/aggregationnone. Direct normalize rejects `Duplicate JSON object key`. Public StructuredTool normalize -> returnedhandle -> render succeeds with records `[{"name":"replacement","value":1}]`,warnings[]. Own real stdio MCP call/resource-read independently confirms isErrorfalse,warnings[],same overwritten records. Installed MCP1.30.0 pre-parses at `.venv/Lib/site-packages/mcp/server/fastmcp/utilities/func_metadata.py:153-189` (179-181).
- **Fix:** shared duplicate-rejecting decoder for ToolSession source/cache, AND canonicalize/validate raw MCP data BEFORE SDK preprocessing in call_tool. A ToolSession-only fix misses realMCP. Preserve relative-file/dataset authority and catch excessive recursion too.
- **If skipped:** input meaning changes silently; direct API/tool/MCP contracts disagree and loss is not reported.

### 3. P2: Python Plotly category/series data creates live HTML links

**File/line:** `python/deepviz/src/deepviz/engines.py:355-358`, audit other markup-capable label/text at369-398; contrast escaped table/title at399-407 and safe_json32-38/748.

- **What this is:** safe_json blocks script-tag breakout, but Plotly later interprets supported rich HTML inside unescaped category/series strings.
- **Problem/repro:** actual ToolSession Plotly bar with category+group `<a href="https://example.invalid/R03_02_DATA_LINK">R03_02_LINK_TEXT</a>`,y1,plus safecontrol. Own probe_plotly_html.py generates unchanged self-containedHTML; own probe_plotly_html.cjs uses existing Playwright1.65.1/Chromium159.0.8154.6 and awaits real render. DOM contains TWOliveSVGanchors (tick/legend), xlink:href to the .invalid sentinel,target_blank,textR03_02_LINK_TEXT, instead of literal markup. AllHTTP(S) blocked; no click/no requests/no console or runtime errors.
- **Fix:** HTMLescape string values in every Plotly rich-text-capable data/series/label/text position, preserving numeric types; retain script/outerHTML escaping. TS already uses a string text helper at packages/deepviz/src/renderers.ts175-199.
- **If skipped:** data changes visible labeling and inserts unsolicited navigation/phishing links. Confirmed HTML/link injection, NOT demonstratedJavaScript execution or credential access. HTMLSHA25639489ff3a4fd6947d48fae9357e5b8b5277723f9c5e6ec25665890e16305215b.

## Should fix

### 4. P2: successful MCP renders accumulate unbounded resource registrations

**File/line:** `python/deepviz/src/deepviz/mcp_server.py:55-75,77-93`; tools.py117-118bounds only datasets.

- **What this is:** every unique artifact registers a new read_artifact closure. Installed MCP ResourceManager stores all in a dictionary; list_resources materializes every entry.
- **Problem/repro:** one real create_server,64small ECharts calls via actual SDK call_tool:16/32/64calls=>32/64/128resources from public list_resources; aftergc traced retained284008/479994/871961bytes. Earliest resource still readable. No private registry mutation/fake renderer. No cap/expiry/removal; deleting disk artifacts does not delete registrations.
- **Fix:** explicit session-issued-resource cap/lifetime, enforced before generating more output, or explicit expiry with documented errors. Keep issuance/containment checks; do not delete successful host files silently or expose arbitraryfilesystem via a template.
- **If skipped:** long-lived local process/discovery replies grow with historical renders despite bounded datasets/files. README269-275documents disk retention, not registry growth. Small overhead for short one-shot runs; NOexhaustion attempt.

## Checked boundaries and unverified areas

- Final focused suite: **102passed/1skipped/0failed51.05s**, real stdio seven-tool discovery/calls/allfiveengine resources, strict extraarguments, dataset copy/eviction/isolation, cleanup/peer preservation, LangChain/DeepAgent flow, script-closing and Vega/Plotly escaping oracles. Not universal coverage.
- Own realstdio probe denies parent/encodedtraversal, Windowsabsolute,remoteURL,rawpath,expiredhandle with useful errors and no exposedtraceback; fabricated local sentinel unchanged/unreturned; subsequent allowedfile succeeds. No realsecret access/remoteexploitation.
- No reproduced model-only traversal bypass. Symlinkswap test SKIPPED WinError1314 (host privilege); junction/reparse/hardlink/race not validated. README explicitly excludes maliciouslocalfilesystemowner/concurrentrace sandbox; not reported as an unqualified exploit.
- Read strict ChartSpec extras/enumerations and fixed nativebootstrap. Python source grep for eval/exec/subprocess/os.system/Popen/urlopen/http clients hadNOmatches. No model-authored execution/remote-dataURL path found in inspected boundary; no audit of thirdpartyrenderer internals/advisories.
- 10000nested emptyJSONarrays (20000characters) raises raw RecursionError in ToolSession; realMCP returns error text withouttraceback and recovers. Lower-priority error-contract hardening, NOTprocesscrash/criticalexploit. Sharedstrictdecoder fix should cover it; existing1500depth tests pass.
- TS render.ts/renderers.ts/models.ts read only; NO TS build/test/browser claim. Host-authorized assetoptions are separate from ChartSpec. No borrowed role20 evidence.
- NO fullpytest,mypy,Ruff,build,distribution,10Mscale,CDN,paidmodel,remoteGitHub/CI/issues/PR,OOM/maxmatrix or multiengine visualacceptance. One Plotly DOMsafety check is not visual signoff. No final reviewed head beyond pinned source.

## Exact commands and outcomes

WT is path in identity. Existing Python `C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe` (3.12.16). Before successful substantive checks set PYTHONPATH=WT/python/deepviz/src; PYTHONDONTWRITEBYTECODE=1; PYTHONUTF8=1; MPLBACKEND=Agg. No installs/shared env edits. Preliminary read-only import withoutPYTHONPATH resolvedMAIN and was NOTtest evidence; corrected identity asserted all6modules underWT.

1. session_move MAIN/WT success, sameactualID. Read assigned COMMON/02/R05/canonical/RESUME/STATE/N06report/resourcepolicy. MAIN git status --short --branch;git rev-parse HEAD;git worktree list --porcelain exit0. `git worktree add --detach WT 0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43` exit0. Scoped git show/log diffs exit0.
2. Initial combined startup shellwrite rejected portable-scanner invalid-structure beforeexecution; Test-Path confirmed ownnote/report/WTabsent, narrowwrites succeeded. Later combinedprobehelper/finalreport shell commands similarly scannerrejected; readbackconfirmed reportunchanged; splitnarrowwrites succeeded. No product mutation. One guessed absent python/deepviz/pyproject.toml read gave nonterminatingFileNotFound; rootpyprojectread succeeded.
3. Initial selected65test pytest exit1:65setuperrors/zero bodies due nonexistentbasetemp parent WinError3, notsource finding. Raw output C:/Users/bagma/.local/share/opencode/shell/17ee7ceebbcd5b5c9e301ccb5a97b3b2e50ff842/sh_21aa8488b001tsqs9LfMI03cxK.out. Ownparentcreated; same7modules rerun exit0,64passed/1skip31.62s. No doublecount with final suite.
4. Own probe_security.py firstrun exit1 after64renders because helper assumed list notSDKstructuredoutputtuple; failedprobe-001/artifacts/logpreserved, no combinedresultclaim. Fixed onlyownhelper. `python tests/r03_probes/security-review/probe_security.py C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/probe-002` exit0:duplicate,64renderregistry,64/128/256table,64/1500/10000depth finiteprobes, summary/logsaved. Additional read-onlySDKinspect tried missingmoduleattribute resource and exited1 after printingResourceManager; corrected directfileinspectionreadactualSDK. Doublyencodedhandle was explicitly rejected (probeexit1) and nottreatedasdefect; one preliminaryshellJSONquoting probe produced onlySyntaxWarning and was superseded by file-backedrepro.
5. `python tests/r03_probes/security-review/probe_stdio.py C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/stdio-001` exit0:actualstdio duplicate,7denied/errorcases,allowedrecovery/unchangedsentinel. summary/stderr/logpreserved.
6. Final exactfocused command (sameexistingpython/pinnedPYTHONPATH):

`python -m pytest -q -rs --tb=short --basetemp=C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/pytest-parent/run-002 --junitxml=C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/focused-junit.xml python/deepviz/tests/test_mcp_transport.py python/deepviz/tests/test_n06_mcp_validation.py python/deepviz/tests/test_n06_tool_lifecycle.py python/deepviz/tests/test_n06_encoded_handles.py python/deepviz/tests/test_backend_plotly.py python/deepviz/tests/test_backend_vega.py tests/test_n13_concurrency.py python/deepviz/tests/test_render.py::test_untrusted_strings_cannot_end_json_script_or_html_title python/deepviz/tests/test_integrations.py`

**Exit0,102passed/1skipped51.05s.** Exact skip mcp_transport.py172 Hostdoesnotpermitsymlinkcreation WinError1314. focused-pytest.log/focused-junit.xmlsaved. Earlier64passoverlap, notdistinctcoverage.

7. `python tests/r03_probes/security-review/probe_sparse_public.py C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/sparse-public-001` exit0,summary/artifacts/logsaved.
8. `python tests/r03_probes/security-review/probe_plotly_html.py C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/plotly-html-001`; `node tests/r03_probes/security-review/probe_plotly_html.cjs C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/plotly-html-001` bothexit0. Existing Node26.13.1/Playwright1.65.1/Chromium159.0.8154.6. ActualHTMLhashabove,2liveanchors,0requests/consoleerrors/pageerrors. No click/install.
9. Final WT `git rev-parse HEAD;git status --short --branch;git diff --exit-code;git diff --check` exit0: pinnedSHA,onlyownuntrackedprobes,trackedsourceunchanged. Hashesreadback. No staging/commit/reset/checkout/push.

## Evidence and source bytes

Compact sanitized MAIN `docs/coordination/evidence/R03-02/`:

| File | SHA256 |
|---|---|
|probe-summary.json|56c935e9adad0b0f18fea1e1c3bc58f5c3cf70347fbe90a1c4e2243af1f1fe51|
|stdio-summary.json|b806c279b7986c5d0c151576472deb646801e2b77ec89a46fcf5aa25f9019671|
|sparse-public-summary.json|ac3c10577447ee04ed9fb1cf572046b53d3a3795515747cc6f85ad45217c9e28|
|focused-pytest.log|4a3f88dc0f3b41485839c6a45fee696912634e07bd929f45f7e67cc6be6bdd1d|
|plotly-browser-summary.json|actualHTMLhash recorded inside|

Large/localoutputs remain `C:/Users/bagma/AppData/Local/Temp/opencode/r03-02-security-artifacts/`; focused-junit.xmlSHA25630b51dee0bf26c31e89120a1c9e9fde9f2a3fd210da3a8752029999294029b9b. No generateddataset/build/image committed.

Actual imports under WT/python/deepviz/src/deepviz, asserted beforeprobes:

| Module | SHA256 |
|---|---|
|models.py|890ecb0e29e1345364b2bf4840bdea7a542067003caf54d7b0855536ee2b6a76|
|normalize.py|0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83|
|tools.py|ae2390e5616e2e455df6bfdb4471865bafa148eb2853ea5793d144f88a16e0cb|
|mcp_server.py|3d1e44d323a76d0e2adcf37a7d5951e7716f8883c792dc9046fabe7cdb655d95|
|engines.py|a4cabd2c0fdff2ec067e3090378460a0832b931946e26aa9e2cef682cd9d53f3|
|render.py|5d74fdb673a0fc923d49388a379d0ac3ac6b3998c465e120e3b51302a9bc1b56|

Loadeddependencies: MCP1.30.0,LangChainCore1.8.5,Pydantic2.14.4; existingvenvread-only. Ownnewprobes WT/tests/r03_probes/security-review; source/oraclesunchanged. All authorizednotes/evidence in MAIN, not onlyWT.

## Handoff / next executable action

R04route1+3toPythonrenderowner,2+4tointegrationowner. Add unchanged failing regressions then scopedfixes without weakenedtests/authority. Reproduce with pinnedPYTHONPATH and `python tests/r03_probes/security-review/probe_security.py FRESH_UNIQUE_TEMP_DIRECTORY`; probes refuseexistingdirectories. NativeHTML: run own probe_plotly_html.py then probe_plotly_html.cjs against afreshownoutputdirectory. Re-review actual integratedfinalSHA and rerun affectedtests/DOMchecks afterfixes. Symlinkprivilege/runtimecoverage remainsblocked; notpass. Nofinalapprovalissued.
