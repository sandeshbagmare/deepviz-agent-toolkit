# R35-02: independent sealed Plotly source review and ONE new hover counterexample

Review source fb0d22e13b89a26eb7df0f6ed008770ecb9e1c35, production94319d679661a169856fb0a0ec0e9de5cbd6986f/prerequisite72244399d3606046621afd6b11aaf19894d1460b/base7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6. Source-only outside-function/AST/57-path/source-import proofs in source-before.json and source-after.json. Author23 and unchangedQA20nine controls read AS SOURCE, NOT replayed. No production/oracle/dependency/install/API writes.

## Concrete new finding R35-02-F1/P2

With two Cartesian line series, color=series, hover first point on series R35 long "Ω" & <b>series-name-preserve-END</b>. Native legend is full literal; hover name is R35 long "Ω"... due to actual hoverlabel.namelength15. Four manifest rows/native numerical coordinates remain unchanged, zero anchors/handlers/console/pageerrors/network. This is incomplete visible hover data, NOT JS execution or a manifest data-loss claim. Original two representation oracle failures need R04 separate narrow disposition; do not waive this actual DOM loss with them.

## Exact bounded repro

Use the existing Python environment/Node/Playwright/Chromium ONLY. Set R35_02_SOURCE to clean sealed checkout; PYTHONPATH to its python/deepviz/src; R35_02_NODE_MODULES to existing MAIN/node_modules; PYTHONDONTWRITEBYTECODE=1 and PYTHONUTF8=1. A unique results directory is required. The test reads this frozen source-before.json and verifies module hashes before render; no missing prerequisite is skipped or installed. Current DOM/PNG destinations already exist: preserve them and use a NEW copy of only this owned probe/evidence for a fresh authorized run, do not overwrite evidence. Do NOT replay merely to reconfirm this handoff.

Command actually run: EXISTING_PYTHON -m pytest docs/coordination/evidence/R35-02/test_long_hover_counterexample.py -q -rs --tb=short -p no:cacheprovider --basetemp UNIQUE_NEW_TEMP --junitxml docs/coordination/evidence/R35-02/long-hover.xml

Final actual exit1/1failed0errors0skipped4.44s. Strict expected full literal hover name intentionally remains RED; never change to truncation, xfail or skip. JS helper only trusted local inspection/pointer hover; no clicks/data evaluation/unexpected requests.

summary.json reconciles ONE distinct new case, three execution checkpoints: initial single-series expectation wrongly assumed a name field (NOT finding); corrected two-series context1FAIL5.62s; final no-op typing.cast correction1FAIL4.44s. calibration-single-trace and calibrated-before-typecast preserve all initial logs/XML/DOM/PNG/source. All three screenshots actually opened; final long-hover.png shows the clipped hover and complete legend.

Final own focused Ruff0/mypy0(ONE Python file)/node --check0. Initial mypy optional __file__ typing1 corrected only by cast. A collector Unicode-pipeline expected-literal assertion1 corrected to ASCII chr(937), no test/source/oracle rerun; source-after partial write was read back before continuing. None of these tooling events is an extra product failure or independent test count.

Future fix belongs R04 alone. Suggested direction: native hoverlabel.namelength=-1, preserving exact-one display escaping and original records. Actual NEW source SHA and NEW independent identity adapter are required before future repaired-source testing; preserve published full-hover assertion and existing fb0 proof, never pass a new engine against an old identity claim. No final Plotly acceptance/CI/default/PR/issue closure inferred.
