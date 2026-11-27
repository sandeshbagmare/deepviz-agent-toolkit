# Actual merged-main31cff independent QA commands

All commands ran once in this trigger. Exact default/Git fetch/worktree/ancestry/ALL15hash commands are preserved without overwriting baseline at `../R26-13/source31cff/source-freeze.json` and `official-freeze.json`. Actual main frozen 2026-11-27T16:51:34.279523Z; no later default/CI queries.

## shipped82

`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -I -S C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\tests\r38_probes\role13\verify_merged.py --source C:\Users\bagma\AppData\Local\Temp\opencode\r26-13-main-31cff73-ses_de56780caffekQ9gdZ58EgQwb5 --sha 31cff73ab057c3fed69bd400ac005f2f11609027 --site-packages C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages --probe C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\tests\r26_probes\role13\test_default_contract.py --mode shipped --output C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\docs\coordination\evidence\R38-13\shipped82`

CWD `C:\Users\bagma\AppData\Local\Temp\opencode\r38-13-empty-cwd-ses_de56780caffekQ9gdZ58EgQwb5`; exit 0; outer seconds 4.001264000005904; totals {"tests": 82, "failures": 0, "errors": 0, "skipped": 0}; passed 82. Raw stdout/stderr and commandJSON are adjacent; real JUnit/model JSON/source/import receipts in the matching subdirectory.

## retained30

`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -I -S C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\tests\r38_probes\role13\verify_merged.py --source C:\Users\bagma\AppData\Local\Temp\opencode\r26-13-main-31cff73-ses_de56780caffekQ9gdZ58EgQwb5 --sha 31cff73ab057c3fed69bd400ac005f2f11609027 --site-packages C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages --probe C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\tests\r26_probes\role13\test_default_contract.py --mode probe --output C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\docs\coordination\evidence\R38-13\retained30`

CWD `C:\Users\bagma\AppData\Local\Temp\opencode\r38-13-empty-cwd-ses_de56780caffekQ9gdZ58EgQwb5`; exit 0; outer seconds 3.4544741999998223; totals {"tests": 30, "failures": 0, "errors": 0, "skipped": 0}; passed 30. Raw stdout/stderr and commandJSON are adjacent; real JUnit/model JSON/source/import receipts in the matching subdirectory.

## mapping-schema-smoke

`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -I -S C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\tests\r38_probes\role13\verify_merged.py --source C:\Users\bagma\AppData\Local\Temp\opencode\r26-13-main-31cff73-ses_de56780caffekQ9gdZ58EgQwb5 --sha 31cff73ab057c3fed69bd400ac005f2f11609027 --site-packages C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages --probe C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\tests\r38_probes\role13\test_merged_mapping.py --mode probe --output C:\Users\bagma\AppData\Local\Temp\opencode\r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5\docs\coordination\evidence\R38-13\mapping-schema-smoke`

CWD `C:\Users\bagma\AppData\Local\Temp\opencode\r38-13-empty-cwd-ses_de56780caffekQ9gdZ58EgQwb5`; exit 1; outer seconds 3.399463400011882; totals {"tests": 7, "failures": 3, "errors": 0, "skipped": 0}; passed 4. Raw stdout/stderr and commandJSON are adjacent; real JUnit/model JSON/source/import receipts in the matching subdirectory.

## Focused actual-main static gates

`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\ruff.exe check --no-cache .`; CWD `C:\Users\bagma\AppData\Local\Temp\opencode\r26-13-main-31cff73-ses_de56780caffekQ9gdZ58EgQwb5`; exit 0; outer seconds 0.09583740000380203.

`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\mypy.exe --cache-dir C:\Users\bagma\AppData\Local\Temp\opencode\r38-13-mypy-cache-ses_de56780caffekQ9gdZ58EgQwb5`; CWD `C:\Users\bagma\AppData\Local\Temp\opencode\r26-13-main-31cff73-ses_de56780caffekQ9gdZ58EgQwb5`; exit 0; outer seconds 5.1361547999986215.

`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\ruff.exe --version`; CWD `C:\Users\bagma\AppData\Local\Temp\opencode\r26-13-main-31cff73-ses_de56780caffekQ9gdZ58EgQwb5`; exit 0; outer seconds 0.04802090000885073.

`C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\mypy.exe --version`; CWD `C:\Users\bagma\AppData\Local\Temp\opencode\r26-13-main-31cff73-ses_de56780caffekQ9gdZ58EgQwb5`; exit 0; outer seconds 0.5287221000035061.

Pre-execution NEW-own-probe lint: `C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\ruff.exe check --no-cache tests/r38_probes/role13/verify_merged.py tests/r38_probes/role13/test_merged_mapping.py`; exit0 (actual prior native result; no runtime file edits/replay).

Saved-artifact integrity commands: project venv `python.exe -`, JUnit/count/observations/source hashes, exit0; these are not additional product tests. Initial issue metadata collector `python.exe -` exited1 on Windows cp1252 U+2192 print; preserve failure summary, no complete saved global-search claim. Bounded recovery only #5/#30 body/comments: 4GET200/zero API writes, child UTF8, saved before printing. No auth repair/installs/default or CI polling.

Numeric #30 acceptance PASS; three strict known #5/dashboard-schema failures remain RED (not xfails). Python3.11/3.13/Linux/remote postmerge CI/builds/cleaninstall/browser/render/MCP/DeepAgents/npm/10M NOTRUN here; absent implementations are not regressions.
