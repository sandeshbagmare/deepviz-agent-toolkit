# R23 COUNT channel repair: exact source and independent retest

Source repair **85796dbe3360fb88686f2e7188122e2da80d54c2** changes exactly two
lines inside `engines.py::channels`, plus a NEW permanent 16-case test file.
Normalizers, schemas, metadata, `_antv`, all other renderer functions and all
existing oracles are unchanged. R04 alone integrates this source commit.

The normalizer writes `count` for explicit non-heatmap COUNT without named y.
The mapper must select that measure rather than retained numeric color/size.
Named y, SUM/mean/min/max/NONE, actual auto COUNT, scatter, zero/null/missing,
heatmap axes, retained color/size and nonmutation have positive controls.
`auto` is intentionally not reinterpreted: the planner may select SUM when a
numeric measure is available. A raw field merely named `count` is not authority
to replace another measure.

## Observed producer checks, not independent approval

- Before edit: permanent16 **4 failures /12 passes/0 skips** (bar/line/bubble
  measure and malformed direct-helper missing-count boundary).
- Same unmodified test after two-line fix: **16 passes/0 skips**.
- Immutable17 `76cac9d05b0b4abc94e5ff316e3de4d3bc835b79` semantic checks:
  **55 passes/0 skips/1 identity-only deselection**. Its old identity test
  hardcodes5340; it was not edited. Four actual corrected-source module bytes
  were verified separately against the chosen source Git blobs.
- Connected existing aggregation/render regressions: **167 passes/3 opt-in
  browser skips/85 all-kind-render cases deselected**. No hidden full-suite pass.
- Scoped Ruff/project mypy/whitespace checks passed. Existing dependencies were
  read-only; no installs or shared caches/environment/source changes.
- All five native engine measures and manifests emit literal A2/B3/C1/6→3/count,
  retaining numeric legend labels90/80/70. Actual Matplotlib and Vega static
  images plus two genuine Plotly browser fixtures were opened. The unchanged17
  browser reports2 strict passes/0 console/page/request errors. ECharts/G2 native
  values/HTML were checked, **not** browser-painted/CDN-health accepted.

Complete commands, source/oracle hashes, raw-log identities, failure history,
three skip names and opened images are under `docs/coordination/evidence/R23-07/`.
The exact source commit is distinct from later evidence-only commits.

## Minimal independent recipe

Use a fresh worktree at exact85796db (or R04's actual integrated commit after
source-equivalence verification), existing installed tools read-only, and NEW
artifact directories. Do not borrow the producer's imported modules/builds.

```powershell
$Python = '<existing-venv>/Scripts/python.exe'
$env:PYTHONPATH = "$PWD/python/deepviz/src"
$env:PYTHONDONTWRITEBYTECODE = '1'
& $Python -B -m pytest python/deepviz/tests/test_r23_count_channel.py -q
& $Python -B -m ruff check --no-cache python/deepviz/src/deepviz/engines.py python/deepviz/tests/test_r23_count_channel.py
& $Python -B -m mypy --cache-dir <own-new-cache> python/deepviz/src/deepviz
```

Extract `count_contract.py`, `test_count_measure.py`, and `browser-count.cjs`
from immutable17 commit76cac9d with byte-preserving Git output. Require test
SHA256`c09f6a052afb4822e3bf06e6877d2e061810fd71d423049152c2b098f9325d54`,
contract`0e0d468a5d70a3f36f8dda088ffa09e73da031952168e0ecd0cd6918b1940cd1`,
browser`84ca2c022efdb08624f8e082fd0d6dc8d8a22cc8ce1097f91f843aff52159eee`.

```powershell
& $Python -B -m pytest <immutable17>/test_count_measure.py -q -k 'not loaded_modules_match_pinned_source_identity'
```

Require55 semantic passes/0 failures/0 skips and explicitly1 identity test
deselected. Independently compare actual loaded `models/normalize/engines/render`
files against exact chosen-commit Git blobs and record origins/hashes before
claiming source identity. Never alter the old identity test or silently pass a
skip, and never relabel a5340 result as current-source validation.

For actual bounded output use this NEW collector (from an evidence checkout) with
PYTHONPATH pointing to the separate exact source checkout:

```powershell
& $Python -B <evidence-checkout>/tests/r23_probes/role07/outputs.py --source <exact-source> --expected-sha 85796dbe3360fb88686f2e7188122e2da80d54c2 --oracle-dir <immutable17> --output <new-output>
$env:NODE_PATH = '<existing-installed-node-dependencies>/node_modules'
node <immutable17>/browser-count.cjs <new-output> <new-browser-output>
```

The unchanged17 browser uses installed Edge on Windows; if absent, record that
actual limitation rather than installing or passing a skip. It checks real
interactive Plotly values, geometry within0.1px and pointer hover, with no
external requests. Open actual PNGs. ECharts/G2 HTML requires its disclosed
exact-version network runtime; native payload success is not browser/CDN proof.

No full-project/scale/npm/distribution/CI/release/independent-approval claim is
made here. No issues were created or closed; this repairs the existing known
R03-01/R15-17 COUNT cause, not a new batch of tickets.
