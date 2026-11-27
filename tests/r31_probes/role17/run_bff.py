"""Exact bff source/test-provenance runner; run each mode once with fresh outputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

SHA = "bff9384d1ebe5c8f6f8f0f994300264b32bb98d8"
MODEL_SHA = "8532ec73be4a212d822aab2ee5b021e9d56a7cc266ddbd9ae111ed8310b7262d"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("provided", "independent", "mapping"))
    parser.add_argument("identity", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    identity_path = args.identity.resolve(strict=True)
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    assert identity["product_source_sha"] == SHA and sys.flags.no_site == 1
    root = identity_path.parent
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)

    def proof():
        for row in identity["source_files"]:
            assert hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"]
        for row in identity["consumer_test_files"]:
            assert hashlib.sha256(Path(row["absolute_path"]).read_bytes()).hexdigest() == row["sha256"]
        return {"source": SHA, "source_files_verified": len(identity["source_files"]),
                "consumer_test_files_verified": len(identity["consumer_test_files"]),
                "python_executable": sys.executable, "sys_path": sys.path, "python_no_site": sys.flags.no_site}

    before = proof()
    os.chdir(root)
    os.environ.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    if args.mode == "independent":
        assert "deepviz.models" not in sys.modules
        os.environ.update(DEEPVIZ_R22_SOURCE_IDENTITY=str(identity_path), DEEPVIZ_R22_EXPECT_SOURCE=SHA,
                          DEEPVIZ_R22_OUTPUT=str(output / "actual-model-output"))
        tests = [identity["independent_unchanged_79_probe"]["absolute_path"]]
    else:
        import deepviz.models as models

        actual = Path(models.__file__).resolve()
        assert actual == Path(identity["actual_model_path"]).resolve()
        assert hashlib.sha256(actual.read_bytes()).hexdigest() == MODEL_SHA
        before.update(actual_public_model_file=str(actual), actual_public_model_sha256=MODEL_SHA)
        if args.mode == "provided":
            tests = []  # All actual focused tests, no filtering or copied author suite.
        else:
            os.environ.update(DEEPVIZ_R31_SOURCE=SHA, DEEPVIZ_R31_MAPPING_OUTPUT=str(output / "actual-mapping-outputs.json"))
            tests = [identity["new_mapping_probe_absolute_path"]]
    (output / "before-provenance.json").write_text(json.dumps(before, indent=2), encoding="utf-8", newline="\n")
    import pytest

    result = int(pytest.main([*tests, "-q", "--strict-markers", "--tb=short", "-p", "no:cacheprovider",
                             "--junitxml=" + str(output / "results.xml")]))
    after = proof()
    after["pytest_exit"] = result
    (output / "after-provenance.json").write_text(json.dumps(after, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"source": SHA, "mode": args.mode, "pytest_exit": result,
                      "all15source_and_all_consumer_test_hashes_before_after_exact": True}))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
