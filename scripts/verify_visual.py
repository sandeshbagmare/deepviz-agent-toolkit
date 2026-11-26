"""Fail on raster bar-geometry regressions, ignoring cross-platform font rasterization."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from PIL import Image


def check_bar_pixels(image: NDArray[Any], values: tuple[float, ...]) -> dict[str, Any]:
    """Compare saturated mark pixels with an independently computed rectangular silhouette."""
    assert image.ndim == 3 and image.shape[2] >= 3, "Expected an RGB raster"
    rgb = image[:, :, :3].astype(np.int16)
    # Gray text/grid/background pixels are intentionally outside the regression mask.
    foreground = rgb.max(axis=2) - rgb.min(axis=2) > 45
    columns = np.flatnonzero(foreground.sum(axis=0) >= 4)
    assert columns.size, "No colored chart marks: blank or broken rendering"
    groups = np.split(columns, np.flatnonzero(np.diff(columns) > 1) + 1)
    groups = [group for group in groups if len(group) >= 4]
    assert len(groups) == len(values), f"Expected {len(values)} bars, found {len(groups)}"
    ys, _ = np.nonzero(foreground)
    top, bottom = int(ys.min(axis=0)), int(ys.max(axis=0)) + 1
    assert bottom - top >= 12, "Chart marks are too small to compare"
    expected = np.zeros(foreground.shape, dtype=bool)
    for group, value in zip(groups, values, strict=True):
        height = round((bottom - top) * value / max(values))
        expected[bottom - height:bottom, int(group[0]):int(group[-1]) + 1] = True
    intersection = int(np.count_nonzero(foreground & expected))
    union = int(np.count_nonzero(foreground | expected))
    score = intersection / union
    assert score >= 0.94, f"Bar raster geometry changed: silhouette IoU {score:.4f} < 0.94"
    return {"intersection_over_union": score, "minimum_iou": 0.94, "bars": len(groups)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/visual"))
    args = parser.parse_args()
    os.environ.setdefault("MPLBACKEND", "Agg")
    from deepviz.models import ChartSpec
    from deepviz.render import render

    args.output.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix="raster-", dir=args.output))
    reports = []
    themes: tuple[Literal["light", "dark"], ...] = ("light", "dark")
    for theme in themes:
        for values in ((2.0, 6.0, 4.0), (6.0, 2.0, 4.0)):
            data = [{"category": name, "value": value} for name, value in zip("ABC", values, strict=True)]
            spec = ChartSpec(kind="bar", x="category", y="value", title="Raster contract", theme=theme)
            artifact = render(data, spec, engine="matplotlib", output_dir=run_dir)
            pngs = [Path(path) for path in artifact.paths if Path(path).suffix.lower() == ".png"]
            assert len(pngs) == 1, "Matplotlib must produce exactly one PNG for the visual fixture"
            with Image.open(pngs[0]) as image:
                rgb = np.asarray(image.convert("RGB"))
            assert rgb.shape[:2] == (spec.height, spec.width), "Declared raster dimensions regressed"
            report = check_bar_pixels(rgb, values)
            assert artifact.input_count == artifact.output_count == 3, "Visual fixture lost or duplicated records"
            corner = rgb[0, 0].astype(float).mean()
            assert corner < 100 if theme == "dark" else corner > 200, "Theme background regressed"
            reports.append({"theme": theme, "values": values, "path": str(pngs[0]), **report})
    summary = {
        "source_commit": os.environ.get("GITHUB_SHA", "local-unrecorded"),
        "method": "colored raster silhouette versus analytic bar geometry; text excluded", "cases": reports,
    }
    (run_dir / "report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
