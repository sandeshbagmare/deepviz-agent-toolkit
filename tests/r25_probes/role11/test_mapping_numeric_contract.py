"""Supported Mapping carriers must not bypass the public strict numeric contract."""
from collections import UserDict
from types import MappingProxyType

import pytest
from deepviz.models import ChartSpec
from pydantic import ValidationError


@pytest.mark.parametrize("carrier", [UserDict, MappingProxyType])
@pytest.mark.parametrize("field,value", [("width", "900"), ("version", True), ("columns", True)])
def test_supported_mapping_carriers_reject_the_same_invalid_numeric_values(carrier, field, value):
    with pytest.raises(ValidationError):
        ChartSpec.model_validate(carrier({field: value}))


@pytest.mark.parametrize("carrier", [UserDict, MappingProxyType])
def test_valid_integral_numbers_remain_supported_through_mapping_carriers(carrier):
    spec = ChartSpec.model_validate(carrier({"width": 900.0, "columns": 2.0}))
    assert spec.width == 900 and type(spec.width) is int
    assert spec.columns == 2 and type(spec.columns) is int


@pytest.mark.parametrize("carrier", [UserDict, MappingProxyType])
def test_dashboard_child_mapping_does_not_bypass_numeric_validation(carrier):
    with pytest.raises(ValidationError):
        ChartSpec.model_validate({"kind": "dashboard", "charts": [carrier({"width": "900"})]})
