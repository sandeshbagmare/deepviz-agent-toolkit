"""Independent bounded adversarial probes on the integrated N17 candidate.

Cell/field-name probes enforce the documented defensive UTF-8 ceilings.
Remaining byte observations are not full resource-envelope acceptance. The
unmarked semantic/cleanup regressions remain strict for source owners.
"""
from __future__ import annotations

import asyncio
import importlib
import json
import os
import subprocess
import sys
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

import pytest

from deepviz import normalize, render
from deepviz.engines import browser_html, native_spec, safe_json
from deepviz.models import ChartSpec
from deepviz.tools import ToolSession

ATTACK = '</ScRiPt><img src=x onerror="globalThis.n17Executed=1"><script>&\u2028\u2029'


class _Elements(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.handlers: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        self.handlers.extend((key, value) for key, value in attrs if key.startswith("on"))


@pytest.mark.parametrize("width", [1024, 1025])
def test_n17_record_width_boundary(width: int) -> None:
    rows = [{f"field_{index}": index for index in range(width)}]
    if width == 1025:
        with pytest.raises(ValueError, match="1024 fields"):
            normalize(rows, {"kind": "table", "aggregation": "none"})
    else:
        assert len(normalize(rows, {"kind": "table", "aggregation": "none"}).records[0]) == width


def test_n17_schema_width_counts_nonretained_fields() -> None:
    rows = [{f"field_{index}": index for index in range(offset, offset + 600)} for offset in [0, 600]]
    with pytest.raises(ValueError, match="schema exceeds 1024"):
        normalize(rows, {"kind": "table", "aggregation": "sample", "max_points": 10})


def test_n17_nested_and_cyclic_values_fail_safely() -> None:
    value: dict = {"leaf": 1}
    for _ in range(66):
        value = {"next": value}
    with pytest.raises(ValueError, match="deeply|cyclic"):
        normalize([value], {"kind": "table"})
    cycle: dict = {}
    cycle["next"] = cycle
    with pytest.raises(ValueError, match="deeply|cyclic"):
        normalize([cycle], {"kind": "table"})


def test_n17_high_cardinality_preserves_all_contributions() -> None:
    # Includes later repeats of retained and overflow labels, not just unique rows.
    rows = [{"g": str(index % 100), "v": index + 1} for index in range(1000)]
    result = normalize(iter(rows), {"x": "g", "y": "v", "aggregation": "sum", "max_points": 10})
    assert result.input_count == 1000
    assert len(result.records) == 10
    assert sum(row["v"] for row in result.records) == 500500
    assert result.records[0] == {"g": "0", "v": 4510}
    assert any("cardinality" in warning for warning in result.warnings)


def test_n17_oversized_utf8_cell_rejected_before_consuming_tail() -> None:
    # Baseline O1 measured acceptance; the documented policy now rejects it.
    payload = "\U0001f642" * 16385
    assert len(payload) < 64 * 1024 < len(payload.encode("utf-8"))
    visits: list[int] = []

    def source():
        for index in range(3):
            visits.append(index)
            yield {"label": payload, "v": index}

    with pytest.raises(ValueError, match="cell exceeds 65536 UTF-8 bytes"):
        normalize(source(), {"kind": "table", "aggregation": "none", "max_points": 10})
    assert visits == [0]


def test_n17_oversized_utf8_field_name_rejected_before_consuming_tail() -> None:
    field = "\U0001f642" * 1025
    assert len(field) < 4 * 1024 < len(field.encode("utf-8"))
    visits: list[int] = []

    def source():
        for index in range(3):
            visits.append(index)
            yield {field: index}

    with pytest.raises(ValueError, match="field name exceeds 4096 UTF-8 bytes"):
        normalize(source(), {"kind": "table", "aggregation": "none"})
    assert visits == [0]


@pytest.mark.parametrize("name", [
    "../outside.json", "..\\outside.json", "C:/outside.json", "C:outside.json",
    "\\\\host\\share\\outside.json", "/outside.json", "https://example.invalid/x",
    "file:///outside.json", "inside.json:stream", "sub/../../outside.json",
])
def test_n17_tool_rejects_model_authored_path_escape(tmp_path: Path, name: str) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    (tmp_path / "outside.json").write_text('[{"secret":1}]', encoding="utf-8")
    session = ToolSession(tmp_path / "outputs", data_dir=allowed)
    with pytest.raises(ValueError):
        session.normalize_data({"file": name})


def test_n17_symlink_outside_data_directory_is_rejected(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text('[{"secret":1}]', encoding="utf-8")
    try:
        os.symlink(outside, allowed / "escape.json")
    except OSError as error:
        pytest.skip(f"Host cannot create symlinks: {error}")
    with pytest.raises(ValueError, match="escapes"):
        ToolSession(tmp_path / "outputs", data_dir=allowed).normalize_data({"file": "escape.json"})


@pytest.mark.skipif(sys.platform != "win32", reason="Windows directory-junction containment probe")
def test_n17_directory_junction_cannot_escape_data_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    (outside / "records.json").write_text('[{"secret":1}]', encoding="utf-8")
    junction = allowed / "escape"
    created = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
                             capture_output=True, text=True, check=False)
    assert created.returncode == 0, created.stderr
    try:
        with pytest.raises(ValueError, match="escapes"):
            ToolSession(tmp_path / "out", data_dir=allowed).normalize_data({"file": "escape/records.json"})
        assert (outside / "records.json").read_text(encoding="utf-8") == '[{"secret":1}]'
    finally:
        os.rmdir(junction)  # Remove only the junction, never recurse into its target.


def test_n17_strings_never_opt_in_to_local_file_reads(tmp_path: Path) -> None:
    source = tmp_path / "records.json"
    source.write_text('[{"v":7}]', encoding="utf-8")
    with pytest.raises(ValueError):
        normalize(str(source), {"kind": "table"})
    assert normalize(source, {"kind": "table"}).records == [{"v": 7}]
    session = ToolSession(tmp_path / "out", data_dir=tmp_path)
    for value in [str(source), json.dumps(str(source))]:
        with pytest.raises(ValueError):
            session.normalize_data(value)
    assert session.normalize_data({"file": "records.json"})["input_count"] == 1


def test_n17_handle_expiry_and_renewal_do_not_alias_expired_handle(tmp_path: Path) -> None:
    session = ToolSession(tmp_path / "out")
    first = session.normalize_data([{"v": 1}])["dataset_id"]
    renewed = session.normalize_data({"dataset_id": first})["dataset_id"]
    for index in range(31):
        session.normalize_data([{"v": index}])
    assert len(session.datasets) == 32
    with pytest.raises(ValueError, match="expired"):
        session.recommend_chart({"dataset_id": first})
    assert session._source({"dataset_id": renewed}) == [{"v": 1}]


def test_n17_inline_size_is_utf8_not_character_count(tmp_path: Path) -> None:
    session = ToolSession(tmp_path / "out")
    encoded = json.dumps([{"v": "\U0001f642" * 260000}], ensure_ascii=False)
    assert len(encoded) < 1_000_000 < len(encoded.encode("utf-8"))
    with pytest.raises(ValueError, match="1 MB"):
        session.normalize_data(encoded)


@pytest.mark.parametrize("engine", ["plotly", "vega", "echarts", "antv"])
def test_n17_title_field_and_data_stay_inert_in_html_and_script_json(engine: str) -> None:
    chart = ChartSpec(title=ATTACK, description=ATTACK, x=ATTACK, y="v", aggregation="none")
    records = [{ATTACK: ATTACK, "v": 2}]
    native, _, _ = native_spec(engine, records, chart)
    encoded = safe_json(native)
    assert json.loads(encoded) == native
    assert "</script" not in encoded.lower()
    assert all(character not in encoded for character in ["<", ">", "&", "\u2028", "\u2029"])
    # Vega uses a static-image wrapper in the real render path.
    html = browser_html(engine, [native], [chart], chart,
                        metadata=[{"records": records}], image="chart.svg" if engine == "vega" else None)
    parser = _Elements()
    parser.feed(html)
    assert not parser.handlers
    assert parser.tags.count("img") == (1 if engine == "vega" else 0)


@pytest.mark.parametrize("engine", ["matplotlib", "vega", "echarts", "antv", "plotly"])
def test_n17_actual_python_artifacts_keep_injected_text_inert(tmp_path: Path, engine: str) -> None:
    field = "<svg/onload=alert(1)>"
    rows = [{field: ATTACK, "v": 2}, {field: "Safe B", "v": 5}]
    output = Path(os.environ.get("N17_ARTIFACT_ROOT", str(tmp_path))) / engine
    artifact = render(rows, {"x": field, "y": "v", "title": ATTACK, "description": ATTACK,
                             "aggregation": "none"}, engine, output)
    manifest = json.loads(Path(artifact.paths[-1]).read_text(encoding="utf-8"))
    assert manifest["charts"][0]["records"] == rows
    for value in artifact.paths:
        path = Path(value)
        if path.suffix == ".html":
            parser = _Elements()
            parser.feed(path.read_text(encoding="utf-8"))
            assert not parser.handlers
            assert parser.tags.count("img") == (1 if engine in {"matplotlib", "vega"} else 0)
        elif path.suffix == ".svg":
            for element in ElementTree.fromstring(path.read_text(encoding="utf-8")).iter():
                assert element.tag.rsplit("}", 1)[-1] not in {"script", "foreignObject", "image"}
                assert not any(key.lower().startswith("on") for key in element.attrib)
    print(json.dumps({"probe": "N17 actual Python artifacts", "engine": engine,
                      "input_count": artifact.input_count, "output_count": artifact.output_count,
                      "paths": artifact.paths}))


def test_n17_dashboard_decimal_replay_preserves_supported_scalar_semantics(tmp_path: Path) -> None:
    # Regression N17-F1: default=str silently turns a supported Decimal measure
    # into excluded nonnumeric data only when a dashboard receives an iterator.
    rows = [{"g": "a", "v": Decimal("2.5")}, {"g": "a", "v": Decimal("3.5")}]
    child = {"kind": "bar", "x": "g", "y": "v", "aggregation": "sum"}
    expected = normalize(rows, child).records
    artifact = render(iter(rows), {"kind": "dashboard", "charts": [child]}, "echarts", tmp_path)
    manifest = json.loads(Path(artifact.paths[-1]).read_text(encoding="utf-8"))
    assert manifest["charts"][0]["records"] == expected


def test_n17_dashboard_replay_uses_source_once_and_removes_failed_spool(tmp_path: Path, monkeypatch) -> None:
    module = importlib.import_module("deepviz.render")
    original = module.tempfile.TemporaryDirectory
    created: list[Path] = []

    def tracked_directory(*args, **kwargs):
        directory = original(*args, dir=tmp_path, **kwargs)
        created.append(Path(directory.name))
        return directory

    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", tracked_directory)
    visits: list[int] = []

    def source():
        for index in range(3):
            visits.append(index)
            yield {"g": "a", "v": index}
        raise ValueError("N17 source failure")

    with pytest.raises(ValueError, match="N17 source failure"):
        render(source(), {"kind": "dashboard", "charts": [{"x": "g", "y": "v"}]}, "echarts", tmp_path)
    assert visits == [0, 1, 2]
    assert created and all(not path.exists() for path in created)


def test_n17_dashboard_serialization_order_observation(tmp_path: Path, monkeypatch) -> None:
    module = importlib.import_module("deepviz.render")
    original = module.json.dumps
    serialized: list[int] = []
    row = {f"k{index}": index for index in range(1025)} | {"payload": "x" * 1048576}

    def observed_dumps(value, *args, **kwargs):
        encoded = original(value, *args, **kwargs)
        if value is row:
            serialized.append(len(encoded.encode("utf-8")))
        return encoded

    monkeypatch.setattr(module.json, "dumps", observed_dumps)
    with pytest.raises(ValueError, match="1024 fields"):
        render(iter([row]), {"kind": "dashboard", "charts": [{"kind": "table"}]}, "echarts", tmp_path)
    assert serialized and serialized[0] > 1048576
    print(f"N17 replay order observation: invalid wide row serialized {serialized[0]} UTF-8 bytes before field rejection")


def test_n17_dashboard_replay_validation_closes_file_before_scratch_cleanup(tmp_path: Path, monkeypatch) -> None:
    # Regression N17-F3: tiny deterministic Windows repro, independent of bytes.
    module = importlib.import_module("deepviz.render")
    original = module.tempfile.TemporaryDirectory
    created: list[Path] = []

    def tracked_directory(*args, **kwargs):
        directory = original(*args, dir=tmp_path, **kwargs)
        created.append(Path(directory.name))
        return directory

    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", tracked_directory)
    row = {f"k{index}": index for index in range(1025)}
    with pytest.raises(ValueError, match="1024 fields"):
        render(iter([row]), {"kind": "dashboard", "charts": [{"kind": "table"}]}, "echarts", tmp_path)
    assert created and all(not path.exists() for path in created)


def test_n17_dashboard_total_bytes_observation_is_not_fanout_acceptance(tmp_path: Path) -> None:
    rows = [{"g": str(index), "v": index + 1, "text": "x" * 8000} for index in range(10)]
    source_bytes = len(json.dumps(rows).encode("utf-8"))
    child = {"x": "g", "y": "v", "aggregation": "none", "max_points": 10}
    artifact = render(iter(rows), {"kind": "dashboard", "max_points": 10, "charts": [child] * 24},
                      "echarts", tmp_path)
    manifest = json.loads(Path(artifact.paths[-1]).read_text(encoding="utf-8"))
    retained = sum(len(json.dumps(chart["records"]).encode("utf-8")) for chart in manifest["charts"])
    artifact_bytes = sum(Path(path).stat().st_size for path in artifact.paths)
    assert artifact.input_count == 10
    assert artifact.output_count == 240
    assert retained == 24 * source_bytes
    print(f"N17 dashboard bytes: source={source_bytes}, retained={retained}, artifacts={artifact_bytes}, child_rows=240")


def test_n17_failed_tool_render_does_not_accumulate_orphan_directories(tmp_path: Path) -> None:
    # Regression N17-F2: a rejected request must not leak an output directory.
    outputs = tmp_path / "out"
    session = ToolSession(outputs)
    with pytest.raises(ValueError, match="missing"):
        session.render_chart("echarts", [{"g": "a", "v": 1}], {"x": "missing", "y": "v"})
    assert not list(outputs.iterdir()), "Failed model requests leave per-call output directories"


def test_n17_artifact_limit_rejection_reclaims_its_own_files(tmp_path: Path, monkeypatch) -> None:
    # A reduced test cap safely reproduces the failure-cleanup path without
    # creating >16 MiB artifacts. This is not evidence that the real cap is safe.
    tools = importlib.import_module("deepviz.tools")
    monkeypatch.setattr(tools, "MAX_ARTIFACT_BYTES", 100)
    session = ToolSession(tmp_path / "out")
    with pytest.raises(ValueError, match="16 MiB"):
        session.render_chart("echarts", [{"g": "a", "v": 1}], {"x": "g", "y": "v"})
    assert not list(session.output_dir.rglob("*")), "Rejected generated artifacts remain on disk"


def test_n17_artifact_names_are_unique_and_existing_files_untouched(tmp_path: Path) -> None:
    marker = tmp_path / "do-not-overwrite.txt"
    marker.write_text("N17 sentinel", encoding="utf-8")
    session = ToolSession(tmp_path)
    first = session.render_chart("echarts", [{"g": "a", "v": 1}], {"x": "g", "y": "v"})
    second = session.render_chart("echarts", [{"g": "a", "v": 1}], {"x": "g", "y": "v"})
    assert set(first["paths"]).isdisjoint(second["paths"])
    assert marker.read_text(encoding="utf-8") == "N17 sentinel"
    assert all(Path(path).resolve().is_relative_to(tmp_path.resolve())
               for path in [*first["paths"], *second["paths"]])


def test_n17_real_stdio_handle_expiry_resource_identity_and_deleted_file(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from mcp.shared.exceptions import McpError

    # Reuse the baseline black-box transport harness, not server/tool mocks.
    from test_mcp_transport import metadata, resource_links, running_server

    async def exercise() -> None:
        async with running_server(tmp_path) as session:
            initial = metadata(await session.call_tool("normalize_data", {"data": [{"v": 7}]}))["dataset_id"]
            renewed = metadata(await session.call_tool("normalize_data", {"data": {"dataset_id": initial}}))["dataset_id"]
            for index in range(31):
                metadata(await session.call_tool("normalize_data", {"data": [{"v": index}]}))
            expired = await session.call_tool("recommend_chart", {"data": {"dataset_id": initial}})
            assert expired.isError
            assert not (await session.call_tool("recommend_chart", {"data": {"dataset_id": renewed}})).isError
            arguments = {"data": [{"g": "a", "v": 2}], "spec": {"x": "g", "y": "v"}}
            first = resource_links(await session.call_tool("render_echarts", arguments))
            second = resource_links(await session.call_tool("render_echarts", arguments))
            assert len(first) == len(second) == 2
            assert {str(link.uri) for link in first}.isdisjoint(str(link.uri) for link in second)
            first_html = next(link for link in first if link.mimeType == "text/html")
            assert (await session.read_resource(first_html.uri)).contents
            artifacts = list((tmp_path / "artifacts").rglob("chart.html"))
            assert len(artifacts) == 2
            for artifact in artifacts:
                artifact.unlink()
            with pytest.raises(McpError):
                await session.read_resource(first_html.uri)
            assert (await session.list_tools()).tools  # Bad/missing resource does not kill transport.

    asyncio.run(exercise())
