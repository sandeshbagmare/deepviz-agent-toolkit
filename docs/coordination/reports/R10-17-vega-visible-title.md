# R10-17 — portable strict Vega dashboard regressions

## Result and source identity

**New portable checks: 40 passed on checkpoint source; 40 passed on old baseline source. Original matrix: 10 failures remain unchanged.** No renderer/theme/source/existing-test fixes were made. Actual composed native Vega-Lite SVG/PNG and browser images preserve the visible literal parent and each correct child title. This is source-specific evidence, **not final-candidate signoff**.

- Owner SAME-ID `ses_de5678086ffeNido4phnXCJ8J4`; branch `agents/r10-17-vega-visible-title`, based on assigned checkpoint **`3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`**, not a final freeze. Existing WT `C:/Users/bagma/AppData/Local/Temp/opencode/r10-17-vega-visible-title-ses_de5678086ffeNido4phnXCJ8J4` (WT below).
- Immutable baseline WT/source **`0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43`** and historical R03 outputs are preserved. R03's different 18 probes + 12 backend tests = **30**, not these new 28 + 12 = **40**. Source/loaded-module paths/hashes: [source-comparison.json](../evidence/R10-17/source-comparison.json).
- Read R10 common+17, canonical/RESUME/STATE, own baseline/note, laptop-github-workflow; R13 common+17 recovery reused this branch and resumed publication only. No completed tests/browser/builds were repeated for recovery; previous collector completed exit0, with no command in flight. [R13 recovery report](R13-17-vega-publication.md).
- Allowed publication paths: own NEW `tests/r10_probes/role17/`, this report, own actual-ID note, compact `evidence/R10-17/`, own R13 recovery report/evidence. No installs/shared-env changes, source/existing matrix edits, others' notes, shared-branch operations, spawning or issue/PR writes. R04 alone integrates/issues/PRs. Rolling18–22/POC=pointofcontact/fullproduction/900legitimate-created-and-resolved remain in force.

## Acceptance and correctness rationale

`tests/r10_probes/role17/` is self-contained: embedded three-row fixtures, public renderer, installed real `vl_convert`, and no MAIN paths or imports from the existing matrix. It captures the real composed compilation call (wraps, not fake compiler), inspects actual SVG and independently compiles native children.

- Require exact literal SVG `<text>` for the parent **and both correct children** in the full export. Pair `manifest["native_specs"]` with `manifest["charts"]` using equal lengths/strict zip; each standalone native child must retain **its own** title, never the parent's title.
- Five source forms × light/dark: records, columns, nested JSON, GraphQL edges/nodes, CSV. Require exact source/native/SVG values, three bars/three points, quantitative x=0/1/10 and y=2/8/4, six dashboard contributions from three inputs.
- Real point positions are **[0,180], [21,0], [210,120]** in native child coordinates; bars have correct 2/8/4 heights and zero baseline. Wrong native values or drawn geometry fail even when metadata is intact.
- Metadata `<title>/<desc>/comment` cannot replace any parent/child text; hidden-parent display/visibility/opacity controls fail. Missing visible text, parent-substituted child titles, injected script/foreignObject/style, event attributes and external hrefs are rejected. Distinct malicious field/category/child strings remain literal inert text.
- The XML guard rejects tested common hidden sinks, not every CSS/paint trick; actual PNG/browser inspection complements it. No universal chart/theme/scale claim.

**Unchanged original oracle diagnosis:** original matrix first validates the full composed SVG's parent title, then recursively discovers/recompiles standalone manifest children while expecting the **parent** title on each. Those child SVGs correctly contain their own titles. Keep the full visible-parent/security/value/geometry checks; scope standalone title assertions to the correct child. Do not change renderer titles, drop parent checks or accept metadata-only title substitutes. This proposal is **not implemented** in any existing test.

## Exact executed checks

MAIN existing `.venv/Scripts/python.exe` (Python3.12.16), process-only `PYTHONPATH=<selected source>/python/deepviz/src`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`; CWD=WT. No installs. Installed vl-convert-python1.9.0.post1 (module reports1.9.0), pytest9.2.0, Ruff0.17.6. Exact counts/commands/raw-JUnit hashes: [runs.json](../evidence/R10-17/runs.json).

| Executed command | Actual result |
| --- | --- |
| `python -m pytest python/deepviz/tests/test_backend_vega.py tests/r10_probes/role17 -q --tb=short --junitxml=artifacts/local/R10-17/checks/current-final.xml` with checkpoint PYTHONPATH | **40passed/0failed/0skip17.59s**, exit0. 28new + 12unmodifiedbackend. [Console log](../evidence/R10-17/current-final.log). |
| Same command, `--junitxml=artifacts/local/R10-17/checks/baseline-portable.xml`, with oldpin PYTHONPATH | **40passed/0failed/0skip32.65s**, exit0. Same NEW harness, explicitly old source, not historicalR03's30. [Log](../evidence/R10-17/baseline-portable.log). |
| `python -m pytest tests/test_acceptance_matrix.py -q -k 'vega-dashboard' --tb=short --junitxml=artifacts/local/R10-17/original/matrix.xml` | **10failed/1139deselected/0skip6.22s**, exit1; unchanged wrong recursive-title oracle. All ten names/hash in runs.json; raw failure log/XML stays local. |
| `python -m ruff check tests/r10_probes/role17`; `python -m mypy` with checkpoint source | Both exit0; mypy9sourcefiles. No repository-wide lint or probe-typecheck claim. |
| `python tests/r10_probes/role17/vega_contract.py --output artifacts/local/R10-17/current-smoke-v2` | Exit0; actual checkpoint modules, nativeSVG/realPNG/relative artifact paths/hash summary. Same CLI with oldpin PYTHONPATH and `baseline-smoke-v1` exit0. Both source-specific SVG/PNG bytes identical for this fixture. |
| Process-only `NODE_PATH=C:/Users/bagma/deepviz-agent-toolkit/node_modules`; `node tests/r10_probes/role17/browser.cjs artifacts/local/R10-17/current-smoke-v2` | Exit0; **4HTTP200navigations/4pass**, **0consoleerrors/warnings/pageerrors/failedrequests/externalrequests**. Playwright1.65.1/Node26.13.1/Edge158.0.4370.45; no CDN/fallback. |

Timing limitation: raw JUnit suite attributes for the two40case runs both advertise17.425s, while console totals are17.59/32.65s. Both are recorded separately; cause is unestablished and **no performance comparison** is claimed. No retest was run to conceal the mismatch.

### Real image/security evidence

Opened/visually inspected current composedPNG and both original ordinary/strict wrapper screenshots: full escaped parent and correct child titles, bars2/8/4, irregular quantitative scatter spacing, and strict field/category attack text. Actual SVG is compiled Vega-Lite, **not fallback**. Direct SVG pages have positive text bounds/visible styles and mark counts; wrapper images load native640×400SVG. All markers undefined; zero executable/foreign nodes, event attributes or anchors. [Browser results](../evidence/R10-17/browser-results.json).

Small published native artifacts: [composed.svg](../evidence/R10-17/composed.svg) (**17622B**, SHA256`27b44161189e1577179e49b463087802ca1607d2bbe660f5522b49382a1286e7`) and [composed.png](../evidence/R10-17/composed.png) (**73884B**, `012e315522075e130d0a379f6cf99ed15462f58aff1099441f6762ddd9db1d56`). Larger local wrapper screenshots/payload/rawJUnit remain WT/artifacts/local/R10-17/, indexed in [artifact-index.json](../evidence/R10-17/artifact-index.json). Direct-SVG screenshots were **not attempted**; original-wrapper paint and converterPNG were inspected. Harness-only favicon204 is disclosed.

### Preserved unsuccessful own-harness checks

First own visibility guard falsely treated ancestor fill=none as hiding explicitly filled text: **12failed/27passed/0skip9.61s**, exit1. Ancestor-chain diagnosis exit0 proved paint inheritance; only own new guard corrected. Then39passed20.48s. Initial ownRuff1importgroup issue corrected. First CLI exit1 after generatingSVGPNG due relative-vs-absolute output paths; only ownCLI corrected and an unrelated-CWD/relative-output regression added. Final40 includes that positive control. Failed raw outputs remain local; these are not product defects, green gates or deleted failures.

## Agile mapping, publication and current next action

Authenticated GET02:25:50UTC confirmed expected `sandeshbagmare`, exact publicrepo/pushpermission and real OPEN [issue23](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/23), **Inspect real renderer outputs and commit reproducible visual evidence**. This harness contributes strict Vega acceptance evidence; no issue closure/PR mutation. Then-observed PR31open/draft/unmergedheadca25 is dated metadata, not the assigned checkpoint or currentCI proof. [Initial auth summary](../evidence/R10-17/github-prewrite.json). Recovery GET/user13:53:01UTC againHTTP200/expectedidentity; credential captured only in memory, never saved/logged/argumented.

**Published meaningful commit:** **`e974da9856ee8cc4a7f8567d731c8f947acaa64e`** (18ownedfiles), `git push -u origin agents/r10-17-vega-visible-title` **exit0**, immediate `git ls-remote --heads origin refs/heads/agents/r10-17-vega-visible-title` **exit0/exactSHA match**. Source/existingmatrix unchanged; no issue/PR creation despite GitHub's standard suggestedPRURL. [Actual publication receipt](../evidence/R13-17/publication-receipt.json). Final staged18paths boundary/credential-pattern/whitespace checks exited0. Full suites/builds/packages/other engines/scales/later-source retests, independent non-author reviews/testers and observed green remoteCI remain outside this result and still required. Fullproduction/900goal remains unmet.

**Worker next action:** publish only this owned docs/receipt checkpoint, then save finalremoteHEAD readback in MAINownnote/report and hand off. Do not rerun completed40+40/browser or recreateworktrees. **Product next action (R04):** independently inspect/adopt the portable oracle proposal while retaining full visibleparent+correctchildtitles/nativevalues/geometry/XSS/hiddennegativecontrols; decide any existing-oracle correction in an authorized candidate and rerun affected tests on that source. No finalsignoff from this worker.
