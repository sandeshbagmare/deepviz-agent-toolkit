"""Strict baseline REDs; no xfail, source fixes or expectations from payloads."""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
from pathlib import Path

import pytest
from count_contract import (
    BUBBLE_PAIRS,
    COUNT_PAIRS,
    COUNT_RECORDS,
    ENGINES,
    NONE_PAIRS,
    NONE_ROWS,
    ROWS,
    SUM_PAIRS,
    count_spec,
    native_values,
    normalized_count,
)

from deepviz.normalize import normalize
from deepviz.render import render


def test_loaded_modules_match_pinned_source_identity():
    identity_path = os.environ.get("DEEPVIZ_R15_SOURCE_IDENTITY")
    if not identity_path:
        pytest.skip("Set source identity ledger to verify exact 5340 snapshot; semantic tests remain runnable")
    identity = json.loads(Path(identity_path).read_text(encoding="utf-8"))
    expected = {entry["path"]: entry["sha256"] for entry in identity["files"]}
    assert identity["source_sha"] == "5340bc69b7203ad7a9166543062482d819f9b705"
    for name in ("normalize", "models", "engines", "render"):
        module = importlib.import_module("deepviz." + name)
        digest = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        assert digest == expected[f"python/deepviz/src/deepviz/{name}.py"]


@pytest.mark.parametrize("kind", ("bar", "line", "bubble"))
def test_count_retains_exact_groups_and_measure_not_unmapped_weight(kind):
    normalized_count(kind)


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("kind", ("bar", "line", "bubble"))
def test_count_native_measure_equals_literal_multiplicity_not_numeric_color_or_size(engine, kind):
    data, spec = normalized_count(kind)
    expected = BUBBLE_PAIRS if kind == "bubble" else COUNT_PAIRS
    assert native_values(engine, data.records, spec) == expected


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("kind", ("bar", "line"))
@pytest.mark.parametrize("aggregation", ("sum", "none"))
def test_explicit_sum_and_none_bar_line_preserve_caller_measure(engine, kind, aggregation):
    spec = count_spec(kind, aggregation=aggregation, y="measure")
    data = normalize(copy.deepcopy(ROWS if aggregation == "sum" else NONE_ROWS), spec)
    assert data.strategy == aggregation and not data.warnings
    assert native_values(engine, data.records, spec) == (SUM_PAIRS if aggregation == "sum" else NONE_PAIRS)


@pytest.mark.parametrize("engine", ENGINES)
def test_categorical_color_count_is_a_valid_positive_control(engine):
    rows = [{**row, "series": {90: "red", 80: "blue", 70: "green"}[row["series"]]} for row in ROWS]
    spec = count_spec()
    result = normalize(rows, spec)
    assert [row["count"] for row in result.records] == [2, 3, 1]
    assert native_values(engine, result.records, spec) == COUNT_PAIRS


@pytest.mark.parametrize("engine", ENGINES)
def test_explicit_count_y_uses_the_named_output_measure(engine):
    spec = count_spec(y="measure")
    result = normalize(copy.deepcopy(ROWS), spec)
    assert [row["measure"] for row in result.records] == [2, 3, 1]
    assert "count" not in result.records[0]
    assert native_values(engine, result.records, spec) == COUNT_PAIRS


def test_count_cannot_silently_discard_a_mapped_size_field():
    with pytest.raises(ValueError, match="remove the mapped size field"):
        normalize(copy.deepcopy(ROWS), count_spec("bubble", size="weight"))


def test_retained_numeric_color_size_channels_do_not_become_the_count_measure():
    from deepviz.engines import channels

    result, spec = normalized_count("bubble")
    mapped = channels(result.records, spec)
    assert [row["_color"] for row in mapped] == ["90", "80", "70"]
    assert [row["_size"] for row in mapped] == [90, 80, 70]
    assert [row["_y"] for row in mapped] == [2, 3, 1]


@pytest.mark.parametrize("engine", ENGINES)
def test_public_artifact_reports_exact_count_reduction_without_fallback(tmp_path, engine):
    artifact = render(copy.deepcopy(ROWS), count_spec(), engine, tmp_path)
    assert artifact.engine == engine
    assert (artifact.input_count, artifact.output_count, artifact.strategy) == (6, 3, "count")
    manifest_path = next(Path(path) for path in artifact.paths if Path(path).name == "manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chart = manifest["charts"][0]
    assert chart["records"] == COUNT_RECORDS
    assert (chart["input_count"], chart["output_count"], chart["strategy"]) == (6, 3, "count")
    assert chart["requested_kind"] == chart["rendered_kind"] == "bar"
    assert not any("fallback" in warning.lower() for warning in artifact.warnings)
    expected_warning = "HTML requires network access to load its exact-version pinned browser library from jsDelivr."
    assert artifact.warnings == ([expected_warning] if engine in {"echarts", "antv"} else [])
