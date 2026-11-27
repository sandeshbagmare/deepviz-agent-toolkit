<!-- deepviz-r22-finite-svg-range -->
## Reproduced defect: accepted finite data becomes invalid SVG geometry

The TypeScript native `svg` renderer accepts two finite values, `-1e308` and
`+1e308`, and preserves both normalized records, but returns a zero-height negative
bar and a positive bar with `y="NaN" height="NaN"`. This is one vertical-scale
overflow defect, not two tickets and not the separate numeric-tick clipping repair.

Related implementation/QA scopes: #15 and #23 (broad stories, not duplicate bug
reports). #32 concerns category-label overlap; #22's finite-SUM comment concerns
normalization/aggregation, not this `aggregation:'none'` coordinate calculation.

## Exact source and immutable evidence

- Reviewed source: [`5e595a8f893955ce34a0e26553bb7bf257ea93ae`, `renderers.ts:225`](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/5e595a8f893955ce34a0e26553bb7bf257ea93ae/packages/deepviz/src/renderers.ts#L225), mark construction at lines252–259.
- The same scale expression is present in [parent `ca25af486bf443949125df789f5b5fd1fda8bba8`](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/ca25af486bf443949125df789f5b5fd1fda8bba8/packages/deepviz/src/renderers.ts). The tick-margin change did **not** introduce it.
- Published independent [strict two-case regression](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/38ce71e50ce59e58dc647417de26e547d5e42d5a/tests/r17_probes/role13/finite-range-regression.mjs), [actual TAP/exit/source receipt](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/38ce71e50ce59e58dc647417de26e547d5e42d5a/docs/coordination/evidence/R17-13/finite-range-regression.json), and [independent review](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/38ce71e50ce59e58dc647417de26e547d5e42d5a/docs/coordination/reports/R17-13-svg-tick-review.md).
- Source `renderers.ts` SHA256: `be34bcb2be9e44459cb30d145386c3606933bcbdea389ba2fd3fca8d738fac80`.
- Actual imported `dist/renderers.js` SHA256: `7640f5147a11e795f3f78564409adae0fb21421bf59f2b95c2d4a9b83c28c4b1`; [clean-source build/import provenance](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/38ce71e50ce59e58dc647417de26e547d5e42d5a/docs/coordination/evidence/R17-13/source-build-unit.json).
- Strict probe SHA256: `a731617b686d7d9b1bdedfdec70c45fea39e9d54f2be266d10be504a705a7202`.

## Minimal reproduction and actual result

Using that exact source and matching built public package:

```js
const data = [
  {group: 'negative', value: -1e308},
  {group: 'positive', value: 1e308},
];
const artifact = render(data, {
  kind: 'bar', x: 'group', y: 'value', aggregation: 'none',
  width: 240, height: 200,
}, 'svg');
const svg = artifact.renderer_spec.spec.svg;
```

The actual strict regression asserts `normalized.records` exactly equals `data`.
It then fails on the emitted SVG (abbreviated attributes, unchanged values):

```xml
<rect class="mark" x="122.75" y="135" width="22" height="0" ...>
  <title>negative: -1e+308</title>
</rect>
<rect class="mark" x="150.25" y="NaN" width="22" height="NaN" ...>
  <title>positive: 1e+308</title>
</rect>
```

| Actual executed case | Result |
|---|---|
| Two values `[-1e200,+1e200]`, same spec | **PASS**: two finite35px-height bars sharing the same zero baseline. |
| Two values `[-1e308,+1e308]`, same spec | **FAIL**: negative height0; positive y/heightNaN, despite accepted unchanged finite records. |

Recorded command: **exit1; 1passed / 1failed / 0skipped; 201.4248ms**. From the
published probe checkout, pointing only to the immutable matching source/build:

```powershell
$env:R17_13_SOURCE = '<clean 5e595a8 checkout with matching built dist>'
node --test --test-reporter=tap tests/r17_probes/role13/finite-range-regression.mjs
```

No tests, compiler, browser, installs or scale runs were repeated to file this bug.
This failure is the recorded R17 run, not an expected-failure waiver. The pair has
two input records and two emitted rect elements; the strict regression proves
their normalized values are unchanged. It did not separately record top-level
artifact warning/count fields, so no warning-free/successful-render claim is made
from those fields. Their truthfulness must be retained in a fix.

## Cause and impact

The unchanged vertical mapping is:

```ts
const py=(value:number)=>pad+h-(value-min)/(max-min)*h;
```

For this accepted domain, `max-min` overflows to Infinity. The negative endpoint's
ratio collapses to0; the positive endpoint computes Infinity/Infinity, producing
NaN. Both quantitative bars disappear even though the input is finite. No
aggregation, large input, CDN, browser-error or label-density condition is needed
to demonstrate the invalid geometry. Other shared scale callers need inspection;
this report does not claim that all kinds/engines were executed at these extremes.

## Acceptance and ownership — OPEN

- [ ] For supported accepted finite inputs, emit only finite valid coordinates,
  two nonzero bars for this pair, equal35px magnitudes/common zero at240x200,
  and correct value ratios/sign/order; retain the1e200 positive control.
- [ ] Preserve exact original data, truthful input/output counts/warnings and
  dimensions. No silent clamp/value substitution, missing marks, warned-null
  workaround or false-success artifact.
- [ ] If a finite domain is intentionally unsupported, choose and document an
  explicit actionable validation/no-successful-artifact policy instead. That is
  an **R04 production/policy decision**, not approval granted by this QA issue.
- [ ] Check connected line/area/scatter/bubble callers, constant/single/empty
  domains and zero/sign/ratio boundaries with strict positive/negative tests;
  retain numeric-label containment and keep #32's density policy separate.
- [ ] Independently retest the actual fixed head, inspect real output with no
  unexpected errors, and satisfy manager-owned PR/CI/default-merge acceptance
  before closure. Do not turn the existing strict RED into an xfail or approval.

**Suggested severity: P2. R04 owns production, release and stable-range policy.**
The eligible role12 stable-scale proposal is not an implemented/approved fix.
The separate narrow tick repair's11unit+29bounded passes (28browser captures,
four opened images) do not approve this range failure or the full product. This
is one independently reproduced bug, not issue-count padding or final signoff.
