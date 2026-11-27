"""Independent same-model JSON Schema/wire interoperability, not final PR approval."""
from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
from collections.abc import Generator
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from wire_cases import INVALID_JSON_WIRES, NUMERIC_DEFAULTS, WireCase, wire_cases

jsonschema = pytest.importorskip("jsonschema", reason="Existing optional Draft202012 validator not installed; no install allowed")
PREFLIGHT_PIN = "e44f667ed494fa272f97792ef99942a364ebca24"
CASES = wire_cases()


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _reject_non_json_constant(token: str) -> None:
    raise ValueError(f"Non-JSON numeric token: {token}")


def _decode(wire: str) -> Any:
    return json.loads(wire, parse_constant=_reject_non_json_constant)


@dataclass
class Subject:
    model: Any
    generated: dict[str, Any]
    committed: dict[str, Any] | None
    identity: dict[str, Any]


@pytest.fixture(scope="module")
def subject(tmp_path_factory: pytest.TempPathFactory) -> Generator[Subject, None, None]:
    root = Path(os.environ["R22_SOURCE_ROOT"]).resolve()
    pin = os.environ.get("R22_EXPECTED_PIN", PREFLIGHT_PIN)

    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *args])

    assert git("rev-parse", "HEAD").decode().strip() == pin
    assert not git("status", "--porcelain", "--untracked-files=no").strip()
    manifest = {}
    for name in git("ls-files").decode().splitlines():
        actual = (root / name).read_bytes()
        assert actual == git("show", pin + ":" + name), f"Raw committed-source mismatch: {name}"
        manifest[name] = hashlib.sha256(actual).hexdigest()
    module_name = "r22_role15_trusted_committed_models"
    path = root / "python/deepviz/src/deepviz/models.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # Standard import of trusted committed source, not schema-authored code.
    assert module.__file__ is not None
    assert Path(module.__file__).resolve() == path and module.ChartSpec.__module__ == module_name
    assert not [key for key in sys.modules if key == "deepviz" or key.startswith("deepviz.")]
    model = module.ChartSpec
    generated = model.model_json_schema()
    jsonschema.Draft202012Validator.check_schema(generated)
    artifact = root / "schemas/chart-spec.schema.json"
    committed = json.loads(artifact.read_text()) if artifact.is_file() else None
    if committed is not None:
        jsonschema.Draft202012Validator.check_schema(committed)
    identity = {
        "source_commit": pin, "phase": "preflight-not-focused-signoff" if pin == PREFLIGHT_PIN else "focused-head-test",
        "exact_raw_git_equal_paths_sha256": manifest,
        "import_module": module_name, "import_relative_path": path.relative_to(root).as_posix(),
        "deepviz_package_imported": False, "generated_schema_sha256": _canonical_sha(generated),
        "committed_schema_sha256": _canonical_sha(committed) if committed is not None else None,
        "generated_equals_committed": generated == committed if committed is not None else None,
        "versions": {name: importlib.metadata.version(name) for name in ("pydantic", "jsonschema", "referencing", "pytest")},
    }
    directory = tmp_path_factory.mktemp("r22-source-proof")
    (directory / "identity.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")
    (directory / "same-model-generated-schema.json").write_text(json.dumps(generated, indent=2), encoding="utf-8")
    yield Subject(model, generated, committed, identity)
    assert git("rev-parse", "HEAD").decode().strip() == pin
    assert not git("status", "--porcelain", "--untracked-files=no").strip()
    for name, digest in manifest.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
        assert (root / name).read_bytes() == git("show", pin + ":" + name)


def _verify(case: WireCase, subject: Subject, schema_override: dict[str, Any] | None = None) -> dict[str, Any]:
    parsed = _decode(case.wire)
    generated = subject.generated if schema_override is None else schema_override
    generated_errors = list(jsonschema.Draft202012Validator(generated).iter_errors(parsed))
    committed_errors = None if subject.committed is None else list(jsonschema.Draft202012Validator(subject.committed).iter_errors(parsed))
    try:
        value = subject.model.model_validate_json(case.wire)
    except ValidationError as error:
        value = None
        runtime_errors = sorted({item["type"] for item in error.errors()})
    else:
        runtime_errors = []
    assert (not generated_errors) is case.accepted, f"Generated schema disagrees with literal oracle: {case.name}"
    if committed_errors is not None:
        assert (not committed_errors) is case.accepted, f"Committed schema disagrees with literal oracle: {case.name}"
    assert (value is not None) is case.accepted, f"Pydantic wire disagrees with literal oracle: {case.name}"
    receipt = {"name": case.name, "approved_accept": case.accepted, "generated_schema_accept": not generated_errors,
               "committed_schema_accept": None if committed_errors is None else not committed_errors,
               "runtime_accept": value is not None, "runtime_errors": runtime_errors,
               "generated_schema_error_keywords": sorted({error.validator for error in generated_errors})}
    if value is not None:
        wire = value.model_dump_json()
        canonical = _decode(wire)
        assert json.dumps(canonical, allow_nan=False)
        jsonschema.Draft202012Validator(subject.generated).validate(canonical)
        if subject.committed is not None:
            jsonschema.Draft202012Validator(subject.committed).validate(canonical)
        assert subject.model.model_validate_json(wire) == value
        expected = NUMERIC_DEFAULTS | dict(case.expected_numeric_overrides)
        assert {key: canonical[key] for key in expected} == expected
        assert all(type(canonical[key]) is int for key in expected), "Integral JSON floats canonicalize to bounded JSON integers"
        if "title" in parsed:
            assert canonical["title"] == parsed["title"]
        if case.name == "child-integral-float":
            assert {key: canonical["charts"][0][key] for key in NUMERIC_DEFAULTS} == NUMERIC_DEFAULTS
        receipt["canonical_roundtrip_sha256"] = _canonical_sha(canonical)
        receipt["numeric_result"] = expected
    return receipt


def test_actual_same_model_schema_and_artifact(subject: Subject, record_property) -> None:
    assert subject.committed is not None, "This pinned contract slice includes a committed schema artifact"
    assert subject.generated == subject.committed
    record_property("source_commit", subject.identity["source_commit"])
    record_property("same_model_schema_sha256", _canonical_sha(subject.generated))


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_literal_json_wire_schema_runtime_and_roundtrip(case: WireCase, subject: Subject, record_property) -> None:
    receipt = _verify(case, subject)
    record_property("source_commit", subject.identity["source_commit"])
    record_property("literal_wire", case.wire)
    record_property("outcome", json.dumps(receipt, sort_keys=True))


@pytest.mark.parametrize("label,wire", INVALID_JSON_WIRES, ids=[label for label, _ in INVALID_JSON_WIRES])
def test_nonstandard_nonfinite_tokens_are_not_json(label: str, wire: str, subject: Subject, record_property) -> None:
    with pytest.raises(ValueError, match="Non-JSON numeric token"):
        _decode(wire)
    with pytest.raises(ValidationError):
        subject.model.model_validate_json(wire)
    record_property("literal_wire", wire)
    record_property("schema_stage", "N/A: invalid JSON tokens rejected before an instance exists; not a Draft validation pass")


def test_wrong_positive_literal_oracle_is_detected(subject: Subject) -> None:
    boolean_case = WireCase("known-boolean-negative", '{"width":true}', False)
    with pytest.raises(AssertionError, match="literal oracle"):
        _verify(replace(boolean_case, accepted=True), subject)


def test_unsafe_extra_property_schema_mutation_is_detected(subject: Subject) -> None:
    schema = copy.deepcopy(subject.generated)
    schema["$defs"]["ChartSpec"]["additionalProperties"] = True
    with pytest.raises(AssertionError, match="Generated schema"):
        _verify(WireCase("unsafe-extra", '{"expression":"not executable"}', False), subject, schema)


def test_corrupt_numeric_schema_type_is_detected(subject: Subject) -> None:
    schema = copy.deepcopy(subject.generated)
    schema["$defs"]["ChartSpec"]["properties"]["width"] = {"type": "string"}
    with pytest.raises(AssertionError, match="Generated schema"):
        _verify(WireCase("corrupt-width-type", '{"width":"900"}', False), subject, schema)
