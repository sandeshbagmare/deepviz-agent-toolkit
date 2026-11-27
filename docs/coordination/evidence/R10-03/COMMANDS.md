# R10-03 executed-command ledger

Owner `ses_de5678315ffeDxQVEpE9V9WSTE`. Tested product checkpoint
`3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`, not final freeze.

All product commands ran in the isolated OWN branch
`agents/r10-03-echarts-numeric-x`. Existing MAIN Python3.12.16 venv was read-only
execution tooling. DeepViz module paths/hashes in `results.json` prove OWN source.
No dependency installs, source edits or changes to existing matrix/oracles.

```powershell
$py = 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe'
$browserPy = 'C:\Users\bagma\AppData\Local\Programs\Python\Python314\python.exe'
$env:PYTHONPATH = "$PWD\python\deepviz\src"
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'

git worktree add -b agents/r10-03-echarts-numeric-x C:/Users/bagma/AppData/Local/Temp/opencode/r10-03-echarts-numeric-x-ses_de5678315ffeDxQVEpE9V9WSTE 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab
# exit0, once. Baseline0c5 worktree/artifacts preserved.

& $py -m pytest tests/r10_probes/role03/test_echarts_numeric_x.py -q --strict-markers --tb=short --basetemp=artifacts/r10-03/portable-temp --junitxml=artifacts/r10-03/portable.xml
# exit0:36passed,0skipped0.60s (before own fixture annotation-only correction).

& $py -m pytest tests/test_acceptance_matrix.py -k 'test_engine_kind_theme_source_acceptance and echarts and (line or area)' -q --strict-markers --tb=short --basetemp=artifacts/r10-03/original-matrix-temp --junitxml=artifacts/r10-03/original-matrix.xml
# exit1:20failed,1129deselected,0skipped1.82s. No xfail/assertion/oracle edits.

& $py tests/r10_probes/role03/visual_probe.py generate artifacts/r10-03/visual-v1
# exit0:6fresh artifacts, each3input/3output rows. Destination must be NEW.
& $browserPy tests/r10_probes/role03/visual_probe.py capture artifacts/r10-03/visual-v1/fixtures.json
# exit0:6captured,0console/page/requesterrors.

& $py -m ruff check tests/r10_probes/role03
# first and final exit0 (new owned probes only).
& $py -m mypy tests/r10_probes/role03/echarts_coordinate_oracle.py --strict --cache-dir artifacts/r10-03/mypy-oracle-cache
# first exit1:own fixture dictionary annotation inference,1error1file.
# ONLY own annotation corrected; final exit0:noissues1file.
& $py -m mypy --cache-dir artifacts/r10-03/mypy-product-cache
# exit0:noissues9sourcefiles (configured product scope, not whole-repo tests).
```

Final ordinary tests after the own annotation correction were also run from
**outside repo CWD** (`<OWNworktree>/artifacts/r10-03`). With `$root` resolved to
the OWN repo and ownsourcePYTHONPATH:

```powershell
& $py -m pytest "$root/tests/r10_probes/role03/test_echarts_numeric_x.py" -q --strict-markers --tb=short "--basetemp=$root/artifacts/r10-03/portable-external-temp" "--junitxml=$root/artifacts/r10-03/portable-external.xml"
# exit0:36passed,0skipped0.59s. No stale capture/CWD dependency.

# Back at OWN repo root, final actual browser probe after annotation correction:
& $browserPy tests/r10_probes/role03/visual_probe.py capture artifacts/r10-03/visual-v1/fixtures.json
# exit0:6captured,0errors, realCDN no interception/stubs.

& $py artifacts/r10-03/collect_evidence.py
# first exit1:local contact collector wrongly assumed640x400 screenshots.
# All6 actualPNGs are640x401. Only localcollector patched to read tile dimensions,
# paste unresized/uncropped into1280x1203contact. Original failed attempt preserved.
```

R13 recovery read existing own branch/logs/status and performed **one** bounded
matching-Python process snapshot: no surviving owncollector/browser. No completed
test/browser/full command was replayed as recovery. The already-patched collector
was the first unfinished action:

```powershell
& $py artifacts/r10-03/collect_evidence.py
# exit0:SOURCE=3aa521a5...; NEW_TESTS=36; MATRIX_FAILURES=20; BROWSER_CASES=6; ERRORS=0
git diff --exit-code 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab -- python packages schemas tests/test_acceptance_matrix.py
# collector subprocess exit0:source/existing-oracle unchanged.
```

Image reader then OPENED all6 originalPNGs (`line/area-value/category/time.png`)
and the contact. Values2/8/3 and titles were visible; numeric/time gapratio2,
categorygapratio1, area closes to zero. Browser JSON asserts actual SVGvertices
within0.00006pixel of native mapped coordinates, not just paint/artifactpresence.
Images are6finite lighttheme controls, NOT universal/theme/security/finalsignoff.

Authentication before writes: expected HTTPS origin and credentialhelpermanager;
GCM stdout/token captured only in subprocess memory, authenticated GET/user200
verified`sandeshbagmare`, GETrepo200 verified expectedpublicrepo. No auth/config
changes. Initial receipt`github-identity.json`; fresh prepublication receipt
separate. Initial ownbranch `git ls-remote --heads origin refs/heads/agents/r10-03-echarts-numeric-x`
exit0 returnedno ref (not a push).

Explicit staging/security/whitespace/commit/push/actualremoteSHA receipts are
recorded separately in the own report/publication evidence. This ledger does not
claim unrun fullPython/ruffroot/builds/packages/scales/MCP/DeepAgent/CI gates.
