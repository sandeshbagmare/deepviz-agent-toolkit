"""Independent probe controls; Fraction is used only on six-term oracle fixtures."""
from __future__ import annotations

import copy
import importlib.util
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest


def probe():
    path = Path(__file__).with_name("promotion_probe.py")
    assert path.is_file(), "Independent promotion probe has not been implemented"
    spec = importlib.util.spec_from_file_location("role11_promotion_probe", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("case", ["ordinary", "promoted"])
@pytest.mark.parametrize("count", [24, 96, 6000, 100000])
def test_closed_form_oracle_counts_complete_six_term_cycles_and_zero_padding(case, count):
    api = probe()
    for group in range(4):
        tiny_fixture = api.terms(case, group)
        assert len(tiny_fixture) == 6
        assert sum(map(Fraction.from_float, tiny_fixture), Fraction()) == group + 4
    expected = [{"g": f"g-{group}", "v": (count // 24) * (group + 4)} for group in range(4)]
    assert api.oracle(count) == expected


def test_row_source_has_no_length_and_is_exhausted_only_by_full_consumption():
    api = probe()
    rows = api.CountedSource(api.rows(31, "promoted"))
    assert not hasattr(rows, "__len__") and not hasattr(rows, "__length_hint__")
    assert next(rows) == {"g": "g-0", "v": 1e308}
    assert rows.consumed == 1 and not rows.exhausted
    for _ in rows:
        pass
    assert rows.consumed == 31 and rows.exhausted


@pytest.mark.parametrize("count", [0, -1, 100001, 1000000, True])
def test_refuses_out_of_scope_counts_before_generating_rows(count):
    with pytest.raises(ValueError, match="100000"):
        next(probe().rows(count, "ordinary"))


def valid_result():
    return {"requested_count": 96, "input_count": 96, "consumed_count": 96,
            "source_exhausted": True, "records": probe().oracle(96), "output_count": 4,
            "strategy": "sum", "warnings": [], "error": None}


def test_exact_result_matches_without_approximate_numeric_tolerance():
    assert probe().validate_result(valid_result()) == "match"


@pytest.mark.parametrize("mutation", ["count", "pulls", "exhaustion", "bound", "strategy", "warning",
                                     "value", "duplicate", "null", "error"])
def test_strict_count_value_and_loss_guard_rejects_altered_results(mutation):
    result = valid_result()
    if mutation == "count":
        result["input_count"] -= 1
    elif mutation == "pulls":
        result["consumed_count"] -= 1
    elif mutation == "exhaustion":
        result["source_exhausted"] = False
    elif mutation == "bound":
        result["output_count"] += 1
    elif mutation == "strategy":
        result["strategy"] = "sample"
    elif mutation == "warning":
        result["warnings"] = ["unknown loss"]
    elif mutation == "value":
        result["records"][0]["v"] += 1
    elif mutation == "duplicate":
        result["records"][1] = copy.deepcopy(result["records"][0])
    elif mutation == "null":
        result["records"][0]["v"] = None
    else:
        result["error"] = "some other error"
    with pytest.raises(AssertionError):
        probe().validate_result(result)


def test_baseline_null_sum_is_classified_as_a_real_oracle_mismatch_not_a_pass():
    result = valid_result()
    result["records"] = [{"g": f"g-{group}", "v": None} for group in range(4)]
    result["warnings"] = ["4 non-finite numeric values replaced by null."]
    assert probe().validate_result(result, allow_known_red=True) == "oracle_mismatch"


@pytest.mark.parametrize("mutation", ["commit", "hash", "dirty", "module", "missing_file"])
def test_source_guard_rejects_mixed_dirty_or_wrong_import_provenance(mutation):
    before: dict[str, Any] = {"commit": "a" * 40, "sha256": {"deepviz/normalize.py": "b" * 64}, "dirty_paths": [],
                              "loaded_modules": {"deepviz.normalize": "deepviz/normalize.py"}}
    after = copy.deepcopy(before)
    if mutation == "commit":
        after["commit"] = "c" * 40
    elif mutation == "hash":
        after["sha256"]["deepviz/normalize.py"] = "c" * 64
    elif mutation == "dirty":
        after["dirty_paths"] = ["deepviz/normalize.py"]
    elif mutation == "module":
        after["loaded_modules"]["deepviz.normalize"] = "../wrong.py"
    else:
        after["sha256"].clear()
    with pytest.raises(AssertionError):
        probe().require_source(before, after)


def test_state_rejection_needs_an_early_budget_error_not_fake_exhaustion_or_results():
    api = probe()
    valid = {"requested_count": 100000, "input_count": None, "consumed_count": 42000,
             "source_exhausted": False, "records": None, "output_count": None,
             "strategy": None, "warnings": None, "error": "ValueError: retained state exceeds 16777216 bytes"}
    assert api.validate_rejection(valid) == "early_state_budget_rejection"
    for key, bad in [("consumed_count", 100000), ("source_exhausted", True), ("records", []),
                     ("error", "ValueError: unrelated field error")]:
        changed = valid | {key: bad}
        with pytest.raises(AssertionError):
            api.validate_rejection(changed)
