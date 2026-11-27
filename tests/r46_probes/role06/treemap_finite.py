"""One NEW strict finite-treemap gap and ordinary control; no old matrix replay."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    sha = "3eab699b61850a20e91132e16caf8c589085f9ee"

    def git(*argv: str) -> bytes:
        return subprocess.run(["git", "-C", str(source), *argv], capture_output=True, check=True).stdout

    assert git("rev-parse", "HEAD").decode().strip() == sha
    assert git("status", "--porcelain") == b""
    files = ["__init__.py", "models.py", "normalize.py", "engines.py", "render.py"]

    def raw_proof() -> list[dict]:
        results = []
        for name in files:
            relative = "python/deepviz/src/deepviz/" + name
            raw = (source / relative).read_bytes()
            blob = git("show", sha + ":" + relative)
            assert raw == blob
            results.append({"file": relative, "Git_raw_sha256": hashlib.sha256(raw).hexdigest()})
        return results

    before = raw_proof()
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(source / "python/deepviz/src"))
    sys.path.append(str(args.site.resolve()))
    origins = []
    for name in ("deepviz", "deepviz.models", "deepviz.normalize", "deepviz.engines", "deepviz.render"):
        module = importlib.import_module(name)
        assert module.__file__ is not None
        file = Path(module.__file__).resolve()
        assert file.is_relative_to(source / "python/deepviz/src/deepviz")
        origins.append({"module": name, "actual_file": str(file)})
    import vl_convert as vlc
    from deepviz import render

    proof = {"source_SHA": sha, "python": sys.version, "isolated": sys.flags.isolated,
             "no_site": sys.flags.no_site, "raw_before_import": before, "actual_origins": origins,
             "probe_sha256_before_consumer": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "vl_convert_version": vlc.__version__, "vl_convert_origin": str(Path(vlc.__file__).resolve())}
    assert Path(vlc.__file__).resolve().is_relative_to(args.site.resolve())
    (output / "before-consumer.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
    results = []
    try:
        for label, weight in (("ordinary-control", 1.0), ("finite-large-counterexample", 1e308)):
            rows = [{"category": "A", "value": weight}, {"category": "B", "value": weight}]
            saved = json.dumps(rows)
            spec = {"kind": "treemap", "x": "category", "y": "value", "aggregation": "none",
                    "width": 640, "height": 400, "title": "R46 equal finite weights " + label}
            artifact = render(rows, spec, "vega", output / label)
            manifest_path = next(Path(name) for name in artifact.paths if name.endswith("manifest.json"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload = manifest["native_specs"][0]
            data = payload["data"]["values"]
            expected = [[0.0, 0.5], [0.5, 1.0]]
            actual = [[row["_left"], row["_right"]] for row in data]
            svg = next(Path(name) for name in artifact.paths if name.endswith(".svg"))
            png = output / (label + ".png")
            png.write_bytes(vlc.svg_to_png(svg.read_text(encoding="utf-8")))
            assert artifact.input_count == artifact.output_count == 2
            assert manifest["charts"][0]["records"] == rows and saved == json.dumps(rows)
            assert [row["_y"] for row in data] == [weight, weight]
            result = {"id": label, "rows": rows, "input_count": artifact.input_count,
                      "output_count": artifact.output_count, "original_values_and_rows_preserved": True,
                      "literal_expected_edges": expected, "actual_native_edges": actual,
                      "literal_expected_widths": [0.5, 0.5],
                      "actual_native_widths": [right - left for left, right in actual],
                      "strict_literal_geometry_pass": actual == expected,
                      "warnings": artifact.warnings, "public_artifact_paths": artifact.paths,
                      "actual_public_svg_sha256": hashlib.sha256(svg.read_bytes()).hexdigest(),
                      "actual_rasterized_svg_png": str(png), "PNG_sha256": hashlib.sha256(png.read_bytes()).hexdigest()}
            results.append(result)
            (output / "result.json").write_text(json.dumps({"proof": proof, "results": results}, indent=2), encoding="utf-8")
            if label == "ordinary-control":
                assert result["strict_literal_geometry_pass"], "Ordinary control failed; stop before new candidate"
        print(json.dumps(results, indent=2))
        assert results[1]["strict_literal_geometry_pass"], (
            "Two equal finite positive weights must each retain half the native treemap width; "
            "successful zero-width geometry silently loses the entire mapped area"
        )
        return 0
    finally:
        proof["raw_after_consumer"] = raw_proof()
        proof["source_clean_after"] = git("status", "--porcelain") == b""
        (output / "after-consumer.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
