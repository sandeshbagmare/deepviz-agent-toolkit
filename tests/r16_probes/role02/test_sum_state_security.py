"""Independent finite public admission/state-lifetime probes, not SUM-value or scale tests."""
from __future__ import annotations

import gc
import importlib
import json
import math
import os
import sys
import tracemalloc
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize

SPEC = {"kind": "table", "x": "g", "y": "v", "aggregation": "sum", "max_points": 1000}


def save(name: str, record: dict[str, Any]) -> None:
    destination = os.environ.get("R16_02_RESULTS")
    if destination:
        with (Path(destination) / f"{name}.json").open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, allow_nan=False)
            stream.write("\n")


@pytest.fixture(scope="session", autouse=True)
def pin_source() -> None:
    root = Path(os.environ["R16_02_SOURCE"]).resolve()
    for name in ("normalize", "models"):
        module = importlib.import_module(f"deepviz.{name}")
        filename = module.__file__
        assert filename is not None
        assert Path(filename).resolve() == root / "python/deepviz/src/deepviz" / f"{name}.py"


def label(index: int, width: int) -> str:
    return f"{index:04d}" + "x" * (width - 4)


def test_promotion_rejects_before_exhausting_a_public_near_budget_stream() -> None:
    """510 large but allowed keys fit as ordinary states; overflow promotion must not fit."""
    consumed = 0

    def rows(tail: float) -> Iterator[dict[str, Any]]:
        nonlocal consumed
        for value in (1e308, tail):
            for index in range(510):
                consumed += 1
                yield {"g": label(index, 32700), "v": value}

    ordinary = normalize(rows(0.0), SPEC)
    assert ordinary.input_count == consumed == 1020
    assert len(ordinary.records) == 510
    assert ordinary.warnings == []
    del ordinary
    consumed = 0
    gc.collect()
    tracemalloc.start()
    try:
        with pytest.raises(ValueError, match="retained.*bytes|bytes.*retained"):
            normalize(rows(1e308), SPEC)
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert 510 < consumed < 1020, "Promotion must be admitted incrementally, not after exhausting input"
    save("python-promotion-admission", {"groups": 510, "key_ascii_bytes": 32700,
         "ordinary_rows": 1020, "overflow_consumed_rows": consumed, "traced_current_bytes": current,
         "traced_peak_bytes": peak, "method": "CPython tracemalloc around rejected public call only; not RSS/benchmark"})
    fresh = normalize([{"g": "fresh", "v": 1}], SPEC)
    assert fresh.input_count == len(fresh.records) == 1
    assert fresh.warnings == []


def test_eviction_other_and_fresh_calls_do_not_keep_a_promoted_state_per_unknown_key() -> None:
    def rows() -> Iterator[dict[str, Any]]:
        for index in range(1000):
            for value in (1e308, 1e308, -1e308, -1e308):
                yield {"g": label(index, 4096), "v": value}

    gc.collect()
    tracemalloc.start()
    try:
        result = normalize(rows(), dict(SPEC, max_points=10))
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result.input_count == 4000
    assert len(result.records) == 10
    assert result.records[-1]["g"].startswith("__deepviz_other__")
    assert len(result.warnings) == 1 and "other bucket" in result.warnings[0]
    assert all(set(row) == {"g", "v"} and math.isfinite(row["v"]) for row in result.records)
    json.dumps({"records": result.records, "input_count": result.input_count, "warnings": result.warnings}, allow_nan=False)
    fresh = normalize([{"g": "fresh", "v": 0}], SPEC)
    assert fresh.input_count == len(fresh.records) == 1 and fresh.warnings == []
    save("python-other-lifetime", {"unique_input_groups": 1000, "rows": 4000, "output_records": 10,
         "traced_current_bytes": current, "traced_peak_bytes": peak, "warnings": result.warnings,
         "method": "CPython tracemalloc public grouped stream; memory observed not a process-heap cap"})


def test_input_integer_repr_guard_stops_before_growing_existing_fallback() -> None:
    limit = sys.get_int_max_str_digits()
    if not 0 < limit <= 10000:
        pytest.skip("Requires finite configured Python decimal repr guard <=10000; never changes the guard")
    consumed = 0

    def rows() -> Iterator[dict[str, Any]]:
        nonlocal consumed
        for index in range(32):
            consumed += 1
            yield {"g": "one", "v": 1e308 if index < 2 else 0.0}
        consumed += 1
        yield {"g": "one", "v": 10 ** (limit + 1)}
        consumed += 1
        yield {"g": "one", "v": 0}

    with pytest.raises(ValueError, match="integer string conversion|Exceeds the limit"):
        normalize(rows(), SPEC)
    assert consumed == 33
    save("python-integer-repr-admission", {"configured_repr_digit_limit": limit, "consumed_rows": consumed,
         "input_integer_decimal_digits": limit + 2, "guard_changed": False,
         "scope": "Public row representation rejection before fallback update; not float-only 2151-bit proof"})
