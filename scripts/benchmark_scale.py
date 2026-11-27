"""Measure real generator normalization, one isolated process per size/mode.

Run from a checkout with its src on PYTHONPATH (or with the package installed):
    python scripts/benchmark_scale.py

JSONL output reports wall-clock processing time and the operating system's
whole-process peak resident memory, *not* an estimate based on output size.
--trace-memory additionally measures Python allocations, at substantial overhead.
No large source list or artifact is created. Sum results are checked against the
closed-form total of the generated input, and every worker checks input_count.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tracemalloc
from collections.abc import Iterator
from pathlib import Path
from time import perf_counter
from typing import Any


def _peak_rss() -> int:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class MemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(counters.PeakWorkingSetSize)
    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


def _measure(size: int, mode: str, max_points: int, trace: bool) -> dict[str, Any]:
    from deepviz.normalize import normalize

    baseline = _peak_rss()
    if trace:
        tracemalloc.start()
    started = perf_counter()
    source: Iterator[dict[str, Any]]
    if mode == "sample":
        source = ({"x": i, "y": i * 2} for i in range(size))
        spec = {"kind": "scatter", "x": "x", "y": "y", "aggregation": "sample", "max_points": max_points}
    else:
        source = ({"x": str(i % 100), "y": i} for i in range(size))
        spec = {"kind": "bar", "x": "x", "y": "y", "aggregation": "sum", "max_points": max_points}
    result = normalize(source, spec)
    elapsed = perf_counter() - started
    traced_peak = tracemalloc.get_traced_memory()[1] if trace else None
    if trace:
        tracemalloc.stop()
    peak = _peak_rss()
    if result.input_count != size or len(result.records) > max_points:
        raise AssertionError("Normalizer violated its count/bounded-output contract")
    if mode == "sum" and sum(row["y"] for row in result.records) != size * (size - 1) // 2:
        raise AssertionError("Grouped reduction lost generated observations")
    return {
        "mode": mode, "input_count": result.input_count, "output_count": len(result.records),
        "strategy": result.strategy, "elapsed_seconds": round(elapsed, 6),
        "rows_per_second": round(size / elapsed), "peak_rss_bytes": peak,
        "baseline_peak_rss_bytes": baseline, "peak_rss_increase_bytes": peak - baseline,
        "traced_peak_bytes": traced_peak, "warnings": result.warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10, 1000, 100000, 1000000, 10000000])
    parser.add_argument("--modes", nargs="+", choices=["sample", "sum"], default=["sample", "sum"])
    parser.add_argument("--max-points", type=int, default=2000)
    parser.add_argument("--trace-memory", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if any(size < 0 for size in args.sizes):
        parser.error("sizes must be non-negative")
    if args.worker:
        print(json.dumps(_measure(args.sizes[0], args.modes[0], args.max_points, args.trace_memory)))
        return
    for size in args.sizes:
        for mode in args.modes:
            command = [
                sys.executable, str(Path(__file__).resolve()), "--worker", "--sizes", str(size),
                "--modes", mode, "--max-points", str(args.max_points),
            ]
            if args.trace_memory:
                command.append("--trace-memory")
            completed = subprocess.run(command, check=True, capture_output=True, text=True)
            print(completed.stdout.strip(), flush=True)


if __name__ == "__main__":
    main()
