"""Independent non-dict Mapping variants: literal root/child contracts, not finder copies."""
from __future__ import annotations

import json
import os
from collections import ChainMap
from collections.abc import Mapping
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from deepviz.models import ChartSpec

NUMBERS = {"version": 1, "max_points": 2000, "width": 900, "height": 520, "columns": 2}
BELOW = {"version": 0, "max_points": 9, "width": 239, "height": 199, "columns": 0}


class TupleMapping(Mapping):
    """Small read-only Mapping implementation, deliberately not a dict subclass."""

    def __init__(self, values):
        self.entries = tuple(values.items())

    def __getitem__(self, key):
        for name, value in self.entries:
            if name == key:
                return value
        raise KeyError(key)

    def __iter__(self):
        return (name for name, _ in self.entries)

    def __len__(self):
        return len(self.entries)


def layered(values):
    pairs = list(values.items())
    return ChainMap(dict(pairs[::2]), dict(pairs[1::2]))


def fingerprint(value):
    if isinstance(value, ChainMap):
        return (type(value).__name__, id(value), tuple(fingerprint(layer) for layer in value.maps))
    if isinstance(value, Mapping):
        return (type(value).__name__, id(value), tuple((key, fingerprint(item)) for key, item in value.items()))
    if isinstance(value, list):
        return ("list", id(value), tuple(fingerprint(item) for item in value))
    return (type(value).__name__, repr(value))


@pytest.fixture(scope="session")
def observations():
    rows = []
    yield rows
    output = Path(os.environ["DEEPVIZ_R31_MAPPING_OUTPUT"])
    output.write_text(json.dumps({"source": os.environ["DEEPVIZ_R31_SOURCE"],
        "actual_model_module": ChartSpec.__module__, "observations": rows}, indent=2), encoding="utf-8", newline="\n")


def observe(factory, child, values, wanted, observations):
    native_values = factory(values)
    assert isinstance(native_values, Mapping) and not isinstance(native_values, dict)
    native = {"kind": "dashboard", "charts": [native_values]} if child else native_values
    literal = {"kind": "dashboard", "charts": [dict(values)]} if child else dict(values)
    before = fingerprint(native)
    validator = Draft202012Validator(ChartSpec.model_json_schema())
    row = {"variant": factory.__name__, "child": child, "literal_json": json.dumps(literal),
           "expected": wanted, "schema_accepted": validator.is_valid(literal)}
    try:
        parsed = ChartSpec.model_validate(native)
    except ValidationError as error:
        row.update(model_accepted=False, errors=[{"type": item["type"], "loc": item["loc"],
            "msg": item["msg"]} for item in error.errors(include_context=False, include_url=False)])
        if child:
            assert all(item["loc"][:2] == ("charts", 0) for item in row["errors"])
    else:
        row.update(model_accepted=True, serialized_json=parsed.model_dump_json(),
                   serialized_value=parsed.model_dump(mode="json"))
        target = parsed.charts[0] if child else parsed
        assert {key: getattr(target, key) for key in NUMBERS} == NUMBERS
        assert all(type(getattr(target, key)) is int for key in NUMBERS)
        assert validator.is_valid(row["serialized_value"])
        assert ChartSpec.model_validate_json(row["serialized_json"]) == parsed
        assert ChartSpec.model_validate_json(row["literal_json"]) == parsed
    row["input_unchanged_including_backing_identity_and_numeric_types"] = fingerprint(native) == before
    observations.append(row)
    assert row["input_unchanged_including_backing_identity_and_numeric_types"]
    assert (row["model_accepted"], row["schema_accepted"]) == (wanted, wanted), "independent Mapping literal oracle"


@pytest.mark.parametrize("factory", [layered, TupleMapping])
@pytest.mark.parametrize("child", [False, True])
def test_mapping_defaults_and_integral_floats_are_canonical_without_mutation(factory, child, observations):
    for values in ({}, {name: float(value) for name, value in NUMBERS.items()}):
        observe(factory, child, values, True, observations)


@pytest.mark.parametrize("factory", [layered, TupleMapping])
@pytest.mark.parametrize("child", [False, True])
def test_mapping_numeric_strings_and_each_boolean_fail_at_root_and_child(factory, child, observations):
    for name, value in NUMBERS.items():
        for bad in (str(value), True, False):
            observe(factory, child, {name: bad}, False, observations)


@pytest.mark.parametrize("factory", [layered, TupleMapping])
@pytest.mark.parametrize("child", [False, True])
def test_mapping_does_not_relax_fractional_or_lower_bounds(factory, child, observations):
    for name, value in NUMBERS.items():
        for bad in (value + 0.5, BELOW[name]):
            observe(factory, child, {name: bad}, False, observations)


def test_wrong_native_mapping_acceptance_oracle_is_strict(observations):
    with pytest.raises(AssertionError, match="independent Mapping literal oracle"):
        observe(layered, True, {"width": "900"}, True, observations)
