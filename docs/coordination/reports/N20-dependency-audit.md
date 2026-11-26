# N20 installed dependency / CDN / supply-chain audit

- Status: IN PROGRESS; initial checkpoint 2026-11-27 (local +05:30).
- Owner: N20, dispatched by C17; runtime child session ID not exposed to this session.
- Assignment: `docs/coordination/tasks/N20-dependency-audit.md` and `C17-wave-common.md`.
- Branch: `release/candidate`; base/current source SHA `b6abc8d9b80a8dd4e3813e5d4ef28f17f1788835`.
- Initial dirty state: tracked `AGENTS.md`, `opencode.json`; untracked `RESUME.md`, `docs/coordination/`. These are preserved; not N20 edits.
- Allowed writes: this report and unique evidence under `artifacts/local/N20`; no source, Git, shared environment changes, installations, lockfile changes, or spawning.
- Initial command: `git status --short --branch; git rev-parse HEAD; git worktree list --porcelain; Get-Date -Format o` — exit 0; source identity confirmed, worktrees preserved.
- Acceptance checks: actual `npm audit --json`; installed Python dependency metadata/consistency and actual advisory-version checks where available; runtime imports vs wheel/npm declarations; CDN pins/integrity and offline boundary; license/notice/assets; Python/Node compatibility and reproducibility boundaries. Findings require concrete repro, severity and N07/N08 owner.
- Current action: reading common contract/recovery/package declarations before read-only audit.
- Next executable action: inspect `pyproject.toml`, `package.json`, lockfile and renderer CDN imports, then save bounded machine-readable audit evidence.
- No test/advisory pass claimed yet. The existing zero-vulnerability npm-ci summary and installed extras are baseline only.

## Checkpoint 1 — installed graph and actual advisory queries

- `python -B artifacts/local/N20/inventory.py` using main `.venv/Scripts/python.exe`, explicit main `PYTHONPATH`, bytecode disabled — exit 0. Captured 118 installed Python distributions, 179 npm lock entries, all 15 non-stdlib Python import sites, package requirements/licenses and exact source/lockfile SHA-256 in `artifacts/local/N20/{python-installed,source-inventory,npm-lock-inventory}.json`.
- Queried the official PyPI exact-version JSON endpoint for each installed distribution (2026-11-26 UTC / 2026-11-27 local). 117 public versions returned metadata with zero `vulnerabilities`; unpublished local `deepviz-agent-toolkit==0.1.0` returned expected HTTP 404. This is **PyPI's advisory coverage only**, not proof of universal safety. Full bounded results: `pypi-exact-version-advisories.json`.
- `npm audit --json --ignore-scripts --cache artifacts/local/N20/npm-cache` — exit 0; actual registry audit reports 0 info/low/moderate/high/critical vulnerabilities (180 dependency count in npm's report). Saved `npm-audit.json`. `npm ls --all --json` — exit 0; installed graph saved `npm-installed-tree.json`.
- Environment: Windows 11 x64; main Python 3.12.16; Node v26.13.1; npm 11.20.0. `python -B -m pip check` — exit 0, no broken requirements. Import identity: `C:\Users\bagma\deepviz-agent-toolkit\python\deepviz\src\deepviz\__init__.py`.
- `npm pack --dry-run --json --ignore-scripts --workspace @deepviz/agent-toolkit --cache artifacts/local/N20/npm-cache` — exit 0; 22 planned files, no bundled dependencies, includes LICENSE and schema. No prepack/build/source mutation. Saved `npm-pack-dry-run.json`.
- `python -B -m build --no-isolation --wheel --outdir artifacts/local/N20/dist` — exit 1: shared environment intentionally lacks `hatchling`. This is a tooling boundary, not a product defect; no shared install attempted. Saved `python-wheel-build.log`.
- Switched to isolated build with `TEMP`, `TMP`, `PIP_CACHE_DIR` under N20 artifacts; `python -B -m build --wheel --outdir artifacts/local/N20/dist` — exit 0; isolated hatchling 1.33.0, wheel created. No shared env changes. Saved `python-wheel-isolated-build.log`.
- Preliminary boundaries: Python embeds Plotly.js **3.7.0** from installed plotly 6.9.0, while root npm tests pin Plotly.js 4.3.0; Python ECharts CDN pins **5.6.0**, while root npm pins **6.1.0**. Therefore root npm audit alone does not cover Python browser payload dependencies. Not yet classified as a vulnerability.
- Current action / next executable action: inspect actual wheel METADATA/contents and CDN bundle license/integrity/advisory metadata; produce concrete owner repros without editing production code.

## Confirmed finding F1 — moderate dependency advisory outside npm-ci/audit coverage

- **Owner N07** (dependency/build gates; coordinate Python renderer pin with N05); **N08** documents the effective browser dependency inventory/advisory boundary. Source `python/deepviz/src/deepviz/engines.py:26,650-652` emits ECharts **5.6.0**, not the npm-lock-tested **6.1.0**.
- Actual CDN URL returned HTTP 200; SHA-256 `bf4a223524e40b77c304bec67e1222cf551f14880cf42c69dc046558e11c07b1`. Official npm bulk advisory POST for the actual browser versions returned **GHSA-fgmj-fm8m-jvvx / CVE-2026-45249**, moderate, CVSS 6.1, affected `<6.1.0`, patched `6.1.0`. Full request/response in `artifacts/local/N20/cdn-npm-advisories.json`; asset bytes hashes/SRI in `cdn-assets.json`. Root `npm audit` was genuinely zero because its ECharts is 6.1.0.
- Primary upstream patch: `https://github.com/apache/echarts/commit/1e39b00` and upstream PR `https://github.com/apache/echarts/pull/21608` (merged 2026-05-08). Advisory record: `https://github.com/advisories/GHSA-fgmj-fm8m-jvvx` (published 2026-05-26, updated 2026-06-30). Vendor announcement `https://lists.apache.org/thread/1g6xk7gd9vg1c6zyqqt2lnko10zomc3o` is JS-only in the read tool; upstream patch and registry are readable independent evidence.
- **Reachability qualification:** this is an actual affected shipped dependency, **not a demonstrated DeepViz XSS exploit**. The advisory concerns ECharts **`lines`** series tooltip HTML with attacker-controlled data `name`; current DeepViz `_echarts` emits `line`, not `lines`, and forces `tooltip.renderMode='richText'` (`engines.py:447,455`). These constrain the reported path. Do not label this remotely exploitable in current ChartSpec without a separate repro.
- Exact repro from main: `.venv/Scripts/python.exe -B artifacts/local/N20/assets_and_wheel.py`; inspect `cdn-npm-advisories.json` and `engines.py:26`. Exit 0; all seven unique CDN assets returned 200. Smallest remediation: synchronize the Python ECharts pin to a tested patched version and audit effective CDN/embedded versions in CI, not solely npm lock entries. Re-run semantic/browser acceptance after updating the major version.
