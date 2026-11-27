"""Independent literal native-Mapping decoder/model/schema/non-mutation checks."""
from __future__ import annotations

import copy
import json
from collections import UserDict
from collections.abc import Mapping
from types import MappingProxyType

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from deepviz.models import ChartSpec

DEFAULTS = {"version": 1, "max_points": 2000, "width": 900, "height": 520, "columns": 2}
# Literal outcomes, not extracted from the model, permanent tests or generated schema.
CASES: tuple[tuple[str, dict[str, object], bool, dict[str, int] | None], ...] = (
    ("defaults", {}, True, DEFAULTS),
    ("native-integral-minima", {"version": 1.0, "max_points": 10.0, "width": 240.0, "height": 200.0, "columns": 1.0},
     True, {"version": 1, "max_points": 10, "width": 240, "height": 200, "columns": 1}),
    ("native-upper-bounds", {"version": 1, "max_points": 100000, "width": 4096, "height": 4096, "columns": 6},
     True, {"version": 1, "max_points": 100000, "width": 4096, "height": 4096, "columns": 6}),
    ("version-bool", {"version": True}, False, None),
    ("max-points-string", {"max_points": "10"}, False, None),
    ("width-string", {"width": "240"}, False, None),
    ("height-bool", {"height": False}, False, None),
    ("columns-string", {"columns": "1"}, False, None),
    ("width-fraction", {"width": 900.5}, False, None),
    ("width-above-bound", {"width": 4097}, False, None),
)


def plain(value):
    """Only convert the explicitly constructed trusted Mapping/list test fixtures."""
    if isinstance(value, Mapping):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


@pytest.mark.parametrize("factory", [UserDict, MappingProxyType], ids=["UserDict", "MappingProxyType"])
@pytest.mark.parametrize("site", ["root", "dashboard-child"])
@pytest.mark.parametrize("label,values,accepted,expected", CASES, ids=[row[0] for row in CASES])
def test_native_mapping_decoder_schema_roundtrip_and_nonmutation(factory, site, label, values, accepted, expected,
                                                                record_property):
    backing = copy.deepcopy(values)
    native = factory(backing)
    payload = native if site == "root" else {"kind": "dashboard", "charts": [native]}
    # Serialized snapshots retain integral-float representation; 900.0->900 mutation cannot hide behind ==.
    wire = json.dumps(plain(payload), separators=(",", ":"), allow_nan=False)
    backing_wire = json.dumps(backing, separators=(",", ":"), allow_nan=False)
    schema = Draft202012Validator(ChartSpec.model_json_schema())
    assert schema.is_valid(json.loads(wire)) is accepted
    receipt = {"factory": factory.__name__, "site": site, "literal_case": label, "expected_accept": accepted,
               "literal_json": wire, "paths": {}}
    for path, call in (("native_mapping", lambda: ChartSpec.model_validate(payload)),
                       ("decoded_json", lambda: ChartSpec.model_validate(json.loads(wire))),
                       ("json_wire", lambda: ChartSpec.model_validate_json(wire))):
        try:
            result = call()
        except ValidationError as error:
            assert not accepted, f"Expected acceptance: {factory.__name__}/{site}/{label}/{path}"
            receipt["paths"][path] = {"accepted": False, "actual_errors": [
                {"type": item["type"], "loc": list(item["loc"]), "msg": item["msg"]} for item in error.errors()
            ]}
        else:
            assert accepted, f"Forbidden acceptance: {factory.__name__}/{site}/{label}/{path}"
            output_wire = result.model_dump_json()
            output = json.loads(output_wire)
            schema.validate(output)
            target = output if site == "root" else output["charts"][0]
            assert {key: target[key] for key in DEFAULTS} == expected
            assert all(type(target[key]) is int for key in DEFAULTS)
            assert ChartSpec.model_validate_json(output_wire) == result
            receipt["paths"][path] = {"accepted": True, "actual_json": output, "actual_json_wire": output_wire,
                                       "schema_valid": True, "roundtrip_equal": True}
    assert json.dumps(plain(payload), separators=(",", ":"), allow_nan=False) == wire
    assert json.dumps(backing, separators=(",", ":"), allow_nan=False) == backing_wire
    if accepted:
        assert receipt["paths"]["native_mapping"]["actual_json"] == receipt["paths"]["decoded_json"]["actual_json"]
        assert receipt["paths"]["native_mapping"]["actual_json"] == receipt["paths"]["json_wire"]["actual_json"]
    receipt["input_and_backing_not_mutated"] = True
    record_property("native_mapping_actual_output", json.dumps(receipt, sort_keys=True, allow_nan=False))
