"""Strict encoded-data admission oracles; real stdio, never SDK/parser replacements."""
from __future__ import annotations

import asyncio
import json
import sys
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

import pytest

from deepviz import normalize
from deepviz.tools import MAX_INLINE_BYTES, ToolSession, create_tools

SPEC = {"kind": "table", "aggregation": "none"}
ROWS = [{"category": "東京🌸", "amount": 7}, {"category": "München", "amount": -2}]
DUPLICATES = [
    '[{"category":"discarded","category":"kept","amount":1}]',
    '[{"category":{"label":"discarded","label":"kept"},"amount":1}]',
    '{"file":"first.json","file":"rows.json"}',
    '[{"\\u0061":1,"a":2}]',
]
DUPLICATE_IDS = ["record-key", "nested-key", "control-key", "escaped-equivalent-key"]
OPERATIONS = ["normalize_data", "recommend_chart", "render_echarts"]
SOURCE = Path(__file__).resolve().parents[1] / "src"


def setup_data(root: Path) -> Path:
    data = root / "data"
    data.mkdir()
    for name, rows in (("rows.json", ROWS), ("first.json", [{"different": 9}])):
        (data / name).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return data


def arguments(operation: str, data) -> dict:
    result = {"data": data}
    if operation == "render_echarts":
        result["spec"] = SPEC
    return result


def text_metadata(result) -> dict:
    assert not result.isError, "Recovery tool call failed"
    return json.loads(next(block.text for block in result.content if block.type == "text"))


@asynccontextmanager
async def real_stdio(root: Path, data_dir: Path):
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "deepviz.mcp_server", "--output-dir", str(root / "output"),
              "--data-dir", str(data_dir)],
        cwd=str(root),
        env={"PYTHONPATH": str(SOURCE), "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
             "MPLBACKEND": "Agg"},
    )
    with (root / "server.stderr").open("w", encoding="utf-8") as stderr:
        async with stdio_client(params, errlog=stderr) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
                assert (await session.initialize()).serverInfo.name == "DeepViz"
                assert len((await session.list_tools()).tools) == 7
                yield session


@pytest.mark.parametrize("raw", DUPLICATES, ids=DUPLICATE_IDS)
def test_r11_core_normalizer_rejects_duplicate_json_control(raw: str) -> None:
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        normalize(raw, SPEC)


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("raw", DUPLICATES, ids=DUPLICATE_IDS)
def test_r11_tool_session_rejects_duplicate_json_before_cache_or_output(
    tmp_path: Path, operation: str, raw: str,
) -> None:
    session = ToolSession(tmp_path / "output", data_dir=setup_data(tmp_path))
    if operation == "render_echarts":
        invoke = session.renderer("echarts")
    else:
        invoke = getattr(session, operation)
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        invoke(**arguments(operation, raw))
    assert not session.datasets
    assert not list((tmp_path / "output").rglob("*"))


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("raw", DUPLICATES, ids=DUPLICATE_IDS)
def test_r11_structured_tools_reject_duplicate_json(
    tmp_path: Path, operation: str, raw: str,
) -> None:
    pytest.importorskip("langchain_core")
    tools = {tool.name: tool for tool in create_tools(tmp_path / "output", data_dir=setup_data(tmp_path))}
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        tools[operation].invoke(arguments(operation, raw))
    assert not list((tmp_path / "output").rglob("*"))


@pytest.mark.parametrize("caller", ["core", "session", "structured"])
def test_r11_recursive_encoded_json_is_declared_value_error(tmp_path: Path, caller: str) -> None:
    raw = "[" * 10_000 + "]" * 10_000
    if caller == "core":
        def invoke():
            return normalize(raw, SPEC)
    elif caller == "session":
        def invoke():
            return ToolSession(tmp_path / "output").normalize_data(raw)
    else:
        pytest.importorskip("langchain_core")
        tool = next(tool for tool in create_tools(tmp_path / "output") if tool.name == "normalize_data")

        def invoke():
            return tool.invoke({"data": raw})
    with pytest.raises(ValueError, match="[Nn]est|[Dd]epth|[Rr]ecurs") as caught:
        invoke()
    assert len(str(caught.value).encode("utf-8")) < 1024


@pytest.mark.parametrize("caller", ["session", "structured"])
def test_r11_valid_unicode_file_and_copied_handle_remain_authorized(tmp_path: Path, caller: str) -> None:
    data_dir = setup_data(tmp_path)
    output = tmp_path / "output"
    if caller == "session":
        tool_session = ToolSession(output, data_dir=data_dir)

        def call(name, value):
            return getattr(tool_session, name)(value) if name != "render_echarts" else (
                tool_session.render_chart("echarts", value, SPEC)
            )
    else:
        pytest.importorskip("langchain_core")
        tools = {tool.name: tool for tool in create_tools(output, data_dir=data_dir)}

        def call(name, value):
            return tools[name].invoke(arguments(name, value))
    for value in (json.dumps(ROWS, ensure_ascii=False), json.dumps({"file": "rows.json"})):
        info = call("normalize_data", value)
        copied = call("normalize_data", json.dumps({"dataset_id": info["dataset_id"]}))
        handle = {"dataset_id": copied["dataset_id"]}
        assert call("recommend_chart", handle)["input_count"] == len(ROWS)
        result = call("render_echarts", handle)
        manifest = next(Path(path) for path in result["paths"] if Path(path).name == "manifest.json")
        assert json.loads(manifest.read_text(encoding="utf-8"))["charts"][0]["records"] == ROWS


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("case", [*DUPLICATE_IDS, "recursion", "raw-inline-bytes", "raw-file-bytes"])
def test_r11_real_stdio_rejects_raw_admission_then_reads_recovered_resource(
    tmp_path: Path, operation: str, case: str,
) -> None:
    data_dir = setup_data(tmp_path)
    if case in DUPLICATE_IDS:
        raw = DUPLICATES[DUPLICATE_IDS.index(case)]
    elif case == "recursion":
        raw = "[" * 10_000 + "]" * 10_000
    else:
        payload = ROWS if case == "raw-inline-bytes" else {"file": "rows.json"}
        raw = " " * (MAX_INLINE_BYTES + 1) + json.dumps(payload, ensure_ascii=False)

    async def exercise() -> None:
        async with real_stdio(tmp_path, data_dir) as session:
            bad = await session.call_tool(operation, arguments(operation, raw))
            files_after_bad = [str(path.relative_to(tmp_path)) for path in (tmp_path / "output").rglob("*")]
            info = text_metadata(await session.call_tool("normalize_data", {
                "data": json.dumps(ROWS, ensure_ascii=False),
            }))
            copied = text_metadata(await session.call_tool("normalize_data", {
                "data": json.dumps({"dataset_id": info["dataset_id"]}),
            }))
            advice = text_metadata(await session.call_tool("recommend_chart", {
                "data": {"dataset_id": copied["dataset_id"]},
            }))
            assert advice["input_count"] == len(ROWS)
            file_info = text_metadata(await session.call_tool("normalize_data", {
                "data": json.dumps({"file": "rows.json"}),
            }))
            rendered = text_metadata(await session.call_tool("render_echarts", {
                "data": {"dataset_id": file_info["dataset_id"]}, "spec": SPEC,
            }))
            resource = next(item for item in rendered["resources"] if item["mime_type"] == "application/json")
            retrieved = (await session.read_resource(resource["uri"])).contents[0].text
            manifest = json.loads(retrieved)
            assert manifest["charts"][0]["records"] == ROWS
            assert manifest["charts"][0]["input_count"] == len(ROWS)
            error_text = "\n".join(block.text for block in bad.content if block.type == "text")
            observed = {"case": case, "operation": operation, "raw_utf8_bytes": len(raw.encode("utf-8")),
                        "is_error": bad.isError, "error_utf8_bytes": len(error_text.encode("utf-8")),
                        "files_after_bad": files_after_bad, "recovery_unicode_and_copied_handle": True,
                        "authorized_file_resource_read": True}
            (tmp_path / "observed.json").write_text(json.dumps(observed, indent=2), encoding="utf-8")
            assert bad.isError, f"Raw {case} accepted by real MCP before SDK canonicalization: {observed}"
            assert all(block.type == "text" for block in bad.content)
            assert len(error_text.encode("utf-8")) < 2048 and "Traceback" not in error_text
            if case in DUPLICATE_IDS:
                assert "duplicate" in error_text.lower()
            elif case.startswith("raw-"):
                assert "inline" in error_text.lower() and "1 MB" in error_text
            else:
                assert any(word in error_text.lower() for word in ("nest", "depth", "recurs"))
            assert not files_after_bad, "Rejected admission allocated renderer output"

    asyncio.run(asyncio.wait_for(exercise(), timeout=150))


@pytest.mark.parametrize("caller", ["session", "structured"])
@pytest.mark.parametrize("reference", [False, True], ids=["inline", "authorized-file"])
def test_r11_raw_utf8_byte_limit_direct_controls(tmp_path: Path, caller: str, reference: bool) -> None:
    data_dir = setup_data(tmp_path)
    payload = {"file": "rows.json"} if reference else ROWS
    raw = " " * (MAX_INLINE_BYTES + 1) + json.dumps(payload, ensure_ascii=False)
    if caller == "session":
        with pytest.raises(ValueError, match="Inline data exceeds"):
            ToolSession(tmp_path / "output", data_dir=data_dir).normalize_data(raw)
    else:
        pytest.importorskip("langchain_core")
        tool = next(tool for tool in create_tools(tmp_path / "output", data_dir=data_dir)
                    if tool.name == "normalize_data")
        with pytest.raises(ValueError, match="Inline data exceeds"):
            tool.invoke({"data": raw})
