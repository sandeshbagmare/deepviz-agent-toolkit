# Pull request and issue inventory (initial snapshot)

This is the original inventory snapshot at `484ff08...`; use `18-current-state-audit.md` and the synchronized YAML root fields for current PR/issue state. The original #28 criterion is superseded by the caller decision recorded in plan v1.1.

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

| PR | Title | Head -> base | State | Draft | CI | Review | Mergeable | Size | Linked open issue body references | Disposition / justification |
|---:|---|---|---|:---:|---|---|---|---:|---|---|
| #38 | Align dashboard JSON Schema with the runtime contract | `fix/r42-dashboard-schema-parity` -> `main` | MERGED | N | Numeric contract / Python 3.11=SUCCESS; Numeric contract / Python 3.12=SUCCESS; Numeric contract / Python 3.13=SUCCESS | none recorded | UNKNOWN | +299/-1; 4 paths | #5 | V1-MERGE - Already merged; three Python 3.11-3.13 checks passed. |
| #33 | fix: reject numeric string and boolean coercion in ChartSpec (#30) | `fix/r22-strict-numeric-contract` -> `main` | MERGED | N | Numeric contract / Python 3.11=SUCCESS; Numeric contract / Python 3.11=SUCCESS; Numeric contract / Python 3.12=SUCCESS; Numeric contract / Python 3.12=SUCCESS; Numeric contract / Python 3.13=SUCCESS; Numeric contract / Python 3.13=SUCCESS | none recorded | UNKNOWN | +773/-0; 9 paths | #30 | V1-MERGE - Already merged; six Python contract checks passed. |
| #31 | Integrate Python-first DeepViz toolkit and evidence-backed verification | `release/candidate` -> `main` | OPEN | Y | Python 3.11 lint, types, unit and integration=FAILURE; evidence=SUCCESS; Python 3.12 lint, types, unit and integration=FAILURE; Python 3.13 lint, types, unit and integration=FAILURE; npm build, types and tests (Node 24)=SUCCESS; Raster visual regression (semantic pixel comparison)=SUCCESS; One-pass scale 10 records=SUCCESS; One-pass scale 1000 records=SUCCESS; One-pass scale 100000 records=SUCCESS; One-pass scale 1000000 records=SUCCESS; One-pass scale 10000000 records=SUCCESS; Python and npm distribution checks (no publishing)=SUCCESS | none recorded | UNKNOWN | +36025/-3; 324 paths | #4, #8, #20, #21, #22, #23, #24, #25, #26, #27, #28, #29, #30, #32, #36 | CLOSE-SUPERSEDED - 324 paths, +36,025/-3, three failing Python checks, no review; replace with focused PRs. |

## Mapping and verification limits

- **62 branches have no PR**; all are listed in file 01/YAML. No missing head branch, duplicate-head PR, or non-default base was found.
- PR #31 open comments/reviews were checked by REST (0/0). `gh pr view --comments` was unavailable because token lacks GraphQL discussion scope; `gh pr checks 31` returned 12 jobs shown above.

## Open issues

GitHub returned 35 open issues; all issue numbers, titles, labels, bodies, assignees and inferred links to PR body/commit-subject references are in YAML. Important open items: #28 P0 900-issue criterion; #20/#21/#23/#26 CI/security/visual/review; #30 P0 numeric coercion despite merged fix #33; #32 SVG label layout; #35-#37 browser/Plotly/SVG bugs. No issue was changed.
