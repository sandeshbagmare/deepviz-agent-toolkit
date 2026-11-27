"""Independent literal JSON contract probes; never import a moving installed model."""
from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

MODEL_PATH = "python/deepviz/src/deepviz/models.py"
DEFAULTS = {
    "version": 1, "kind": "bar", "title": "Visualization", "description": "",
    "x": None, "y": None, "color": None, "size": None, "data_path": None,
    "format": "auto", "aggregation": "auto", "max_points": 2000,
    "width": 900, "height": 520, "theme": "light", "charts": [], "columns": 2,
}
# Raw JSON tokens and literal canonical values are independently caller-authored.
VALID = [
    ("version", "1", 1), ("version", "1.0", 1),
    ("max_points", "10", 10), ("max_points", "100000", 100000),
    ("max_points", "10.0", 10), ("max_points", "100000.0", 100000),
    ("width", "240", 240), ("width", "4096", 4096),
    ("width", "240.0", 240), ("width", "4096.0", 4096), ("width", "900.0", 900),
    ("height", "200", 200), ("height", "4096", 4096),
    ("height", "200.0", 200), ("height", "4096.0", 4096),
    ("columns", "1", 1), ("columns", "6", 6), ("columns", "1.0", 1), ("columns", "6.0", 6),
]
NUMERIC_FIELDS = [
    ("version", '"1"', "1.5", "0", "2"),
    ("max_points", '"2000"', "2000.5", "9", "100001"),
    ("width", '"900"', "900.5", "239", "4097"),
    ("height", '"520"', "520.5", "199", "4097"),
    ("columns", '"2"', "2.5", "0", "7"),
]
INVALID = [
    (field, token)
    for field, numeric_string, fractional, below, above in NUMERIC_FIELDS
    for token in (numeric_string, "true", "false", "null", "[]", "{}", fractional, below, above)
] + [("width", '"900.0"')]


@pytest.fixture(scope="session")
def contract():
    required = ("DEEPVIZ_R22_SOURCE_IDENTITY", "DEEPVIZ_R22_EXPECT_SOURCE", "DEEPVIZ_R22_OUTPUT")
    assert all(os.environ.get(key) for key in required), "Explicit immutable identity, expected source and NEW output are required"
    identity_path = Path(os.environ[required[0]]).resolve(strict=True)
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    assert identity["product_source_sha"] == os.environ[required[1]]
    model_path = Path(identity["actual_model_path"]).resolve(strict=True)
    expected_hash = next(row["sha256"] for row in identity["source_files"] if row["path"] == MODEL_PATH)
    actual_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    assert actual_hash == expected_hash, "Actual model bytes must match the recorded exact Git source"
    module_name = "deepviz_r22_role17_contract_under_test"
    spec = importlib.util.spec_from_file_location(module_name, model_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # Trusted committed module, never schema-authored code.
    schema = module.ChartSpec.model_json_schema()
    Draft202012Validator.check_schema(schema)
    output = Path(os.environ[required[2]]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "generated-schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    (output / "default-model.json").write_text(module.ChartSpec().model_dump_json(indent=2), encoding="utf-8")
    provenance = {
        "product_source_sha": identity["product_source_sha"], "module_name": module_name,
        "actual_loaded_file": module.__file__, "actual_model_sha256": actual_hash,
        "identity_file": str(identity_path), "python_executable": sys.executable,
        "dependencies": {name: importlib.metadata.version(name) for name in ("pydantic", "jsonschema", "pytest")},
        "installed_modern_deepviz_model_imported": "deepviz.models" in sys.modules,
        "trusted_file_loader_reason": "Old e44 has no package initializer; exact file avoids installed modern package shadowing.",
        "scope": "Independent bounded contract preflight, not final focused-PR approval or renderer tests.",
    }
    (output / "loaded-provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return SimpleNamespace(model=module.ChartSpec, module=module, schema=schema,
                           validator=Draft202012Validator(schema), identity=identity,
                           source_root=identity_path.parent, provenance=provenance)


def observed_acceptance(contract, raw_json, validator=None):
    try:
        contract.model.model_validate_json(raw_json)
    except ValidationError:
        model_accepts = False
    else:
        model_accepts = True
    schema_accepts = (validator or contract.validator).is_valid(json.loads(raw_json))
    return model_accepts, schema_accepts


def require_contract_acceptance(observed, expected):
    assert observed == (expected, expected), "Model and actual generated schema must both match the independent literal oracle"


def test_loaded_file_is_exact_git_model_not_installed_dashboard_contract(contract):
    assert Path(contract.module.__file__).resolve() == Path(contract.identity["actual_model_path"]).resolve()
    assert contract.model.__module__ == "deepviz_r22_role17_contract_under_test"
    assert contract.provenance["installed_modern_deepviz_model_imported"] is False


def test_same_old_model_generated_schema_agrees_with_its_committed_schema(contract):
    committed = json.loads((contract.source_root / "schemas/chart-spec.schema.json").read_text(encoding="utf-8"))
    assert contract.schema == committed


def test_defaults_are_literal_bounded_and_json_roundtrip_safe(contract):
    require_contract_acceptance(observed_acceptance(contract, "{}"), True)
    model = contract.model.model_validate_json("{}")
    assert model.model_dump(mode="json") == DEFAULTS
    assert contract.model.model_validate_json(model.model_dump_json()) == model


@pytest.mark.parametrize("field,token,wanted", VALID)
def test_json_integer_bounds_and_integral_floats_are_accepted_and_canonical(contract, field, token, wanted):
    raw = f'{{"{field}":{token}}}'
    require_contract_acceptance(observed_acceptance(contract, raw), True)
    model = contract.model.model_validate_json(raw)
    assert getattr(model, field) == wanted and type(getattr(model, field)) is int
    assert model.model_dump(mode="json")[field] == wanted
    assert contract.model.model_validate_json(model.model_dump_json()) == model


@pytest.mark.parametrize("field,token", INVALID)
def test_strings_bools_noninteger_types_fractional_and_outside_bounds_are_rejected(contract, field, token):
    require_contract_acceptance(observed_acceptance(contract, f'{{"{field}":{token}}}'), False)


@pytest.mark.parametrize("key", ("code", "expression", "javascript", "sql", "url", "formatter"))
def test_unknown_executable_remote_and_callback_keys_are_not_schema_capabilities(contract, key):
    require_contract_acceptance(observed_acceptance(contract, json.dumps({"width": 900, key: "not executable"})), False)


def test_ordinary_literal_text_and_mapped_fields_remain_data_not_extra_code(contract):
    raw = '{"title":"<b>caller & literal</b>","x":"métric.Δ","y":"amount","color":"group","size":"weight"}'
    require_contract_acceptance(observed_acceptance(contract, raw), True)
    model = contract.model.model_validate_json(raw)
    assert (model.title, model.x, model.y, model.color, model.size) == (
        "<b>caller & literal</b>", "métric.Δ", "amount", "group", "weight")


@pytest.mark.parametrize("raw,wrong_expectation", [
    ('{"width":true}', True),
    ('{"width":900.0}', False),
    ('{"width":900,"code":"not executable"}', True),
])
def test_wrong_accepted_type_valid_float_or_extra_key_oracle_cannot_pass(contract, raw, wrong_expectation):
    observed = observed_acceptance(contract, raw)
    with pytest.raises(AssertionError, match="independent literal oracle"):
        require_contract_acceptance(observed, wrong_expectation)


def test_corrupt_schema_accepting_boolean_is_detected_not_promoted_to_pass(contract):
    corrupt = copy.deepcopy(contract.schema)
    corrupt["$defs"]["ChartSpec"]["properties"]["width"] = {"type": "boolean"}
    validator = Draft202012Validator(corrupt)
    observed = observed_acceptance(contract, '{"width":true}', validator)
    assert observed == (False, True), "Real model rejects while intentionally weakened local schema accepts"
    with pytest.raises(AssertionError, match="independent literal oracle"):
        require_contract_acceptance(observed, False)
