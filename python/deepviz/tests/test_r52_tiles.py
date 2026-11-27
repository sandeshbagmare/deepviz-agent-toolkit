"""R52 strict finite-weight treemap regressions; expectations are literal."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from deepviz import engines
from deepviz.engines import _tiles, native_spec
from deepviz.models import ChartSpec
from deepviz.render import render


def test_r52_imports_exact_product_worktree() -> None:
    expected = Path(__file__).resolve().parents[3] / "python" / "deepviz" / "src" / "deepviz" / "engines.py"
    assert Path(engines.__file__).resolve() == expected


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([1, 1], [[0, 0.5], [0.5, 1]]),
        ([1e308, 1e308], [[0, 0.5], [0.5, 1]]),
        ([1e308, 5e307], [[0, 2 / 3], [2 / 3, 1]]),
        ([1.5e308, 7.5e307], [[0, 2 / 3], [2 / 3, 1]]),
        ([0, 0], [[0, 0.5], [0.5, 1]]),
        ([0, 1], [[0, 0], [0, 1]]),
        ([-2, 2], [[0, 0], [0, 1]]),
    ],
)
def test_treemap_tiles_have_literal_finite_proportional_edges(values: list[float], expected: list[list[float]]) -> None:
    records = [{"_x": label, "_y": value} for label, value in zip(("A", "B"), values, strict=True)]
    original = [dict(row) for row in records]

    tiles = _tiles(records)
    edges = [[tile["_left"], tile["_right"]] for tile in tiles]

    assert [(tile["_x"], tile["_y"]) for tile in tiles] == [("A", values[0]), ("B", values[1])]
    assert all(math.isfinite(edge) for pair in edges for edge in pair)
    for actual, literal in zip(edges, expected, strict=True):
        assert actual == pytest.approx(literal)
    actual_widths = [right - left for left, right in edges]
    expected_widths = [right - left for left, right in expected]
    assert actual_widths == pytest.approx(expected_widths)
    assert records == original


@pytest.mark.parametrize("engine", ["vega", "echarts"])
def test_finite_large_native_treemap_payload_preserves_values_and_serializes(engine: str) -> None:
    records = [{"category": "A", "value": 1e308}, {"category": "B", "value": 1e308}]
    spec = ChartSpec(kind="treemap", x="category", y="value", aggregation="none")

    native, _, rendered_kind = native_spec(engine, records, spec)

    assert rendered_kind == "treemap"
    if engine == "vega":
        geometry = native["data"]["values"]
        assert [(row["_x"], row["_y"]) for row in geometry] == [("A", 1e308), ("B", 1e308)]
        edges = [[row["_left"], row["_right"]] for row in geometry]
        assert edges == [[0, 0.5], [0.5, 1]]
    else:
        values = native["series"][0]["data"]
        assert values == [{"name": "A", "value": 1e308}, {"name": "B", "value": 1e308}]

    json.dumps(native, allow_nan=False)


@pytest.mark.parametrize("engine", ["vega", "echarts"])
def test_negative_treemap_weight_remains_visible_as_disclosed_zero(engine: str) -> None:
    records = [{"category": "A", "value": -2}, {"category": "B", "value": 2}]
    spec = ChartSpec(kind="treemap", x="category", y="value", aggregation="none")

    native, warnings, rendered_kind = native_spec(engine, records, spec)

    assert rendered_kind == "treemap"
    assert any("negative weights as zero" in warning for warning in warnings)
    geometry = native["series"][0]["data"] if engine == "echarts" else native["data"]["values"]
    field = "value" if engine == "echarts" else "_y"
    assert [row[field] for row in geometry] == [0, 2]
    assert records == [{"category": "A", "value": -2}, {"category": "B", "value": 2}]


@pytest.mark.parametrize("engine", ["vega", "echarts"])
def test_missing_treemap_weight_has_disclosure_and_truthful_retained_count(
    engine: str, tmp_path: Path,
) -> None:
    rows = [{"category": "A", "value": 1}, {"category": "missing", "value": None}]

    artifact = render(rows, {"kind": "treemap", "x": "category", "y": "value", "aggregation": "none"},
                      engine=engine, output_dir=tmp_path)
    manifest_path, = [path for path in artifact.paths if path.endswith("manifest.json")]
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

    # Output count is the retained normalized-record count, not the painted-mark count.
    assert (artifact.input_count, artifact.output_count) == (2, 2)
    assert manifest["charts"][0]["records"] == rows
    native, = manifest["native_specs"]
    geometry = native["series"][0]["data"] if engine == "echarts" else native["data"]["values"]
    assert len(geometry) == 1
    assert any("missing/non-numeric y observations omitted" in warning for warning in artifact.warnings)


def test_public_vega_treemap_keeps_half_widths_and_original_counts_for_large_finite_weights(
    tmp_path: Path,
) -> None:
    rows = [{"category": "A", "value": 1e308}, {"category": "B", "value": 1e308}]

    artifact = render(rows, {"kind": "treemap", "x": "category", "y": "value", "aggregation": "none"},
                      engine="vega", output_dir=tmp_path)
    manifest_path, = [path for path in artifact.paths if path.endswith("manifest.json")]
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

    assert (artifact.input_count, artifact.output_count) == (2, 2)
    assert manifest["charts"][0]["records"] == rows
    assert artifact.warnings == [
        "Flat-record hierarchy: each x value is a first-level child; no parent hierarchy is inferred."
    ]
    native, = manifest["native_specs"]
    assert [row["_y"] for row in native["data"]["values"]] == [1e308, 1e308]
    assert [[row["_left"], row["_right"]] for row in native["data"]["values"]] == [[0, .5], [.5, 1]]
