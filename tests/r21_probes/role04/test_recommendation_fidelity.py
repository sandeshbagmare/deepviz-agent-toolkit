"""Practical bounded public recommendations, with real native value oracles."""
from __future__ import annotations

import copy
import importlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from deepviz import ChartSpec, normalize
from deepviz.engines import matplotlib_figure
from deepviz.tools import ToolSession

TARGET = "7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6"
CASES: list[dict[str, Any]] = [
    {"goal": "comparison", "kind": "bar", "x": "region", "y": "units",
     "rows": [{"region": "Alpha", "units": 7}, {"region": "Beta", "units": 19},
              {"region": "Gamma", "units": 11}]},
    {"goal": "trend", "kind": "line", "x": "date", "y": "load",
     "rows": [{"date": "2026-01-03", "load": 4}, {"date": "2026-01-04", "load": 1},
              {"date": "2026-01-09", "load": 9}]},
    {"goal": "relationship", "kind": "scatter", "x": "distance", "y": "temperature",
     "rows": [{"distance": 1.5, "temperature": 19}, {"distance": 2.5, "temperature": 10},
              {"distance": 5.0, "temperature": 23}]},
    {"goal": "distribution", "kind": "histogram", "x": "duration", "y": None,
     "rows": [{"duration": value} for value in (1, 1, 2, 3, 5, 8)]},
    {"goal": "composition", "kind": "pie", "x": "part", "y": "units",
     "rows": [{"part": "North", "units": 8}, {"part": "South", "units": 5}]},
]


@pytest.fixture(scope="session", autouse=True)
def exact_source_guard() -> None:
    root = Path(os.environ.get("DEEPVIZ_R21_SOURCE_ROOT", Path(__file__).resolve().parents[3])).resolve()
    pin = os.environ.get("DEEPVIZ_R21_TARGET", TARGET)
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip() == pin
    for name in ("__init__", "tools", "recommend", "normalize", "models", "render", "engines"):
        module = importlib.import_module("deepviz" if name == "__init__" else f"deepviz.{name}")
        path = root / "python/deepviz/src/deepviz" / f"{name}.py"
        assert module.__file__ is not None
        assert Path(module.__file__).resolve() == path
        assert path.read_bytes() == subprocess.check_output(
            ["git", "-C", str(root), "show", f"{pin}:python/deepviz/src/deepviz/{name}.py"]
        )


def assert_editable_heuristic(advice: dict[str, Any]) -> None:
    notes = " ".join(advice["warnings"]).lower()
    assert "bounded" in notes and "observed" in notes and "review fields" in notes
    assert advice["rationale"] and "model" not in advice and "confidence" not in advice
    ChartSpec.model_validate(advice["spec"])


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["goal"])
def test_public_handle_recommendation_preserves_real_native_goal_values(case: dict[str, Any], tmp_path: Path) -> None:
    rows = copy.deepcopy(case["rows"])
    before = copy.deepcopy(rows)
    session = ToolSession(tmp_path)
    summary = session.normalize_data(rows)
    advice = session.recommend_chart({"dataset_id": summary["dataset_id"]}, case["goal"])
    assert_editable_heuristic(advice)
    chart = ChartSpec.model_validate(advice["spec"])
    assert (chart.kind, chart.x, chart.y) == (case["kind"], case["x"], case["y"])
    assert advice["engine"] == "matplotlib" and advice["input_count"] == len(rows)
    normalized = normalize(rows, chart)
    assert normalized.records == rows and normalized.input_count == len(rows)
    assert normalized.warnings == [] and normalized.strategy != "sample"
    fig, notes = matplotlib_figure([(normalized.records, chart)])
    try:
        ax = fig.axes[0]
        assert notes == []
        if case["goal"] == "comparison":
            assert [patch.get_height() for patch in ax.patches] == [7, 19, 11]
            assert [text.get_text() for text in ax.get_xticklabels()] == ["Alpha", "Beta", "Gamma"]
        elif case["goal"] == "trend":
            line, = ax.lines
            assert [date.isoformat()[:10] for date in line.get_xdata()] == ["2026-01-03", "2026-01-04", "2026-01-09"]
            assert line.get_ydata().tolist() == [4, 1, 9]
            assert "ordering" in advice["rationale"].lower()
        elif case["goal"] == "relationship":
            assert ax.collections[0].get_offsets().tolist() == [[1.5, 19.0], [2.5, 10.0], [5.0, 23.0]]
            assert "does not establish causality" in advice["rationale"]
        elif case["goal"] == "distribution":
            assert sum(patch.get_height() for patch in ax.patches) == 6
            assert ax.get_ylabel() == "Count"
        else:
            assert [text.get_text() for text in ax.texts] == ["North", "South"]
            assert [(wedge.theta2 - wedge.theta1) / 360 for wedge in ax.patches] == pytest.approx([8 / 13, 5 / 13])
    finally:
        fig.clear()
    assert rows == before and summary["profile"]["profiled_rows"] == len(rows)


@pytest.mark.parametrize("values", [[-4, 9, 2], [0, 0, 0]], ids=["negative-parts", "zero-total"])
def test_unsafe_composition_is_editable_bar_with_original_native_values(values: list[int], tmp_path: Path) -> None:
    rows = [{"part": part, "amount": value} for part, value in zip(("A", "B", "C"), values, strict=True)]
    advice = ToolSession(tmp_path).recommend_chart(rows, "composition")
    assert_editable_heuristic(advice)
    chart = ChartSpec.model_validate(advice["spec"])
    assert chart.kind == "bar" and "positive total" in advice["rationale"]
    normalized = normalize(rows, chart)
    fig, notes = matplotlib_figure([(normalized.records, chart)])
    try:
        assert [patch.get_height() for patch in fig.axes[0].patches] == values
        assert notes == [] and normalized.warnings == []
    finally:
        fig.clear()


@pytest.mark.parametrize("measure", ["absent", "all-null", "boolean"], ids=str)
@pytest.mark.parametrize("goal", ["relationship", "composition"])
def test_no_numeric_measure_never_invents_a_valid_mapping(measure: str, goal: Any, tmp_path: Path) -> None:
    rows: list[dict[str, Any]] = [{"part": "A"}, {"part": "B"}]
    if measure != "absent":
        for index, row in enumerate(rows):
            row["amount"] = None if measure == "all-null" else bool(index)
    session = ToolSession(tmp_path)
    summary = session.normalize_data(rows)
    advice = session.recommend_chart({"dataset_id": summary["dataset_id"]}, goal)
    assert summary["profile"]["numeric_fields"] == []
    assert advice["spec"]["kind"] == "table"
    assert advice["spec"].get("x") is None and advice["spec"].get("y") is None
    assert "choose fields explicitly" in advice["rationale"]
    assert_editable_heuristic(advice)


def test_empty_source_stays_a_reviewable_table(tmp_path: Path) -> None:
    advice = ToolSession(tmp_path).recommend_chart([], "distribution")
    assert advice["input_count"] == 0 and advice["spec"]["kind"] == "table"
    assert advice["spec"].get("y") is None
    assert_editable_heuristic(advice)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf], ids=["nan", "inf", "minus-inf"])
def test_nonfinite_tool_input_rejects_before_advice_cache_or_artifact(value: float, tmp_path: Path) -> None:
    output = tmp_path / "never-rendered"
    session = ToolSession(output)
    with pytest.raises(ValueError, match="finite JSON"):
        session.recommend_chart([{"part": "A", "amount": value}], "composition")
    assert not session.datasets and not output.exists()


@pytest.mark.parametrize("width", [99, 100, 101])
def test_public_profile_exact_field_cap_privacy_and_truncation(width: int, tmp_path: Path) -> None:
    secret = "R21_PRIVATE_SYNTHETIC_CELL_DO_NOT_INCLUDE_43f8"
    row = {f"field_{index:03}": secret for index in range(width)}
    session = ToolSession(tmp_path)
    summary = session.normalize_data([row])
    profile = summary["profile"]
    assert profile["fields"] == [f"field_{index:03}" for index in range(min(width, 100))]
    assert profile["fields_truncated"] is (width > 100)
    assert profile["profiled_rows"] == 1
    advice = session.recommend_chart({"dataset_id": summary["dataset_id"]}, "comparison")
    assert secret not in json.dumps([summary, advice])
    assert "records" not in summary and len(json.dumps([summary, advice])) < 12_000
    assert_editable_heuristic(advice)


def test_public_profile_name_256_is_retained_257_is_signaled_not_rewritten(tmp_path: Path) -> None:
    keep, omit = "n" * 256, "m" * 257
    secret = "R21_PRIVATE_VALUE_NOT_A_FIELD_72a1"
    session = ToolSession(tmp_path)
    summary = session.normalize_data([{keep: secret, omit: secret, "measure": 7}])
    profile = summary["profile"]
    assert profile["fields"] == [keep, "measure"] and profile["fields_truncated"] is True
    assert profile["numeric_fields"] == ["measure"]
    advice = session.recommend_chart({"dataset_id": summary["dataset_id"]}, "comparison")
    assert secret not in json.dumps([summary, advice]) and omit not in json.dumps([summary, advice])
    assert_editable_heuristic(advice)


@pytest.mark.parametrize("ambiguous", ["numeric-id", "mixed-string"], ids=str)
def test_uncertain_semantics_require_editable_review_not_perfect_field_guess(ambiguous: str, tmp_path: Path) -> None:
    if ambiguous == "numeric-id":
        rows: list[dict[str, Any]] = [{"id": 1001, "reading": 4}, {"id": 1002, "reading": 9}]
        goal: Any = "relationship"
    else:
        rows = [{"part": "A", "reading": 4}, {"part": "B", "reading": "9"},
                {"part": "C", "reading": "not-a-measure"}]
        goal = "composition"
    advice = ToolSession(tmp_path).recommend_chart(rows, goal)
    assert_editable_heuristic(advice)
    assert advice["spec"]["kind"] != "pie"
    assert all(field in rows[0] for field in (advice["spec"].get("x"), advice["spec"].get("y")) if field)
    if ambiguous == "numeric-id":
        assert "does not establish causality" in advice["rationale"]


def test_recommended_spec_reaches_real_static_render_unchanged_and_exact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path(os.environ.get("DEEPVIZ_R21_ARTIFACT_ROOT", str(tmp_path))).resolve()
    root.mkdir(parents=True, exist_ok=True)
    marker = root / "caller-owned.txt"
    marker.write_text("keep R21 caller-owned", encoding="utf-8")
    rows = copy.deepcopy(CASES[0]["rows"])
    before = copy.deepcopy(rows)
    session = ToolSession(root)
    advice = session.recommend_chart(rows, "comparison")
    original_spec = copy.deepcopy(advice["spec"])
    module = importlib.import_module("deepviz.render")
    real_figure = module.matplotlib_figure
    observed: dict[str, Any] = {}

    def inspect_actual_figure(*args: Any, **kwargs: Any) -> Any:
        figure, notes = real_figure(*args, **kwargs)
        axis = figure.axes[0]
        observed.update(native_heights=[patch.get_height() for patch in axis.patches],
                        native_labels=[label.get_text() for label in axis.get_xticklabels()],
                        native_x_label=axis.get_xlabel(), native_y_label=axis.get_ylabel(),
                        native_notes=notes)
        return figure, notes

    # Observation-only forwarder returns the untouched real figure used by savefig.
    monkeypatch.setattr(module, "matplotlib_figure", inspect_actual_figure)
    artifact = session.render_chart(advice["engine"], {"dataset_id": advice["dataset_id"]}, advice["spec"])
    assert observed["native_heights"] == [7, 19, 11]
    assert observed["native_labels"] == ["Alpha", "Beta", "Gamma"]
    assert observed["native_x_label"] == "region" and observed["native_y_label"] == "units"
    assert observed["native_notes"] == []
    assert artifact["input_count"] == artifact["output_count"] == 3
    assert artifact["strategy"] == "sum" and artifact["warnings"] == []
    assert advice["spec"] == original_spec and rows == before
    paths = [Path(path) for path in artifact["paths"]]
    manifest = json.loads(next(path for path in paths if path.name == "manifest.json").read_text(encoding="utf-8"))
    chart, = manifest["charts"]
    assert chart["records"] == before and chart["input_count"] == chart["output_count"] == 3
    assert chart["requested_kind"] == chart["rendered_kind"] == "bar" and chart["warnings"] == []
    assert marker.read_text(encoding="utf-8") == "keep R21 caller-owned"
    assert all(path.resolve().is_relative_to(root) for path in paths)
    png = next(path for path in paths if path.suffix == ".png")
    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    (root / "render-observation.json").write_text(json.dumps({
        "advice": advice, "artifact": artifact, "native": observed, "fixture": before,
        "manifest_matches_exact_fixture": True, "input_and_recommended_spec_unchanged": True,
        "caller_file_preserved": True, "actual_png": str(png),
        "visual_inspection": "Pending actual image opening; file existence is not visual acceptance",
    }, indent=2), encoding="utf-8")
