"""Literal AntV boundary fixtures; no payload overrides or production helpers."""

from __future__ import annotations

from typing import Any


def cases() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for kind in ("pie", "sunburst", "treemap", "gauge"):
        rows = [{"category": "Alpha", "value": 12}, {"category": "Beta", "value": 31},
                {"category": "Gamma", "value": 7}]
        expected = [["Alpha", 12], ["Beta", 31], ["Gamma", 7]]
        if kind == "gauge":
            rows = [{"category": "Load", "value": 37}]
            expected = [["Value", 37], ["Remaining", 63]]
        result.append({"id": kind, "mode": "category", "rows": rows, "expected": expected,
                       "spec": {"kind": kind, "x": "category", "y": "value"}})
    for label, values in (("negative", [-7, -2]), ("positive", [2, 7]), ("signed", [-7, 2]),
                          ("constant", [1, 1]), ("zero", [0, 0])):
        result.append({"id": "heatmap-" + label, "mode": "heatmap", "expected": values,
                       "rows": [{"day": "Mon", "slot": "AM", "heat": values[0]},
                                {"day": "Tue", "slot": "PM", "heat": values[1]}],
                       "spec": {"kind": "heatmap", "x": "day", "y": "slot", "color": "heat"}})
    for kind in ("line", "scatter"):
        result.append({"id": kind, "mode": "fixed", "expected": [[1, 2], [2, 8], [4, 5]],
                       "rows": [{"x": 1, "y": 2}, {"x": 2, "y": 8}, {"x": 4, "y": 5}],
                       "spec": {"kind": kind, "x": "x", "y": "y"}})
    for fixture in result:
        fixture["spec"].update(aggregation="none", width=900, height=480,
                               title="R18 AntV " + fixture["id"])
    return result
