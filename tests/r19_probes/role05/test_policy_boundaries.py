"""Novel public header-inclusive boundary and accessible-text preflight checks."""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest

renderer = importlib.import_module("deepviz.render")


class PermittedNativeBoundary(RuntimeError):
    """Safe stop after an allowed preflight, not a production failure."""


def sparse(rows: int, fields: int) -> list[dict[str, int]]:
    records = [{f"c{i % fields}": i} for i in range(rows)]
    for i in range(rows, fields):
        records[0][f"c{i}"] = i
    assert len(set().union(*(row.keys() for row in records))) == fields
    return records


@pytest.mark.parametrize("rows,fields,panels,expected_cells,allowed", [
    (99, 100, 1, 10_000, True),
    (136, 73, 1, 10_001, False),
    (49, 100, 2, 10_000, True),
])
def test_public_header_inclusive_cell_boundary_without_dense_generation(
    rows: int, fields: int, panels: int, expected_cells: int, allowed: bool,
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    # Expected arithmetic comes from rows/union columns/header, not private constants.
    assert (rows + 1) * fields * panels == expected_cells
    data = sparse(rows, fields)
    table: dict[str, Any] = {"kind": "table", "aggregation": "none"}
    spec = table if panels == 1 else {
        "kind": "dashboard", "aggregation": "none", "charts": [table] * panels,
    }
    calls: list[str] = []

    def stop(*args: Any, **kwargs: Any) -> Any:
        calls.append("native")
        raise PermittedNativeBoundary("Allowed table reached test-only safe stop")

    monkeypatch.setattr(renderer, "native_spec", stop)
    output = tmp_path / "not-created"
    if allowed:
        with pytest.raises(PermittedNativeBoundary):
            renderer.render(data, spec, "echarts", output)
        assert calls == ["native"]
    else:
        with pytest.raises(ValueError, match="cell budget.*headers"):
            renderer.render(data, spec, "echarts", output)
        assert calls == []
    assert not output.exists()


@pytest.mark.parametrize("engine", ["matplotlib", "plotly", "vega", "echarts", "antv"])
def test_public_non_table_accessible_text_budget_precedes_native_and_output(
    engine: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    #32 present4KiB keys,1056 expanded cells: far under10K cells and16MiB input.
    #Declared repeated-column/text allowance alone >16MiB; no inferred exact threshold.
    data = [{f"{i:04d}" + "&" * 4092: i} for i in range(32)]
    assert 32 * 33 == 1056
    assert 32 * 4096 * 33 * 6 > 16 * 1024 * 1024
    calls: list[str] = []

    def stop(*args: Any, **kwargs: Any) -> Any:
        calls.append("renderer")
        raise AssertionError("Accessible byte budget did not precede renderer allocation")

    monkeypatch.setattr(renderer, "native_spec", stop)
    monkeypatch.setattr(renderer, "matplotlib_figure", stop)
    output = tmp_path / "not-created"
    with pytest.raises(ValueError, match="estimated byte budget"):
        renderer.render(data, {"kind": "bar", "aggregation": "none"}, engine, output)
    assert calls == [] and not output.exists()
