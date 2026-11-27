"""Public package-boundary regressions for the explicitly sealed dependency upgrade."""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import deepviz
import pytest


@pytest.mark.parametrize("stream", [False, True], ids=["records", "one-pass"])
@pytest.mark.parametrize("sign", [1, -1])
def test_package_sum_preserves_residual_before_late_promotion(sign: int, stream: bool) -> None:
    values = [sign * value for value in [1e308, 1e200, 1.0, -1e200, 1e308, -1e308, -1e308]]
    pulled: list[float] = []

    def source() -> Iterator[dict[str, Any]]:
        for value in values:
            pulled.append(value)
            yield {"g": "one", "v": value}

    rows = source() if stream else [{"g": "one", "v": value} for value in values]
    result = deepviz.normalize(rows, {"x": "g", "y": "v", "aggregation": "sum", "max_points": 10})
    assert result.records == [{"g": "one", "v": float(sign)}]
    assert result.input_count == 7 and result.strategy == "sum" and result.warnings == []
    assert pulled == (values if stream else [])


def test_package_scalar_column_is_not_misread_as_graphql_edges() -> None:
    result = deepviz.normalize({"edges": [True, None, False]}, {
        "kind": "table", "y": "edges", "aggregation": "none",
    })
    assert result.records == [{"edges": True}, {"edges": None}, {"edges": False}]
    assert result.input_count == 3 and result.strategy == "none" and result.warnings == []


def test_package_explicit_selected_column_object_gets_its_own_root_boundary() -> None:
    result = deepviz.normalize({"outer": {"payload": [True, None, False]}}, {
        "kind": "table", "data_path": "outer", "y": "payload", "aggregation": "none",
    })
    assert result.records == [{"payload": True}, {"payload": None}, {"payload": False}]
    assert result.input_count == 3 and result.strategy == "none" and result.warnings == []
