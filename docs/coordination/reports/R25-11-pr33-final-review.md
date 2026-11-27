# R25-11 - final independent review of PR33 at 99841ff

**What this change does:** It rejects strings and booleans in five numeric ChartSpec fields while retaining integral JSON numbers, defaults and existing bounds. It adds the complete model tests, a canonical schema export, real model/JSON output and narrowly named contract CI; it does not ship a renderer or the full toolkit.

**Verdict: fix finding 1 first. REQUEST CHANGES on the exact head below.** Supplied40 plus unchanged own13 pass, but new supported-Mapping controls produce eight genuine failures. This is independent agent review, not a GitHub human approval. Other reviewer01/testers17+15 remain separate; R04 alone may fix/merge/close after actual affected-head gates.

## Must fix

### 1. [P2] Ordinary Mapping inputs bypass the strict numeric guard

**R25-11-F1** - `python/deepviz/src/deepviz/models.py:41-47` (especially the dict-only check at41).

- **What this is:** The new before-validator checks raw numeric types before Pydantic can convert a string or boolean into an integer. The public model_validate API also accepts ordinary Mapping objects, not only dict.
- **Problem:** UserDict and MappingProxyType do not enter the guard. Numeric strings and booleans are silently converted, including in dashboard children. All three original issue30 examples therefore remain accepted when carried by a supported Mapping. This is an incomplete fix of preexisting coercion, not a claim that the PR introduced the original bug.
- **Smallest fix:** Apply the raw-type check to `collections.abc.Mapping` instead of only dict, or validate the five field values before coercion. Preserve numeric integral floats and do not convert the incoming values first. Source changes belong to R04/the author; no production edit was made here.
- **If skipped:** The Python contract depends on the caller's container type. Code can still pass a string width or boolean version/columns through the public validation boundary even though equivalent dict/JSON inputs reject them.

Actual reproduction on immutable998, exact imported model SHA25694824d6f:

```python
from collections import UserDict
from types import MappingProxyType
from deepviz.models import ChartSpec

ChartSpec.model_validate(UserDict({"width": "900"})).width          # actual 900, expected ValidationError
ChartSpec.model_validate(MappingProxyType({"columns": True})).columns  # actual 1, expected ValidationError
ChartSpec.model_validate(UserDict({"version": True})).version    # actual 1, expected ValidationError
ChartSpec.model_validate({"kind": "dashboard", "charts": [UserDict({"width": "900"})]})
# actual accepted child.width900; expected ValidationError
```

New independent regression file `tests/r25_probes/role11/test_mapping_numeric_contract.py:10-27`: **8 failed /2 passed /0 skipped /0 errors /0 deselected**,0.30s,exit1. All eight failures are DID NOT RAISE ValidationError: six field/carrier combinations and two child carriers. Two positive integral-number Mapping controls pass. No model_construct, custom executable object, installed sibling source, changed oracle or weakened assertion is involved. Failures/log/XML and actual source proof are committed as evidence.

## Exact source and published-head proof

Owner/session `ses_de567811cffdTBwcb8pF5nDi9v`, independent non-author reviewer11. Read full manager R24 actual22-line packet, rootR25 common+11, R26/current MAIN AGENTS/checkpoint/ownnote. Own branch `agents/r10-11-python-scale-envelope`, clean starting head `18d7121b5194c76d95a9d3b5f60e4b8002f84449`.

- Actual public PR https://github.com/sandeshbagmare/deepviz-agent-toolkit/pull/33.
- Tested immutable head **99841ffb80e0f2ea90c753c1bf0ceff718e0e180**, direct parent/base **0ae2cf26426822135fc10d337fcacf580b7ed833**.
- All eight changed paths inspected in full; seven files added and the existing model changed,727 added lines. Complete immutable tree is14 files. All14 were copied from Git object bytes, checked before/after execution and again against Git at evidence packaging.
- Actual model import is the unique snapshot's `python/deepviz/src/deepviz/models.py`, SHA256 **94824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170**. No model was imported from MAIN or old e44.
- Actual schema Git-LF SHA256 **ecd85be393444b7ff5bd9fcbb99cae4c900fad570d961476e1bcd4e443c6f65d**; canonical sorted compact hash75972780be039e8dbbbf78a93d0611d9e6a5c9ed6e57a7ecf4239c2af20d6670.

One bounded official authenticated READ-ONLY snapshot at **2026-11-27 15:50:10 UTC** returned200 for expected user sandeshbagmare, repository/default main, PR33, files and check-runs. It independently confirms exact998/base0ae2, open/nondraft/**unmerged**, exactly eight paths matching local Git, and all six focused Numeric contract check-runs SUCCESS across Python3.11/3.12/3.13 (two runs each). The API merge_commit_sha is GitHub's proposed/test merge while merged=false, NOT an actual merge. No full-toolkit/human-approval/other-report completion was inferred. Receipt: `evidence/R25-11/published-pr33-checks.json`.

## All eight paths reviewed

| Actual998 path and lines | Independent conclusion |
|---|---|
| `python/deepviz/src/deepviz/models.py:1-80`, delta38-47 | Only11 added runtime lines; fields, after-validator and dataclasses otherwise unchanged from base. dict/JSON behavior good; Mapping bypass is finding1. |
| `tests/test_models.py:1-66` | Complete original30-case prerequisite present. Non-import AST, all function bodies/decorators/assertions identical to e44. Only import regrouping differs; actual SHA90b1675f matches the earlier import-only proposal. F1 old import-order finding is resolved on this actual head. |
| `tests/test_numeric_schema.py:1-59` | Ten new tests independently reviewed, including actual checkout origin, model/schema equality, all five numeric fields and child JSON. Real strict assertions; no skips/xfails. Missing ordinary Mapping carriers now covered by our NEW failing file. |
| `schemas/chart-spec.schema.json:1-190` | Actual generated export checked structurally and byte-for-byte against json.dumps(model_json_schema(),indent=2)+LF. No new fields; exported schema remains the existing numeric declaration. |
| `.github/workflows/chart-contract.yml:1-34` | Read complete workflow; details below. Model hash alone was not treated as workflow/test approval. |
| `docs/verification/r22-contract/README.md:1-28` | Honest model-only scope, original30/import-only and new10 prerequisites, real output, limits and four-agent/CI merge gates. It does not claim a renderer or full toolkit. |
| `docs/verification/r22-contract/red-green-summary.json:1-114` | All five claimed Git-LF file hashes match actual998. Historical precommit/not_yet_a_commit and pending gates are capture-time labels, not current remote status; ours supplies independent actual-head evidence. Author historical RED runs were NOT replayed or counted as our results. |
| `docs/verification/r22-contract/validation-output.json:1-225` | Independently rebuilt all four accepted outputs and six rejected fixtures through public Python and JSON APIs; exact serialized values/error locations/types/messages and schema decisions match. Finding1 concerns additional Mapping inputs absent from these fixtures. |

Unchanged `pyproject.toml` was also inspected against base: exact same bytes. There are no additional shipped runtime callers/modules in this14-file foundation beyond the model and tests; future renderers/CLI modules were not imported. All original source/test prerequisites are present, with no parent pyproject force-include or dependency changes smuggled in.

## Workflow and safety review

Workflow lines3-7 run on push to main/fix branch and pull_request targeting main. Lines9-10 restrict token to contents:read. There is no pull_request_target, secret access, untrusted title/body/path interpolation, API mutation, external chart URL ingestion or ignored test failure. Matrix3.11/3.12/3.13 is static; PYTHONPATH points to checkout source. Dependency-only install at28 matches existing declared Pydantic/test/static ranges. It intentionally does not pip-install the incomplete broader package. Steps30/32/34 run the full test suite actually present in this slice, Ruff over the branch and configured mypy over the model. This is honest focused contract CI, not a hidden full-toolkit filter waiver. Floating action version tags and dependency ranges limit exact dependency reproducibility; no exploited permissions issue is claimed.

Risk priorities: no new file-write/delete, data-ingestion, filesystem-path execution or HTML/render sink exists in this runtime diff. data_path/title remain inert model values, not proof future sinks are safe. The guard does not mutate input and only examines five fields per visited model; existing children/bounds remain. No process RSS, recursion/huge-input memory guarantee, chart validity/visibility, renderer output or full-toolkit safety claim follows from this bounded model review. Finding1 is the actual input-integrity defect, not an invented injection/path exploit.

## Independent execution on actual998

| Check | Actual result |
|---|---|
| Provided40 + unchanged own R22 strict13, fresh immutable998 | **53 passed**,0failed/0skipped/0errors/0deselected,0.26s pytest,7.160936s driver wall,exit0 |
| NEW ordinary-Mapping regressions | **8 failed /2 passed**,0skip/0errors/0deselected,0.30s,exit1; genuine unexpected acceptance |
| Actual full immutable branch Ruff | exit0, no cache, no fixes |
| Actual configured mypy | exit0,1model source file, no incremental reuse |
| NEW own Mapping probe Ruff | exit0 |
| Published schema versus actual generated export | Exact structure and canonical formatted bytes match, Draft202012 schema valid |
| Committed real validation output | Four accepted/serialized/schema-valid and six rejected with exact errors rebuilt independently |

Python3.12.16/Pydantic2.14.4/pytest9.2.0/jsonschema4.26.0/Ruff0.17.6/mypy2.4.1 from the existing read-only shared venv. Local matrix/platform/dependency-minimum coverage was not fabricated; remote six successful jobs were read back separately. No old e44/parent baseline, scale/fulltoolkit/npm/build/browser/provider/API-write/install work was performed.

## Exact replay and source isolation

Unique artifact root `C:/Users/bagma/AppData/Local/Temp/opencode/r25-11-pr33-998-ses_de567811cffdTBwcb8pF5nDi9v-artifacts`, immutable tree subdirectory source. Use existing MAIN venv python.exe with **-S**, PYTHONDONTWRITEBYTECODE=1, PYTHONPATH=SNAP/python/deepviz/src plus readonly MAIN/.venv/Lib/site-packages. This prevents editable .pth sibling hooks; both drivers assert actual model __file__, exact14 Git hashes before/after and unchanged probe hashes. source-identity.json is reviewer metadata, not a shipped product file. An inert installed namespace search location exists after the snapshot; the exact loaded models path/hash is asserted, not guessed.

Original53 driver calls pytest.main with `tests` and the unchanged own `tests/r22_probes/role11/test_numeric_contract_slice.py`, `-q -p no:cacheprovider --strict-markers --basetemp UNIQUE --junitxml UNIQUE`. Its R22_SOURCE_ROOT fixture is explicitly rebound to actual998/schema, not old e44. Mapping driver calls only NEW `tests/r25_probes/role11/test_mapping_numeric_contract.py` with the same flags plus --tb=short. Raw command arrays, versions, actual paths, hashes and result receipts are in review-checks.json.

Static commands from immutable source CWD: `python -S -m ruff check . --no-cache`; `python -S -m mypy --no-incremental --cache-dir OWN_TEMP`; NEW probe lint uses exact snapshot pyproject via --config. No source or existing oracle was edited.

Two setup issues are disclosed separately from product results: an initial portable-shell request was rejected BEFORE execution; an initial snapshot count expected15 but actual tree is14. All14 copied bytes were already correct; count-only manifest correction occurred before imports/tests. No false baseline RED, swallowed product failure or rerun-green substitution.

## Evidence, publication and next action

Own `docs/coordination/evidence/R25-11/` contains published-pr33-checks.json, review-checks.json, actual998-53.xml, mapping-red.xml, mapping-red.log and independent-validation-output.json. Review-checks SHA256 **1e4b15a86b98224054ae739d49af875bed19eb5646e7d48f4d3ed1d741331982**. Source manifest, both raw/Git-LF XML identities, full negative case names, diagnostics, versions, commands, workflow audit and limits are preserved. Windows traceback CRLF may normalize to Git LF; exact raw/LF hashes are recorded separately, not falsely equated. Meaningful owned-path commit/nonforce remote publication receipt will be saved to MAIN after actual confirmation, with no endless self-receipt commits.

**Executable owner action:** R04 should fix/disposition finding1, freeze a new published head and return that exact head to reviewer01+11/testers17+15 for affected controls/workflow/source reevaluation and fresh focused CI before merge/#30 closure. Do not silently carry forward this request-changes report or count53GREEN/remote green as resolving eight preserved failures. No approval, merge, closure, full-production or900-resolution success is invented.

**Not checked:** Other independent reports, merged main/default ancestry, release/package consumers, renderer/HTML/browser output, large input memory/scale, minimum dependency/platform local matrix and broader draft PR31. Those are not green by implication.

Publication harness disclosure: the first UTF8-only secret scan stopped before commit because PowerShell had redirected the raw Mapping failure log as UTF16LE. Raw external log remains unchanged; portable log was decoded to UTF8 LF without changing text. Both original and published hashes, plus raw/Git-LF probe identities, are recorded in review-checks.json. No tests/source/results were changed or rerun.
