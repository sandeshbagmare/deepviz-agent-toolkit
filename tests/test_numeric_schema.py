"""JSON Schema agreement for the numeric runtime fix, not toolkit integration."""
import json
from pathlib import Path

import deepviz.models as models
import pytest
from deepviz.models import ChartSpec
from jsonschema import Draft202012Validator
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]


def test_model_import_is_this_checkout_not_an_installed_sibling():
    assert Path(models.__file__).resolve() == ROOT / "python/deepviz/src/deepviz/models.py"


def test_published_schema_is_the_actual_model_export():
    published = json.loads((ROOT / "schemas/chart-spec.schema.json").read_text(encoding="utf-8"))
    assert published == ChartSpec.model_json_schema()
    Draft202012Validator.check_schema(published)


@pytest.mark.parametrize("field,minimum,maximum,default", [
    ("version", 1, 1, 1),
    ("max_points", 10, 100000, 2000),
    ("width", 240, 4096, 900),
    ("height", 200, 4096, 520),
    ("columns", 1, 6, 2),
])
def test_numeric_json_types_and_bounds_agree(field, minimum, maximum, default):
    schema = Draft202012Validator(ChartSpec.model_json_schema())
    for value, expected in [
        (minimum, True), (maximum, True), (default, True), (float(default), True),
        (True, False), (False, False), (str(default), False), (None, False),
        (minimum - 1, False), (maximum + 1, False), (default + 0.5, False),
    ]:
        payload = {field: value}
        assert schema.is_valid(payload) is expected
        try:
            parsed = ChartSpec.model_validate_json(json.dumps(payload))
        except ValidationError:
            assert not expected, (field, value)
        else:
            assert expected, (field, value)
            assert schema.is_valid(parsed.model_dump(mode="json"))


@pytest.mark.parametrize("width,valid", [(900.0, True), ("900", False), (True, False)])
def test_numeric_child_validation_is_not_bypassed_by_dashboard(width, valid):
    payload = {"kind": "dashboard", "charts": [{"width": width}]}
    schema = Draft202012Validator(ChartSpec.model_json_schema())
    assert schema.is_valid(payload) is valid
    if valid:
        spec = ChartSpec.model_validate_json(json.dumps(payload))
        assert spec.charts[0].width == 900
    else:
        with pytest.raises(ValidationError):
            ChartSpec.model_validate_json(json.dumps(payload))
