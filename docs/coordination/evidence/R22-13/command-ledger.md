# R22-13 executed command / HTTP ledger

OWN cwd: `C:/Users/bagma/AppData/Local/Temp/opencode/r10-13-ci-negative-controls-ses_de56780caffekQ9gdZ58EgQwb5`.
Python used read-only: `C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`.
No product tests/build/browser/scale commands or environment changes ran in R22.

| Actual command | Exit / observed result |
|---|---|
| `git status --short --branch` | 0; OWN branch clean at start, `agents/r10-13-ci-negative-controls`. |
| `git log -5 --oneline` | 0; f4c6a8a,38ce71e,1317dd1,2e2b639,dedb41f. |
| `git show --no-patch --format="%H%n%P%n%s" 5e595a8f893955ce34a0e26553bb7bf257ea93ae` | 0; parentca25af486bf443949125df789f5b5fd1fda8bba8. |
| `python -` (initial read-only metadata collector) | 1; own text-spelling assertion after matching source hashes, before any API/JSON write. Not a product failure. |
| `python -` (bounded saved-text/expression diagnostic) | 0; parent/current expression both occur once; actual report says `1passed/1failed`. |
| `python -` (corrected read-only metadata collector) | 0; preflight/immutable JSONs, preserved source/build/probe hashes. |
| `python -` (complete open-issue/body/comment inventory) | 0; 34GET200,31issues+1PRentry, marker0. |
| `python -` (complete prewrite inventory/comment refresh) | 0; 37GET200,34issues+2PRentries, marker0; new34/35/36 bodies read and unrelated. |
| `python -` (guarded single issue create + immediate readback) | 0;4GET200+ONEPOST201; issue37 OPEN, exactfullbody/title/number/URL/marker. |
| `git ls-remote --heads origin refs/heads/agents/r10-13-ci-negative-controls` | 0; prepublicationactualremote f4c6a8a06b863491e3623273163e9110e8c27ecf. |
| `python -` (saved-artifact/owned-scope integrity) | 0;7existingJSONparse,75GET200+1POST201 receipts, bodyhashes equal, savedsource/probehashes equal, sourceclean/protecteddiff0, credentialpatterns0. These are not product test totals. |

The `python -` commands received host-authored stdin, not model-authored chart
code or user data execution. Full exact HTTP methods/paths/statuses/UTC are in
`open-inventory.json`, `prepost-refresh.json` and `issue-readback.json`; they do
not contain auth headers, credential output or tokens.

## Authorized HTTP sequence

- Authenticated `GET /user`, expectedlogin`sandeshbagmare`; `GET /repos/sandeshbagmare/deepviz-agent-toolkit`, expectedrepo/pushrights. GCM `credential fill` stdout/stderr captured only in memory and never printed/stored. Redirects disabled;403/429/ambiguitywouldSTOP, no retry/account substitution.
- Complete paginated `GET /repos/sandeshbagmare/deepviz-agent-toolkit/issues?state=open&sort=created&direction=asc&per_page=100&page=1` (no nextpage in these snapshots), with PRs excluded from issuecounts.
- Complete `GET /repos/sandeshbagmare/deepviz-agent-toolkit/issues/{number}/comments?per_page=100&page=1` for allopenissues; no nextpage in these snapshots. All fullbodies/comments read, not search snippets.
- Write-intent and exactdraftSHA saved BEFORE mutation. Final GETlisting matched the reviewedset. **ONE `POST /repos/sandeshbagmare/deepviz-agent-toolkit/issues`201**, ONLY title+body; **immediate `GET /repos/sandeshbagmare/deepviz-agent-toolkit/issues/37`200**, exactbodyhash/number/title/URL/marker/OPENverified.

**ONE finite-bug grant consumed.** Restart recovery is GETverify/reuse, never
repeatPOST. No API source/default/PR/closure/label/assignee mutation. R04 owns
production policy/fix/review/test/merge/closure. Publication commands/results are
saved in the owned report after their actual execution, not preclaimed here.
