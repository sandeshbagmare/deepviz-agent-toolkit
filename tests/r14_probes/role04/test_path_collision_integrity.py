"""Independent path collision and contribution integrity on published 5340 source."""
from __future__ import annotations

import copy
import json
import unicodedata
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize

CORPUS = json.loads(Path(__file__).with_name("collision-cases.json").read_text(encoding="utf-8"))
BASE: dict[str, Any] = {"kind": "table", "aggregation": "none", "max_points": 100}
AMBIGUITY = r"(?i)(collid|collision|ambig)"


def reverse_objects(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: reverse_objects(item) for key, item in reversed(value.items())}
    if isinstance(value, list):
        return [reverse_objects(item) for item in value]
    return value


def assert_preserved(records: Any, count: int, expected: list[dict[str, Any]]) -> None:
    assert records == expected
    assert count == len(expected)


def test_literal_fixture_really_contains_byte_distinct_confusables() -> None:
    row = next(case for case in CORPUS["preservations"]
               if case["id"] == "byte-distinct-unicode-no-normalization")["expected"][0]
    assert unicodedata.normalize("NFC", "cafe\u0301") == "caf\u00e9"
    assert "cafe\u0301".encode("utf-8") != "caf\u00e9".encode("utf-8")
    assert [row[key] for key in ("caf\u00e9", "cafe\u0301", "a.b", "a\uff0eb", "\u0430.b")] == [
        11, 29, 31, 37, 43,
    ]


@pytest.mark.parametrize("case", CORPUS["collisions"], ids=lambda case: case["id"])
@pytest.mark.parametrize("reverse", [False, True], ids=["original-order", "reversed-order"])
@pytest.mark.parametrize("carrier", ["records", "json", "selected"])
def test_colliding_contributions_reject_before_overwriting(
    case: dict[str, Any], reverse: bool, carrier: str,
) -> None:
    row = reverse_objects(case["row"]) if reverse else copy.deepcopy(case["row"])
    before = copy.deepcopy(row)
    spec = {**BASE, "x": "id", "y": case["field"]}
    data: Any = [row]
    if carrier == "json":
        data, spec = json.dumps(data, ensure_ascii=False), {**spec, "format": "json"}
    elif carrier == "selected":
        data, spec = {"payload": {"rows": data}}, {**spec, "data_path": "payload.rows"}
    with pytest.raises(ValueError, match=AMBIGUITY) as error:
        normalize(data, spec)
    assert len(str(error.value).encode("utf-8")) <= 240
    assert row == before


@pytest.mark.parametrize("case", CORPUS["preservations"], ids=lambda case: case["id"])
@pytest.mark.parametrize("carrier", ["records", "jsonl"])
def test_noncolliding_mapped_values_counts_and_input_remain_exact(case: dict[str, Any], carrier: str) -> None:
    data = copy.deepcopy(case["rows"])
    before = copy.deepcopy(data)
    spec = {**BASE, **case["spec"]}
    source: Any = data
    if carrier == "jsonl":
        source = "\n".join(json.dumps(row, ensure_ascii=False) for row in data)
        spec["format"] = "jsonl"
    result = normalize(source, spec)
    assert_preserved(result.records, result.input_count, case["expected"])
    assert result.warnings == [] and result.strategy == "none"
    assert data == before


@pytest.mark.parametrize("case", CORPUS["columns"], ids=lambda case: case["id"])
def test_column_contributions_are_preserved_or_clearly_rejected(case: dict[str, Any]) -> None:
    data, spec = copy.deepcopy(case["data"]), {**BASE, **case["spec"]}
    before = copy.deepcopy(data)
    if case.get("reject"):
        with pytest.raises(ValueError, match=AMBIGUITY) as error:
            normalize(data, spec)
        assert len(str(error.value).encode("utf-8")) <= 240
    else:
        try:
            result = normalize(data, spec)
        except ValueError as error:
            assert case["ambiguity_allowed"]
            assert "ambig" in str(error).lower() and len(str(error).encode("utf-8")) <= 240
        else:
            assert_preserved(result.records, result.input_count, case["expected"])
            assert result.warnings == [] and result.strategy == "none"
    assert data == before


@pytest.mark.parametrize("case", CORPUS["selected"], ids=lambda case: case["id"])
def test_explicit_data_path_positive_selection_does_not_pick_a_lookalike(case: dict[str, Any]) -> None:
    result = normalize(copy.deepcopy(case["data"]), {**BASE, **case["spec"]})
    assert_preserved(result.records, result.input_count, case["expected"])
    assert result.warnings == [] and result.strategy == "none"


class GuardedRows(Iterator[dict[str, Any]]):
    def __init__(self, case: dict[str, Any], invalid_index: int | None) -> None:
        self.case, self.invalid_index = case, invalid_index
        self.pulled = 0
        self.exhausted = False

    def __next__(self) -> dict[str, Any]:
        index = self.pulled
        if index == 60:
            self.exhausted = True
            raise StopIteration
        assert self.invalid_index is None or index <= self.invalid_index, "Consumed collision tail"
        self.pulled += 1
        if index == self.invalid_index:
            return copy.deepcopy(self.case["row"])
        return {"id": index, self.case["field"]: index + 11}


@pytest.mark.parametrize("case", CORPUS["collisions"], ids=lambda case: case["id"])
@pytest.mark.parametrize("invalid_index", [0, 40])
def test_collision_consumption_stops_on_first_bad_row(case: dict[str, Any], invalid_index: int) -> None:
    source = GuardedRows(case, invalid_index)
    with pytest.raises(ValueError, match=AMBIGUITY):
        normalize(source, {**BASE, "x": "id", "y": case["field"]})
    assert source.pulled == invalid_index + 1 and not source.exhausted


def test_noncolliding_stream_is_not_stopped_at_inference_prefix() -> None:
    case = CORPUS["collisions"][0]
    source = GuardedRows(case, None)
    result = normalize(source, {**BASE, "x": "id", "y": case["field"]})
    assert_preserved(result.records, result.input_count, [{"id": index, "part.leaf": index + 11}
                                                        for index in range(60)])
    assert source.pulled == 60 and source.exhausted
    assert result.warnings == [] and result.strategy == "none"


@pytest.mark.parametrize("corruption", ["last-write-only", "dropped-field", "wrong-count"])
def test_preservation_oracle_rejects_corrupt_success(corruption: str) -> None:
    expected = [{"literal": 11, "nested": 29}]
    records, count = copy.deepcopy(expected), 1
    if corruption == "last-write-only":
        records = [{"literal": 29}]
    elif corruption == "dropped-field":
        records = [{"literal": 11}]
    else:
        count = 2
    with pytest.raises(AssertionError):
        assert_preserved(records, count, expected)
