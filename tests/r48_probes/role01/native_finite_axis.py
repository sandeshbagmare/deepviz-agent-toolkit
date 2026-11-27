"""One fresh native finite-axis boundary and one ordinary positive control."""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import math
import os
import subprocess
import sys
import time
import traceback
import unittest
import warnings
from pathlib import Path

SOURCE = "3eab699b61850a20e91132e16caf8c589085f9ee"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repository", type=Path, required=True)
parser.add_argument("--snapshot", type=Path, required=True)
parser.add_argument("--dependencies", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
assert not any(n == "deepviz" or n.startswith("deepviz.") for n in sys.modules)
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
cache = output / "owned-cache"
cache.mkdir()
os.environ["MPLCONFIGDIR"] = str(cache)
os.environ["MPLBACKEND"] = "Agg"
os.environ["TEMP"] = os.environ["TMP"] = str(cache)
verified = {}
for name in ("__init__", "models", "normalize", "engines", "render"):
    relative = "python/deepviz/src/deepviz/" + name + ".py"
    raw = (args.snapshot / relative).read_bytes()
    assert raw == subprocess.check_output(["git", "-C", str(args.repository), "show", SOURCE + ":" + relative])
    verified[name] = {"path": str((args.snapshot / relative).resolve()), "sha256": hashlib.sha256(raw).hexdigest()}
sys.path[:0] = [str((args.snapshot / "python/deepviz/src").resolve()), str(args.dependencies.resolve())]
import matplotlib
import numpy
import pydantic
from PIL import Image
from deepviz.models import ChartSpec
from deepviz.render import render
from deepviz.engines import matplotlib_figure
for name, proof in verified.items():
    module = importlib.import_module("deepviz" if name == "__init__" else "deepviz." + name)
    assert Path(module.__file__).resolve() == Path(proof["path"])
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == proof["sha256"]
for module in (matplotlib, numpy, pydantic):
    assert Path(module.__file__).resolve().is_relative_to(args.dependencies.resolve())
proof = {"source": SOURCE, "verified_before_product_import": True, "loaded_modules": verified,
         "isolation": "-B -I -S; explicit snapshot and existing readonly dependencies",
         "Matplotlib": matplotlib.__version__, "NumPy": numpy.__version__, "Pydantic": pydantic.__version__,
         "global_dependency_env_changes": False, "only_child_owned_cache": str(cache)}
(output / "source-before.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
observations = {}
entry_calls = 0

class FiniteNativeAxis(unittest.TestCase):
    def check_case(self, name, ys):
        global entry_calls
        rows = [{"t": 0, "v": ys[0]}, {"t": 1, "v": ys[1]}]
        literal_before = json.dumps(rows, allow_nan=False)
        spec = ChartSpec(kind="line", x="t", y="v", aggregation="none", width=640, height=400,
                         title="Finite values " + name)
        root = output / name
        root.mkdir()
        sentinel = root / "chart.svg"
        sentinel.write_text("caller-owned sentinel", encoding="utf-8")
        observed = observations[name] = {"literal_rows": rows, "expected_public_success": True,
                                        "expected_counts": [2, 2], "expected_strategy": "none"}
        started = time.perf_counter()
        with warnings.catch_warnings(record=True) as emitted:
            warnings.simplefilter("always")
            try:
                entry_calls += 1
                artifact = render(rows, spec, "matplotlib", root)
                paths = {Path(p).suffix: Path(p) for p in artifact.paths}
                manifest = json.loads(paths[".json"].read_bytes())
                observed.update({"artifact": artifact.to_dict(), "manifest_records": manifest["charts"][0]["records"],
                                 "files": {p.name: {"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths.values()}})
                self.assertEqual((artifact.input_count, artifact.output_count, artifact.strategy), (2, 2, "none"))
                self.assertEqual(manifest["charts"][0]["records"], rows)
                self.assertEqual(set(paths), {".png", ".svg", ".html", ".json"})
                with Image.open(paths[".png"]) as image:
                    image.load()
                    self.assertEqual(image.size, (640, 400))
                entry_calls += 1
                fig, native_warnings = matplotlib_figure([(rows, spec)])
                try:
                    fig.canvas.draw()
                    axis = fig.axes[0]
                    line = axis.lines[0]
                    points = axis.transData.transform([[0, ys[0]], [1, ys[1]]]).tolist()
                    observed.update({"native_y": list(line.get_ydata()), "native_warnings": native_warnings,
                                     "axis_limits": [list(axis.get_xlim()), list(axis.get_ylim())], "display_points": points})
                    self.assertEqual(list(line.get_ydata()), ys)
                    self.assertTrue(all(math.isfinite(v) for pair in points for v in pair))
                    self.assertGreater(abs(points[1][1] - points[0][1]), 50)
                finally:
                    fig.clear()
            except BaseException as error:
                observed["exception_type"] = type(error).__name__
                observed["exception"] = str(error)
                observed["traceback"] = traceback.format_exc()
                frames = []
                cursor = error.__traceback__
                while cursor:
                    frame = cursor.tb_frame
                    frames.append({"file": frame.f_code.co_filename, "function": frame.f_code.co_name, "line": cursor.tb_lineno})
                    candidate = frame.f_locals.get("fig")
                    if candidate is not None and hasattr(candidate, "axes"):
                        observed["exception_traceback_retains_native_axes"] = len(candidate.axes)
                        observed["exception_retained_lines_y"] = [list(line.get_ydata()) for ax in candidate.axes for line in ax.lines]
                        candidate.clear()
                    cursor = cursor.tb_next
                observed["frames"] = frames
                self.fail("Literal finite source must render a finite, distinct line without backend exception: " + repr(error))
            finally:
                observed["runtime_warnings"] = [str(w.message) for w in emitted]
                observed["elapsed_seconds"] = time.perf_counter() - started
                observed["remaining_root_entries"] = sorted(p.name for p in root.iterdir())
                observed["caller_sentinel_intact"] = sentinel.read_text(encoding="utf-8") == "caller-owned sentinel"
                observed["caller_rows_unchanged"] = json.dumps(rows, allow_nan=False) == literal_before

    def test_01_ordinary_positive_control(self):
        self.check_case("ordinary", [-1.0, 1.0])

    def test_02_finite_opposite_extrema(self):
        self.check_case("finite-extrema", [-1e308, 1e308])

suite = unittest.defaultTestLoader.loadTestsFromTestCase(FiniteNativeAxis)
result = unittest.TextTestRunner(verbosity=2).run(suite)
record = {"source": SOURCE, "tests_run": result.testsRun, "failures": len(result.failures),
          "errors": len(result.errors), "skipped": len(result.skipped), "entry_calls": entry_calls,
          "distinct_literal_inputs": 2, "findings_not_test_count": True, "observations": observations}
(output / "results.json").write_text(json.dumps(record, indent=2, default=float) + "\n", encoding="utf-8")
for name, item in verified.items():
    assert hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"]
sys.exit(0 if result.wasSuccessful() else 1)