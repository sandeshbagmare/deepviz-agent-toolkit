"""Negative controls for the bounded receipt verifier; no production data reruns."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest


def verifier():
    path = Path(__file__).with_name("verify_promotion_evidence.py")
    assert path.is_file(), "Independent evidence verifier is not implemented"
    spec = importlib.util.spec_from_file_location("role11_promotion_verify", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def fixture():
    path = Path(__file__).resolve().parents[3] / "docs/coordination/evidence/R14-11/bounded-matrix.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_real_receipt_keeps_five_expected_product_reds_and_four_budget_rejections():
    result = verifier()(fixture())
    assert result == {"workers": 24, "exact_matches": 15, "baseline_oracle_mismatches": 5,
                      "early_state_rejections": 4, "full_exhausted_rows": 1224384,
                      "observed_pulls": 1403326}


@pytest.mark.parametrize("mutation", ["incomplete", "allocation_not_os", "negative_time", "bad_peak_delta",
                                     "wrong_source", "source_changed", "wrong_loaded_module", "dirty",
                                     "count", "value", "warning", "hide_baseline_red", "rejects_too_late"])
def test_portable_verifier_rejects_altered_source_count_time_memory_and_loss_evidence(mutation):
    data = copy.deepcopy(fixture())
    row = next(row for row in data["results"] if row["label"] == "candidate" and not row["state_case"])
    if mutation == "incomplete":
        data["results"].pop()
    elif mutation == "allocation_not_os":
        row["method"] = "tracemalloc"
    elif mutation == "negative_time":
        row["elapsed_seconds"] = -1
    elif mutation == "bad_peak_delta":
        row["peak_high_water_growth_bytes"] += 1
    elif mutation == "wrong_source":
        data["source_snapshots"]["candidate"]["commit"] = "f" * 40
    elif mutation == "source_changed":
        row["source_after_sha256"] = "f" * 64
    elif mutation == "wrong_loaded_module":
        data["source_snapshots"]["candidate"]["loaded_modules"]["deepviz.normalize"] = "../wrong.py"
    elif mutation == "dirty":
        data["source_snapshots"]["candidate"]["dirty_paths"] = ["normalize.py"]
    elif mutation == "count":
        row["consumed_count"] -= 1
    elif mutation == "value":
        row["records"][0]["v"] += 1
    elif mutation == "warning":
        row["warnings"] = ["Unknown loss"]
    elif mutation == "hide_baseline_red":
        next(row for row in data["results"] if row["oracle_status"] == "oracle_mismatch")["oracle_status"] = "match"
    else:
        row = next(row for row in data["results"] if row["state_case"])
        row["consumed_count"] = row["requested_count"]
    with pytest.raises(AssertionError):
        verifier()(data)
