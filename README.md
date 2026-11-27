# DeepViz Agent Toolkit

## Staged 0.1 Python data library

This branch prepares an installable **data-only foundation**, not the completed
visualization toolkit or a released v1. It adds a public normalization API,
inline typing, the paired JSON schema, and versioned prompt resources. It is
**draft/unmergeable while the remaining normalization, schema-policy and
distribution acceptance gates are unresolved**. A source import is not proof of
a built distribution, isolated installation, green CI or independent approval.

The full goal remains Python-first declarative visualization, five rendering
engines, npm interoperability, Deep Agent tools and MCP. Those later modules
are deliberately **not imported or advertised as usable APIs in this slice**.

### Available public API

```python
from deepviz import Artifact, ChartSpec, NormalizedData, normalize, read_prompt
from deepviz import __version__

spec = ChartSpec(x="group", aggregation="count", max_points=10)
rows = ({"group": group} for group in ["A", "B", "A", "B", "C", "B"])
result = normalize(rows, spec)
assert result.records == [
    {"group": "A", "count": 2},
    {"group": "B", "count": 3},
    {"group": "C", "count": 1},
]
assert result.input_count == 6 and result.strategy == "count"
assert result.warnings == []
assert __version__ == "0.1.0"
policy_text = read_prompt("system", version=1)
```

`NormalizedData` exposes `records`, `input_count`, `strategy` and `warnings`.
`Artifact` is the shared result **data contract**, not a renderer. Versioned
prompts are retained templates for the full target toolkit; their references to
tools/renderers do **not** mean those tools are provided by this data library.
Only `system` and `request`, version1, are accepted by `read_prompt`.

```python
import json
from importlib.resources import files

schema = json.loads(files("deepviz").joinpath("resources/chart-spec.schema.json").read_text())
```

The wheel force-includes the canonical schema and `prompts/v1` resources; source
resource copies have identical canonical bytes. `py.typed` marks inline types.
Both schema and model remain the exact focused-contract prerequisite, not a
backport of a different model that could remove its strict numeric guard.

### Inputs, reduction and limits

- Pass records, scalar sequences, column arrays, JSON/JSONL/CSV/TSV content,
  supported GraphQL shapes/pages, finite generators, or explicitly authorized
  `pathlib.Path` objects. Strings are **data**, never path or URL authority.
- Arrow/Parquet needs the existing optional `[columnar]` dependency. No optional
  columnar, agent or MCP SDK is imported for ordinary data normalization.
- Use explicit field mappings and aggregation for heterogeneous inputs. Automatic
  inference uses a bounded prefix, not semantic knowledge of every observation.
- `max_points` bounds output records, not input rows scanned. `none` may become a
  warned deterministic reservoir sample; high-cardinality grouping can merge
  observations into a disclosed other bucket. Always inspect warnings and counts.
- JSON documents may be decoded as a whole. Streaming JSONL/delimited inputs and
  finite generators do not imply universal bounded input memory. Retained-payload
  budgets are **not process RSS limits**. No 10M performance claim is made here.

The immutable normalizer dependency is the sealed
`546c25ea75ee9d8a41b3832aa639664bc9a683b5` milestone, adopted whole under R04's
explicit dependency permission. The package author does not edit that normalizer.
Its required independent03/19 source reviews and10 acceptance gates must clear
before package PR merge. The 4KiB field-name versus64KiB policy disagreement and
raw-dashboard JSON-schema contract cases remain merge blockers; their original
tests are retained without xfails, stubs or weakened expectations.

### Packaging and deliberately deferred commands

The declared backend remains **hatchling>=1.27 / hatchling.build**. Python>=3.11
and all existing required dependencies remain unchanged: Pydantic, numpy,
matplotlib, Plotly and vl-convert. The renderer libraries are still **required
metadata dependencies**, even though this slice does not import them. This change
does not quietly make them optional. Existing agents/MCP/columnar/dev extras are
also unchanged; agents/MCP extras alone do not provide the absent toolkit modules.

With an authorized build environment containing the declared dependencies:

```console
python -m build
python -m twine check dist/*
python -m pytest tests/test_packaging_regressions.py
```

The original packaging regression fixture performs isolated builds and local
installs. Do not run it where that environment/install permission is unavailable;
report it BLOCKED rather than substituting a source import. An offline
`--no-isolation` build is separate evidence, not execution of that original fixture.

There is **no `render`, `create_tools`, `deepviz` command or `deepviz-mcp` command**
in this slice. The two previously dangling console-script registrations are
deferred until their real CLI/MCP modules and dependency closures land. No fake
entrypoint, placeholder implementation or borrowed installed source replaces them.

The minimum data-foundation workflow runs only on a relevant PR or explicit
manual dispatch; adding it does not claim that it has run or passed remotely.
R04 alone merges after actual source-specific independent review/test and final
affected gates. Full production scope and its remaining delivery criteria are
not reduced by this staged library boundary.
