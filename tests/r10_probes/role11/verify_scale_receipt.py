"""Verify saved performance_suite JSON without rerunning a dataset or importing DeepViz.

Accepts the original matrix or its compact R10 receipt. Original worker assertions
checked retained sample values before hashing; this checks their reported counts,
repeated hashes and metadata, not independent reconstruction or measurement truth.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

COUNTS = [10, 1_000, 100_000, 1_000_000, 10_000_000]
CASES = ["numeric_sample", "category_sum", "category_mean"]


def validate_receipt(data: dict[str, Any], expected_sha: str) -> dict[str, int]:
    if not __debug__:
        raise RuntimeError("Evidence assertions must not run under Python optimization")
    assert re.fullmatch(r"[0-9a-f]{40}", expected_sha), "Expected SHA must be a full commit ID"
    assert data["status"] == "passed" and data["errors"] == [], "Matrix did not pass"
    source = data["source"]
    assert source["commit"] == expected_sha and source["dirty_paths"] == [], "Wrong or dirty source"
    for name in ("normalize.py", "models.py"):
        assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"][f"python/deepviz/src/deepviz/{name}"])
    assert data["requested_counts"] == COUNTS and data["requested_cases"] == CASES
    assert data["numeric_repeats"] == 2 and data["render_counts"] == [], "Wrong matrix scope"
    expected = Counter({(case, count): 2 if case == "numeric_sample" else 1
                        for case in CASES for count in COUNTS})
    rows = data["results"]
    assert Counter((row["case"], row["count"]) for row in rows) == expected, "Incomplete matrix"
    for row in rows:
        count, case = row["count"], row["case"]
        assert row["status"] == "passed" and row.get("source", source) == source
        assert type(row["input_count"]) is int and row["input_count"] == row["consumed_count"] == count
        assert row["source_exhausted"] is True and row["max_points"] == 2_000
        assert row["scope"] == "inclusive_process_high_water_mark"
        method = ("GetProcessMemoryInfo.PeakWorkingSetSize" if data["platform"].startswith("Windows")
                  else "resource.getrusage(RUSAGE_SELF).ru_maxrss")
        assert row["method"] == method, "Not the declared OS process-peak method"
        assert row["peak_rss_bytes"] >= row["baseline_peak_rss_bytes"] > 0
        assert row["peak_high_water_growth_bytes"] == row["peak_rss_bytes"] - row["baseline_peak_rss_bytes"]
        assert row["growth_scope"] == "difference_of_process_high_water_marks_not_operation_peak_allocation"
        assert math.isfinite(row["elapsed_seconds"]) and row["elapsed_seconds"] >= 0
        assert row["subprocess_wall_seconds"] >= row["elapsed_seconds"]
        assert re.fullmatch(r"[0-9a-f]{64}", row["output_sha256"])
        if case == "numeric_sample":
            assert row["strategy"] == "sample" and row["output_count"] == min(count, 2_000)
            assert bool(row["warnings"]) == (count > 2_000), "Sampling loss not disclosed"
        else:
            assert row["strategy"] == case.removeprefix("category_") and row["output_count"] == 7
            values = {}
            for category in range(7):
                size = (count - category + 6) // 7
                first = category + 1
                last = first + 7 * (size - 1)
                values[f"group-{category}"] = (size * (first + last) // 2 if case == "category_sum"
                                               else (first + last) / 2)
            assert row["category_values"] == values, "Exact aggregate values differ"
            assert row["observed_grand_total"] == count * (count + 1) // 2
    for count in COUNTS:
        samples = [row for row in rows if row["case"] == "numeric_sample" and row["count"] == count]
        assert {row["repeat"] for row in samples} == {1, 2}, "Duplicate repeat"
        assert len({row["output_sha256"] for row in samples}) == 1, "Samples are not repeatable"
    gates = data["memory_growth_checks"]
    assert len(gates) == 3 and {gate["case"] for gate in gates} == set(CASES)
    for gate in gates:
        case_rows = [row for row in rows if row["case"] == gate["case"]]
        baseline = min(row["peak_rss_bytes"] for row in case_rows if row["count"] == 10)
        growth = max(row["peak_rss_bytes"] for row in case_rows) - baseline
        assert gate["inclusive_peak_growth_bytes"] == growth <= gate["limit_bytes"] == 64 * 1024**2
    return {"workers": len(rows), "consumed_rows": sum(row["consumed_count"] for row in rows),
            "sample_pairs": len(COUNTS), "memory_gates": len(gates)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    data = json.loads(args.receipt.read_text(encoding="utf-8"))
    result = validate_receipt(data, args.expected_sha)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
