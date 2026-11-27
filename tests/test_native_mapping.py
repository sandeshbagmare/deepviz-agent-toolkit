"""Accepted native Mapping containers must not bypass numeric validation."""
from collections import UserDict
from types import MappingProxyType

import pytest
from deepviz.models import ChartSpec
from pydantic import ValidationError

FACTORIES = [UserDict, MappingProxyType]
NUMBERS = {"version": 1, "max_points": 2000, "width": 900, "height": 520, "columns": 2}


@pytest.mark.parametrize("factory", FACTORIES)
@pytest.mark.parametrize("field", NUMBERS)
@pytest.mark.parametrize("invalid", ["numeric-string", True, False])
def test_supported_mappings_reject_the_same_numeric_coercions(factory, field, invalid):
    value = str(NUMBERS[field]) if invalid == "numeric-string" else invalid
    original = {field: value}
    payload = factory(original)
    with pytest.raises(ValidationError, match=f"{field} must be a JSON number"):
        ChartSpec.model_validate(payload)
    assert dict(payload) == original


@pytest.mark.parametrize("factory", FACTORIES)
@pytest.mark.parametrize("values", [{}, {key: float(value) for key, value in NUMBERS.items()}])
def test_supported_mappings_preserve_defaults_and_integral_numbers(factory, values):
    payload = factory(values)
    parsed = ChartSpec.model_validate(payload)
    assert {key: getattr(parsed, key) for key in NUMBERS} == NUMBERS
    assert all(type(getattr(parsed, key)) is int for key in NUMBERS)
    assert dict(payload) == values


@pytest.mark.parametrize("factory", FACTORIES)
@pytest.mark.parametrize("invalid", ["900", True, False])
def test_nested_mapping_children_cannot_bypass_the_numeric_guard(factory, invalid):
    with pytest.raises(ValidationError, match="width must be a JSON number"):
        ChartSpec.model_validate({"kind": "dashboard", "charts": [factory({"width": invalid})]})


@pytest.mark.parametrize("factory", FACTORIES)
def test_nested_integral_mapping_children_remain_valid(factory):
    parsed = ChartSpec.model_validate({"kind": "dashboard", "charts": [factory({"width": 900.0})]})
    assert parsed.charts[0].width == 900
