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
