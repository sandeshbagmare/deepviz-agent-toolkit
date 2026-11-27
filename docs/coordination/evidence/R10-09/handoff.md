# R10-09 strict regression handoff (RED)

Actual owner `ses_de56782e5ffe3H1lUAoxrBtEhx`; own branch `agents/r10-09-helper-null-fix`, exact released base `6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce`. Preserved immutable R03 baseline. This session's higher-priority **do not edit production code** instruction prevents applying the requested source fix; only NEW regression and scoped evidence are published. This is not a fixed/green producer branch and must not be integrated alone.

## Reproduce

Use installed tooling without changing shared dependencies. From this isolated branch on this machine:

```powershell
$env:PATH='C:\Users\bagma\deepviz-agent-toolkit\node_modules\.bin;'+$env:PATH
$env:NPM_CONFIG_CACHE=Join-Path (Get-Location) 'artifacts\r10-09-20261127\npm-cache'
$env:NPM_CONFIG_UPDATE_NOTIFIER='false'
npm run build
npm run typecheck
node --test packages/deepviz/test/test_r07_tool_spec_null.test.mjs
npm test
npm run schema:check
$env:PYTHONPATH=Join-Path (Get-Location) 'python\deepviz\src'
& 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' scripts/export_schema.py --check
& 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' -m pytest tests/test_models.py tests/test_schema_contract.py tests/test_cross_language_contract.py tests/test_n12_authoritative_parity.py -q
```

Build/types/schema: exit0. New permanent regression: **31pass/5fail/0skip**, each explicit-null case fails with missing expected ValidationError rejection. Full npm: **277pass/5fail/0skip**, all246existingtests pass. Focused Python/public-TS parity: **689pass/0skip**. Original40wrappercomparisons: **35agreement/5nullmismatch**, strict exit1. `run-summary.json` includes exact totals, origin, hashes and limitations.

## Root cause and owner acceptance

At this base `packages/deepviz/src/render.ts:140`, `input.spec??{}` defaults explicit invalidnull as omittedspec. Unchanged helper schema and `validateSpec(null)` reject it. All5realpublichelpers exhibit the mismatch. Intended owner correction: default only `undefined` (`input.spec === undefined ? {} : input.spec`); no schema/existing-oracle change. It must preserve omitted/explicitundefined/emptyvalidspec, mapped values and dashboard defaults/titles, reject null and other invalidvalues, and pass the full suite. The permanent regression tests these behaviors without mocks.

Related real issue[#30](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/30) was GET-confirmedopen at2026-11-27T02:40:06UTC; F1is a distinct helper-defaulting defect, not the original numeric-coercion complaint. R04 owns the issue mapping/disposition, productionfix and integration. No issue/PRwrite/closure or independent finalapproval is claimed. After authoring this regression I am not the non-author final reviewer/tester.

Raw logs and expanded machine results remain in unique temp worktree `artifacts/r10-09-20261127/`, not committed caches/data/dependencies. Source and schemas unchanged. MAIN report `docs/coordination/reports/R10-09-helper-null-fix.md` and own actual-ID note receive publication receipts after real non-force pushes/readbacks.
