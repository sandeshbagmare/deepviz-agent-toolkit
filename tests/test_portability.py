"""Filesystem, encoding, and optional-extra contracts across Windows and Linux."""
from __future__ import annotations

import inspect
import json
import os
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

import pytest

from deepviz.models import Artifact, ChartSpec

OPTIONAL_IMPORT_BLOCKER = """
import importlib.abc
import sys

class NoOptionalExtras(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {
            'deepagents', 'langchain', 'langchain_core', 'langgraph', 'mcp', 'pyarrow',
        }:
            raise ModuleNotFoundError('Blocked optional extra: ' + fullname, name=fullname)

sys.meta_path.insert(0, NoOptionalExtras())
"""


@pytest.fixture
def rows() -> list[dict[str, Any]]:
    return [{"label": "café", "value": 2}, {"label": "東京", "value": 5}]


@pytest.fixture
def spec() -> ChartSpec:
    return ChartSpec(kind="bar", x="label", y="value", max_points=10, width=320, height=240)


def _paths(artifact: Artifact, root: Path) -> list[Path]:
    paths = [Path(value) for value in artifact.paths]
    assert paths, "A successful render must return its artifacts"
    for path in paths:
        assert path.is_absolute(), f"Artifact is dependent on the caller's cwd: {path}"
        assert path.is_file(), f"Artifact was not written: {path}"
        assert path.resolve().is_relative_to(root.resolve()), f"Artifact escaped output_dir: {path}"
    return paths


def _manifest(paths: list[Path]) -> dict[str, Any]:
    path = next(path for path in paths if path.name == "manifest.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _run_python(arguments: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    # Pin subprocesses to the same checkout as pytest, not a different editable install.
    source_root = str(Path(inspect.getfile(ChartSpec)).resolve().parents[1])
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [source_root, env.get("PYTHONPATH")]))
    result = subprocess.run(
        [sys.executable, *arguments], cwd=cwd, env=env, capture_output=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    return result


def test_render_writes_utf8_artifacts_under_spaced_unicode_directory(tmp_path, rows, spec):
    from deepviz.render import render

    destination = tmp_path / "résultats 東京 with spaces"
    artifact = render(rows, spec, engine="echarts", output_dir=destination)

    paths = _paths(artifact, destination)
    assert _manifest(paths)["charts"][0]["records"] == rows
    html = next(path for path in paths if path.suffix == ".html").read_text(encoding="utf-8")
    assert "<html" in html.lower()


def test_hostile_title_is_metadata_not_a_raw_filesystem_path(tmp_path, rows, spec):
    from deepviz.render import render

    title = '../CON:..\\NUL?*|"<東京> '
    artifact = render(rows, spec.model_copy(update={"title": title}), engine="echarts", output_dir=tmp_path)

    paths = _paths(artifact, tmp_path)
    assert _manifest(paths)["charts"][0]["spec"]["title"] == title
    for path in paths:
        for component in path.relative_to(tmp_path).parts:
            assert not set('<>:"/\\|?*').intersection(component)
            assert component == component.rstrip(" .")
            assert not PureWindowsPath(component).is_reserved()


def test_existing_user_files_named_like_artifacts_are_never_overwritten(tmp_path, rows, spec):
    from deepviz.render import render

    originals = {
        name: b"user-owned\x00\xff" + name.encode("ascii")
        for name in ("chart.html", "chart.png", "chart.svg", "manifest.json")
    }
    for name, content in originals.items():
        (tmp_path / name).write_bytes(content)

    paths = _paths(render(rows, spec, engine="echarts", output_dir=tmp_path), tmp_path)

    assert all((tmp_path / name).read_bytes() == content for name, content in originals.items())
    assert all(path not in {tmp_path / name for name in originals} for path in paths)


def test_repeated_tool_session_renders_have_unique_paths_and_preserve_prior_bytes(tmp_path, rows, spec):
    from deepviz.tools import ToolSession

    destination = tmp_path / "tool output 東京"
    session = ToolSession(destination)
    first = Artifact(**session.render_chart("echarts", rows, spec))
    saved = {path: path.read_bytes() for path in _paths(first, destination)}

    second = Artifact(**session.render_chart("echarts", rows, spec))
    new_paths = _paths(second, destination)

    assert set(saved).isdisjoint(new_paths)
    assert all(path.read_bytes() == content for path, content in saved.items())


def test_relative_output_directory_is_resolved_at_render_time(tmp_path, monkeypatch, rows, spec):
    from deepviz.render import render

    monkeypatch.chdir(tmp_path)
    artifact = render(rows, spec, engine="echarts", output_dir="relative output 東京")
    elsewhere = tmp_path / "different cwd"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    _paths(artifact, tmp_path / "relative output 東京")


def test_absolute_output_directory_is_independent_of_current_directory(tmp_path, monkeypatch, rows, spec):
    from deepviz.render import render

    elsewhere = tmp_path / "unrelated cwd"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    destination = tmp_path / "absolute output 東京"

    artifact = render(rows, spec, engine="echarts", output_dir=str(destination))

    _paths(artifact, destination)
    assert list(elsewhere.iterdir()) == []


def test_file_used_as_output_directory_is_rejected_without_destroying_it(tmp_path, rows, spec):
    from deepviz.render import render

    destination = tmp_path / "existing user file 東京"
    destination.write_bytes(b"keep this file unchanged")

    with pytest.raises((OSError, ValueError)):
        render(rows, spec, engine="echarts", output_dir=destination)

    assert destination.read_bytes() == b"keep this file unchanged"
    assert list(tmp_path.iterdir()) == [destination]


def test_cli_stdout_is_utf8_json_and_unicode_paths_round_trip(tmp_path, rows, spec):
    source = tmp_path / "données 東京.json"
    source.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    spec_path = tmp_path / "chart spec 東京.json"
    spec_path.write_text(spec.model_copy(update={"title": "Café 東京"}).model_dump_json(), encoding="utf-8")

    result = _run_python([
        "-m", "deepviz.cli", "render", source.name, "--spec", spec_path.name,
        "--engine", "echarts", "--output-dir", "CLI output 東京",
    ], tmp_path)

    payload = json.loads(result.stdout.decode("utf-8", errors="strict"))
    artifact = Artifact(**payload)
    paths = _paths(artifact, tmp_path / "CLI output 東京")
    assert artifact.input_count == artifact.output_count == 2
    manifest = _manifest(paths)
    assert manifest["charts"][0]["records"] == rows
    assert manifest["charts"][0]["spec"]["title"] == "Café 東京"


def test_core_package_imports_without_agent_mcp_or_columnar_extras(tmp_path):
    _run_python(["-c", OPTIONAL_IMPORT_BLOCKER + """
import deepviz
import deepviz.cli
import deepviz.mcp_server
import deepviz.tools

assert callable(deepviz.render)
assert callable(deepviz.normalize)
result = deepviz.normalize([{'x': 1, 'y': 2}], deepviz.ChartSpec(kind='scatter', x='x', y='y'))
assert result.input_count == 1 and result.records == [{'x': 1, 'y': 2}]
"""], tmp_path)


@pytest.mark.parametrize("module,factory,extra", [
    ("deepviz", "create_tools", "agents"),
    ("deepviz.mcp_server", "create_server", "mcp"),
])
def test_missing_optional_extra_has_actionable_error_without_uninstalling_it(tmp_path, module, factory, extra):
    script = OPTIONAL_IMPORT_BLOCKER + f"""
from importlib import import_module

factory = getattr(import_module({module!r}), {factory!r})
try:
    factory({str(tmp_path)!r})
except ImportError as error:
    message = str(error).lower()
    assert 'install' in message and {extra!r} in message, str(error)
else:
    raise AssertionError('Optional dependency was blocked, but its factory succeeded')
"""
    _run_python(["-c", script], tmp_path)


def test_dashboard_consumes_generator_once_and_replays_every_row_for_each_child(tmp_path, rows, spec):
    from deepviz.render import render

    consumed = []

    def source():
        for row in rows:
            consumed.append(row["label"])
            yield row

    dashboard = ChartSpec(kind="dashboard", charts=[spec, spec.model_copy(update={"kind": "line"})])
    artifact = render(source(), dashboard, engine="echarts", output_dir=tmp_path)

    charts = _manifest(_paths(artifact, tmp_path))["charts"]
    assert consumed == ["café", "東京"]
    assert artifact.input_count == 2 and artifact.output_count == 4
    assert len(charts) == 2
    assert all(chart["input_count"] == 2 and chart["records"] == rows for chart in charts)
