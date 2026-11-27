"""Portable evidence controls; these do not rerun any 10M input stream."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
PIN = "0c5fa825f7058f8c5a4ab6ec9597b9fd5fd4ca43"


def validator():
    path = Path(__file__).with_name("verify_scale_receipt.py")
    assert path.is_file(), "Portable evidence verifier has not been implemented"
    spec = importlib.util.spec_from_file_location("role11_scale_receipt", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_receipt


def receipt() -> dict[str, Any]:
    return json.loads((ROOT / "docs/coordination/evidence/R10-11/baseline-0c5fa82.json").read_text())


def test_preserved_real_receipt_has_twenty_workers_and_exact_counts():
    checked = validator()(receipt(), PIN)
    assert checked == {"workers": 20, "consumed_rows": 44_404_040, "sample_pairs": 5, "memory_gates": 3}


@pytest.mark.parametrize("mutation", [
    "incomplete", "wrong_source", "unexhausted", "wrong_count", "wrong_bound",
    "undisclosed_loss", "changed_sample", "wrong_aggregate", "missing_category",
    "allocation_not_os_peak", "memory_gate", "duplicate_repeat",
])
def test_receipt_validator_rejects_misleading_evidence(mutation: str):
    data = copy.deepcopy(receipt())
    sample = next(row for row in data["results"] if row["case"] == "numeric_sample" and row["count"] == 10_000_000)
    aggregate = next(row for row in data["results"] if row["case"] == "category_sum" and row["count"] == 10_000_000)
    if mutation == "incomplete":
        data["results"].pop()
    elif mutation == "wrong_source":
        data["source"]["commit"] = "f" * 40
    elif mutation == "unexhausted":
        sample["source_exhausted"] = False
    elif mutation == "wrong_count":
        sample["consumed_count"] -= 1
    elif mutation == "wrong_bound":
        sample["output_count"] += 1
    elif mutation == "undisclosed_loss":
        sample["warnings"] = []
    elif mutation == "changed_sample":
        sample["output_sha256"] = "0" * 64
    elif mutation == "wrong_aggregate":
        aggregate["category_values"]["group-0"] += 1
    elif mutation == "missing_category":
        aggregate["category_values"].pop("group-6")
    elif mutation == "allocation_not_os_peak":
        sample["method"] = "tracemalloc"
    elif mutation == "memory_gate":
        data["memory_growth_checks"][0]["inclusive_peak_growth_bytes"] += 1
    else:
        sample["repeat"] = 2
    with pytest.raises(AssertionError):
        validator()(data, PIN)
