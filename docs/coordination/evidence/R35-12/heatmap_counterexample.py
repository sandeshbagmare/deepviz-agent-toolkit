"""One strict uncovered heatmap counterexample and numeric positive control."""
from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
import unittest
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = "85796dbe3360fb88686f2e7188122e2da80d54c2"
assert sys.flags.no_site and sys.dont_write_bytecode
assert "deepviz" not in sys.modules
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == SOURCE
site_packages = Path(sys.executable).resolve().parents[1] / "Lib" / "site-packages"
assert site_packages.is_dir()
sys.path[:0] = [str(ROOT / "python/deepviz/src"), str(site_packages)]
modules = {name: importlib.import_module(f"deepviz.{name}") for name in ("models", "normalize", "engines", "render")}
identity = []
for name, module in modules.items():
    path = Path(module.__file__).resolve()
    expected = ROOT / "python/deepviz/src/deepviz" / f"{name}.py"
    assert path == expected, (path, expected)
    relative = path.relative_to(ROOT).as_posix()
    blob = subprocess.check_output(["git", "show", f"{SOURCE}:{relative}"], cwd=ROOT)
    assert path.read_bytes().replace(b"\r\n", b"\n") == blob
    identity.append({"module": module.__name__, "file": str(path),
                     "sha256": hashlib.sha256(blob).hexdigest()})
ChartSpec, normalize, channels = modules["models"].ChartSpec, modules["normalize"].normalize, modules["engines"].channels
observations = []


class ImplicitHeatmapCoordinate(unittest.TestCase):
    def check_coordinates(self, north_values):
        first, second = north_values
        rows = [{"east": "E", "north": first}, {"east": "E", "north": first},
                {"east": "W", "north": second}]
        spec = ChartSpec(kind="heatmap", x="east", aggregation="count")
        normalized = normalize(rows, spec)
        mapped = channels(normalized.records, spec)
        observation = {"input": rows, "spec": spec.model_dump(), "normalized": asdict(normalized),
                       "channels": mapped, "expected_y": north_values,
                       "actual_y": [row["_y"] for row in mapped]}
        observations.append(observation)
        self.assertEqual(normalized.records, [
            {"east": "E", "north": first, "count": 2},
            {"east": "W", "north": second, "count": 1},
        ])
        self.assertEqual(normalized.input_count, 3)
        self.assertEqual(normalized.strategy, "count")
        self.assertEqual(normalized.warnings, [])
        self.assertEqual([row["_x"] for row in mapped], ["E", "W"])
        self.assertEqual([row["_heat"] for row in mapped], [2, 1])
        self.assertEqual([row["_y"] for row in mapped], north_values)

    def test_numeric_coordinate_positive(self):
        self.check_coordinates([0, 1])

    def test_string_coordinate_counterexample(self):
        self.check_coordinates(["N", "S"])


with (OUT / "heatmap-counterexample-v1.log").open("x", encoding="utf-8", newline="\n") as log:
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ImplicitHeatmapCoordinate))
receipt = {
    "source": SOURCE, "python": sys.version, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "no_site": True, "no_bytecode_writes": True, "readonly_dependencies": str(site_packages),
    "same_process_own_module_identity": identity, "observations": observations,
    "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
    "skips": len(result.skipped), "passes": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
    "classification": "Pre-existing heatmap implicit-coordinate inference bug; the two added 857 lines exclude heatmap",
    "native_artifacts_or_browser_paint": False, "production_changed": False,
}
with (OUT / "heatmap-counterexample-v1.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({key: value for key, value in receipt.items() if key not in {
    "same_process_own_module_identity", "observations"
}}, indent=2))
sys.exit(0 if result.wasSuccessful() else 1)
