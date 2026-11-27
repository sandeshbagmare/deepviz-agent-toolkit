# Independent helper-null retest

Exact tested source: **7d8ccdce22430a9ddf3a14a9e64bf15b2373ae57**.
The publication branch deliberately does not merge that producer source.

- `run_retest.py`: demands a new clean exact checkout, absent dist/node_modules,
  Gitblob source/config/lock identity and immutable oracle hashes. Builds ONCE
  with explicit read-only Node/TypeScript, then runs unchanged36 cases and the
  unchanged original40 comparisons. No npm install/fullsuite/repeated builds.
- `guard-imports.mjs`: verifies actual public resolution and all connected dist
  bytes BEFORE loading; never redirects imports/transforms code. A real wrong
  MAIN-dist public resolution is rejected before any API executes.
- `probe_tool_schema_refs.py`: BYTE-IDENTICAL original09 oracle, SHA256
  `9b4846c4858ae6f098567245fcce1cc9b4c396ee75cb9315d898bea0bdb1fbde`.
  Runner copies it into the new source at the same root-relative depth and checks
  Python module origins before executing its unchanged code. Original36 test is
  read from the producer commit, SHA256
  `08be1d15661d6bd5bf87bdcec7db11ba3097d9eee294db654369564716e32227`.
- `inspect-small.mjs`: invokes the guarded fresh public SVG helper for two small
  outputs, saves HTML/native SVG, checks values/counts/title/zero axis; optionally
  captures browser output using read-only installed Playwright.
- `capture-existing.mjs`: captures already-generated HTML only. It records DOM,
  CDP layout and console evidence BEFORE viewport screenshots, no helper rerender.

Observed **36pass/0fail/0skip;40/40agreement**. Fresh build0, exact source/tools/
oracles/dist unchanged after. Two opened viewport PNGs: A2/B3, titles,2→2/4 counts,
zero baselines;0 console/page/bootstrap errors and0 external requests.

Honest recovery: initial own harness used a Windows path rather than file URI in
Node `--import`, so it stopped before product tests. `--resume-completed-build`
then verified saved source/tools/oracle/whole-dist hashes and retained the ONE
successful build; only unexecuted gates ran. Initial fullPage screenshot protocol
failure is preserved; one viewport-only capture of stored HTML succeeded. No
fullPage support claim or hidden rerender/rebuild/repeated suite.

```powershell
python -B tests/r22_probes/role05/run_retest.py `
  --source NEW_CLEAN_EXACT_7D_WORKTREE --artifacts NEW_ARTIFACT_DIRECTORY `
  --oracle tests/r22_probes/role05/probe_tool_schema_refs.py `
  --node 'C:/Program Files/nodejs/node.exe' `
  --tsc 'C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript/bin/tsc' `
  --wrong-package 'C:/Users/bagma/deepviz-agent-toolkit/packages/deepviz'
```

See owned report/evidence R22-05 for exact executed commands, failures/recovery,
immutable input hashes and fresh rendered images. This is not fullnpm282/core689,
oldbudget38, Python packaging, installed-consumer, later candidate, first schema
PR, final CI/release/900 acceptance. No production/existing-oracle/API writes.
