# R25-01 final independent review of actual PR33 head

What this change does: add a before-validator to reject strings and booleans in five numeric fields without rejecting integral JSON numbers. The focused PR supplies complete tests, generated schema, actual JSON output and contract-only CI.

Actual reviewed head: **99841ffb80e0f2ea90c753c1bf0ceff718e0e180**.
Base: **0ae2cf26426822135fc10d337fcacf580b7ed833**. PR33.
Reviewer: ses_de5678335ffeI7xJrod5l25Q0Q, non-author.

## Must fix

### R25-01-F1 / P2: native Mapping inputs bypass the new numeric guard

Location: python/deepviz/src/deepviz/models.py:41-47.

What this is: Pydantic's public ChartSpec.model_validate accepts mapping objects, including the standard-library collections.UserDict. Valid mappings continue to work on this exact head, so they are not rejected input containers.

Problem/reproduction on actual998:

```python
from collections import UserDict
from deepviz.models import ChartSpec
ChartSpec.model_validate(UserDict({"width": "900"})).width  # actual 900
ChartSpec.model_validate(UserDict({"version": True})).version  # actual 1
ChartSpec.model_validate(UserDict({"columns": True})).columns  # actual 1
```

Equivalent plain dict inputs raise ValidationError. The guard checks dict only, so supported UserDict inputs bypass every field check and reach Pydantic coercion. UserDict({"width":900}) remains a valid positive control. This is an incomplete native-input repair, NOT a JSON-wire failure or a newly introduced remote exploit. The runtime type-rejection claim has no stated native-Mapping exception.

Smallest fix: apply the existing checks to supported Mapping containers, e.g. collections.abc.Mapping, preserving valid mapping/integral-number behavior. R04 owns any source change and affected retest/review; I did NOT apply or verify that proposed repair.

If skipped: Python callers still pass the strings/booleans the repair says it rejects by wrapping input in an ordinary mapping. Do not equate JSON-only GREEN with complete native-input closure.

NEW permanent strict counterexample: tests/r25_probes/role01/test_mapping_numeric_boundary.py. Actual998 exit1: **1 failed,0 errors,0 skips,0.17s**. It first confirms valid dict/UserDict positives and strict dict negatives, then preserves all three unexpected Mapping acceptances in one failed assertion. Original oracles unchanged. See new-mapping-boundary.log/.xml and native-mapping-diagnostic.json.

## All eight actual paths reviewed

1. models.py: only11 runtime lines added. Fixed five-field loop; input not mutated; existing defaults/bounds/dashboard rules unchanged. JSON bool exclusion/integral-number policy correct, but accepted Mapping branch bypasses it.
2. tests/test_models.py: COMPLETE original30 cases. Entire non-import AST, including decorators/bodies/assertions/constants, exactly equals e44; bytes are NOT identical because imports were reordered. This resolves prior I001 without disabling rules or changing pyproject. Actual998 Ruff passes.
3. tests/test_numeric_schema.py:10 new cases verify own import, fresh schema and numeric JSON bounds/children. Genuine JSON coverage, but native negatives are dicts; accepted Mapping input is missing.
4. schemas/chart-spec.schema.json: independently regenerated exact UTF-8/LF bytes SHA256 ecd85be393444b7ff5bd9fcbb99cae4c900fad570d961476e1bcd4e443c6f65d. Existing dashboard after-validation exceeds inherited structural schema; no new universal semantic-parity claim or later dashboard schema imported.
5. .github/workflows/chart-contract.yml: push main/fix branch and PR main; contents read only; no secrets/write token/pull_request_target. Minimal dependency-only Pydantic2/pytest/jsonschema/Ruff/mypy install; own PYTHONPATH; unfiltered full focused pytest/root Ruff/one-file mypy. Python3.11-3.13 is honestly contract-only, not toolkit/package CI.
6. docs/verification/r22-contract/README.md: accurate scoped prerequisites/source isolation/output rationale. No implemented CLI/rendering/packaging/full-toolkit or independent-author approval claim.
7. red-green-summary.json: source/test/workflow Git hashes checked against actual blobs. Historical RED counts are author evidence, not my replay. not_yet_a_commit/pending gates describe capture time, not current PR facts or independent signoff.
8. validation-output.json: ALL4accepted outputs and6rejected input/error records independently regenerated on998, compared exactly. Defaults/integral lower bounds/children/errors agree. Model JSON is applicable real output; no renderer exists here, so chart/browser images are not invented.

Connected main pyproject/model API and all14 actual tree files read or hash-verified. Foundation's pre-existing absent CLI/package modules are not called a new regression. No new filesystem traversal, HTML sink, eval/URL authority or unbounded data structure in this diff; not whole-toolkit security approval.
## Actual independent execution / source proof

Unique ignored snapshot from ALL actual998 Git blobs. All14 hashes checked BEFORE execution. Python-S bypassed the editable sibling; process-local PYTHONPATH contains own source plus existing read-only site-packages. Actual model path and hash asserted in the SAME PROCESS before pytest and output checks:
94824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170.

| Actual998 check | Observed result |
|---|---|
| Supplied40 plus UNCHANGED own7 nested JSON guards | exit0,47passed/0failed/0errors/0skips,1.15s |
| Root python-S -m ruff check . --no-cache | exit0 |
| Root python-S -m mypy --cache-dir OWN | exit0,1 source file |
| Schema regeneration plus ALL4accept/6reject output/error checks | exit0,exact schema/output/errors |
| NEW native Mapping strict control | exit1,1failed/0errors/0skips,0.17s |

47GREEN is actual-head execution, not e44 carry-forward. No parent/e44/30-only baseline replay. NEW RED is separate; overall acceptance is NOT green. No other reviewer/tester result borrowed.

Own NEW probe initially resolved surrounding OWN-branch Ruff configuration via its absolute outside path: I001. This OWN harness error is preserved, not misreported as a focused production failure. Explicit --config actual998/pyproject.toml then passed on SAME unchanged probe bytes. No runtime/oracle replay for lint. One oversized report-write shell request was scanner-rejected BEFORE execution; targeted report read confirmed it unchanged, then bounded writes used. No lost/partial source write or fabricated pass.

Versions: Python3.12.16/Pydantic2.14.4/pytest9.2.0/jsonschema4.26.0/Ruff0.17.6/mypy2.4.1. No installations/environment mutations. Exact argv/cwd/exits/JUnit/module proof/source/test hashes/full diff/outputs: docs/coordination/evidence/R25-01/.

## Official PR/CI observation, limits and next owner

ONE bounded official public GET-only snapshot15:41:10-11UTC: HTTP200 PR33/files/exact-head checks. PR open/nondraft/UNMERGED, head998/base0ae2, exactly eight files. All SIX observed Python3.11/3.12/3.13 contract jobs completed SUCCESS. Actual IDs/URLs/head/files saved in official-pr33-read-only.json. Focused CI green is not my extra failing control, four reports, human approval, merge or900-issue completion. No API writes.

**Verdict: fix F1 first, or explicitly disposition the native-input contract gap before treating #30 as fully repaired.** JSON-wire/dict behavior verified, but I do NOT provide unconditional merge approval on998 with unresolved F1. R04 owns source/PR/default/contract scope decision. New immutable repair head needs affected exact-head review/retest; do not borrow998/e44 approval. Root receives the actionable blocker without idle polling.

Not checked: other agents' reports, actual merge/default ancestry/closure, local Python3.11/3.13 (remote observed only), other dependency versions, distribution/CLI/toolkit/npm/renderers/browser/scale. Production/schema/workflow/original tests read-only; no shared Git/API writes/install/spawn.