"""Strict NEW cross-page controls, no existing-test imports or production patches."""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
from graphql_fixtures import CORPUS, RAW, PullPages, late_fault, sibling_pages, success

from deepviz.models import NormalizedData
from deepviz.normalize import normalize

ROOT = Path(__file__).resolve().parents[3]


def assert_result(result: NormalizedData, expected: list[dict[str, Any]], notices: list[str]) -> None:
    assert result.input_count == len(expected), "count must be actual non-null rows, not page/server totals"
    assert result.records == expected, "all supplied pages must preserve order, scalar values and nested fields"
    assert Counter(json.dumps(row, sort_keys=True) for row in result.records) == Counter(
        json.dumps(row, sort_keys=True) for row in expected
    ), "legitimate equal repeated nodes must not be deduplicated or invented"
    assert result.strategy == "none", "these finite controls request no aggregation or sampling"
    lowered = [warning.lower() for warning in result.warnings]
    assert len(lowered) == len(notices)
    for notice in notices:
        matches = [warning for warning in lowered if notice in warning and (notice != "graphql" or "error" in warning)]
        assert len(matches) == 1, f"{notice} loss/error must be disclosed exactly once"
        if notice == "null":
            assert matches[0].startswith("2 ")
        if notice in {"missing", "graphql"}:
            assert matches[0].startswith("1 ")


def invoke(data: Any, spec: dict[str, Any], carrier: str) -> tuple[NormalizedData, PullPages | None]:
    if carrier == "json":
        return normalize(json.dumps(data), dict(spec, format="json")), None
    if carrier == "iterator":
        values = data if isinstance(data, list) else [data]
        source = PullPages(values)
        result = normalize(source, spec)
        assert source.pulled == list(range(len(values))) and source.finished
        return result, source
    return normalize(data, spec), None


@pytest.mark.parametrize("carrier", ["list", "json", "iterator"])
@pytest.mark.parametrize("name", CORPUS["successes"])
def test_empty_intermediate_page_and_repeated_values_are_not_termination_or_identity_keys(name, carrier):
    data, spec, expected, notices = success(name)
    original = copy.deepcopy(data)
    result, _ = invoke(data, spec, carrier)
    assert_result(result, expected, notices)
    assert data == original, "traversal must not mutate caller pages, cursors, errors or node records"


@pytest.mark.parametrize("carrier", ["list", "json", "iterator"])
@pytest.mark.parametrize("selected", [False, True], ids=["auto", "explicit"])
@pytest.mark.parametrize("fault", CORPUS["late_faults"])
def test_invalid_late_page_after_empty_page_is_not_a_successful_prefix(fault, selected, carrier):
    data, spec = late_fault(fault, selected)
    original = copy.deepcopy(data)
    source = PullPages(data, poison_after=3) if carrier == "iterator" else None
    with pytest.raises(ValueError, match="(?i)graphql|edge|node|collision") as caught:
        if source is not None:
            normalize(source, spec)
        elif carrier == "json":
            normalize(json.dumps(data), dict(spec, format="json"))
        else:
            normalize(data, spec)
    assert len(str(caught.value)) <= 512, "error must be concise rather than echo the source dataset"
    if source is not None:
        assert source.pulled == [0, 1, 2], "a failing node must stop before any subsequent page"
    assert data == original


@pytest.mark.parametrize("carrier", ["list", "json", "iterator"])
@pytest.mark.parametrize("reverse", [False, True], ids=["feed-first", "shadow-first"])
def test_late_multiple_connections_require_path_not_an_implicit_semantic_merge(reverse, carrier):
    data, spec = late_fault("node-field-collision", False)
    candidates = [("feed", {"nodes": [{"id": "left"}]}), ("shadow", {"nodes": [{"id": "right"}]})]
    data[-1] = {"data": dict(reversed(candidates) if reverse else candidates)}
    with pytest.raises(ValueError, match="(?i)ambiguous|data_path|multiple"):
        invoke(data, spec, carrier)


@pytest.mark.parametrize("name", CORPUS["known_sibling_variants"])
def test_known_sibling_loss_remains_strictly_rejected_when_only_late_page_has_it(name):
    # DEDUP R10-01 F1, not a new root cause or ticket.
    with pytest.raises(ValueError, match="(?i)ambiguous|data_path"):
        normalize(sibling_pages(name), RAW)


@pytest.mark.parametrize("single_page", [False, True], ids=["direct-records", "single-page"])
def test_minimal_valid_direct_and_single_page_controls(single_page):
    records = [{"id": "repeat", "measure": -3.25}, {"id": "repeat", "measure": -3.25}]
    source = {"data": {"feed": {"nodes": records}}} if single_page else records
    assert_result(normalize(source, RAW), records, [])


@pytest.mark.parametrize("fault", ["error-only-response", "error-only-no-data", "error-only-empty-data"])
def test_direct_error_only_envelope_control_uses_same_policy_as_page_list(fault):
    pages, _ = late_fault(fault, False)
    with pytest.raises(ValueError, match="(?i)graphql.*errors.*data"):
        normalize(pages[-1], RAW)


def test_import_and_fixture_guards_cannot_silently_use_an_installed_or_sibling_normalizer():
    import importlib

    module = importlib.import_module("deepviz.normalize")
    assert Path(module.__file__).resolve() == ROOT / "python/deepviz/src/deepviz/normalize.py"
    assert CORPUS["limits"]["valid_prefix_rows"] == 40
