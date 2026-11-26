# N12 authoritative contract/parity QA

- Status: in progress; initial checkpoint 2026-11-27.
- Owner/session: N12 parity QA; actual runtime session ID not exposed to this child.
- Main read-back: `release/candidate` at `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`; main dirty paths `AGENTS.md`, `opencode.json`, `RESUME.md`, `docs/coordination/` belong to other owners and are preserved.
- Assigned new worktree: `C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n12`; branch `test/n12-parity`; base `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.
- Allowed writes: this MAIN report; new disjoint schema/parity regression tests and fixtures in own worktree; unique artifacts `artifacts/local/N12`. No production/schema edits, main Git/source writes, installs into shared venv, or spawning.
- Acceptance: identify Python imports/commit/dirty state; rebuild own TS; compare Python-authoritative accept/reject/defaults against JSON Schema and TS; root/package schema fingerprints; normalization GraphQL/data_path/count/heatmap/missing/nonfinite/overflow semantics; assess historical test assumptions. Preserve honest failures and route minimal repros here immediately to N03 (TS), N04 (Python normalization), C17 (models/schema).
- Commands so far: main `git status --short --branch` exit 0; `git worktree list --porcelain` exit 0. Candidate source identity confirmed; no product tests claimed.
- Current action: read remaining design/plan/dependency gates, create assigned clean worktree, inspect contract and existing parity tests.
- Next executable action: `git worktree add -b test/n12-parity C:\Users\bagma\AppData\Local\Temp\opencode\deepviz-n12 b6abc8d` from main.
- Blockers: none established. Final-candidate signoff is explicitly not claimed; this assignment checks the fixed b6abc8d baseline unless resumed on a newer integrated SHA.

## Execution checkpoint 1

- `git worktree add -b test/n12-parity ...\deepviz-n12 b6abc8d` exit 0; own new worktree created at assigned base, no historical worktree modified.
- Read complete model/TS validator/normalization implementations and historical schema/cross-language tests. Historical model already prevents JSON numeric string/boolean coercion. Generated schema intentionally omits dashboard semantic validators; the historical test name saying these rules are not expressible in JSON Schema is too strong (conditional schemas can express them). Will measure this boundary rather than treat Python-authoritative rules as negotiable.
- Own `npm ci` timed out after 120 seconds, exit 143/SIGTERM, with no output. No build/test pass claimed. Next: inspect own dependency installation and rerun `npm ci` with a bounded longer timeout, then build locally before parity execution.

## Immediate finding N12-F1 — C17 historical corpus contradicts current authority

- Source: clean production `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`, own N12 worktree. Imported `deepviz/__init__.py`, `models.py`, `normalize.py` all under `...\deepviz-n12\python\deepviz\src\deepviz`; Python 3.12.16. Own TS rebuilt successfully (not sibling/stale dist).
- Command: `$env:PYTHONPATH = "$PWD\python\deepviz\src"; $env:PYTHONDONTWRITEBYTECODE = '1'; & 'C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe' -m pytest tests/test_cross_language_contract.py tests/test_schema_contract.py tests/test_models.py -q` in N12 root: exit 1; **13 failed, 407 passed, 0 skipped**.
- Every failure is `test_python_chart_spec_matches_contract_corpus` asserting historical coercion acceptance, not TS/Python disagreement. Public npm-vs-Python cases passed. Minimal fixture: `{"version":true}`; corpus says accepted, Python authoritative before-validator rejects, TS rejects. Also rejected by both: `{"max_points":"10"}`, `{"width":"240"}`, `{"columns":true}`, recursive child versions of these.
- Smallest change request to C17: correct the 13 stale fixture expectations/IDs in `tests/fixtures/schema-parity.json`; **do not weaken models/TS to restore coercion**. N12 owns only new test/fixture files and will not edit historical files.
- Dependency retry `npm ci --prefer-offline --no-audit --no-fund`: exit 0, 160 packages; `npm run build`: exit 0. First provenance probe mistakenly accessed package-exported `deepviz.normalize` function as a module, exit 1; corrected `importlib.import_module` provenance probe exit 0. This was a QA probe error, not a product defect.
- Next action: extend fresh authoritative schema/default/normalization matrix and immediately record minimal mismatches for N03/N04/C17 here.

## Immediate findings N12-F2/F3 — minimal normalized-value repros

All below reproduced on unchanged b6abc8d production, own freshly built TS; own diagnostic command `python artifacts/local/N12/probe_n12.py` with explicit own PYTHONPATH, exit 0 **as an evidence probe, not a passing product gate**. Full case values/output/import identity/hashes saved at own `artifacts/local/N12/baseline-probe.json` (45 exploratory cases). It reports 12 bytewise mismatches, **one is only 45.0 vs 45 and not a semantic defect**. Other cases require owner disposition, not a blanket claim of 11 unique bugs.

### N03 TypeScript minimal requests

1. **Confirmed wrong-data extraction:** data `{"data":{},"errors":[{"message":"test"}]}`, spec `{"kind":"table","aggregation":"none"}`. Python rejects GraphQL errors/no usable data; TS returns the error message as a record `[{"message":"test"}]` input_count 1, falsely warning usable data. Fix empty-data/error handling and exclude errors from collection candidates; never chart protocol errors as rows.
2. **Confirmed row identity/data loss:** data `[{"id":1,"items":["a","b"]}]`, same raw spec. Python preserves single record `{"id":1,"items.0":"a","items.1":"b"}`; TS discards `id` and emits two scalar index/value records. Restrict wrapper inference when a record has sibling nonmetadata scalar fields, or require an explicit data_path rather than silently discarding the parent.
3. **Auto JSONL gap:** data string `{"id":1}\n{"id":2}` with raw spec and default format. Python returns 2 records; TS SyntaxError. Minimal fix match Python auto extra-data JSONL detection; explicit `format=jsonl` passed.
4. **CSV scalar mismatch:** `g,v\na, 2 \nb, \n`, raw spec + `format=csv`: Python v values `[2,null]`, TS `[" 2 "," "]`. `g,v\na,NaN\nb,Infinity\nc,-inf\n`: Python all null + nonfinite warning, TS retains strings/no warning. `g,v\na,1e999\n`: Python null + warning, TS string. Match Python cell interpretation for whitespace/numeric/nonfinite text or document a deliberate language boundary; do not drop nonfinite warnings.

### C17 contract / N04 normalization decisions

5. Group data `[{"g":1,"v":1},{"g":1.0,"v":2}]`, spec `{"x":"g","y":"v","aggregation":"sum"}`: Python deliberately type-tags int/float into two groups, TS JSON number treats one group -> v=3. This is a real cross-language grouping-policy mismatch; C17 decide whether JSON numeric categories are one identity or preserve lexical integer/float distinction (JS parsing cannot retain lexical distinction without a new boundary). Booleans vs numbers are correctly distinct in both. Do not silently remove existing Python type-tagging without authority.
6. Ambiguous shape boundaries need one shared fixture policy: `[{"tags":["a","b"]}]` -> Python 2 column records vs TS 1 flattened record; `{"payload":[{"id":1},{"id":2}]}` -> Python keys `payload.id` vs TS `id`; `{"pages":[{"nodes":[{"id":1}]},{"nodes":[{"id":2}]}]}` -> Python keys `pages.nodes.0.id` vs TS `id`. These are inference/shape decisions, not permission for N12 production edits. Explicit data_path can remove custom-wrapper ambiguity. Reported to N04/C17 for documented selection, N03 then mirror.
7. `{"data":{"team":{"nodes":[{"id":1}]},"version":1}}`: Python rejects ambiguous GraphQL siblings; TS flattens 1 parent record rather than extracting team. Match explicit-data_path boundary; avoid claiming automatic parity on ambiguous GraphQL.

### C17 schema semantic boundary

- Probe confirms root schema, TS exported schema, and Python generated schema are structurally equal. Raw `{"kind":"dashboard"}`, `{"charts":[{}]}`, and nested dashboard payload are **accepted by generated JSON Schema but rejected by both runtime validators**. Historical schema tests explicitly treat semantic checks as Python-only. C17 should either encode the semantic constraints in generated contract JSON Schema or clearly keep schema advertised as structural plus runtime validation; exact raw accept/reject parity is not currently satisfied. Numeric strings/booleans and integer-valued numeric literals already match across the validators.
- Current next action: add scoped new red regression tests with explicit source-independent oracles, compare warning disclosure categories, verify weighted overflow means with numerical tolerance, and finish root/package/dist fingerprints. No source/schema edits made.

## Immediate finding N12-F4 — cancellation numerical accuracy (N04/N03)

- Command own-source `python -m pytest python/deepviz/tests/test_normalize.py python/deepviz/tests/test_graphql_contract.py python/deepviz/tests/test_aggregation_semantics.py -q`: exit 1, **1 failed, 124 passed, 0 skipped** on b6abc8d.
- Historical failing test `test_sum_preserves_small_residual_under_large_cancellation_with_documented_tolerance` is a meaningful arithmetic oracle, not a stale coercion assumption: float measures `[1e16,1.0,-1e16]` in one explicit sum group return 0.0 instead of the residual 1.0 (integer case remains exact). N04 smallest request: compensated bounded sum state or explicit numerical-loss policy; do not weaken residual-scaled tolerance. Source `normalize.py` uses naïve state addition at line 498. TS has same naïve grouped addition at `normalize.ts:286`, to verify in new cross-language residual regression.
- Full historical GraphQL/normalize cases otherwise passed; this does not resolve the additional cross-language shape inferences above.
