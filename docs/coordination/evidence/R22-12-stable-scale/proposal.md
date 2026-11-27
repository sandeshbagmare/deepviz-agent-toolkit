# Stable finite SVG scale proposal (not applied at this checkpoint)

Exactsource5e595a8; py225, numericpx232 and tickposition265 need the same fraction.

1. Keep normal finite same-sign/nearby endpoint differences unscaled (preserves adjacent
   large and subnormal X spacing). Before any potentially overflowing opposite-sign
   subtraction, divide value/low/high by a common finite endpoint magnitude. Subtract
   those normalized endpoints, then divide the normalized distance by that finite span.
   Do not normalize all same-sign close endpoints indiscriminately: avoid needless
   cancellation/rounding. Constant numericX remains atleft; empty arrays invoke no Xscale.
2. Keep original Ydomain0..atleast1, tickformat/values/count/order, currentleftmargin,
   dimensions and single sharedpy(0). All bar/line/area/scatter/bubble calls use the same
   stable fraction; numericXticks and marks use the same Xfraction. No valueclamp/null.
3. Reject clearly BEFORE returning output if the emitted coordinate becomes nonfinite,
   or a nonzero Ymeasurement collapses exactly onto emittedzero through floating-point
   coordinate resolution. Subpixel-but-distinct is not a promise of human legibility;
   extreme mixed dynamic range is not an unlimited-IEEE754visibility claim. Original
   literal data must never be changed to rescue successful output.
4. NEWTDDmust demonstrate extreme signedranges/unequalamplitudes/MAX, same-sign adjacent
   numericX, subnormalX, explicit unrepresentable-subnormalY rejection vs truezero,
   empty/constant/allnegative, and all shared line/area/scatter/bubblecallers. Original13
   exact35pxbaroracle and12density observations stay immutable; futureheadadaptersmay
   only change source-pin setup, never expectedgeometry/value/nonoverlap assertions.

#32is independent: R04R23nowapproves fulltext/readable12px+containment+pairwise nonoverlap,
bounded2rowcandidateonlywhenverified, otherwise clear density-infeasibility error before
artifactreturn. No thinning/abbreviation/successwarning. Conservative font support must be
verified/disclosed, not guessed universally. No metricsdependency/newAPI/layoutframework.

This proposal was source-readiness only. Root's later actualR23admission nowactivates the
file-backedscopedrelease AFTER thischeckpoint; implement through NEWREDtests, not by
claiming the prior R17 evidence has turnedGREEN. No newmath/product/browser run yet.
