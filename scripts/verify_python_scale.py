"""Measure bounded Python normalization using generated streams in fresh workers."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCALES = (10, 1_000, 100_000, 1_000_000, 10_000_000)
CASES = ("sample", "sum", "mean")


class CountedRows(Iterator[dict[str, Any]]):
    """Generate small rows on demand and count actual iterator consumption."""

    def __init__(self, count: int, case: str) -> None:
        self.count = count
        self.case = case
        self.consumed = 0
        self.exhausted = False

    def __length_hint__(self) -> int:
        raise AssertionError("Input stream must not be eagerly materialized")

    def __next__(self) -> dict[str, Any]:
        if self.consumed == self.count:
            self.exhausted = True
            raise StopIteration
        index = self.consumed
        self.consumed += 1
        if self.case == "sample":
            return {"x": index, "value": index % 101 - 50}
        return {"category": f"group-{index % 7}", "value": index + 1}


def expected_groups(count: int, case: str) -> dict[str, int | float]:
    expected: dict[str, int | float] = {}
    for category in range(min(count, 7)):
        size = (count - 1 - category) // 7 + 1
        first = category + 1
        total = size * (2 * first + (size - 1) * 7) // 2
        expected[f"group-{category}"] = total if case == "sum" else total / size
    return expected


def validate_result(result: dict[str, Any], *, count: int, case: str, bound: int) -> dict[str, Any]:
    assert result["input_count"] == count, "Normalizer input_count differs from generated rows"
    assert result["consumed_count"] == count, "Normalizer did not consume every generated row"
    assert result["source_exhausted"], "Normalizer stopped before source exhaustion"
    records = result["records"]
    assert 0 < len(records) <= bound, "Normalized output is empty or exceeds max_points"
    json.dumps(records, allow_nan=False)

    if case == "sample":
        assert len(records) == min(count, bound), "Sample count differs from requested bound"
        indices = [row["x"] for row in records]
        assert indices == sorted(set(indices)), "Sample rows are duplicated or out of source order"
        for row in records:
            index = row["x"]
            assert type(index) is int and 0 <= index < count, "Sample row came from outside the source"
            assert row["value"] == index % 101 - 50, "Sample row value changed during normalization"
        if count > bound:
            assert result["strategy"] == "sample", "Lossy sampling strategy was not reported"
            assert result["warnings"], "Lossy sampling was not disclosed"
        return {}

    aggregation = case
    expected = expected_groups(count, aggregation)
    actual = {row["category"]: row["value"] for row in records}
    assert len(actual) == len(records) == len(expected), "Reducer omitted or duplicated categories"
    assert set(actual) == set(expected), "Reducer returned unexpected categories"
    for category, value in expected.items():
        correct = (
            type(actual[category]) is int and actual[category] == value if case == "sum"
            else math.isclose(actual[category], value, rel_tol=1e-12, abs_tol=1e-12)
        )
        assert correct, (
            f"{aggregation} differs from the independent closed-form oracle for {category}"
        )
    weighted_total = sum(actual.values()) if case == "sum" else sum(
        actual[f"group-{category}"] * ((count - 1 - category) // 7 + 1)
        for category in range(min(count, 7))
    )
    assert math.isclose(weighted_total, count * (count + 1) // 2, rel_tol=1e-12, abs_tol=1e-9), (
        "Reducer lost generated contributions"
    )
    assert result["strategy"] == aggregation, "Reducer strategy metadata is inaccurate"
    return {"weighted_total": weighted_total}


def peak_memory() -> dict[str, Any]:
    """Read process lifetime peak RSS/working set; report unsupported APIs explicitly."""
    try:
        if sys.platform == "win32":
            from ctypes import wintypes

            class Counters(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD,
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = Counters()
            counters.cb = ctypes.sizeof(counters)
            if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
                raise ctypes.WinError(ctypes.get_last_error())
            peak = int(counters.PeakWorkingSetSize)
            method = "GetProcessMemoryInfo.PeakWorkingSetSize"
        else:
            import resource

            value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            peak = int(value if sys.platform == "darwin" else value * 1024)
            method = "resource.getrusage(RUSAGE_SELF).ru_maxrss"
        return {
            "peak_rss_bytes": peak,
            "method": method,
            "scope": "inclusive_process_high_water_mark",
            "caveat": "Includes interpreter/imports; not operation-only peak allocation.",
        }
    except (AttributeError, OSError, ImportError) as error:
        return {
            "peak_rss_bytes": None,
            "method": "unavailable",
            "scope": "inclusive_process_high_water_mark",
            "error": f"{type(error).__name__}: {error}",
        }


def source_snapshot(root: Path) -> dict[str, Any]:
    git = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=False, capture_output=True, text=True,
    )
    source = root / "python/deepviz/src/deepviz"
    hashes = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source.rglob("*")) if path.is_file() and "__pycache__" not in path.parts
    }
    return {"root": str(root.resolve()), "commit": git.stdout.strip() if git.returncode == 0 else None,
            "source_sha256": hashes}


def load_normalizer(root: Path) -> tuple[Any, Any]:
    source = (root / "python/deepviz/src").resolve()
    normalizer = source / "deepviz/normalize.py"
    if not normalizer.is_file():
        raise RuntimeError(f"Real normalization source is unavailable: {normalizer}")
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    normalize_module = importlib.import_module("deepviz.normalize")
    models_module = importlib.import_module("deepviz.models")
    for module in (normalize_module, models_module):
        if not module.__file__:
            raise RuntimeError(f"Cannot verify source location for {module.__name__}")
        location = Path(module.__file__).resolve()
        if not location.is_relative_to(source):
            raise RuntimeError(f"Refusing a package import outside the requested source root: {location}")
    return normalize_module.normalize, models_module.ChartSpec


def run_worker(root: Path, count: int, case: str, bound: int) -> dict[str, Any]:
    before = source_snapshot(root)
    normalize, ChartSpec = load_normalizer(root)
    source = CountedRows(count, case)
    spec = ChartSpec(
        kind="scatter" if case == "sample" else "bar",
        x="x" if case == "sample" else "category",
        y="value",
        aggregation=case,
        max_points=bound,
    )
    baseline = peak_memory()
    started = time.perf_counter()
    normalized = normalize(source, spec)
    elapsed = time.perf_counter() - started
    memory = peak_memory()
    result = {
        "status": "passed",
        "case": case,
        "input_kind": "generated_one_pass_python_iterator",
        "count": count,
        "input_count": normalized.input_count,
        "consumed_count": source.consumed,
        "source_exhausted": source.exhausted,
        "output_count": len(normalized.records),
        "max_points": bound,
        "strategy": normalized.strategy,
        "warnings": normalized.warnings,
        "elapsed_seconds": elapsed,
        "memory": memory,
        "baseline_memory": baseline,
    }
    oracle = validate_result(result | {"records": normalized.records}, count=count, case=case, bound=bound)
    result.update(oracle)
    result["output_sha256"] = hashlib.sha256(
        json.dumps(normalized.records, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    after = source_snapshot(root)
    if before != after:
        raise RuntimeError("Source changed during benchmark; refusing mixed-source evidence")
    result["source"] = before
    return result


def run_case(root: Path, count: int, case: str, bound: int, timeout: float) -> dict[str, Any]:
    command = [
        sys.executable, str(Path(__file__).resolve()), "--worker", "--source-root", str(root),
        "--count", str(count), "--case", case, "--max-points", str(bound),
    ]
    started = time.perf_counter()
    try:
        process = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {
            "status": "failed", "count": count, "case": case,
            "error": f"worker exceeded timeout of {timeout} seconds; no result was recorded",
        }
    if process.returncode != 0:
        return {
            "status": "failed", "count": count, "case": case,
            "error": (process.stderr or process.stdout).strip(),
        }
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        return {"status": "failed", "count": count, "case": case, "error": f"invalid worker JSON: {error}"}
    result["subprocess_elapsed_seconds"] = time.perf_counter() - started
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--counts", nargs="+", type=int, default=list(SCALES))
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    parser.add_argument("--max-points", type=int, default=2_000)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--count", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--case", choices=CASES, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if any(count < 1 for count in args.counts) or len(set(args.counts)) != len(args.counts):
        parser.error("counts must be positive and unique")
    if not 10 <= args.max_points <= 100_000 or args.timeout <= 0:
        parser.error("max-points must be 10..100000 and timeout must be positive")
    if args.output and args.output.exists():
        parser.error("output already exists; choose a unique evidence path")
    root = args.source_root.resolve()
    initial = source_snapshot(root)

    if args.worker:
        if args.count is None or args.case is None:
            parser.error("worker mode requires --count and --case")
        print(json.dumps(run_worker(root, args.count, args.case, args.max_points), allow_nan=False))
        return 0

    results: list[dict[str, Any]] = []
    work = [{"count": count, "case": case} for count in args.counts for case in args.cases]
    unrun: list[dict[str, Any]] = []
    for index, item in enumerate(work):
        print(f"{item['case']}: count={item['count']}", file=sys.stderr, flush=True)
        result = run_case(root, item["count"], item["case"], args.max_points, args.timeout)
        results.append(result)
        if result["status"] == "failed":
            unrun = work[index + 1:]
            break
    if not unrun:
        try:
            if source_snapshot(root) != initial:
                raise RuntimeError("Source changed during benchmark; refusing mixed-source evidence")
        except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
            results.append({"status": "failed", "error": str(error)})

    status = "passed" if not unrun and all(row["status"] == "passed" for row in results) else "failed"
    report = {
        "status": status,
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        "source": initial,
        "environment": {
            "python": sys.version,
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
        },
        "requested_counts": args.counts,
        "requested_cases": args.cases,
        "unrun_scales": [count for count in SCALES if count not in args.counts],
        "max_points": args.max_points,
        "results": results,
        "unrun_cases": unrun,
        "renderer_checks": {"status": "not_run", "reason": "Requires renderer-linked acceptance after NEW-03/NEW-04."},
        "columnar_checks": {"status": "not_run", "reason": "This harness measures generated Python iterators, not Arrow/Parquet readers."},
    }
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    else:
        print(encoded)
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
