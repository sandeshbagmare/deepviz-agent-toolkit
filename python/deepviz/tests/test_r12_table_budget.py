"""Dense tables must be bounded before native/HTML Cartesian allocation."""
from __future__ import annotations

import importlib
import json
from collections import Counter
from pathlib import Path

import pytest

from deepviz import ChartSpec, render
from deepviz.engines import browser_html, matplotlib_figure, native_spec

ENGINES = ["plotly", "vega", "echarts", "antv"]


def _sparse(size: int) -> list[dict]:
    return [{f"f{i}": i} for i in range(size)]


@pytest.mark.parametrize("engine", ENGINES)
def test_sparse_native_table_rejects_missing_cell_expansion(engine: str) -> None:
    # 128 * 129 = 16,512 cells, despite only 128 values in the source.
    with pytest.raises(ValueError, match="Dense table.*cell budget"):
        native_spec(engine, _sparse(128), ChartSpec(kind="table", aggregation="none"))


@pytest.mark.parametrize("kind", ["table", "bar"])
def test_accessible_html_rejects_sparse_grid_even_for_non_table_chart(kind: str) -> None:
    spec = ChartSpec(kind=kind, aggregation="none")
    with pytest.raises(ValueError, match="Dense table.*cell budget"):
        browser_html("echarts", [], [spec], spec,
                     metadata=[{"records": _sparse(128)}], image="chart.svg")


@pytest.mark.parametrize("kind", ["table", "bar"])
def test_public_render_rejects_before_creating_output_directory(kind: str, tmp_path: Path) -> None:
    output = tmp_path / "not-created"
    with pytest.raises(ValueError, match="Dense table.*cell budget"):
        render(_sparse(128), {"kind": kind, "aggregation": "none"}, "echarts", output)
    assert not output.exists(), "Rejected table planning must not leave an output directory"


def test_matplotlib_rejects_before_constructing_a_figure(monkeypatch: pytest.MonkeyPatch) -> None:
    from matplotlib.figure import Figure

    def forbidden_figure(*args: object, **kwargs: object) -> None:
        raise AssertionError("Oversized table reached native figure allocation")

    # This dependency tripwire prevents allocating the very object being bounded.
    monkeypatch.setattr(Figure, "__init__", forbidden_figure)
    with pytest.raises(ValueError, match="Dense table.*cell budget"):
        matplotlib_figure([(_sparse(128), ChartSpec(kind="table", aggregation="none"))])


def test_dashboard_preflights_combined_cells_before_any_native_compilation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    renderer = importlib.import_module("deepviz.render")

    def forbidden_native(*args: object, **kwargs: object) -> None:
        raise AssertionError("Over-budget dashboard reached native allocation")

    monkeypatch.setattr(renderer, "native_spec", forbidden_native)
    spec = {"kind": "dashboard", "aggregation": "none", "charts": [{"kind": "table"}] * 3}
    # Each panel has 4,160 cells; all three together have 12,480.
    with pytest.raises(ValueError, match="Dense table.*cell budget"):
        render(_sparse(64), spec, "echarts", tmp_path / "not-created")
    assert not (tmp_path / "not-created").exists()


@pytest.mark.parametrize("engine", ENGINES)
def test_native_text_expansion_is_budgeted_before_dense_payload(engine: str) -> None:
    rows = [{"payload": "<" * 65_536} for _ in range(64)]
    with pytest.raises(ValueError, match="Dense table.*byte budget"):
        native_spec(engine, rows, ChartSpec(kind="table", aggregation="none"))


def test_html_text_expansion_is_budgeted_before_escaping() -> None:
    spec = ChartSpec(kind="bar", aggregation="none")
    rows = [{"payload": "<" * 65_536} for _ in range(64)]
    with pytest.raises(ValueError, match="Dense table.*byte budget"):
        browser_html("vega", [], [spec], spec, metadata=[{"records": rows}], image="chart.svg")


@pytest.mark.parametrize("engine", ["vega", "antv"])
def test_repeated_field_coordinates_are_included_in_expansion_budget(engine: str) -> None:
    # Native text marks repeat each column name for every row, including missing cells.
    rows = [{f"{i:04d}" + "&" * 4_092: i} for i in range(32)]
    with pytest.raises(ValueError, match="Dense table.*byte budget"):
        native_spec(engine, rows, ChartSpec(kind="table", aggregation="none"))


def test_dashboard_preflights_combined_text_bytes_before_native_compilation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    renderer = importlib.import_module("deepviz.render")

    def forbidden_native(*args: object, **kwargs: object) -> None:
        raise AssertionError("Over-budget text reached native allocation")

    monkeypatch.setattr(renderer, "native_spec", forbidden_native)
    rows = [{"payload": "<" * 65_536} for _ in range(32)]
    spec = {"kind": "dashboard", "aggregation": "none", "charts": [{"kind": "table"}] * 2}
    with pytest.raises(ValueError, match="Dense table.*byte budget"):
        render(rows, spec, "echarts", tmp_path / "not-created")
    assert not (tmp_path / "not-created").exists()


def test_sparse_table_below_budget_preserves_every_missing_and_present_cell() -> None:
    native, _, _ = native_spec("echarts", _sparse(99), ChartSpec(kind="table", aggregation="none"))
    texts = [item["style"]["text"] for item in native["graphic"]]
    assert len(texts) == 9_900  # 99 headers + 99 * 99 body cells.
    assert texts.count("") == 9_702
    assert texts.count("98") == 1
    assert texts.count("f98") == 1


@pytest.mark.parametrize("engine", ENGINES)
def test_small_native_table_preserves_headers_and_values(engine: str) -> None:
    rows = [{"label": "A", "value": 3}, {"label": "B", "value": 7}]
    native, _, kind = native_spec(engine, rows, ChartSpec(kind="table", aggregation="none"))
    if engine == "echarts":
        texts = [item["style"]["text"] for item in native["graphic"]]
    elif engine == "antv":
        texts = [item["_text"] for item in native["data"]]
    elif engine == "vega":
        texts = [item["text"] for item in native["data"]["values"]]
    else:
        trace = native["data"][0]
        texts = trace["header"]["values"] + [value for col in trace["cells"]["values"] for value in col]
    assert kind == "table"
    assert Counter(texts) == Counter(["label", "value", "A", "3", "B", "7"])
    assert rows == [{"label": "A", "value": 3}, {"label": "B", "value": 7}]


def test_small_public_table_keeps_counts_records_and_caller_files(tmp_path: Path) -> None:
    sentinel = tmp_path / "caller.txt"
    sentinel.write_text("keep", encoding="utf-8")
    rows = [{"label": "A", "value": 3}, {"label": "B", "value": 7}]
    artifact = render(rows, {"kind": "table", "aggregation": "none"}, "echarts", tmp_path)
    manifest = json.loads(next(Path(p) for p in artifact.paths if p.endswith("manifest.json")).read_text())
    assert (artifact.input_count, artifact.output_count, artifact.strategy) == (2, 2, "none")
    assert manifest["charts"][0]["records"] == rows
    assert len(manifest["native_specs"][0]["graphic"]) == 6
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_small_static_companion_table_keeps_literal_escaped_text() -> None:
    spec = ChartSpec(kind="bar", title="Literal table", aggregation="none")
    page = browser_html("vega", [], [spec], spec,
                        metadata=[{"records": [{"<field>": '<a href="https://example.invalid">A</a>'}]}],
                        image="chart.svg")
    assert '<th scope="col">&lt;field&gt;</th>' in page
    assert "&lt;a href=&quot;https://example.invalid&quot;&gt;A&lt;/a&gt;" in page
    assert "<a href=" not in page
