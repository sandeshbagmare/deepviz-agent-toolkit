# Role07: exact-checkpoint clean Python distributions

This is an independent issue [#24](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/24) acceptance harness. It does not change production code, install into a shared environment, or certify a later source revision.

## Replay

Use an existing Python 3.12+ interpreter. Choose a **new short external output path** (Windows path length matters), and the exact Git SHA being tested:

```powershell
$Source = (Get-Location).Path
$Sha = (git rev-parse HEAD).Trim()
$Output = 'C:\Users\bagma\AppData\Local\Temp\opencode\role07-fresh-run'
python -B tests/r10_probes/role07/run_clean_distribution.py --source $Source --expected-sha $Sha --output $Output
```

The output path must not exist and must be outside the checkout. No deletions/reuse/reset are performed. This command requires network access to public PyPI unless its requirements are already available through the interpreter's public installation mechanism; no private index configuration is inherited. Only requirements declared in `pyproject.toml` and their resolver dependencies are installed, exclusively into the three new disposable environments:

- **build-env:** declared Hatchling backend and declared `build`/`twine` tools;
- **wheel-env:** actual new wheel and its base runtime dependencies;
- **sdist-env:** declared Hatchling backend, actual new sdist, base runtime and declared `mcp` extra.

After both consumers, the declared mypy tool is installed **only into build-env**. It type-checks positive and deliberate `str`→`int` negative examples against each installed consumer interpreter. Both negatives must exit1 for assignment incompatibility, not an untyped/missing module. The main runner includes the same typing recipe already exercised by the bounded recovery continuation; the existing artifacts were not rebuilt to add that portable orchestration.

`git archive <exact SHA>` supplies the build source so uncommitted probes/reports cannot contaminate the sdist. The default frontend builds the wheel **from the new sdist**. Strict Twine and a separate all-member/source-byte/RECORD inspection check the actual archives. The sdist consumer also performs a direct no-build-isolation pip install of that sdist with its own declared backend.

Both consumer probes run `-I`, assert no system/user/shared import fallback, verify all nine package module bytes, package/schema/prompts/license/typing marker and PEP610 archive provenance, execute both actual console entrypoints, and render local Matplotlib PNG and native Vega SVG through the installed CLI. A local installed vl-convert SVG→PNG preview makes the genuine Vega output viewable without a browser/network. The strict MIME-aware oracle rejects wrong PNG bytes/non-SVG XML; it does not pretend every engine emits PNG. The wheel consumer proves optional packages are absent; its MCP transport case is deliberately not run. The independent sdist-with-MCP consumer executes the actual console stdio server: initialize, discover seven tools, normalize→recommend→render, retrieve PNG bytes matching inline content, reject unauthorized file input, and shut down. No paid provider, Deep Agent extra, browser/CDN rendering, matrix compatibility, scale, remote CI or final-source acceptance is implied.

Every completed child command appends exact argv/cwd/exit/elapsed evidence and preserves separate stdout/stderr in the new output directory. Any failure is retained; do not rerun into that directory. `result.json` is an honest partial checkpoint if interrupted. Package/dependency versions and isolated origins are retained in per-environment result files, not borrowed from an earlier wheel.

## Harness controls

```powershell
python -B -m pytest tests/r10_probes/role07/test_clean_distribution.py -q
python -B -m ruff check tests/r10_probes/role07
python -B -m mypy --follow-imports=silent tests/r10_probes/role07/run_clean_distribution.py tests/r10_probes/role07/inspect_archives.py tests/r10_probes/role07/consumer_smoke.py
```

Controls reject shared imports, inherited Python/private-index configuration, accidental dependency scope expansion and reused outputs. They do not replace actual installed consumers. Review the rendered PNG itself before visual approval. Publish only compact sanitized results/one small meaningful image—not venvs, caches, logs containing credentials, datasets or dependency trees.
