"""Novel nested-JSON/schema guards absent from the historical 30 root tests."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

import deepviz.models as loaded_models
from deepviz.models import ChartSpec

EXPECTED_MODEL = Path(os.environ["R22_EXPECTED_MODEL"]).resolve()
assert Path(loaded_models.__file__).resolve() == EXPECTED_MODEL
assert hashlib.sha256(EXPECTED_MODEL.read_bytes()).hexdigest() == os.environ["R22_EXPECTED_MODEL_SHA256"]
HISTORICAL_SCHEMA = json.loads(Path(os.environ["R22_SCHEMA_FILE"]).read_text(encoding="utf-8"))
SCHEMA = ChartSpec.model_json_schema()
VALIDATOR = Draft202012Validator(SCHEMA)


def test_generated_contract_matches_historical_schema_without_new_fields() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA == HISTORICAL_SCHEMA
    properties = SCHEMA["$defs"]["ChartSpec"]["properties"]
    for field in ("version", "columns", "width", "height", "max_points"):
        assert properties[field]["type"] == "integer"
    assert SCHEMA["$defs"]["ChartSpec"]["additionalProperties"] is False


@pytest.mark.parametrize("key,value", [("width", "900"), ("columns", True), ("version", True)])
def test_nested_json_objects_cannot_bypass_numeric_schema_types(key: str, value: object) -> None:
    payload = {"kind": "dashboard", "charts": [{"kind": "bar", key: value}]}
    assert not VALIDATOR.is_valid(payload)
    with pytest.raises(ValidationError):
        ChartSpec.model_validate_json(json.dumps(payload))


def test_nested_integral_json_numbers_remain_valid_and_defaults_remain_bounded() -> None:
    payload = {
        "kind": "dashboard", "columns": 2.0,
        "charts": [{"version": 1.0, "width": 900.0, "height": 520.0, "max_points": 2000.0}],
    }
    VALIDATOR.validate(payload)
    spec = ChartSpec.model_validate_json(json.dumps(payload))
    assert spec.columns == 2
    assert spec.charts[0].width == 900
    assert spec.charts[0].height == 520
    assert spec.charts[0].max_points == 2000
    assert spec.charts[0].model_dump()["version"] == 1
    assert len(spec.charts) == 1 and spec.charts[0].charts == []


def test_nested_extra_executable_key_is_rejected_not_inherited_as_an_option() -> None:
    payload = {"kind": "dashboard", "charts": [{"javascript": "not executable"}]}
    assert not VALIDATOR.is_valid(payload)
    with pytest.raises(ValidationError):
        ChartSpec.model_validate_json(json.dumps(payload))


def test_markup_like_labels_remain_literal_data_not_an_invented_rejection_policy() -> None:
    literal = "</script><strong>literal label</strong>"
    payload = {"kind": "dashboard", "charts": [{"title": literal, "x": "900", "y": "true"}]}
    VALIDATOR.validate(payload)
    spec = ChartSpec.model_validate_json(json.dumps(payload))
    assert spec.charts[0].title == literal
    assert spec.charts[0].x == "900" and spec.charts[0].y == "true"