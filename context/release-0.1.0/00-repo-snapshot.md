# Repository snapshot

- Default branch: `main`
- Main SHA analyzed: `484ff08ddcae6c36d43ce61de774c00b6c422c88`
- Date: 2026-11-28
- Plan version: 1.0

## Repository and stack

- `sandeshbagmare/deepviz-agent-toolkit`; verified default branch `main`; SHA `484ff08ddcae6c36d43ce61de774c00b6c422c88`, commit date 2026-11-27.
- GitHub reports Python as primary/only language. Main `pyproject.toml`: version 0.1.0, Python >=3.11, Pydantic 2, NumPy, Matplotlib, Plotly, vl-convert.
- Main contains the ChartSpec model/schema and five test files. README states "Python-first, schema-driven visualization tools for Deep Agents and MCP" and "Under active construction." No npm workspace/TypeScript on main.

## Build and CI

| Purpose | Command |
|---|---|
| Tests | `python -m pytest -q --strict-markers` |
| Lint | `python -m ruff check .` |
| Types | `python -m mypy` |
| sdist/wheel | `python -m build` |
| Clean install | Install wheel in a fresh venv; import `deepviz.models.ChartSpec`; exercise CLI and optional MCP entrypoint |

`.github/workflows/chart-contract.yml` runs Python 3.11/3.12/3.13; pytest, Ruff and mypy. It does not build distributions or test renderers/integrations.

## Current main verification

| Check | Evidence | Result |
|---|---|---|
| GitHub CI | API check-runs for `484ff08ddcae6c36d43ce61de774c00b6c422c88` | 3/3 success (3.11, 3.12, 3.13) |
| pytest | Exact `git archive origin/main` tree, Python 3.14.8 | 118 passed in 1.02s; exit 0 |
| Ruff | Same tree | All checks passed; exit 0 |
| mypy | Same tree | No issues in one source file; exit 0 |
| Build | `python -m build` isolated environment, hatchling 1.33.0 | sdist and wheel successfully built; exit 0 |

No release tags exist (`git tag --sort=-creatordate` returned no rows). Recent history:

```text
484ff08d Merge pull request #38: align dashboard schema with runtime
dd1c4080 fix: align dashboard JSON Schema with runtime composition
31cff73a Merge PR #33: strict numeric ChartSpec contract
bff9384d fix: validate numeric types in supported Mapping inputs
99841ffb fix: merge-ready strict numeric ChartSpec contract slice
0ae2cf26 build: establish Python package and shared chart contracts
b9f7c176 docs: define visualization contracts and autonomous implementation plan
```

`git fetch --all --prune` completed. There are 66 remote refs including main, excluding symbolic `origin/HEAD`: 65 non-default branches. All 65 branch tip commits list `sandeshbagmare` as Git author. Branch names include agent-round identifiers, but these do not verify individual contributor identity; full tip metadata is in YAML.
