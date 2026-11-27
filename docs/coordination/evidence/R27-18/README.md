# R27 Plotly literal-text evidence and reproduction

**Final943 full non-scale result:** exit1, **38failed/2547passed/5skipped/9scale-deselected/517errors327.01s**. `final-full-not-scale-94319d6.json` retains ALL560nonpassing IDs/kinds/messages/detailhashes and rawXML/log hashes; same nonpassing ID/kindset as first722 run, no new IDs, no waiver. Both background runs completed automatically with source/HEAD frozen and no poll/interrupt; no jobs remain. Final23new+original9pass does not imply full-suite GREEN. All earlier pending/running descriptions in historical JSON relate only to their explicitly named checkpoint.

Author role18; immutable product base `7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6`, source commits `72244399d3606046621afd6b11aaf19894d1460b` then `94319d679661a169856fb0a0ec0e9de5cbd6986f`. Manager authorization: MAIN `docs/coordination/tasks/R27-manager-queue-and-plotly-release.md`13–21. Existing source/tests outside `_plotly` unchanged. Source is not shipped to main or independently approved by this evidence.

## What ran

Existing read-only Python3.12.16 project environment; no installations. Node26.13.1, existing Playwright1.65.1/Chromium159.0.8154.6, self-contained local Plotly runtime. Browser requests are intercepted; any unexpected request is aborted and makes a strict assertion fail. No link is clicked. No HTML-link observation is called demonstrated JavaScript execution.

`A = C:/Users/bagma/AppData/Local/Temp/opencode/r27-18-output-ses_de567805bffdER1GlVd0ngLgKg`. Raw logs, XML and self-contained artifact HTML/manifests remain there; compact committed JSON contains exact hashes and all nonpassing IDs. PNGs here are actual captured and opened browser output, not fabricated previews.

Set the existing interpreter to `$Python`, repository worktree to the current directory, and create a fresh unique `$Out` directory. In PowerShell:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'python/deepviz/src'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$env:MPLBACKEND = 'Agg'
$env:R27_NODE_MODULES = '<existing directory containing playwright, not a newly installed copy>'
& $Python -m pytest python/deepviz/tests/test_r27_plotly_literal.py -q --tb=short --junitxml "$Out/new.xml" --basetemp "$Out/new"
& $Python -m ruff check .
& $Python -m mypy
& $Python -m mypy python/deepviz/tests/test_r27_plotly_literal.py
node --check tests/browser/r27_plotly_literal.mjs
& $Python -m pytest -m 'not scale' -q -rs --tb=short --junitxml "$Out/full.xml" --basetemp "$Out/full"
& $Python -m build --no-isolation --sdist --wheel --outdir "$Out/distributions"
```

Browser cases skip explicitly if existing Node/Playwright is unavailable; they never install. Our recorded5cases actually ran, and all fourteen cases including the unchanged external QA20 nine ran. Missing installed Chromium is an error, not silently converted to a pass. Scale is explicitly excluded, not measured or approved.

## Exact original-QA20 execution (author run, not independent approval)

Existing unchanged QA checkout:
`C:/Users/bagma/AppData/Local/Temp/opencode/r10-20-plotly-ses_de567801cffeGZFlt50oYv0Dnt` (Q).
Original4file hashes and exact public `eb98261567d05300b9c7d79af78c83f04812c853` Git-blob comparison are in `focused-results-7224439.json`.

For the final57.50s combined run, `R10_20_NODE_MODULES` and `R13_20_NODE_MODULES` were set to the same existing node_modules directory. Exact pytest targets:

```text
python -m pytest
  python/deepviz/tests/test_r27_plotly_literal.py
  Q/tests/r10_probes/role20/test_plotly_literal_labels.py
  Q/tests/r13_probes/role20/test_plotly_sink_discrimination.py
  python/deepviz/tests/test_backend_plotly.py
  python/deepviz/tests/test_render.py
  -q -rs --tb=short --junitxml A/final-focused.xml --basetemp A/final-focused
```

23 NEW +9original QA cases passed; connected176 add171pass/2unchangedrepresentation failures/3opt-in-CDN skips. Total **203pass/2fail/3skip**, not broad GREEN. Native coordinates, original manifests/records, counts/grouping, numeric/date axes and QA20 exact geometric spacing remain asserted.

## RED → GREEN chain and unresolved gates

- Exact7bc same-process import/Gitblob guards before initial NEW21 permanent RED;21fail/0error/0skip19.06s. Initial minimal `_plotly` mapping→21pass20.51s; unchanged QA20nine→9pass44.10s.
- Author self-review found accepted string-longitude values can become geo category ticks. Actual first fix722 had one link in that edge case. Added two NEW permanent controls, watched **2fail4.71s** before ONE additional `_plotly::geo` x-string mapping. Final23allpass and valid numeric geo unchanged. No geo input-validation semantics were broadened or narrowed.
- `_plotly` uses string-only HTML-text-sink escaping once, after original grouping/geometry, with `quote=False`; this preserves visible ordinary quotes and existing literal entity text. It never escapes the entire JSON or modifies source rows. Script/outer-HTML escaping remains unchanged.
- Existing `test_backend_plotly.py:202` expects quote entities, and `test_render.py:310` expects raw attack text inside native JSON rather than encoded sink text. Both remain unchanged and failing; R04 must explicitly disposition narrowly scoped representation expectations while preserving breakout/DOM safety and original-manifest assertions. No weakening/removal or unqualified safety waiver.
- First full722 run **38fail/2545pass/5skip/9scale-deselected/517errors286.45s**; all560nonpassing IDs/messages/hashes retained. Npm fixture errors reflect missing build of THIS checkout, not a copied sibling distribution. Other source failures remain disclosed, not fixed outside scope. Final943 full result must be read separately; do not extrapolate the earlier result.
- Full repository Ruff0/mypy0ninefiles; owned tests/helper typecheck0/Nodecheck0. Offline distribution build1: missing `hatchling.build`. No installed dependency or CDN/provider changes; no scale run, green CI, independent approval, main merge or issue closure claim.

## Review and ownership

Report: `docs/coordination/reports/R27-18-plotly-literal-text.md`. R04 alone integrates/opens PRs/merges/default-publishes/closes #36; root routes independent QA20/security02 on the real sealed source SHA. Author review and author execution of existing QA oracles are not independent approval. Local worktrees/proposals/old oracle files were preserved. Own branch publication uses explicit-path staging, non-force push and exact remote-SHA readback, never a blind whole-candidate merge.
