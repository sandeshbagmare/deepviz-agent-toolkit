"""Negative controls for the owned clean-distribution harness, without installations."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest


def harness(filename="run_clean_distribution.py"):
    path = Path(__file__).with_name(filename)
    assert path.is_file(), "The clean distribution harness is missing"
    spec = importlib.util.spec_from_file_location("r10_role07_distribution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inherited_python_and_private_index_configuration_is_removed(tmp_path):
    environment = harness().isolated_env({
        "PATH": "safe", "PYTHONPATH": "shared", "pythonhome": "global",
        "PYTHONPYCACHEPREFIX": "elsewhere", "VIRTUAL_ENV": "main", "PIP_EXTRA_INDEX_URL": "private",
        "PIP_INDEX_URL": "private", "UV_INDEX_URL": "private", "MYPYPATH": "workspace",
    }, tmp_path)
    assert not {"PYTHONPATH", "pythonhome", "PYTHONPYCACHEPREFIX", "VIRTUAL_ENV",
                "PIP_EXTRA_INDEX_URL", "UV_INDEX_URL", "MYPYPATH"}.intersection(environment)
    assert environment["PIP_INDEX_URL"] == "https://pypi.org/simple"
    assert environment["PIP_CONFIG_FILE"] == os.devnull
    assert environment["PYTHONNOUSERSITE"] == "1"


def test_only_project_declared_build_tool_requirements_are_selected():
    config = {"build-system": {"requires": ["hatchling>=1.27"]}, "project": {
        "optional-dependencies": {"dev": ["build>=1.2", "twine>=6", "pytest>=8", "ruff>=0.11"]},
    }}
    assert harness().build_requirements(config) == ["hatchling>=1.27", "build>=1.2", "twine>=6"]


def test_existing_output_is_not_overwritten(tmp_path):
    path = tmp_path / "existing"
    path.mkdir()
    sentinel = path / "sentinel.txt"
    sentinel.write_text("preserve")
    with pytest.raises(FileExistsError):
        harness().fresh_output(path)
    assert sentinel.read_text() == "preserve"


def test_shared_or_checkout_import_is_rejected(tmp_path):
    own = tmp_path / "own"
    shared = tmp_path / "shared"
    own.mkdir()
    shared.mkdir()
    installed = own / "api.py"
    installed.write_text("local")
    outside = shared / "api.py"
    outside.write_text("not isolated")
    harness().require_origin(installed, own)
    with pytest.raises(AssertionError):
        harness().require_origin(outside, own)


def test_svg_static_output_is_valid_without_a_png(tmp_path):
    svg = tmp_path / "chart.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect width="4" height="10"/></svg>')
    module = harness("consumer_smoke.py")
    assert hasattr(module, "static_image"), "MIME-aware static image oracle is missing"
    assert module.static_image([svg], "image/svg+xml") == svg


def test_invalid_png_is_not_a_static_png_pass(tmp_path):
    png = tmp_path / "chart.png"
    png.write_bytes(b"not a PNG")
    module = harness("consumer_smoke.py")
    assert hasattr(module, "static_image"), "MIME-aware static image oracle is missing"
    with pytest.raises(AssertionError):
        module.static_image([png], "image/png")


def test_non_svg_xml_is_not_a_static_svg_pass(tmp_path):
    svg = tmp_path / "chart.svg"
    svg.write_text("<html/>")
    module = harness("consumer_smoke.py")
    assert hasattr(module, "static_image"), "MIME-aware static image oracle is missing"
    with pytest.raises(AssertionError):
        module.static_image([svg], "image/svg+xml")
