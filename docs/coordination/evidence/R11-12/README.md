# R11-12: numeric tick clipping RED → GREEN

Base: `ca25af486bf443949125df789f5b5fd1fda8bba8`; own branch `agents/r11-12-svg-tick-margin`.
Producer: `ses_de5678115ffewUEpZFi8faBW8C`; not an independent reviewer.

The original native SVG right-anchored its numeric ticks at x57, clipping `6.250e+12` in
both standalone SVG and generated HTML. The scoped fix sets explicit 12px monospace axis
metrics and reserves `max(65, 32 + 8 * longestFormattedTick.length)` left space. Numeric
strings/data/chart dimensions/vertical scale/zero baseline remain unchanged. Other margins
remain65px; horizontal plot space adjusts to fit labels. Pie geometry remains unchanged.

| Gate | RED | GREEN |
|---|---|---|
| New permanent unit tests | 1 pass,10 fail,0 skip | 11 pass,0 fail,0 skip |
| Real Chromium SVG + HTML | 8 pass,12 containment failures,0 skip | 20 pass,0 fail,0 skip |
| Full npm (includes new unit tests) | not rerun pre-fix | 257 pass,0 fail,0 skip |
| Build/typecheck/schema/pack dry-run | original build0 | all exit0 |

Five eight-row fixtures cover the exact previously measured grouped values, positive,
negative, signed scientific and long fixed-small-negative ticks at960x540and240x200.
All actual browser cases retain eight nonempty value-correct marks, exact literal strings,
relative heights/common zero and zero console/page/runtime/network errors. Real local
artifacts are loaded offline, not fake assets. Four included screenshots were actually opened.

**Remaining visual limitation:** at minimum240pxwidth the category ticks crowd/overlap.
Containment is not a category non-overlap gate or all-kind visual approval. This is a
numeric clipping correction only; issue23 is not closed. Source-owner integration needs
genuine non-author review/testing and final-source evidence.

`red-green-summary.json` records source/build/test hashes, actual numeric DOM boxes,
all40browser case output hashes and raw-log fingerprints. Exact commands and exclusions
are in `../../reports/R11-12-svg-tick-margin.md`. No10M rerun, new memory claim, npmci,
clean-consumer approval, remote CI, Python gate or final release approval is implied.
