# R22-04 — independent owned-input unwind review/retest

**Scoped P1 PASS:** exact immutable local partial source **`5ba860305dcc86ac2f95f01705b984d2b40f2799`**; **18 passed / 0 failed / 0 errors / 0 skipped, 4.60s**. Unchanged author5 ran once; unchanged original four reducer-guard ownership invariants all pass; NEW9 independent controls pass. Scoped Ruff0/mypy0(two files). **No uncovered blocker in this finite subset. Not author16's final handoff, remote source publication, final candidate or release approval.** Own review publication pending execution.

## Owner, scope and immutable provenance

- SAME-ID `ses_de5678314ffeuDXtC7RfGsbD6V`; full MAIN R22common+04/later completion section, current AGENTS and own note read at entry. Prework report/note saved before substantive tests; canonical/RESUME/STATE were re-read during source inspection before execution (initial note's combined read-list was not a precise chronological assertion). No worker spawning or producer-progress polling.
- Existing own publication branch **`agents/r10-04-utf8-field-envelope`**, clean at R21 **`9be3dc01d6808e3beaf16f387e49673176069510`**; its product source is **not**5ba. No product cherry-pick/copy/integration. `git worktree add --detach C:/Users/bagma/AppData/Local/Temp/opencode/r22-04-source5ba-ses_de5678314ffeuDXtC7RfGsbD6V 5ba860305dcc86ac2f95f01705b984d2b40f2799` exit0 created exact clean read-only source. Source HEAD/status/diff remain identical before/after tests and evidence extraction.
- `5ba` parent **`ec9f669eff28cd5351da142765b7755e3b2f484f`**; full immutable diff reviewed: `normalize.py` **+78/−66** (144changed lines), NEW87line `python/deepviz/tests/test_r17_normalizer_boundaries.py`. Exactly two source-commit paths. No reading another worker's in-flight tree. One overly broad read-only search inadvertently returned short R17-16 report snippets; not followed up/polled/used for acceptance. All evidence below is independent immutable-source execution.
- Writes ONLY NEW `tests/r22_probes/role04/` (two Python files + README), this report, `evidence/R22-04/` and own note. No production/model/schema/original-oracle/other-notes/workflow/venv/install/API/spawn/issue/PR/shared-branch edits. Current task prohibits API calls, so no fresh `/user` GET; earlier generic prework auth requirement superseded. Verified existing expected HTTPSorigin/ownref/helper/author and use only non-force owned Git publication/readback.
- Same actual pytest process verifies GitHEAD/clean status, five real imported source module paths and exact Gitbytes, original/author/config/NEW fixture bytes **before and after**, external CWD separate from both source/publication trees and no `deepviz` CWD shadow. No import rewriting/fake implementation. Normalizer SHA256 **`eef44a7df71926932fc14b33ff47225903b30824c2435e74b9707b49ed357f2b`**. Author test SHA256 **`4451d287cfba3cf2e18a3c5174341eeee30436b0304d6e6591c83125a0629068`**.
- Compact actual source/module/hash/JUnit/native-resource/fixture proof: [`../evidence/R22-04/owned-unwind-results.json`](../evidence/R22-04/owned-unwind-results.json). Eleven raw artifacts hashed; actual before/after receipt equal,18collected/0fail. Existing read-only venv: Windows11/Python3.12.16/pytest9.2.0/**pyarrow26.0.1 actually used**, no optional skips. Own production/originaltests/schema diffagainst9beexit0.

## Independent connected-code review

| Exact5ba location | Review / disposition |
|---|---|
| `_without_bom:89–96`; `_jsonl:99–103`; `_delimited:116–135` | Replace `yield from iterator` with explicit non-owning iteration: parser destruction/close no longer forwards `close()` into borrowed stream. Actual late CSV/JSONL exception/cause and borrowed usability tests pass. Delimited syntax validation/error wrapping unchanged. |
| `_path_rows:228–236`; `_binary_rows:204–225` | Real owned text `with path.open`, ParquetFile context and Arrow input-stream context already define ownership; patch explicitly unwinds suspended root so contexts exit promptly, not only when traceback/GC releases frames. No `ExitStack`/`iterclose` symbol exists at this source; those are concepts, not invented implementation paths. |
| `_source:239–264`; `_records:481–521` | Internal adapter root retained **before** selected-path wrapping. `owned=source if source is not data else None` leaves plain borrowed iterables/generators unowned. Text adapters are library-created wrappers but iterate borrower nondelegating. Eager JSON Path opens/reads/closes within its existing `with`; unsupported/missing-file/validation errors retain ordinary exceptions. Root adapter close does not blindly call caller input close. |
| `_select_path:267–297`; `_expand:326–385` | Nested delegation/path views do not lose the retained root owner; author selected-path planning failure covers the former leak. Caller nested iterable ownership is not expanded. |
| `normalize:692–755` | Outer `try/finally rows.close()` spans32rowprefix, `_plan`, reducer accumulation/finish and reservoir processing. `_records` finalizer then closes only the retained root. Already exhausted generator close is harmless; no double owned text close in independent normal/error probes. Source records/counts/reduction/sampling/resource-limit semantics are unchanged by inspected diff. |
| `_arrow_rows:171–184` / Arrow reader borrowing | Borrowed RecordBatchReader is iterated using `for`, not close-forwarding delegation into the borrower. Root adapter close releases its local generator without taking ownership of caller reader. **Code review only for borrowed future-batch usability here**, not a rerun of the old broad matrix. Actual owned Arrow/Parquet guard resources are independently tested below. |

No material source/security/correctness blocker found in this limited cleanup repair. No new caller-to-owner conversion, exception suppression, ownership/close-error policy or byte-budget change is proposed. Does not certify every exotic adapter or later producer changes.

## Exact test subset and native OS observations

| Executed group | Count | Result / immutable expectation |
|---|---:|---|
| Unchanged5ba author P1 test file, once |5| Owned JSONL planning/late collision/selected-path planning close promptly while traceback retained; borrowed generator stays usable; borrowed second-line JSONL stream stays open. Exact87line Gitbytes above. |
| Original R13–R15 reducer-state ownership failures, unchanged, once |4| CSV/JSONL/Arrow IPCstream/Parquet each reach **actual16MiB guard** with32prefixrows/**input_count256**, traceback frames`normalize→add→_check_retained_bytes`; real acquired resource `.closed==true` and Windows rename succeeds **BEFORE test-owned cleanup**. Original postcleanup rename also succeeds. |
| NEW owned CSV/JSONL success |2| Literal3records/count3/warnings[], actual owned file close exactlyonce; original synthetic bytes unchanged before real Win32 rename+unlink; unrelated caller marker survives. |
| NEW late malformed CSV/JSONL × owned/borrowed |4|40valid rows then real malformed syntax; ValueError at CSVline42/JSONLline41, original `csv.Error`/`JSONDecodeError` cause and traceback retained. Owned close1/unlocked; borrowed close0 before explicit callerclose1, seek/read usable and bytes preserved; Windows rename+unlink after correct ownership cleanup. |
| NEW postprefix EIO × owned/borrowed |2| After40actual lines, **same OSError object/errno.EIO** propagates; owned close1 versus borrowed0, retained traceback, real underlying file correct and unlocked. Explicit deterministic fault injection, **not physical disk failure**. |
| NEW borrowed plain iterator error |1| After40rows, same RuntimeError object/traceback propagates; library explicit callerclose count0. No new caller ownership rule. |
| **Total** |**18**| **18PASS/0FAIL/0ERROR/0SKIP4.60s**. No fake tickets or one-case-per-bug claim. |

Original immutable oracle: **`8a10108752567f6d0faac700240c4acf77b32556:tests/r13_probes/role15/test_reducer_source_ownership.py`**, SHA256 **`5a9ebaba4968381624d20f646afbd8105531be4bfd179fe56fa5accb7118314e`**. Extracted byte-exact from Git to own ignored artifacts, not edited. Selected only `::test_reducer_state_guard_releases_owned_source_after_valid_prefix`'s four parameters; **not**21/43/64matrices. Original270finite rows/65,520byte groups/reducer/publicAPI/16MiBguard/prefix/close/Win32 expectations unchanged. Largest actual fixture Arrow17,695,768B; CSV17,691,214B; JSONL17,694,450B; Parquet836,514B. Payload bounds, **not process RSS measurement**. Error/input_count256 is a failure-stage observation, not a successful partial-normalization count or silent-row-loss claim.

## Commands, one launch error and honest execution count

Existing absolute Python executable, `PYTHONPATH=<exact5ba>/python/deepviz/src;<own>/tests/r22_probes/role04`, bytecode/plugin-autoload disabled. CWD `C:/Users/bagma/AppData/Local/Temp/opencode/r22-04-external-run-ses_de5678314ffeuDXtC7RfGsbD6V`, outside both trees. Flags/env and portable recipe in `tests/r22_probes/role04/README.md`.

```text
python -m pytest -p provenance_guard -c <5ba>/pyproject.toml <5ba-author-test>
  <immutable-original-copy>::test_reducer_state_guard_releases_owned_source_after_valid_prefix
  <own>/tests/r22_probes/role04/test_owned_unwind_review.py -q --strict-markers -rs
  --tb=short -o junit_family=legacy -p no:cacheprovider --basetemp <own-unique-basetemp>
  --junitxml <own>/artifacts/local/R22-04/owned-unwind-executed.xml
```

- Actual selected execution **exit0/18PASS4.60s**; `python -m ruff check tests/r22_probes/role04` **0**, `python -m mypy tests/r22_probes/role04` **0/2files**, no source/test changes after those checks. Evidence collector0: JUnit18/no skips, all4original actual closed/rename/count/stage properties verified,11raw hashes and3NEW file hashes, clean5ba/source/module exact, own source diff0, expected ownref9be/helpermanager/author verified; **APIcalls0**.
- Initial PowerShell launch **exit4, zero tests**: `--basetemp=(Join-Path...)` reached argv as empty`--basetemp=` plus separate path (same junitxml issue). Minimal argv diagnostic reproduced then verified separate option/value correction; both diagnostics0. Initial XML/sessionstart receipt absent; original launch log/exits preserved. Corrected run is the **only actual author/original execution**, not an unauthorized replay or product failure. No own-test correction or production edit.

## Disposition and handoff

- **Accept only this cleanup P1 fix subset at5ba:** four original retained-traceback reducer resource failures independently becomeGREEN; original author tests and nine genuinely independent controls support owned unwind without borrower takeover. No uncovered counterexample; do not invent one or call this final16approval. Other normalizer math/GraphQL/SUM work, actual producer handoff and integrated final-candidate gates remain separately owned/unproven.
- No render/spec semantics changed; real OS handle/rename/unlink is the relevant output. PNG/browser visual artifact **N/A**, not silently skipped or a PNG acceptance claim. No full test/build/global type/lint/npm/TS/SUM/R21recommendation/10M/RSS/API/provider/release/CI/issue-closure/900work performed.
- **Current action:** explicit own3NEWprobe/docs+report+compactJSON+ownnote stage/scope/secret/hash/whitespace check, meaningful owncommit/non-forcepush/exactremoteSHA receipt; no source integration/sharedGit. Postpush actual receipt follows only observed remote result.
- **One executable next action for R04:** inspect this exact source-specific review/test commit, retain strict original ownership oracles and borrower-preservation constraints; use narrow5ba P1 evidence while obtaining actual16final committed handoff, then independently verify the frozen integrated candidate before issue closure/release. Do not merge all unrelated branch history or substitute this partial test review for four genuine final-head reports.
