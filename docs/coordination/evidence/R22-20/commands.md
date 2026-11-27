# R22-20 exact commands / outcomes / limitations

Owner/session `ses_de567801cffeGZFlt50oYv0Dnt`; existingOWNbranch `agents/r10-20-plotly-literal-labels` started clean/tracking at **ffea4d74ece9a02864eae404eb0596d660172ba9**. Native session_move SAMEID. MAINR22 common+20 and latestAGENTStopline permit exactly one genuine deduplicatedF20bugCREATEorCOMMENT; no source/PR/closure/defaultauthority. Preworkreport/ownMAINnote saved. ReadactualR03/R10/R13reports+unchangedprobes; R13namefoundbyglob, notassumed. No spawning.

## Initial read-only identity and source checks (exit0)

```powershell
git status --short --branch
git rev-parse HEAD
git log -3 --oneline
git remote get-url origin
git diff --exit-code ffea4d74ece9a02864eae404eb0596d660172ba9 -- python\deepviz\src packages\deepviz\src schemas tests\r10_probes\role20 tests\r13_probes\role20 tests\r16_probes\role20
git show --stat --oneline c1bf91c5439d585e2ff157752f380cfa4fe85c6d
git show --stat --oneline f9087d0518e74378e810b9efe6d6630a12044399
```

Source/probes unchanged. TestedPlotlysource3aa, R10c1bfstrict2fail4pass0skip and R13f908strict3fail0skip, 0console; **not rerun here**. R16SUM18passdoesnotfixPlotly. A guessed related02report read returnednotfound; glob/grepactual`R03-02-security-review.md`section3confirms samecategory/seriesanchorcause, no duplicateissue.

## Safe discovery and before-write dedup

```powershell
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe docs\coordination\evidence\R22-20\github_discovery.py
```

**Exit0,2026-11-27T15:00:43UTC**. CapturedGCMsubprocessargs`['git','-c','credential.interactive=false','credential','fill']`, stdin`protocol=https\nhost=github.com\n\n`,20stimeout; tokenonlyinmemory. OriginexactauthorizedHTTPSrepository; APIrequestsONLY`https://api.github.com`relativeallowlistedpaths, redirectsdisabled/60stimeout/sanitizederrors. GET/user200expected`sandeshbagmare`,repo200exactpublic/defaultmain/issuesenabled/notarchived,completeopenpagination1page31items=30issues+1PRexcluded; explicit#10/#21/#23all200/comments0. SixGET/noPOST. `discovery.json`whitelistpublicfields/statuses/body; noheaders/token/helperoutput/signedURLs.

All30openissuebodies/titlesandrequiredstoriesread; no specificF20Plotlybug. #10/#21/#23arebroadfeature/security/visualstories, #30schema-coercionunrelated; saveCREATEONEdecisionbeforePOST in`dedup-decision.json`. Relatedrole02samebugnotnewticket.

## Own new helpers lint/type/audit and honest intermediate failures

```powershell
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m ruff check docs\coordination\evidence\R22-20\github_discovery.py docs\coordination\evidence\R22-20\audit_evidence.py docs\coordination\evidence\R22-20\create_bug_once.py
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m mypy --follow-imports=silent --ignore-missing-imports docs\coordination\evidence\R22-20\github_discovery.py docs\coordination\evidence\R22-20\audit_evidence.py docs\coordination\evidence\R22-20\create_bug_once.py
```

FirstRuff0/mypy1twoOWNemptylistannotations(issues/prsline84), notproductfailure. Addexplicit`list[dict]`annotationsonly. NextsamethreefileRuff0/mypy0; `python ...\audit_evidence.py`exit0,13localimmutableGitpermalinks/5PNGhashmatches/recordedXML2fail4pass+3fail/0skip/9browsercases0errors, unchangedsource/oracles. Readbackauditnotnewproducttest; bodyhashmustmatchbeforePOST.

## Conservative stop, full comment classification (no mutation retry)

First`python docs\coordination\evidence\R22-20\create_bug_once.py`**exit1 BEFORE POST**: freshidentity/repo/openissues/requiredstories/comments10GETsall200. DetectorflaggedtwoNEWbroadtriagecomments(#27/#20)thatmentionPlotly, saved`publication-blocker.json`/`new-specific-match-blocker.json`. **No POST was attempted; no attempt marker**, no HTTP403/429 or transport error. Stopped to read, not an API mutation retry.

```powershell
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe docs\coordination\evidence\R22-20\inspect_match_comments.py
```

Exit0/twoGET200; whitelist`match-comment-readback.json`. FirstpublicbodyconsoleprintCP1252UnicodeEncodeError(exit1), thenASCII-escapedline-by-lineFULLbodyreadexit0. BothcommentsareCI/processplanning, explicitly“thiscommentcreatesneither”andretainQA20exclusivefiling; neitherisactualF20bugreport. ExactreviewedbodySHAhashesd787ebdf.../#27andd9c03d72.../#20savedindecision; ONLYthosecontentversionsnonduplicate, allnew/editedmatchescauseSTOP. ThisisexplicitdedupclassificationunderalreadyR22authority, notnewmanagerapproval/accountchange/HTTPPOSTretry. Productoraclesnotchanged.

NextRuff1singleOWNnewcommentreaderimportorderI001; chainedcommandstoppedbeforemypy/audit/API. Sortedimportsonly, notproductfinding/noPOST.

## Final scoped checks + sole first POST / actual issue readback

```powershell
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m ruff check docs\coordination\evidence\R22-20
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m mypy --follow-imports=silent --ignore-missing-imports docs\coordination\evidence\R22-20\github_discovery.py docs\coordination\evidence\R22-20\audit_evidence.py docs\coordination\evidence\R22-20\create_bug_once.py docs\coordination\evidence\R22-20\inspect_match_comments.py
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe docs\coordination\evidence\R22-20\audit_evidence.py
& C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe docs\coordination\evidence\R22-20\create_bug_once.py
```

**All exit0**, Ruffallpassed/mypy4filesnoissues/audit13Gitlinks5PNGmatches/no productrerun. Freshexpectedidentity/repo/completeopenissues/requiredparents/allcommentpagesGET200. Exactreviewednonbugcommenthashesmatch; no otherF20specificmatch. Persistent`post-attempt.json`createdBEFOREsolePOST, rejectsallfutureinvocations(no morewritepermission).

**ONE POST `/repos/sandeshbagmare/deepviz-agent-toolkit/issues`201 → actual#36**, GET`/issues/36`200 exactnumberURL/body/title/openstateverifiedat**2026-11-27T15:29:31UTC**. https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/36 . BodySHA256`e92b28d940ee7fb2e6cf936e0a977bfa95c40aa1d115afa8570a4312a0a4c971`. `issue-receipt.json`statuses/whitelistactualfields; `post-response.json`publicissuebodyonly. Creates1/comments0/closuresPRsourcewrites0. No retries/alternateidentity/authchange/privateheaders/rawcredentiallogs/signedURLs. Rule403/429/transportambiguitySTOPremainsimplemented; noneoccurred.

## Limits / next action / publication

No production/source/oracle edits or browser/build/count/SUM/fullsuite/format/scale/MCP/DeepAgent/replay. NewQAworkisrealonebug+traceability, notnewtestpass/Plotlyfix/greenCI/finalsignoff/900claim. OriginalstrictREDsource3aa+probecommitsc1bf/f908+5actualPNG/DOMevidencepermalinksremainimmutable. Nativeanchors/markupinterpretationconfirmed, NOclick/JSexecution/exploitationclaim. R04owns`_plotly`, eligible08`_antv`outofscope; unchangedninecaseindependentfrozen-fixedsourceacceptance/focusedgatesstillneededbeforeclosure.

Pending scopedOWNR22report/evidence/noteexplicitstage/whitespace/credential/bodyhashreceiptcheck, meaningfulOWNcommit/nonforcepush/exactremoteSHAreadback. Sourcefix/pr/default/closureauthoritynotgranted; neverreruncreationhelper.
