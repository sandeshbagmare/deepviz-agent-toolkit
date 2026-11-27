"""Bounded independent literals, no producer helpers, model-computed expectations or cap edits."""
from __future__ import annotations

import copy
import io
import json
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize


class OnePassRows:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.iterations = 0
        self.pulled: list[int] = []

    def __iter__(self) -> Iterator[dict[str, Any]]:
        self.iterations += 1
        assert self.iterations == 1, "Do not consume caller source twice"
        for index, row in enumerate(self.rows):
            self.pulled.append(index)
            yield row


def test_selected_root_keeps_two_named_scalar_columns_and_false_null() -> None:
    data = {"outer": {"rows": [True, None, False], "quality": [9, 8, 7]}}
    pristine = copy.deepcopy(data)
    result = normalize(data, {"kind": "table", "aggregation": "none", "data_path": "outer"})
    assert result.records == [{"rows": True, "quality": 9}, {"rows": None, "quality": 8},
                              {"rows": False, "quality": 7}]
    assert result.input_count == 3 and result.strategy == "none" and result.warnings == []
    assert data == pristine


def test_float_promotion_after_literal_integer_prefix_is_one_pass() -> None:
    rows: list[dict[str, Any]] = [{"g": "a", "v": 1} for _ in range(32)]
    rows += [{"g": "a", "v": value} for value in (1e200, 0.25, -1e200)]
    pristine = copy.deepcopy(rows)
    source = OnePassRows(rows)
    result = normalize(source, {"x": "g", "y": "v", "aggregation": "sum"})
    assert result.records == [{"g": "a", "v": 32.25}]
    assert result.input_count == 35 and source.pulled == list(range(35)) and source.iterations == 1
    assert result.strategy == "sum" and result.warnings == [] and rows == pristine


def test_one_pass_count_keeps_all_other_bucket_observations() -> None:
    rows = [{"g": f"g{i}", "v": None} for i in range(11)] + [{"g": "g10", "v": None}]
    source = OnePassRows(rows)
    result = normalize(source, {"x": "g", "y": "v", "aggregation": "count", "max_points": 10})
    expected = [{"g": f"g{i}", "v": 1} for i in range(9)] + [{"g": "__deepviz_other__", "v": 3}]
    assert result.records == expected and result.input_count == 12 and result.strategy == "count"
    assert source.iterations == 1 and source.pulled == list(range(12))
    assert len(result.warnings) == 1 and "first 9 groups" in result.warnings[0] and "other" in result.warnings[0]


@pytest.mark.parametrize("owned", [True, False], ids=["owned-path", "borrowed-stream"])
def test_selected_late_collision_retained_traceback_closes_only_owned_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, record_property: Any, owned: bool,
) -> None:
    path = tmp_path / "selected-late.jsonl"
    rows: list[dict[str, Any]] = [{"selected": {"g": "safe", "v": 1}} for _ in range(45)]
    rows[41] = {"selected": {"g": "bad", "v": 2, "nested.key": 1, "nested": {"key": 2}}}
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    resources: list[io.TextIOBase] = []
    original = Path.open

    def opened(self: Path, *args: Any, **kwargs: Any) -> Any:
        handle = original(self, *args, **kwargs)
        if self == path:
            resources.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", opened)
    source: Any = path if owned else path.open("r", encoding="utf-8")
    try:
        with pytest.raises(ValueError, match="Flattened field collision") as caught:
            normalize(source, {"format": "jsonl", "data_path": "selected", "x": "g", "y": "v",
                               "aggregation": "sum"})
        assert caught.traceback is not None
        frames: list[str] = []
        stage: dict[str, int] = {}
        traceback = caught.value.__traceback__
        while traceback is not None:
            frame = traceback.tb_frame
            if frame.f_globals.get("__name__") == "deepviz.normalize":
                frames.append(frame.f_code.co_name)
                if frame.f_code.co_name == "normalize":
                    stage = {"prefix": len(frame.f_locals["prefix"]), "input_count": frame.f_locals["input_count"]}
            traceback = traceback.tb_next
        assert stage == {"prefix": 32, "input_count": 41} and "_flatten" in frames
        assert resources and all(handle.closed is owned for handle in resources)
        record_property("traceback_retained_stage", json.dumps(stage))
        record_property("closed_before_test_cleanup", json.dumps([handle.closed for handle in resources]))
        if owned:
            moved = path.with_suffix(".unlocked")
            path.rename(moved)
            moved.rename(path)
        else:
            source.seek(0)
            assert json.loads(source.readline()) == {"selected": {"g": "safe", "v": 1}}
    finally:
        for handle in resources:
            handle.close()


def test_two_group_field_budget_stops_borrowed_generator_without_taking_ownership(record_property: Any) -> None:
    consumed: list[int] = []
    closed: list[bool] = []

    def rows() -> Generator[dict[str, Any], None, None]:
        try:
            for index in range(140):
                consumed.append(index)
                yield {"g": "a" * 65516 + f"{index:04d}", "c": "b" * 65520, "v": None}
        finally:
            closed.append(True)

    source = rows()
    try:
        with pytest.raises(ValueError, match="Normalized retained data exceeds 16777216 bytes") as caught:
            normalize(source, {"x": "g", "color": "c", "y": "v", "aggregation": "count", "max_points": 512})
        assert caught.traceback is not None and consumed == list(range(128)) and closed == []
        # Each literal group payload is131064 bytes; 128*131193 accounting exceeds16MiB,127doesnot.
        record_property("pulled_before_guard", 128)
        record_property("borrowed_closed_before_caller_cleanup", False)
        future = next(source)
        assert future["g"].endswith("0128") and future["v"] is None
        assert len(consumed) == 129 and closed == []
    finally:
        source.close()
    assert closed == [True]


@pytest.mark.parametrize("digits,aggregation", [(4000, "sum"), (1000, "mean")], ids=["large-int-sum", "smaller-int-mean"])
def test_large_integer_positive_controls_do_not_require_digit_limit_changes(digits: int, aggregation: str) -> None:
    large = 10**digits
    rows = [{"g": "only", "v": large}, {"g": "only", "v": -large}]
    pristine = json.dumps(rows)
    assert len(pristine) < 16384
    source = OnePassRows(rows)
    result = normalize(source, {"x": "g", "y": "v", "aggregation": aggregation, "max_points": 10})
    assert result.records == [{"g": "only", "v": 0}]
    assert result.input_count == 2 and source.pulled == [0, 1] and source.iterations == 1
    assert result.strategy == aggregation and result.warnings == [] and json.dumps(rows) == pristine


def test_one_pass_business_errors_field_is_literal_data_not_a_transport_failure() -> None:
    rows = [{"g": "x", "v": 2, "errors": ["business-code"]}]
    source = OnePassRows(rows)
    result = normalize(source, {"kind": "table", "aggregation": "none"})
    assert result.records == [{"g": "x", "v": 2, "errors.0": "business-code"}]
    assert result.input_count == 1 and result.strategy == "none" and result.warnings == []
    assert source.iterations == 1 and source.pulled == [0]
