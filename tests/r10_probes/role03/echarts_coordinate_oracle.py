"""Independent ECharts coordinate assertions: no production-private helpers or captures.

The caller declares the expected axis from its fixture, never from the result.
This prevents a category-axis regression from redefining its own oracle.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any, Literal

Axis = Literal["value", "category", "time"]


def assert_native_coordinates(
    option: dict[str, Any], rows: list[dict[str, Any]], *,
    kind: Literal["line", "area"], axis: Axis, group: str | None = None,
) -> None:
    """Require exact mapped pairs/group membership/multiplicity and native axis semantics."""
    assert option["xAxis"]["type"] == axis, "x axis changed the declared observation domain"
    assert option["yAxis"]["type"] == "value", "y must remain a quantitative coordinate"
    expected: dict[str, list[tuple[Any, float]]] = defaultdict(list)
    for row in rows:
        name = str(row[group]) if group else "Series"
        expected[name].append((row["x"], float(row["y"])))
    if axis == "category":
        assert all(type(row["x"]) is str for row in rows), "category fixture requires literal labels"
        assert option["xAxis"]["data"] == list(dict.fromkeys(row["x"] for row in rows))
    else:
        assert not option["xAxis"].get("data"), "continuous axes must not use a category domain"
    series = option["series"]
    assert len(series) == len(expected), "missing, duplicate, or invented series"
    assert {item["name"] for item in series} == set(expected), "series labels/group membership changed"
    for item in series:
        assert item["type"] == "line", "line and area require a connected native line series"
        assert ("areaStyle" in item) == (kind == "area"), "requested line/area geometry changed"
        actual = []
        for point in item["data"]:
            value = point["value"] if isinstance(point, dict) else point
            assert isinstance(value, list) and len(value) == 2, "expected exactly two mapped coordinates"
            x, y = value
            if axis == "value":
                assert type(x) in (int, float) and math.isfinite(x), "numeric x was coerced or lost"
            else:
                assert type(x) is str, "literal category/time coordinate changed scalar type"
            assert type(y) in (int, float) and math.isfinite(y), "y must remain a finite number"
            actual.append((x, y))
        assert Counter(actual) == Counter(expected[item["name"]]), (
            "native x/y pairing, group, or duplicate multiplicity changed"
        )


def fixture_rows(domain: Axis, *, grouped: bool = False) -> list[dict[str, Any]]:
    """Small literal fixtures with 1:2 quantitative versus 1:1 categorical x gaps."""
    domains: dict[Axis, list[Any]] = {
        "value": [-2.5, 0.5, 6.5],
        "category": ["1", "4", "10"],
        "time": ["2026-02-01T00:00:00Z", "2026-02-04T00:00:00Z", "2026-02-10T00:00:00Z"],
    }
    xs = domains[domain]
    rows = [{"x": x, "y": y, "cohort": "North"}
            for x, y in zip(xs, [2.0, 8.0, 3.0], strict=True)]
    if grouped:
        rows += [{"x": x, "y": y, "cohort": "South"}
                 for x, y in zip(xs, [9.0, 4.0, 6.0], strict=True)]
    return rows
