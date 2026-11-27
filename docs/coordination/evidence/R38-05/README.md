# R38-05 — independent Python mean acceptance evidence

PRODUCT pin: `c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19` ONLY.
Owner actual session: `ses_de567830effe0E5yIwQgDACLMD`.

One fresh execution: **76 passed / 0 failed / 0 skipped**, pytest/process exit0,
2026-11-27T17:18:09.427801Z–17:18:14.192977Z; pytest2.26s.
This is not approval of later546c, an integrated package, actualmain, or a release.

## Actual coverage and non-coverage

- 21 unchanged producer mean controls selected by their two exact function names.
  The five ownership controls in that same file were not selected or replayed.
- 55 NEW independent controls:16 literal bit-pattern oracles ×records/one-pass;
  six finite standard-library Fraction reference grids ×records/one-pass;
  positive/negative weighted-other/collision cases; invalid/null/nonfinite/missing
  denominator cases; empty/global/heatmap mapping; four genuine budget negatives.
- Every public normalize call was checked BEFORE its first instruction using a
  same-process Python profile hook:76 consumers,76 independently recorded origins.
  All9 Python source files, config, schema, unchanged producer file (12 Git blobs),
  NEW probe/wrapper bytes and loaded module/function/code origins were checked.
- No editable .pth processing (`-B -S` plus explicit existing site-packages),
  no environment mutation, plugin autoload, source/cap/oracle edits or installs.
- Original caller records/spec are checked for mutation. Expected values come
  from literals and standard-library Fraction, never production output/helpers.
- Real public budget negatives yielded exactly0(invalidpointbudget),33(lateUTF8
  cell),1(widerecord),254(real16MiB retained-state rejection from advertised300).
  No constant monkeypatch, large-scale benchmark, RSS claim or source alteration.
- No SUM-accuracy/scalar/GraphQL/formats/Arrow matrix, fullsuite,10M, npm,
  build, browser, MCP, CI or currentdefault acceptance was run or implied.

## Receipts

`command.json` records exact child argv/CWD/exits/UTC/raw-log hashes.
`pytest-command.json` records exact SAMEprocess pytest argv and0envmutations.
`identity-{before,after}.json` bind raw Git-LF bytes/imports/executed probe hashes.
`collected.json`, `mean.xml`, `case-results.json`,
`before-consumer-origins.json` and `summary.json` record all76 actual cases.
`verification.json` independently audits the saved receipts (no test rerun),
including all228 original setup/call/teardown reports and four negative controls.
`quality.json` retains the initial OWN mypy1(optional module filename), then
corrected AST/Ruff/mypy0 on the two NEW files; no product error is invented.
Three readonly file-discovery errors are retained in the detailed report.

The full228 phase reports/raw stdout remain in the unique local command/gate
directory named in the receipts. Published `case-results.json` contains76call
reports only; all228 phase reports were verified PASS before export.
`stdout.txt` normalizes CRCRLF/CRLF→LF; both raw/published hashes and byte counts
are explicit in `verification.json`. All other initial14 compact files were
copied byte-exact. Index-stage Git-LF/raw differences, if any, are explicitly
recorded by the publication manifest; never silently treat raw and Git as equal.

## Reproduce on another permitted machine

Create a fresh detached checkout of the exact PRODUCT pin, preserve all existing
worktrees, and use an already provisioned Python/pytest/pydantic environment:

```text
git worktree add --detach <new-source-directory> c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19
<python> -B -S tests/r38_probes/role05/run_mean_acceptance.py --source <new-source-directory> --site-packages <existing-site-packages> --artifacts <new-evidence-directory>
```

The wrapper requires clean source, exact raw Git blobs/no stale source bytecode,
unchanged producer tests, the two NEW probe files together, and a new artifact
directory. A checkout with CRLF-converted product files fails closed before
product import. No installation or source changes are part of this recipe.

R04 must apply any relevant independent review/integration gates to the actual
future dependency-complete package head; this pin-specific result is one input,
not a borrowed final-head approval. Root owns admitted useful SAME-ID refill.
