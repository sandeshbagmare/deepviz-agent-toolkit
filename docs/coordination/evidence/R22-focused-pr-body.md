## Focused fix for #30 — first independently usable default-branch slice

**Proposed head:** `99841ffb80e0f2ea90c753c1bf0ceff718e0e180`; **base:** actual `main` `0ae2cf26426822135fc10d337fcacf580b7ed833`. Related #30; no automatic closure until reviewed acceptance, merge and default-SHA verification. Broad draft #31 is separate and remains failing/unmerged.

### Narrow behavior / dependency boundary

The only runtime change is11 lines in `models.py`: reject string and boolean values for version/max_points/width/height/columns before Pydantic coercion. Integral JSON numbers such as900.0 remain valid, with existing defaults/bounds/child/dashboard behavior. The source blob is exact historicale44, transplanted onto the seven-file foundation rather than blindly cherry-picking an absent test hunk. Complete original30-test prerequisite plus10schema/import/JSON controls, generated contract, and clearly named **contract-only** Python3.11/3.12/3.13 CI are included. No renderer, normalizer, SDK, dependencies/pyproject or later toolkit code is pulled in.

### Executed tests and actual outputs

- Original source/oracle: **6 failed /24 passed /0 skipped**.
- Expanded controls before validator: **12 failed /28 passed /0 skipped**.
- Full focused checkout: **40 passed /0 failed /0 skipped**,0.35s; full-branch Ruff exit0; mypy exit0/one model source.
- Regenerated schema is unchanged from the unfixed declaration: SHA256`ecd85be393444b7ff5bd9fcbb99cae4c900fad570d961476e1bcd4e443c6f65d`.
- [Actual accepted/rejected public model JSON output](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/99841ffb80e0f2ea90c753c1bf0ceff718e0e180/docs/verification/r22-contract/validation-output.json): four real accepted/serialized/Schema-valid fixtures and six real rejections/errors, including children.
- [Reproduction, source/test/workflow hashes, all RED names and limits](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/99841ffb80e0f2ea90c753c1bf0ceff718e0e180/docs/verification/r22-contract/README.md). Model-only change: chart rendering is not applicable and no screenshot/full-toolkit integration claim is invented. Existing main does not yet have CLI/rendering implementations; this PR does not claim a complete runnable toolkit.

### Required pre-merge gates — pending, not fabricated signoff

- [ ] Reviewer11: independent readiness/source review of this exact head.
- [ ] Reviewer01: second independent source review of this exact head.
- [ ] Tester17: independent literal numeric/schema controls on this exact head.
- [ ] Tester15: independent JSON/wire/model-boundary controls on this exact head.
- [ ] Resolve any material findings; observe all three real focused CI jobs green.
- [ ] Verify merge/default ancestry before manually closing #30.

Root dispatches the four actual existing agent lanes; agent reports are not human GitHub approvals. Author results are not counted as independent reviews. The commit label does not approve merging before these gates. No force-push/default rename/all-branch merge or900issue padding. Subsequent fully tested toolkit slices continue independently.
