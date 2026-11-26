# Baseline integrated-candidate findings, b6abc8d

C17 ran main candidate baseline (Python3.12.16/npm installed). Logs in `C:\Users\bagma\AppData\Local\Temp\opencode\C17-*.log`.

- npm build exit0, typecheck exit0, npm test exit0:30 passed/0 failed/0 skipped. Npm ci exit0/0 vulnerabilities. Not final-candidate signoff.
- Ruff exit1:10 import organization errors, all fixable. C17 will handle ONLY import organization on existing baseline test files after inspecting exact file list; source worker owns its source lint.
- Mypy exit1:8 errors/3 files. N05 owns engines.py:275 list assigned to int variable;276 int not iterable;362/363 object.update. render.py:63 str vs kind Literal;77 object.append;136 warnings wrong inferred type. N06 owns tools.py:113 OrderedDict index object vs str. Fix scoped typing without weakening behavior/test or Any blanket suppression. Exact main log available; re-run on own source with explicit MYPYPATH/config.
- Full pytest completed exit1:502 failed,1484 passed,4 skipped in830.26s. Source b6abc8d runtime unchanged;13 collected stale coercion goldens have since been repaired4aa3788 and390 targeted contract tests passed. This is not502 distinct issues: many are shared acceptance helper/oracle assumptions. Exact full log temp/C17-pytest-baseline.log (not polled; completion notification received).
- N09 independent static tester owns triage/repair of baseline acceptance/backend/performance TEST assumptions only, in addition to new tests. Keep strong semantic assertions; no xfails/skips or accepting wrong actual numbers. Examples: Unicode minus glyph parse, accessible Plotly lines+markers vs exact lines, accessible AntV layered view vs flat line, physical SVG width/viewBox conventions. Actual source defects remain N05/N04. Test oracle changes require recorded rationale and positive+negative controls, not merely greening suite.

Next C17: inspect model/schema current contract, report exact parent-owned parity decisions; preserve source-worker ownership.
