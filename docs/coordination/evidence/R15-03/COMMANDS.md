# R15-03 exact execution and reproducibility

Owner `ses_de5678315ffeDxQVEpE9V9WSTE`. CWD unless noted:
`C:/Users/bagma/AppData/Local/Temp/opencode/r10-03-echarts-numeric-x-ses_de5678315ffeDxQVEpE9V9WSTE` (**WT**).
Read-only interpreter **PY**=`C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`;
read-only compiler=`C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript/bin/tsc`.
`PYTHONPATH=WT/python/deepviz/src`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.
No dependency installs or production/existing-oracle edits. Source target5340;
OWN branch941c4e8 product bytes exactly equal it before publication.

## Actual commands (not a recipe substituted for execution)

1. `git status --short --branch; git rev-parse HEAD; git log -3 --oneline; git cat-file -t 5340bc69b7203ad7a9166543062482d819f9b705; git diff --exit-code 5340bc69b7203ad7a9166543062482d819f9b705 -- python packages schemas tests/test_acceptance_matrix.py; git ls-remote --heads origin refs/heads/agents/r10-03-echarts-numeric-x`
   - exit0; own tracked clean, untracked owned artifacts; object commit; source diff0;
     remote941c4e8352010fbfc57d75ccf7f251c8fd3a1ecc=HEAD.
2. Native `session_move` to existing WT returned SAME actualID, not a new session/worktree.
3. `node C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript/bin/tsc -p packages/deepviz/tsconfig.json`
   - exit0; only WT ignored dist. This is TS compilation, **not both package builds**.
4. `PY -m pytest tests/r15_probes/role03/test_graphql_pages.py -q --strict-markers --tb=short -p no:cacheprovider --basetemp=artifacts/r15-03/run-v1/pytest-temp --junitxml=artifacts/r15-03/run-v1/python.xml`
   - exit1;55pass3fail0skip0.65s, three own warning-classification mistakes.
5. `node --test --test-reporter=tap tests/r15_probes/role03/graphql-pages.test.mjs`
   - initial exit1;49pass9fail0skip0cancel311.124ms. Three own matcher mistakes,
     two carrier-source failures, four known sibling failures. `run-v1/node.log`.
6. `PY -m ruff check tests/r15_probes/role03` initial exit0 (before diagnostics added).
7. `node tests/r15_probes/role03/diagnose_graphql_pages.mjs artifacts/r15-03/node-carrier-diagnostic.json`
   - exit0;17observations. Saving observations is not acceptance.
8. `PY tests/r15_probes/role03/diagnose_graphql_pages.py artifacts/r15-03/python-carrier-diagnostic.json`
   - first exit1 own dataclass `.model_dump` error; corrected only own `asdict`.
   - corrected exit0;17observations, all15error-variant/carrier controls reject.
9. Step4 with basetemp=`artifacts/r15-03/run-final/pytest-temp` and JUnit=
   `artifacts/r15-03/run-final/python.xml`, expanded corpus:
   - exit0;73pass0fail0skip0.56s. `run-final/python.log`.
10. Step5 expanded corpus: exit1;63pass10fail0skip0cancel505.7722ms.
    `run-final/node.log`. Exactly6carrier-source +4dedup01F1 failures.
11. Scoped Ruff after diagnostic: exit1 own I001 import order; corrected only import order.
    Later final Ruff exit0 (`ruff-final.log`).
12. `node tests/r15_probes/role03/diagnose_graphql_pages.mjs artifacts/r15-03/node-carrier-diagnostic-final.json`
    - exit0;18observations, adds independent smallest literal two-page repro.
13. Step5 after replacing tautological import assertion with business-errors positive:
    - exit1;63pass10fail0skip0cancel495.1407ms, `run-final/node-final.log`.
14. `PY -m mypy tests/r15_probes/role03/graphql_fixtures.py --strict --cache-dir artifacts/r15-03/mypy-fixtures-cache`
    - first exit1 one own dict inference assignment; explicit annotation only.
    - final exit0,1source file. Not whole-release or all-probe type-check claim.
15. **External CWD**=`C:/Users/bagma/AppData/Local/Temp/opencode`:
    `PY -m pytest WT/tests/r15_probes/role03/test_graphql_pages.py -q --strict-markers --tb=short -p no:cacheprovider --basetemp=WT/artifacts/r15-03/run-final/external-temp --junitxml=WT/artifacts/r15-03/run-final/python-external.xml`
    - exit0;73pass0fail0skip0.81s. Final tested Python fixture annotation bytes.
16. Same external CWD: `node --test --test-reporter=tap WT/tests/r15_probes/role03/graphql-pages.test.mjs`
    - exit1;63pass10fail0skip0cancel469.4565ms. Final Node test bytes.
17. From WT: step14 and scoped Ruff final both exit0. No further probe changes.
18. `PY artifacts/r15-03/collect_r15.py` exit0:
   7compact evidence files;8probe hashes; exact totals/failure IDs,18Node/17Python
   diagnostic observations, source/schema/existing-oracle diff0 verified. Collector
   exit0 means evidence internally checked, **not Node green**. Large raw initial
   logs/XML remain under unique WT artifacts; compact final logs/diagnostics included.

PowerShell captured each native `$LASTEXITCODE` immediately, wrote UTF8-with-BOM
logs via `Set-Content -Encoding utf8`, and exited with the test code. JSON records
raw bytes SHA256. Git may canonicalize text CRLF to LF; publication staging records
raw-worktree and Git-blob hashes separately, never conflating them.

## Smallest observed distinct additional failure

```js
normalize([
  {data:{feed:{nodes:[{id:'kept',measure:2}]}}},
  {data:null,errors:[{message:'late page unavailable'}]}
], {kind:'table',aggregation:'none',max_points:100})
```

TS actual:2rows, final `{data:null,'errors.0.message':'late page unavailable'}`,
no warnings. Direct failed envelope, async source and explicit selection all reject;
Python rejects all carriers. Six strict RED tests cover three failed-envelope forms
times automatic list/encoded JSON, one proposed root cause GP-ERR-CARRIER.

`sequenceEnvelope` requires a collection under data; `unpack`'s array ordinary-row
branch therefore yields error-only pages without `checkGraphql`. The four additional
RED late-sibling cases are **already-known R10-01F1**, no new ticket or closure.
Automatic pages-wrapper versus column inference is separately N12-known policy,
tested through explicit path only. Ordinary business `errors` field positive guards
against over-broad rejection. No new implicit merge/object-only-node policy.

Not run here: installs, all formats/scales, rendering/browser, both distribution
builds, MCP/Deep Agent, full-release suites/lint/types, final candidate/green CI or
900issue verification. No GitHub issue/PR mutation. Publication receipts follow
actual OWN commit/push/readback; no final signoff implied.
