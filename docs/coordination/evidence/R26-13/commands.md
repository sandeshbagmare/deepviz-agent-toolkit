# R26-13 exact command entry points and results

No installs, source/config/original-test edits, broader candidate tests, branch
merges, browser runs, 10M runs or PR/default/closure/API mutations occurred.

## Pinning and source inventory

Safe expected-account GETs and timestamps are in `default-start.json`:
`GET /user`, repository metadata, `GET .../git/ref/heads/main`, and one
`GET .../pulls/33`. All200. Main0ae2, PR33unmerged998 at that snapshot; its
speculative merge ref was **not** treated as a real merge. No CI/job polling.

```powershell
git fetch --no-tags origin 0ae2cf26426822135fc10d337fcacf580b7ed833
git worktree add --detach C:/Users/bagma/AppData/Local/Temp/opencode/r26-13-main-0ae2-ses_de56780caffekQ9gdZ58EgQwb5 0ae2cf26426822135fc10d337fcacf580b7ed833
git rev-parse HEAD
git status --porcelain
git ls-tree -r --name-only 0ae2cf26426822135fc10d337fcacf580b7ed833
```

All exit0; detached actual0ae2, clean, exactly7trackedfiles. Full raw/GitLF
hashes and actual fetch/worktree output are in `default-consumer.json`.
No testfiles, committed schemaJSON, CI, renderer, npmworkspace or implemented
CLI/MCP ships at that source. Absences are baseline, not new bugs.

## One shipped collection and one NEW bounded probe

Actual full argv/cwd/exits/outer timings are `shipped-command.json` and
`probe-command.json`. Common entry point (the two mode/output pairs ran once):

```powershell
& 'C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe' -I -S `
  'C:/Users/bagma/AppData/Local/Temp/opencode/r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5/tests/r26_probes/role13/verify_default.py' `
  --source 'C:/Users/bagma/AppData/Local/Temp/opencode/r26-13-main-0ae2-ses_de56780caffekQ9gdZ58EgQwb5' `
  --sha 0ae2cf26426822135fc10d337fcacf580b7ed833 `
  --site-packages 'C:/Users/bagma/deepviz-agent-toolkit/.venv/Lib/site-packages' `
  --probe 'C:/Users/bagma/AppData/Local/Temp/opencode/r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5/tests/r26_probes/role13/test_default_contract.py' `
  --mode '<shipped or probe>' --output '<unique R26-13 evidence>/<shipped or probe>'
```

- External empty CWD:`C:/Users/bagma/AppData/Local/Temp/opencode/r26-13-cwd-ses_de56780caffekQ9gdZ58EgQwb5`.
- `shipped`: **exit5/0tests/0passed/0failed/0skipped**, pytest0.11s, outer3.2239127999928314s. NOTa passing suite.
- `probe`: **exit1/30tests/6failed/24passed/0errors/0skipped**, pytest0.90s, outer4.527751600006013s.24passes include3OWNprovenanceguards and21publiccontractcontrols. All6numericcoercionRED map to known#30.
- `-I -S` excludes editable hooks; child-only plugin-autoload suppression and no bytecode/cacheprovider. All7Git/rawsourcebytes+OWNrunner/probehashes+HEAD/origin checked in the same actual pytest process before/after. Namespace fallback portion is disclosed in receipts; the actually imported **models.py** is exact0ae2, not an installed candidate copy.
- FullJUnit, generated same-model schema, literal accepted/coerced/rejected wire observations and provenance are under `shipped/` and `probe/`; rawstdout/stderr logs retained. The collector's exit0 is not the producttestexit1.

## Actual configured main-model static checks

```powershell
& 'C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/ruff.exe' check --config '<actual 0ae2 source>/pyproject.toml' '<actual 0ae2 source>/python/deepviz/src/deepviz/models.py'
& 'C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/mypy.exe' --config-file '<actual 0ae2 source>/pyproject.toml' --cache-dir '<OWN R26-13 output>/mypy-cache' '<actual 0ae2 source>/python/deepviz/src/deepviz/models.py'
```

Both exit0 (0.0669437s /3.7604798s), mypy1sourcefile. Exact expanded argv/cwd,
elapsed and rawlog paths are in `static-checks.json`. Read-only installed tools:
`ruff --version`exit0=`0.17.6`; `mypy --version`exit0=`2.4.1`; actual testprocess
Python3.12.16/Pydantic2.14.4/pytest9.2.0. No fullcandidate/static-green claim.

## Deduplication and saved-result verification

One fresh complete post-test open-issue/title/body search plus all21relevant
commentlists:24GET/all200,35actualopenissues+2PRentries, exact#30bodyread.
`bug-dedup.json` records whitelisted bodies/comments/paths/times and the decision:
**reuse existing #30**, no new issue/comment necessary for the same6coercions.
0API mutations in R26. #37belongs to prior5e/candidateQA, not this default pass.

`python -` saved-result integrity exit0 verified realJUnit/30cases/6strictfails,
3guardcases, observations, both before/after hashmaps/current bytes, clean0ae2,
generatedschemaequality, static exits and known#30dedup. `summary.json` is the
compact result. These integrity assertions are not additional product tests.

## Own-probe hygiene and no-replay boundary

`ruff check --no-cache tests/r26_probes/role13/verify_default.py tests/r26_probes/role13/test_default_contract.py`
initially exit1/2I001import-order findings, ONLYnewOWNfiles. Exactexecuted
bytes were saved in `executed-sources/*.py.txt` and verified against both
originalreceipts. Current files changed ONLY top-levelimportordering;
`own-import-order.json` proves equal importmultisets/every nonimport AST node.
The same Ruff command then exit0. **No unchanged0ae2 producttest rerun.**
Runtimeclaims remain about exactarchivedbytes; current reorderedbytes have
lint/static-equivalence proof, not a falsely asserted new runtime run.

Finalsaved-artifact integrity `python -` exit0 validates12existingJSONs,
2XMLs, archivedexecuted/currentformattedhash distinctions, all7sourcebytes,
clean0ae2/protectedsource-config-workflowdiff0/credentialpatterns0. Disposable
ownmypycache was preserved outside the publication at
`C:/Users/bagma/AppData/Local/Temp/opencode/r26-13-mypy-cache-ses_de56780caffekQ9gdZ58EgQwb5`;
not deleted or committed. `prepublication-integrity.json` records the exact
28evidencefiles(atthatcheckpointincludingitself)/manifest hashes. Later
documentation-only checkpoint edits are staged/reviewed separately.

**Next:** manager/root supplies actual merge/default SHA notification. Freeze
newmain, verify ancestry/exactsource/imports and run all actually shipped
first-slice tests plus retained literal/schema smoke. No polling, unmerged998
approval, repeated0ae2 tests or newly invented bug to fill time.
