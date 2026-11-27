"""Public consumers catch incomplete data packages and accidental renderer imports."""
from __future__ import annotations

import importlib.resources
import json
import os
import subprocess
import sys
import tomllib
from collections.abc import Iterator
from pathlib import Path

import deepviz
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_public_count_consumes_once_and_exports_actual_data_types() -> None:
    assert callable(getattr(deepviz, "normalize", None)), "The public data API is missing"
    pulled: list[str] = []

    def source() -> Iterator[dict[str, str]]:
        for group in ["A", "B", "A", "B", "C", "B"]:
            pulled.append(group)
            yield {"group": group}

    rows = source()
    result = deepviz.normalize(rows, deepviz.ChartSpec(x="group", aggregation="count", max_points=10))
    assert isinstance(result, deepviz.NormalizedData)
    assert result.records == [
        {"group": "A", "count": 2}, {"group": "B", "count": 3}, {"group": "C", "count": 1},
    ]
    assert result.input_count == 6 and result.strategy == "count" and result.warnings == []
    assert pulled == ["A", "B", "A", "B", "C", "B"] and list(rows) == []
    assert deepviz.__version__ == "0.1.0"
    artifact = deepviz.Artifact([], "application/json", "data", result.input_count, 3, result.strategy)
    assert artifact.to_dict() == {
        "paths": [], "mime_type": "application/json", "engine": "data", "input_count": 6,
        "output_count": 3, "strategy": "count", "warnings": [],
    }


def test_public_sampling_retains_bounded_values_and_reports_loss() -> None:
    assert callable(getattr(deepviz, "normalize", None)), "The public data API is missing"
    result = deepviz.normalize(({"i": i} for i in range(100)), {
        "kind": "table", "aggregation": "none", "max_points": 10,
    })
    assert result.input_count == 100 and len(result.records) == 10 and result.strategy == "sample"
    assert all(set(row) == {"i"} and row["i"] in range(100) for row in result.records)
    assert any("sampl" in warning.lower() for warning in result.warnings)


@pytest.mark.parametrize("name", ["system", "request"])
def test_public_prompt_reads_canonical_utf8_resource(name: str) -> None:
    assert callable(getattr(deepviz, "read_prompt", None)), "The installed-resource API is missing"
    assert deepviz.read_prompt(name, version=1).encode("utf-8") == (ROOT / "prompts/v1" / f"{name}.md").read_bytes()


@pytest.mark.parametrize("name,version", [("../system", 1), ("other", 1), ("system", 2), ("request", 0)])
def test_prompt_selector_rejects_escape_and_unshipped_versions(name: str, version: int) -> None:
    assert callable(getattr(deepviz, "read_prompt", None)), "The installed-resource API is missing"
    with pytest.raises(ValueError):
        deepviz.read_prompt(name, version=version)


def test_public_resources_publish_schema_and_inline_type_marker() -> None:
    package = importlib.resources.files("deepviz")
    assert package.joinpath("py.typed").is_file(), "The PEP561 package marker is missing"
    schema = json.loads(package.joinpath("resources/chart-spec.schema.json").read_text(encoding="utf-8"))
    assert schema == json.loads((ROOT / "schemas/chart-spec.schema.json").read_text(encoding="utf-8"))
    assert schema == deepviz.ChartSpec.model_json_schema()


def test_declared_console_scripts_have_real_shipped_modules() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    for name, entry in project.get("scripts", {}).items():
        module = entry.split(":", 1)[0]
        assert (ROOT / "python/deepviz/src" / (module.replace(".", "/") + ".py")).is_file(), name


def test_external_data_consumer_needs_no_unshipped_render_or_optional_sdk(tmp_path: Path) -> None:
    script = """
import importlib.abc
import pathlib
import sys
class Unavailable(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'numpy', 'matplotlib', 'plotly', 'vl_convert', 'pyarrow', 'mcp', 'deepagents', 'langchain_core'} or fullname in {'deepviz.render', 'deepviz.engines', 'deepviz.tools', 'deepviz.cli', 'deepviz.mcp_server'}:
            raise AssertionError('Data import reached an unshipped/optional runtime: ' + fullname)
sys.meta_path.insert(0, Unavailable())
import deepviz
assert deepviz.__file__ and pathlib.Path(deepviz.__file__).resolve().is_relative_to(pathlib.Path(sys.argv[1]).resolve())
result = deepviz.normalize(iter([{'g':'A'}, {'g':'A'}, {'g':'B'}]), {'x':'g','aggregation':'count'})
assert result.records == [{'g':'A','count':2}, {'g':'B','count':1}] and result.input_count == 3
assert deepviz.read_prompt('request').strip()
assert not any(hasattr(deepviz, name) for name in ['render', 'create_tools'])
print(deepviz.__file__)
"""
    result = subprocess.run([sys.executable, "-S", "-B", "-c", script, str(ROOT / "python/deepviz/src")],
                            cwd=tmp_path, env=os.environ.copy(), text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
