"""Exercise Python distribution contents without importing the editable checkout."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output = tmp_path_factory.mktemp("packaging-dist")
    result = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(output)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return next(output.glob("*.whl"))


def test_sdist_built_wheel_contains_versioned_prompts(wheel: Path) -> None:
    with ZipFile(wheel) as archive:
        for name in ("system", "request"):
            resource = f"deepviz/resources/prompts/v1/{name}.md"
            assert resource in archive.namelist(), f"Missing wheel resource: {resource}"
            assert archive.read(resource).decode("utf-8") == (
                ROOT / "prompts" / "v1" / f"{name}.md"
            ).read_text(encoding="utf-8")


@pytest.mark.parametrize("kind", ["wheel", "sdist"])
def test_python_distributions_publish_inline_typing_marker(wheel: Path, kind: str) -> None:
    if kind == "wheel":
        with ZipFile(wheel) as archive:
            assert "deepviz/py.typed" in archive.namelist(), "Wheel lacks the PEP 561 marker"
    else:
        with tarfile.open(next(wheel.parent.glob("*.tar.gz")), "r:gz") as source:
            markers = [
                member for member in source.getmembers()
                if member.name.endswith("/python/deepviz/src/deepviz/py.typed") and member.isfile()
            ]
            assert len(markers) == 1, "Sdist lacks the PEP 561 marker"


def test_installed_wheel_can_read_prompts_and_schema(wheel: Path, tmp_path: Path) -> None:
    target = tmp_path / "installed"
    install = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", "--target", str(target), str(wheel)],
        capture_output=True, text=True, check=False,
    )
    assert install.returncode == 0, install.stdout + install.stderr
    probe = subprocess.run(
        [sys.executable, "-I", "-c", """
import importlib.resources
import json
import pathlib
import sys
sys.path.insert(0, sys.argv[1])
import deepviz
assert pathlib.Path(deepviz.__file__).is_relative_to(pathlib.Path(sys.argv[1]))
for name in ('system', 'request'):
    assert deepviz.read_prompt(name).strip()
schema = json.loads(importlib.resources.files('deepviz').joinpath('resources/chart-spec.schema.json').read_text())
assert schema['$defs']['ChartSpec']['properties']['version']['const'] == 1
assert importlib.resources.files('deepviz').joinpath('py.typed').is_file(), 'Installed PEP 561 marker absent'
print(json.dumps({'source': deepviz.__file__, 'prompts': ['system', 'request']}))
""", str(target)],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert probe.returncode == 0, probe.stdout + probe.stderr
    assert json.loads(probe.stdout)["prompts"] == ["system", "request"]


def test_external_mypy_discovers_installed_public_annotations(wheel: Path, tmp_path: Path) -> None:
    consumer = tmp_path / "consumer"
    python = consumer / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    for command in (
        [sys.executable, "-m", "venv", str(consumer)],
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
    ):
        result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
    environment = {key: value for key, value in os.environ.items()
                   if key not in {"MYPYPATH", "PYTHONPATH", "PYTHONHOME"}}
    probe = tmp_path / "consumer_api.py"
    probe.write_text(
        'from typing import assert_type\nimport deepviz\n'
        'assert_type(deepviz.read_prompt("system", version=1), str)\n', encoding="utf-8",
    )
    command = [
        sys.executable, "-I", "-m", "mypy", "--python-executable", str(python),
        "--no-incremental", "--follow-imports=silent", "--show-error-codes", str(probe),
    ]
    valid = subprocess.run(command, cwd=tmp_path, env=environment, capture_output=True, text=True, check=False)
    assert valid.returncode == 0, valid.stdout + valid.stderr
    probe.write_text('import deepviz\ndeepviz.read_prompt(123, version="1")\n', encoding="utf-8")
    invalid = subprocess.run(command, cwd=tmp_path, env=environment, capture_output=True, text=True, check=False)
    assert invalid.returncode == 1, invalid.stdout + invalid.stderr
    assert invalid.stdout.count("[arg-type]") == 2, invalid.stdout + invalid.stderr
