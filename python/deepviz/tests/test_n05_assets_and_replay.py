"""Author regressions for concrete N20/N17 asset and replay findings."""
from __future__ import annotations

import hashlib
import importlib
from html.parser import HTMLParser
from pathlib import Path

import pytest

from deepviz.models import ChartSpec
from deepviz.render import render


class _HTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.comments = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.scripts.append(dict(attrs))

    def handle_comment(self, data):
        self.comments.append(data)


def test_echarts_artifact_loads_the_reviewed_patched_runtime(tmp_path):
    artifact = render([{"label": "Alpha", "value": 3}], ChartSpec(), "echarts", tmp_path)
    document = _HTML()
    document.feed(next(Path(path) for path in artifact.paths if path.endswith(".html")).read_text(encoding="utf-8"))
    assert [script["src"] for script in document.scripts if "src" in script] == [
        "https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"
    ]


def test_standalone_plotly_contains_complete_offline_upstream_notice(tmp_path):
    from plotly.offline import get_plotlyjs_version

    artifact = render([{"label": "Alpha", "value": 3}], ChartSpec(), "plotly", tmp_path)
    document = _HTML()
    document.feed(next(Path(path) for path in artifact.paths if path.endswith(".html")).read_text(encoding="utf-8"))
    notices = [comment for comment in document.comments
               if "MIT License" in comment and "Plotly Technologies Inc." in comment]
    assert len(notices) == 1, "Self-contained copied runtime must retain its complete permission/warranty notice"
    assert get_plotlyjs_version() in notices[0], "Identify the runtime actually copied, not only the audited tag"
    notice = "MIT License" + notices[0].split("MIT License", 1)[1]
    # Independent N20 hash of the exact official v3.7.0 LICENSE; not a hash of production's resource.
    assert hashlib.sha256((notice.strip() + "\n").encode()).hexdigest() == (
        "8c45d9eaf50c2f72dd9c7ab9ef440788ba58a3538484b5c51c1f17d5128752e7"
    )
    assert not any("src" in script for script in document.scripts)


def test_invalid_dashboard_width_stops_source_before_replay_serialization(tmp_path):
    visits = []

    def source():
        visits.append("invalid")
        yield {f"field_{index}": index for index in range(1025)}
        visits.append("overread")
        raise AssertionError("A malformed row must fail before requesting another source row")

    with pytest.raises(ValueError, match="1024 fields"):
        render(source(), {"kind": "dashboard", "charts": [{"kind": "table"}]}, "echarts", tmp_path)
    assert visits == ["invalid"]
    assert not list(tmp_path.iterdir())


def test_replay_owned_file_closes_on_flattened_schema_validation_error(tmp_path, monkeypatch):
    module = importlib.import_module("deepviz.render")
    monkeypatch.setattr(module.tempfile, "tempdir", str(tmp_path))
    # Every individual object is narrow, but the flattened record exceeds the field boundary.
    row = {f"group_{group}": {f"value_{index}": index for index in range(5)} for group in range(205)}
    with pytest.raises(ValueError, match="1024 fields"):
        render(iter([row]), {"kind": "dashboard", "charts": [{"kind": "table"}]}, "echarts", tmp_path / "out")
    assert not list(tmp_path.iterdir()), "A live replay generator must not block Windows scratch cleanup"
