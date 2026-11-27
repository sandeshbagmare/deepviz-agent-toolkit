"""Independent streaming contract checks; missing integration is a failure, not a pass."""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import pytest

from scripts import performance_suite as suite

ROOT = Path(__file__).resolve().parents[1]


def test_generator_is_lazy_and_observer_counts_only_consumed_rows():
    source = suite.CountedSource(suite.generate_rows(10_000_000, "numeric_sample"))
    assert source.consumed == 0
    assert list(itertools.islice(source, 3)) == [
        {"x": 0, "value": -50}, {"x": 1, "value": -49}, {"x": 2, "value": -48},
    ]
    assert source.consumed == 3
    assert not source.exhausted


def test_counted_source_confirms_exhaustion_without_reiterating():
    source = suite.CountedSource(suite.generate_rows(10, "category_sum"))
    assert len(list(source)) == 10
    assert source.consumed == 10
    assert source.exhausted
    assert list(source) == []
    assert source.consumed == 10


@pytest.mark.parametrize("count", [0, -1, True, 1.5])
def test_invalid_stream_count_is_rejected(count):
    with pytest.raises(ValueError):
        list(suite.generate_rows(count, "numeric_sample"))


def test_category_expected_totals_use_all_rows_and_unequal_group_sizes():
    assert suite.expected_categories(10, "sum") == {
        "group-0": 9, "group-1": 11, "group-2": 13,
        "group-3": 4, "group-4": 5, "group-5": 6, "group-6": 7,
    }
    assert suite.expected_categories(10, "mean") == {
        "group-0": 4.5, "group-1": 5.5, "group-2": 6.5,
        "group-3": 4, "group-4": 5, "group-5": 6, "group-6": 7,
    }


def test_os_peak_memory_is_positive_and_labels_its_scope():
    sample = suite.peak_memory()
    assert sample["peak_rss_bytes"] > 0
    assert sample["scope"] == "inclusive_process_high_water_mark"
    assert sample["method"] in {
        "resource.getrusage(RUSAGE_SELF).ru_maxrss",
        "GetProcessMemoryInfo.PeakWorkingSetSize",
    }


def test_result_validator_rejects_wrong_count_bound_and_aggregates():
    valid = {
        "input_count": 10, "consumed_count": 10, "source_exhausted": True,
        "records": [{"category": k, "value": v} for k, v in suite.expected_categories(10, "sum").items()],
        "strategy": "sum", "warnings": [],
    }
    checked = suite.validate_normalized(valid, 10, "category_sum", 10)
    assert checked["observed_grand_total"] == 55
    assert checked["category_values"]["group-2"] == 13
    for bad in (
        valid | {"input_count": 9}, valid | {"consumed_count": 9},
        valid | {"source_exhausted": False}, valid | {"records": valid["records"] * 2},
        valid | {"records": [{"category": "group-0", "value": 55}]},
    ):
        with pytest.raises(AssertionError):
            suite.validate_normalized(bad, 10, "category_sum", 10)


def test_peak_growth_gate_rejects_input_scaled_memory():
    small = {"count": 10, "case": "numeric_sample", "peak_rss_bytes": 20 * 1024**2}
    large = small | {"count": 10_000_000, "peak_rss_bytes": 300 * 1024**2}
    with pytest.raises(AssertionError, match="peak RSS"):
        suite.check_peak_growth([small, large], limit_bytes=64 * 1024**2)


def test_result_validator_rejects_altered_sample_and_undisclosed_loss():
    records = [{"x": i * 10, "value": (i * 10) % 101 - 50} for i in range(10)]
    valid = {"input_count": 100, "consumed_count": 100, "source_exhausted": True,
             "records": records, "strategy": "sample", "warnings": ["sampled"]}
    suite.validate_normalized(valid, 100, "numeric_sample", 10)
    for bad in (valid | {"warnings": []}, valid | {"records": records[:-1]},
                valid | {"records": [{"x": 99, "value": -999}] + records[1:]}):
        with pytest.raises(AssertionError):
            suite.validate_normalized(bad, 100, "numeric_sample", 10)


def test_missing_source_cannot_report_a_successful_worker(tmp_path):
    with pytest.raises(RuntimeError, match="Worker failed"):
        suite.run_worker(tmp_path, count=10, case="numeric_sample", max_points=10)


def test_changed_source_cannot_be_combined_into_one_benchmark():
    before = {"commit": "a" * 40, "sha256": {"normalize.py": "old"}}
    suite.require_same_source(before, before)
    with pytest.raises(AssertionError, match="Source changed"):
        suite.require_same_source(before, before | {"sha256": {"normalize.py": "new"}})
    with pytest.raises(AssertionError, match="Source changed"):
        suite.require_same_source(before, before | {"commit": "b" * 40})


@pytest.mark.parametrize("suffix,contents", [
    (".svg", '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L2 2"/></svg>'),
    (".html", '<html><script type="application/json">{"x": 1}</script></html>'),
])
def test_artifact_structure_inspection_is_not_reported_as_browser_execution(tmp_path, suffix, contents):
    path = tmp_path / f"artifact{suffix}"
    path.write_text(contents, encoding="utf-8")
    result = suite.inspect_artifact(path)
    assert "not_" in result["inspection"]
    path.write_text("<svg/>" if suffix == ".svg" else "<html/>", encoding="utf-8")
    with pytest.raises(AssertionError):
        suite.inspect_artifact(path)


def test_png_inspection_rejects_a_decodable_but_blank_image(tmp_path):
    from PIL import Image

    path = tmp_path / "artifact.png"
    image = Image.new("RGB", (4, 4), "white")
    image.save(path)
    with pytest.raises(AssertionError, match="single flat color"):
        suite.inspect_artifact(path)
    image.putpixel((1, 1), (0, 0, 0))
    image.save(path)
    assert suite.inspect_artifact(path)["inspection"] == "png_decoded_nonuniform_pixels_not_visual_review"


@pytest.mark.integration
@pytest.mark.parametrize("case", ["numeric_sample", "category_sum", "category_mean"])
@pytest.mark.parametrize("count", [10, 1_000])
def test_real_normalization_preserves_counts_and_expected_reductions(case, count):
    result = suite.run_case(ROOT, count=count, case=case, max_points=10)
    assert result["input_count"] == result["consumed_count"] == count
    assert result["output_count"] <= 10
    assert result["status"] == "passed"
    assert result["peak_rss_bytes"] > 0


@pytest.mark.integration
def test_reservoir_is_repeatable_but_not_a_truncated_prefix():
    first = suite.normalize_case(ROOT, 1_000, "numeric_sample", 10)
    second = suite.normalize_case(ROOT, 1_000, "numeric_sample", 10)
    assert first["records"] == second["records"]
    xs = [row["x"] for row in first["records"]]
    assert xs == sorted(xs)
    assert len(set(xs)) == 10
    assert max(xs) > 100
    assert first["strategy"] == "sample"
    assert first["warnings"]


@pytest.mark.integration
def test_high_cardinality_mean_other_bucket_is_weighted():
    normalize, ChartSpec, _ = suite.load_api(ROOT)
    # Ten groups of size one, then 90 extra observations in an overflow group.
    source = ({"category": f"g-{i if i < 10 else 10}", "value": i + 1} for i in range(100))
    result = normalize(source, ChartSpec(kind="bar", x="category", y="value", aggregation="mean", max_points=10))
    assert result.input_count == 100
    assert len(result.records) == 10
    assert result.warnings
    retained = {row["category"]: row["value"] for row in result.records[:9]}
    assert retained == {f"g-{i}": i + 1 for i in range(9)}
    assert math.isclose(result.records[-1]["value"], 55.0, rel_tol=1e-12)


@pytest.mark.integration
@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_all_renderers_receive_bounded_records(engine, tmp_path):
    result = suite.run_case(ROOT, count=1_000, case="numeric_sample", max_points=10,
                            engine=engine, artifact_dir=tmp_path)
    assert result["input_count"] == 1_000
    assert result["renderer_input_count"] == 10
    assert result["renderer_output_count"] <= 10
    assert result["artifacts"]
    assert all(item["inspection"] for item in result["artifacts"])


@pytest.mark.integration
def test_fresh_worker_reports_exact_input_and_source_provenance():
    result = suite.run_worker(ROOT, count=10, case="category_sum", max_points=10)
    assert result["status"] == "passed"
    assert result["consumed_count"] == 10
    assert result["output_count"] == 7
    assert result["elapsed_seconds"] >= 0
    assert len(result["source"]["commit"]) == 40
    assert "python/deepviz/src/deepviz/normalize.py" in result["source"]["sha256"]
    json.dumps(result, allow_nan=False)


@pytest.mark.scale
@pytest.mark.parametrize("count", [100_000, 1_000_000, 10_000_000])
@pytest.mark.parametrize("case", ["numeric_sample", "category_sum", "category_mean"])
def test_large_real_stream_contract(count, case):
    result = suite.run_worker(ROOT, count=count, case=case, max_points=2000)
    assert result["status"] == "passed"
    assert result["consumed_count"] == count
    assert result["output_count"] <= 2000
