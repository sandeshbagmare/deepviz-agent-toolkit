"""Identity-only launcher: execute all unchanged dd1 shipped tests, no semantic adapter."""
from pathlib import Path
import collections
import hashlib
import importlib
import importlib.util
import json
import os
import sys

snapshot = Path(sys.argv[1]).resolve(strict=True)
dependencies = Path(sys.argv[2]).resolve(strict=True)
output = Path(sys.argv[3]).resolve()
output.mkdir(exist_ok=False)
proof = json.loads(Path(sys.argv[4]).read_text())
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
assert not os.environ.get("PYTEST_ADDOPTS"), "Ambient PYTEST_ADDOPTS forbidden; environment not modified"
assert not any(n == "deepviz" or n.startswith("deepviz.") for n in sys.modules)
assert not any("editable" in type(f).__module__.lower() for f in sys.meta_path)

def check_bytes():
    for record in proof["tracked_files"]:
        raw = (snapshot / record["file"]).read_bytes()
        assert len(raw) == record["bytes"]
        assert hashlib.sha256(raw).hexdigest() == record["sha256"]

check_bytes()
pre = {"source": proof["source"], "raw_Git_files_verified_before_import": 17,
       "flags": {"isolated": sys.flags.isolated, "no_site": sys.flags.no_site,
                 "dont_write_bytecode": sys.dont_write_bytecode},
       "product_modules_before_import": [], "no_editable_finder": True}
(output / "before-import.json").write_text(json.dumps(pre, indent=2) + "\n")
sys.path.insert(0, str(dependencies))
sys.path.insert(0, str(snapshot / "tests"))
sys.path.insert(0, str(snapshot / "python/deepviz/src"))
namespace = importlib.util.find_spec("deepviz")
assert namespace is not None and namespace.origin is None
observed_paths = list(namespace.submodule_search_locations)
own_namespace = str(snapshot / "python/deepviz/src/deepviz")
assert observed_paths[0] == own_namespace
extras = observed_paths[1:]
assert extras in ([], [str(dependencies / "deepviz")])
if extras:
    assert sorted(p.name for p in (dependencies / "deepviz").iterdir()) == ["resources"]
# Identity-only namespace confinement: no production/SDK source, tests or environment changes.
namespace.submodule_search_locations = [own_namespace]
parent_namespace = importlib.util.module_from_spec(namespace)
sys.modules["deepviz"] = parent_namespace
assert list(parent_namespace.__path__) == [own_namespace]
(output / "namespace-identity-adapter.json").write_text(json.dumps({
    "observed_namespace_paths": observed_paths, "selected": list(parent_namespace.__path__),
    "reason": "Installed resources-only namespace; confine imports to exact Git source before models import",
    "no_product_or_SDK_patch": True, "no_environment_or_semantic_oracle_change": True,
}, indent=2) + "\n")
model_spec = importlib.util.find_spec("deepviz.models")
assert model_spec is not None
model_file = snapshot / "python/deepviz/src/deepviz/models.py"
assert Path(model_spec.origin).resolve() == model_file
assert "deepviz.models" not in sys.modules
check_bytes()
models = importlib.import_module("deepviz.models")
assert Path(models.__file__).resolve() == model_file
assert models.ChartSpec.__module__ == "deepviz.models"
import dashboard_schema_oracle as oracle
assert Path(oracle.__file__).resolve() == snapshot / "tests/dashboard_schema_oracle.py"
assert hashlib.sha256(Path(oracle.__file__).read_bytes()).hexdigest() == proof["oracle_sha256"]
assert len(oracle.CASES) == 17
import jsonschema
import pytest
for dependency in (pytest, jsonschema):
    assert Path(dependency.__file__).resolve().is_relative_to(dependencies)
generated = models.ChartSpec.model_json_schema()
published = json.loads((snapshot / "schemas/chart-spec.schema.json").read_bytes())
assert generated == published
jsonschema.Draft202012Validator.check_schema(generated)
(output / "generated-schema.json").write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
records, collected = [], []
model_identity = id(models)
def identity():
    check_bytes()
    assert sys.modules["deepviz.models"] is models and id(models) == model_identity
    assert Path(models.__file__).resolve() == model_file
    assert models.ChartSpec.__module__ == "deepviz.models"
    assert set(n for n in sys.modules if n == "deepviz" or n.startswith("deepviz.")) == {"deepviz", "deepviz.models"}
    assert models.ChartSpec.model_json_schema() == published

class IdentityOnly:
    def pytest_collection_finish(self, session):
        collected.extend(item.nodeid for item in session.items)
        assert len(collected) == 118
        identity()
    def pytest_runtest_setup(self, item):
        identity()
    def pytest_runtest_logreport(self, report):
        records.append({"nodeid": report.nodeid, "phase": report.when, "outcome": report.outcome})

identity()
arguments = [str(snapshot / "tests"), "-q", "--noconftest", "--disable-plugin-autoload", "-p", "no:cacheprovider",
             "-o", "addopts=", "--junitxml=" + str(output / "shipped.xml"),
             "--basetemp=" + str(output / "tmp")]
status = int(pytest.main(arguments, plugins=[IdentityOnly()]))
identity()
counts = dict(collections.Counter(r["outcome"] for r in records if r["phase"] == "call"))
result = {"source": proof["source"], "pytest_exit": status, "collected": len(collected),
          "call_outcomes": counts, "all_reports": records, "pytest_arguments": arguments,
          "source_before_after_17_files_unchanged": True, "namespace_before_after_exact": True,
          "namespace_paths": list(sys.modules["deepviz"].__path__), "model_origin": str(model_file),
          "model_object_identity_before": model_identity, "model_object_identity_after": id(models),
          "raw_cases": 17, "unchanged_oracle_sha256": proof["oracle_sha256"],
          "generated_schema_equals_published_before_after": True,
          "literal_semantics": "17 original RAW strings, never model_dump as input; no original test edits",
          "limits": "118 shipped test executions; overlap with portable36, NOT154distinct tests; no CI/main approval"}
(output / "full-results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
raise SystemExit(status)
