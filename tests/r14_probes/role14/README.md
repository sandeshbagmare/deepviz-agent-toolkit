# R14 advisory coverage probe

Operator-run, bounded metadata-only research for the versions in the existing R10
installed asset inventory. It neither builds/installs/executes downloaded code nor
changes product files or GitHub issues. It writes only a NEW caller-selected output
directory. Run with the existing interpreter/dependencies; do not provision packages.

```text
python -B -I tests/r14_probes/role14/query_advisories.py --authenticate --max-pages 2 --out NEW_OUTPUT
python -B -I -m pytest -q -p no:cacheprovider tests/r14_probes/role14/test_query_controls.py
```

`--authenticate` captures the existing GCM credential in memory, never command-line
arguments/files/logs, and requires authenticated GET/user to be `sandeshbagmare`.
Without it, queries are public/unauthenticated and may hit a lower rate limit.
Redirects are denied. Do not enable shell tracing or debug logging of credentials.

The fixed target list names six inventoried runtime-version combinations and
explicit Plotly canonical/dist aliases (eight package/version query targets). Each
uses ecosystem=npm and affects=package@version, including the scoped @antv/g2 name,
for reviewed, unreviewed and malware records. Six additional package-wide reviewed
queries retain historical ranges rather than mistaking an exact-version zero for
an empty database. API version 2026-03-10 matches the official docs retrieved on
2026-11-27. Dates/API defaults are not future-proof assertions.

Each query has at most two 100-item pages; each response is capped at1MiB. The
maximum main run is61HTTP requests including identity. Pagination may only stay on
api.github.com/advisories with the same exact coverage filters. HTTP, shape, size
or page-cap failures are gaps, not zero-match success. Per-query progress is saved;
no timers, polling, retries or automatic updates. A successful collector exit means
only that those filtered pages were received, **not** that the libraries are safe.

Offline controls reject wrong-scheme/origin/resource cursors, changed filters,
wrong ecosystem/package responses and unreported HTTP/page-cap gaps. Real extra
historical-version server controls and upstream metadata/policy source reads are
preserved in the companion evidence/report; no runtime/exploit code executed.

Coverage is source/date-specific: immutable3aa→5340 relevant-code/config/lock/schema
byte continuity is recorded in source-continuity.json. It does not certify a moving
producer tree, future CDN bytes/SDK versions, transitive packages, unpublished or
unindexed advisories, alternative package names or ChartSpec exploit reachability.
In particular, official Plotly4.3 release/PR8168 describes a security-related fix
without an affected-version range; zero exact-version query results do not resolve
whether embeddedJS3.7 is affected. Its old policy-linked advisory page redirects to
a Chart Studio shutdown page. Preserve those gaps instead of claiming all-safe.
