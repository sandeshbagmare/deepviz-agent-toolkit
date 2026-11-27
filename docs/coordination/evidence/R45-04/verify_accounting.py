"""Run scoped tests only after same-process source and dependency verification."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "546c25ea75ee9d8a41b3832aa639664bc9a683b5"
DEPENDENCIES = Path("C:/Users/bagma/deepviz-agent-toolkit/.venv/Lib/site-packages")
ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "python/deepviz/src"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("tests", nargs="+")
    args = parser.parse_args()
    assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
    assert not any(name == "deepviz" or name.startswith("deepviz.") for name in sys.modules)
    output = Path(__file__).resolve().parent / args.phase
    output.mkdir(exist_ok=False)
    model_sources: dict[str, str] = {}
    for path in (SOURCE / "deepviz").rglob("*.py"):
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        expected = subprocess.check_output(["git", "show", f"{BASE}:{relative}"], cwd=ROOT)
        if path.name == "normalize.py":
            assert digest(data) == args.source_sha256
            if args.phase == "red":
                assert data == expected
        else:
            assert data == expected
        model_sources[relative] = digest(data)
    test_hashes = {
        text: digest((ROOT / text.split("::", 1)[0]).read_bytes()) for text in args.tests
    }
    digits = sys.get_int_max_str_digits()
    sys.path[:0] = [str(SOURCE), str(DEPENDENCIES)]
    normalizer = importlib.import_module("deepviz.normalize")
    assert Path(normalizer.__file__).resolve() == SOURCE / "deepviz/normalize.py"
    assert digest(Path(normalizer.__file__).read_bytes()) == args.source_sha256
    import pytest

    assert Path(pytest.__file__).resolve().is_relative_to(DEPENDENCIES)
    proof = {
        "phase": args.phase, "base": BASE, "root": str(ROOT),
        "module_origin_before_tests": normalizer.__file__,
        "normalizer_sha256_before_tests": args.source_sha256,
        "package_files_verified_before_import": model_sources,
        "test_hashes_before": test_hashes, "integer_digit_limit_before": digits,
        "isolation": {"isolated": sys.flags.isolated, "no_site": sys.flags.no_site,
                      "no_bytecode": sys.dont_write_bytecode},
        "pytest_origin": pytest.__file__, "pytest_version": pytest.__version__,
    }
    target = output / "verification.json"
    target.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    arguments = [
        "-q", "--disable-plugin-autoload", "-p", "no:cacheprovider", "--strict-markers",
        "--tb=short", "--rootdir", str(ROOT), "--confcutdir", str(ROOT),
        "--basetemp", str(output / "temp"), "--junitxml", str(output / "tests.xml"),
        *args.tests,
    ]
    started = time.perf_counter()
    result = int(pytest.main(arguments))
    elapsed = time.perf_counter() - started
    cases = list(ET.parse(output / "tests.xml").getroot().iter("testcase"))
    failures = [case.attrib["name"] for case in cases if case.find("failure") is not None]
    errors = [case.attrib["name"] for case in cases if case.find("error") is not None]
    skipped = [case.attrib["name"] for case in cases if case.find("skipped") is not None]
    for relative, expected_hash in model_sources.items():
        assert digest((ROOT / relative).read_bytes()) == expected_hash
    for text, expected_hash in test_hashes.items():
        assert digest((ROOT / text.split("::", 1)[0]).read_bytes()) == expected_hash
    assert sys.get_int_max_str_digits() == digits
    assert Path(normalizer.__file__).resolve() == SOURCE / "deepviz/normalize.py"
    proof.update({
        "pytest_argv": arguments, "exit": result, "elapsed_seconds": elapsed,
        "tests": len(cases), "failures": failures, "errors": errors, "skipped": skipped,
        "passed": len(cases) - len(failures) - len(errors) - len(skipped),
        "sources_and_tests_unchanged_after": True,
        "integer_digit_limit_after": sys.get_int_max_str_digits(),
    })
    target.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: proof[key] for key in (
        "phase", "exit", "elapsed_seconds", "tests", "passed", "failures", "errors", "skipped",
        "integer_digit_limit_before", "integer_digit_limit_after",
    )}, indent=2))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
