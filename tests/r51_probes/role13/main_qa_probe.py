"""Bounded non-author QA for exactly one verified merged main source tree."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

PIN = "484ff08ddcae6c36d43ce61de774c00b6c422c88"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source = Path(os.environ["R51_SOURCE"]).resolve(strict=True)
    site_packages = Path(os.environ["R51_SITE_PACKAGES"]).resolve(strict=True)
    out = Path(os.environ["R51_EVIDENCE"]).resolve()
    assert source.joinpath(".git").exists() or source.joinpath(".git").is_file()
    assert source.joinpath("python/deepviz/src/deepviz/models.py").is_file()
    assert source.joinpath("schemas/chart-spec.schema.json").is_file()
    assert os.environ["R51_SOURCE_SHA"] == PIN
    assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
    sys.path[:0] = [str(site_packages), str(source / "python/deepviz/src")]
    import jsonschema
    import pydantic
    from deepviz.models import Artifact, ChartSpec

    model_path = Path(__import__("deepviz.models", fromlist=["__file__"]).__file__).resolve()
    assert model_path == source / "python/deepviz/src/deepviz/models.py"
    schema_path = source / "schemas/chart-spec.schema.json"
    schema = json.loads(schema_path.read_bytes())
    generated = ChartSpec.model_json_schema()
    assert schema == generated
    jsonschema.Draft202012Validator.check_schema(schema)

    cases = {
        "default": ({}, True),
        "dashboard": ({"kind": "dashboard", "charts": [{"kind": "line"}]}, True),
        "dashboard_missing_children": ({"kind": "dashboard"}, False),
        "non_dashboard_children": ({"kind": "line", "charts": [{"kind": "bar"}]}, False),
        "numeric_string": ({"width": "900"}, False),
        "numeric_boolean": ({"columns": True}, False),
        "extra_executable_field": ({"expression": "not code"}, False),
    }
    observations = {}
    for name, (payload, expected) in cases.items():
        try:
            actual = ChartSpec.model_validate(payload)
        except Exception as error:  # Validation is the expected negative surface.
            observations[name] = {"accepted": False, "error_type": type(error).__name__}
            assert not expected, (name, payload)
        else:
            observations[name] = {"accepted": True, "json": actual.model_dump(mode="json")}
            assert expected, (name, payload)
    spec = ChartSpec(kind="line", title="R51 exact merged main", x="day", y="value", max_points=10)
    artifact = Artifact(paths=["r51-model-output.json"], mime_type="application/json",
                        engine="contract-only", input_count=2, output_count=1, strategy="none")
    model_output = {"source_sha": PIN, "model_origin": str(model_path),
                    "chart_spec": json.loads(spec.model_dump_json()), "artifact": artifact.to_dict(),
                    "pydantic_version": pydantic.__version__, "jsonschema_version": jsonschema.__version__}
    out.mkdir(parents=True, exist_ok=True)
    (out / "actual-model-output.json").write_text(json.dumps(model_output, indent=2) + "\n", encoding="utf-8")
    (out / "schema-output.json").write_text(json.dumps({"source_sha": PIN, "schema": schema}, indent=2) + "\n",
                                             encoding="utf-8")
    receipt = {"source_sha": PIN, "model_origin": str(model_path), "model_sha256": sha256(model_path),
               "schema_sha256": sha256(schema_path), "cases": observations, "case_count": len(cases),
               "model_schema_equal": True, "schema_valid": True, "artifact_metadata": artifact.to_dict(),
               "viewable_chart_artifact": False,
               "viewable_artifact_limit": "Exact merged tree contains only models/schema; no renderer or image/html output exists to open.",
               "installed_candidate_import": False, "network_install_api": 0}
    (out / "probe.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
