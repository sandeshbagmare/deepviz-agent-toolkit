# R51-09 exact96 TEST2 commands and receipts

Product source: `96b819aee5b01ba88b5a609b587331a528aaa070` in `C:\Users\bagma\AppData\Local\Temp\opencode\r51-09-accounting96-ses_de56782e5ffe3H1lUAoxrBtEhx`; clean tracked tree, exact normalizer SHA `b64814a6406857d9c9a1078fb759725a65a4a91d0db033c765d015df018dc6fd`. Existing Python 3.12.16 executable below; no install. The PowerShell process set transient `PYTHONPATH` to this checkout's `python\deepviz\src`; no persistent environment change.

Executable: `C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe`

Final authoritative commands, each run once on the final NEW test file (exit in parentheses):

1. `& '<python>' -B -m ruff check --no-cache --config '<source>\pyproject.toml' '<source>\tests\r51_probes\role09\test_numeric_accounting_test2.py'` (0)
2. `& '<python>' -B -m mypy --config-file '<source>\pyproject.toml' --no-site-packages --follow-imports=skip --no-incremental --cache-dir '<source>\artifacts\r51-09\mypy-final-2' '<source>\tests\r51_probes\role09\test_numeric_accounting_test2.py'` (0)
3. `& '<python>' -B -m pytest '<source>\tests\r51_probes\role09\test_numeric_accounting_test2.py' -q --disable-plugin-autoload --strict-markers --tb=short -p no:cacheprovider --basetemp '<source>\artifacts\r51-09\pytest-temp-final-2' --junitxml='<source>\artifacts\r51-09\tests-final-2.xml'` (0):19 passed,0 failed/error/skip/deselected,1.06s.

Draft/static correction history: initial test-file Ruff exit1 for one unused `os` import, mypy0, pytest19pass/1.47s; after removing the import, Ruff0/mypy0/pytest19pass/1.93s, but then the test's bit-bound assertion was made a local independent arithmetic oracle rather than calling the production helper. Final three commands above run against that final exact file; prior draft run output is preserved, never counted as the final check.

Coverage: eight huge mean/SUM cancellation combinations (sign/order/native/one-pass), six ordinary/signed/finite-float/count literals, independent `bit_length//3+1+sign` bound, unchanged natural retained budget on lazy stream, explicit zero/nonmutation, unsupported-value TypeError/nonmutation, exact source/default4300 guard. No cap/source/oracle/global digit changes; no old R44 matrix, author tests, producer tests, or product test replay.

Strict role11 TEST1 compare read from its own clean worktree HEAD `8aadc163d72c6e258a657eab54fd6060e936cbd0`: its report and verification JSON bind same96 source/normalizer/default4300;17pass0fail0skip, natural budget1001. No disagreements; overlap acknowledged. Role11 result is not included in role09 totals and neither suite approves its author.

No full suite/package/build/install/10M/browser/MCP/DeepAgents/CI/default/API/PR/issue status was verified. Next owner: R04 compares role09+11 tests with source reviews14/21 and makes the PR2/role07 integration decision. Remaining estimate UNKNOWN.
