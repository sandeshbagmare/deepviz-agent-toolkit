"""Run exact PR33 tests with same-process public import or unchanged tester probes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

SOURCE = "99841ffb80e0f2ea90c753c1bf0ceff718e0e180"
MODEL_PATH = "python/deepviz/src/deepviz/models.py"


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("provided", "independent"))
    parser.add_argument("identity", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("independent_test", type=Path)
    args = parser.parse_args()
    identity_path = args.identity.resolve(strict=True)
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    assert identity["product_source_sha"] == SOURCE
    source_root = identity_path.parent
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    own_test = args.independent_test.resolve(strict=True)
    assert hashlib.sha256(own_test.read_bytes()).hexdigest() == identity["independent_unchanged_79_probe"]["sha256"]
    for row in identity["source_files"]:
        assert hashlib.sha256((source_root / row["path"]).read_bytes()).hexdigest() == row["sha256"]
    assert sys.flags.no_site == 1, "Use python -S with exact snapshot source and read-only site-packages"
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.chdir(source_root)
    provenance = {"source": SOURCE, "mode": args.mode, "python_executable": sys.executable,
                  "sys_path": sys.path, "no_site": sys.flags.no_site,
                  "working_source_files_verified": len(identity["source_files"]),
                  "independent_79_test_unchanged": True}
    if args.mode == "provided":
        import deepviz.models as models

        model_path = Path(models.__file__).resolve()
        assert model_path == (source_root / MODEL_PATH).resolve()
        assert hashlib.sha256(model_path.read_bytes()).hexdigest() == "94824d6f8f151881c0cf21dc85126c18cbb0e98bfb66ab9b4699c98e82293170"
        provenance.update(actual_public_module_file=str(model_path), actual_public_model_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest())
        test_args = []  # ALL provided tests selected by actual focused pyproject.
    else:
        assert "deepviz.models" not in sys.modules
        os.environ["DEEPVIZ_R22_SOURCE_IDENTITY"] = str(identity_path)
        os.environ["DEEPVIZ_R22_EXPECT_SOURCE"] = SOURCE
        os.environ["DEEPVIZ_R22_OUTPUT"] = str(output / "independent-model-output")
        test_args = [str(own_test)]
    write_json(output / "before-pytest-provenance.json", provenance)
    import pytest

    code = int(pytest.main([*test_args, "-q", "--strict-markers", "--tb=short", "-p", "no:cacheprovider",
                            "--junitxml=" + str(output / "results.xml")]))
    # Preserve strict test failures; do not run output-inspection controls after RED.
    if code:
        return code
    for row in identity["source_files"]:
        assert hashlib.sha256((source_root / row["path"]).read_bytes()).hexdigest() == row["sha256"]
    write_json(output / "after-pytest-source-proof.json", {"source": SOURCE, "pytest_exit": code,
               "working_source_files_still_exact": len(identity["source_files"]),
               "independent_79_test_still_unchanged": hashlib.sha256(own_test.read_bytes()).hexdigest() == identity["independent_unchanged_79_probe"]["sha256"]})
    print(json.dumps({"mode": args.mode, "source": SOURCE, "pytest_exit": code,
                      "working_source_files_verified_after_tests": len(identity["source_files"])}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
