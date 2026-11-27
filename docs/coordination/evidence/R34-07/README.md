# R34-07 actual Python data foundation

## Product, not just evidence

Owned branch: `feat/r34-python-data-foundation`.
Exact stacked base: `bff9384d1ebe5c8f6f8f0f994300264b32bb98d8` (not an assertion of merged main).
Product commits, in order:
1. `a711ea5c9f4b97d53a80e1cac86c42e25c9d4dbc`: actual data-only package, resources, metadata, original prerequisite/test closure, new public consumers and minimum CI.
2. `9ce04fcc0e91c1896979e3efb9740294dae38240`: one-line wheel-only exclusion plus the permanent offline-wheel regression; canonical resources forced exactly once.

Review the full **bff..9ce product range**, not only the last packaging fix and not the later evidence-only tip. Actual non-force source publication/exact remote readback is in `source-publication.json`. R04 alone integrates/default-merges/changes PRs and issues; no author signoff is independent review.

The initializer exports `ChartSpec`, `NormalizedData`, `Artifact`, `normalize`, `read_prompt`, `__version__`; it imports no absent render/tools/CLI/MCP module. Required dependencies, optional extras and declared hatchling backend are unchanged. Only the two dangling console scripts are deferred, with a truthful staged README. The full toolkit/v1 goal is not reduced.

## Immutable source and original tests

`immutable-inputs.json` binds 20 files to actual Git blobs. Normalizer is **EXACT c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19**, SHA256 `f3cc6e78e188ed97f62133a954154dbfdd416128c97cd4b154144ae62f778296`; verified history includes **5ba860305dcc86ac2f95f01705b984d2b40f2799**. No normalizer fix/cap/source modification. Models/canonical schema and focused82 tests stay bff; no old728 model is copied over the Mapping guard. Original normalization/aggregation/GraphQL/N04/N19/R07/schema/resource-policy/107-line packaging tests and benchmark/export scripts are copied whole from their exact authorized commits, not stubs.16's P1+mean test file stays whole at c1.

Protected bff files are CRLF in this Windows checkout but LF Git blobs. Both actual raw and canonical hashes are recorded; no protected file was rewritten. Archive checks compare actual build-input bytes, with Git provenance recorded separately. This is not an excuse to patch original oracles.

For a fresh independent **exact-source** run, use your OWN clean9ce worktree/output dirs and an existing approved read-only Python environment. Do not install dependencies under this assignment. Put that worktree's `python/deepviz/src` and its approved runtime site-packages on process-only `PYTHONPATH`; run Python with `-S -B` to avoid editable `.pth` hooks. `verify-and-test.py <OWN_ROOT> <pytest arguments...>` performs same-process source/import proof before pytest. The c1 commit/history must already exist in the read-only Git object store; do not silently omit the proof if unavailable.

Useful actual commands (replace only owned root/output paths):

```console
python -S -B verify-and-test.py <OWN_ROOT> tests/test_r34_data_foundation.py -q -p no:cacheprovider --basetemp <OWN_TMP>
python -S -B verify-and-test.py <OWN_ROOT> python/deepviz/tests tests -m "not integration and not scale" -q -p no:cacheprovider --basetemp <OWN_TMP> --junitxml <OWN_XML>
python -S -B -m ruff check --no-cache python/deepviz/src/deepviz tests/test_r34_data_foundation.py tests/test_r34_offline_wheel.py
python -S -B -m mypy
python -S -B scripts/export_schema.py --check
```

## Observed results — NOT a green merge

- Public small11: actual11FAIL before API/resource/metadata changes → SAME11PASS. The only subsequent new-test change was import sorting, with all non-import AST bodies proven equal. Exact executed pre-format test is preserved externally; its digest is in the RED/GREEN receipts.
- Full shipped originals/new public tests: **483PASS / 9FAIL / 0ERROR / 0SKIP / 5integrationDESELECTED**. Focused bff82 and16 P1+mean26 all pass. Counts by original file are in `per-file.json`; all nine exact failure IDs are in `preserved-gates.json` and `full-shipped-data.log`.
- Four64KiB-field policy failures vs unchanged4096-byte field limit, five raw-dashboard-schema failures. None xfailed, softened, reclassified successful or fixed outside07 authority.
- Source+new-consumer Ruff0; project mypy0/3sourcefiles; positive public type consumer0 and negative expected1 with exactly2arg-type errors. Full-root Ruff remains **12 I001**, all in immutable original test imports; `full-root-ruff.log` preserves every finding.
- Exporter `--check` remains1 against exact protected bff schema serialization, although JSON semantic equality passes; R04 owns the schema prerequisite. No schema regeneration here.
- Original107-line packaging fixture **five cases BLOCKED / deselected**: it performs default isolated builds and pip/venv operations not authorized here. This has NOT been replaced with a fake pass. Installed typing/clean dependency-resolution acceptance remains unrun.

## Real offline build, failure and repair

`backend-current.json` revalidates only the six already-extracted previously owned cache roots: hatchling1.33.0 and five active dependency requirements, **183 existing files rehashed unchanged**. No downloads, installs, shared venv/cache changes or backend substitution. Backend origins/hashes are actual; prior R06 results were not borrowed as current acceptance.

First clean a711 default build really made a sdist, then failed on duplicate wheel resource destinations. That failure/partial artifact identity remain in `build-first.json` and `build-first-stderr.log`. New permanent `test_r34_offline_wheel.py` genuinely1RED → SAME1GREEN after the one-line wheel exclusion; it inspects a real wheel, unique canonical resources, exact three Python modules, typing marker and absent dangling entrypoints. No original packaging test was edited.

On CLEAN9ce, process-only verified backend paths, own short TEMP, `PIP_NO_INDEX=1`/`UV_OFFLINE=1`:

```console
python -S -B -m build --no-isolation --outdir <OWN_DIST>
python -S -B -m twine check --strict <ACTUAL_WHEEL> <ACTUAL_SDIST>
```

The first command is the real default **sdist → wheel FROM sdist** flow, exit0/3.838s; strictTwine both archives0. Current artifacts retained only in owned temp storage:

- Wheel21,015B: `0b297fd5e6232c41b23090f356ea9880416321d85219ec80c4f55097f3d39fd6`.
- Sdist56,633B: `de00145da6b6d31451701cf173e1a1ba64a237a46cd601c1d56f4238ba4e515e`.

`archive-manifest.json`:11 unique wheel entries,42 sdist files, actual legal/metadata/schema/prompts/PEP561, full immutable source/test bytes. No fabricated assets/rendering/CLI/MCP shipping. Byte hashes describe this observed Windows build, not a cross-platform reproducibility claim.

Fresh archive materialization into an empty owned target, external `-I -S -B` consumer: **actual0**; every loaded package module originates inside that target and matches actual wheel bytes, no checkout/cache fallback. Literal COUNT A2/B3/C1/input=consumed6,100→10 warned sample, schema/prompts/marker all checked, all unshipped/optional renderer SDK imports forbidden by a real import guard. Runtime Pydantic reuses the existing read-only shared dependency directory and its origin is recorded. This is **a real built-artifact consumer, NOT pip installation, independent clean dependency resolution or installed PEP561 type-discovery validation**.

## Handoff limits and next owner

Known9 semantic REDs, exact schema export1, full-root original lint12 and original packaging/clean-install gates remain honest draft blockers. Later16 scalar/GraphQL/prefix-SUM handbacks were not adopted without R04 permission. No browser/10M/npm/full-toolkit replay, remote CI result, independent review/test approval, main merge, issue closure or900 claim.

R04/root next: inspect the actual package code/range and source-specific evidence, allocate genuine independent reviews/tests, resolve policy/schema/16/clean-install blockers, and revalidate affected gates at its actual final merged source. R35's "unstarted" deferral versus ROOT's actual R34 acceptance/current direct dispatch is documented in the report; no finite-SVG review completion was invented.07 does not spawn or override manager/dispatcher ownership.
