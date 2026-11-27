"""Validate raw/compact R14 Python observations; this does not rerun measurements."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

COMMITS = {"reference": "6d0e72ebef4b622f8dec2bce2bd07cc23e7a81ce",
           "candidate": "ec9f669eff28cd5351da142765b7755e3b2f484f"}
NORMALIZERS = {"reference": "0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83",
               "candidate": "34e8ed94a479acb2d7360a79ba4f62897bb453928fc1eec97efceb052a5e76f2"}


def fingerprint(value: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def compact(raw: dict[str, Any]) -> dict[str, Any]:
    result = {key: value for key, value in raw.items() if key != "results"}
    result.update(source_snapshots={}, results=[])
    for original in raw["results"]:
        row = {key: value for key, value in original.items() if key not in {"source_before", "source_after"}}
        before, after = original["source_before"], original["source_after"]
        assert before == after and not before["dirty_paths"], "Source changed; invalidate evidence"
        if row["label"] in result["source_snapshots"]:
            assert result["source_snapshots"][row["label"]] == before
        result["source_snapshots"][row["label"]] = before
        row.update(source_before_sha256=fingerprint(before), source_after_sha256=fingerprint(after))
        result["results"].append(row)
    return result


def verify(data: dict[str, Any]) -> dict[str, int]:
    if not __debug__:
        raise RuntimeError("Evidence assertions require non-optimized Python")
    if "source_snapshots" not in data:
        data = compact(data)
    assert data["status"] == "observations_complete" and not data["errors"]
    assert data["new_maximum_rows"] == 100000
    for label, source in data["source_snapshots"].items():
        assert source["commit"] == COMMITS[label] and source["dirty_paths"] == []
        assert source["sha256"]["python/deepviz/src/deepviz/normalize.py"] == NORMALIZERS[label]
        assert source["sha256"]["python/deepviz/src/deepviz/models.py"] == "890ecb0e29e1345364b2bf4840bdea7a542067003caf54d7b0855536ee2b6a76"
        assert all(re.fullmatch(r"[0-9a-f]{64}", digest) for digest in source["sha256"].values())
        expected_loaded = {"deepviz": "python/deepviz/src/deepviz/__init__.py"} | {
            "deepviz." + name: f"python/deepviz/src/deepviz/{name}.py"
            for name in ("normalize", "models", "render", "engines")}
        assert source["loaded_modules"] == expected_loaded, "Wrong imported module source"
    assert set(data["source_snapshots"]) == set(COMMITS)
    expected = Counter((label, case, count, repeat, False) for label in COMMITS
                       for case in ("ordinary", "promoted") for count in (96, 6000, 100000)
                       for repeat in range(1, 4 if count == 100000 else 2))
    expected.update((label, case, 100000, 1, True) for label in COMMITS for case in ("ordinary", "promoted"))
    rows = data["results"]
    assert Counter((r["label"], r["case"], r["requested_count"], r["repeat"], r["state_case"]) for r in rows) == expected
    outcomes: Counter[str] = Counter()
    for row in rows:
        digest = fingerprint(data["source_snapshots"][row["label"]])
        assert row["source_before_sha256"] == row["source_after_sha256"] == digest
        assert row["worker_exit"] == 0 and type(row["worker_pid"]) is int and row["worker_pid"] > 0
        assert math.isfinite(row["elapsed_seconds"]) and row["elapsed_seconds"] >= 0
        assert row["subprocess_wall_seconds"] >= row["elapsed_seconds"]
        method = ("GetProcessMemoryInfo.PeakWorkingSetSize" if data["platform"] == "win32"
                  else "resource.getrusage(RUSAGE_SELF).ru_maxrss")
        assert row["method"] == method and row["scope"] == "inclusive_process_high_water_mark"
        assert row["peak_rss_bytes"] >= row["baseline_peak_rss_bytes"] > 0
        assert row["peak_high_water_growth_bytes"] == row["peak_rss_bytes"] - row["baseline_peak_rss_bytes"]
        assert type(row["consumed_count"]) is int
        if row["state_case"]:
            assert row["oracle_status"] == "early_state_budget_rejection"
            assert 32 < row["consumed_count"] < row["requested_count"] == 100000 and not row["source_exhausted"]
            assert all(row[key] is None for key in ("input_count", "output_count", "records", "strategy", "warnings"))
            assert row["error"] == "ValueError: Normalized retained data exceeds 16777216 bytes"
        else:
            count = row["requested_count"]
            assert row["error"] is None and row["strategy"] == "sum" and row["source_exhausted"] is True
            assert row["input_count"] == row["consumed_count"] == count <= 100000
            assert row["output_count"] == len(row["records"]) == 4
            mismatch = row["label"] == "reference" and row["case"] == "promoted"
            assert row["oracle_status"] == ("oracle_mismatch" if mismatch else "match")
            values = [None] * 4 if mismatch else [(count // 24) * (group + 4) for group in range(4)]
            assert row["records"] == [{"g": f"g-{group}", "v": value} for group, value in enumerate(values)]
            assert row["warnings"] == (["4 non-finite numeric values replaced by null."] if mismatch else [])
        outcomes[row["oracle_status"]] += 1
    return {"workers": len(rows), "exact_matches": outcomes["match"],
            "baseline_oracle_mismatches": outcomes["oracle_mismatch"],
            "early_state_rejections": outcomes["early_state_budget_rejection"],
            "full_exhausted_rows": sum(r["consumed_count"] for r in rows if not r["state_case"]),
            "observed_pulls": sum(r["consumed_count"] for r in rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.receipt.read_text(encoding="utf-8"))), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
