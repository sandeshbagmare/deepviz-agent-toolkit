# Independent findings routing / decisions

Source baseline b6abc8d, main now d4ee4e8 is import-order-only equivalent. Full reports own exact repros/artifacts. Do not duplicate fixes or edit another owner's paths.

| Finding | Owner | Required disposition |
|---|---|---|
| N01 1 count heatmap picks y categorical instead of generated count | N05 Python renderer | fix shared channels and all5 engine semantic regression |
| N01 2 missing numeric→0 | N05 | preserve null/gaps or explicit disclosed omission, never fabricate measurement; distribution helpers too |
| N01 3 scalar histogram bins index | N05 | observation value inference, [10,10,10,20] bins3/1 |
| N01 4 iterator dashboard Decimal replay stringifies | N05 | same list/generator semantics and supported scalar canonicalization/rejection, no default=str silent conversion |
| N01 5 GraphQL data_path suppresses partial errors | N04 normalize | envelope warning before path extraction |
| existing float cancellation [1e16,1,-1e16]→0 not1 | N04, N03 parity counterpart | bounded compensated sums/mean; preserve independent oracle |
| N01/N17 row caps don't bound cell/bytes | N04 primary, N03 TS, N05 replay | choose explicit safe byte envelope and rejection/truncation disclosure; report cross-owner consequences. No schema expansion needed for internal budgets. |
| N02 1 wheel prompts missing | N07 packaging (+N06 read_prompt only if path needed) | package actual prompt files, clean wheel read_prompt("system") |
| N02 2 Python CI parity lacks TS built prerequisite | N07 CI | install Node/npm/build or combined job, no unconditional skip |
| N02 3 thirteen stale coercion goldens | C17 parent contract | strict JSON number/no booleans/no strings is current deliberate policy, update goldens to negative cases; don't weaken validators |
| baseline8 mypy errors | N05 renderer7,N06 tools1 | scoped type repairs, preserve semantics |
| baseline10 import order errors | C17 existing test9 corrected d4ee4e8; N08 example1 | example deep_agent import group add blank before first-party deepviz |

C17 ruling: authoritative existing strict JSON numeric policy stands (e44f667 already deliberate). Correct stale fixture expectations, not runtime acceptance. Structural JSON Schema cannot express every dashboard semantic validation alone; document/test semantic runtime layer. Any new confirmed parity beyond these stale goldens goes to source owners/C17.
