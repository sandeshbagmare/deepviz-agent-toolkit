"""Bounded mixed-Mapping acceptance and strict known dashboard-schema witnesses."""

import json
from collections import UserDict
from collections.abc import Mapping
from types import MappingProxyType

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from r26_default_guard import OBSERVATIONS

from deepviz.models import ChartSpec

SCHEMA = Draft202012Validator(ChartSpec.model_json_schema())


def plain(value):
    """Snapshot tiny input containers, not a production-derived expected oracle."""
    if isinstance(value, Mapping):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


@pytest.mark.parametrize("root_factory,child_factory", [
    (UserDict, MappingProxyType), (MappingProxyType, UserDict),
])
def test_mixed_mapping_root_and_child_literal_json_roundtrip_without_mutation(
    root_factory, child_factory,
):
    child = child_factory({"width": 240.0, "height": 200.0, "title": "<literal> & 東京"})
    payload = root_factory({
        "kind": "dashboard", "charts": [child], "version": 1.0,
        "columns": 1.0, "width": 4096.0, "height": 4096.0, "max_points": 10.0,
    })
    before = plain(payload)
    model = ChartSpec.model_validate(payload)
    output = json.loads(model.model_dump_json())
    assert (model.version, model.columns, model.width, model.height, model.max_points) == (
        1, 1, 4096, 4096, 10
    )
    assert (model.charts[0].width, model.charts[0].height) == (240, 200)
    assert output["charts"][0]["title"] == "<literal> & 東京"
    assert SCHEMA.is_valid(output)
    assert ChartSpec.model_validate_json(model.model_dump_json()) == model
    assert plain(payload) == before and payload["charts"][0] is child
    OBSERVATIONS.append({
        "mixed_mapping_factories": [root_factory.__name__, child_factory.__name__],
        "actual_json_output": output, "input_unchanged": True,
    })


@pytest.mark.parametrize("bad_location", ["root", "child"])
def test_mixed_mapping_failure_preserves_root_and_child_inputs(bad_location):
    child = UserDict({"width": 900.0, "columns": "2" if bad_location == "child" else 2})
    payload = MappingProxyType({
        "kind": "dashboard", "charts": [child],
        "version": True if bad_location == "root" else 1,
    })
    before = plain(payload)
    assert not SCHEMA.is_valid(before)
    with pytest.raises(ValidationError) as caught:
        ChartSpec.model_validate(payload)
    error = caught.value.errors(include_url=False, include_context=False, include_input=False)[0]
    assert error["loc"] == (() if bad_location == "root" else ("charts", 0))
    assert plain(payload) == before and payload["charts"][0] is child
    OBSERVATIONS.append({
        "invalid_mapping_location": bad_location, "literal_input": before,
        "actual_error": error, "input_unchanged": True,
    })


@pytest.mark.parametrize("wire", [
    '{"kind":"dashboard","charts":[]}',
    '{"charts":[{}]}',
    '{"kind":"dashboard","charts":[{"kind":"dashboard","charts":[{}]}]}',
])
def test_known_728_invalid_dashboard_forms_must_be_rejected_by_published_schema(wire):
    """Retain actual known RED; this is not a numeric-coercion regression or xfail."""
    value = json.loads(wire)
    with pytest.raises(ValidationError):
        ChartSpec.model_validate_json(wire)
    schema_accepts = SCHEMA.is_valid(value)
    OBSERVATIONS.append({
        "known_728_literal_wire": wire, "runtime_rejects": True,
        "schema_accepts": schema_accepts,
    })
    assert not schema_accepts, "Known dashboard-schema constraints are still absent from this main slice"
