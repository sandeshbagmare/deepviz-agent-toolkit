# R31-01 final independent Mapping repair review

What this change does: apply the existing five-field numeric guard to all supported Mapping inputs, instead of dict alone. It adds one standard-library import, changes one isinstance target and supplies42 permanent tests. No schema/default/bound/wire/renderer contract expansion.

**Reviewed actual source bff9384d1ebe5c8f6f8f0f994300264b32bb98d8**.
Parent99841ffb80e0f2ea90c753c1bf0ceff718e0e180/base0ae2cf26426822135fc10d337fcacf580b7ed833/PR33.
Reviewer ses_de5678335ffeI7xJrod5l25Q0Q, original F1 finder/non-author.

## Verdict and F1 disposition

**R25-01-F1 is RESOLVED on this exact bff head.** The published strict counterexample remains BYTE-IDENTICAL to commit16f8f1 and now passes. UserDict strings/booleans no longer reach numeric coercion; valid Mapping inputs remain accepted. No remaining must-fix finding in the reviewed repair/source slice. This is my genuine narrow independent source-review acceptance, NOT human GitHub approval, evidence for another head, four-agent completion, CI clearance, merge/default ancestry or issue closure.

## Actual source and all nine PR paths

- python/deepviz/src/deepviz/models.py:5,41-48: the complete new runtime delta is exactly the Mapping import and dict-to-Mapping guard substitution. Byte reconstruction from998 matches actualbff. Guard only reads and returns input; no copying, mutation, new conversion, authority or exception swallowing. Dict subclasses and supported read-only/native mappings take the same checks; existing JSON numbers/integral floats/child/dashboard validation remain unchanged.
- tests/test_native_mapping.py: all45 lines inspected,42 cases:30 root negative cases,4 defaults/integral positives,6 child negatives,2 child integral positives. Invalid guard-message consistency includes values already rejected by bounds; I do not label these36 new defects. All42 ran independently onbff.
- tests/test_models.py and tests/test_numeric_schema.py: both existing files EXACT998 Git bytes. Original40 assertions/import formatting unchanged by repair; no oracle weakening. Entire current tests inspected as context, not falsely claimed rerun here:17+15 own complete82 execution.
- schemas/chart-spec.schema.json: EXACT998 bytes and independently regenerated actualbff output, SHA256 ecd85be393444b7ff5bd9fcbb99cae4c900fad570d961476e1bcd4e443c6f65d. No schema expansion/native Mapping waiver; invalid mapped scalar values reject consistently with JSON Schema numeric types.
- .github/workflows/chart-contract.yml: EXACT998 bytes, full34 lines reviewed. Ordinary main/fix push and PR main; contents read-only; no secret/write-token/pull_request_target. Three-version dependency-only contract pytest/root Ruff/mypy remains honest, not a full toolkit/build CI claim.
- docs/verification/r22-contract/README.md, red-green-summary.json, validation-output.json: EXACT998 bytes, reviewed as historical initial numeric-repair evidence, not bff source/hash/test results or current gate approval. ALL4accept/6reject committed model JSON outputs/error records independently reproduced exactly onbff. Current repair/evidence are in this report and R32 actual-head packet, not a silent recasting of historical998 numbers.

Those are ALL9 base-to-bff changed paths. New parent-to-bff delta is ONLY2 paths, not a broad cherry-pick. No changed HTML, filesystem, execution/URL sink, unbounded buffer or renderer. No whole-toolkit safety approval is inferred.

## Fresh origin proof and metadata correction

All15 current tree files materialized directly from immutablebff Git objects, raw bytes verified before testing. Actual module imported from own unique snapshot; Python-S disables editable sibling hooks; process-local PYTHONPATH includes own source and existing read-only dependencies. SAME-PROCESS model path/hash, all15 file hashes, provided new42 test hash and unchanged published F1 hash asserted BEFORE pytest.

Actual bff model Git-LF SHA256 is **8532ec73be4a212d822aab2ee5b021e9d56a7cc266ddbd9ae111ed8310b7262d** (3021 bytes). R32 packet's93d1472b... does NOT match it; hypothetical fullCRLF hash e4c86a... also differs. Initial identity guard correctly stopped BEFORE tests. I inspected actual Git diff/bytes, proved exact minimal substitution, then used actual immutable Git identity; no guessed normalization or wrong-source test. Cause of producer packet hash is unverified. R04 should correct that metadata; it is not a remaining runtime blocker because exact published source is independently proven.

Published F1 probe SHA256 remains308c62bcf763965ca166e7939a5e79aabda7194bec258b276b4ed9f01657d6e4. New provided42 file SHA4f06bc1ad9cdc021f5081f5c59b10081783439e2fa95b69287d079e5dc82bb94. All proof/commands/logs/JUnit retained in evidence/R31-01/.

## Independent affected execution

| Exactbff check | Actual result |
|---|---|
| NEWprovided42 + UNCHANGEDpublishedF1 + NEWindependent4 | exit0,47passed/0fail/0error/0skip,0.34s |
| Root python-S -m ruff check . --no-cache | exit0 |
| Root python-S -m mypy --cache-dir OWN | exit0,1 source file |
| NEWown probe Ruff with explicit actual-head config | exit0 |
| Generated schema and ALL10 committed JSON input/output/error fixtures | exit0,exact bytes/results |

Independent4 cases cover UserDict and MappingProxy at root and as children of native Mapping dashboards. Each checks defaults, all-five-field integral lower/upper bounds, integer output types, model-JSON roundtrip/schema validity, invalid strings/True/False for all5 fields, input values and child-list/object ownership unchanged on success and rejection. This is bounded affected coverage, not a full old40/79/74 replay. The prior998/e44 models were NOT executed; historicalRED1 remains untouched provenance.

Versions Python3.12.16/Pydantic2.14.4/pytest9.2.0/jsonschema4.26.0/Ruff0.17.6/mypy2.4.1; existing dependencies read-only/no installs. Model JSON is the applicable real output. No renderer exists here; chart screenshots/browser/scale are not invented requirements or passes.

## Limits and immediate owner action

No CI polling/API writes, source/schema/workflow/original-oracle edits, installs, spawn/shared/default Git mutation. No source changes made by this reviewer. Current remote CI, other agents' results, actual merge/default ancestry, local other Python/dependency versions and toolkit/build/browser/scale are unverified here.

**R04: use this exact-head independent acceptance with the other three genuine bff gates and fresh exact-head CI; merge the focused slice promptly if all gates pass, then verify default ancestry/notifyQA13 and disposition#30.** This reviewer has no remaining F1 source blocker onbff. Old998/e44 reports are provenance, not substituted approval.