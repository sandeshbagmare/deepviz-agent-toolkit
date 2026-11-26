"""The checked-in JSON schema must be an exact export of Python's contract."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from deepviz.models import ChartSpec
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]


def exported_schema() -> dict[str, Any]:
    return ChartSpec.model_json_schema()


def test_checked_in_schema_matches_python_contract() -> None:
    schema_path = ROOT / "schemas" / "chart-spec.schema.json"
    assert schema_path.is_file(), "Run python scripts/export_schema.py and commit the generated schema"
    assert json.loads(schema_path.read_text(encoding="utf-8")) == exported_schema()
    jsonschema.Draft202012Validator.check_schema(exported_schema())


@pytest.mark.parametrize("payload", [
    {},
    {"kind": "line", "x": "month", "y": "revenue", "max_points": 2000},
    {"kind": "dashboard", "charts": [{"kind": "bar", "x": "category", "y": "value"}]},
])
def test_json_schema_accepts_python_examples(payload: dict[str, Any]) -> None:
    spec = ChartSpec.model_validate(payload)
    jsonschema.Draft202012Validator(exported_schema()).validate(spec.model_dump(mode="json"))


@pytest.mark.parametrize("payload", [
    {"version": 2}, {"kind": "arbitrary-js"}, {"onClick": "alert(1)"},
    {"width": 239}, {"height": 4097}, {"max_points": 9}, {"max_points": 100001},
    {"title": "x" * 501}, {"charts": [{"script": "eval('unsafe')"}]},
])
def test_json_schema_and_python_reject_invalid_structure(payload: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        ChartSpec.model_validate(payload)
    assert list(jsonschema.Draft202012Validator(exported_schema()).iter_errors(payload))


@pytest.mark.parametrize("payload", [
    {"kind": "dashboard", "charts": []},
    {"kind": "bar", "charts": [{"kind": "line"}]},
    {"kind": "dashboard", "charts": [{"kind": "dashboard", "charts": [{"kind": "bar"}]}]},
])
def test_python_enforces_semantic_rules_not_expressible_by_generated_schema(payload: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        ChartSpec.model_validate(payload)


def test_export_script_is_deterministic_and_check_never_rewrites(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "contract.json"
    env = {**os.environ, "PYTHONPATH": str(ROOT / "python" / "deepviz" / "src")}

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "export_schema.py"), "--output", str(destination), *args],
            check=False, capture_output=True, text=True, env=env, cwd=ROOT,
        )

    assert run("--check").returncode == 1
    assert not destination.exists()
    first = run()
    assert first.returncode == 0, first.stderr
    original = destination.read_bytes()
    assert json.loads(original) == exported_schema()
    assert run().returncode == 0
    assert destination.read_bytes() == original
    assert run("--check").returncode == 0
    destination.write_text("{}\n", encoding="utf-8")
    assert run("--check").returncode == 1
    assert destination.read_text(encoding="utf-8") == "{}\n"
