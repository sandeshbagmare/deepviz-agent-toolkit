"""Independent exact546 gates; source-binding only, immutable published oracles."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import runpy
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

PIN = "546c25ea75ee9d8a41b3832aa639664bc9a683b5"
BASE = "6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce"
GP = "acb11f862dd211a0563fd3dd824b8e5f5493ffaf"
PREFIX = "8dae3381e6caa0c99d6f032c2d2d318d5cf2a5ce"
HERE = Path(__file__).resolve().parent


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def git(source: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(source), *args], check=True,
                          capture_output=True, timeout=30).stdout


def command(argv: list[str], cwd: Path, env: dict[str, str], output: Path, label: str) -> dict[str, Any]:
    started = time.perf_counter()
    child = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=180)
    (output / (label + ".stdout.log")).write_bytes(child.stdout)
    (output / (label + ".stderr.log")).write_bytes(child.stderr)
    return {"argv": argv, "cwd": str(cwd), "exit": child.returncode,
            "elapsed_seconds": time.perf_counter() - started,
            "stdout_sha256": sha(child.stdout), "stderr_sha256": sha(child.stderr)}


def materialize(source: Path, commit: str, target: Path, paths: list[str]) -> list[dict[str, Any]]:
    target.mkdir(parents=True, exist_ok=False)
    result = []
    names = git(source, "ls-tree", "-r", "--name-only", commit, "--", *paths).decode().splitlines()
    for relative in names:
        data = git(source, "show", f"{commit}:{relative}")
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        assert path.read_bytes() == data
        result.append({"path": str(path.resolve()), "relative": relative, "sha256": sha(data),
                       "Git_commit": commit, "bytes": len(data)})
    return result


def setup(source: Path, output: Path, compiler: Path) -> None:
    assert git(source, "rev-parse", "HEAD").decode().strip() == PIN
    assert not git(source, "status", "--porcelain")
    output.mkdir(parents=True, exist_ok=False)
    candidate, baseline = output / "candidate", output / "baseline"
    common = ["python/deepviz/src/deepviz", "packages/deepviz/src", "packages/deepviz/tsconfig.json",
              "packages/deepviz/package.json", "pyproject.toml"]
    current = materialize(source, PIN, candidate, common + ["python/deepviz/tests/test_r17_normalizer_boundaries.py",
                          "packages/deepviz/test/test_r17_normalizer_boundaries.test.mjs", "tests/test_n11_resource_policy.py"])
    base = materialize(source, BASE, baseline, common)
    oracles = []
    for commit, prefix in [(GP, "tests/r15_probes/role03"), (PREFIX, "tests/r13_probes/role01")]:
        temporary = output / ("extract-" + commit[:7])
        copied = materialize(source, commit, temporary, [prefix])
        for item in copied:
            destination = candidate / item["relative"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(Path(item["path"]).read_bytes())
            item["path"] = str(destination.resolve())
        oracles += copied
    compiler_files = [compiler, compiler.parent.parent / "package.json"]
    compiler_files += [path for path in (compiler.parent.parent / "lib").glob("*tsc.js")]
    tools = [{"path": str(path), "sha256": sha(path.read_bytes())} for path in compiler_files]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    version = command(["node", str(compiler), "--version"], source, environment, output, "compiler-version")
    assert version["exit"] == 0
    builds = []
    for label, root in [("candidate", candidate), ("baseline", baseline)]:
        build = command(["node", str(compiler), "-p", "packages/deepviz/tsconfig.json"], root, environment, output, label + "-compile")
        builds.append(build)
        save(output / "partial-builds.json", builds)
        assert build["exit"] == 0, build
    for tool in tools:
        assert sha(Path(tool["path"]).read_bytes()) == tool["sha256"]
    built: list[dict[str, Any]] = [{"path": str(path.resolve()), "sha256": sha(path.read_bytes()), "bytes": path.stat().st_size}
             for root in (candidate, baseline) for path in sorted((root / "packages/deepviz/dist").rglob("*")) if path.is_file()]
    assert any(item["path"].endswith("normalize.js") for item in built)
    for item in current:
        actual = source / item["relative"]
        assert actual.read_bytes() == Path(item["path"]).read_bytes()
    assert not git(source, "status", "--porcelain")
    save(output / "bindings.json", {"source_sha": PIN, "source_root": str(source), "baseline_sha": BASE,
         "candidate": str(candidate), "baseline": str(baseline), "current": current, "base": base,
         "oracles": oracles, "built": built, "compiler": tools, "compiler_version": version, "builds": builds})
    print(json.dumps({"setup": "PASS", "source_sha": PIN, "candidate_input_files": len(current),
                      "base_input_files": len(base), "unchanged_oracle_files": len(oracles), "own_compiled_files": len(built)}))


def prove(binding: dict[str, Any], baseline: bool = False, load: bool = False) -> dict[str, Any]:
    for key in ("current", "base", "oracles", "built", "compiler"):
        for item in binding[key]:
            assert sha(Path(item["path"]).read_bytes()) == item["sha256"], item["path"]
    root = Path(binding["baseline" if baseline else "candidate"])
    sys.path.insert(0, str(root / "python/deepviz/src"))
    modules = []
    if load:
        importlib.import_module("deepviz")
        for name, module in tuple(sys.modules.items()):
            if name == "deepviz" or name.startswith("deepviz."):
                origin = getattr(module, "__file__", None)
                if origin is None:
                    continue
                path = Path(origin).resolve()
                assert path.is_relative_to(root / "python/deepviz/src/deepviz"), (name, origin)
                expected = next(item for item in binding["base" if baseline else "current"] if Path(item["path"]) == path)
                assert sha(path.read_bytes()) == expected["sha256"]
                modules.append({"name": name, "origin": str(path), "sha256": expected["sha256"]})
    return {"source_sha": BASE if baseline else PIN, "root": str(root), "loaded_modules": modules,
            "all_Git_input_oracle_emit_tool_hashes_verified": True, "no_site": sys.flags.no_site}


def python_gate(binding_path: Path, policy: bool, original: Path | None, ownership: bool = False) -> int:
    assert sys.flags.no_site == 1 and not sys.flags.optimize
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    output, root = binding_path.parent, Path(binding["candidate"])
    base_mode = original is not None
    before = prove(binding, base_mode, True)
    if original is not None:
        assert original.resolve() == root / "tests/r13_probes/role01/test_sum_review.py"
        sys.argv = [str(original), "--unaffected"]
        runpy.run_path(str(original), run_name="__main__")
        save(output / "base-child-proof.json", {"before": before, "after": prove(binding, True, True), "real_original": str(original)})
        return 0
    pytest = importlib.import_module("pytest")
    targets = [str(root / "python/deepviz/tests/test_r17_normalizer_boundaries.py"),
               str(root / "tests/r15_probes/role03/test_graphql_pages.py"),
               str(root / "tests/r13_probes/role01/test_sum_review.py"), str(HERE / "test_literals.py")]
    label = "known-policy-red" if policy else "python-semantics"
    if ownership:
        targets = [str(HERE / "test_ownership_positive.py")]
        label = "python-ownership-positive"
    if policy:
        file = str(root / "tests/test_n11_resource_policy.py")
        targets = [file + "::test_exact_64kib_utf8_key_or_cell_is_preserved[key-" + value + "]"
                   for value in ("ascii", "two-byte", "four-byte")]
        targets += [file + "::test_flattened_multibyte_key_at_64kib_is_preserved"]
    arguments = [*targets, "-c", str(root / "pyproject.toml"), "-q", "-rs", "--tb=short", "-p", "no:cacheprovider",
                 "--basetemp", str(output / (label + "-tmp")), "--junitxml", str(output / (label + ".xml"))]
    original_run = subprocess.run
    calls = []

    def source_bound_run(argv: Any, *args: Any, **kwargs: Any) -> Any:
        expected = [sys.executable, str(root / "tests/r13_probes/role01/test_sum_review.py"), "--unaffected"]
        if argv == expected:
            # Real baseline child; only source binding/-S added, no output or assertion replacement.
            argv = [sys.executable, "-S", str(Path(__file__).resolve()), "base", "--bindings", str(binding_path),
                    "--original", expected[1]]
            calls.append(argv)
        return original_run(argv, *args, **kwargs)

    os.chdir(root)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(subprocess, "run", source_bound_run)
        code = int(pytest.main(arguments))
    save(output / (label + "-proof.json"), {"before": before, "after": prove(binding, False, True),
         "pytest_argv": arguments, "pytest_exit": code, "source_binding_real_baseline_child_argv": calls})
    return code


def run(binding_path: Path, node_only: bool = False) -> int:
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    output, root = binding_path.parent, Path(binding["candidate"])
    prove(binding)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTEST_ADDOPTS="",
                       R41_BINDINGS=str(binding_path), R41_PROOF_DIR=str(output / "node-proofs"),
                       R13_BASE_PYTHONPATH=str(Path(binding["baseline"]) / "python/deepviz/src") + os.pathsep + os.environ["PYTHONPATH"],
                       R13_TS_MODULE=str(root / "packages/deepviz/dist/index.js"),
                       R13_BASE_TS_MODULE=str(Path(binding["baseline"]) / "packages/deepviz/dist/index.js"),
                       R41_ARTIFACT=str(output), MPLCONFIGDIR=str(output / "mpl"), MPLBACKEND="Agg",
                       TMP=str(output / "tmp"), TEMP=str(output / "tmp"), TMPDIR=str(output / "tmp"))
    for path in (output / "tmp", output / "node-proofs", output / "mpl"):
        path.mkdir(exist_ok=node_only)
    steps = [("python-semantics", [sys.executable, "-S", str(Path(__file__).resolve()), "python", "--bindings", str(binding_path)]),
             ("node-semantics", ["node", "--import", (HERE / "node_gate.mjs").as_uri(), "--test", "--test-reporter=tap",
              str(root / "packages/deepviz/test/test_r17_normalizer_boundaries.test.mjs"),
              str(root / "tests/r15_probes/role03/graphql-pages.test.mjs"),
              str(root / "tests/r13_probes/role01/sum-review.test.mjs"), str(HERE / "literals.test.mjs")]),
             ("known-policy-red", [sys.executable, "-S", str(Path(__file__).resolve()), "policy", "--bindings", str(binding_path)])]
    if node_only:
        steps = [("node-bound", steps[1][1])]
    results = []
    for label, argv in steps:
        result = command(argv, root, environment, output, label)
        result["label"] = label
        xml = output / (label + ".xml")
        if xml.exists():
            suite = ET.parse(xml).getroot().find("testsuite")
            assert suite is not None
            result["counts"] = {key: int(suite.get(key, "0")) for key in ("tests", "failures", "errors", "skipped")}
        results.append(result)
        save(output / ("node-resume-runs.json" if node_only else "actual-runs.json"), results)
    prove(binding)
    assert not git(Path(binding["source_root"]), "status", "--porcelain")
    print(json.dumps(results, indent=2))
    # Keep the original policy child RED; runner success must not conceal it.
    return 1 if any(result["exit"] for result in results) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["setup", "run", "node", "python", "policy", "base", "ownership"])
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compiler", type=Path)
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--original", type=Path)
    args = parser.parse_args()
    if args.mode == "setup":
        assert args.source is not None and args.output is not None and args.compiler is not None
        setup(args.source.resolve(), args.output.resolve(), args.compiler.resolve())
        return 0
    assert args.bindings is not None
    path = args.bindings.resolve()
    if args.mode in {"run", "node"}:
        return run(path, args.mode == "node")
    return python_gate(path, args.mode == "policy", args.original, args.mode == "ownership")


if __name__ == "__main__":
    raise SystemExit(main())
