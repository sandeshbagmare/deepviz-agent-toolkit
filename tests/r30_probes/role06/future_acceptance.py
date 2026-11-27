"""FUTURE first-render acceptance recipe; NOT EXECUTED during R30 preparation.

Requires an actually frozen/merged, dependency-complete Matplotlib-only bar/line
release head supplied by R04, its real built/installed wheel, and source proof.
This is deliberately strict: missing capability gates or old COUNT code fail.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import UserDict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    proof = json.loads(args.proof.read_text(encoding="utf-8"))
    assert len(proof["source_sha"]) == 40 and proof["clean_git_source"] is True
    prefix = Path(sys.prefix).resolve()
    assert sys.prefix != sys.base_prefix, "Use the independently installed consumer venv, not editable MAIN"
    origins = {}
    for name in ("deepviz", "deepviz.models", "deepviz.normalize", "deepviz.engines",
                 "deepviz.render", "deepviz.tools", "deepviz.recommend", "deepviz.cli"):
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        assert path.is_relative_to(prefix), f"Wrong installed module origin: {name}"
        relative = "deepviz/" + ("__init__.py" if name == "deepviz" else name.split(".")[-1] + ".py")
        digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert digest == proof["module_git_LF_sha256"][relative], f"Installed/source mismatch: {name}"
        origins[name] = {"path": str(path), "git_LF_sha256": digest}

    import deepviz
    from deepviz.engines import channels, matplotlib_figure
    from deepviz.models import ChartSpec
    from deepviz.tools import ToolSession
    from PIL import Image

    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    sentinel = root / "caller-file.txt"
    sentinel.write_text("preserve caller bytes", encoding="utf-8")
    count_rows = ([{"label": "A", "series": 90}] * 2 +
                  [{"label": "B", "series": 80}] * 3 + [{"label": "C", "series": 70}])
    count_spec = {"kind": "bar", "title": "R30 count bars", "x": "label", "color": "series",
                  "aggregation": "count", "width": 640, "height": 400}
    count_records = [{"label": "A", "series": 90, "count": 2},
                     {"label": "B", "series": 80, "count": 3},
                     {"label": "C", "series": 70, "count": 1}]
    line_rows = [{"x": -3, "value": -2}, {"x": 0, "value": 0}, {"x": 6, "value": 4}]
    line_spec = {"kind": "line", "title": "R30 numeric line", "x": "x", "y": "value",
                 "aggregation": "none", "width": 640, "height": 400}
    cases = [("count-bar", count_rows, count_spec, count_records, 6, "count"),
             ("numeric-line", line_rows, line_spec, line_rows, 3, "none")]
    observed = []

    def check_artifact(result: dict, records: list, input_count: int, strategy: str, title: str) -> None:
        assert result["engine"] == "matplotlib" and result["mime_type"] == "image/png"
        assert (result["input_count"], result["output_count"], result["strategy"]) == (input_count, 3, strategy)
        assert result["warnings"] == []
        paths = [Path(value).resolve(strict=True) for value in result["paths"]]
        assert len(paths) == 4 and len({path.parent for path in paths}) == 1
        assert all(path.is_relative_to(root) for path in paths)
        files = {path.name: path for path in paths}
        assert set(files) == {"chart.png", "chart.svg", "chart.html", "manifest.json"}
        with Image.open(files["chart.png"]) as image:
            image.load()
            assert image.size == (640, 400) and image.format == "PNG"
        svg = ET.fromstring(files["chart.svg"].read_text(encoding="utf-8"))
        # Matplotlib SVG dimensions are points (72/in), PNG dimensions are pixels (100 dpi).
        assert math.isclose(float(svg.attrib["width"].removesuffix("pt")), 460.8)
        assert math.isclose(float(svg.attrib["height"].removesuffix("pt")), 288)
        for element in svg.iter():
            for key in ("d", "points", "x", "y", "cx", "cy", "width", "height", "transform"):
                assert not any(word in element.get(key, "") for word in ("NaN", "Infinity", "nan", "inf"))
        html = files["chart.html"].read_text(encoding="utf-8")
        assert title in html and '<img src="chart.svg"' in html and "<script" not in html
        manifest = json.loads(files["manifest.json"].read_text(encoding="utf-8"))
        assert manifest["engine"] == "matplotlib" and manifest["native_specs"] == []
        assert manifest["accessible_path"] == "chart.html" and manifest["strategy"] == strategy
        chart = manifest["charts"][0]
        assert chart["records"] == records and chart["spec"]["title"] == title
        assert (chart["input_count"], chart["output_count"], chart["strategy"]) == (input_count, 3, strategy)
        assert chart["rendered_kind"] == chart["requested_kind"]
        observed.append({"title": title, "paths": [str(path) for path in paths],
                         "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}})

    for name, rows, spec, records, input_count, strategy in cases:
        normalized = deepviz.normalize(rows, spec)
        assert normalized.records == records and normalized.input_count == input_count
        result = deepviz.render(rows, spec, engine="matplotlib", output_dir=root / "api" / name).to_dict()
        check_artifact(result, records, input_count, strategy, spec["title"])
        fig, warnings = matplotlib_figure([(records, ChartSpec.model_validate(spec))])
        try:
            fig.canvas.draw()
            axis = fig.axes[0]
            assert not warnings and axis.get_title() == spec["title"]
            if name == "count-bar":
                assert [row["_y"] for row in channels(records, ChartSpec.model_validate(spec))] == [2, 3, 1]
                assert [patch.get_height() for patch in axis.patches] == [2, 3, 1]
                assert all(patch.get_y() == 0 for patch in axis.patches)
                assert [label.get_text() for label in axis.get_xticklabels()] == ["A", "B", "C"]
            else:
                assert list(axis.lines[0].get_xdata()) == [-3, 0, 6]
                assert list(axis.lines[0].get_ydata()) == [-2, 0, 4]
                points = axis.transData.transform([[-3, -2], [0, 0], [6, 4]])
                assert math.isclose((points[2][0] - points[1][0]) / (points[1][0] - points[0][0]), 2)
                assert axis.get_ylim()[0] < 0 < axis.get_ylim()[1]
            title = axis.title.get_window_extent(fig.canvas.get_renderer())
            assert 0 <= title.x0 < title.x1 <= fig.bbox.width and title.y1 <= fig.bbox.height
        finally:
            fig.clear()
        data_file, spec_file = root / f"{name}-data.json", root / f"{name}-spec.json"
        data_file.write_text(json.dumps(rows), encoding="utf-8")
        spec_file.write_text(json.dumps(spec), encoding="utf-8")
        command = [sys.executable, "-I", "-m", "deepviz.cli", "render", str(data_file),
                   "--spec", str(spec_file), "--engine", "matplotlib", "--output-dir", str(root / "cli" / name)]
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
        assert completed.returncode == 0, completed.stderr
        check_artifact(json.loads(completed.stdout), records, input_count, strategy, spec["title"])

    def rejects(call) -> None:
        try:
            call()
        except (ValueError, TypeError):
            return
        raise AssertionError("An essential malformed/unsupported request was accepted")

    rejects(lambda: ChartSpec.model_validate(UserDict({"width": "640"})))
    rejects(lambda: ChartSpec.model_validate({"version": True}))
    rejects(lambda: deepviz.render(line_rows, {**line_spec, "callback": "danger()"}, output_dir=root / "bad"))
    rejects(lambda: deepviz.render(line_rows, line_spec, engine="plotly", output_dir=root / "bad"))
    rejects(lambda: deepviz.render(line_rows, {**line_spec, "kind": "pie"}, output_dir=root / "bad"))
    rejects(lambda: deepviz.render([{"x": 1}], line_spec, output_dir=root / "bad"))
    rejects(lambda: deepviz.normalize([{"count": "A"}], {"x": "count", "aggregation": "count"}))
    rejects(lambda: ToolSession(root / "bad")._source('{"records":[],"records":[{"x":1}]}'))
    bad_cli = subprocess.run(
        [sys.executable, "-I", "-m", "deepviz.cli", "render", str(root / "numeric-line-data.json"),
         "--spec", str(root / "numeric-line-spec.json"), "--engine", "plotly", "--output-dir", str(root / "bad-cli")],
        cwd=root, capture_output=True, text=True, check=False,
    )
    assert bad_cli.returncode == 2 and not (root / "bad-cli").exists()
    assert not (root / "bad").exists(), "Admission failures must not allocate outputs"
    assert sentinel.read_text(encoding="utf-8") == "preserve caller bytes"
    summary = {"source_sha": proof["source_sha"], "installed_origins": origins, "artifacts": observed,
               "browser_visual_QA": "NOT PERFORMED BY THIS SCRIPT; open actual PNG/SVG and run separate HTML browser gate",
               "status": "Only claim this result after an actual future invocation"}
    (root / "actual-future-result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
