"""Keep raw dashboard JSON Schema aligned with the existing runtime contract."""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema
import pytest
from dashboard_schema_oracle import CASES
from deepviz.models import ChartSpec
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = ROOT / "schemas/chart-spec.schema.json"


@pytest.mark.parametrize(("name", "raw", "expected"), CASES, ids=[case[0] for case in CASES])
def test_runtime_honors_literal_dashboard_json(name: str, raw: str, expected: bool) -> None:
    try:
        ChartSpec.model_validate_json(raw)
    except ValidationError:
        accepted = False
    else:
        accepted = True
    assert accepted is expected, name


@pytest.mark.parametrize(("name", "raw", "expected"), CASES, ids=[case[0] for case in CASES])
def test_generated_and_published_schema_honor_raw_dashboard_json(
    name: str, raw: str, expected: bool,
) -> None:
    # Validate the original JSON, never a default-expanded model_dump.
    for schema in (ChartSpec.model_json_schema(), json.loads(SCHEMA_FILE.read_bytes())):
        validator = jsonschema.Draft202012Validator(schema)
        assert validator.is_valid(json.loads(raw)) is expected, name


def test_contract_imports_the_model_in_this_checkout() -> None:
    assert Path(inspect.getfile(ChartSpec)).resolve() == (
        ROOT / "python/deepviz/src/deepviz/models.py"
    ).resolve()


def test_published_dashboard_schema_is_the_actual_model_export() -> None:
    generated = ChartSpec.model_json_schema()
    jsonschema.Draft202012Validator.check_schema(generated)
    assert json.loads(SCHEMA_FILE.read_bytes()) == generated
