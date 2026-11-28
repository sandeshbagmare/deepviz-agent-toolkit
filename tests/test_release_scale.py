"""Independent controls for normalization-scale evidence, without renderer claims."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_python_scale.py"


@pytest.fixture
def harness() -> Any:
    spec = importlib.util.spec_from_file_location("release_scale", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def observation(records: list[dict[str, Any]], count: int, strategy: str) -> dict[str, Any]:
    return {
        "records": records,
        "input_count": count,
        "consumed_count": count,
        "source_exhausted": True,
        "strategy": strategy,
        "warnings": ["Sampling disclosed"] if strategy == "sample" and count > len(records) else [],
    }


def test_requested_release_scales_and_generated_source(harness: Any) -> None:
    assert harness.SCALES == (10, 1_000, 100_000, 1_000_000, 10_000_000)
    source = harness.CountedRows(10, "sample")
    assert next(source) == {"x": 0, "value": -50}
    assert source.consumed == 1 and not source.exhausted
    with pytest.raises(AssertionError, match="materializ"):
        list(source)
    remaining = [row for row in source]
    assert len(remaining) == 9 and remaining[-1] == {"x": 9, "value": -41}
    assert source.consumed == 10 and source.exhausted


@pytest.mark.parametrize("case,values", [
    ("sum", [27, 30, 33, 12, 13, 14, 15]),
    ("mean", [9, 10, 11, 12, 13, 14, 15]),
])
def test_closed_form_reducer_oracles_use_all_generated_rows(harness: Any, case: str, values: list[int]) -> None:
    # 17 values grouped by index % 7: 1+8+15, 2+9+16, 3+10+17, 4+11, ...
    correct = [24, 27, 30, 15, 17, 19, 21] if case == "sum" else [8, 9, 10, 7.5, 8.5, 9.5, 10.5]
    rows = [{"category": f"group-{index}", "value": value} for index, value in enumerate(correct)]
    summary = harness.validate_result(observation(rows, 17, case), count=17, case=case, bound=10)
    assert summary["weighted_total"] == 153
    # Plausible values from a different stream must not pass on counts alone.
    wrong = [{"category": f"group-{index}", "value": value} for index, value in enumerate(values)]
    with pytest.raises(AssertionError, match=case):
        harness.validate_result(observation(wrong, 17, case), count=17, case=case, bound=10)


def test_sample_accepts_only_unchanged_unique_rows_and_disclosed_loss(harness: Any) -> None:
    indices = [0, 111, 222, 333, 444, 555, 666, 777, 888, 999]
    rows = [{"x": index, "value": index % 101 - 50} for index in indices]
    report = observation(rows, 1001, "sample")
    harness.validate_result(report, count=1001, case="sample", bound=10)
    for field, bad in [("input_count", 1000), ("consumed_count", 1000),
                       ("source_exhausted", False), ("strategy", "none"), ("warnings", [])]:
        with pytest.raises(AssertionError):
            harness.validate_result(report | {field: bad}, count=1001, case="sample", bound=10)
    for bad_rows in [rows[:-1], rows + [rows[-1]], [rows[0], *rows[:-1]],
                     [rows[0] | {"value": 999}, *rows[1:]], list(reversed(rows))]:
        with pytest.raises(AssertionError):
            harness.validate_result(report | {"records": bad_rows}, count=1001, case="sample", bound=10)


def test_reducer_cannot_hide_duplicated_categories_or_wrong_strategy(harness: Any) -> None:
    rows = [{"category": f"group-{index}", "value": value}
            for index, value in enumerate([24, 27, 30, 15, 17, 19, 21])]
    for bad_rows in [rows[:-1], [rows[0], *rows[:-1]]]:
        with pytest.raises(AssertionError):
            harness.validate_result(observation(bad_rows, 17, "sum"), count=17, case="sum", bound=10)
    with pytest.raises(AssertionError):
        harness.validate_result(observation(rows, 17, "none"), count=17, case="sum", bound=10)


def test_large_integer_sum_cannot_lose_even_one_contribution(harness: Any) -> None:
    # Seven million source integers, partitioned into seven arithmetic progressions.
    totals = [3_499_997_500_000, 3_499_998_500_000, 3_499_999_500_000, 3_500_000_500_000,
              3_500_001_500_000, 3_500_002_500_000, 3_500_003_500_000]
    rows: list[dict[str, Any]] = [
        {"category": f"group-{index}", "value": total} for index, total in enumerate(totals)
    ]
    harness.validate_result(observation(rows, 7_000_000, "sum"), count=7_000_000, case="sum", bound=10)
    rows[0]["value"] -= 1
    with pytest.raises(AssertionError, match="sum"):
        harness.validate_result(observation(rows, 7_000_000, "sum"), count=7_000_000, case="sum", bound=10)


def test_real_process_memory_has_a_named_method_or_explicit_unavailability(harness: Any) -> None:
    result = harness.peak_memory()
    assert result["scope"] == "inclusive_process_high_water_mark"
    if result["peak_rss_bytes"] is None:
        assert result["method"] == "unavailable" and result["error"]
    else:
        assert result["peak_rss_bytes"] > 0
        assert result["method"] in {
            "GetProcessMemoryInfo.PeakWorkingSetSize",
            "resource.getrusage(RUSAGE_SELF).ru_maxrss",
        }


def test_source_stability_ignores_non_source_metadata_but_rejects_hash_changes(harness: Any) -> None:
    before = {"commit": "abc", "dirty_paths": [], "source_sha256": {"module.py": "one"}}
    after = before | {"dirty_paths": ["?? generated.svg"]}
    harness.require_same_source(before, after)
    changed_source = after | {"source_sha256": {"module.py": "two"}}
    with pytest.raises(AssertionError, match="Source changed"):
        harness.require_same_source(before, changed_source)


def test_missing_source_records_a_failed_case_without_a_fabricated_measurement(tmp_path: Path) -> None:
    (tmp_path / "python/deepviz/src/deepviz").mkdir(parents=True)
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--source-root", str(tmp_path), "--counts", "10", "--cases", "sum"],
        capture_output=True, text=True, timeout=30,
    )
    assert process.returncode == 1
    report = json.loads(process.stdout)
    assert report["status"] == "failed" and len(report["results"]) == 1
    result = report["results"][0]
    assert result["status"] == "failed" and result["count"] == 10 and result["case"] == "sum"
    assert "normalize.py" in result["error"]
    assert "elapsed_seconds" not in result and "output_count" not in result
    assert report["renderer_checks"]["status"] == "not_run"
    assert report["unrun_scales"] == [1000, 100000, 1000000, 10000000]


def test_evidence_output_is_never_overwritten(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"
    output.write_text("preserve evidence", encoding="utf-8")
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--counts", "10", "--cases", "sum", "--output", str(output)],
        capture_output=True, text=True, timeout=30,
    )
    assert process.returncode == 2 and "already exists" in process.stderr
    assert output.read_text(encoding="utf-8") == "preserve evidence"
