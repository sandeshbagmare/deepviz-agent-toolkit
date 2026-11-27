# Category-density strict RED, not a product pass

Source `5e595a8f893955ce34a0e26553bb7bf257ea93ae`; existing compiled renderer reused
by exact SHA256. No source edits, installs, rebuild, fullsuite or10Mreplay.

Single NEW command: `node --test --test-reporter=tap tests/r17_probes/role12/category-density.test.mjs`
→ **exit1,5pass/4fail/0skip**,4141.2145ms. Five passes are four fullsize real browser
positives plus one overlap-oracle self-control, not five fixed minimum-width cases.

| Full labels, eight1..8observations | Plot/slot(px) | Label bbox(px) | Minimum gap(px) | Overlapping pairs |
|---|---:|---:|---:|---:|
| Ordinary`g0`…`g7`,240x200 |103/12.875|13.598|-0.723|7|
| Ordinary`g0`…`g7`,960x540 |823/102.875|13.598|89.277|0|
| Unicode branch names,240x200 |103/12.875|92|-79.125|28|
| Unicode branch names,960x540 |823/102.875|92|10.875|0|

Standalone SVG and HTML agree for all four rows. All eight cases retain complete literal
labels/order,8nonempty correct-value bars/height ratios/common zero and correct dimensions.
No text is clipped and no console/page/runtime/network errors occur; minimum-width visible
labels nevertheless overlap. All8included actual screenshots were opened, not merely counted.

`browser-cases.jsonl` contains exact boxes/marks/gaps/pair intersections/PNG/input hashes.
`summary.json` ties the actual source/build/probe/tool versions/command to results. The log
is normalized UTF8/LF from actual UTF16LE/BOM PowerShell TAP; both hashes are disclosed.

One finding only: count-based tick selection ignores available plot width and actual glyph
boxes. `../../reports/R17-12-category-density.md` proposes measured-fit layout, a bounded
two-row ordinary-label candidate and explicit infeasibility when fulltext cannot fit;
none is implemented/approved. R04 must decide/release an eligible producer. No silent
truncation/hiding/value change/global schema minimum expansion or universal Unicode promise.

This probe author also authored the earlier numeric-margin fix, so this is NOT independent
review of that fix. Role13's independent work stays separate. No issue/PR closure or final
visual/scale/release approval is implied.
