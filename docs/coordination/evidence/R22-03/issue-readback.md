<!-- deepviz-r22-graphql-error-carrier -->
## Reproduced defect: failed GraphQL page becomes a data row

The TypeScript public normalizer silently succeeds when a supplied GraphQL
page array or its encoded JSON contains an error-only response after valid data.
Instead of rejecting the failed page, it flattens the transport error into an
invented record, increments the count, and emits **no warning**.

One cause, not six tickets: `data:null`, absent `data`, and `data:{}` each fail
through automatic array and encoded-JSON carriers. Direct-envelope, real async
stream, explicit-path, and Python controls already reject these same envelopes.
This does **not** report the separate known unexpected-connection-sibling loss.

Related parent: #7 (nested/GraphQL pages); related contract: #14.
Fresh complete open-issue/body/comment review found no specific duplicate.
Those broad feature stories are not the same bounded defect report.

## Exact source and already-executed independent QA

- Product checkpoint: **5340bc69b7203ad7a9166543062482d819f9b705**;
  [TypeScript source](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/5340bc69b7203ad7a9166543062482d819f9b705/packages/deepviz/src/normalize.ts#L95-L118).
- Permanent independent probes/evidence: **648f399e2745aa1f62319cddb15fb0095ab0a34c**;
  [strict Node suite](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/648f399e2745aa1f62319cddb15fb0095ab0a34c/tests/r15_probes/role03/graphql-pages.test.mjs),
  [Python controls](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/648f399e2745aa1f62319cddb15fb0095ab0a34c/tests/r15_probes/role03/test_graphql_pages.py),
  [actual diagnostic](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/648f399e2745aa1f62319cddb15fb0095ab0a34c/docs/coordination/evidence/R15-03/node-carrier-diagnostic.json#L190-L229),
  [commands/results/import hashes](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/648f399e2745aa1f62319cddb15fb0095ab0a34c/docs/coordination/evidence/R15-03/verification.json).
- Loaded source SHA256:
  `d1b45d2a55dfd05361184a57da952a0da735e9b6d72c2491f908ef27bda22371`;
  compiled `normalize.js` SHA256:
  `adb0493123fd478567212e76e2c6e52c828aeaa9eb5425c219b5b1a576689612`.
- Windows / Nodev26.13.1 / Python3.12.16. Independent isolated source was byte-equal
  to checkpoint5340, not a sibling dirty build. No mocks, xfails, sampling or skips.

Already-executed strict command (not newly rerun during bug filing):

```powershell
node --test --test-reporter=tap tests/r15_probes/role03/graphql-pages.test.mjs
```

Actual: **73tests /63PASS /10FAIL /0skip /0cancel**, exit1,469.4565ms from an
external-CWD portability run. **Six** failures are this error-carrier cause;
the other **four** are explicitly deduplicated known F1 sibling-loss tests and
must not inflate this bug. Same-source Python controls: **73PASS /0skip**,
exit0,0.81s. [Exact failed IDs and raw logs](https://github.com/sandeshbagmare/deepviz-agent-toolkit/tree/648f399e2745aa1f62319cddb15fb0095ab0a34c/docs/coordination/evidence/R15-03).

## Minimal two-page literal (no fixture builder)

From the repository root after building that pinned package:

```js
import {normalize} from './packages/deepviz/dist/index.js';
const pages = [
  {data: {feed: {nodes: [{id: 'kept', measure: 2}]}}},
  {data: null, errors: [{message: 'late page unavailable'}]}
];
normalize(pages, {kind: 'table', aggregation: 'none', max_points: 100});
// Also reproduces with JSON.stringify(pages) and format: 'json'.
```

Actual saved output for the literal array:

```json
{
  "records": [
    {"id": "kept", "measure": 2},
    {"data": null, "errors.0.message": "late page unavailable"}
  ],
  "input_count": 2,
  "warnings": [],
  "strategy": "none"
}
```

Larger strict fixtures keep40valid records, an empty intermediate page and then
the failed page: actual41records/41input_count/no warnings. The empty page is
not the termination point; the error envelope is wrongly treated as an observation.

## Expected behavior / fix acceptance

- Reject error-only GraphQL pages concisely and consistently across supplied
  arrays, encoded JSON, direct envelopes, async streams and explicit paths;
  never return a successful prefix or invented error row. Existing direct/stream
  controls use `GraphQL response contains errors and no data`.
- Make all **six** permanent error-carrier negatives pass without xfail/skipping
  or weakening count/value/type/order/early-stop assertions. Keep known F1 sibling
  regressions separate, strict, and independently tracked.
- Preserve ordinary business records containing an `errors` field: the existing
  sync+async positive produces `{'id':'business-record','errors.0.message':...}`.
  Do not reject all fields named `errors` indiscriminately.
- Preserve partial-error warnings with usable data, null-node warning disclosure,
  empty-page continuation, valid explicit selection, and exact ordered repeated
  values/counts (five records include four legitimate equal repeated nodes).
- Source-flow diagnosis: `sequenceEnvelope` requires a data collection;
  `unpack`'s array ordinary-row branch therefore bypasses `checkGraphql` for these
  failed envelopes. Reuse the existing validation semantics without inventing
  implicit connection merging or an object-only node policy.

Source ownership remains16/R04; QA has not changed implementation or existing
oracles. Proposed priorityP1 because failed input silently becomes fabricated
data, subject to maintainer triage. Leave open until a reviewed fix and fresh
independent candidate retest; this report is not a fix, greenCI, merge, closure
or final-release signoff. No test/build/browser rerun was needed to file the bug.
