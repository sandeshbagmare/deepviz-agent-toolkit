# R15 role03: paginated GraphQL integrity

Independent NEW public Python/TS probes on source bytes from published
`5340bc69b7203ad7a9166543062482d819f9b705`. No production or existing oracle edits.

With existing dependencies, from this checkout:

```powershell
$env:PYTHONPATH = "$PWD\python\deepviz\src"
python -m pytest tests/r15_probes/role03/test_graphql_pages.py -q --strict-markers --tb=short
node node_modules/typescript/bin/tsc -p packages/deepviz/tsconfig.json
node --test --test-reporter=tap tests/r15_probes/role03/graphql-pages.test.mjs
```

An already-installed compiler in a different checkout can be passed by absolute
path. Compilation writes this checkout's ignored dist only. No installs or browser
are required. Ordinary tests use no mocks, skips, xfails or private implementation
helpers. Fixtures/expected five literal records live beside the tests.

New combinations: nonempty→empty→nonempty supplied pages; repeated real records
and reused cursors; false `hasNextPage` on an early supplied page; mixed edges/nodes;
late nulls/partial errors; nested broadcast and explicit selection ignoring invalid
unselected connections; a missing branch versus a truly empty connection; and
invalid edge/colliding-node/error-only late pages after40 valid rows plus an empty
page. One-shot Python and genuine async TS sources assert exact page consumption
and no request after the failing page, but do NOT assert lifecycle closure.

The4 late-sibling tests are **dedup R10-01 F1**, not4new issues. They strictly
require rejecting ambiguous siblings rather than silently losing fields. Preserve
their RED state until the authorized owner fixes the source. Multiple valid
connections also require a path; tests do not request implicit semantic merging.
Python notices carry counts; TS notices only deduplicate categories. The suite
checks exact Python null/page notice counts without claiming TS exposes them.

Measured checkpoint: Python **73pass0skip**, TS **63pass10fail0skip**. Six TS RED
cases are one additional carrier-bypass finding: error-only late pages with data
null/empty/absent become ordinary rows in automatic arrays/encoded JSON instead of
raising the same GraphQL validation error as direct/async/explicit calls. Four RED
cases are the known sibling family above. Never xfail or weaken these assertions
to manufacture green. `diagnose_graphql_pages.{py,mjs}` capture public observations;
their exit0 only means observations saved. Ordinary business `errors` fields remain
valid records, guarding against an over-broad proposed source fix.

Automatic `{pages: [...]}` versus column inference is an already-reported N12
policy ambiguity; this suite tests its **explicit** path only. Scalar nodes have
no newly invented object-only rejection policy. No remote fetching, full-format/
scale/rendering/MCP/build/package/final-source/CI/900-issue completion is implied.
