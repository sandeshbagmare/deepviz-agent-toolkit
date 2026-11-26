"""Independent actual-output oracles, not a claim of an exploitable user-data path."""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from deepviz import render

# Preserved official v3.7.0 LICENSE, not the project's or production resource's text:
# https://raw.githubusercontent.com/plotly/plotly.js/v3.7.0/LICENSE
PLOTLY_LICENSE = """MIT License

Copyright (c) 2016-2024 Plotly Technologies Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
ROWS = [{"category": "a", "value": 2}, {"category": "b", "value": 3}]


class _Html(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.sources.extend(value for name, value in attrs if name == "src" and value)

    def handle_data(self, data: str) -> None:
        self.text.append(data)

    def handle_comment(self, data: str) -> None:
        self.text.append(data)


def _assert_patched_echarts(html: str) -> None:
    parsed = _Html()
    parsed.feed(html)
    sources = [source for source in parsed.sources if re.search(r"/echarts(?:@|/)", urlsplit(source).path)]
    assert sources, "Actual Python HTML does not identify an exact-version ECharts script"
    for source in sources:
        url = urlsplit(source)
        pin = re.search(r"/echarts@(\d+)\.(\d+)\.(\d+)/dist/echarts(?:\.min)?\.js$", url.path)
        assert url.scheme == "https" and pin, f"ECharts must use an exact stable HTTPS pin: {source}"
        assert tuple(map(int, pin.groups())) >= (6, 1, 0), f"Unpatched effective ECharts runtime: {source}"


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for child in value.values() for text in _strings(child)]
    if isinstance(value, list):
        return [text for child in value for text in _strings(child)]
    return []


def _assert_notice_delivered(paths: list[Path]) -> None:
    expected = " ".join(PLOTLY_LICENSE.split())
    for path in paths:
        assert path.is_file(), f"Returned artifact does not exist: {path}"
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.suffix == ".json":
            texts = _strings(json.loads(content))
        else:
            parsed = _Html()
            parsed.feed(content)
            texts = [content, " ".join(parsed.text)]
        if any(expected in " ".join(text.split()) for text in texts):
            return
    pytest.fail("Full upstream Plotly.js copyright, permission and warranty notice absent from returned artifacts")


def _spec(dashboard: bool) -> dict:
    child = {"kind": "bar", "x": "category", "y": "value", "aggregation": "none"}
    return {"kind": "dashboard", "charts": [child, {**child, "kind": "line"}]} if dashboard else child


@pytest.mark.parametrize("dashboard", [False, True], ids=["single", "dashboard"])
def test_n20_actual_python_echarts_html_uses_patched_pin(tmp_path: Path, dashboard: bool) -> None:
    artifact = render(ROWS, _spec(dashboard), engine="echarts", output_dir=tmp_path)
    assert artifact.engine == "echarts"
    html = [Path(path) for path in artifact.paths if Path(path).suffix == ".html"]
    assert html, "Artifact.paths must return the generated HTML"
    for path in html:
        _assert_patched_echarts(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("dashboard", [False, True], ids=["single", "dashboard"])
def test_n20_actual_plotly_output_delivers_full_upstream_notice(tmp_path: Path, dashboard: bool) -> None:
    artifact = render(ROWS, _spec(dashboard), engine="plotly", output_dir=tmp_path)
    assert artifact.engine == "plotly"
    html = [Path(path) for path in artifact.paths if Path(path).suffix == ".html"]
    assert html and any("plotly.js v" in path.read_text(encoding="utf-8") for path in html)
    _assert_notice_delivered([Path(path) for path in artifact.paths])


def test_n20_preserved_official_notice_identity() -> None:
    assert hashlib.sha256(PLOTLY_LICENSE.encode()).hexdigest() == (
        "8c45d9eaf50c2f72dd9c7ab9ef440788ba58a3538484b5c51c1f17d5128752e7"
    )


@pytest.mark.parametrize("pin", ["5.6.0", "6.0.9", "6.1.0-rc.1", "latest", "^6.1.0"])
def test_n20_pin_oracle_rejects_old_prerelease_and_floating_versions(pin: str) -> None:
    with pytest.raises(AssertionError):
        _assert_patched_echarts(f'<script src="https://cdn.jsdelivr.net/npm/echarts@{pin}/dist/echarts.min.js">')


@pytest.mark.parametrize("pin", ["6.1.0", "6.2.0", "7.0.0"])
def test_n20_pin_oracle_accepts_stable_patched_versions(pin: str) -> None:
    _assert_patched_echarts(f'<script src="https://cdn.jsdelivr.net/npm/echarts@{pin}/dist/echarts.min.js">')


@pytest.mark.parametrize("delivery", ["inline", "returned-text", "returned-json"])
def test_n20_notice_oracle_accepts_complete_inline_or_returned_companion(tmp_path: Path, delivery: str) -> None:
    html = tmp_path / "chart.html"
    html.write_text(f"<pre>{PLOTLY_LICENSE}</pre>" if delivery == "inline" else "<p>Chart</p>", encoding="utf-8")
    paths = [html]
    if delivery != "inline":
        companion = tmp_path / ("notice.json" if delivery == "returned-json" else "LICENSE.txt")
        companion.write_text(json.dumps({"license": PLOTLY_LICENSE}) if delivery == "returned-json"
                             else PLOTLY_LICENSE, encoding="utf-8")
        paths.append(companion)
    _assert_notice_delivered(paths)


@pytest.mark.parametrize("short_notice", [
    "Copyright 2012-2026 Plotly, Inc. Licensed under the MIT license",
    PLOTLY_LICENSE.split("THE SOFTWARE IS PROVIDED")[0],
    PLOTLY_LICENSE[PLOTLY_LICENSE.index("THE SOFTWARE IS PROVIDED"):],
    '<a href="https://raw.githubusercontent.com/plotly/plotly.js/v3.7.0/LICENSE">MIT license</a>',
])
def test_n20_notice_oracle_rejects_incomplete_or_only_unreturned_notice(tmp_path: Path, short_notice: str) -> None:
    html = tmp_path / "chart.html"
    html.write_text(short_notice, encoding="utf-8")
    (tmp_path / "unreturned-LICENSE.txt").write_text(PLOTLY_LICENSE, encoding="utf-8")
    with pytest.raises(pytest.fail.Exception, match="Full upstream Plotly.js"):
        _assert_notice_delivered([html])
