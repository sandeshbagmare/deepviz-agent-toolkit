"""Public source-lifetime regressions for the R17 normalizer boundary repair."""
from __future__ import annotations

import io
import json
import math
from collections.abc import Generator
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize


@pytest.mark.parametrize("phase", ["plan", "late-flatten", "selected-path-plan"])
def test_owned_jsonl_unwinds_before_downstream_exception_returns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str,
) -> None:
    path = tmp_path / "owned.jsonl"
    records: list[dict[str, Any]] = [{"label": "a", "note": "b"} for _ in range(40)]
    if phase == "late-flatten":
        records[35] = {"a.b": 1, "a": {"b": 2}}
    if phase == "selected-path-plan":
        records = [{"page": record} for record in records]
    path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
    handles: list[Any] = []
    original = Path.open

    def opened(self: Path, *args: Any, **kwargs: Any) -> Any:
        file = original(self, *args, **kwargs)
        if self == path:
            handles.append(file)
        return file

    monkeypatch.setattr(Path, "open", opened)
    spec: dict[str, Any] = {"kind": "bar", "format": "jsonl", "aggregation": "sum"}
    if phase == "late-flatten":
        spec["aggregation"] = "none"
    elif phase == "selected-path-plan":
        spec["data_path"] = "page"
    message = "collision" if phase == "late-flatten" else "numeric y"
    try:
        with pytest.raises(ValueError, match=message) as caught:
            normalize(path, spec)
        assert caught.traceback is not None
        assert handles and all(file.closed for file in handles), "Owned adapter must unwind even with retained traceback"
        moved = path.with_suffix(".unlocked")
        path.rename(moved)
        assert moved.exists()
    finally:
        for file in handles:
            file.close()


def test_borrowed_generator_is_not_closed_when_planning_raises() -> None:
    closed: list[bool] = []

    def records() -> Generator[dict[str, str], None, None]:
        try:
            for _ in range(40):
                yield {"label": "a", "note": "b"}
        finally:
            closed.append(True)

    source = records()
    try:
        with pytest.raises(ValueError, match="numeric y") as caught:
            normalize(source, {"kind": "bar", "aggregation": "sum"})
        assert caught.traceback is not None
        assert closed == [], "Do not transfer caller generator ownership on downstream failure"
        assert next(source) == {"label": "a", "note": "b"}
    finally:
        source.close()
    assert closed == [True]


_TINY = float.fromhex("0x0.0000000000001p-1022")
_MEAN_CASES = [
    ("split-positive", [1.0, _TINY, -1.0, _TINY, _TINY]),
    ("split-negative", [-1.0, -_TINY, 1.0, -_TINY, -_TINY]),
    ("overflow-tiny-tail", [1e308, 1e308, -1e308, -1e308, 4 * _TINY]),
    ("late-overflow", [8 * _TINY] * 32 + [1e308, 1e308, -1e308, -1e308]),
    ("constant-tiny", [_TINY] * 5),
    ("tie-even", [_TINY, 2 * _TINY]),
    ("positive-half-zero", [0.0, _TINY]),
    ("negative-half-zero", [0.0, -_TINY]),
    ("wide-numerator", [0.0] * 32 + [1e308, 1e308]),
    ("prefix-residual", [1e30, 1.0, -1e30, _TINY, 1e308, 1e308, -1e308, -1e308]),
]


@pytest.mark.parametrize("stream", [False, True], ids=["records", "one-pass"])
@pytest.mark.parametrize("name,values", _MEAN_CASES, ids=[case[0] for case in _MEAN_CASES])
def test_mean_rounds_exact_finite_rational_once(name: str, values: list[float], stream: bool) -> None:
    expected = float(sum(map(Fraction.from_float, values), Fraction()) / len(values))
    rows = [{"g": "only", "v": value} for value in values]
    consumed: list[int] = []

    def records() -> Generator[dict[str, Any], None, None]:
        for row in rows:
            consumed.append(1)
            yield row

    result = normalize(records() if stream else rows, {
        "kind": "bar", "x": "g", "y": "v", "aggregation": "mean", "max_points": 10,
    })
    assert result.input_count == len(values)
    assert result.strategy == "mean" and result.warnings == []
    assert result.records == [{"g": "only", "v": expected}], name
    assert math.copysign(1, result.records[0]["v"]) == math.copysign(1, expected)
    json.dumps(result.records, allow_nan=False)
    assert len(consumed) == (len(values) if stream else 0)


def test_other_mean_uses_all_numeric_contributions_not_boolean_or_null() -> None:
    rows: list[dict[str, Any]] = [{"g": f"g{i}", "v": i} for i in range(9)]
    values: list[Any] = [1e308, 1e308, -1e308, -1e308, 6 * _TINY, True, None, "2"]
    rows += [{"g": f"overflow{i}", "v": value} for i, value in enumerate(values)]
    result = normalize(iter(rows), {"x": "g", "y": "v", "aggregation": "mean", "max_points": 10})
    assert result.input_count == len(rows) and len(result.records) == 10
    assert result.records[:9] == rows[:9]
    assert result.records[-1] == {"g": "__deepviz_other__", "v": _TINY}
    assert any("non-numeric" in message.lower() for message in result.warnings)
    assert any("other" in message for message in result.warnings)


@pytest.mark.parametrize("name", ["rows", "records", "items", "results", "data", "nodes", "edges", "pages"])
@pytest.mark.parametrize("mapped", [False, True], ids=["inferred", "explicit-y"])
@pytest.mark.parametrize("encoded", [False, True], ids=["object", "encoded-json"])
def test_scalar_array_column_keeps_its_name_and_boolean_null_cells(name: str, mapped: bool, encoded: bool) -> None:
    data = {name: [True, None, False]}
    spec: dict[str, Any] = {"kind": "table", "aggregation": "none"}
    if mapped:
        spec["y"] = name
    result = normalize(json.dumps(data) if encoded else data, spec)
    assert result.input_count == 3 and result.strategy == "none" and result.warnings == []
    assert result.records == [{name: True}, {name: None}, {name: False}]


@pytest.mark.parametrize("stream", [False, True], ids=["records", "one-pass"])
def test_scalar_sequence_and_nested_flags_are_not_empty_records(stream: bool) -> None:
    values: list[Any] = [True, None, False, {"flags": [True, None, False]}]
    result = normalize(iter(values) if stream else values, {"kind": "table", "aggregation": "none"})
    assert result.input_count == 4 and result.warnings == []
    assert result.records == [
        {"index": 0, "value": True}, {"index": 1, "value": None}, {"index": 2, "value": False},
        {"flags.0": True, "flags.1": None, "flags.2": False},
    ]


@pytest.mark.parametrize("key", ["nodes", "edges"])
@pytest.mark.parametrize("sibling", [{"version": 7}, {"audit": {"source": "left"}}])
def test_connection_siblings_require_a_path_instead_of_disappearing(key: str, sibling: dict[str, Any]) -> None:
    connection = {key: [{"id": 1}] if key == "nodes" else [{"node": {"id": 1}}]}
    with pytest.raises(ValueError, match=r"(?i)ambiguous.*data_path"):
        normalize(connection | sibling, {"kind": "table", "aggregation": "none"})
    selected = normalize(connection | sibling, {"kind": "table", "aggregation": "none", "data_path": key})
    assert selected.records == [{"id": 1}] and selected.input_count == 1


def test_custom_connection_wrapper_requires_explicit_selection() -> None:
    source = {"payload": {"nodes": [{"id": 1}]}}
    with pytest.raises(ValueError, match=r"(?i)custom.*data_path"):
        normalize(source, {"kind": "table", "aggregation": "none"})
    assert normalize(source, {"kind": "table", "aggregation": "none", "data_path": "payload.nodes"}).records == [{"id": 1}]


@pytest.mark.parametrize("key", ["nodes", "edges"])
def test_known_nested_connection_carrier_preserves_flags_nulls_and_metadata(key: str) -> None:
    node = {"id": 1, "flag": False, "flags": [True, None, False]}
    nodes = [node, None] if key == "nodes" else [{"node": node}, {"node": None}]
    source = {"data": {"users": {key: nodes, "totalCount": 2}}, "errors": [{"message": "partial"}]}
    result = normalize(source, {"kind": "table", "aggregation": "none"})
    assert result.records == [{"id": 1, "flag": False, "flags.0": True, "flags.1": None, "flags.2": False}]
    assert result.input_count == 1
    assert any("errors" in warning for warning in result.warnings)
    assert any("null" in warning.lower() for warning in result.warnings)


def test_named_column_iterators_stay_one_pass_without_materializing_a_probe_prefix() -> None:
    consumed: list[int] = []

    def values() -> Generator[bool | None, None, None]:
        for value in [True, None, False]:
            consumed.append(1)
            yield value

    result = normalize({"flags": values()}, {"kind": "table", "aggregation": "none", "y": "flags"})
    assert result.records == [{"flags": True}, {"flags": None}, {"flags": False}]
    assert result.input_count == len(consumed) == 3 and result.warnings == []


def test_explicit_selected_column_object_keeps_root_boundary() -> None:
    result = normalize({"outer": {"payload": [True, None, False]}}, {
        "kind": "table", "aggregation": "none", "data_path": "outer", "y": "payload",
    })
    assert result.records == [{"payload": True}, {"payload": None}, {"payload": False}]
    assert result.input_count == 3 and result.warnings == []


def test_explicit_selected_record_array_keeps_nested_cells_and_source_order() -> None:
    result = normalize({"outer": [{"flags": [True, None]}, {"flags": [False]}]}, {
        "kind": "table", "aggregation": "none", "data_path": "outer",
    })
    assert result.records == [{"flags.0": True, "flags.1": None}, {"flags.0": False}]
    assert result.input_count == 2 and result.warnings == []


def test_borrowed_second_line_jsonl_parse_failure_keeps_stream_usable() -> None:
    source = io.StringIO('{"v":1}\nnot-json\n')
    try:
        with pytest.raises(ValueError, match="line 2") as caught:
            normalize(source, {"kind": "table", "format": "jsonl", "aggregation": "none"})
        assert caught.traceback is not None
        assert not source.closed
        source.seek(0)
        assert source.readline() == '{"v":1}\n'
    finally:
        source.close()
