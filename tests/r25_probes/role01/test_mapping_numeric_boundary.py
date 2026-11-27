"""One missing native Mapping input boundary for the strict-numeric repair."""
from collections import UserDict

import pytest
from deepviz.models import ChartSpec
from pydantic import ValidationError


def test_native_mapping_cannot_bypass_numeric_type_rejection():
    # Preserve the established public model's valid Mapping input support.
    assert ChartSpec.model_validate(UserDict({"width": 900})).width == 900
    assert ChartSpec.model_validate({"width": 900}).width == 900
    rejected_values = [("width", "900"), ("version", True), ("columns", True)]
    for field, value in rejected_values:
        with pytest.raises(ValidationError):
            ChartSpec.model_validate({field: value})

    unexpected_acceptances = []
    for field, value in rejected_values:
        try:
            parsed = ChartSpec.model_validate(UserDict({field: value}))
        except ValidationError:
            continue
        unexpected_acceptances.append((field, value, parsed.model_dump()[field]))
    assert not unexpected_acceptances, (
        "A native Mapping must not bypass the same field type checks as a dict: "
        f"{unexpected_acceptances!r}"
    )