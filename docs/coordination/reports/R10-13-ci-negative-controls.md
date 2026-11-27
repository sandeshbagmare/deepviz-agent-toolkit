# R10-13 — independent CI negative controls

Status: SCOPED CONTROLS VERIFIED / WHOLE SUITE RED / OWN BRANCH PUBLISHED, 2026-11-27. Not final CI approval.

**Recovery pointer:** SAME-ID R13 resumed existing clean dedb41f branch after upstream interruption; no control/full-suite replay or branch recreation. Nonforce OWNpush0 and remoteSHAreadback0 confirm `2e2b6391b8bf8fb9bd6d6e2e481e56686381022f` including dedb41f on `agents/r10-13-ci-negative-controls`. Publication and exact36-case gate-repair handoff are tracked in [`R13-13-ci-gate-repair-handoff.md`](R13-13-ci-gate-repair-handoff.md). R13 authenticated snapshot verifies5340PR31draft/unmerged and Verification45928608970FAIL; evidence-policy success is not approval. Original R10 results below remain unchanged.

## Outcome / decision for R04

Fifteen NEW independent CLI controls verify13intentional child rejections and5positive command outcomes on unchanged checkpoint `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`. With16existingCIcontrols,31tests pass. **Full ordinary Python suite remains RED:36failed/3019passed/5skipped630.59s.** No production workflow/configuration, existing oracle, source schema, dependency or historical evidence was edited; no lint waiver was added.

New executable recipe/tests: `tests/r10_probes/role13/{README.md,test_gate_negative_controls.py}`. Small tested commit **`dedb41fa8df3fdb90b845eef7a10b5fa4032872c`** changes only those2files. Report/note/sanitized evidence publication follows on OWN branch only; no local commit is called a push. R04 alone may integrate/modify production gates or issues/PRs.

Acceptance/dependency: contributes to existing open[#20](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/20) (real CI gates); not issue closure or proof that required evidence is enforced for every PR. The real `evidence-required` label is still opt-in; absent-label bootstrap returns0with an explicit nonapproval warning. The controls lock that distinction rather than claiming bootstrapgreen=independentapproval. Positive format fixtures use`.invalid`URLs and synthetic role IDs; not real reviews/images/signoffs.

## Authority / identity / scope

- Actual SAME-ID owner: `ses_de56780caffekQ9gdZ58EgQwb5`, native session-move confirmed at MAIN on continuation.
- Read full `tasks/R10-rolling-agile-sdlc.md` common contract and role13, current MAIN checkpoint/RESUME/STATE, own note and R03-13 baseline report. POC means point of contact; full production/900 genuine issue scope remains. No spawning; root/R04 retain dispatch/integration authority.
- Required current-source base: `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`; MAIN observed at that SHA on `release/candidate`, dirty coordination and preserved evidence only, tracking at same SHA. Prior isolated `0c5fa82` worktree/report/evidence remain untouched.
- Planned branch: `agents/r10-13-ci-negative-controls`; planned isolated worktree `C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5`.
- Allowed new writes: this report, own actual-ID note, `docs/coordination/evidence/R10-13/` compact sanitized evidence, own new `tests/r10_probes/role13/`. Own isolated branch publication only; no production workflow/config/dependency/existing-oracle or historical-evidence changes, installs, issue/PR writes, shared branch staging/push or credential/config mutation.
- Laptop GitHub workflow loaded. `git config --get-all credential.helper` exit0=`manager`; identity verification via captured in-memory GCM and authenticated GET is pending before branch/publication writes. No secrets will be logged or stored.

## Short implementation / acceptance plan

1. Verify exact base object, own branch/path absence, HTTPS target, authenticated GET `/user` expected `sandeshbagmare`; observe relevant issue/PR read-only, not a new issue census.
2. Create one isolated branch at exact base. Add NEW pytest subprocess controls plus a portable recipe under `tests/r10_probes/role13/`: clean/stale/missing schema checks using scratch destinations only; strict required evidence versus complete positive/bootstrap/unsafe/untrusted packet controls; actual passing/failing pytest CLI exit propagation with no production test edits.
3. Execute controls, retain exact child RED exits and positive checks separately. Review current clean full-root lint versus unchanged seven N15 archival findings; no broad lint waiver. Run own lint/types and CI gate tests with installed tools only. State full-suite/remote/OS limits explicitly.
4. Save compact argv/exits/totals/hash/source evidence. Copy only owned note/report/evidence to own isolated branch, review explicit paths + staged diff/whitespace/credential scan, small commit, non-force own-branch push, read back remote SHA, save receipt in own MAIN report/note. R04 alone integrates; no self-approval.

## Agile mapping / acceptance / limits

- Existing issue mapping pending safe GET: CI quality gate issue #20 and schema issue #30; no new issue manufactured or closed.
- Acceptance: negative commands return nonzero for the intended rejection (not setup errors); clean controls return0; strict evidence cannot be mistaken for bootstrap approval; failing test propagates exit1. Any structural-evidence validator weakness is reported rather than hidden/changed out of scope.
- Product code is not being implemented or fixed. New controls test unchanged real CLI entry points; scratch fixture files and pytest children are uniquely owned, no mutation of existing schemas/tests/evidence.
- Commands so far: native session-move success; MAIN `git status --short --branch`, `git rev-parse HEAD`, `git worktree list --porcelain`, credential-helper lookup each exit0. No new controls/authenticated GET/commits/pushes yet.
- Current action: authenticated identity/source/branch preflight, then implement bounded new independent controls.
- Blocker: none observed; only installed tools allowed, no Linux or green remote CI implied.
- Next executable action: captured in-memory GCM credential → authenticated GET `/user`, validate expected login, and verify base/own branch absence before worktree creation.

## Checkpoint 1 — authenticated preflight / task design

- Authenticated GET `/user` HTTP200 confirmed expected `sandeshbagmare`; GCM secret remained captured/in memory only. `preflight.json` contains sanitized results, no headers/credential output. Open #20 is the precise CI-gate work item; #30 is coercion/parity (related schema context, not a claim this work resolves it). PR31 observed open/draft/unmerged at `ca25af486bf443949125df789f5b5fd1fda8bba8`;12checks include in-progress/queued Python/scale and successes. This bounded snapshot is not green CI or a new census.
- Exact base exists; own local branch absent (show-ref1), own remote query0/absent, unique worktree path absent, configured author present. `git worktree add -b agents/r10-13-ci-negative-controls <own path> 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab` exit0; native session move returned SAME-ID. No shared branch checkout/staging.
- Read actual schema/evidence CLIs and existing tests. **Ruling:** no production implementation/fix is authorized; add only independent subprocess controls and recipe. RED here means deliberate child gate/test rejection observed with return1, not an invented missing-feature failure or source RED→GREEN claim. Existing direct generic stale/missing-report tests are not duplicated: new cases exercise valid-but-stale nested schema, insecure URL schemes, exact label-versus-body distinction, inert command text, and real pytest/JUnit failure propagation.
- Portable new files: `tests/r10_probes/role13/test_gate_negative_controls.py` (real CLI boundary controls and child trace), `tests/r10_probes/role13/README.md` (one-command reproduction, strict versus bootstrap and limits). Test fixtures are explicitly synthetic and use `.invalid` URLs; they are never real review/test signoffs or linked evidence for merge.
- Existing source/oracles/config/evidence unchanged. Next executable action: write/run new subprocess controls, save child returncodes and genuine positive/rejection outputs under own ignored artifact directory, then run lint/CI controls.

## Checkpoint 2 — first independent controls run, harness defect preserved

- NEW controls command: MAIN `.venv/Scripts/python.exe -m pytest tests/r10_probes/role13 -q --strict-markers --basetemp <own-temp>/cases --junitxml <own-temp>/controls.xml`; explicit pinned PYTHONPATH and `R10_13_COMMAND_TRACE`. Exit1: **1 failed /14 passed /0 skipped,4.38s**. Raw log/XML/child trace preserved at `C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-evidence-ses_de56780caffekQ9gdZ58EgQwb5`.
- The sole failure is **own probe setup**, not a gate/product defect: test assumed schema root `properties`, but actual recursive pinned schema is `$ref`/`$defs.ChartSpec` (read real schema). It failed with KeyError before stale mutation or rejection command. Existing14 controls already exercised the real evidence/pytest boundaries. No invented stale-schema RED pass.
- Own new-probe Ruff exit0, mypy exit0(1file). Next executable action: correct ONLY the new scratch-fixture traversal to actual `$defs.ChartSpec.properties.max_points`, rerun controls to a fresh run2 output/trace path, preserve run1 evidence and all production bytes.

## Checkpoint 3 — actual controls GREEN / whole source suite RED

- Corrected only new fixture traversal. Same own-controls command plus `.github/tests`, fresh run2 artifacts: exit0, **31passed/0failed/0skipped3.74s** =15NEWcontrols+16existingCIcontrols. Child trace has18realcommands:13intendedrejections exit1,5positivecontrols exit0, no setup/collection errors. `evidence/R10-13/controls-summary.json` preserves sanitized exact argv/cwd/stdout/stderr, source hashes and raw-artifact hashes.
- Installed MAIN TypeScript tool PATH, isolated `npm run build` exit0 before Python parity; no install/node_modules copy/link. Full ordinary `python -m pytest -ra --junitxml <own-temp>/full-suite/full.xml` ran in background once, never polled, completion notification received. **Exit1:36failed/3019passed/5skipped630.59s**,3060total, all15NEWcontrols pass. This is current3aa source plus new tests, NOTgreenCI. Source files/existing oracles unchanged.
- Full failures:20ECharts numeric-x line/area acceptance cases;10Vega-dashboard acceptance cases;4historical64KiB-field resource cases;`python/deepviz/tests/test_backend_antv.py::test_dashboard_duplicate_titles_get_unique_containers_and_independent_options`;`python/deepviz/tests/test_n17_boundaries.py::test_n17_dashboard_serialization_order_observation`. All names/messages/skips in `evidence/R10-13/full-suite-index.json`; its IDs are module-path::function labels (append`.py` to module path for a pytest file node). Raw full log/XML/command remain under owned temp `.../full-suite/`, hashes in index. No failure hidden or fixed out of scope.
- Exact clean checkpoint+newprobes full-root Ruff0; package+newprobe mypy0(10files); schema--check0; existingActionlint0. MAIN current source concurrently advanced to5340bc6; MAIN full-root Ruff1 and directN15Ruff1 produce identical seven findings. Original N15 byte hashes still match baseline. No Ruff waiver/config/exclusion was applied. `quality-summary.json` preserves commands/results/hashes.
- Current action: staged only two NEW probe/recipe files; inspect staged diff/whitespace/secret scan, scoped commit, then sanitize/publish owned report/note/evidence and verify remote receipt. No source/sharedGit/issuePRwrites/spawning.
- Next executable action: review `git diff --cached`, scan only those owned staged files and `git diff --cached --check`, then small own-branch commit with honest full-suite RED disclosure.

## Exact executed acceptance evidence

All new-check commands use the already-installed MAIN `.venv/Scripts/python.exe` read-only with `PYTHONPATH=<own-checkout>/python/deepviz/src`, `PYTHONDONTWRITEBYTECODE=1`. Optional trace is operator-owned `R10_13_COMMAND_TRACE`; child commands execute Python argv without a shell. Command records replace local paths with`<checkout>`,`<owned-temp>`,`<project-python>` where applicable; the recipe supplies executable expansion. No auth environment/header/credential output is captured.

| Command / real boundary | Observed result |
| --- | --- |
| `python -m pytest tests/r10_probes/role13 .github/tests -q --strict-markers --basetemp <owned-temp>/run2/cases --junitxml <owned-temp>/run2/controls.xml` |0;31passed,0failed,0skipped,3.74s;15NEW+16existing. |
| Real `scripts/export_schema.py --output <case>/scratch-schema.json`, then same`--check` |0/0; actual exporter and check succeed before corruption. |
| Same schema`--check` after scratch `$defs.ChartSpec.properties.max_points.maximum=100001` |1; validJSON drift rejected, scratch bytes unchanged. Existing canonical schema untouched. |
| Real `python -I scripts/verify_evidence.py <case>/synthetic-event.json` |11intended packet-rejection exits1:4nonHTTPSimage schemes,5nonHTTPS/markup report links,1missing requiredpacket,1inert commandtext+invalidimage. No stderr/setup error, no filecreated by bodytext. |
| Same evidence CLI: absent-label body containing labeltext; complete synthetic-format packet |0/0; bootstrap explicitly asserts no evidenceapproval; formatpositive explicitly says truth/independence notverified/noapproval. |
| Real child`python -m pytest -q --strict-markers --confcutdir <case> <positive> --junitxml <case>/positive.xml` |0;1actual pass. |
| Same childpytest with positive+deliberateassertionfailure |1;1failed+1passed; JUnit exactly1failure/0errors. Outercontrol must observe this RED exit, not swallow it. |
| `python -m pytest -ra --junitxml <owned-temp>/full-suite/full.xml` |1;36failed/3019passed/5skipped,630.59s,3060total. All15NEWcontrols pass; full fail/skip index retained. |
| `python -m ruff check . .github/tests` in isolated checkpoint+newprobes |0; full-root clean, no exclude/ignore flag. |
| `python -m mypy python/deepviz/src/deepviz tests/r10_probes/role13/test_gate_negative_controls.py` |0;10files. |
| `python scripts/export_schema.py --check`; installedActionlint1.7.12 on bothworkflows |0/0. |
| `npm run build` with processPATH=MAINinstalled`node_modules/.bin`+PATH |0; prerequisite for actual Python/TS parity; no npm install/copy/link, no lockfile change. |
| MAIN full-root Ruff; direct preservedN15twofiles Ruff |1/1; byte-identical sevenfindings; original N15 hashes match0c5baseline. MAIN observed5340bc6is moving, not silently relabeled3aa. |
| Explicit2path`git add`; stageddiffreview; credential-pattern scan;`git diff --cached --check`;`git commit -m "test: add independent CI gate rejection controls"` |each0; only two NEW scoped probe files,0credentialpatternhits; committeddedb41f. |

Evidence: [`controls-summary.json`](../evidence/R10-13/controls-summary.json) has18childargv/exits/outputs plus all31case identities; [`full-suite-index.json`](../evidence/R10-13/full-suite-index.json) has all36failure labels/messages and5skip reasons; [`quality-summary.json`](../evidence/R10-13/quality-summary.json) has exact lint/type/schema/Actionlintcommands/N15hashes; [`provenance.json`](../evidence/R10-13/provenance.json) pinsactualown`deepviz`/`deepviz.models`modulehashes and source/config/oracle diff0; [`preflight.json`](../evidence/R10-13/preflight.json) is the bounded authenticateduser/issue/PR/checksnapshot. Rawfirst-failed and corrected/full logs/XML/childtrace are unique local artifacts under `C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-evidence-ses_de56780caffekQ9gdZ58EgQwb5`; raw byteSHA256/lengths in compact evidence. No raw datasets/dependencytrees/caches published.

### Limits / review / next action

-5full-suite skips are2WindowsWinError1314symlinkprivilege skips and3opt-in installedChromium/CDN native suites (plotly/echarts/antv). Not pass/visualcoverage. Current task did not independently inspect chart output, executeLinux/Node24, buildPython distributions or observe completedgreenremoteCI. R03`0c5`results stay historical, not upgraded by this run.
- Sourcecheck: `git diff --exit-code 3aa521a5 -- scripts .github pyproject.toml schemas packages python/deepviz/src python/deepviz/tests`=0; no production/oracle edits. No unsafe bodytext is executed; testmarker strings are inert JSON fixture data. Gate rejects tested bad link formats but does not verify arbitraryHTTPScontent safety/truth/revieweridentity; that remains human/independent-agent evidence review.
- Author self-review only: actualCLIs/callers read, stagedfullcode+recipe reviewed, scopes/whitespace/secretpatterns checked. **No non-author review claimed**; explicit no-spawn means root/R04 must route genuine independent review/testing before integration/finalmerge. No issue/PRwrites or fabricated900contributions.
- Next executable action: copy ONLY owned report/note/compactR10-13evidence into ownbranch, inspect+scan explicitstagedpaths, commitcheckpoint; authenticatedexpecteduser verification, nonforceOWNpush and actualremoteSHAreadback; save MAINreceipt. R04 then decides integration and remaining36failure dispositions; keep PRdraft/finalgates unmet.
