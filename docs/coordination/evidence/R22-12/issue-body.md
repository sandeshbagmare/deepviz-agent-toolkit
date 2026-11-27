<!-- deepviz-qa-key: R17-12-D1-category-density -->
## Reproduced defect (one layout cause)

The TypeScript native SVG renderer successfully returns a chart at the schema-valid
minimum240x200dimensions, but its category labels overlap. Both standalone SVG and
generated HTML retain all eight correct values/marks while the visible labels are unreadable.
This is not the separate numeric-tick clipping fix and is not a request for a ticket per case.

Related parent scopes:#15,#23. Fresh complete open-issue review found no specific duplicate;
those are broad browser/visual stories, not this bounded defect report.

## Exact source and already-executed QA evidence

- Renderer source:[5e595a8f893955ce34a0e26553bb7bf257ea93ae](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/5e595a8f893955ce34a0e26553bb7bf257ea93ae/packages/deepviz/src/renderers.ts).
- Probe/evidence:[4867f144507436ba5d81cec515a4976723c4a698](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/tests/r17_probes/role12/category-density.test.mjs).
- Actual imported compiled`renderers.js`SHA256:`7640f5147a11e795f3f78564409adae0fb21421bf59f2b95c2d4a9b83c28c4b1`; source SHA256:`be34bcb2be9e44459cb30d145386c3606933bcbdea389ba2fd3fca8d738fac80`.
- Node26.13.1/Chromium159.0.8154.6/Windows. Single strict NEW test command: **exit1,5pass/4fail/0skip**,4141.2145ms. Four failures are genuine final pairwise text-box overlap assertions; four full-size browser controls plus one overlap-oracle self-control pass.
- All eight cases preserve literal category text/order, eight nonempty marks, original1..8values, height ratios/common zero and dimensions. All eight have **0console/page/runtime errors,0external/failed requests and0clipped text boxes**. Containment and correct values do not imply readable category labels.
- Actual PNGs were opened and inspected. Exact[DOM boxes/gaps/mark values](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/browser-cases.jsonl),[summary](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/summary.json),[actual TAP](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/density.tap.log).

## Bounded reproduction

Eight finite records:`{group: 'g0', value:1}`…`{group:'g7', value:8}`.
One additional finite Unicode fixture uses`東京都東部支店1`…`東京都東部支店8` with the
same1..8values, below the existing18-character abbreviation threshold.
Spec:`{kind:'bar',x:'group',y:'value',aggregation:'none',max_points:10,width:240,height:200}`;
engine`svg`. Repeat at`width:960,height:540` as positive control; inspect rawSVGandHTML.

From the immutable probe commit with matching built`dist/`and an already available
Playwright/Chromium (see[probe README](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/tests/r17_probes/role12/README.md)):

```powershell
$env:DEEPVIZ_PLAYWRIGHT_ENTRY = 'C:/path/to/existing/node_modules/playwright/index.mjs'
$env:DEEPVIZ_R17_OUTPUT = 'C:/path/to/NEW/unique/output'
node --test --test-reporter=tap tests/r17_probes/role12/category-density.test.mjs
```

No tests/build/browser/10Mwere replayed to file this issue; these are the recorded R17 results.

| Fixture/dimensions | Plot/slot(px) | Label bbox width(px) | Minimum adjacent gap(px) | Overlapping pairs | Actual SVG screenshot | Actual HTML screenshot |
|---|---:|---:|---:|---:|---|---|
| Ordinary8,240x200 |103/12.875|13.598|-0.723|7|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-240-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-240-html.png)|
| Ordinary8,960x540 |823/102.875|13.598|89.277|0|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-960-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/ordinary-eight-960-html.png)|
| Unicode8,240x200 |103/12.875|92|-79.125|28|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-240-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-240-html.png)|
| Unicode8,960x540 |823/102.875|92|10.875|0|[SVG](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-960-svg.png)|[HTML](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/evidence/R17-12/unicode-eight-960-html.png)|

## Cause, expected outcome and open decision

Current tick selection uses category count(`ceil(n/12)`) without the remaining plot width
or actual category glyph boxes. All eight labels are selected even when each slot is narrower
than its label. This is ONE layout cause across both carriers/fixtures. The existing HTML
accessible-data disclosure does not make the visible chart labels nonoverlapping.

- [ ] For supported finite fixtures, provide readable complete labels without positive-area overlap or clipping in actual SVG+HTML, keeping values/order/mark meaning/usable plot and readable text size.
- [ ] If the requested dimensions truly cannot fit the complete finite labels, follow an **explicitly approved** descriptive density-infeasibility policy rather than successful unreadable output. No silent hiding/truncation/category or value change, arbitrary global schema-minimum expansion or unlimited-Unicode-text promise.
- [ ] Preserve the960positive controls and numeric-axis containment; add strict future fixed-head controls for any approved rejection/no-output path rather than calling the current RED a pass.
- [ ] Obtain genuine non-author fixed-head review/retest before closure. This QA author also authored the separate numeric-margin change; this report is not self-signoff on it.

**Policy/implementation owner:R04; layout-policy and eligible-producer release decision remain OPEN.**
The[bounded stagger/infeasibility proposal](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/4867f144507436ba5d81cec515a4976723c4a698/docs/coordination/reports/R17-12-category-density.md)
is not an approved or implemented fix. Font fallback metrics above are actual Chromium/Windows
measurements, not a universal font guarantee. Leave this genuine bug open until the manager's
evidence-based acceptance/merge/closure process is satisfied. No900-count padding or final
visual/scale/release approval is claimed.
