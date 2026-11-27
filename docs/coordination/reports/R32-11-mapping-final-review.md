# R32-11 - final independent SOURCE review of repaired PR33

**What this change does:** It extends the existing raw numeric-type check from dict to all ordinary Mapping containers and adds42 permanent root/child regressions. Integral numbers/defaults/bounds/dashboard rules stay unchanged; this remains a model-only contract slice, not the broader toolkit.

**Genuine independent SOURCE verdict: APPROVE the exact model-only PR33 head bff9384d1ebe5c8f6f8f0f994300264b32bb98d8. No remaining material finding in this scope. R25-11-F1 is RESOLVED.** This is our actual new-head review and execution, not old998/e44/author approval carried forward. It is not a GitHub human approval, wholetoolkit green or authority to merge; R04 still must combine the other actualbff reports and new-head CI.

## Finding disposition and new execution

Former F1 at models.py41-47 allowed UserDict/MappingProxy numeric strings and booleans through a dict-only guard. Repaired `python/deepviz/src/deepviz/models.py:5,42-48` imports collections.abc.Mapping and applies exactly the same check to every supported Mapping. The error/body/defaults/fields/after-validator are unchanged. No native Mapping contract exception was adopted.

**Actual new-head total:105 passed /0 failed /0 skipped /0 errors /0 deselected**,0.36s pytest,0.4835047s driver wall,exit0:

- All provided82: unchanged original40 plus NEW42 permanent tests.
- Own unchanged published strict13, rebound explicitly to actualbff/source/schema.
- **Own unchanged published Mapping10: all original eight RED assertions and two positive controls now PASS.** Published bytes were extracted from own7527a8c Git objects and checked before and after execution. No assertion, original oracle or production file was edited.

The previously failing reproduction now raises ValidationError on actualbff, for both carrier types and in dashboard children:

```python
ChartSpec.model_validate(UserDict({"width": "900"}))
ChartSpec.model_validate(MappingProxyType({"columns": True}))
ChartSpec.model_validate(UserDict({"version": True}))
ChartSpec.model_validate({"kind": "dashboard", "charts": [UserDict({"width": "900"})]})
```

The NEW permanent `tests/test_native_mapping.py:1-45` contributes30 root invalid cases (all five numeric fields, string/True/False, two carriers), four default/integral positive cases, six child invalid cases and two child integral positives. It checks caller input preservation for root cases. Our unchanged10 and independent actual root/child output evidence separately confirm the real repair. Author RED/GREEN history is not counted as our result.

## Exact source identity, including newline disclosure

Owner/session ses_de567811cffdTBwcb8pF5nDi9v, second independent non-author SOURCE reviewer11. Full manager R32/13lines, root affected-gate packet/30lines, MAIN currentAGENTS/canonical/ownnote read. Own branch agents/r10-11-python-scale-envelope clean at7527a8c88a785bc39efad6c2173aa2c7932782cc before work. Reviewer01 and testers17+15 remain independent lanes; their completion is not invented here.

- Actual published PR33 frozen head **bff9384d1ebe5c8f6f8f0f994300264b32bb98d8**; direct parent99841ffb80e0f2ea90c753c1bf0ceff718e0e180, base main0ae2cf26426822135fc10d337fcacf580b7ed833.
- One actual `git ls-remote --heads origin refs/heads/fix/r22-strict-numeric-contract refs/heads/main` exit0 independently returned exactbff and main0ae2. No merge/default advancement or new-head remote CI result is inferred. No CI polling/API write occurred.
- Complete actualbff tree15files, all copied from Git blob bytes, verified before imports/tests, checked same-process before/after, and finally compared again against Git at evidence packaging. Imported models.py is the unique actualbff snapshot, not MAIN/old998/e44/installed sibling.
- **Published Git-LF model SHA2568532ec73be4a212d822aab2ee5b021e9d56a7cc266ddbd9ae111ed8310b7262d.** Packet SHA93d1472b168feb9f1a12fa47f81e0296228459ebe006c14a4daba2637d3616ba is the manager's raw mixed-newline worktree file (63CRLF among81LF). Independently read-only checked: raw.replace(CRLF,LF) equals the immutable published Git blob EXACTLY. No manager worktree source was executed.
- NEW permanent-test Git SHA2564f06bc1ad9cdc021f5081f5c59b10081783439e2fa95b69287d079e5dc82bb94. Schema exactecd85be393444b7ff5bd9fcbb99cae4c900fad570d961476e1bcd4e443c6f65d.

The initial guard correctly stopped exit1 BEFORE model import/test because the packet RAW hash was compared to GitLF bytes. Count15/exactcopiedsource were correct; the guard was corrected only after actual raw-to-Git normalization was proved. This is a disclosed pre-test identity mismatch, not a product failure, source alteration or false RED. Both hash identities and proof are saved.

## All nine PR paths and connected code reviewed

| Actual PR path | Source-specific review |
|---|---|
| python/deepviz/src/deepviz/models.py:1-81 | Full source read; exact new delta versus998 is one Mapping import and dict-to-Mapping check. Five numeric fields/error/defaults/bounds/extra-forbid/dashboard/dataclasses otherwise unchanged. Standard dict/subclasses remain Mapping; no mutation or pre-coercion conversion added. |
| tests/test_native_mapping.py:1-45 | Entire NEW42 permanent tests inspected; strict rejection, valid integral/default types, root/child checks, no skips/xfails/weakened old oracle. Exact4f06 hash verified before execution. |
| tests/test_models.py:1-66 | Byte-identical to998 and executed again as part of82; original complete30 assertions/import-only prerequisites preserved. |
| tests/test_numeric_schema.py:1-59 | Byte-identical to998 and executed again: ten numeric/schema/origin/child controls, no weakening. |
| schemas/chart-spec.schema.json:1-190 | Byte-identical to998; independently regenerated from actualbff model and exact formatted bytes match. Five numeric declarations, bounds and recursive child schema unchanged. |
| .github/workflows/chart-contract.yml:1-34 | Byte-identical to998, entire34lines reread: static3-version matrix, pushmain/fixbranch and PRmain, contents:read, no PRtarget/secrets/untrusted shell expression, no ignore-failures. All shipped tests/Ruff/configured mypy, dependency-only install. No new workflow/dependency privilege boundary. |
| docs/verification/r22-contract/README.md:1-28 | Byte-identical prerepair author evidence/scope: model-only, actual JSON output not fake chart; original review gates apply. Original30+10 counts describe its first capture, not our current105. |
| docs/verification/r22-contract/red-green-summary.json:1-114 | Byte-identical historical precommit998/e44 capture. Its old model94824d6/hash and author40 are NOT misreported as currentbff hash/current independent result. Fresh complete bff manifest/results here are authoritative for this review. |
| docs/verification/r22-contract/validation-output.json:1-225 | Byte-identical; independently rebuilt actualbff all four accepted outputs and six negative JSON fixtures with exact errors/schema decisions. |

All seven non-repair PR paths are byte-equal to fully independently reviewed998 by explicit Git comparisons, not an unproved model-hash shortcut. Unchanged pyproject was also checked byte-identical to base; no parent packaging/schemaforceinclude/config/dependency change. This15-file foundation has no shipped renderer/normalizer/CLI runtime caller to exercise; tests/public model entrypoints are the connected consumers. No later broad candidate is imported.

## Real model output, schema and safety

Independent output script on exactbff produced six accepted Mapping root/child outputs (defaults, all five integral floats, child integral width for both carriers) and eight rejected root/child Mapping inputs. Actual model_dump_json output is schema-valid; every input remains unchanged. It also verified all10 committed literal JSON fixtures on new source. Generated schema equals published structure AND json.dumps(model_json_schema(),indent=2)+LF bytes. Own13 covers literal numeric bounds/booleans/strings/null/fractions, schema freshness, original input ownership/defaults; permanent42 covers all five Mapping fields. Existing custom dashboard rules are not falsely claimed to be fully encoded by exported JSON Schema.

Full actual focused-branch Ruff `--no-cache` exit0; configured mypy `--no-incremental` exit0 for1model source file. Static checks ran on the immutable branch, not the evidence-heavy own worktree. No install/shared cache/source edits. Existing Python3.12.16/Pydantic2.14.4/pytest9.2.0/jsonschema4.26.0/Ruff0.17.6/mypy2.4.1 used read-only. No local minimum-version/platform matrix or unqueried new-head remoteCI claim.

Risk review prioritizes data integrity/HTML/path/memory: no new file read/write/delete, HTML/template/render sink, arbitrary URL/code or path authority exists in the runtime repair. Guard reads five fields; it does not mutate caller data. Existing chart bounds/dashboard checks are unchanged. No guarantee about huge recursive-input memory/RSS, future sinks, rendered charts/10Mvisible marks or whole toolkit follows. Action version tags/dependency ranges remain floating as disclosed previously; no new exploit or release reproducibility proof is invented.

## Commands, evidence and limits

Artifacts: C:/Users/bagma/AppData/Local/Temp/opencode/r32-11-pr33-bff-ses_de567811cffdTBwcb8pF5nDi9v-artifacts, immutable source subdirectory. Python-S plus explicit actual snapshot/source path and read-only MAIN/.venv/Lib/site-packages, PYTHONDONTWRITEBYTECODE=1, plugin autoload disabled in this process. No editable .pth hooks. Same-process exact source/probe hashes/path checked before pytest and afterward. source-identity.json is reviewer metadata, not a product file. Own controls are byte-exact Git copies under external unchanged-published-probes, never rewritten.

Exact pytest args/path/interpreter/versions/hashes are in evidence review-checks.json: `tests` plus published own13 and published Mapping10, `-q -p no:cacheprovider --strict-markers --basetemp UNIQUE --junitxml UNIQUE`, called through guarded pytest.main in Python-S. Static CWD actual source: `python -S -m ruff check . --no-cache`; `python -S -m mypy --no-incremental --cache-dir OWN_TEMP`. XML independently parsed105cases/zero failures/errors/skips. There is no old998/e44/parent baseline replay, new softened test, source/oracle edit, API write, install, spawn, CI poll, build, scale or oldSUM replay.

Own evidence/R32-11 contains review-checks.json, actual-bff-105.xml and independent-model-output.json. Review-checks SHA256 **c0389637a86d61a962c61946ccb2a4a0a5020437a7677f031a4b53cffc1470fc**. Full15file/probe/import manifest, newline equivalence, unchanged7paths,105case counts, exact static commands/exits, JSON/schema/no-mutation outputs and limits saved MAIN+OWNbranch. No NEW r32tests required because original published strict controls suffice. Own meaningful scoped nonforcepublication/exactremoteSHA receipt follows only after confirmation.

**Executable next action:** R04 collect actualbff reviewer01 and testers17+15 reports plus fresh actualbff three-version CI. If all genuine gates are green, merge this usable slice promptly, verify default SHA/ancestry, notify dedicated mainQA13 and disposition#30. Do not wait for unrelated inventory/900/fulltoolkit/wave; do not count this source approval as another agent or a human GitHub approval.

**Not checked:** Other agents' final reports, new-head remoteCI (no polling), actual merge/default ancestry/issue closure, packaging/CLI/renderer/browser/provider/build/scale/memory/fulltoolkit and minimum-dependency/platform matrices. No new-head or future-head acceptance beyond this exact source is implied.
