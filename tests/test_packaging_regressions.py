"""Exercise Python distribution contents without importing the editable checkout."""
from __future__ import annotations

import json
import subprocess
import sys
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
print(json.dumps({'source': deepviz.__file__, 'prompts': ['system', 'request']}))
""", str(target)],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert probe.returncode == 0, probe.stdout + probe.stderr
    assert json.loads(probe.stdout)["prompts"] == ["system", "request"]
