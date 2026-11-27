"""Fresh-process Python SUM observations, <=100K rows; not final scale acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

REFERENCE = "6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce"
CANDIDATE = "ec9f669eff28cd5351da142765b7755e3b2f484f"
COUNTS = (96, 6000, 100000)
ROOT = Path(__file__).resolve().parents[3]


class CountedSource(Iterator[dict[str, Any]]):
    def __init__(self, source: Iterator[dict[str, Any]]) -> None:
        self.source = source
        self.consumed = 0
        self.exhausted = False

    def __next__(self) -> dict[str, Any]:
        try:
            value = next(self.source)
        except StopIteration:
            self.exhausted = True
            raise
        self.consumed += 1
        return value


def terms(case: str, group: int) -> tuple[float, ...]:
    if case not in {"ordinary", "promoted"}:
        raise ValueError("Unknown case")
    magnitude = 1e16 if case == "ordinary" else 1e308
    return magnitude, magnitude, float(group + 1), -magnitude, -magnitude, 3.0


def rows(count: int, case: str, state: bool = False) -> Iterator[dict[str, Any]]:
    if type(count) is not int or not 24 <= count <= 100000:
        raise ValueError("Probe requires 24..100000 rows; no 1M/10M path")
    complete = count // 24 * 24
    for block in range(complete // 6):
        group = block if state else block % 4
        key = f"g-{group:05d}-" + "k" * 2048 if state else f"g-{group}"
        for value in terms(case, group):
            yield {"g": key, "v": value}
    for _ in range(count - complete):
        yield {"g": "g-0", "v": 0.0}


def oracle(count: int) -> list[dict[str, Any]]:
    return [{"g": f"g-{group}", "v": (count // 24) * (group + 4)} for group in range(4)]


def validate_result(result: dict[str, Any], allow_known_red: bool = False) -> str:
    assert result["error"] is None
    assert result["input_count"] == result["consumed_count"] == result["requested_count"]
    assert result["source_exhausted"] is True and result["strategy"] == "sum"
    assert result["output_count"] == len(result["records"]) == 4
    if allow_known_red and result["records"] == [{"g": f"g-{g}", "v": None} for g in range(4)]:
        assert result["warnings"] and all("non-finite" in warning.lower() for warning in result["warnings"])
        return "oracle_mismatch"
    assert result["records"] == oracle(result["requested_count"]), "Exact closed-form sum differs"
    assert result["warnings"] == [], "Unexplained loss or non-finite warning"
    return "match"


def validate_rejection(result: dict[str, Any]) -> str:
    assert 32 < result["consumed_count"] < result["requested_count"] <= 100000
    assert result["source_exhausted"] is False
    assert result["input_count"] is result["records"] is result["output_count"] is None
    assert result["strategy"] is result["warnings"] is None
    assert result["error"] and "retained" in result["error"].lower() and "bytes" in result["error"].lower()
    return "early_state_budget_rejection"


def require_source(before: dict[str, Any], after: dict[str, Any]) -> None:
    assert before == after and not before["dirty_paths"] and before["sha256"], "Mixed/changed source; invalidate run"
    assert all(not path.startswith("../") for path in before["loaded_modules"].values())


def git_bytes(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def prepare_snapshot(repo: Path, commit: str, destination: Path) -> None:
    assert re.fullmatch(r"[0-9a-f]{40}", commit)
    assert git_bytes(repo, "rev-parse", commit + "^{commit}").decode().strip() == commit
    destination.mkdir(parents=True, exist_ok=False)
    paths = git_bytes(repo, "ls-tree", "-r", "--name-only", commit, "--",
                      "python/deepviz/src/deepviz", "scripts/performance_suite.py").decode().splitlines()
    hashes = {}
    for name in paths:
        if not name.endswith(".py"):
            continue
        target = destination / name
        assert target.resolve().is_relative_to(destination.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        data = git_bytes(repo, "show", commit + ":" + name)
        with target.open("xb") as output:
            output.write(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    metadata = {"commit": commit, "sha256": hashes, "origin": "immutable canonical Git LF objects, not producer dirty tree"}
    with (destination / "snapshot.json").open("x", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(metadata, indent=2) + "\n")


def identity(root: Path) -> dict[str, Any]:
    metadata = json.loads((root / "snapshot.json").read_text(encoding="utf-8"))
    actual = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(root.rglob("*.py"))}
    dirty = sorted(key for key in actual.keys() | metadata["sha256"].keys()
                   if actual.get(key) != metadata["sha256"].get(key))
    loaded = {}
    for name, module in sys.modules.copy().items():
        if name == "deepviz" or name.startswith("deepviz."):
            filename = module.__file__
            assert filename is not None, "Loaded module lacks a filesystem identity"
            path = Path(filename).resolve()
            assert path.is_relative_to(root), "Loaded module outside exact requested snapshot"
            loaded[name] = path.relative_to(root).as_posix()
    return metadata | {"sha256": actual, "dirty_paths": dirty, "loaded_modules": loaded}


def helper(root: Path):
    path = root / "scripts/performance_suite.py"
    spec = importlib.util.spec_from_file_location("role11_existing_performance", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def measure(root: Path, count: int, case: str, state: bool) -> dict[str, Any]:
    if not __debug__:
        raise RuntimeError("Probe assertions require non-optimized Python")
    root = root.resolve()
    support = helper(root)
    normalize, ChartSpec, _ = support.load_api(root)
    before = identity(root)
    require_source(before, before)
    source = CountedSource(rows(count, case, state))
    spec = ChartSpec(kind="table", x="g", y="v", aggregation="sum", max_points=100000 if state else 10)
    baseline = support.peak_memory()
    started = time.perf_counter()
    result: dict[str, Any] = {"requested_count": count, "case": case, "state_case": state,
                              "error": None, "input_count": None, "output_count": None,
                              "records": None, "strategy": None, "warnings": None}
    try:
        normalized = normalize(source, spec)
    except ValueError as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    else:
        result.update(records=normalized.records, input_count=normalized.input_count,
                      output_count=len(normalized.records), strategy=normalized.strategy, warnings=normalized.warnings)
    result["elapsed_seconds"] = time.perf_counter() - started
    result.update(consumed_count=source.consumed, source_exhausted=source.exhausted)
    result["oracle_status"] = (validate_rejection(result) if state else
                               validate_result(result, allow_known_red=before["commit"] == REFERENCE and case == "promoted"))
    memory = support.peak_memory()
    result.update(memory)
    result["baseline_peak_rss_bytes"] = baseline["peak_rss_bytes"]
    result["peak_high_water_growth_bytes"] = memory["peak_rss_bytes"] - baseline["peak_rss_bytes"]
    after = identity(root)
    require_source(before, after)
    result.update(source_before=before, source_after=after, worker_pid=os.getpid())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--count", type=int, default=96)
    parser.add_argument("--case", choices=("ordinary", "promoted"), default="ordinary")
    parser.add_argument("--state", action="store_true")
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(measure(args.worker, args.count, args.case, args.state), allow_nan=False))
        return 0
    if args.artifacts is None:
        parser.error("--artifacts must be a NEW external directory")
    args.artifacts.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {"status": "running", "results": [], "errors": [], "new_maximum_rows": 100000,
                              "python": sys.version, "platform": sys.platform,
                              "timing_scope": "normalize only; includes lazy source generation; excludes import/hash checks",
                              "memory_scope": "Fresh-process inclusive lifetime OS high-water working set; baseline difference is not exclusive allocation",
                              "reference": REFERENCE, "candidate": CANDIDATE}
    output = args.artifacts / "matrix.json"
    try:
        for label, commit in (("reference", REFERENCE), ("candidate", CANDIDATE)):
            snapshot = args.artifacts / label
            prepare_snapshot(args.repo, commit, snapshot)
            jobs = [(case, count, repeat, False) for case in ("ordinary", "promoted")
                    for count in COUNTS for repeat in range(1, 4 if count == 100000 else 2)]
            jobs += [(case, 100000, 1, True) for case in ("ordinary", "promoted")]
            for case, count, repeat, state in jobs:
                command = [sys.executable, str(Path(__file__).resolve()), "--worker", str(snapshot),
                           "--count", str(count), "--case", case, *(["--state"] if state else [])]
                env = os.environ | {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(snapshot / "python/deepviz/src")}
                started = time.perf_counter()
                worker = subprocess.run(command, capture_output=True, text=True, env=env, timeout=90)
                assert worker.returncode == 0, worker.stderr + worker.stdout
                row = json.loads(worker.stdout)
                row.update(label=label, repeat=repeat, worker_exit=worker.returncode,
                           subprocess_wall_seconds=time.perf_counter() - started)
                report["results"].append(row)
                print(f"{label} {case} {count} repeat={repeat} state={state}: {row['oracle_status']}", flush=True)
    except Exception as error:
        report["errors"].append(type(error).__name__ + ": " + str(error))
    report["status"] = "observations_complete" if not report["errors"] else "invalid_or_incomplete"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("REPORT=" + str(output))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
