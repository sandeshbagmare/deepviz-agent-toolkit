"""Small independent gaps in e44's existing 30 contract cases; no renderer APIs."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from deepviz.models import ChartSpec

LIMITS = {"version": (1, 1), "max_points": (10, 100000), "width": (240, 4096),
          "height": (200, 4096), "columns": (1, 6)}


def test_review_loads_exact_requested_model_not_installed_current_candidate():
    root = Path(os.environ["R22_SOURCE_ROOT"]).resolve()
    expected = json.loads((root / "source-identity.json").read_text(encoding="utf-8"))
    module = importlib.import_module("deepviz.models")
    filename = module.__file__
    assert filename is not None
    path = Path(filename).resolve()
    assert path == root / "python/deepviz/src/deepviz/models.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected["sha256"]["python/deepviz/src/deepviz/models.py"]


@pytest.mark.parametrize("key", LIMITS)
def test_json_true_false_null_and_numeric_strings_are_not_numbers(key):
    default = getattr(ChartSpec(), key)
    for value in (True, False, None, str(default)):
        with pytest.raises(ValidationError):
            ChartSpec.model_validate_json(json.dumps({key: value}))
        with pytest.raises(ValidationError):
            ChartSpec.model_validate({key: value})


@pytest.mark.parametrize("key,limits", LIMITS.items())
def test_integral_json_float_endpoints_preserve_bounds_not_truthiness(key, limits):
    for value in limits:
        result = ChartSpec.model_validate_json(json.dumps({key: float(value)}))
        assert getattr(result, key) == value and type(getattr(result, key)) is int
    for value in (limits[0] - 1, limits[1] + 1, limits[0] + 0.5):
        with pytest.raises(ValidationError):
            ChartSpec.model_validate_json(json.dumps({key: value}))


def test_validator_does_not_mutate_input_or_miss_nested_dashboard_numeric_fields():
    raw = {"width": 900.0, "max_points": 2000.0}
    before = json.dumps(raw)
    validated = ChartSpec.model_validate(raw)
    assert json.dumps(raw) == before and type(raw["width"]) is float
    assert type(validated.width) is int and validated.width == 900
    with pytest.raises(ValidationError):
        ChartSpec.model_validate_json('{"kind":"dashboard","charts":[{"columns":true}]}')
    valid = ChartSpec.model_validate_json('{"kind":"dashboard","charts":[{"columns":1.0}]}')
    assert valid.charts[0].columns == 1


def test_existing_schema_and_generated_schema_agree_on_json_number_boundaries():
    root = Path(os.environ["R22_SOURCE_ROOT"])
    persisted = json.loads((root / "schemas/chart-spec.schema.json").read_text(encoding="utf-8"))
    generated = ChartSpec.model_json_schema()
    assert generated == persisted, "e44 numeric validation should not silently change the JSON schema"
    Draft202012Validator.check_schema(generated)
    validator = Draft202012Validator(generated)
    validator.validate(ChartSpec().model_dump(mode="json"))
    for key, limits in LIMITS.items():
        validator.validate({key: float(limits[0])})
        for value in (True, False, None, str(limits[0]), limits[0] + 0.5):
            assert not validator.is_valid({key: value})
