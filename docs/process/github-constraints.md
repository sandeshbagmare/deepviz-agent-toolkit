# GitHub constraints and honest blocker handling

Primary sources accessed directly on **2026-11-26**:

1. GitHub Docs, [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), especially *About secondary rate limits*, *Checking the status of your rate limit* and *Exceeding the rate limit*.
2. GitHub Docs, [Approving a pull request with required reviews](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews), especially the note on author self-approval and stale reviews.
3. GitHub Docs, [Best practices for using the REST API](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api), for serial mutation pacing and backoff guidance.

## Content creation is a shared constrained resource

GitHub documents general secondary content-generating limits of **80 requests/minute** and **500/hour**. Some endpoints have lower creation limits; secondary limits can change or apply for undisclosed reasons. Content actions through the web UI, REST and GraphQL all count toward these content limits. Parallel sessions cannot treat the same automation identity as separate budgets. Switching interfaces/accounts/tokens is not an approved workaround.

The current secondary-budget balance is not queryable. Primary `x-ratelimit-*` headers or `GET /rate_limit` do not prove that the secondary content allowance is available.

The seed performed **56 successful mutations**: 19 new labels + 4 milestones + 29 issue creates + 4 epic-body link updates. One subsequent #28 wording update adds the explicit 1,800-mutation lower bound, bringing this process task to **57 successful content mutations**. Mutation operations were serial; seed calls were separated by at least 1.1 seconds in addition to request time. Identity and remote-state reads were additional non-mutation requests. This count does not include other sessions' operations, does not imply all endpoint-specific limits are known, and is not a measurement of the remaining shared allowance. Subsequent documented edits must be added to any operational count.

### The 900-issue requirement

At least **900 genuinely created and closed issues require at least 1,800 create/close mutations**, before comments, labels, milestones, PR actions, evidence updates, discovered fixes and other account activity. Nine hundred creates alone exceed a single documented 500-content-requests hourly allowance. This arithmetic is a scheduling constraint, **not** evidence that GitHub rejected a request, a claim of an exact completion duration, or a permanent ban on creating 900 legitimate issues.

The substantive blocker is that 900 distinct completed, verified deliverables do not currently exist in the evidence ledger. The seed represents 29 genuine scopes; it is not acceptable to duplicate them, split every assertion into a meaningless ticket or close them post hoc merely to inflate a target. See issue #28.

**Observed result:** all seed mutations succeeded. **No HTTP 403/429 rate-limit rejection was observed or claimed by the process agent.** If a real rate-limit failure occurs later, record its sanitized status, time, operation and server retry guidance. Do not relabel a permission/validation error as a rate-limit event.

### Safe operating procedure

1. Coordinate content-generating work through the parent session. Query before creating to avoid duplicates; save the returned issue number immediately.
2. Keep mutating calls serial; pause at least one second between mutations and account for the broader hourly budget. Do not launch bulk issue creation as concurrent jobs.
3. On an uncertain write, read remote state before retrying; issue creation is not transactional.
4. On a real 403/429, inspect sanitized response/error details. Respect `retry-after` when supplied, or primary reset time when primary remaining is zero. GitHub otherwise directs at least a minute's wait for secondary failures, with increasing backoff and bounded retries. Do not continue hammering the API.
5. Preserve a content-operation ledger, but never store credentials, request authorization headers, signed artifact URLs or child-process environments.

## Agent independence is not GitHub account independence

The user requires **two independent reviewer-agent reports and two independent tester-agent reports per merged PR**, plus committed screenshots/SVG/PNG embedded in the PR body. Four genuine reports can be written by independent sessions and posted as artifacts/comments by one coordinator account, provided provenance and exact reviewed/tested SHAs are retained. The implementation author is not an independent reviewer/tester of its own work.

GitHub explicitly disallows a PR author approving their own PR. Multiple sessions posting through the same GitHub identity do not create multiple platform reviewers. A Markdown heading such as “Approved,” an agent report, a comment, or a successful test is not a GitHub `APPROVED` review.

If the request means **two literal GitHub approvals**, two eligible distinct non-author GitHub reviewers must be available with the permissions required by the repository rules. The process agent has neither invited accounts nor changed repository rules. No inability to merge under actual rules is claimed without inspecting the real PR/rules state; issue #29 records the prerequisite and semantic distinction.

Do not bypass protections, impersonate reviewers, invent identities or mark comments as approvals. If the intended requirement is four independent agent reports rather than platform approvals, state that interpretation explicitly in each PR and the final acceptance audit. Changed code can stale prior review evidence; GitHub also documents that enabled stale-review dismissal can invalidate approvals after code-modifying commits.

## Visibility and cost are separate from proof

The parent explicitly reported that the user authorized public visibility and that the repository was changed to PUBLIC. This supersedes the private-by-default background in the original design; this process branch does not edit that design or change visibility. Confirm current repository visibility before final reporting. Public visibility alone proves neither runner availability, a passing Actions run, artifact publication nor a free/unlimited compute entitlement. Those require actual observed workflow state.
