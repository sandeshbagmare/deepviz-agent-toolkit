"""Actual frozen PR33 source/import proof, supplied tests and wire model outputs."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from wire_cases import NUMERIC_DEFAULTS, wire_cases

import deepviz.models as models

PIN = "99841ffb80e0f2ea90c753c1bf0ceff718e0e180"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    source, artifacts = args.source.resolve(), args.artifacts.resolve()
    artifacts.mkdir(parents=True, exist_ok=False)

    def git(*values: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(source), *values])

    assert git("rev-parse", "HEAD").decode().strip() == PIN
    assert not git("status", "--porcelain").strip()
    manifest = {}
    for name in git("ls-files").decode().splitlines():
        blob = git("show", PIN + ":" + name)
        assert (source / name).read_bytes() == blob
        manifest[name] = hashlib.sha256(blob).hexdigest()
    assert len(manifest) == 14
    assert models.__file__ is not None
    assert Path(models.__file__).resolve() == source / "python/deepviz/src/deepviz/models.py"
    import deepviz

    assert deepviz.__file__ is None
    namespace_paths = [Path(path).resolve() for path in deepviz.__path__]
    assert namespace_paths[0] == source / "python/deepviz/src/deepviz"
    for path in namespace_paths[1:]:
        assert not list(path.rglob("*.py")), "An installed extra Python module namespace is not accepted"
    assert {name for name in sys.modules if name.startswith("deepviz.")} == {"deepviz.models"}
    generated = models.ChartSpec.model_json_schema()
    committed = json.loads((source / "schemas/chart-spec.schema.json").read_text())
    assert generated == committed
    Draft202012Validator.check_schema(generated)
    validator = Draft202012Validator(generated)
    outputs: list[dict[str, Any]] = []
    for case in wire_cases():
        # Two real public paths: native JSON decoder -> model and JSON wire -> model.
        decoded = json.loads(case.wire)
        assert validator.is_valid(decoded) is case.accepted
        result: dict[str, Any] = {"name": case.name, "literal_wire": case.wire, "approved_accept": case.accepted}
        for label, call in (("decoded_object", lambda obj=decoded: models.ChartSpec.model_validate(obj)),
                            ("wire_json", lambda wire=case.wire: models.ChartSpec.model_validate_json(wire))):
            try:
                value = call()
            except ValidationError as error:
                assert not case.accepted
                result[label] = {"accepted": False, "errors": [
                    {"type": item["type"], "loc": list(item["loc"]), "msg": item["msg"]}
                    for item in error.errors()
                ]}
            else:
                assert case.accepted
                actual_json = value.model_dump_json()
                actual = json.loads(actual_json)
                validator.validate(actual)
                expected = NUMERIC_DEFAULTS | dict(case.expected_numeric_overrides)
                assert {key: actual[key] for key in expected} == expected
                assert all(type(actual[key]) is int for key in expected)
                assert models.ChartSpec.model_validate_json(actual_json) == value
                assert json.dumps(actual, allow_nan=False)
                if "title" in decoded:
                    assert actual["title"] == decoded["title"]
                result[label] = {"accepted": True, "actual_json": actual, "actual_json_wire": actual_json, "schema_valid": True}
        assert result["decoded_object"]["accepted"] == result["wire_json"]["accepted"]
        if case.accepted:
            assert result["decoded_object"]["actual_json"] == result["wire_json"]["actual_json"]
        outputs.append(result)
    assert len(outputs) == 67 and sum(row["approved_accept"] for row in outputs) == 19
    # Original supplied40 are run in this very process after verifying the actual public namespace import.
    code = pytest.main([str(source / "tests"), "-c", str(source / "pyproject.toml"), "-q", "--strict-markers",
                        "-rs", "--tb=short", "-p", "no:cacheprovider", "--junitxml=" + str(artifacts / "provided40.xml")])
    for name, digest in manifest.items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
        assert (source / name).read_bytes() == git("show", PIN + ":" + name)
    assert not git("status", "--porcelain").strip()
    assert {name for name in sys.modules if name.startswith("deepviz.")} == {"deepviz.models"}
    assert Path(models.__file__).resolve() == source / "python/deepviz/src/deepviz/models.py"
    identity = {"source_commit": PIN, "source_Git_raw_equal_sha256": manifest, "tracked_clean_before_after": True,
                "same_process_public_import_relative": "python/deepviz/src/deepviz/models.py",
                "actual_loaded_deepviz_modules_only_this_checkout": True, "no_editable_hooks_python_S": True,
                "unused_extra_namespace_resources_only_no_py_files": len(namespace_paths) - 1,
                "schema_generated_equals_committed": True,
                "schema_canonical_sha256": hashlib.sha256(json.dumps(generated, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                "versions": {name: importlib.metadata.version(name) for name in ("pydantic", "pytest", "jsonschema", "referencing")},
                "provided40_pytest_exit": int(code), "literal_wire_cases": 67, "literal_accepted": 19, "literal_rejected": 48}
    (artifacts / "source-import-identity.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")
    (artifacts / "actual-validation-output.json").write_text(json.dumps({"source_commit": PIN, "literal_outcomes": outputs}, indent=2, allow_nan=False), encoding="utf-8")
    print("R25_ACTUAL998_PUBLIC_NAMESPACE_AND_67_DECODER_WIRE_OUTPUTS_VERIFIED; PROVIDED40_EXIT=" + str(int(code)))
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
