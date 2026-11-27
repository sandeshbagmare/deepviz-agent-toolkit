# R30-06 FUTURE first-render acceptance — NOT EXECUTED

This recipe accompanies static release preparation. **No build, install, package import, render, image open, test or browser run occurred in R30-06.** It is NOT approval of candidate3eab699, models998 or a future slice. R04 must first supply an actual dependency-complete frozen/merged head and authorize these gates. `future_acceptance.py` targets the recommended honest **Matplotlib-only bar/line** first surface; it intentionally rejects Plotly/pie until those capabilities have their own release. If R04 chooses a different fully gated surface, agree its acceptance before execution; do not silently remove negatives to turn a result green.

## 1. Actual source and installed consumer — future commands only

Use a NEW detached clean worktree at the ACTUAL manager-supplied SHA, not dirty MAIN, the old evidence branch, or guessed future source. Record `git rev-parse HEAD`, `git status --porcelain`, the precise module Git blobs, commands/exits and wheel SHA256. A correct clean source snapshot must contain all8modules imported by this recipe, a valid build configuration and all declared resources.

Create `source-proof.json` from **actual committed Git blobs**, not installed/working files: JSON keys `source_sha` (actual40hex), `clean_git_source` (true only after observed empty status), and `module_git_LF_sha256` mapping `deepviz/__init__.py`, `models.py`, `normalize.py`, `engines.py`, `render.py`, `tools.py`, `recommend.py`, `cli.py` to SHA256 of their committed bytes with ONLY CRLF→LF normalization. Record rawblobhashes and any newline-only difference separately. Verify the built wheel's eight members against that proof BEFORE installation. This is not a caller-supplied magic approval flag; the independent tester produces it from verified Git and preserves the commands/output.

From the actual source, using an approved build environment with installed `build`, **hatchling>=1.27**, Twine and core dependencies:

```powershell
& $BuildPython -m build --outdir $NewDist
& $BuildPython -m twine check "$NewDist\*"
Get-FileHash -Algorithm SHA256 $ActualWheel
& $BuildPython -m venv $NewConsumer
$ConsumerPython = Join-Path $NewConsumer 'Scripts\python.exe'
# Only after separate installation approval; use an approved complete dependency wheelhouse.
& $ConsumerPython -m pip install --no-index --find-links $ApprovedWheelhouse $ActualWheel pillow
& $ConsumerPython -I -m pip check
```

If the wheelhouse/backend/dependency is missing, STOP and report the precise blocker; do not add `--no-deps` and call it a clean consumer or silently install online. Current main/candidate metadata declares Python>=3.11; core Pydantic>=2.10,<3, NumPy>=1.26, Matplotlib>=3.9 **and also Plotly>=6,<7/vl-convert-python>=1.7**. Those last two are unnecessary on the native path but still installation requirements unless an actually reviewed packaging change moves them; this recipe does not pretend that change exists. Agent/MCP/Arrow extras are NOT required for the selected native path. Check wheel+sdist for schema/prompts/typing marker if their APIs/config remain exposed.

Copy this standalone recipe into an external consumer directory, not the repo; use an empty CWD and `-I` (no editable `PYTHONPATH`/MAIN-hook fallback). Then:

```powershell
& $ConsumerPython -I "$ExternalRecipe\future_acceptance.py" --proof $ActualSourceProof --output $NeverUsedOutput
& (Join-Path $NewConsumer 'Scripts\deepviz.exe') --help
# Exercise the actual installed console script too, not only `python -m`.
& (Join-Path $NewConsumer 'Scripts\deepviz.exe') render "$NeverUsedOutput\count-bar-data.json" --spec "$NeverUsedOutput\count-bar-spec.json" --engine matplotlib --output-dir $NewConsoleOutput
```

No first-render head was supplied/tested during preparation. Exact new-source hashes/results must be collected later; old262/857author reports are not these commands' outcomes.

## 2. Fixed literal quantitative oracles

- **COUNT bar:** six literal rows A/series90 twice, B/series80 three times, C/series70 once; x=`label`, color=`series`, y OMITTED, aggregation=`count`. Expected retained rows `{A,90,count2}`,`{B,80,count3}`,`{C,70,count1}` in that order, input6/output3/count/no warnings. Actual Matplotlib heights2/3/1, not90/80/70; every bar starts at zero. This forces the shared-channel fix into the first native release.
- **Line:** x[-3,0,6], y[-2,0,4], aggregationnone, input3/output3/original order/no warnings. Data-transform pixel x-gaps1:2, literal midpoint sample(0,0), signed zero in y-range. No copied renderer formula or automatic-category assumption.
- Each case runs public installed API and installed CLI, producing PNG, SVG, static accessible HTML and manifest. PNG640×400; Matplotlib SVG460.8×288**pt** at100dpi (not640×400pt). Same artists backPNG/SVG. Titles exact `R30 count bars`/`R30 numeric line`; axis values/title boxes, manifest records/counts/strategy and native artist geometry supplement actual image inspection.
- Strict new negatives pin current Mappingmodel weakness, boolean numeric coercion, extra executable/callback field, unsupported initial engine/kind, absent yfield, generatedcount/group collision and duplicate encodedtool fields. No successful zero/empty/NaN replacement, xfail, silentclamp or weakening. Admission failure before output allocation, caller sentinel unchanged.

The standalone recipe is a future starting acceptance gate, not exhaustive qualification or a claim that raw helper geometry alone certifies public output. CLI module tests are supplemented by the installed console-script command. Add source-dependent gap/nonfinite/path/latefile-error cases to the actual authored test suite only after inspecting the proposed extraction; existing strict tests remain unchanged.

## 3. Future real images / static HTML browser gate

Open the actual generated count-bar and line PNGs using the image reader; inspect corresponding SVGs, readabletitles/ticks/labels/zero/signedvalues, correct1:2spacing, unclipped plot and no unrelated file overwrite. Record actualpaths+hashes and image observations. NEVER create replacement images or call metadata/screenshot existence visual approval.

Where installed browser tooling is available and authorized, open the genuine companion `chart.html`, wait for its actual relative `img` load (`complete && naturalWidth>0`), check table rows/countsummary/title, fail on every console/page error/failed local request, and capture actualoutput. This staticHTMLpath contains NOscript and NOCDN: **do not wait for `deepvizReady`**, which is a different browser-engine contract. Zero externalrequests and zeroerrors are applicable future gates, NOT observations made in R30. If optional browser tooling is absent, record an explicit pending/skip, never a pass. No CDN mocks, source substitutions, live provider/MCP/10M/fulloldmatrix required for this tiny slice.

## 4. Handback gate

Record actual frozen head+module/wheel/recipe hashes, commands/exits/test totals/skips, decodedPNG/SVG/HTML/manifest correctness and actualopenedimages. Two genuine source reviewers and two independent testers, affected focusedCI and manager actual main ancestry/merge checks are still required. R04 owns sequencing/PR/default; this recipe grants no production edits, installations, dispatch or merge authority.
