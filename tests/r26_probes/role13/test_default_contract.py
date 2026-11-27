"""Literal public-contract controls, independent of broader candidate packages."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from r26_default_guard import CONTEXT, OBSERVATIONS, validate_identity

from deepviz.models import Artifact, ChartSpec, NormalizedData

SCHEMA = Draft202012Validator(ChartSpec.model_json_schema())


@pytest.mark.parametrize(
    ("field", "literal"),
    [
        ("version", '"1"'), ("version", "true"),
        ("columns", '"2"'), ("columns", "true"),
        ("width", '"900"'), ("width", "true"),
        ("height", '"520"'), ("height", "true"),
        ("max_points", '"2000"'), ("max_points", "true"),
    ],
)
def test_json_numeric_types_agree_with_schema(field, literal):
    wire = '{"' + field + '":' + literal + "}"
    value = json.loads(wire)
    assert not SCHEMA.is_valid(value), "Independent schema must reject this type"
    try:
        model = ChartSpec.model_validate_json(wire)
    except ValidationError:
        OBSERVATIONS.append({"wire": wire, "schema_accepts": False, "model_accepts": False})
        return
    OBSERVATIONS.append({
        "wire": wire, "schema_accepts": False, "model_accepts": True,
        "coerced_value": getattr(model, field),
    })
    pytest.fail("Runtime accepted a numeric type rejected by its public JSON Schema")


@pytest.mark.parametrize(
    ("field", "literal"),
    [("version", "1.0"), ("columns", "2.0"), ("width", "900.0"),
     ("height", "520.0"), ("max_points", "2000.0")],
)
def test_integral_json_numbers_stay_supported(field, literal):
    wire = '{"' + field + '":' + literal + "}"
    assert SCHEMA.is_valid(json.loads(wire))
    model = ChartSpec.model_validate_json(wire)
    assert getattr(model, field) == int(float(literal))
    assert SCHEMA.is_valid(json.loads(model.model_dump_json()))


@pytest.mark.parametrize(
    ("field", "low", "high"),
    [("columns", 1, 6), ("width", 240, 4096), ("height", 200, 4096),
     ("max_points", 10, 100000)],
)
def test_numeric_bounds_are_enforced(field, low, high):
    for number in (low, high):
        assert SCHEMA.is_valid({field: number})
        assert getattr(ChartSpec.model_validate_json(json.dumps({field: number})), field) == number
    for number in (low - 1, high + 1, low + 0.5):
        assert not SCHEMA.is_valid({field: number})
        with pytest.raises(ValidationError):
            ChartSpec.model_validate_json(json.dumps({field: number}))


def test_defaults_and_unicode_literal_roundtrip():
    model = ChartSpec.model_validate_json('{"title":"QA <literal> & 東京"}')
    assert (model.version, model.width, model.height, model.max_points, model.columns) == (
        1, 900, 520, 2000, 2
    )
    output = json.loads(model.model_dump_json())
    assert output["title"] == "QA <literal> & 東京"
    assert output["aggregation"] == "auto" and output["kind"] == "bar"
    assert SCHEMA.is_valid(output)
    OBSERVATIONS.append({"valid_public_model_json": output})


def test_extra_executable_configuration_is_not_admitted():
    for key in ("code", "callback", "javascript", "url"):
        value = {key: "inert marker, never executed"}
        assert not SCHEMA.is_valid(value)
        with pytest.raises(ValidationError):
            ChartSpec.model_validate_json(json.dumps(value))


def test_valid_dashboard_public_model():
    model = ChartSpec.model_validate_json('{"kind":"dashboard","charts":[{"kind":"line"}]}')
    assert len(model.charts) == 1 and model.charts[0].kind == "line"
    assert SCHEMA.is_valid(json.loads(model.model_dump_json()))


@pytest.mark.parametrize("wire", [
    '{"kind":"dashboard","charts":[]}',
    '{"kind":"bar","charts":[{"kind":"line"}]}',
    '{"kind":"dashboard","charts":[{"kind":"dashboard","charts":[{}]}]}',
])
def test_invalid_dashboard_composition_is_rejected(wire):
    with pytest.raises(ValidationError):
        ChartSpec.model_validate_json(wire)


def test_normalized_data_warning_lists_are_not_shared():
    first = NormalizedData(records=[], input_count=0)
    second = NormalizedData(records=[], input_count=0)
    first.warnings.append("first only")
    assert second.warnings == [] and first.strategy == "none"


def test_artifact_public_dict_preserves_counts_and_copies_lists():
    artifact = Artifact(["not-an-opened-file.svg"], "image/svg+xml", "example", 2, 2, "none")
    value = artifact.to_dict()
    assert value["input_count"] == value["output_count"] == 2
    value["warnings"].append("copy only")
    assert artifact.warnings == []


@pytest.mark.parametrize("bad", ["sha", "hash", "origin"])
def test_default_identity_guard_rejects_wrong_provenance(bad):
    source, sha, digest, origin = (CONTEXT[k] for k in ("source", "sha", "model_hash", "origin"))
    if bad == "sha":
        sha = "0" * 40
    elif bad == "hash":
        digest = "0" * 64
    else:
        origin = Path(__file__)
    with pytest.raises(RuntimeError):
        validate_identity(source, sha, digest, origin)
