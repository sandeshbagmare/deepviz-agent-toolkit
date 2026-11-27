"""N01-owned positive controls for streaming, parser, and trust boundaries."""
from __future__ import annotations

import io
import json
import tracemalloc
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from deepviz.engines import browser_html, native_spec
from deepviz.models import ChartSpec
from deepviz.normalize import normalize
from deepviz.tools import ToolSession


def test_bounded_unique_stream_keeps_sum_of_every_source_observation() -> None:
    source_count = 100_000
    tracemalloc.start()
    try:
        prepared = normalize(
            ({"category": f"group-{i}", "value": i} for i in range(source_count)),
            {"x": "category", "y": "value", "aggregation": "sum", "max_points": 10},
        )
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert prepared.input_count == source_count
    assert len(prepared.records) == 10
    assert sum(row["value"] for row in prepared.records) == source_count * (source_count - 1) // 2
    assert any("other" in note for note in prepared.warnings)
    assert peak < 4_000_000
    print(f"N01_STREAMING_MEMORY input={source_count} output={len(prepared.records)} python_peak_bytes={peak}")


def test_delimited_multiline_quotes_bom_and_nonfinite_disclosure() -> None:
    text = '\ufeffid,note,value\r\n001,"north,\r\n\"\"quoted\"\"",3\r\n002,end,Infinity\r\n'
    prepared = normalize(text, {"kind": "table", "format": "csv", "aggregation": "none"})
    assert prepared.records == [
        {"id": "001", "note": 'north,\r\n"quoted"', "value": 3},
        {"id": "002", "note": "end", "value": None},
    ]
    assert prepared.input_count == 2
    assert any("non-finite" in note for note in prepared.warnings)


def test_jsonl_text_stream_retains_pages_and_reports_null_nodes() -> None:
    pages = [
        {"data": {"users": {"edges": [{"node": {"value": 3}}, {"node": None}]}}},
        {"data": {"users": {"edges": [{"node": {"value": 5}}]}}},
    ]
    source = io.StringIO("\n".join(json.dumps(page) for page in pages))
    prepared = normalize(source, {"format": "jsonl", "aggregation": "none"})
    assert prepared.records == [{"value": 3}, {"value": 5}]
    assert prepared.input_count == 2
    assert any("null GraphQL" in note for note in prepared.warnings)


@pytest.mark.parametrize("untrusted", ["https://invalid.example/data.json", "C:/private/secrets.json"])
def test_plain_data_strings_never_open_local_files(untrusted: str, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden_open(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("A data string was interpreted as a file")

    monkeypatch.setattr(Path, "open", forbidden_open)
    with pytest.raises(ValueError):
        normalize(untrusted, {"kind": "table"})


@pytest.mark.parametrize("extra", [{"expression": "process.exit(1)"}, {"data_url": "http://127.0.0.1/"}])
def test_model_rejects_execution_and_remote_source_fields(extra: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        ChartSpec.model_validate(extra)


def test_tool_session_requires_explicit_host_file_authority(tmp_path: Path) -> None:
    session = ToolSession(output_dir=tmp_path)
    with pytest.raises(ValueError, match="configure data_dir"):
        session.normalize_data({"file": "source.json"})
    with pytest.raises(ValueError, match="explicit.*file|inline JSON"):
        session.normalize_data("C:/private/secrets.json")


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_payload = False
        self.payload: list[str] = []
        self.image_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("id") == "deepviz-data":
            self.in_payload = True
        if tag == "img":
            self.image_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_payload = False

    def handle_data(self, data: str) -> None:
        if self.in_payload:
            self.payload.append(data)


@pytest.mark.parametrize("engine", ["echarts", "antv"])
def test_hostile_title_category_and_series_remain_data_in_html(engine: str) -> None:
    hostile = '</script><img src=x onerror="alert(1)">\u2028\u2029'
    spec = ChartSpec(title=hostile, x="category", y="value", color="series")
    prepared = normalize([{"category": hostile, "value": 3, "series": hostile}], spec)
    native, _, _ = native_spec(engine, prepared.records, spec)
    html = browser_html(engine, [native], [spec], spec)
    parser = ScriptCollector()
    parser.feed(html)
    assert parser.image_count == 0
    assert json.loads("".join(parser.payload)) == [native]
    assert hostile not in html
