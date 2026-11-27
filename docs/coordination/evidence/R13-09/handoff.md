# R13-09 immutable RED handoff and future retest

The recovered own branch `agents/r10-09-helper-null-fix` really published **ee30c8a600ab1610477341894922ade6e5bad7f6**: non-forcepush0, savedimmediatereadback0 and one recoveryreadback0/exactmatch. No product suite repeated. Original strict test commit **4a585cd2ab683421a19c217d3373478b88e49379**, regression SHA256 **08be1d15661d6bd5bf87bdcec7db11ba3097d9eee294db654369564716e32227**, is immutable.

**Still RED/unfixed:** fivehelperexplicitnulls renderdefaults againstrejectingschema/directvalidator. New36tests31pass5RED; fullnpm277pass5RED; coreparity689passes are retainedexecutedR10evidence, notnewR13results. Allpositivecontrols preserveomitted/undefined/emptyvalidspec, mappedvalues, dashboardchildtitles/defaults andotherinvalidrejections. Proposed source-owner fix is ONLY `input.spec === undefined ? {} : input.spec` instead of`input.spec??{}`, no schemaweakening.

Higher-priority tester prohibition forbids thissession editingproduction. Root explicitly respects it. **R04 owns the decision and must record an eligible-producer transfer before anyone else edits `render.ts`.** This packet is notselfapproval, producerGREEN, issueclosure ormergepermission.

## Future eligible-producer commit: executable retest

Use the NEW own recipe `tests/r13_probes/role09/retest-helper-null.ps1` from thisbranch against a DIFFERENT cleanisolatedworktree containingtheeligibleproducer's exactcommit AND theimmutable regression. Do not checkout/resetthisbaseline oroverwritesiblingwork. Substitute realfullSHA and newuniqueevidencepath, use existingreadonlytooling:

```powershell
$recipe='C:\path\to\this-branch\tests\r13_probes\role09\retest-helper-null.ps1'
$parameters=@{
  Candidate='C:\path\to\clean-eligible-producer-worktree'
  ExpectedSha='<actual-full-40-character-producer-SHA>'
  EvidenceDirectory='C:\Users\bagma\AppData\Local\Temp\opencode\<unique-new-retest-evidence>'
  Python='C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe'
  ToolsBin='C:\Users\bagma\deepviz-agent-toolkit\node_modules\.bin'
}
& $recipe @parameters        # validates source/test/schema identity; prints NOT_RUN plan only
& $recipe @parameters -Run   # after inspecting plan and R04's actual producer release
```

The run refuses recordedunfixedrenderbytes and anexistingevidencedirectory, records exact exits/logs/source+buildhashes/publicexportorigin, failfastpreservesremainingNOT_RUN. Requiredactualsuccess: all36immutabletests, fullnpm, build/type/schema/coreparityandpackdryrun exit0; no nullacceptance/schemaweakening/default-value regression. Then separately rerun original40casewrapperprobe fromR10report: expect40agree/0mismatch. FullPython/distributionconsumers/visuals/MCP/DeepAgent/10M/finalCIandtwoindependentreviewer+twotester acceptance are separate, NOT satisfiedbythisrecipe. Packdryrun is not aninstalledpackagebuild/consumerpass.

On ee30c8a the NEW recipepreflight was actually validated: plan0/9gatesNOT_RUN; knownunfixed-Run1expected; wrongSHA1expected; combined3controlsPASS/0productsuitesrun. ExecutionbranchincludingfuturecandidateproductgatesremainsUNRUN. Sourcefix/CI/900remainunmet; see ownR13report/preflight-summary.json for exactlimits and owner.
