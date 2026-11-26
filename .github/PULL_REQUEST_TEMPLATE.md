## Summary

Describe the change and its limits. Do not claim checks that were not run.

## Linked issues

Link the real repository issues this addresses using their full GitHub issue URLs.
Explain the mapping; do not auto-close issues until their acceptance evidence is present.

## Rendered output

Embed an actual image with `![description](https://...)`. Include the input/spec,
renderer, source commit, and links to SVG/HTML/browser artifacts where relevant.
For infrastructure-only changes, explain the scope and attach a representative
verification run/output; discuss any justified image exception with maintainers.

## Correctness explanation

Explain why the observed marks, values, labels, axes, aggregation, and themes are
correct. Describe lossy reduction and any missing optional/browser checks explicitly.

## Verification commands and results

Record exact commands, source commit, pass/fail/skip counts, environment, elapsed
time, and memory methodology for scale results. A file upload is not a visual test.

## Independent evidence

Replace all cells with real evidence. Each row needs a different independently
spawned agent/session, a report link, and the current PR head's full 40-character
commit SHA. These reports are not GitHub human approvals. Never invent signoffs.

| Role | Agent/session ID | Report URL | Tested commit (40 hex) |
| --- | --- | --- | --- |
| reviewer-1 | TODO | TODO | TODO |
| reviewer-2 | TODO | TODO | TODO |
| tester-1 | TODO | TODO | TODO |
| tester-2 | TODO | TODO | TODO |

## Checklist

- [ ] Linked real issues and explained the implemented acceptance criteria.
- [ ] Included an actual rendered image and a correctness explanation.
- [ ] Verified Python/TypeScript schema agreement after contract changes.
- [ ] Ran lint, types, unit, integration, visual and relevant scale/package checks.
- [ ] Recorded failures, skips and unsupported optional environments honestly.
- [ ] Attached two independent reviewer and two independent tester reports.
- [ ] Did not commit tokens, unsafe executable specs, or unrelated user artifacts.

Maintainers: add `evidence-required` when this PR is ready for the evidence gate.
The label is deliberately opt-in during bootstrap; its absence is not an approval
or an exemption from the repository's delivery policy.
