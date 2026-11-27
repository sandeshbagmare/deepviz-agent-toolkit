"""Use an already available declared backend; never install build dependencies."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.integration


def test_offline_wheel_has_one_canonical_resource_copy_and_no_dangling_commands(tmp_path: Path) -> None:
    output = tmp_path / "dist"
    result = subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation", "--wheel", "--outdir", str(output)],
        cwd=ROOT, env={**os.environ, "PIP_NO_INDEX": "1", "UV_OFFLINE": "1"},
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(output.glob("*.whl"))
    assert len(wheels) == 1
    with ZipFile(wheels[0]) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), "Wheel must not contain ambiguous duplicate destinations"
        for resource, canonical in (
            ("deepviz/resources/prompts/v1/system.md", "prompts/v1/system.md"),
            ("deepviz/resources/prompts/v1/request.md", "prompts/v1/request.md"),
            ("deepviz/resources/chart-spec.schema.json", "schemas/chart-spec.schema.json"),
        ):
            assert names.count(resource) == 1
            assert archive.read(resource) == (ROOT / canonical).read_bytes()
        assert "deepviz/py.typed" in names
        assert {name for name in names if name.startswith("deepviz/") and name.endswith(".py")} == {
            "deepviz/__init__.py", "deepviz/models.py", "deepviz/normalize.py",
        }
        assert not any(name.endswith("/entry_points.txt") for name in names)
