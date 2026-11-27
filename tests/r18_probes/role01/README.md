# R18-01 bounded npm prompt-copy source-review fixtures

Reviewed commit: `f9c437286c9dfe2245a7d914995d90346e29c233`.
Base: `ca25af486bf443949125df789f5b5fd1fda8bba8`.

These NEW four controls use the committed copy script unchanged in tiny,
reviewer-owned temporary directories. They do not pack, install, fetch from the
network, invoke a provider, run a browser, or rerun numerical/SUM oracles.

Set process-local paths:

- `R18_SOURCE_ROOT`: source checkout/snapshot at the reviewed commit, containing
  `packages/deepviz/scripts/copy-prompts.mjs`, metadata and canonical `prompts/v1`.
- `R18_BASE_ROOT`: base checkout/snapshot containing package.json and src/index.ts.
- `R18_ARTIFACT_ROOT`: NEW empty owned fixture parent. Fixtures are retained there
  for inspection, not recursively cleaned.

Run with Node22+:

    node --test --test-reporter=tap tests/r18_probes/role01/prompt-copy-review.test.mjs

Assertions cover fixed URL names across spaces/#/%/Unicode and unrelated cwd,
ignored environment/argv path inputs, exact literal content and preservation of
unrelated files, real missing-file failure, and additive metadata compatibility.
The missing-file case explicitly records partial/stale outputs after failure;
that is NOT a successful package build. Normal prepack must not bypass build.

The unchanged permanent five tests remain in the reviewed source and should be
run only after an actual build. They are not copied or modified here. Their
canonical-byte assertions are supplemented by independent Git-blob hashes in the
report evidence rather than trusting emitted resources as their own oracle.

Passing these source-fixture checks does not approve a materialized tarball,
rendered chart, final integrated commit, remote CI or whole-system security.