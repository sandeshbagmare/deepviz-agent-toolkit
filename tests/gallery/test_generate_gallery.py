"""Real CLI/Matplotlib regressions for the test-only gallery producer."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

SCRIPT = Path(__file__).with_name("generate-gallery.py")
ROOT = Path(__file__).resolve().parents[2]


def run_cli(output: Path, *options: str, no_site: bool = False) -> subprocess.CompletedProcess[str]:
    assert SCRIPT.is_file(), "The real gallery CLI has not been implemented"
    command = [sys.executable, *(["-S"] if no_site else []), str(SCRIPT),
               "--source-root", str(ROOT), "--output", str(output), *options]
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(command, env=env, capture_output=True, text=True, timeout=90, check=False)


def read_manifest(output: Path) -> dict:
    return json.loads((output / "gallery-manifest.json").read_text(encoding="utf-8"))


def verify_file(root: Path, info: dict) -> Path:
    path = Path(info["path"])
    assert not path.is_absolute() and ".." not in path.parts and "\\" not in info["path"]
    target = (root / path).resolve(strict=True)
    assert target.is_relative_to(root.resolve())
    content = target.read_bytes()
    assert hashlib.sha256(content).hexdigest() == info["sha256"]
    if "bytes" in info:
        assert type(info["bytes"]) is int and len(content) == info["bytes"] > 0
    return target


@pytest.fixture(scope="module")
def gallery_module():
    assert SCRIPT.is_file(), "The real gallery CLI has not been implemented"
    spec = importlib.util.spec_from_file_location("n14_gallery", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def native_bar(tmp_path_factory):
    output = tmp_path_factory.mktemp("n14-gallery-parent") / "bar"
    result = run_cli(output, "--engine", "matplotlib", "--case", "bar-light")
    assert result.returncode == 0, result.stdout + result.stderr
    return output, read_manifest(output), result


def test_cli_produces_real_native_bar_and_v1_manifest(native_bar):
    output, manifest, result = native_bar
    assert manifest["version"] == 1 and manifest["failures"] == []
    assert len(manifest["items"]) == 1
    item = manifest["items"][0]
    assert item["id"] == "bar-light-matplotlib"
    assert item["case"] == "bar-light" and item["engine"] == "matplotlib"
    assert item["spec"]["aggregation"] == "none" and item["spec"]["theme"] == "light"
    assert (item["input_count"], item["output_count"], item["strategy"]) == (3, 3, "none")
    paths = [verify_file(output, info) for info in item["files"]]
    assert {path.suffix for path in paths} >= {".png", ".svg", ".html", ".json"}
    assert item["entry_path"].endswith("chart.html")
    assert output / item["entry_path"] in paths
    native = json.loads((output / item["native_manifest_path"]).read_text())
    assert item["warnings"] == native["warnings"]
    assert native["charts"][0]["records"] == [
        {"category": "Alpha", "value": 2}, {"category": "Beta", "value": 5},
        {"category": "Gamma", "value": 9},
    ]
    image = next(path for path in paths if path.suffix == ".png")
    assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    with Image.open(image) as picture:
        assert picture.width >= 600 and picture.height >= 350
        colors = picture.convert("RGB").getcolors(picture.width * picture.height)
        assert colors is not None and len(colors) > 20
    assert str(ROOT / "python/deepviz/src/deepviz/__init__.py") in result.stderr


def test_source_commit_and_portable_snapshots_match_actual_checkout(native_bar):
    output, manifest, _ = native_bar
    source = manifest["source"]
    assert re.fullmatch(r"[a-f0-9]{40}", source["commit"])
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert source["commit"] == head and source["python_version"] == sys.version
    assert len(source["module_files"]) >= 5
    for info in source["module_files"]:
        snapshot = verify_file(output, info)
        original = ROOT / Path(info["path"]).relative_to("source")
        assert snapshot.read_bytes() == original.read_bytes()


def test_existing_output_is_never_reused_or_changed(native_bar):
    output, manifest, _ = native_bar
    before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    result = run_cli(output, "--engine", "matplotlib", "--case", "bar-light")
    assert result.returncode != 0 and "exist" in result.stderr.lower()
    assert read_manifest(output) == manifest
    assert before == {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}


@pytest.mark.parametrize(("case", "counts"), [("line-numeric", (3, 3)), ("dashboard-mixed", (2, 4))])
def test_cli_other_known_cases_use_actual_public_render(tmp_path, case, counts):
    output = tmp_path / case
    result = run_cli(output, "--engine", "matplotlib", "--case", case)
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = read_manifest(output)
    assert not manifest["failures"]
    item = manifest["items"][0]
    assert (item["input_count"], item["output_count"]) == counts
    native = json.loads((output / item["native_manifest_path"]).read_text())
    if case == "line-numeric":
        assert [(r["x"], r["y"]) for r in native["charts"][0]["records"]] == [(1, 2), (2, 8), (4, 5)]
    else:
        assert [chart["spec"]["theme"] for chart in native["charts"]] == ["light", "dark"]
        assert all([r["value"] for r in chart["records"]] == [3, 7] for chart in native["charts"])


def test_invalid_engine_keeps_honest_partial_manifest(tmp_path):
    output = tmp_path / "partial"
    result = run_cli(output, "--engine", "unknown-engine", "--engine", "matplotlib", "--engine", "matplotlib",
                     "--case", "bar-light", "--case", "bar-light")
    assert result.returncode == 1
    manifest = read_manifest(output)
    assert [item["id"] for item in manifest["items"]] == ["bar-light-matplotlib"]
    assert len(manifest["failures"]) == 1
    assert manifest["failures"][0]["engine"] == "unknown-engine"
    assert "unknown" in manifest["failures"][0]["error"].lower()


@pytest.mark.parametrize("options", [("--engine", "--case", "bar-light"),
                                    ("--engine", "matplotlib", "--case", "unknown-case")])
def test_bad_or_missing_selection_is_failure_not_skip(tmp_path, options):
    output = tmp_path / "invalid"
    result = run_cli(output, *options)
    assert result.returncode == 1
    manifest = read_manifest(output)
    assert manifest["items"] == [] and len(manifest["failures"]) == 1
    assert manifest["failures"][0]["error"]


def test_missing_installed_dependency_is_not_reported_as_success(tmp_path):
    output = tmp_path / "missing-dependency"
    result = run_cli(output, "--engine", "matplotlib", "--case", "bar-light", no_site=True)
    assert result.returncode == 1
    manifest = read_manifest(output)
    assert manifest["items"] == [] and len(manifest["failures"]) == 1
    assert "ModuleNotFoundError" in manifest["failures"][0]["error"]
    assert not list(output.rglob("*.png"))


def test_default_cli_attempts_all_fifteen_combinations_without_skipping_missing_backends(tmp_path):
    output = tmp_path / "all-missing-dependencies"
    result = run_cli(output, no_site=True)
    assert result.returncode == 1
    manifest = read_manifest(output)
    assert manifest["items"] == [] and len(manifest["failures"]) == 15
    attempted = {(failure["case"], failure["engine"]) for failure in manifest["failures"]}
    assert attempted == {(case, engine) for case in ("bar-light", "line-numeric", "dashboard-mixed")
                         for engine in ("matplotlib", "plotly", "vega", "echarts", "antv")}
    assert all("ModuleNotFoundError" in failure["error"] for failure in manifest["failures"])


def test_defaults_and_independent_known_oracles(gallery_module):
    assert gallery_module.ENGINES == ("matplotlib", "plotly", "vega", "echarts", "antv")
    assert gallery_module.CASES == ("bar-light", "line-numeric", "dashboard-mixed")
    expected = {case: gallery_module.known_case(case)[2] for case in gallery_module.CASES}
    assert expected["bar-light"]["charts"][0]["points"] == [["Alpha", 2], ["Beta", 5], ["Gamma", 9]]
    assert expected["line-numeric"]["charts"][0]["points"] == [[1, 2], [2, 8], [4, 5]]
    panels = expected["dashboard-mixed"]["charts"]
    assert [panel["theme"] for panel in panels] == ["light", "dark"]
    assert all(panel["points"] == [["A", 3], ["B", 7]] for panel in panels)
