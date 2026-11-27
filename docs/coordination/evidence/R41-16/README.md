# R41-16 — BLOCKED callback candidate, not approval

**Product:** `f48c72e26000560b48f3dfd137696fa9acf17637`, exact e47 parent,
`fix/r41-callback-admission`. Four approved additions only. Source was
non-force-published and exact remote SHA read back; it remains **FROZEN**.

## Decisive counterexample

Read `counterexample-e47.json`, `counterexample-f48.json` and
`semantic-compatibility-gate.json` first. Create a handle from a host-authorized
one-row file, replace that OWN file with two new-field rows, then recommend with
bare JSON `{"dataset_id": handle}`. On all run/arun/invoke/ainvoke forms:

| Result | Exact clean e47 | Four-line f48 |
| --- | --- | --- |
| input_count | 2, reread | 1, stale cached summary |
| spec | histogram x=amount | bar x=label, y=value |
| handle | new | original |

Explicit-dictionary recommendation remains cached1 and fresh normalization
returns2 on BOTH sources. Each valid recommendation has one SDK start/end and
no output artifacts. The two actual-SDK observation commands exited0; the
separate strict saved-actual-output gate exited**1**, four violating forms.
Those are **not** four additional pytest executions or independent reviews.

This changes public results/reference behavior outside the accepted callback
representation change. **Do not merge f48 as-is. R04 decision/new scope needed.**
No source/tests/backend/cache policy were changed after discovery; no oracle
was weakened to bless stale output. The expected baseline2 remains literal.

## Execution ledger

`P = C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe`

`A = C:\Users\bagma\AppData\Local\Temp\opencode\r41-16-callback-admission-ses_de567808bffdXko8hyKFRhPv77-artifacts`

Working OWN checkout uses the same name without `-artifacts`. Helpers are
retained verbatim as `.py.txt` so they are not accidentally collected/linted as
new product modules. The original two role02 files retain exact Git SHA256;
the old d65 identity helper is **preserved, not executed as f48 proof**.

Executed command forms (`P -S`, own source first, readonly existing site
bootstrap and six actual-module Git/import guards; no install):

1. `P -S A/run_checks.py identity pre-red` after correcting omitted pywin32
   bootstrap. First attempt failed before tests; transcript/report discloses it.
2. `P -S A/run_checks.py pytest python/deepviz/tests/test_r41_callback_admission.py -q --tb=short -p no:cacheprovider --basetemp A/pytest-red --junitxml A/red.xml`
   — initial32fail46pass; four NEW mistaken mixed-object rowcount expectations
   corrected1vs2 before production (not changes to any old oracle).
3. Same command with `pytest-red-final/red-final.xml`: untouched-e47
   **28fail50pass**, then ONLY four source additions; same78cases GREEN
   **78pass** using `pytest-green/green.xml`.
4. Readonly `ruff.exe check --no-cache` and `mypy.exe --cache-dir A/mypy-cache`
   on `python/deepviz/src/deepviz/tools.py` and NEW test: both exit0.
5. `P -S A/run_checks.py pytest python/deepviz/tests/test_r14_tool_json_boundary.py -k structured -q --tb=short -p no:cacheprovider --basetemp A/pytest-connected-json --junitxml A/connected-json.xml`
   — 11pass26deselected, not a stdio/SDK matrix replay.
6. Same pytest runner on the following exact `test_integrations.py::` nodes,
   with `pytest-connected-tools/connected-tools.xml`: 18pass:
   `test_normalization_returns_bounded_profile_and_reusable_handle`,
   `test_flow_preserves_original_input_count_after_bounded_profile`,
   `test_file_inputs_cannot_escape_the_explicit_data_root`,
   `test_file_inputs_disabled_without_data_root`,
   `test_file_input_and_recommendation_do_not_return_raw_rows`,
   `test_invalid_references_are_not_evaluated_or_treated_as_paths`,
   `test_inline_payload_limit_points_to_file_workflow`,
   `test_extra_executable_spec_fields_are_rejected`,
   `test_model_cannot_choose_output_directory`,
   `test_recommendation_uses_observed_types_and_goal`.
7. `P -S A/freeze_source.py` exact four-addition byte proof, explicit three-path
   source commit, staged-byte checks, no unrelated source changes: exit0/f48.
8. `P -S A/run_checks.py identity committed-f48` then
   `P -S A/run_checks.py original f48c72e26000560b48f3dfd137696fa9acf17637 -q -rs --tb=short -p no:cacheprovider --basetemp A/pytest-original-six --junitxml A/original-six.xml`
   — **6pass2deselected0skip**, actual committed source guards FIRST, unchanged
   original assertions. Only documented source/results fixture bindings change.
9. Fresh committed NEW suite, `pytest-committed/committed.xml`: **78pass0skip**.
   Actual sync/async native PNGs opened by author (A3/B7, clear axes/title,
   no clipping), SVG/manifest data checked. PNGs are900x520, matching manifests.
10. `P -S A/publish_owned.py f48c72e26000560b48f3dfd137696fa9acf17637 source`
    — nonforce own push0/exact remote readback0. Initial receipt's broad
    `no persistent-config change` scope wording is corrected: authorized
    `--set-upstream` writes OWN branch tracking. Raw receipt is retained.
11. After STOP, own detached clean e47 control worktree created; ONLY bounded
    `P -S A/semantic_counterexample.py SOURCE PIN e47|f48` observation probes,
    both exit0. **No source/test edits**, all four actual forms; then
    `P -S A/compare_counterexample.py` strict gate **exit1**.
12. Evidence collector initially failed on an incorrect guessed display size
    (900x540). Actual partial output read/retained; recovery reuses byte-identical
    owned copies and validates native pixels against real manifest900x520.
    No test/product oracle changed; recovery exit0. Text evidence is UTF8/LF for
    Git, with raw artifact hashes retained and original two Python SHAs intact.

113 distinct passing AUTHOR cases do not waive the later four-form public
compatibility counterexample. No independent review/tester credit, CI, full
suite, distribution/npm build, full SDK/stdio/browser matrix, scale/10M replay,
PR/issue/merge/closure or release signoff is claimed.

## Remaining owner/blockers

- **R04:** decide the unaccepted public routing/reference change and issue a new
  scoped contract/source assignment; no unilateral widening by role16.
- **R04:** disposition of the disclosed initial `git config core.autocrlf false`
  setup write to common repo-local configuration (prior value UNKNOWN; no blind
  rollback attempted). OWN upstream tracking is separately authorized.
- Only own branch, own note/report/evidence and MAIN central `status/role16.md`
  were intentionally published/updated; no main/shared-candidate/default merge
  or API mutation. Forecast UNKNOWN until R04 decision and actual release gates.
