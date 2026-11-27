# R23 role12 — author evidence, not independent approval

- Owner: `ses_de5678115ffewUEpZFi8faBW8C`.
- Base: `5e595a8f893955ce34a0e26553bb7bf257ea93ae`.
- Finite-only source commit: `c3ee1edbfc65406cef7fd809f5a6887471d576a5`.
- Density source commit: `342234891c1a34ce6cf4a0d722971c518628815b`.
- Owned branch: `fix/r23-svg-finite-density`.

## Results that must stay separate

| Source slice | Author evidence | Status |
| --- | --- | --- |
| Finite only | 13 new units RED→GREEN; 10 actual SVG/HTML cases; full npm 270 passed, zero skipped | Ready for independent review, not an approval |
| Density | 17 new units pass; 16 actual chart cases plus one clear rejection control pass | **Not merge-ready** |
| Density full npm | 269 passed, **5 failed**, zero skipped | Manager/test-owner policy disposition needed |
| Unchanged original 13 bar assertions | 2 passed through a source-pin setup adapter | Author retest only |
| Unchanged original 12 density assertions | 7 passed, **2 failed** because Unicode 240px now rejects before artifact return | Rejections are not successful chart passes |

The five full-npm failures are the old reduced-stream scatter success case, explicit category-thinning test, and three R11 numeric-margin success cases at 240px (measured aggregate, signed scientific, fixed small negative). No old oracle or expected geometry was changed. Issue 32 remained open; zero GitHub check runs were observed at source handoff. No CI success is inferred.

## Files and integrity

- `summary.json`: result counts, identities, limits and explicit negative status flags.
- `finite-*`, `density-*`: own raw test logs, actual browser input/geometry/PNG output, identity and command receipts. Real PNGs were opened; screenshots supplement, not replace, literal value/mark/ratio assertions.
- `immutable-oracles-v1`: original-assertion adapters with only setup/root/import pin changes, exact hashes and real execution receipts. These are archived executed files, not current-HEAD turnkey scripts: do not weaken assertions to change their status.
- `manifest.json`: hashes of copied local evidence bytes before Git line-ending normalization.
- `git-blob-integrity.json`: actual Git-blob hashes/OIDs for all 145 initial evidence entries; exactly five PowerShell-derived logs differ only by CRLF→LF. Both hashes are recorded. Those logs also retain disclosed OEM glyph mojibake; result names, counts and stack traces remain readable.
- `tool-identity.json`: actual Node 26.13.1, TypeScript 7.0.2, Playwright 1.65.1 and executable hashes. Existing tools were read-only; no installs or shared tool/source modifications occurred.

## Reproduction in the owned isolated source worktree

Use existing installed compiler/Playwright only. Set `R23_PLAYWRIGHT` to the existing `playwright/index.mjs` if it is not locally resolvable; leave `R23_OUTPUT` unset for a new unique temporary output directory. Build the owned source before running:

```text
npm test
npm run typecheck
npm run schema:check
npm pack --dry-run --workspace @deepviz/agent-toolkit
node --test packages/deepviz/test/test_r23_svg_finite_density.test.mjs
node --test tests/browser/r23-svg-finite-density.mjs
```

`npm test` is expected to remain RED in the five disclosed cases until the manager/test owner explicitly resolves the changed full-text/rejection policy versus old success expectations. Do not modify immutable old tests, hide labels, lower readable font size, waive exceptions, or report a rejection as a chart pass to obtain green.

Conservative two-row width estimates are host-scoped, not proof of every Unicode font/shaping environment. Finite arithmetic preserves tested representable ratios/signs/zero; this is not arbitrary-precision rendering or a proof for every IEEE-754 input. No Python/full-toolkit/10M/installed-package-consumer or remote-CI verification was performed in R23. No issue/PR mutation, merge, shared-candidate/default publication, or spawning occurred. R04 owns integration and policy disposition; root owns independent 13/06 dispatch.
