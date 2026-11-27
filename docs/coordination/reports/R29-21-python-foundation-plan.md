# R29-21: smallest usable Python foundation / packaging dependency plan

## Authority, exact inputs and result

- Owner: native SAME-ID `ses_de5678018ffezK8JGDUaSzvcWn`; OWN branch `agents/r10-21-recovery-git-bootstrap`, clean prework base `e2df3e0e42a8094aaebb62ebd0fb878fd128c2ee`.
- FULL MAIN R27 manager queue (25 lines), R29 (48 including role21), current AGENTS (49), canonical and own note read. **R04 alone owns all-branch inventory, priorities, assignments, PRs and releases.** This is one static Python prerequisite proposal, not a competing release plan or source grant.
- ONE remote read `git ls-remote --symref origin HEAD refs/heads/main` at **2026-11-27T15:57:51Z**, exit0: default `main`, **`0ae2cf26426822135fc10d337fcacf580b7ed833`**. No later default/PR/CI state is inferred. Root's 15+3 admission is attributed, not a permanent runtime count or our census.
- Immutable source candidate **`3eab699b61850a20e91132e16caf8c589085f9ee`**; separate sealed MCP **`e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23`**. All inspected product bytes are `git show` blobs, not dirty MAIN/producer files. No all-branch enumeration or API query.
- **Recommendation:** prepare a complete, installable **normalization/library foundation** after the focused numeric-contract PR. Add an intentional data-only public initializer and honest package metadata; do NOT copy the candidate initializer alone or pretend model-only main is a usable toolkit. Defer renderer/tool/CLI claims until their full closures land. This staged feature is not v1/full-production acceptance.
- Scope is only this NEW report, `evidence/R29-21/`, own note and OWN Git publication. **Zero tests, builds, installs, product imports, browser/scale/envelope runs.** Read-only Git/static Python AST/TOML parsing only. No source/config/dependency/workflow/schema/oracle/other-note edits, API/default/PR/closure writes or spawning.

## What exact main actually contains (not what installed packages can do)

`main-tree.txt` is all **7** tracked paths at 0ae2: `.gitignore`, LICENSE, README,
2 design/plan documents, pyproject and **only `python/deepviz/src/deepviz/models.py`**.
There is no initializer, normalize/render/engines/tools/CLI/MCP source, schema, prompts,
typing marker or tests. `main:pyproject.toml:20-25` nevertheless declares
`deepviz = deepviz.cli:main`, `deepviz-mcp = deepviz.mcp_server:main` and the package
root. **Structural reproduction:** compare those two declared module paths to
`git ls-tree -r --name-only 0ae2cf26426822135fc10d337fcacf580b7ed833` (captured,
exit0): neither exists. This is static evidence of dangling entry points, not a
claimed executed import/install failure. A model-contract merge alone cannot fix it.

## Public/source dependency closure at 3eab (file:line references use that commit)

| Boundary | Required exact code / consequence |
|---|---|
| Core models | `models.py:7,16-92`: Pydantic ChartSpec plus NormalizedData/Artifact; no internal module imports. |
| Normalization + streaming | `normalize.py:44,683-769` depends internally only on models. Single source file owns parsing, iteration and reducers; **no separate streaming module**. 32-row prefix and reservoir/reduction paths return records/count/warnings/strategy. |
| Actual stream limits | `normalize.py:226-261,688-700`: Path JSON and auto text streams may read whole content; CSV/TSV/JSONL paths iterate; Arrow batches are4096. 16MiB retained-payload limit is **not RSS or all-input memory boundedness**. Do not advertise arbitrary JSON ingestion as the 10M streaming path. |
| Existing public import | `__init__.py:8-12` eagerly imports models, normalize, **render**; `render.py:15-26` imports **engines**, whose `engines.py:19` imports numpy at module load. Copying just normalize plus this initializer still imports missing render/engines. Minimal unchanged eager closure is5modules, not2. |
| Public factory | `__init__.py:23-27` lazily loads tools; `tools.py:14-15,99,141` additionally needs recommend, normalize and render. `recommend.py:8` needs models. Full public factory closure is7modules. |
| CLI completeness | `cli.py:9-10,16-35,37-52`: imports ToolSession/ENGINES, supports render/normalize/recommend/MCP. Even normalize-only CLI uses tools + recommend; MCP subcommand needs mcp_server. No unchanged standalone normalize CLI can be extracted. |
| Unchanged package + both scripts | All **9** modules: `__init__`, models, normalize, render, engines, tools, recommend, cli, mcp_server. `mcp_server.py:14-23` closes back onto tools/models and imports MCP SDK inside create_server. All relative-import AST edges resolve only with this closure. |
| Installed resources | `__init__.py:16-20`: read_prompt requires `prompts/v1/system.md` and `request.md`; `pyproject.toml:27-29` force-includes schema and prompts into wheel. Include `py.typed` and root LICENSE/README. No evidence that a checkout path proves wheel/sdist inclusion. |
| Renderer assets | `engines.py:737-776`: Plotly JS obtained from installed plotly plus packaged `resources/plotly-js-LICENSE.txt`; other native browser libraries are pinned CDN requirements. `render.py:177+` also has matplotlib and vl-convert paths. No assets/rendering gate may be inferred from package existence. |

## Exact extraction sources; not blanket cherry-pick advice

All candidate file hashes/last modifying commits are in `source-path-provenance.json`.
The listed history explains provenance; extraction must use reviewed final file hunks
on a fresh actual-main branch, preserving newer main changes and original strict oracles.

| File/group | Exact source / history and prerequisite |
|---|---|
| Contract baseline | Focused PR33 source **99841ffb80e0f2ea90c753c1bf0ceff718e0e180** is a proposed prerequisite, not observed merged here. Compared to3eab, its model differs only in dashboard JSON-schema configuration (`focused-contract-model.txt`), not the numeric validator. Preserve that strict validator. |
| Model/schema/export | Take paired model + `schemas/chart-spec.schema.json` from3eab; last pair change **728bbac47b747501ad27f40525220317ea218064**. Numeric validator provenance **e44f667ed494fa272f97792ef99942a364ebca24**; first schema packaging **715c1f5ca0c13c276110c64d2af8c21deca881ea**. Include `scripts/export_schema.py`/original schema tests; do not combine old schema715 with new model728. |
| Normalizer | Final3eab file is **7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6** bytes, not just initial **ba171160de0895f785807e895b4b4cb14dff970e**. Keep intervening4795509 heatmap, f650964 byte/GraphQL,3051823 duplicate/boundary,235e7e3 numeric identity and7bc overflow corrections; full hashes in history evidence. Active16's later work is NOT adopted. |
| Public glue / CLI / recommendation | Existing source first added at **52b817d29eb1fc55538f5b7f8f30d1356e584223**, current candidate init/cli/recommend unchanged since. Data-only initializer/metadata adaptation recommended below **does not yet exist as a reviewed commit**; eligible implementation needs R04's explicit grant. |
| Package resources / typing | pyproject+prompt force-inclusion **f67afac5fb13a7950202671e858491856c72908d**; `py.typed` **8b26852cab342df9c652867a015073b8cc029d18**. Preserve canonical prompt bytes and root legal files, not generated substitutes. |
| Render/engines later | Initial **7c62cc1afc25e413846a94ab25fbac1ea45926e5** is incomplete history. Current3eab renderer/engines last change **1c721bb6497746641b897eb2eb938cfad52068d2**; retain earlier asset/replay **7698c03461a3e88a8fa47ac714532a9bb1170568** and other semantics fixes. Do not overwrite07/08/12/18 active disjoint scopes. |
| Tools/MCP later | 3eab tools is last **4a766c4a2dce49992c09cc4844492ccc6abd9460**, MCP **65b3fc4a4202fd834a524bc2e0ab33c7430f179e**: NOT the later security/resource handback. For integration review separate P1 **d65dfc0fd807d0335b858476de8cdf7c6b958711**, P2 **cd75c459ddba9f3d6bc0a5185b570af369fb4980**, sealed e47. Never merge the whole evidence branch or restore old tools to satisfy CLI. |

## Suggested minimal PR boundary / sequence for R04 to disposition

**P0 prerequisite:** R04 disposes actual PR33 final review/test/CI and obtains its
real merged-main SHA. This role observed only main0ae2; no current PR/merge claim.
Prepare work without waiting on unrelated worker waves, but rebase/revalidate on
actual merged default; do not reapply e44 wholesale over the focused runtime fix.

**P1 usable normalization + Python distribution (recommended first Python product PR):**
- Fresh branch from that actual default, single R04-assigned producer. Extract paired
  models/schema/exporter, final reviewed normalize, `py.typed`, canonical prompts,
  root LICENSE and accurate README; include existing force-inclusion mappings from
  715/f67. New **small data-only initializer** exports ChartSpec, NormalizedData,
  Artifact, normalize, read_prompt and version; retains read_prompt validation/code.
  Do NOT import/render or advertise create_tools yet. This is explicit staged API
  work for an authorized implementer, NOT a source change performed/approved here.
- Explicitly remove/defer both currently dangling `[project.scripts]` entries and
  agents/MCP functionality claims until P3; retain columnar optional extra and build/
  dev metadata. Preserve declared baseline runtime dependencies initially unless
  R04 separately authorizes a dependency split. Static core *needs* only Pydantic
  (plus optional pyarrow); existing pyproject still mandates numpy/matplotlib/plotly/
  vl-convert as well. Do not silently call those optional or alter deps here.
- Include complete original relevant tests: existing focused model tests, schema
  contract, `python/deepviz/tests/test_normalize.py`, test_aggregation_semantics,
  test_graphql_contract, test_n04_{format_guards,normalize_regressions,shape_policy},
  test_n19_{format_regressions,formats}, test_r07_finite_overflow and corresponding
  immutable strict normalizer bug controls/new fixes as R04 receives them.
  **Hidden test prerequisite:** original `test_normalize.py:340-343` runs
  `scripts/benchmark_scale.py --sizes 100 --modes sample sum`; include that script
  intact (it imports normalize at its line56), not a stub. No such command ran here.
- Add unchanged `tests/test_packaging_regressions.py` (107lines) from3eab: build,
  sdist/wheel/prompts/typing/installed-resource and positive+negative type consumers
  all remain meaningful because read_prompt ships. Add NEW installed public-normalize
  generator/count/bound smoke and import-origin/no-render-extra checks; preserve old
  strict tests, no green-by-rewrite. Tests requiring later renderer/tools cannot be
  claimed delivered/passing in this slice; retain originals for their later PRs.
- **After real gates**, user can install wheel, `from deepviz import ChartSpec,
  normalize`, normalize records/JSONL/CSV/finite generators with explicit mappings,
  inspect counts/loss warnings, load schema/prompts and consume inline types. No CLI,
  rendering, agent/MCP/npm/v1 claim. This is an actually useful library milestone,
  not another model-only contract PR or a report-only substitute.

**P2 first real render path, then engine correctness:** after P1, integrate reviewed
render+engines source and Plotly legal asset; explicitly export render. Preserve
candidate budget/replay fixes and obtain current07/08/12/18 immutable handbacks and
applicable original semantic/HTML/finite/layout gates. One successful Matplotlib
SVG/PNG path is an observable next milestone; merely copying current engines.py
also exposes four other engines, so their known failures cannot be hidden by a
single-engine smoke. R04 must choose proper scoped availability or gate the full
exposed matrix; this report grants neither a rewrite nor permission to waive RED.

**P3 tools + complete CLI + MCP:** after P1+required render paths, recommend.py,
reviewed ToolSession/tools and sealed e47 P1/P2 source, merge actual independent02/10
findings and revalidate against new base. Ship both cli.py/mcp_server.py together
with their advertised scripts, plus `[agents]`/`[mcp]` metadata/docs and real SDK/stdio
consumers. Preserve raw JSON duplicate/byte handling, resource lifetime128 policy,
authorized local path containment and caller-file preservation. Do not wire CLI to
old unguarded candidate tools just because its imports resolve. If R04 requires a
CLI in P1, it must explicitly assign/test a NEW standalone normalize CLI; the old
candidate CLI is NOT such a slice. No proposal is counted as implemented.

**Alternative if R04 requires the candidate public API unchanged:** P1 necessarily
expands to all9 modules + complete resources/scripts and gates of P1-P3, including
latest tools/MCP fixes; it is not a two-file foundation. That is larger and blocked
by renderer/security source gates. Do not silently substitute it for the recommended
small usable data library. Global release ordering/other branches/npm remain R04's.

## Build / runtime / optional-extra prerequisites and actual blockers

1. `pyproject.toml:1-3` at main AND candidate requires **hatchling>=1.27 / hatchling.build**.
   Read-only current MAIN venv site-packages listing has `build`+build1.6.1 metadata,
   **no hatchling directory/dist-info match** (`dependency-edges.json`). No module
   import-resolution/build attempted here; alternate interpreter/path state remains
   unverified. Immutable e47 author handback `R14-18-mcp-json-budget.md:11,23-26`
   separately reports prior offline `build --no-isolation` exit1 missing hatchling.
   That old failure is attributed, not a fresh command or package-code diagnosis.
   **R04/environment owner must supply an authorized backend in an isolated build
   environment/offline wheelhouse or working CI.** Do not swap backend, use borrowed
   wheel/editable source or relabel source-import success as a distribution build.
2. `pyproject.toml:12`: base Pydantic2.10<3, numpy1.26+, matplotlib3.9+, plotly6<7,
   vl-convert1.7+ are currently REQUIRED. Renderer module import needs numpy even
   before plotting. `[columnar]` pyarrow19+ is optional; `normalize.py:161-165` raises
   actionable ImportError only when Arrow requested. Base/data consumers must not
   silently need pyarrow or agent/MCP extras. Test those separately with and without.
3. `[agents]` deepagents0.3+ / langchain-core1<2; `[mcp]` mcp1.12<2.
   `tools.py:175-180` imports StructuredTool only inside factory; MCP SDK imports
   inside create_server. Lazy *dependency imports* do not excuse missing local
   modules behind registered scripts. Directory/version listings are NOT installed
   consumer or minimum-version compatibility tests. No provider calls needed here.
4. Normalizer7bc remains only a source candidate. R27/active16 assignments report
   GraphQL error-carrier, cleanup/mean/scalar/prefix-SUM work; prior SUM limitation
   remains open in canonical. Not independently reproduced in this static scope.
   R04 must receive exact committed16 fix and unchanged strict-review/test evidence
   for affected shipped behavior, or explicitly block P1; **never copy dirty work,
   revert to ba to evade controls, or claim these issues solved by packaging**.
5. Optional/full integration prerequisites: original cross-language/all-repo tests
   may need npm source/dist. e47 author full run reports42fail2521pass5skip520errors
   with517missing npm prerequisites and missing backend (NOT rerun, NOT subtracted
   to green). Do not add unshipped npm-dependent tests to P1 then ignore their errors;
   once claiming full toolkit run, build/validate own npm prerequisite first and
   retain every actual failure/skip. R04 owns the separate npm prerequisite plan.

## Acceptance commands / outputs to request, ALL PROPOSED / NOT RUN HERE

R04 assigns one producer, two independent reviewers and two independent testers per
exact product PR, links a real existing/deduplicated issue (no invented issue/PR ID),
and records exact final source, all results/skips, actual CI and default ancestry.
This planning author is not a package reviewer/tester signoff.

- Data/schema: on exact P1 source and approved dependencies, `python scripts/export_schema.py --check`;
  `python -m pytest tests/test_models.py tests/test_schema_contract.py python/deepviz/tests`;
  `python -m ruff check .`; `python -m mypy`. The proposed pytest directory must
  contain the original relevant files listed above, not renderer/tool tests for code
  not in this slice. Also retain/run the actual focused33 strict oracles by their
  final paths; do not overwrite them with old candidate test_models. Snapshot inputs,
  per-file collected IDs, exact command exits/totals and any optional-columnar skips.
- Distribution: in an authorized clean environment with declared backend,
  `python -m build --outdir <fresh-external-dist>` (sdist then wheel from sdist),
  `python -m twine check <exact-built-files>` and
  `python -m pytest tests/test_packaging_regressions.py`. Backend isolation may
  need authorized network/offline dependencies; these are not executed installs.
  Inspect archive allowlist/entry_points/dist metadata, legal files, schema/prompt
  byte equality and py.typed. Installed wheel and sdist-rebuilt wheel must have
  functional identical public-normalize/resource/type consumers from outside
  checkout with own module-origin evidence, no editable-sitehook masquerade.
- P1 public-consumer expected behavior: finite generator consumed once; input_count
  equals actual consumed count; records <=max_points, exact numeric/category values
  and honest strategy/loss warnings. Add a clean wheel-only no-MCP/no-LangChain/
  no-pyarrow import path plus optional-columnar success/error controls. File refs
  remain host-authorized Paths; never turn data strings into filesystem authority.
- P2: actual exact-shipped-engine SVG/PNG/browser output and semantic comparison;
  zero browser console/page errors/unexpected network; inline script/text/HTML
  injection and caller-file preservation negative controls. Include strict original
  renderer/count/channel/finite/legend/title/table/dashboard tests and known fixes.
- P3: installed `deepviz --help`, normalize/recommend/render subcommands and
  `deepviz-mcp --help`/real stdio SDK list/call/read; correct extra-missing messages,
  actual128-resource boundary, duplicate/raw-byte/recursion tests and independent
  security/transport reports, no arbitrary filesystem or executable-schema access.
- Release-scale: only after immutable actual source/runner/test/config and imported
  child provenance gates, run10/1K/100K/1M/10M real streaming with counts, values,
  time and stated RSS methodology. Prior R22 envelope39synthetic fixtures prove
  **none** of these measurements or same-process origins; no replay in this role.
  Report partial/failed/skipped evidence honestly, never announce v1 from this plan.

## Evidence, static findings and disposition

`evidence/R29-21/startup.json` contains exact initial branch/SHA/clean/log, candidate
identity and single remote-default command/exits/stdout. `main-tree.txt` and
`candidate-tree.txt` are immutable trees. `static-inputs.json`, scoped history/diff
files and `source-path-provenance.json` bind source paths to commits/bytes. Raw Git
blobs are under `inputs/` only as evidence, not executed/new product source.
`dependency-edges.json` is AST/TOML plus local directory-list evidence;
`normalization-test-prerequisites.json` captures test imports/benchmark dependency.
`static-assertions.json`: **14/14 structural assertions true,0false** (not14tests).
No command proposed above was run; no present-build or final-package approval.

Actionable findings, structural reproduction and smallest owner decision:
- **Main dangling scripts:** main pyproject20-22 versus7-file tree; R04 P1 must
  deliver modules or remove unavailable scripts. Not a new remotely filed bug.
- **Incomplete naive extraction:** candidate init8-12 -> render15-26 -> engines19;
  copying only init+normalize lacks eager dependencies. R04 chooses explicit
  data-only staged API (recommended) or all9module unchanged closure and its gates.
- **Missing build prerequisite:** declared hatchling versus empty current local
  hatchling listing + attributed prior build1; R04/environment owner supplies
  backend, not an unauthorized install/backend switch or a fake passing command.
- **CLI is tools/security coupled:** cli10/38-52 and tools141 -> render; existing
  normalize CLI is not independent. Ship P3 closure including reviewed e47 fixes
  or explicitly authorize a new narrow CLI; no unreviewed source introduced here.

Next executable decision for **R04**: approve P1's exact staged API/metadata boundary,
assign its producer + independent gates, and obtain immutable16 fix dispositions and
an authorized hatchling build environment. Prepare data+distribution PR on the actual
focused33/default base; do not wait for the whole branch inventory to draft useful
code, do not merge dependency/semantic RED. Root handles supported dispatch only.
Remaining global branches/priorities/schedule/PR IDs/releases belong to R04; no ETA,
project percentage, CI green,900-issue completion or worker adoption is invented.

Publication status at report assembly: own scoped commit/nonforcepush/readback next;
only actual receipt will establish publication, not this sentence.

Final static integrity before publication:40 immutable source/evidence blobs,301624B,
all bytes rechecked by exact Git-show(exit0),20 full commit objects present
(cat-file batch exit0),14 structural assertions true/0false, heuristic secret0.
These are static integrity observations, NOT unit/package/consumer pass counts.
Source/query commands and hashes remain in frozen-input-manifest/startup/evidence.

## Actual OWN publication (not package approval)
C1 **4839c0d026a7deec247b41c57af8a9da7435e6b4** committed65ownedpaths;
2026-11-27T16:11:51.762918Z-16:11:58.034135Z nonforcepush0/ownremoteSHA0exactC1.
Only plan/note/evidence (raw immutable source snapshots are evidence, not product).
Precommit64payloadfiles449431B+stageintegrity, staticAST/sourcebytes/scopechecks0,
heuristicsecret0. No productimport/test/build/install/browser/scale/envelope/API.
This small receipt checkpoint will embed actual C1 receipt; final C2 receipt remains
MAIN-only rather than pretending a commit can contain its own future publication.
