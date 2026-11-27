"""Finite non-scalar envelope controls; dashboard thresholds are reduced in-process.

Literal production defaults are checked separately. Injected tiny thresholds test
public-path boundary/cleanup behavior, not physical 64/32-MiB stress acceptance.
"""
from __future__ import annotations

import importlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize
from deepviz.models import ChartSpec

render_module = importlib.import_module("deepviz.render")


class Counted(Iterator[dict[str, Any]]):
    def __init__(self, rows: Iterator[dict[str, Any]]):
        self.rows = rows
        self.pulled = 0
        self.exhausted = False

    def __next__(self) -> dict[str, Any]:
        try:
            row = next(self.rows)
        except StopIteration:
            self.exhausted = True
            raise
        self.pulled += 1
        return row


def test_1024_field_stream_retains_bounded_original_wide_rows():
    source = Counted({f"f{column}": index + column for column in range(1024)} for index in range(96))
    result = normalize(source, {"kind": "table", "aggregation": "none", "max_points": 10})
    assert source.pulled == result.input_count == 96 and source.exhausted
    assert len(result.records) == 10 and result.strategy == "sample" and result.warnings
    for row in result.records:
        assert row == {f"f{column}": row["f0"] + column for column in range(1024)}


def test_schema_union_is_bounded_even_when_every_individual_row_is_narrow():
    source = Counted({f"field{index}": index} for index in range(1100))
    with pytest.raises(ValueError, match="schema exceeds 1024 fields"):
        normalize(source, {"kind": "table", "aggregation": "sample", "max_points": 10})
    assert source.pulled == 1025 and not source.exhausted


def test_late_1025_field_row_is_checked_after_sample_reservoir_is_full():
    source = Counted({f"f{column}": index for column in range(1025 if index == 40 else 2)}
                     for index in range(100))
    with pytest.raises(ValueError, match="1024 fields"):
        normalize(source, {"kind": "table", "aggregation": "sample", "max_points": 10})
    assert source.pulled == 41 and not source.exhausted


@pytest.mark.parametrize("aggregation", ["sum", "mean", "count"])
def test_long_key_high_cardinality_merges_every_overflow_contribution(aggregation: str):
    keys = ["__deepviz_other__", *[f"retained-{index}-" + "é" * 400 for index in range(1, 9)]]

    def rows():
        for index, key in enumerate(keys):
            yield {"group": key, "value": index + 10}
        for index in range(4096):
            yield {"group": f"overflow-{index}-" + "界" * 300, "value": index + 1}
        for _ in range(100):
            yield {"group": keys[0], "value": 10}

    source = Counted(rows())
    result = normalize(source, {"kind": "bar", "x": "group", "y": "value",
                                "aggregation": aggregation, "max_points": 10})
    assert result.input_count == source.pulled == 4205 and source.exhausted
    assert len(result.records) == 10 and result.strategy == aggregation
    assert [row["group"] for row in result.records[:9]] == keys
    expected = ([101, *([1] * 8)] if aggregation == "count" else
                [1010 if aggregation == "sum" else 10, *range(11, 19)])
    assert [row["value"] for row in result.records[:9]] == expected
    other = result.records[-1]
    assert other["group"] not in keys and other["group"].startswith("__deepviz_other__")
    assert other["value"] == {"sum": 4096 * 4097 // 2, "mean": 2048.5, "count": 4096}[aggregation]
    assert any("all non-retained groups" in warning for warning in result.warnings)


def test_dashboard_literal_default_budgets_are_not_silently_shrunk():
    assert render_module._MAX_REPLAY_BYTES == 64 * 1024**2
    assert render_module._MAX_REPLAY_ROW_BYTES == 1024**2
    assert render_module._MAX_RENDER_BYTES == 32 * 1024**2


def track_scratch(monkeypatch, tmp_path: Path) -> list[Path]:
    original = render_module.tempfile.TemporaryDirectory
    scratch = []

    def owned_directory(*args, **kwargs):
        kwargs["dir"] = tmp_path
        directory = original(*args, **kwargs)
        scratch.append(Path(directory.name))
        return directory

    monkeypatch.setattr(render_module.tempfile, "TemporaryDirectory", owned_directory)
    return scratch


def dashboard() -> ChartSpec:
    return ChartSpec(kind="dashboard", charts=[ChartSpec(kind="scatter", x="x", y="y"),
                                               ChartSpec(kind="line", x="x", y="y")])


@pytest.mark.parametrize("delta", [0, -1], ids=["exact-accept", "one-byte-reject"])
def test_public_dashboard_replay_exact_cumulative_byte_boundary_and_cleanup(monkeypatch, tmp_path, delta):
    scratch = track_scratch(monkeypatch, tmp_path)
    row = {"x": 1, "y": 2, "padding": "é" * 100}
    total = 6 * (len(json.dumps(row, ensure_ascii=False).encode("utf-8")) + 1)
    monkeypatch.setattr(render_module, "_MAX_REPLAY_BYTES", total + delta)
    source = Counted(dict(row) for _ in range(6))
    output = tmp_path / "outputs"
    if delta < 0:
        with pytest.raises(ValueError, match="source budget"):
            render_module.render(source, dashboard(), engine="echarts", output_dir=output)
        assert source.pulled == 6 and not source.exhausted and not output.exists()
    else:
        artifact = render_module.render(source, dashboard(), engine="echarts", output_dir=output)
        assert artifact.input_count == source.pulled == 6 and source.exhausted
        assert artifact.output_count == 12
        manifest_path = next(Path(path) for path in artifact.paths if Path(path).name == "manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert [chart["input_count"] for chart in manifest["charts"]] == [6, 6]
        assert all(chart["records"] == [row] * 6 for chart in manifest["charts"])
    assert len(scratch) == 1 and all(not path.exists() for path in scratch)


def test_dashboard_replay_row_limit_counts_encoded_utf8_before_output(monkeypatch, tmp_path):
    scratch = track_scratch(monkeypatch, tmp_path)
    monkeypatch.setattr(render_module, "_MAX_REPLAY_ROW_BYTES", 300)
    source = Counted({"x": 1, "y": 2, "padding": "🙂" * 100} for _ in range(20))
    with pytest.raises(ValueError, match="record exceeds 300 bytes"):
        render_module.render(source, dashboard(), engine="echarts", output_dir=tmp_path / "outputs")
    assert source.pulled == 1 and not source.exhausted
    assert all(not path.exists() for path in scratch) and not (tmp_path / "outputs").exists()


def test_payload_budget_exact_cumulative_encoded_boundary(monkeypatch):
    payload = [{"label": "🙂" * 40, "value": 7}]
    size = len(json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8"))
    monkeypatch.setattr(render_module, "_MAX_RENDER_BYTES", size + 17)
    assert render_module._payload_budget(payload, 17) == size + 17
    with pytest.raises(ValueError, match="Combined renderer payload"):
        render_module._payload_budget(payload, 18)


def test_public_dashboard_combined_children_rejected_before_native_serialization(monkeypatch, tmp_path):
    # Each child fits separately; combined retained records/specs do not.
    # Measured retained bytes: child1=1080; both=2157. Reject the second, not native overhead.
    monkeypatch.setattr(render_module, "_MAX_RENDER_BYTES", 2100)
    original_native = render_module.native_spec
    calls = []

    def observe_native(*args, **kwargs):
        calls.append(True)
        return original_native(*args, **kwargs)

    monkeypatch.setattr(render_module, "native_spec", observe_native)
    data = [{"x": index, "y": index + 1, "padding": "x" * 100} for index in range(6)]
    with pytest.raises(ValueError, match="Combined renderer payload"):
        render_module.render(data, dashboard(), engine="echarts", output_dir=tmp_path / "outputs")
    assert calls == [] and not (tmp_path / "outputs").exists()
