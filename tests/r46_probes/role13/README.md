# Actual-default distributions, not another model-unit replay

`distribution_probe.py` has three finite phases, each executed once for the one
officially frozen actual default. Run with the existing Python and **`-B -I -S`**,
fresh OWN run/evidence paths, outside all source checkouts. The saved source/cache
receipts bind the exact default and every tracked raw/GitLF/backend file.

`build` calls the unchanged declared hatchling PEP517 hooks directly: sdist, safe
manual extraction, then wheel FROM that sdist. This is a real offline hook-level
build, **not** an isolated frontend invocation. Only the six exact existing
cached-backend paths are added, with all183 files rehashed before/after; no install,
backend substitution, dependency download or environment mutation. Backend temp
archives use a child-only `tempfile.tempdir` override restored after the build.

`inspect` checks archive path safety, uniqueness, source bytes, metadata,
requirements, entrypoints and wheel RECORD hashes, then manually materializes
the actual wheel. `consume` imports only that wheel's model module, using the
existing read-only Pydantic dependency explicitly; it records real ChartSpec JSON,
Artifact metadata and origins. It does **not** perform pip installation, clean
dependency resolution, installed PEP561 discovery or renderer/CLI/MCP tests.

The namespace/top-level-export/py.typed/missing entrypoint-target limitations of
this model-only default stay explicit under existing #24/#5. The consumer exits1
if advertised entrypoints cannot resolve, while separately recording model-only
subset success. No skip/xfail/new bug padding or source fix. No82/30/4/schema3
test replay. Exact commands/results/artifacts live under `evidence/R46-13/`.
