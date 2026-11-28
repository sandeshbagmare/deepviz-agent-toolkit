"""Verify that release artifacts contain only package inputs and runtime resources."""
from __future__ import annotations

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
def distributions(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    output = tmp_path_factory.mktemp("release-dist")
    result = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(output.glob("*.whl"))
    sdists = list(output.glob("*.tar.gz"))
    assert len(wheels) == len(sdists) == 1
    return wheels[0], sdists[0]


def _assert_no_repository_evidence(paths: list[str]) -> None:
    forbidden = ("/.github/", "/context/", "/docs/", "/tests/", "/evidence/", "/agent-state/")
    assert not [path for path in paths if any(part in f"/{path}" for part in forbidden)]


def test_wheel_has_runtime_metadata_schema_and_typing(distributions: tuple[Path, Path]) -> None:
    wheel, _ = distributions
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert names.count("deepviz/resources/chart-spec.schema.json") == 1
        assert archive.read("deepviz/resources/chart-spec.schema.json") == (
            ROOT / "schemas/chart-spec.schema.json"
        ).read_bytes()
        assert names.count("deepviz/py.typed") == 1

        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_name).decode("utf-8")
        assert "Version: 0.1.0\n" in metadata
        assert "Provides-Extra: agents\n" in metadata
        assert "Provides-Extra: mcp\n" in metadata
        assert "Provides-Extra: columnar\n" in metadata

        entry_points_name = next(name for name in names if name.endswith(".dist-info/entry_points.txt"))
        entry_points = archive.read(entry_points_name).decode("utf-8")
        assert "deepviz = deepviz.cli:main" in entry_points
        assert "deepviz-mcp = deepviz.mcp_server:main" in entry_points
        _assert_no_repository_evidence(names)


def test_sdist_has_build_sources_but_no_repository_evidence(distributions: tuple[Path, Path]) -> None:
    _, sdist = distributions
    with tarfile.open(sdist, "r:gz") as archive:
        names = archive.getnames()
        assert any(name.endswith("/pyproject.toml") for name in names)
        assert any(name.endswith("/schemas/chart-spec.schema.json") for name in names)
        assert any(name.endswith("/python/deepviz/src/deepviz/py.typed") for name in names)
        assert any(name.endswith("/LICENSE") for name in names)
        _assert_no_repository_evidence(names)


def test_installed_wheel_imports_from_its_target(distributions: tuple[Path, Path], tmp_path: Path) -> None:
    wheel, _ = distributions
    target = tmp_path / "installed"
    install = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--target",
            str(target),
            str(wheel),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert install.returncode == 0, install.stdout + install.stderr

    probe = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "import pathlib, sys; sys.path.insert(0, sys.argv[1]); import deepviz.models; "
            "assert pathlib.Path(deepviz.models.__file__).is_relative_to(pathlib.Path(sys.argv[1]))",
            str(target),
        ],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": ""},
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe.returncode == 0, probe.stdout + probe.stderr


def test_wheel_has_each_canonical_prompt_when_prompt_sources_are_present(
    distributions: tuple[Path, Path],
) -> None:
    source = ROOT / "prompts/v1"
    if not source.is_dir():
        pytest.skip("Canonical prompts/v1 sources are introduced by the integrations change.")

    wheel, sdist = distributions
    prompt_paths = sorted(path for path in source.rglob("*") if path.is_file())
    assert prompt_paths
    with ZipFile(wheel) as archive:
        wheel_names = archive.namelist()
        for path in prompt_paths:
            relative = path.relative_to(source).as_posix()
            resource = f"deepviz/resources/prompts/v1/{relative}"
            assert wheel_names.count(resource) == 1
            assert archive.read(resource) == path.read_bytes()
    with tarfile.open(sdist, "r:gz") as archive:
        names = archive.getnames()
        for path in prompt_paths:
            relative = path.relative_to(ROOT).as_posix()
            assert sum(name.endswith(f"/{relative}") for name in names) == 1
