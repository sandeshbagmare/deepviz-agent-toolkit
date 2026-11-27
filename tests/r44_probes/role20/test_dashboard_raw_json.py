"""Independent literal JSON oracles; never round-trip defaults through the model."""
from __future__ import annotations

import copy
import inspect
import json
from collections import UserDict
from pathlib import Path
from typing import Any

import pytest
from deepviz.models import ChartSpec
from jsonschema import Draft202012Validator
from pydantic import ValidationError

HERE = Path(__file__).resolve().parent
SOURCE = Path(inspect.getfile(ChartSpec)).resolve().parents[4]
LITERAL_CASES: list[dict[str, Any]] = json.loads((HERE / "literal_cases.json").read_text(encoding="utf-8"))
MAPPING_CASES: list[dict[str, Any]] = json.loads(
    (HERE / "native_mapping_cases.json").read_text(encoding="utf-8")
)


@pytest.fixture(scope="session")
def validators() -> dict[str, Any]:
    generated = ChartSpec.model_json_schema()
    published = json.loads((SOURCE / "schemas/chart-spec.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(generated)
    Draft202012Validator.check_schema(published)
    return {"generated": Draft202012Validator(generated), "published": Draft202012Validator(published)}


def assert_runtime_attributes(model: ChartSpec, expected: dict[str, Any]) -> None:
    """Expected values are handwritten fixture constants, never production-derived."""
    for key, value in expected.items():
        if key == "child_count":
            assert len(model.charts) == value
        elif key.startswith("child_"):
            assert model.charts
            for child in model.charts:
                assert getattr(child, key.removeprefix("child_")) == value
        else:
            assert getattr(model, key) == value


def assert_runtime(payload: Any, case: dict[str, Any]) -> None:
    if case["accept"]:
        model = ChartSpec.model_validate(payload)
        assert_runtime_attributes(model, case["expected"])
    else:
        with pytest.raises(ValidationError):
            ChartSpec.model_validate(payload)


@pytest.mark.parametrize("case", LITERAL_CASES, ids=[case["id"] for case in LITERAL_CASES])
@pytest.mark.parametrize("surface", ["runtime", "generated", "published"])
def test_original_literal_input_without_default_materialization(
    case: dict[str, Any], surface: str, validators: dict[str, Any],
) -> None:
    payload = json.loads(case["raw"])
    before = copy.deepcopy(payload)
    try:
        if surface == "runtime":
            assert_runtime(payload, case)
        else:
            errors = list(validators[surface].iter_errors(payload))
            assert (not errors) is case["accept"], [(list(error.path), error.message) for error in errors]
    finally:
        assert payload == before, "Validation must not mutate caller JSON or populate absent defaults"


@pytest.mark.parametrize("case", MAPPING_CASES, ids=[case["id"] for case in MAPPING_CASES])
def test_native_mapping_boundary_and_caller_ownership(
    case: dict[str, Any], validators: dict[str, Any],
) -> None:
    # Schema validators receive only the ORIGINAL raw JSON, not a native Mapping
    # or a coerced/model-dumped value. Native Mapping support is a runtime API.
    for validator in validators.values():
        original = json.loads(case["raw"])
        original_before = copy.deepcopy(original)
        errors = list(validator.iter_errors(original))
        assert (not errors) is case["accept"]
        assert original == original_before

    payload = json.loads(case["raw"])
    if case["scope"] == "root":
        selected: UserDict[str, Any] = UserDict(payload)
        payload = selected
    else:
        selected = UserDict(payload["charts"][0])
        payload["charts"][0] = selected
    before = copy.deepcopy(payload)
    backing = selected.data
    child_list = payload.get("charts")
    first_child = child_list[0] if child_list else None
    try:
        assert_runtime(payload, case)
    finally:
        assert payload == before
        assert selected.data is backing
        assert payload.get("charts") is child_list
        if child_list:
            assert child_list[0] is first_child
        assert type(selected) is UserDict


@pytest.mark.parametrize("raw", ['{"kind":"dashboard","charts":[', '{"kind":"dashboard" "charts":[{}]}'])
def test_syntactically_malformed_json_never_becomes_a_schema_instance(raw: str) -> None:
    with pytest.raises(json.JSONDecodeError):
        json.loads(raw)
    with pytest.raises(ValidationError):
        ChartSpec.model_validate_json(raw)


def test_generated_schema_matches_published_artifact_without_using_it_as_truth() -> None:
    # Freshness only. Acceptance truth comes from the independent literal tables.
    generated = ChartSpec.model_json_schema()
    published = json.loads((SOURCE / "schemas/chart-spec.schema.json").read_text(encoding="utf-8"))
    assert generated == published
