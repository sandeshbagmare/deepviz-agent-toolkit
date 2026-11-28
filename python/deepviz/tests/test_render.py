"""Renderer acceptance through actual artifacts and native value semantics."""
from __future__ import annotations

import importlib
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import get_args

import pytest
from deepviz.models import ChartKind, ChartSpec

ENGINES = ["matplotlib", "plotly", "vega"]
ROWS = [{"label": "Alpha", "amount": 12}, {"label": "Beta", "amount": 31}]


def module(name):
    assert importlib.util.find_spec(f"deepviz.{name}"), f"Missing renderer: deepviz.{name}"
    return importlib.import_module(f"deepviz.{name}")


def manifest(artifact):
    path = next(Path(p) for p in artifact.paths if p.endswith("manifest.json"))
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("engine", ENGINES)
def test_artifacts_preserve_values_counts_and_engine(engine, tmp_path):
    artifact = module("render").render(ROWS, {"x": "label", "y": "amount"}, engine, tmp_path)
    assert (artifact.engine, artifact.input_count, artifact.output_count) == (engine, 2, 2)
    info = manifest(artifact)
    assert info["charts"][0]["records"] == ROWS
    assert info["charts"][0]["engine"] == engine
    if engine in {"matplotlib", "vega"}:
        svg = next(Path(p) for p in artifact.paths if p.endswith(".svg"))
        assert ET.fromstring(svg.read_text(encoding="utf-8")).get("width") in {"648pt", "900"}
        if engine == "matplotlib":
            png = next(Path(p) for p in artifact.paths if p.endswith(".png"))
            assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    else:
        assert info["native_specs"][0]["data"][0]["y"] == [12, 31]
    html = next(Path(p) for p in artifact.paths if p.endswith(".html")).read_text(encoding="utf-8")
    assert "View chart data" in html and "Alpha" in html


def test_matplotlib_maps_actual_bar_heights_and_explicit_child_theme():
    first = ChartSpec(x="label", y="amount", theme="light")
    second = first.model_copy(update={"theme": "dark"})
    parent = ChartSpec(kind="dashboard", charts=[first, second], theme="dark")
    figure, _ = module("engines").matplotlib_figure([(ROWS, first), (ROWS, second)], parent)
    try:
        figure.canvas.draw()
        assert [patch.get_height() for patch in figure.axes[0].patches] == [12, 31]
        assert figure.axes[0].get_facecolor()[0] > .9
        assert figure.axes[1].get_facecolor()[0] < .2
    finally:
        figure.clear()


@pytest.mark.parametrize("kind", [k for k in get_args(ChartKind) if k != "dashboard"])
@pytest.mark.parametrize("engine", ["matplotlib", "vega"])
def test_static_backends_produce_real_output_for_declared_kinds(kind, engine, tmp_path):
    artifact = module("render").render(ROWS, {"kind": kind, "x": "label", "y": "amount"}, engine, tmp_path)
    svg = next(Path(p) for p in artifact.paths if p.endswith(".svg"))
    assert len(ET.fromstring(svg.read_text(encoding="utf-8"))) > 0
    info = manifest(artifact)["charts"][0]
    if info["rendered_kind"] != kind:
        assert any("fallback" in note for note in info["warnings"])


@pytest.mark.parametrize("engine", ENGINES)
def test_dashboard_replays_once_and_keeps_child_mapping(engine, tmp_path):
    seen = []

    def source():
        for index in range(2):
            seen.append(index)
            yield {"label": str(index), "a": index + 2, "b": index + 10}

    artifact = module("render").render(source(), {"kind": "dashboard", "x": "label", "charts": [
        {"kind": "bar", "y": "a"}, {"kind": "line", "y": "b"},
    ]}, engine, tmp_path)
    charts = manifest(artifact)["charts"]
    assert seen == [0, 1]
    assert [chart["spec"]["y"] for chart in charts] == ["a", "b"]
    assert [row["b"] for row in charts[1]["records"]] == [10, 11]


def test_plotly_native_labels_are_raw_and_missing_values_are_gaps():
    label = '<a href="https://example.invalid">A & B</a>'
    native, warnings, _ = module("engines").native_spec("plotly", [
        {"x": label, "y": 4}, {"x": "empty", "y": None},
    ], ChartSpec(kind="line", x="x", y="y", title=label))
    assert native["data"][0]["x"] == [label, "empty"]
    assert native["data"][0]["y"] == [4, None]
    assert native["layout"]["title"]["text"] == label
    assert any("gaps" in note for note in warnings)


@pytest.mark.parametrize("engine", ENGINES)
def test_render_never_overwrites_existing_files(engine, tmp_path):
    first = module("render").render(ROWS, {"x": "label", "y": "amount"}, engine, tmp_path)
    before = {path: Path(path).read_bytes() for path in first.paths}
    second = module("render").render(ROWS, {"x": "label", "y": "amount"}, engine, tmp_path)
    assert set(first.paths).isdisjoint(second.paths)
    assert before == {path: Path(path).read_bytes() for path in first.paths}


def test_failed_export_removes_its_own_directory(monkeypatch, tmp_path):
    import vl_convert

    def fail(_payload):
        raise RuntimeError("converter failed")

    monkeypatch.setattr(vl_convert, "vegalite_to_svg", fail)
    with pytest.raises(RuntimeError, match="converter failed"):
        module("render").render(ROWS, {"x": "label", "y": "amount"}, "vega", tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("value", [True, "900", 12])
def test_render_revalidates_unchecked_models(value, tmp_path):
    from pydantic import ValidationError

    unsafe = ChartSpec().model_copy(update={"width": value})
    with pytest.raises(ValidationError):
        module("render").render(ROWS, unsafe, "plotly", tmp_path)
    assert list(tmp_path.iterdir()) == []
