# Future strict acceptance: NOT EXECUTED in R31

Base e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23. One UNAPPLIED proposal adds four lines only. No fix commit exists here, no future result is a pass. R04 is sole source implementer after its Mapping milestone.

## Compatibility decision BEFORE application

Route raw strings through the existing data-envelope preflight. Preserve valid callback start/end counts and SDK kwargs delegation; invalid inline admission raises before ANY callback, as dictionary-form already does.

Observable trace difference: successful bare inputs now have canonical callback inputs.data and dictionary input_str representation, rather than raw input_str and inputs=None. This is NOT byte-exact trace preservation. R04 must explicitly accept this normalization as the intended callback contract. If exact raw callback payload is required, DO NOT APPLY this proposal or call it transparent. No global/context cache, private SDK override, extra raw decode or altered original oracle is proposed to conceal the difference.

## 1. Freeze ACTUAL repaired source; preserve original oracles

Require a real clean committed NEW_PIN and full tools Git-blobSHA256; reject e47/d65 or old tools SHA11273c5f5b0ff2eee16e09c6c727e560582a43fcae723bb315b6ef80d5a68495 as a repair. Check diff, actual same-process import paths, model/normalizer/SDK hashes. No automatic carry of old execution. R04 first checks patch against target bytes, never force-applies it. Existing environment only, no install/skip for missing prerequisite.

Both original Python probes remain byte-for-byte unchanged: working and GitLF hashes in static-proof.json must match published2855f7a and current probe checkout. No assertions/expected errors/callback counts/depths/xfail/skip changes.

Original source_identity.py is intentionally pinned to d65: DO NOT retarget it or claim it proves new source. A NEW separate identity wrapper must guard actual repaired PIN/import bytes. Original test_p1_security.py already accepts R22_02_SOURCE in its import fixture, so needs NO edit.

## 2. Future run of ONLY affected unchanged strict controls

From original owned probe checkout, existing Python and a fresh unique result/basetemp directory AFTER the new-PIN identity guard succeeds:

- Set R22_02_SOURCE to the real repaired checkout and PYTHONPATH to its python/deepviz/src.
- Set PYTHONDONTWRITEBYTECODE=1, PYTHONUTF8=1, R22_02_RESULTS to fresh results directory.
- Command: EXISTING_PYTHON -m pytest tests/r22_probes/role02/test_p1_security.py -q -rs --tb=short -p no:cacheprovider -k "test_all_supported_call_forms_admit_before_callback or test_bare_string_is_a_supported_public_form_with_exact_raw_limit" --basetemp NEW_RESULTS/pytest --junitxml NEW_RESULTS/affected.xml

Expected FUTURE selection is six cases, not an old eight-case/MCP matrix replay. Require actual6PASS/0FAIL/0ERROR/0SKIP and actual exit0. Two original bare run/arun failures must become GREEN with their assertions intact. Existing cases cover escaped duplicate49bytes, raw1,000,001UTF8bytes/999,994characters, encoded5000depth, concise ValueError/zero callback starts on rejection, and same-tool recovery. Dictionary counterparts stay zero-start; exact1,000,000rawUTF8bytes remain accepted with one start. No old e47 baseline rerun or SDK/stdio/capacity/browser/fullsuite/build/CI replay.

## 3. Focused semantic/callback acceptance, NOT another matrix

Producer adds smallest permanent cases under an actual NEW source/test grant; independent02 can execute only after real committed repair handoff. These are UNEXECUTED acceptance conditions, not newly reproduced counterexamples.

- Small normal Unicode JSON array succeeds under both run/arun normalize_data; compare explicit-data form input_count/profile/strategy/warnings, ignoring fresh opaque dataset_id. Default profile spec stays table/sample/max_points200; recommend_chart retains comparison default and normal outputs.
- If R04 accepts section0: valid normalize/recommend gets one start+one end/zero errors; callbacks/tags/metadata/run_name/run_id forwarded intact. inputs.data is decoded data, NOT a nested data wrapper. Raw duplicate/rawbyte overflow/recursion get zero start/end/error callbacks, concise ValueError, no handles/files/outputs; next valid call recovers.
- A bare render string still lacks required spec and MUST NOT succeed. Encoded objects containing data/spec/goal are the DATA object, never unpacked into tool kwargs. Preserve required/extra-field validation; no scalar or filename-string coercion.
- Existing authority only: sole encoded file control requires data_dir; approved relative tiny file succeeds, escaped traversal/absolute/drive/URL rejects and outside sentinel stays untouched. Copied dataset handle rereads authorized original source, not a cached Path. These later _source errors need not have zero callbacks: inline admission, not all filesystem authorization, is moved before callbacks.
- Exactly one strict raw JSON decode; no decode-dump-redecode, global/context memo, replay file, renderer/registry/resource-counter changes. Existing bounded finite-data serialization checks remain. No artifact resources/paths added on profile/rejection. Do not claim total heap/RSS cap from1MB policy. Forward all positional/keyword config unchanged.

Record actual commands/exits/totals/skips/output/source and before-after two original hashes. No fix approval until a new real tools commit and its independent affected gates.
