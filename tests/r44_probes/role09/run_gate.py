"""One fixed Python546 gate per fresh -B -S process; no environment writes."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PIN = "546c25ea75ee9d8a41b3832aa639664bc9a683b5"
GROUPS = ("boundaries", "fidelity", "graphql", "lifetime", "prefix", "literal", "policy", "known-mean")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class ObservedTests:
    def __init__(self) -> None:
        self.selected: list[str] = []
        self.deselected: list[str] = []
        self.reports: list[dict[str, Any]] = []

    def pytest_collection_finish(self, session: Any) -> None:
        self.selected = [item.nodeid for item in session.items]

    def pytest_deselected(self, items: Any) -> None:
        self.deselected.extend(item.nodeid for item in items)

    def pytest_runtest_logreport(self, report: Any) -> None:
        self.reports.append({"nodeid": report.nodeid, "phase": report.when,
                             "outcome": report.outcome, "seconds": report.duration})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--site-packages", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--group", choices=GROUPS, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    probes = source / "tests/r44_probes/role09"
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    assert Path(__file__).resolve().parent == probes, "Run exact OWN546 probe copy"
    assert sys.flags.no_site and sys.dont_write_bytecode, "Require Python -B -S"
    assert sys.get_int_max_str_digits() == sys.int_info.default_max_str_digits == 4300

    def git(*parts: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(source), *parts])

    def snapshot() -> dict[str, Any]:
        assert git("rev-parse", "HEAD").decode().strip() == PIN
        assert not git("status", "--porcelain", "--untracked-files=no").strip()
        untracked = git("ls-files", "--others", "--exclude-standard").decode().splitlines()
        assert all(name.startswith("tests/r44_probes/role09/") for name in untracked)
        names = git("ls-tree", "-r", "--name-only", PIN, "--", "python/deepviz/src",
                    "python/deepviz/tests/test_r17_normalizer_boundaries.py",
                    "tests/test_n11_resource_policy.py", "pyproject.toml",
                    "schemas/chart-spec.schema.json").decode().splitlines()
        files = {}
        for name in names:
            raw, blob = (source / name).read_bytes(), git("show", f"{PIN}:{name}")
            assert raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), name
            files[name] = {"raw_sha256": sha(raw), "git_sha256": sha(blob), "raw_equals_git": raw == blob}
        originals = json.loads((probes / "original-controls.json").read_text())["originals"]
        for item in originals:
            raw = (probes / item["copied_name"]).read_bytes()
            assert sha(raw) == item["sha256"]
            assert raw == git("show", f"{item['commit']}:{item['original_path']}")
        return {"product_sha": PIN, "files": files,
                "probes": {p.name: sha(p.read_bytes()) for p in sorted(probes.iterdir()) if p.is_file()},
                "all_originals_raw_git_exact": True, "source_tracked_clean": True}

    before = snapshot()
    sys.path[:0] = [str(source / "python/deepviz/src"), str(probes), str(args.site_packages.resolve(strict=True))]
    modules = {}
    for name in ("deepviz", "deepviz.normalize", "deepviz.models", "deepviz.engines", "deepviz.render"):
        module = importlib.import_module(name)
        assert module.__file__ is not None
        path = Path(module.__file__).resolve()
        relative = path.relative_to(source).as_posix()
        assert relative in before["files"], f"Foreign import: {name}"
        assert sha(path.read_bytes()) == before["files"][relative]["raw_sha256"]
        modules[name] = {"file": str(path), "raw_sha256": sha(path.read_bytes())}
    normalize = importlib.import_module("deepviz.normalize").normalize
    assert Path(normalize.__code__.co_filename).resolve() == source / "python/deepviz/src/deepviz/normalize.py"
    import pytest

    selections = {
        "boundaries": [str(source / "python/deepviz/tests/test_r17_normalizer_boundaries.py")],
        "fidelity": [str(probes / "test_correctness_regressions.py"), "-k", "test_f1 or test_f3 or test_imports"],
        "graphql": [str(probes / "test_graphql_pages.py")],
        "lifetime": [str(probes / "test_owned_input_cleanup.py"), str(probes / "test_reducer_source_ownership.py")],
        "prefix": [str(probes / "test_sum_review.py"), "-k", "not test_mean_and_sample_match_untouched_base"],
        "literal": [str(probes / "test_literal_acceptance.py")],
        "policy": [str(source / "tests/test_n11_resource_policy.py") + "::" + node for node in [
            "test_exact_64kib_utf8_key_or_cell_is_preserved[key-ascii]",
            "test_exact_64kib_utf8_key_or_cell_is_preserved[key-two-byte]",
            "test_exact_64kib_utf8_key_or_cell_is_preserved[key-four-byte]",
            "test_flattened_multibyte_key_at_64kib_is_preserved"]],
        "known-mean": [str(probes / "test_large_integer_mean.py")],
    }
    argv = [*selections[args.group], "-c", str(source / "pyproject.toml"), "--disable-plugin-autoload",
            "--import-mode=importlib", "--strict-markers", "-q", "--tb=short", "-rA", "-p", "no:cacheprovider",
            "-o", "junit_family=legacy", "--basetemp", str(output / "tmp"), "--junitxml", str(output / "junit.xml")]
    receipt = {"group": args.group, "source": str(source), "python": sys.version,
               "executable": sys.executable, "pytest": pytest.__version__, "argv": argv,
               "int_digit_limit": sys.get_int_max_str_digits(), "no_site": sys.flags.no_site,
               "bytecode_disabled": sys.dont_write_bytecode, "our_environment_writes": 0,
               "before": before, "imports_before_pytest": modules}
    (output / "before.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode())
    recorder = ObservedTests()
    started = time.perf_counter()
    result = int(pytest.main(argv, plugins=[recorder]))
    receipt.update({"exit": result, "wall_seconds": time.perf_counter() - started,
                    "selected": recorder.selected, "deselected": recorder.deselected,
                    "actual_reports": recorder.reports, "after": snapshot()})
    assert receipt["after"] == before, "Source/oracle/new probe drift"
    assert sys.get_int_max_str_digits() == 4300
    (output / "result.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode())
    return result


if __name__ == "__main__":
    raise SystemExit(main())
