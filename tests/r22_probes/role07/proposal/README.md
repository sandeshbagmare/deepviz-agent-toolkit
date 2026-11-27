# R22-07 COUNT channel repair proposal

**Historical R22 proposal checkpoint; no production source is changed in this branch.**
After this checkpoint, R04 granted the function-only R23 repair; actual source
commit85796dbe3360fb88686f2e7188122e2da80d54c2 and its results are recorded
separately in `docs/coordination/reports/R23-07-count-channel.md` on the R23 branch.
The R22 patch remains unapplied here. At the time of this proposal R04 retained
`python/deepviz/src/deepviz/engines.py::channels`; `_antv` is separately owned by
08. The production release request is recorded in
`docs/coordination/reports/R22-07-count-producer-readiness.md` and requires an
explicit file-backed R04 grant at an exact source pin before applying the patch.

## Root cause and minimal line-level change

`normalize()` already owns COUNT semantics. For a non-heatmap with
`aggregation="count"` and no explicit `y`, `_plan()` writes a generated
`count` measure into bounded normalized records and retains only grouping keys
plus that measure. `channels()` then independently picks the first numeric
field after `x`. If a numeric `color` is retained, it is selected before the
generated `count`, so every adapter receives the color value as `_y` (the R15-17
literal multiplicity fixture observes 90/80/70 instead of 2/3/1).

The proposal is exactly two lines in `channels()` after existing x/y inference:

```diff
     x = spec.x or next((key for key in fields if key not in numeric), fields[0] if fields else None)
     y = spec.y or next((key for key in numeric if key != x), numeric[0] if numeric else None)
+    if spec.aggregation == "count" and spec.y is None and spec.kind != "heatmap":
+        y = "count"
```

This is deliberately not an `auto` fix. The normalizer's actual planner treats
numeric color as a possible numeric y/measure for `aggregation="auto"`; changing
that selection in the renderer would silently turn a valid SUM decision into
COUNT or bypass the existing group/measure collision validation. It also does
not infer a count merely because a field is named `count`.

## Contract preservation

- **Explicit COUNT:** uses generated `count` when `y` is omitted, including
  numeric retained `color` and `size`; missing generated measure remains `None`
  and follows existing geometry warnings rather than fabricating a value.
- **Explicit y:** `spec.y` remains authoritative for COUNT with a named output
  measure, and for SUM/NONE. The condition requires `spec.y is None`.
- **SUM/NONE:** untouched. Their mapped y values remain the reducer's named
  measure or original row value, including zero, null and missing values.
- **Heatmap COUNT:** excluded because heatmaps use x/y as coordinates and
  `count` as `_heat`; changing `_y` would destroy the y-axis. Existing x/y/count
  records and `_heat` mapping remain unchanged.
- **Non-numeric color:** no change; auto COUNT continues to use generated count.
- **Retained numeric color/size:** preserved as `_color`/`_size`; only `_y`
  changes to generated count under explicit COUNT. No normalized record/spec is
  mutated; channels continues producing new mapped dictionaries.
- **Metadata:** normalization remains the sole source of input/output counts,
  strategy and warnings. The patch changes no manifest or artifact metadata.

## New bounded controls

`../test_count_proposal_boundaries.py` contains six small boundary cases for
auto COUNT vs numeric-color SUM collision, generated-count key collision,
heatmap coordinate preservation, nonmutation/missing-vs-zero, and the direct
helper's fail-closed handling of an absent generated measure. That last case
deliberately supplies invalid reducer output and is not a public-normalizer
acceptance claim. It does not replay the 56-case R15 matrix, five-engine native suite,
browser suite or any scale run. The proposal patch itself is not applied to the
production worktree.

## Strict GREEN recipe after R04 release

At the exact R04-released source pin, in a fresh own worktree and unique output
directories:

```powershell
$env:PYTHONPATH = "$PWD/python/deepviz/src"
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m ruff check tests/r22_probes/role07/test_count_proposal_boundaries.py
python -m pytest tests/r22_probes/role07/test_count_proposal_boundaries.py -q --tb=short
# Use a separate byte-identical extraction of immutable17 probes at76cac9d.
# Verify corrected-source module identities separately, not with the old5340 assertion.
python -m pytest <immutable17-probe-dir>/test_count_measure.py -q --tb=short -k 'not loaded_modules_match_pinned_source_identity'
```

Before and after the patch, record exact HEAD, loaded `engines.py` SHA256,
`normalize.py`/`models.py` SHAs, command exits, totals and skips. The immutable
R15 identity test hard-codes5340: a new ledger alone cannot retarget it. Deselect
ONLY that identity test, explicitly record1deselected, and independently verify
all four actual corrected-source modules against exact chosen Git blobs. Keep
every semantic oracle byte-identical; require55semantic passes/0fails/0skips,
not56passes or a skipped old identity counted as acceptance. Never label a5340
result as a corrected-source result. Then run the existing bounded R15 native artifact/metadata
probe and its actual-output collector once on the corrected source, inspect
the resulting Matplotlib/Vega/Plotly images and console/request results, and
publish only source-specific evidence. ECharts/G2 network limitations remain
explicit; no browser or all-engine claim follows from this recipe alone.

If any pre-existing R15 control fails after the two-line patch, preserve the
failure and stop; do not weaken the oracle or broaden `channels`. R04 then
decides whether a separate source correction is needed.

## Blocker at the R22 checkpoint (subsequently released)

At this finished R22 checkpoint **production release was not granted**; that
blocker was subsequently lifted by R04's file-backed R23 grant. This historical
R22 branch still changes no product file/schema/dependency/shared branch/PR/issue.
