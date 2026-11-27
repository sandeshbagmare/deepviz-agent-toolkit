# Independent R18 npm prompt consumer

This non-author consumer tests **source f9c437286c9dfe2245a7d914995d90346e29c233**,
not the older source on the tester branch. It reads expected raw prompt bytes
directly from that immutable Git commit, creates one detached clean worktree,
builds using an existing read-only TypeScript compiler, packs a real tarball, and
manually materializes it into a new consumer's `node_modules`.

**No `npm install`, `npm ci`, dependency installation or shared environment writes.**
Manual materialization is deliberately not evidence of npm installation behavior.
Packing uses `--ignore-scripts` after an explicit build; prepack lifecycle behavior
is outside this test's claims.

Example using already-present Windows tools (change absolute tool paths as needed):

```powershell
& 'C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe' `
  tests/r18_probes/role10/run_consumer.py `
  --repository . `
  --artifact-root C:/Users/bagma/AppData/Local/Temp/opencode/r18-own-consumer `
  --node 'C:/Program Files/nodejs/node.exe' `
  --npm-cli 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' `
  --typescript C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript
```

The runner retains commands, actual exits/stdout/stderr, source/working/tar-member
hashes and an evidence summary. `--resume <existing-own-run-directory>` continues
an interrupted own run after verifying source and materialized tar bytes; it does
not repeat a successful build/pack. Do not use another worker's artifact directory.
Completed evidence can be read without rerunning tests. Fully completed runs are
not intended to be replayed with `--resume` because deliberate-corruption fixture
directories are preserved; use a new unique run only when genuinely necessary.

Checks: 9 real ESM/resource/API consumer tests, exact 13 runtime/16 type exports,
external strict compilation with package-contained declarations, invalid-type
rejection, and four separate corrupted-package controls (changed bytes, missing
resource, invalid outside export, extra runtime export). Fourteen pytest cases
test the harness's safe archive admission, **not** product/browser acceptance.

No browser, CDN, model/provider, full-scale, registry-publishing or release/final-
candidate signoff is implied. Test artifacts remain local; only compact sanitized
reports/hashes are committed. Prior independent MCP RED evidence is unrelated and
must not be hidden by this source-specific packaging result.
