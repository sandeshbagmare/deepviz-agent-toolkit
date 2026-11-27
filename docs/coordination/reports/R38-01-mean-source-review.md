# R38-01 independent Python mean SOURCE review

What this change does: replace scaled floating-point mean state with one budgeted exact integer numerator. It calculates the mean once from the numerator and valid-observation count, avoiding intermediate float overflow and subnormal double rounding.

Reviewed source: **c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19**.
Parent79232fb2f402bf21d455fbc021f1c238d19abe80; P1 ancestor5ba860305dcc86ac2f95f01705b984d2b40f2799.
Non-author ses_de5678335ffeI7xJrod5l25Q0Q; Python SOURCE lane, distinct from11 cross-language/cost and05 runtime acceptance.

## Verdict

**No new must-fix in this narrow Python mean source delta. Identified source units clear.** Not runtime acceptance, human GitHub approval, whole-branch integration or main/release delivery.

ALL normalize.py:1-776 read, not just17 changed lines. AST comparison confirms ONLY _Reducer.add and _Reducer.finish changed; all30 other function/method units are unchanged. Public callers and original lifetime test functions are parent-exact. Full four-path commit diff retained; TS semantic/cost acceptance belongs to11, not this report.

## Reviewed invariants

- Exact numerator, normalize.py:565-568,625-630: accepted ints/finite floats become integer multiples of the minimum subnormal. Binary64 integer-ratio denominators are powers of two no greater than2**1074. Ints retain exact significands. Mean adds to ONE integer, without rounding a prefix/residual or rescaling partial means.
- One final rounding/overflow, :656-672: exact numerator is divided by valid count times2**1074, not first converted to float. No float correction/scaling intervenes. Finite float means stay within observation extrema although sums may overflow. Unrepresentably large Python-integer means follow existing OverflowError/nonfinite/null-warning policy, not a promise all integers fit float.
- Subnormal/signed zero: negative integer numerator retains sign into final division/negative underflow. Exact integer cancellation canonicalizes zero positive, matching producer Fraction reference and inherited mean behavior; no negative-zero input-sign preservation promise. Producer negative-half-zero explicitly checks copysign, not only equality.
- Denominator/null/count, :616-629: count remains separate. Mean increments valid count only after exact int/float checking; bool/string/null do not contribute; nonfinite scalars become None at:388-407. All-null state stays None, so no zero division. input_count:723-729 includes all rows, not each group's denominator.
- Weighted other, :593-615,674-684: overflow transfers the last retained group's entire numerator/valid-count state; subsequent raw valid observations update it. No mean-of-means or overflow-key set. Collision labels/group bounds/key types/null policy unchanged.
- Budget, :46-52,426-446,584-591: one numeric state per retained group/other, no input/partials list. For N finite float observations numerator bit length is bounded by about2098+ceil(log2N); denominator/count grow logarithmically. _store charges enlarged integer decimal payload and checks16MiB before numeric-state replacement. Temporary ints/object overhead are not an RSS guarantee; public:692-697 expressly says payload budget.
- Planning/output, :524-562,687-776: mapping/inference/max_points/final record budget/schema/warnings unchanged. Prefix plus remaining adapter consumed once; no new materialization or stream restart.
- Lifetime, :481-521,713-750: P1 owned adapter reference/finally-close and outer rows.close unchanged. Mean changes no ownership transfer. No new file deletion/traversal, HTML/execution/URL authority, resource lifetime or input-history allocation in these two methods.

## Producer oracles inspected, NOT claimed independently run

Full python/deepviz/tests/test_r17_normalizer_boundaries.py:1-139 read. Added21 mean cases:10 fixtures times records/one-pass plus weighted-other/null/bool/string exclusion. Covers signed subnormal tails, overflow before/after prefix, ties, signed underflow, wide numerator and cancellation residual. Expected values use standard-library Fraction.from_float and valid raw counts, NOT production _sum_units. Original lifetime function ASTs unchanged. These are author test definitions, NOT my pass count.

Connected public path review: __init__.py:1-27 export; models.py:1-92 spec/result; render.py:1-229 including normalize:137,139 and metadata:159-162; tools.py:1-191 including normalize_data:95-119/render bridge; cli.py:1-60 including normalize:49-50; mcp_server.py:1-115 including registration:101. No renamed callable/result-shape break. These connected reads are NOT an audit of every unrelated pre-existing defect in those modules.

## Identity and execution limits

Actual normalize.py raw Git-LF SHA256 **f3cc6e78e188ed97f62133a954154dbfdd416128c97cd4b154144ae62f778296**,35309 bytes. All16 captured files byte-compared against immutable c1b Git blobs; parent/P1 ancestry verified. Full diff, file hashes,32 function-unit AST hashes/ranges and unchanged-unit comparisons: evidence/R38-01/.

Initial origin helper guessed short ancestor5ba69: git exit128 BEFORE product execution. Actual source log resolves P1 to5ba860305dcc86ac2f95f01705b984d2b40f2799; explicit ancestry then passed. Two report-write requests were scanner-rejected BEFORE execution; bounded scanner-compatible prose saved this report. Harness/tool errors retained, not product failures/passing tests; source untouched.

**Product imports/calls:0; pytest:0; benchmarks:0; new probes:0.** Static hash/AST checks passed. No concrete uncovered mean bug justified a counterexample, so no runtime padding or duplicate05 acceptance matrix. No product import-path proof is claimed because no product was imported. No install/env/dependency/source/oracle/schema/config mutation/API writes/spawn/job polling/old SUM/10M.

Not cleared: prefix-SUM, scalar conversion, GraphQL and later546c25ea75ee9d8a41b3832aa639664bc9a683b5; TS parity/cost; runtime acceptance/CI; package/render/browser/scale; unrelated old models/MCP/tool defects. c1b predates main's Mapping repair and is NOT a whole branch to merge as current main. R04/root report actual main31cff already merged; no Mapping/main-QA replay here.

Next R04: consume this narrow Python SOURCE gate alongside11/05/TS gates for the intended dependency-complete package/PR; preserve actual-main fixes and other owned normalizer work. New/integrated546 heads need their own affected identity/gates. No source blocker here should delay a genuinely fully gated usable slice.
