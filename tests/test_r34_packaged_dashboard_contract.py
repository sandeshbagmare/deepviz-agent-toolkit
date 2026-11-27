"""Literal raw-package schema controls for the authorized published model/schema pair."""
from __future__ import annotations

import importlib.resources
import json
from typing import Any

import deepviz
import jsonschema
import pytest
from pydantic import ValidationError


@pytest.mark.parametrize("payload", [
    {"kind": "dashboard"},
    {"kind": "dashboard", "charts": []},
    {"charts": [{"kind": "line"}]},
    {"kind": "bar", "charts": [{"kind": "line"}]},
    {"kind": "dashboard", "charts": [{"kind": "dashboard", "charts": [{"kind": "line"}]}]},
], ids=["missing", "empty", "implicit-bar", "explicit-bar", "nested"])
def test_packaged_schema_and_public_model_reject_literal_invalid_composition(payload: dict[str, Any]) -> None:
    schema = json.loads(importlib.resources.files("deepviz").joinpath("resources/chart-spec.schema.json").read_text(encoding="utf-8"))
    assert list(jsonschema.Draft202012Validator(schema).iter_errors(payload))
    with pytest.raises(ValidationError):
        deepviz.ChartSpec.model_validate(payload)


@pytest.mark.parametrize("payload", [
    {"x": "group", "y": "amount"},
    {"kind": "dashboard", "charts": [{"kind": "line", "x": "group", "y": "amount"}]},
], ids=["default-chart", "valid-dashboard"])
def test_packaged_schema_and_public_model_keep_literal_valid_composition(payload: dict[str, Any]) -> None:
    schema = json.loads(importlib.resources.files("deepviz").joinpath("resources/chart-spec.schema.json").read_text(encoding="utf-8"))
    assert not list(jsonschema.Draft202012Validator(schema).iter_errors(payload))
    actual = deepviz.ChartSpec.model_validate(payload)
    assert actual.kind == ("dashboard" if "charts" in payload else "bar")
