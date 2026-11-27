# Current-source packed-consumer probe

Run from an **own isolated source worktree**, never MAIN. Output must be a new
directory outside every Git/npm workspace. The harness preserves every output
and refuses to overwrite an earlier run. It never changes product manifests,
lockfiles or source; `--install` installs only the declared public dependencies
in that source worktree, with dependency lifecycle scripts disabled.

```powershell
node tests/r10_probes/role08/verify-packed-consumer.mjs --source "$PWD" --output "C:\approved-temp\unique-run" --expected-source 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab --install
```

On systems where the npm JS entry is not next to Node, add
`--npm-cli /absolute/path/to/npm/bin/npm-cli.js`. Omit `--install` only if this
isolated source already has its own installed dependencies. Node>=22, the
project-declared development dependencies, system `git`/`tar` and an existing
Playwright Chromium are required. Missing tools are retained blockers, not skips
or silent passes. No third-party browser/package downloads are hidden by the probe.

The runner records command argv/cwd/exits, exact product-source byte hashes,
actual tar members and tarball SHA256, installed bytes and isolated dependency
asset versions/hashes. It runs build/typecheck/npm tests/schema/package-check,
dry-run **and real pack**, then installs that tarball in a materialized external
consumer with offline npm and no workspace/dependency fallback. Types are checked
under strict NodeNext with `skipLibCheck:false` and no ambient source types.

`consumer.test.mjs` independently requires both canonical versioned prompt files
inside the installed tarball (allowed prefix, fixed `prompts/v1/` suffix), with
bytes equal to the source prompts. Their absence is intentional strict RED on
checkpoint3aa521a5, **not** waived by working runtime exports. Do not weaken this
test or promote a partly green run to full distribution acceptance.

Real Chromium imports the installed ESM/JSON modules and loads HTML from each of
the five packed APIs with local declared development bundles. Native SVG bar
heights2/5 and a common baseline are asserted; all cases require real SVG/canvas,
exact normalized values and zero console/page/external-request errors. Open the
saved PNGs to inspect the other engines' visible values/labels before claiming
their bounded visual correctness. Default CDN reachability, Node/browser version
matrices, dashboards, security audits and10M performance are outside this probe.

`summary.json` reports each gate separately and exits nonzero on any failure.
This branch is an independent test/evidence deliverable, not a production fix,
final release or substitute for independent reviewers, remote CI or R04's issue
disposition. Existing issue25 tracks npm clean-consumer exports/types; R04 owns
the additional canonical prompt packaging dependency and candidate integration.
