"""Bounded independent native Mapping root/child contract and ownership controls."""
from collections import UserDict
from types import MappingProxyType

import pytest
from deepviz.models import ChartSpec
from jsonschema import Draft202012Validator
from pydantic import ValidationError


@pytest.mark.parametrize("factory", [UserDict, MappingProxyType])
@pytest.mark.parametrize("child", [False, True])
def test_mapping_contract_root_child_output_and_input_ownership(factory, child):
    validator = Draft202012Validator(ChartSpec.model_json_schema())
    bounds = {
        "version": (1, 1), "max_points": (10, 100000),
        "width": (240, 4096), "height": (200, 4096), "columns": (1, 6),
    }
    defaults = {"version": 1, "max_points": 2000, "width": 900, "height": 520, "columns": 2}
    for values in [{}, {key: float(pair[0]) for key, pair in bounds.items()},
                   {key: float(pair[1]) for key, pair in bounds.items()}]:
        original = values.copy()
        item = factory(values)
        children = [item]
        parent = {"kind": "dashboard", "charts": children} if child else values
        payload = factory(parent) if child else item
        model = ChartSpec.model_validate(payload)
        parsed = model.charts[0] if child else model
        expected = original or defaults
        assert all(type(getattr(parsed, key)) is int for key in bounds)
        assert {key: getattr(parsed, key) for key in bounds} == expected
        validator.validate(model.model_dump(mode="json"))
        assert ChartSpec.model_validate_json(model.model_dump_json()) == model
        assert dict(item) == original and values == original
        if child:
            assert parent["charts"] is children and children[0] is item
            assert dict(payload) == parent

    for field, default in defaults.items():
        for invalid in [str(default), True, False]:
            values = {field: invalid}
            item = factory(values)
            children = [item]
            parent = {"kind": "dashboard", "charts": children} if child else values
            payload = factory(parent) if child else item
            wire = {"kind": "dashboard", "charts": [values]} if child else values
            assert not validator.is_valid(wire)
            with pytest.raises(ValidationError, match=f"{field} must be a JSON number"):
                ChartSpec.model_validate(payload)
            assert dict(item) == {field: invalid} and values == {field: invalid}
            if child:
                assert parent["charts"] is children and children[0] is item