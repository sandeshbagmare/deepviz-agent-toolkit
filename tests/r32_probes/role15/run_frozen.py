"""Run supplied82 and independent native tests with same-process bff import proof."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

import pytest

import deepviz
import deepviz.models as models

PIN = "bff9384d1ebe5c8f6f8f0f994300264b32bb98d8"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
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
    assert len(manifest) == 15
    assert models.__file__ is not None
    assert Path(models.__file__).resolve() == source / "python/deepviz/src/deepviz/models.py"
    assert deepviz.__file__ is None
    namespaces = [Path(path).resolve() for path in deepviz.__path__]
    assert namespaces[0] == source / "python/deepviz/src/deepviz"
    for extra in namespaces[1:]:
        assert not list(extra.rglob("*.py"))
    assert {name for name in sys.modules if name.startswith("deepviz.")} == {"deepviz.models"}
    generated = models.ChartSpec.model_json_schema()
    assert generated == json.loads((source / "schemas/chart-spec.schema.json").read_text())
    tests = Path(__file__).with_name("test_native_wire.py")
    code = pytest.main([str(source / "tests"), str(tests), "-c", str(source / "pyproject.toml"), "-q",
                        "--strict-markers", "-rs", "--tb=short", "-p", "no:cacheprovider", "-o", "junit_family=legacy",
                        "--junitxml=" + str(artifacts / "provided82-plus-native40.xml")])
    assert git("rev-parse", "HEAD").decode().strip() == PIN
    assert not git("status", "--porcelain").strip()
    for name, digest in manifest.items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
        assert (source / name).read_bytes() == git("show", PIN + ":" + name)
    assert Path(models.__file__).resolve() == source / "python/deepviz/src/deepviz/models.py"
    assert {name for name in sys.modules if name.startswith("deepviz.")} == {"deepviz.models"}
    identity = {"source_commit": PIN, "source_Git_raw_equal_sha256": manifest, "tracked_clean_before_after": True,
                "same_process_model_relative_file": "python/deepviz/src/deepviz/models.py",
                "loaded_deepviz_modules_own_checkout_only": True, "python_S_no_editable_hooks": True,
                "unused_resources_only_namespace_no_py_files": len(namespaces) - 1,
                "generated_equals_committed_schema": True,
                "schema_canonical_sha256": hashlib.sha256(json.dumps(generated, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                "versions": {key: importlib.metadata.version(key) for key in ("pydantic", "pytest", "jsonschema", "referencing")},
                "pytest_exit": int(code)}
    (artifacts / "source-import-identity.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")
    print("R32_BFF_ALL15_GIT_SAMEPROCESS_IMPORT_SCHEMA_PROOF_AND_TEST_EXIT=" + str(int(code)))
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
