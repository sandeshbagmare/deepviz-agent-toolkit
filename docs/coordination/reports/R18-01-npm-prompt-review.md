# R18-01 independent npm prompt-distribution source review

**What this change does:** it copies the three canonical v1 Markdown prompts into
`dist/prompts/v1` during build and exposes three explicit raw-resource subpaths.
It adds no runtime prompt-reader API and does not change chart code.

Reviewer: `ses_de5678335ffeI7xJrod5l25Q0Q`, non-author role01.
Reviewed commit: **`f9c437286c9dfe2245a7d914995d90346e29c233`**.
Comparison base: **`ca25af486bf443949125df789f5b5fd1fda8bba8`**.
Own evidence branch: `agents/r10-01-correctness-regressions`, starting clean
`dd73e9d498295567e5b90c9d396acfa748e02751`; neither moving MAIN nor the producer's
later evidence commit was substituted for the reviewed source.

## Findings / disposition

**No concrete must-fix finding in these four changed paths.** This is a scoped
independent source review, not approval of the final integrated candidate,
materialized npm package, remote CI, merge or release.

The full four-path diff and connected build/callers were read:

- `packages/deepviz/scripts/copy-prompts.mjs:3-7`: source/destination are fixed
  file URLs relative to `import.meta.url`; the loop accepts only literal
  `README.md`, `system.md`, `request.md`. No argv/env/model/ChartSpec path,
  interpolation, URL ingestion, code evaluation or recursive cleanup is added.
  `copyFile` overwrites only the three generated destination names by design.
  A genuine fixture with spaces, `#`, `%`, Unicode, unrelated cwd, traversal/URL
  argv and misleading env values copies the expected bytes twice and preserves
  outside/index/user-note sentinels. This is a trusted build checkout, not a
  symlink-resistant filesystem sandbox or a new MCP filesystem interface.
- `packages/deepviz/package.json:9-19`: prior root/types/schema exports, version,
  files/main/types/engines/sideEffects and metadata remain unchanged. Exactly
  three raw `.md` subpaths are additive. The existing `files:["dist",...]`
  includes generated prompt assets; installed-consumer verification belongs to
  role10. No wildcard prompt path or invented JavaScript reader is exposed.
  Root build delegates to the workspace; prepack delegates to build. TypeScript
  must succeed before copy runs because the commands use `&&`.
- `packages/deepviz/README.md:80-97`: the Node22+ ESM read example resolves a raw
  resource, not a JS import/template execution. I executed its resolution/read
  pattern against the built package's self-reference:4582 exact system bytes.
  Runtime still exports the same13 public JS symbols, not `read_prompt` or
  `readPrompt`. This is NOT evidence of a tarball-installed consumer.
- `packages/deepviz/test/test_r11_packaged_prompts.test.mjs:13-40`: unchanged
  permanent five tests cover all three bytes/exports/repeat copies and preservation
  of built code. I built exact source and ran these tests, not merely accepted
  the author's claimed result. Independent Git-blob hashes supplement their
  source-versus-emitted-byte checks.

### Failure behavior, explicitly checked

With canonical `system.md` removed from an OWN fixture, unchanged copy exits1
with `ENOENT` naming `system.md`. The earlier README is already copied and later
assets remain stale. The operation is **not atomic**; the test records this,
not a successful build. Normal build/prepack propagates the failure and must not
be bypassed with `--ignore-scripts` as an ordinary publication workflow. No
unrelated files are removed. This expected fail-fast behavior is not promoted
into a fabricated defect or a claim that failed-build output is safe to ship.

### Canonical policy trust and versions

`prompts/v1/README.md:3-26` identifies ordinary source files, Python's separate
installed loader, single canonical authority and rebuild/version rules.
`system.md:4-19,30-65` treats dataset/tool text as untrusted, rejects code and
traversal, requires real counts/warnings and discloses chart/scale limitations.
`request.md:3-13` is a user-input template with host-approved reference/data,
not executable syntax. Npm's new README explicitly says prompting is not a
sandbox. These unchanged canonical instructions are copied, not executed or
expanded into a purported new npm tool/reader contract.

## Independent execution and source evidence

Materialized **42 files directly from committed Git blobs**, binary writes,
in a NEW OWN ignored snapshot. No sibling dirty sources or dist were used.
All42 source/config hashes and22 independently built dist hashes were verified
after execution. Twelve connected files, including all runtime TS, canonical
prompts, tsconfig and `.gitattributes` LF policy, are byte-identical to base.
Resource-byte determinism is verified; no tarball-byte determinism is claimed.

| Command/check | Actual independent result |
|---|---|
| `node <installed npm-cli.js> run build` in exact snapshot | exit0 |
| `node --test --test-reporter=tap packages/deepviz/test/test_r11_packaged_prompts.test.mjs` | exit0, **5pass/0fail/0skip**,239.019ms |
| NEW `node --test --test-reporter=tap tests/r18_probes/role01/prompt-copy-review.test.mjs` | exit0, **4pass/0fail/0skip**,2502.3726ms |
| `node <installed npm-cli.js> run typecheck` | exit0 |
| Node self-reference ESM resolve/read/public exports | exit0,4582B/13exports/no reader API |
| `node --check tests/r18_probes/role01/prompt-copy-review.test.mjs` | exit0 |

Environment: Node26.13.1, npm11.20.0, existing TypeScript7.0.2. Shared toolchain
and environment were read-only; no installs were run. Exact argv, cwd, exits,
raw logs and SHA256s live in `docs/coordination/evidence/R18-01/`, notably
`initial-verification.json`, `independent-verification.json`,
`connected-checks.json`, `compatibility-and-final-source.json` and
`source-identity.json`; `reviewed.diff` is the actual ca25→f9c four-path diff.

Canonical Git blob / emitted bytes (same exact LF bytes, no CR):

| Asset | Bytes | SHA256 |
|---|---:|---|
| README.md |1787|`324cb7f88211424f577327268f36506c8c27d1793528441458e2caba83ee0bbd`|
| system.md |4582|`b11e691e8f5d89bc2fd726d284702d6675c57c1a32ec0947ec5902040fdbaba0`|
| request.md |761|`845be71cb3141d084f036472a1c5a19670be28c16bf73c4a599a3df9d534c6f2`|

Copy script SHA256:`2e29160390a79c62b13c20992ef88c639126a8bad9bee80b327d5b81e6aa06bd`.
Unmodified permanent five-test source SHA256:
`ec5fb98f80fc2adfe8b3a40fecc82007d4b90f173cc6d2343328d7ce57abb234`.
Small readable exact source excerpts and their commit/hash identity are under
`evidence/R18-01/reviewed-source/`; these are evidence, not production edits.

## Harness correction / limitations

First NEW fixture execution was **3failed/1passed** because I accidentally used
U+0016 in a Windows fixture-directory prefix. The copy script never ran in those
three cases; they are not product RED. Saved original raw failure log/summary as
`*.harness-failure`; corrected only my NEW fixture prefix to `\u00e9`, then all
four checks ran and passed unchanged production source. No source or existing
oracle was weakened. `checkpoint-history.md` preserves pre-work/progress notes.

Not run: npm ci/install, full npm suite, actual pack/dry-run/materialized consumer
(role10's distinct lane), browsers/CDNs/providers, Python gates, scale/RSS,
whole-system security or fresh remote CI. Existing author's13consumer/6browser
results are not borrowed. The reviewer-owned fixture checks are bounded and do
not measure process memory or LLM adherence to policy.

R13 SUM F1 remains **OPEN P2/incomplete inherited repair**, explicitly dispositioned
by R04 in `tasks/R17-normalizer-producer-succession.md`. Its four strict RED cases
were preserved; SUM65/61 suites were NOT rerun for this unrelated assignment.
No production/existing oracle/shared source/other note/GitHub issue/PR edits or
workers spawned. The900 criterion and final-candidate acceptance remain unmet.

**Next action:** R04 reads this source-specific report together with role10's
actual materialized-consumer result before integrating the four-path fix; rerun
appropriate gates on its exact frozen integration commit.

## Actual scoped publication

Independent review/probes/evidence commit
**070ec64bfda5a1b578c8fa0c0486b8eb69c87831** was non-force pushed to the OWN
`agents/r10-01-correctness-regressions` branch at14:52:49UTC. Push exit0 and
immediate actual remote-SHA readback exit0 confirmed that exact SHA. Fresh safe
authenticated GET/user200 verified expected sandeshbagmare; credential remained
in process memory, not args/logs/files. `evidence/R18-01/publication.json` is
the sanitized actual receipt. This publishes a scoped review, not candidate
approval or packed-consumer verification. A small actual-receipt-only checkpoint
follows; its finaltip will be recorded in MAIN only after actual push/readback.