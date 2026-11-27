"""Strict small mean/column regressions; no production or prior SUM edits."""
from __future__ import annotations

import importlib
import json
import os
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize

TINY = float.fromhex("0x0.0000000000001p-1022")
SOURCE_COMMIT = "ec9f669eff28cd5351da142765b7755e3b2f484f"
MEAN_CASES = [
    ("split-subnormal-positive", [1.0, TINY, -1.0, TINY, TINY], TINY),
    ("split-subnormal-negative", [-1.0, -TINY, 1.0, -TINY, -TINY], -TINY),
    ("overflow-then-tiny-tail", [1e308, 1e308, -1e308, -1e308, 4 * TINY], TINY),
    ("late-overflow-after-prefix", [8 * TINY] * 32 + [1e308, 1e308, -1e308, -1e308], 7 * TINY),
    ("constant-subnormal-control", [TINY] * 5, TINY),
    ("tie-even-subnormal-control", [TINY, 2 * TINY], 2 * TINY),
    ("half-to-zero-control", [0.0, TINY], 0.0),
    ("late-wide-numerator-control", [0.0] * 32 + [1e308, 1e308], 5.882352941176471e306),
]


@pytest.fixture(scope="module", autouse=True)
def exact_source_guard() -> None:
    root = Path(os.environ["DEEPVIZ_R16_SOURCE"]).resolve()
    expected = os.environ.get("DEEPVIZ_R16_EXPECTED_COMMIT", SOURCE_COMMIT)
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip() == expected
    module = Path(importlib.import_module("deepviz.normalize").__file__).resolve()
    relative = "python/deepviz/src/deepviz/normalize.py"
    assert module == (root / relative).resolve(), "Wrong imported product module"
    assert module.read_bytes() == subprocess.check_output(["git", "-C", str(root), "show", f"HEAD:{relative}"])


@pytest.mark.parametrize("stream", [False, True], ids=["records", "one-pass-records"])
@pytest.mark.parametrize("name,values,literal", MEAN_CASES, ids=[case[0] for case in MEAN_CASES])
def test_mean_matches_exact_fraction_rounding(
    name: str, values: list[float], literal: float, stream: bool,
) -> None:
    expected = float(sum(map(Fraction.from_float, values), Fraction()) / len(values))
    assert expected == literal, f"Independent oracle/literal disagree for {name}"
    rows = [{"g": "only", "v": value} for value in values]
    result = normalize(iter(rows) if stream else rows, {
        "kind": "bar", "x": "g", "y": "v", "aggregation": "mean", "max_points": 10,
    })
    assert result.input_count == len(values)
    assert result.strategy == "mean"
    assert result.warnings == []
    json.dumps(result.records, allow_nan=False)
    assert result.records == [{"g": "only", "v": expected}], f"{name}: finite representable mean was rounded away"


@pytest.mark.parametrize("name", ["rows", "records", "items", "results", "data"])
@pytest.mark.parametrize("mapped", [False, True], ids=["named-column", "explicit-y"])
def test_single_scalar_column_preserves_wrapper_like_name(name: str, mapped: bool) -> None:
    spec: dict[str, Any] = {"kind": "table", "aggregation": "none", "max_points": 10}
    if mapped:
        spec["y"] = name
    result = normalize({name: [1, 2]}, spec)
    assert result.input_count == 2
    assert result.warnings == []
    assert result.strategy == "none"
    assert result.records == [{name: 1}, {name: 2}]


@pytest.mark.parametrize("data,spec,expected", [
    ({"rows": [{"v": 1}, {"v": 2}]}, {"y": "v"}, [{"v": 1}, {"v": 2}]),
    ({"rows": [1, 2]}, {"data_path": "rows", "y": "value"}, [{"index": 0, "value": 1}, {"index": 1, "value": 2}]),
    ({"payload": [1, 2]}, {"y": "payload"}, [{"payload": 1}, {"payload": 2}]),
    ({"rows": [1, 2], "quality": [3, 4]}, {"x": "rows", "y": "quality"}, [{"rows": 1, "quality": 3}, {"rows": 2, "quality": 4}]),
    ({"outer": {"payload": [1, 2]}}, {"data_path": "outer", "y": "payload"}, [{"payload": 1}, {"payload": 2}]),
], ids=["record-wrapper", "explicit-scalar-array-path", "custom-scalar-column", "two-explicit-columns", "explicit-column-object-path"])
def test_valid_explicit_paths_and_columns_remain_usable(
    data: dict[str, Any], spec: dict[str, Any], expected: list[dict[str, Any]],
) -> None:
    result = normalize(data, {"kind": "table", "aggregation": "none", "max_points": 10, **spec})
    assert result.records == expected
    assert result.input_count == 2
    assert result.warnings == []
    assert result.strategy == "none"
