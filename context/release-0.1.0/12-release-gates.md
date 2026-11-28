# Release gates

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

| Gate | Criteria | Sign-off |
|---|---|---|
| G0 Main green | Build, tests, lint, types, reliable CI on Python 3.11-3.13. Current `484ff08ddcae6c36d43ce61de774c00b6c422c88`: 118 tests, Ruff, mypy, wheel/sdist, CI 3/3 pass. | CI-01 + QA-01 + RM-01 |
| G1 Waves complete | Every in-scope V1 item merged and verified-on-main; no open S1/S2. | INT-01/02, QA, RM-01 |
| G2 Code freeze | Only release fixes/docs; all excluded work labelled v1.1. | RM-01 + owner |
| G3 RC | `v0.1.0-rc.N`; full regression + clean install; zero open S1/S2/P0; every feature row Y. | QA lead, TRI-01, CI-01, RM-01 |
| G4 Release | Owner sign-off, release notes merged, `v0.1.0`; remaining branches labeled v1.1 or closed. | Owner + RM-01 + INT-01 |

G0 PASS. G1-G4 not passed. Issue #28 is open/P0; G3 cannot pass under the release rule until resolved or owner-approved amendment.
