"""One strict public/native literal-series regression; no production monkeypatch."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import math
import shutil
import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sealed", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    proof = json.loads(args.proof.read_text(encoding="utf-8"))
    source = "3eab699b61850a20e91132e16caf8c589085f9ee"
    assert proof["source"] == source
    assert "deepviz" not in sys.modules
    sys.path.insert(0, str(args.sealed / "python/deepviz/src"))
    from deepviz import ChartSpec, render
    from deepviz.engines import matplotlib_figure
    import matplotlib
    from matplotlib._pylab_helpers import Gcf
    from PIL import Image

    identities = {}
    for name in ["deepviz", "deepviz.models", "deepviz.normalize", "deepviz.engines", "deepviz.render"]:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        relative = path.relative_to(args.sealed.resolve()).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == proof["files"][relative]["sha256"]
        identities[name] = {"path": str(path), "sha256": digest}
    assert Path(matplotlib.get_cachedir()).is_relative_to(args.output.parent.resolve())
    rows = [
        {"quarter": "Q1", "units": 2, "region": "_north"},
        {"quarter": "Q1", "units": 3, "region": "South"},
        {"quarter": "Q2", "units": 4, "region": "_north"},
        {"quarter": "Q2", "units": 6, "region": "South"},
    ]
    original = copy.deepcopy(rows)
    expected_labels = ["_north", "South"]
    spec = ChartSpec(kind="bar", x="quarter", y="units", color="region",
                     aggregation="none", title="Quarterly units", width=640, height=400)
    args.output.mkdir(parents=True, exist_ok=False)
    sentinels = {"chart.png": b"preexisting-user-png", "manifest.json": b"preexisting-user-manifest"}
    for name, content in sentinels.items():
        (args.output / name).write_bytes(content)
    before_managers = Gcf.get_num_fig_managers()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        artifact = render(rows, spec, engine="matplotlib", output_dir=args.output)
        figure, notes = matplotlib_figure([(rows, spec)])
        try:
            figure.canvas.draw()
            axis = figure.axes[0]
            labels = [text.get_text() for text in axis.get_legend().get_texts()]
            container_labels = [item.get_label() for item in axis.containers]
            heights = [float(patch.get_height()) for patch in axis.patches]
            limits = [float(value) for value in (*axis.get_xlim(), *axis.get_ylim())]
            bounds = [list(map(float, patch.get_window_extent().bounds)) for patch in axis.patches]
        finally:
            figure.clear()
    paths = {Path(path).name: Path(path) for path in artifact.paths}
    assert set(paths) == {"chart.png", "chart.svg", "chart.html", "manifest.json"}
    assert len({path.parent for path in paths.values()}) == 1
    assert all(path.parent.parent == args.output.resolve() for path in paths.values())
    manifest = json.loads(paths["manifest.json"].read_text(encoding="utf-8"))
    assert manifest["charts"][0]["records"] == rows == original
    assert (artifact.input_count, artifact.output_count, artifact.strategy) == (4, 4, "none")
    assert not artifact.warnings and not notes and not caught
    assert container_labels == expected_labels
    assert heights == [2, 4, 3, 6]
    assert all(math.isfinite(value) for value in limits)
    assert all(math.isfinite(value) for rectangle in bounds for value in rectangle)
    assert all((args.output / name).read_bytes() == content for name, content in sentinels.items())
    assert Gcf.get_num_fig_managers() == before_managers
    svg = paths["chart.svg"].read_text(encoding="utf-8")
    root = ET.fromstring(svg, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    legend = root.find(".//{http://www.w3.org/2000/svg}g[@id='legend_1']")
    assert legend is not None
    svg_labels = [node.text.strip() for node in legend.iter() if node.tag is ET.Comment and node.text]
    html = paths["chart.html"].read_text(encoding="utf-8")
    assert 'src="chart.svg"' in html and "<script" not in html
    assert "_north" in html and "South" in html
    with Image.open(paths["chart.png"]) as image:
        dimensions = list(image.size)
        assert dimensions == [640, 400]
        image.verify()
    for name, path in paths.items():
        shutil.copyfile(path, args.evidence / ("literal-legend-" + name))
    result = {"source": source, "module_identities": identities,
              "matplotlib_version": matplotlib.__version__, "cache": matplotlib.get_cachedir(),
              "case": "four literal rows, grouped public bar plus exact same native artists",
              "expected_legend_labels": expected_labels, "actual_native_legend_labels": labels,
              "actual_public_svg_legend_labels": svg_labels, "native_container_labels": container_labels,
              "native_heights": heights, "finite_limits": limits, "finite_rectangle_bounds": bounds,
              "records_counts_strategy_input_unchanged": True, "public_artifact_warnings": artifact.warnings,
              "python_warnings": [str(w.message) for w in caught], "unrelated_root_sentinels_preserved": True,
              "figure_manager_count_unchanged": True, "png_dimensions": dimensions,
              "artifact_paths": {name: str(path) for name, path in paths.items()},
              "artifact_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()},
              "old_tests_or_production_modified": False, "strict_cases": 1, "skips": 0}
    args.result.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    assert {"native": labels, "public_svg": svg_labels} == {
        "native": expected_labels, "public_svg": expected_labels,
    }, "Every literal series must remain identifiable in the native and public SVG legend"


if __name__ == "__main__":
    main()
