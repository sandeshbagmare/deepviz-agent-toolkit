"""Strict raw-JSON oracles for the next narrow dashboard-schema slice."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

# Literal inputs and decisions are independent of generated schema and model dumps.
# In particular, never validate a default-expanded model_dump instead of these bytes.
CASES: tuple[tuple[str, str, bool], ...] = (
    ("default_bar", '{}', True),
    ("bar_explicit_empty_children", '{"kind":"bar","charts":[]}', True),
    ("dashboard_one_default_child", '{"kind":"dashboard","charts":[{}]}', True),
    ("root_integral_numbers", '{"version":1.0,"max_points":2000.0,"width":900.0,"height":520.0,"columns":2.0}', True),
    ("child_integral_numbers", '{"kind":"dashboard","charts":[{"kind":"line","version":1.0,"max_points":2000.0,"width":900.0,"height":520.0,"columns":2.0}]}', True),
    ("dashboard_missing_children", '{"kind":"dashboard"}', False),
    ("dashboard_empty_children", '{"kind":"dashboard","charts":[]}', False),
    ("bar_nonempty_children", '{"kind":"bar","charts":[{}]}', False),
    ("default_bar_nonempty_children", '{"charts":[{"kind":"line"}]}', False),
    ("nested_empty_dashboard", '{"kind":"dashboard","charts":[{"kind":"dashboard","charts":[]}]}', False),
    ("nested_nonempty_dashboard", '{"kind":"dashboard","charts":[{"kind":"dashboard","charts":[{}]}]}', False),
    ("root_numeric_string", '{"width":"900"}', False),
    ("root_numeric_boolean", '{"columns":true}', False),
    ("child_numeric_string", '{"kind":"dashboard","charts":[{"version":"1"}]}', False),
    ("child_numeric_boolean", '{"kind":"dashboard","charts":[{"width":true}]}', False),
    ("root_forbidden_extra", '{"code":"inert data only"}', False),
    ("child_forbidden_extra", '{"kind":"dashboard","charts":[{"expression":"inert data only"}]}', False),
)
MODEL_PATH = "python/deepviz/src/deepviz/models.py"
SCHEMA_PATH = "schemas/chart-spec.schema.json"
MODULE_NAME = "r33_verified_models"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(repository: Path, *arguments: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repository), *arguments], timeout=30, stderr=subprocess.PIPE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--dependencies", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        parser.error("Use python -B -I -S: editable hooks and ambient imports are forbidden")
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        parser.error("--source-commit must be an immutable full lowercase Git SHA")
    repository = args.repository.resolve(strict=True)
    dependencies = args.dependencies.resolve(strict=True)
    for name in ("pydantic", "jsonschema"):
        if not (dependencies / name / "__init__.py").is_file():
            parser.error(f"Existing explicit dependency directory lacks {name}; do not install")
    if any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules):
        parser.error("A deepviz module was already imported before source verification")
    actual_commit = git_bytes(repository, "rev-parse", f"{args.source_commit}^{{commit}}")
    if actual_commit.decode().strip() != args.source_commit:
        parser.error("Git source identity mismatch")
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    snapshot = output / "snapshot"
    files: list[dict[str, Any]] = []
    for relative in (MODEL_PATH, SCHEMA_PATH):
        data = git_bytes(repository, "show", f"{args.source_commit}:{relative}")
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        assert target.read_bytes() == data, "Snapshot differs BEFORE model import"
        files.append({"file": relative, "bytes": len(data), "sha256": sha256(data)})
    provenance: dict[str, Any] = {
        "source_commit": args.source_commit,
        "repository": str(repository), "snapshot": str(snapshot),
        "verified_before_import": True, "files": files,
        "isolation": {"isolated": sys.flags.isolated, "no_site": sys.flags.no_site,
                      "dont_write_bytecode": sys.dont_write_bytecode},
        "scope": "Only ChartSpec in the exact verified model; no toolkit/renderer imports",
    }
    proof_file = output / "source-provenance.json"
    proof_file.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    # -S avoids .pth/editable hooks. Only the explicit, existing dependency root is added.
    sys.path.insert(0, str(dependencies))
    import jsonschema
    import pydantic
    from pydantic import ValidationError

    for dependency in (jsonschema, pydantic):
        assert dependency.__file__ is not None
        assert Path(dependency.__file__).resolve().is_relative_to(dependencies)
    assert MODULE_NAME not in sys.modules
    model_file = snapshot / MODEL_PATH
    spec = importlib.util.spec_from_file_location(MODULE_NAME, model_file)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve() == model_file.resolve()
    assert sha256(model_file.read_bytes()) == files[0]["sha256"]
    assert not any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules)
    chart_spec = module.ChartSpec
    generated = chart_spec.model_json_schema()
    published = json.loads((snapshot / SCHEMA_PATH).read_bytes())
    validators = {
        "generated": jsonschema.Draft202012Validator(generated),
        "published": jsonschema.Draft202012Validator(published),
    }
    for schema in (generated, published):
        jsonschema.Draft202012Validator.check_schema(schema)
    provenance.update({
        "model_origin": str(Path(module.__file__).resolve()), "module_name": MODULE_NAME,
        "model_origin_hash_verified": True, "unrelated_deepviz_imports": [],
        "dependencies": {name: importlib.metadata.version(name) for name in ("pydantic", "jsonschema")},
        "dependency_origins": {name: str(Path(dep.__file__).resolve())
                               for name, dep in (("pydantic", pydantic), ("jsonschema", jsonschema))},
    })
    proof_file.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    observations: dict[str, dict[str, Any]] = {}

    class DashboardSchemaOracles(unittest.TestCase):
        def test_00_source_origin_stays_verified(self) -> None:
            self.assertEqual(Path(module.__file__).resolve(), model_file.resolve())
            self.assertEqual(sha256(model_file.read_bytes()), files[0]["sha256"])

        def test_01_published_schema_equals_actual_model_export(self) -> None:
            self.assertEqual(published, generated)

    def runtime_case(name: str, raw: str, expected: bool) -> Any:
        def check(self: unittest.TestCase) -> None:
            try:
                chart_spec.model_validate_json(raw)
            except ValidationError as error:
                accepted = False
                error_types = [entry["type"] for entry in error.errors()]
            else:
                accepted, error_types = True, []
            observations.setdefault(name, {}).update({"runtime_accepted": accepted,
                                                      "runtime_error_types": error_types})
            self.assertIs(accepted, expected, f"Actual runtime must honor literal raw JSON: {raw}")
        return check

    def schema_case(name: str, raw: str, expected: bool) -> Any:
        def check(self: unittest.TestCase) -> None:
            accepted: dict[str, bool] = {}
            errors: dict[str, list[dict[str, Any]]] = {}
            for label, validator in validators.items():
                found = list(validator.iter_errors(json.loads(raw)))
                accepted[label] = not found
                errors[label] = [{"validator": entry.validator, "path": list(entry.absolute_path)}
                                 for entry in found]
            observations.setdefault(name, {}).update({"schema_accepted": accepted, "schema_errors": errors})
            self.assertEqual(accepted, dict.fromkeys(validators, expected),
                             f"Strict schema oracle must honor RAW input, not model_dump: {raw}")
        return check

    for name, raw, expected in CASES:
        setattr(DashboardSchemaOracles, "test_runtime_" + name, runtime_case(name, raw, expected))
        setattr(DashboardSchemaOracles, "test_schema_" + name, schema_case(name, raw, expected))
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DashboardSchemaOracles)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    for name, raw, expected in CASES:
        observations[name].update({"raw_json": raw, "expected_accepted": expected})
    report = {
        "source_commit": args.source_commit, "literal_payload_count": len(CASES),
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "successful": result.wasSuccessful(),
        "failed_tests": [test.id() for test, _ in result.failures],
        "error_tests": [test.id() for test, _ in result.errors], "cases": observations,
        "oracle_source_sha256": sha256(Path(__file__).read_bytes()),
        "limits": "Known next-728 prerequisite, not a new issue or bff gate approval; no source/schema fix applied",
    }
    (output / "oracle-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    assert sha256(model_file.read_bytes()) == files[0]["sha256"], "Runtime source changed"
    assert sha256((snapshot / SCHEMA_PATH).read_bytes()) == files[1]["sha256"], "Published schema changed"
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
