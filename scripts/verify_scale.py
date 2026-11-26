"""Exercise the one-pass normalization path and report honest time/memory measurements."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import tracemalloc
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from deepviz.models import ChartSpec, NormalizedData

SCALES = (10, 1_000, 100_000, 1_000_000, 10_000_000)


def check_result(result: NormalizedData, count: int, consumed: int, bound: int) -> None:
    assert result.input_count == count, f"input_count {result.input_count} != {count}"
    assert consumed == count, f"stream consumed {consumed} != {count}"
    assert len(result.records) <= bound, f"output bound exceeded: {len(result.records)} > {bound}"
    assert len(result.records) == min(count, bound), "Sampling unexpectedly lost output records"
    if count > bound:
        assert result.strategy != "none" and result.warnings, "lossy reduction must disclose strategy and warning"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, choices=SCALES, required=True)
    parser.add_argument("--max-points", type=int, default=2_000)
    parser.add_argument("--max-memory-mib", type=float, default=512)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from deepviz.normalize import normalize

    consumed = 0

    def records() -> Iterator[dict[str, Any]]:
        nonlocal consumed
        for index in range(args.count):
            consumed += 1
            yield {"x": index, "y": index % 97}

    spec = ChartSpec(kind="scatter", x="x", y="y", aggregation="sample", max_points=args.max_points)
    tracemalloc.start()
    started = time.perf_counter()
    result = normalize(records(), spec)
    elapsed = time.perf_counter() - started
    _, python_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_rss_mib = None
    if sys.platform == "linux":
        import resource

        peak_rss_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    report = {
        "source_commit": os.environ.get("GITHUB_SHA", "local-unrecorded"),
        "input_count": result.input_count, "consumed": consumed, "output_count": len(result.records),
        "max_points": args.max_points, "strategy": result.strategy, "warnings": result.warnings,
        "elapsed_seconds": elapsed, "python_peak_mib": python_peak / 1024**2,
        "process_peak_rss_mib": peak_rss_mib, "memory_ceiling_mib": args.max_memory_mib,
        "memory_method": (
            "tracemalloc peak during normalization (Python allocations, excludes native allocations); "
            "Linux process lifetime ru_maxrss includes interpreter/dependencies/native allocations. "
            "Fresh process per scale; input is a generator, never a prebuilt list."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    check_result(result, args.count, consumed, args.max_points)
    assert python_peak / 1024**2 <= args.max_memory_mib, "Python allocation memory ceiling exceeded"
    if peak_rss_mib is not None:
        assert peak_rss_mib <= args.max_memory_mib, "Process RSS memory ceiling exceeded"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
